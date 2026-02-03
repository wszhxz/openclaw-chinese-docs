---
summary: "Streaming + chunking behavior (block replies, draft streaming, limits)"
read_when:
  - Explaining how streaming or chunking works on channels
  - Changing block streaming or channel chunking behavior
  - Debugging duplicate/early block replies or draft streaming
title: "Streaming and Chunking"
---
# 流式传输 + 分块

OpenClaw 有两个独立的“流式传输”层：

- **块式流（频道）：** 在助手书写过程中，将完成的 **块** 作为消息发送。这些是普通的频道消息（非令牌增量）。
- **类似令牌的流式传输（仅限 Telegram）：** 在生成过程中，逐步更新一个 **草稿气泡**，最终消息在结束时发送。

目前 **没有真正的令牌流式传输** 到外部频道消息。Telegram 草稿流式传输是唯一支持部分流的接口。

## 块式流（频道消息）

块式流将助手的输出以较粗的块形式分段发送。

```
模型输出
  └─ text_delta/events
       ├─ (blockStreamingBreak=text_end)
       │    └─ chunker 在缓冲区增长时发出块
       └─ (blockStreamingBreak=message_end)
            └─ chunker 在 message_end 时刷新
                   └─ 频道发送（块回复）
```

术语说明：

- `text_delta/events`：模型流式事件（非流式模型可能稀疏）。
- `chunker`：应用最小/最大长度限制 + 分割偏好的 `EmbeddedBlockChunker`。
- `channel send`：实际的出站消息（块回复）。

**控制选项：**

- `agents.defaults.blockStreamingDefault`：`"on"`/`"off"`（默认关闭）。
- 频道覆盖：`*.blockStreaming`（及每个账户的变体）以强制 `"on"`/`"off"`。
- `agents.defaults.blockStreamingBreak`：`"text_end"` 或 `"message_end"`。
- `agents.defaults.block,StreamingChunk`：`{ minChars, maxChars, breakPreference? }`。
- `agents.defaults.blockStreamingCoalesce`：`{ minChars?, maxChars?, idleMs? }`（合并流式块后再发送）。
- 频道硬上限：`*.textChunkLimit`（例如 `channels.whatsapp.textChunkLimit`）。
- 频道分块模式：`*.chunkMode`（默认 `length`，`newline` 在段落边界前按空行分割）。
- Discord 软上限：`channels.discord.maxLinesPerMessage`（默认 17）分割高回复以避免 UI 被截断。

**边界语义：**

- `text_end`：一旦 chunker 发出块即流式传输；每个 `text_end` 都刷新。
- `message_end`：等待助手消息完成，然后刷新缓冲输出。

如果缓冲文本超过 `maxChars`，`message_end` 仍会使用 chunker，因此可以在最后发出多个块。

## 分块算法（低/高边界）

块式分块由 `EmbeddedBlockChunker` 实现：

- **低边界：** 缓冲区 >= `minChars` 时不发出（除非强制）。
- **高边界：** 优先在 `maxChars` 前分割；若强制，则在 `maxChars` 处分割。
- **分割偏好：** `paragraph` → `newline` → `sentence` → `whitespace` → 硬分割。
- **代码块：** 从不分割代码块内；若强制在 `maxChars` 处分割，则关闭 + 重新打开代码块以保持 Markdown 有效。

`maxChars` 会被限制在频道 `textChunkLimit`，因此无法超过每个频道的上限。

## 合并（合并流式块）

当块式流式传输启用时，OpenClaw 可以在发送前 **合并连续的块**，这减少了“单行垃圾信息”同时仍提供渐进式输出。

- 合并等待 **空闲间隙**（`idleMs`）后再刷新。
- 缓冲区受 `maxChars` 限制，若超过则刷新。
- `minChars` 防止小片段发送，直到足够文本累积（最终刷新始终发送剩余文本）。
- 合并器由 `blockStreamingChunk.breakPreference` 派生（`paragraph` → `\n\n`，`newline` → `\n`，`sentence` → 空格）。
- 频道覆盖可通过 `*.blockStreamingCoalesce`（包括每个账户配置）获取。
- 默认合并 `minChars` 除非被覆盖，否则 Signal/Slack/Discord 为 1500。

## 块之间的拟人化节奏

当块式流式传输启用时，你可以在第一个块后添加 **随机暂停** 以分隔块回复。这使多气泡响应感觉更自然。

- 配置：`agents.defaults.humanDelay`（通过 `agents.list[].humanDelay` 每个代理覆盖）。
- 模式：`off`（默认），`natural`（800–2500ms），`custom`（`min