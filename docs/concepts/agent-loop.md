---
summary: "Agent loop lifecycle, streams, and wait semantics"
read_when:
  - You need an exact walkthrough of the agent loop or lifecycle events
title: "Agent Loop"
---
# 智能体循环 (OpenClaw)

智能体循环是智能体的完整“真实”运行：输入 → 上下文组装 → 模型推理 → 工具执行 → 流式回复 → 持久化。这是将消息转化为操作和最终回复的权威路径，同时保持会话状态一致。

在 OpenClaw 中，循环是每个会话的单次串行运行，随着模型思考、调用工具和流式输出而发出生命周期和流事件。本文档解释了该真实循环如何端到端连接。

## 入口点

- 网关 RPC：`agent` 和 `agent.wait`。
- CLI：`agent` 命令。

## 工作原理（高层级）

1. `agent` RPC 验证参数，解析会话 (sessionKey/sessionId)，持久化会话元数据，立即返回 `{ runId, acceptedAt }`。
2. `agentCommand` 运行智能体：
   - 解析模型 + 思考/详细默认值
   - 加载技能快照
   - 调用 `runEmbeddedPiAgent` (pi-agent-core 运行时)
   - 如果嵌入式循环未发出 **生命周期结束/错误**，则发出 **生命周期结束/错误**
3. `runEmbeddedPiAgent`：
   - 通过每个会话 + 全局队列串行化运行
   - 解析模型 + 认证配置并构建 pi 会话
   - 订阅 pi 事件并流式传输助手/工具差异
   - 强制执行超时 -> 如果超过则中止运行
   - 返回负载 + 使用元数据
4. `subscribeEmbeddedPiSession` 桥接 pi-agent-core 事件到 OpenClaw `agent` 流：
   - 工具事件 => `stream: "tool"`
   - 助手差异 => `stream: "assistant"`
   - 生命周期事件 => `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` 使用 `waitForAgentJob`：
   - 等待 **生命周期结束/错误** 用于 `runId`
   - 返回 `{ status: ok|error|timeout, startedAt, endedAt, error? }`

## 排队与并发

- 按会话键 (会话通道) 串行化运行，并通过全局通道 (可选)。
- 这防止了工具/会话竞争并保持会话历史一致。
- 消息通道可以选择队列模式 (收集/引导/跟进) 来馈送此通道系统。
  参见 [命令队列](/concepts/queue)。

## 会话与工作区准备

- 工作区被解析并创建；沙盒运行可能会重定向到沙盒工作区根目录。
- 技能被加载 (或从快照重用) 并注入到环境和提示词中。
- 引导/上下文文件被解析并注入到系统提示词报告中。
- 获取会话写入锁；`SessionManager` 在流式传输之前被打开并准备。

## 提示词组装 + 系统提示词

- 系统提示词基于 OpenClaw 的基础提示词、技能提示词、引导上下文和每次运行的覆盖项构建。
- 强制执行模型特定限制和压缩预留令牌。
- 参见 [系统提示词](/concepts/system-prompt) 了解模型所见内容。

## 钩子点 (您可以拦截的位置)

OpenClaw 拥有两个钩子系统：

- **内部钩子** (网关钩子)：用于命令和生命周期事件的事件驱动脚本。
- **插件钩子**：智能体/工具生命周期和网关管道内的扩展点。

### 内部钩子 (网关钩子)

- **`agent:bootstrap`**：在构建引导文件时运行，此时系统提示词尚未最终确定。
  使用此功能添加/移除引导上下文文件。
- **命令钩子**：`/new`, `/reset`, `/stop` 以及其他命令事件 (参见 Hooks 文档)。

参见 [钩子](/automation/hooks) 了解设置和示例。

### 插件钩子 (智能体 + 网关生命周期)

这些在智能体循环或网关管道内运行：

- **`before_model_resolve`**：在会话前运行 (无 `messages`)，以便在模型解析之前确定性覆盖提供者/模型。
- **`before_prompt_build`**：在会话加载后运行 (带有 `messages`)，以便在提交提示词之前注入 `prependContext`, `systemPrompt`, `prependSystemContext` 或 `appendSystemContext`。使用 `prependContext` 进行每轮动态文本，并使用系统上下文字段以提供应位于系统提示词空间的稳定指导。
- **`before_agent_start`**：遗留兼容性钩子，可能在任一阶段运行；优先使用上述显式钩子。
- **`agent_end`**：完成后检查最终消息列表和运行元数据。
- **`before_compaction` / `after_compaction`**：观察或注释压缩周期。
- **`before_tool_call` / `after_tool_call`**：拦截工具参数/结果。
- **`tool_result_persist`**：在写入会话记录之前同步转换工具结果。
- **`message_received` / `message_sending` / `message_sent`**：入站 + 出站消息钩子。
- **`session_start` / `session_end`**：会话生命周期边界。
- **`gateway_start` / `gateway_stop`**：网关生命周期事件。

参见 [插件](/tools/plugin#plugin-hooks) 了解钩子 API 和注册详情。

## 流式传输 + 部分回复

- 助手差异从 pi-agent-core 流式传输并发出为 `assistant` 事件。
- 块流式传输可以在 `text_end` 或 `message_end` 上发出部分回复。
- 推理流式传输可以作为单独流发出，也可以作为块回复发出。
- 参见 [流式传输](/concepts/streaming) 了解分块和块回复行为。

## 工具执行 + 消息工具

- 工具开始/更新/结束事件在 `tool` 流上发出。
- 工具结果在记录/发出之前针对大小和图片负载进行清理。
- 跟踪消息工具发送以抑制重复的助手确认。

## 回复塑形 + 抑制

- 最终负载由以下内容组装：
  - 助手文本 (及可选推理)
  - 行内工具摘要 (当详细且允许时)
  - 模型出错时的助手错误文本
- `NO_REPLY` 被视为静默令牌并从传出负载中过滤。
- 消息工具重复项从最终负载列表中移除。
- 如果没有可渲染的负载剩余且工具出错，则发出回退工具错误回复 (除非消息工具已经发送了用户可见的回复)。

## 压缩 + 重试

- 自动压缩发出 `compaction` 流事件并可触发重试。
- 在重试时，内存缓冲区和工具摘要被重置以避免重复输出。
- 参见 [压缩](/concepts/compaction) 了解压缩管道。

## 事件流 (当前)

- `lifecycle`: 由 `subscribeEmbeddedPiSession` 发出 (以及作为回退由 `agentCommand` 发出)
- `assistant`: 来自 pi-agent-core 的流式差异
- `tool`: 来自 pi-agent-core 的流式工具事件

## 聊天通道处理

- 助手差异被缓冲到聊天 `delta` 消息中。
- 在 **生命周期结束/错误** 时发出聊天 `final`。

## 超时

- `agent.wait` 默认：30 秒 (仅等待)。`timeoutMs` 参数覆盖。
- 智能体运行时：`agents.defaults.timeoutSeconds` 默认 600 秒；在 `runEmbeddedPiAgent` 中止计时器中强制执行。

## 何处可能提前结束

- 智能体超时 (中止)
- AbortSignal (取消)
- 网关断开或 RPC 超时
- `agent.wait` 超时 (仅等待，不中止智能体)