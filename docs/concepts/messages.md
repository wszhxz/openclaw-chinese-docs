---
summary: "Message flow, sessions, queueing, and reasoning visibility"
read_when:
  - Explaining how inbound messages become replies
  - Clarifying sessions, queueing modes, or streaming behavior
  - Documenting reasoning visibility and usage implications
title: "Messages"
---
# 消息

本页整合说明了 OpenClaw 如何处理入站消息、会话、队列、流式传输以及推理可见性。

## 消息流向（高层级）

```
Inbound message
  -> routing/bindings -> session key
  -> queue (if a run is active)
  -> agent run (streaming + tools)
  -> outbound replies (channel limits + chunking)
```

关键配置项位于配置文件中：

- `messages.*` 用于前缀、队列及群组行为。
- `agents.defaults.*` 用于块流式传输与分块的默认设置。
- 通道级覆盖项（如 `channels.whatsapp.*`、`channels.telegram.*` 等）用于限制和流式传输开关。

完整配置模式请参阅 [配置](/gateway/configuration)。

## 入站去重

通道可能在重连后重复投递相同消息。OpenClaw 维护一个短生命周期缓存，以“通道/账号/对端/会话/消息 ID”为键，确保重复投递不会触发另一次智能体运行。

## 入站防抖

来自**同一发送方**的快速连续消息可通过 `messages.inbound` 批量合并为单次智能体回合。防抖作用域限定于“通道 + 对话”，并采用最新一条消息用于回复线程/ID 关联。

配置（全局默认值 + 通道级覆盖）：

```json5
{
  messages: {
    inbound: {
      debounceMs: 2000,
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
        discord: 1500,
      },
    },
  },
}
```

注意事项：

- 防抖仅适用于**纯文本消息**；媒体/附件将立即刷新。
- 控制指令绕过防抖机制，以确保其保持独立。

## 会话与设备

会话由网关拥有，而非客户端。

- 直接聊天会折叠至智能体主会话密钥下。
- 群组/频道拥有各自独立的会话密钥。
- 会话存储与对话记录均驻留在网关主机上。

多个设备/通道可映射到同一会话，但历史记录并不会完全同步回每个客户端。建议：在长对话中使用一台主设备，以避免上下文分歧。控制界面（Control UI）与终端界面（TUI）始终显示网关托管的会话记录，因此它们是事实真相的唯一来源。

详情请参阅：[会话管理](/concepts/session)。

## 入站消息体与历史上下文

OpenClaw 将**提示正文（prompt body）** 与**指令正文（command body）** 分离：

- `Body`：发送给智能体的提示文本。其中可能包含通道信封及可选的历史包装器。
- `CommandBody`：原始用户文本，用于指令/命令解析。
- `RawBody`：`CommandBody` 的遗留别名（为兼容性保留）。

当通道提供历史记录时，统一使用共享包装器：

- `[Chat messages since your last reply - for context]`
- `[Current message - respond to this]`

对于**非直接聊天**（群组/频道/房间），**当前消息正文**会在开头添加发送者标签（样式与历史条目一致）。此举可确保实时消息与队列/历史消息在智能体提示中保持格式一致。

历史缓冲区为**待处理型（pending-only）**：仅包含**未触发运行**的群组消息（例如受提及条件限制的消息），且**排除**已存在于会话记录中的消息。

指令剥离仅应用于**当前消息**部分，从而保证历史内容保持完整。对历史进行包装的通道应将 `CommandBody`（或 `RawBody`）设为原始消息文本，并将 `Body` 保留为组合后的提示。历史缓冲区可通过 `messages.groupChat.historyLimit`（全局默认值）及通道级覆盖项（如 `channels.slack.historyLimit` 或 `channels.telegram.accounts.<id>.historyLimit`）进行配置（设置 `0` 可禁用该功能）。

## 队列与后续处理

若已有运行正在进行，新入站消息可被加入队列、引导至当前运行，或收集用于后续回合。

- 通过 `messages.queue`（及 `messages.queue.byChannel`）进行配置。
- 支持模式：`interrupt`、`steer`、`followup`、`collect`，以及对应的历史积压（backlog）变体。

详情请参阅：[队列](/concepts/queue)。

## 流式传输、分块与批处理

块流式传输（block streaming）会在模型生成文本块的同时，将部分回复即时发出。分块（chunking）则尊重通道的文本长度限制，并避免分割围栏代码块（fenced code）。

关键设置项：

- `agents.defaults.blockStreamingDefault`（`on|off`，缺省关闭）
- `agents.defaults.blockStreamingBreak`（`text_end|message_end`）
- `agents.defaults.blockStreamingChunk`（`minChars|maxChars|breakPreference`）
- `agents.defaults.blockStreamingCoalesce`（基于空闲时间的批处理）
- `agents.defaults.humanDelay`（块回复之间模拟人类停顿）
- 通道级覆盖项：`*.blockStreaming` 和 `*.blockStreamingCoalesce`（非 Telegram 通道需显式启用 `*.blockStreaming: true`）

详情请参阅：[流式传输 + 分块](/concepts/streaming)。

## 推理可见性与 Token 使用

OpenClaw 可选择公开或隐藏模型推理过程：

- `/reasoning on|off|stream` 控制其可见性。
- 当模型生成推理内容时，该内容仍计入 Token 消耗总量。
- Telegram 支持将推理流式输出至草稿气泡（draft bubble）中。

详情请参阅：[思考与推理指令](/tools/thinking) 及 [Token 使用](/reference/token-use)。

## 前缀、线程化与回复

出站消息格式统一由 `messages` 集中管理：

- `messages.responsePrefix`、`channels.<channel>.responsePrefix` 与 `channels.<channel>.accounts.<id>.responsePrefix`（出站前缀级联），以及 `channels.whatsapp.messagePrefix`（WhatsApp 入站前缀）
- 通过 `replyToMode` 实现回复线程化，并支持各通道默认设置

详情请参阅：[配置](/gateway/configuration#messages) 及各通道文档。