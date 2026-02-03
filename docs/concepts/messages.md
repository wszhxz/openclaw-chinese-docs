---
summary: "Message flow, sessions, queueing, and reasoning visibility"
read_when:
  - Explaining how inbound messages become replies
  - Clarifying sessions, queueing modes, or streaming behavior
  - Documenting reasoning visibility and usage implications
title: "Messages"
---
# 消息

本页面说明了OpenClaw如何处理入站消息、会话、排队、流式传输和推理可见性。

## 消息流程（高层次）

```
入站消息
  -> 路由/绑定 -> 会话密钥
  -> 队列（如果运行中）
  -> 代理运行（流式传输 + 工具）
  -> 出站回复（通道限制 + 分块）
```

关键配置项位于配置中：

- `messages.*` 用于前缀、排队和组行为。
- `agents.defaults.*` 用于块流式传输和分块的默认值。
- 通道覆盖（如 `channels.whatsapp.*`、`channels.telegram.*` 等）用于能力限制和流式传输开关。

完整模式请参见 [配置](/gateway/configuration)。

## 入站去重

通道在重新连接后可能会重新发送相同消息。OpenClaw会维护一个基于通道/账户/对等方/会话/消息ID的短生命周期缓存，以防止重复消息触发代理运行。

## 入站去抖

来自**同一发送者**的快速连续消息可通过 `messages.inbound` 处理为单个代理回合。去抖按通道 + 对话进行作用，并使用最新消息进行回复线程/ID处理。

配置（全局默认 + 每通道覆盖）：

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

说明：

- 去抖仅适用于**纯文本**消息；媒体/附件会立即刷新。
- 控制命令绕过去抖，因此保持独立。

## 会话和设备

会话由网关拥有，而非客户端。

- 直接聊天会合并到代理主会话密钥。
- 群组/频道会拥有自己的会话密钥。
- 会话存储和对话记录存储在网关主机上。

多个设备/频道可以映射到同一个会话，但历史记录不会完全同步回每个客户端。建议：在长对话中使用一个主要设备以避免上下文分歧。控制界面和TUI始终显示网关支持的会话对话记录，因此它们是真实来源。

详情：[会话管理](/concepts/session)。

## 入站正文和历史上下文

OpenClaw将**提示正文**与**命令正文**分离：

- `Body`：发送给代理的提示文本。可能包含通道信封和可选的历史记录包装器。
- `CommandBody`：用于指令/命令解析的原始用户文本。
- `RawBody`：`CommandBody` 的旧别名（保留兼容性）。

当通道提供历史记录时，它使用共享包装器：

- `[自上次回复以来的聊天消息 - 用于上下文]`
- `[当前消息 - 回复此消息]`

对于**非直接聊天**（群组/频道/房间），**当前消息正文**会以发送者标签开头（与历史记录条目使用相同样式）。这保持代理提示中实时和排队/历史消息的一致性。

历史记录缓冲区是**仅待处理**：它们包含未触发运行的群组消息（例如，提及保护消息），并**排除**已包含在会话对话记录中的消息。

指令剥离仅适用于**当前消息**部分，因此历史记录保持完整。包装历史记录的通道应将 `CommandBody`（或 `RawBody`）设置为原始消息文本，并将 `Body` 作为组合提示。历史记录缓冲区可通过 `messages.groupChat.historyLimit`（全局默认）和每通道覆盖（如 `channels.slack.historyLimit` 或 `channels.telegram.accounts.<id>.historyLimit`）进行配置（设置为 `0` 以禁用）。

## 排队和后续操作

如果已有运行，入站消息可以排队、引导至当前运行或收集用于后续回合。

- 通过 `messages.queue`（和 `messages.queue.byChannel`）进行配置。
- 模式：`interrupt`、`steer`、`followup`、`collect`，加上回溯变体。

详情：[排队](/concepts/queue)。

## 流式传输、分块和批处理

块流式传输在模型生成文本块时发送部分回复。分块尊重通道文本限制并避免分割代码块。

关键设置：

- `agents.defaults.blockStreamingDefault`（`on|off`，默认关闭）
- `agents.defaults.blockStreamingBreak`（`text_end|message_end`）
- `agents.defaults.blockStreamingChunk`（`minChars|maxChars|breakPreference`）
- `agents.defaults.blockStreamingCoalesce`（基于空闲的批处理）
- `agents.defaults.humanDelay`（块回复之间的拟人暂停）
- 通道覆盖：`*.blockStreaming` 和 `*.blockStreamingCoalesce`（非Telegram通道需要显式 `*.blockStreaming: true`）

详情：[流式传输 + 分块](/concepts/streaming)。

## 推理可见性和令牌

OpenClaw可以暴露或隐藏模型推理：

- `/reasoning on|off|stream` 控制可见性。
- 模型生成的推理内容仍计入令牌使用。
- Telegram支持将推理流式传输到草稿气泡中。

详情：[思考 + 推理指令](/tools/thinking) 和 [令牌使用](/token-use)。

## 前缀、线程和回复

出站消息格式化在 `messages` 中集中处理：

- `messages.responsePrefix`（出站前缀）和 `channels.whatsapp.messagePrefix`（WhatsApp入站前缀）
- 通过 `replyToMode` 和每通道默认值进行回复线程

详情：[配置](/gateway/configuration#messages) 和通道文档。