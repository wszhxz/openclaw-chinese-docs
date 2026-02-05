---
summary: "Message flow, sessions, queueing, and reasoning visibility"
read_when:
  - Explaining how inbound messages become replies
  - Clarifying sessions, queueing modes, or streaming behavior
  - Documenting reasoning visibility and usage implications
title: "Messages"
---
# 消息

本页汇总了OpenClaw如何处理传入消息、会话、排队、流式传输和推理可见性。

## 消息流（高层次）

```
Inbound message
  -> routing/bindings -> session key
  -> queue (if a run is active)
  -> agent run (streaming + tools)
  -> outbound replies (channel limits + chunking)
```

关键设置位于配置中：

- `messages.*` 用于前缀、排队和组行为。
- `agents.defaults.*` 用于块流式传输和分块默认值。
- 频道覆盖 (`channels.whatsapp.*`, `channels.telegram.*` 等) 用于限制和流式传输开关。

参见 [配置](/gateway/configuration) 获取完整架构。

## 传入去重

频道在重新连接后可能会重新发送相同的消息。OpenClaw通过频道/账户/对等体/会话/消息ID作为键的短期缓存来防止重复交付触发另一个代理运行。

## 传入防抖

来自**同一发送者**的快速连续消息可以通过 `messages.inbound` 批量处理到单个代理轮次。防抖作用于每个频道 + 对话，并使用最近的消息进行回复线程/ID。

配置（全局默认 + 每频道覆盖）：

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

注意：

- 防抖仅适用于**纯文本**消息；媒体/附件会立即刷新。
- 控制命令绕过防抖，因此它们保持独立。

## 会话和设备

会话由网关拥有，而不是客户端。

- 直接聊天合并到代理主会话密钥。
- 组/频道获得自己的会话密钥。
- 会话存储和记录保存在网关主机上。

多个设备/频道可以映射到同一个会话，但历史记录不会完全同步回每个客户端。建议：使用一个主要设备进行长时间对话以避免上下文分歧。控制UI和TUI始终显示网关支持的会话记录，因此它们是权威来源。

详情：[会话管理](/concepts/session)。

## 传入正文和历史上下文

OpenClaw将**提示正文**与**命令正文**分开：

- `Body`：发送给代理的提示文本。这可能包括频道信封和可选的历史包装器。
- `CommandBody`：用于指令/命令解析的原始用户文本。
- `RawBody`：`CommandBody` 的旧别名（出于兼容性保留）。

当频道提供历史记录时，它使用共享包装器：

- `[Chat messages since your last reply - for context]`
- `[Current message - respond to this]`

对于**非直接聊天**（组/频道/房间），**当前消息正文**前面带有发送者标签（与历史条目使用的样式相同）。这保持实时和排队/历史消息在代理提示中的一致性。

历史缓冲区仅包含**待处理**的消息：它们包括未触发运行的组消息（例如，提及触发的消息）并**排除**已在会话记录中的消息。

指令剥离仅适用于**当前消息**部分，因此历史记录保持完整。包装历史记录的频道应将 `CommandBody`（或 `RawBody`）设置为原始消息文本，并保持 `Body` 为组合提示。历史缓冲区可通过 `messages.groupChat.historyLimit`（全局默认）和每频道覆盖（如 `channels.slack.historyLimit` 或 `channels.telegram.accounts.<id>.historyLimit`）进行配置（设置 `0` 以禁用）。

## 排队和后续操作

如果运行已经处于活动状态，传入消息可以排队、引导到当前运行，或收集用于后续轮次。

- 通过 `messages.queue`（和 `messages.queue.byChannel`）进行配置。
- 模式：`interrupt`，`steer`，`followup`，`collect`，以及回溯变体。

详情：[排队](/concepts/queue)。

## 流式传输、分块和批处理

块流式传输在模型生成文本块时发送部分回复。
分块尊重频道文本限制并避免拆分围栏代码。

关键设置：

- `agents.defaults.blockStreamingDefault` (`on|off`，默认关闭)
- `agents.defaults.blockStreamingBreak` (`text_end|message_end`)
- `agents.defaults.blockStreamingChunk` (`minChars|maxChars|breakPreference`)
- `agents.defaults.blockStreamingCoalesce`（基于空闲的批处理）
- `agents.defaults.humanDelay`（块回复之间的人类化暂停）
- 频道覆盖：`*.blockStreaming` 和 `*.blockStreamingCoalesce`（非Telegram频道需要显式 `*.blockStreaming: true`）

详情：[流式传输 + 分块](/concepts/streaming)。

## 推理可见性和令牌

OpenClaw可以暴露或隐藏模型推理：

- `/reasoning on|off|stream` 控制可见性。
- 当模型生成推理内容时，推理内容仍然计入令牌使用量。
- Telegram支持推理流到草稿气泡。

详情：[思考 + 推理指令](/tools/thinking) 和 [令牌使用](/token-use)。

## 前缀、线程和回复

传出消息格式在 `messages` 中集中：

- `messages.responsePrefix`，`channels.<channel>.responsePrefix`，和 `channels.<channel>.accounts.<id>.responsePrefix`（传出前缀级联），以及 `channels.whatsapp.messagePrefix`（WhatsApp传入前缀）
- 回复线程通过 `replyToMode` 和每频道默认值

详情：[配置](/gateway/configuration#messages) 和频道文档。