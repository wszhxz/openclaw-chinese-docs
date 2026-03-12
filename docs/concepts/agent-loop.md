---
summary: "Agent loop lifecycle, streams, and wait semantics"
read_when:
  - You need an exact walkthrough of the agent loop or lifecycle events
title: "Agent Loop"
---
# 代理循环（OpenClaw）

代理循环是代理的一次完整“真实”运行过程：输入 → 上下文组装 → 模型推理 → 工具执行 → 流式响应 → 持久化。它是将一条消息转化为具体动作与最终回复的权威路径，同时确保会话状态的一致性。

在 OpenClaw 中，一次循环即为每个会话中一次独立、串行化的运行，会在模型思考、调用工具及流式输出过程中持续发出生命周期事件和流事件。本文档说明该真实循环如何端到端地被串联起来。

## 入口点

- 网关 RPC：``agent`` 和 ``agent.wait``。
- CLI：``agent`` 命令。

## 工作原理（高层概述）

1. ``agent`` RPC 验证参数、解析会话（sessionKey/sessionId）、持久化会话元数据，并立即返回 ``{ runId, acceptedAt }``。
2. ``agentCommand`` 运行代理：
   - 解析模型及思考/详细模式默认值；
   - 加载技能快照；
   - 调用 ``runEmbeddedPiAgent``（pi-agent-core 运行时）；
   - 若嵌入式循环未发出生命周期结束/错误事件，则主动补发 **lifecycle end/error**。
3. ``runEmbeddedPiAgent``：
   - 通过每会话队列 + 全局队列对运行进行串行化；
   - 解析模型与认证配置文件，并构建 pi 会话；
   - 订阅 pi 事件并流式传输助手/工具增量更新；
   - 强制执行超时机制 → 若超时则中止当前运行；
   - 返回有效载荷及用量元数据。
4. ``subscribeEmbeddedPiSession`` 将 pi-agent-core 事件桥接到 OpenClaw 的 ``agent`` 流：
   - 工具事件 → ``stream: "tool"``
   - 助手增量更新 → ``stream: "assistant"``
   - 生命周期事件 → ``stream: "lifecycle"``（``phase: "start" | "end" | "error"``）
5. ``agent.wait`` 使用 ``waitForAgentJob``：
   - 等待 ``runId`` 的 **lifecycle end/error**；
   - 返回 ``{ status: ok|error|timeout, startedAt, endedAt, error? }``

## 排队与并发控制

- 运行按会话密钥（会话通道）串行化，也可选择通过全局通道进一步串行化。
- 此机制可防止工具/会话竞争，并保障会话历史一致性。
- 消息通道可选择不同队列模式（collect/steer/followup），以适配该通道系统。  
  参见 [命令队列](/concepts/queue)。

## 会话与工作区准备

- 工作区被解析并创建；沙箱化运行可能重定向至沙箱工作区根目录。
- 技能被加载（或复用已有快照），并注入环境与提示词中。
- 启动/上下文文件被解析，并注入系统提示报告中。
- 获取会话写锁；在开始流式传输前，打开并准备 ``SessionManager``。

## 提示词组装与系统提示

- 系统提示由 OpenClaw 基础提示、技能提示、启动上下文及每次运行的覆盖项共同构建。
- 强制执行模型特定的长度限制与压缩预留令牌数。
- 详见 [系统提示](/concepts/system-prompt)，了解模型实际接收到的内容。

## 可拦截点（Hook 点）

OpenClaw 提供两类 Hook 系统：

- **内部 Hook（网关 Hook）**：面向命令与生命周期事件的事件驱动脚本。
- **插件 Hook**：位于代理/工具生命周期及网关流水线中的扩展点。

### 内部 Hook（网关 Hook）

- **``agent:bootstrap``**：在系统提示最终确定前、构建启动文件期间运行。  
  可用于添加或移除启动上下文文件。
- **命令 Hook**：``/new``、``/reset``、``/stop`` 及其他命令事件（参见 Hook 文档）。

详见 [Hook](/automation/hooks)，含配置方法与示例。

### 插件 Hook（代理 + 网关生命周期）

这些 Hook 在代理循环或网关流水线内部运行：

- **``before_model_resolve``**：在会话建立前（尚无 ``messages``）运行，用于在模型解析前确定性地覆写提供方/模型。
- **``before_prompt_build``**：在会话加载后（已具备 ``messages``）运行，可在提交提示前注入 ``prependContext``、``systemPrompt``、``prependSystemContext`` 或 ``appendSystemContext``。使用 ``prependContext`` 可实现每轮动态文本，而系统上下文字段适用于需稳定置于系统提示空间的引导内容。
- **``before_agent_start``**：遗留兼容性 Hook，可能在任一阶段运行；建议优先使用上述显式 Hook。
- **``agent_end``**：在运行完成后检查最终消息列表与运行元数据。
- **``before_compaction`` / ``after_compaction``**：观察或标注压缩周期。
- **``before_tool_call`` / ``after_tool_call``**：拦截工具参数/结果。
- **``tool_result_persist``**：在工具结果写入会话记录前，同步转换其内容。
- **``message_received`` / ``message_sending`` / ``message_sent``**：入站与出站消息 Hook。
- **``session_start`` / ``session_end``**：会话生命周期边界。
- **``gateway_start`` / ``gateway_stop``**：网关生命周期事件。

详见 [插件](/tools/plugin#plugin-hooks)，含 Hook API 与注册细节。

## 流式传输与部分响应

- 助手增量更新从 pi-agent-core 流式输出，并作为 ``assistant`` 事件发出。
- 分块流式传输可在 ``text_end`` 或 ``message_end`` 上发出部分响应。
- 推理流式传输可作为独立流发出，也可作为分块响应发出。
- 详见 [流式传输](/concepts/streaming)，了解分块与分块响应行为。

## 工具执行与消息类工具

- 工具启动/更新/结束事件在 ``tool`` 流上发出。
- 工具结果在记录/发出前，会对大小与图像负载进行清洗。
- 消息类工具发送操作会被追踪，以抑制重复的助手确认响应。

## 回复塑形与抑制

- 最终有效载荷由以下内容组装而成：
  - 助手文本（及可选的推理内容）；
  - 内联工具摘要（仅当启用详细模式且允许时）；
  - 模型报错时的助手错误文本。
- ``NO_REPLY`` 被视为静默令牌，将从外发有效载荷中过滤掉。
- 消息类工具重复项将从最终有效载荷列表中移除。
- 若剩余无可渲染的有效载荷，且某工具报错，则发出回退工具错误响应（除非消息类工具已发送用户可见响应）。

## 压缩与重试

- 自动压缩会发出 ``compaction`` 流事件，并可触发重试。
- 重试时，内存缓冲区与工具摘要将被重置，以避免重复输出。
- 详见 [压缩](/concepts/compaction)，了解压缩流水线。

## 当前事件流

- ``lifecycle``：由 ``subscribeEmbeddedPiSession`` 发出（``agentCommand`` 作为备用兜底）；
- ``assistant``：来自 pi-agent-core 的流式增量更新；
- ``tool``：来自 pi-agent-core 的流式工具事件。

## 聊天通道处理

- 助手增量更新被缓冲为聊天 ``delta`` 消息。
- 在 **lifecycle end/error** 时发出聊天 ``final``。

## 超时机制

- ``agent.wait`` 默认值：30 秒（仅为等待时间）；``timeoutMs`` 参数可覆盖该值。
- 代理运行时：``agents.defaults.timeoutSeconds`` 默认值为 600 秒；由 ``runEmbeddedPiAgent`` 中止计时器强制执行。

## 提前终止的场景

- 代理超时（中止）
- AbortSignal（取消）
- 网关断开连接或 RPC 超时
- ``agent.wait`` 超时（仅等待，不中止代理）