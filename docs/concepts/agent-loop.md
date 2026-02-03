---
summary: "Agent loop lifecycle, streams, and wait semantics"
read_when:
  - You need an exact walkthrough of the agent loop or lifecycle events
title: "Agent Loop"
---
# 代理循环（OpenClaw）

代理循环是代理的完整“真实”运行流程：输入 → 上下文组装 → 模型推理 → 工具执行 → 流式回复 → 持久化。这是将消息转化为行动和最终回复的权威路径，同时保持会话状态的一致性。

在 OpenClaw 中，循环是每个会话的单次序列化运行，会在模型思考、调用工具和流式输出时发出生命周期和流事件。本文档解释了该真实循环如何端到端地连接。

## 入口点

- 网关 RPC：`agent` 和 `agent.wait`。
- CLI：`agent` 命令。

## 工作原理（高层次）

1. `agent` RPC 验证参数，解析会话（sessionKey/sessionId），持久化会话元数据，立即返回 `{ runId, acceptedAt }`。
2. `agentCommand` 运行代理：
   - 解析模型 + 思考/详细模式默认值
   - 加载技能快照
   - 调用 `runEmbeddedPiAgent`（pi-agent-core 运行时）
   - 如果嵌入式循环未发出，则发出 **生命周期结束/错误** 事件
3. `runEmbeddedPiAgent`：
   - 通过会话级 + 全局队列序列化运行
   - 解析模型 + 认证配置文件并构建 pi 会话
   - 订阅 pi 事件并流式传输助手/工具增量
   - 强制超时 → 如果超出则中止运行
   - 返回负载 + 使用元数据
4. `subscribeEmbeddedPiSession` 将 pi-agent-core 事件桥接到 OpenClaw `agent` 流：
   - 工具事件 ⇒ `stream: "tool"`
   - 助手增量 ⇒ `stream: "assistant"`
   - 生命周期事件 ⇒ `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` 使用 `waitForAgentJob`：
   - 等待 **生命周期结束/错误** 事件（针对 `runId`）
   - 返回 `{ status: ok|error|timeout, startedAt, endedAt, error? }`

## 队列 + 并发

- 每个会话键（会话通道）和可选的全局通道序列化运行。
- 这防止了工具/会话竞争并保持会话历史一致性。
- 消息通道可以选择队列模式（收集/引导/后续）来支持该通道系统。
  详见 [命令队列](/concepts/queue)。

## 会话 + 工作区准备

- 工作区被解析并创建；沙箱化运行可能重定向到沙箱工作区根目录。
- 技能被加载（或重用快照）并注入到环境和提示中。
- 启动/上下文文件被解析并注入到系统提示报告中。
- 获取会话写入锁；在流式传输前打开并准备 `SessionManager`。

## 提示组装 + 系统提示

- 系统提示由 OpenClaw 的基础提示、技能提示、启动上下文和运行覆盖组成。
- 强制执行模型特定限制和压缩保留令牌。
- 详见 [系统提示](/concepts/system-prompt) 了解模型看到的内容。

## 钩子点（可拦截的位置）

OpenClaw 有两个钩子系统：

- **内部钩子**（网关钩子）：命令和生命周期事件的事件驱动脚本。
- **插件钩子**：代理/工具生命周期和网关管道中的扩展点。

### 内部钩子（网关钩子）

- **`agent:bootstrap`**：在系统提示最终化前运行，用于构建启动文件。
  使用此钩子添加/删除启动上下文文件。
- **命令钩子**：`/new`、`/reset`、`/stop` 和其他命令事件（详见钩子文档）。

详见 [钩子](/hooks) 了解设置和示例。

### 插件钩子（代理 + 网关生命周期）

这些钩子在代理循环或网关管道中运行：

- **`before_agent_start`**：运行开始前注入上下文或覆盖系统提示。
- **`agent_end`**：运行完成后检查最终消息列表和运行元数据。
- **`before_compaction` / `after_compaction`**：观察或注释压缩周期。
- **`before_tool_call` / `after_tool_call`**：拦截工具参数/结果。
- **`tool_result_persist`**：在工具结果写入会话记录前同步转换。
- **`message_received` / `message_sending` / `message_sent`**：入站 + 出站消息钩子。
- **`session_start` / `session_end`**：会话生命周期边界。
- **`