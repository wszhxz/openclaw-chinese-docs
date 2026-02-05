---
summary: "Agent loop lifecycle, streams, and wait semantics"
read_when:
  - You need an exact walkthrough of the agent loop or lifecycle events
title: "Agent Loop"
---
# Agent Loop (OpenClaw)

代理循环是代理的完整“真实”运行：输入 → 上下文组装 → 模型推理 →
工具执行 → 流式回复 → 持久化。这是将消息转化为操作和最终回复的权威路径，同时保持会话状态的一致性。

在 OpenClaw 中，一个循环是每个会话的单次、序列化的运行，在模型思考、调用工具和流式输出时发出生命周期和流事件。本文档解释了该真实循环是如何端到端连接的。

## 入口点

- 网关 RPC: `agent` 和 `agent.wait`。
- 命令行界面: `agent` 命令。

## 工作原理（高层次）

1. `agent` RPC 验证参数，解析会话（sessionKey/sessionId），持久化会话元数据，立即返回 `{ runId, acceptedAt }`。
2. `agentCommand` 运行代理：
   - 解析模型 + 思考/详细默认值
   - 加载技能快照
   - 调用 `runEmbeddedPiAgent`（pi-agent-core 运行时）
   - 如果嵌入的循环没有发出，则发出 **生命周期结束/错误**
3. `runEmbeddedPiAgent`:
   - 通过每个会话 + 全局队列序列化运行
   - 解析模型 + 认证配置文件并构建 pi 会话
   - 订阅 pi 事件并流式传输助手/工具增量
   - 强制超时 -> 如果超出则中止运行
   - 返回有效负载 + 使用情况元数据
4. `subscribeEmbeddedPiSession` 将 pi-agent-core 事件桥接到 OpenClaw `agent` 流：
   - 工具事件 => `stream: "tool"`
   - 助手增量 => `stream: "assistant"`
   - 生命周期事件 => `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` 使用 `waitForAgentJob`:
   - 等待 **生命周期结束/错误** 对于 `runId`
   - 返回 `{ status: ok|error|timeout, startedAt, endedAt, error? }`

## 排队 + 并发

- 每个会话键（会话车道）的运行是串行化的，并且可选地通过全局车道。
- 这防止了工具/会话竞争并保持会话历史的一致性。
- 消息通道可以选择队列模式（收集/引导/后续）来喂养这个车道系统。
  参见 [命令队列](/concepts/queue)。

## 会话 + 工作区准备

- 解析并创建工作区；沙盒运行可能重定向到沙盒工作区根目录。
- 加载技能（或从快照中重用）并注入到环境和提示中。
- 解析并注入引导/上下文文件到系统提示报告中。
- 获取会话写锁；在流式传输之前打开并准备 `SessionManager`。

## 提示组装 + 系统提示

- 系统提示从 OpenClaw 的基础提示、技能提示、引导上下文和每次运行的覆盖中构建。
- 强制执行特定于模型的限制和压缩保留令牌。
- 参见 [系统提示](/concepts/system-prompt) 了解模型看到的内容。

## 挂钩点（你可以拦截的地方）

OpenClaw 有两个挂钩系统：

- **内部挂钩**（网关挂钩）：针对命令和生命周期事件的事件驱动脚本。
- **插件挂钩**：代理/工具生命周期和网关管道内的扩展点。

### 内部挂钩（网关挂钩）

- **`agent:bootstrap`**: 在系统提示最终确定之前构建引导文件时运行。
  使用此功能添加/删除引导上下文文件。
- **命令挂钩**: `/new`, `/reset`, `/stop`，以及其他命令事件（参见 Hooks 文档）。

参见 [Hooks](/hooks) 了解设置和示例。

### 插件挂钩（代理 + 网关生命周期）

这些在代理循环或网关管道内运行：

- **`before_agent_start`**: 在运行开始之前注入上下文或覆盖系统提示。
- **`agent_end`**: 在完成之后检查最终消息列表和运行元数据。
- **`before_compaction` / `after_compaction`**: 观察或注释压缩周期。
- **`before_tool_call` / `after_tool_call`**: 拦截工具参数/结果。
- **`tool_result_persist`**: 同步转换工具结果，在写入会话记录之前。
- **`message_received` / `message_sending` / `message_sent`**: 入站 + 出站消息挂钩。
- **`session_start` / `session_end`**: 会话生命周期边界。
- **`gateway_start` / `gateway_stop`**: 网关生命周期事件。

参见 [Plugins](/plugin#plugin-hooks) 了解挂钩 API 和注册详情。

## 流式传输 + 部分回复

- 助手增量从 pi-agent-core 流式传输并作为 `assistant` 事件发出。
- 块流式传输可以在 `text_end` 或 `message_end` 发出部分回复。
- 推理流式传输可以作为单独的流或作为块回复发出。
- 参见 [流式传输](/concepts/streaming) 了解分块和块回复行为。

## 工具执行 + 消息工具

- 工具开始/更新/结束事件在 `tool` 流上发出。
- 在日志记录/发出之前，工具结果会根据大小和图像负载进行清理。
- 跟踪消息工具发送以抑制重复的助手确认。

## 回复成形 + 抑制

- 最终有效负载由以下组成：
  - 助手文本（和可选的推理）
  - 内联工具摘要（当详细 + 允许时）
  - 当模型出错时的助手错误文本
- `NO_REPLY` 被视为静默令牌并从传出有效负载中过滤掉。
- 从最终有效负载列表中移除消息工具的重复项。
- 如果没有可渲染的有效负载剩余且工具出错，则发出回退工具错误回复
  （除非消息工具已经发送了一个用户可见的回复）。

## 压缩 + 重试

- 自动压缩发出 `compaction` 流事件并可以触发重试。
- 在重试时，内存缓冲区和工具摘要被重置以避免重复输出。
- 参见 [压缩](/concepts/compaction) 了解压缩管道。

## 事件流（今天）

- `lifecycle`: 由 `subscribeEmbeddedPiSession` 发出（以及作为后备由 `agentCommand` 发出）
- `assistant`: 从 pi-agent-core 流式传输的增量
- `tool`: 从 pi-agent-core 流式传输的工具事件

## 聊天频道处理

- 助手增量被缓冲到聊天 `delta` 消息中。
- 在 **生命周期结束/错误** 时发出一个聊天 `final`。

## 超时

- `agent.wait` 默认: 30秒（仅等待）。`timeoutMs` 参数覆盖。
- 代理运行时: `agents.defaults.timeoutSeconds` 默认 600秒；在 `runEmbeddedPiAgent` 中断计时器中强制执行。

## 可能提前结束的地方

- 代理超时（中止）
- AbortSignal（取消）
- 网关断开连接或 RPC 超时
- `agent.wait` 超时（仅等待，不停止代理）