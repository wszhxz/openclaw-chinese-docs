---
summary: "Streaming + chunking behavior (block replies, draft streaming, limits)"
read_when:
  - Explaining how streaming or chunking works on channels
  - Changing block streaming or channel chunking behavior
  - Debugging duplicate/early block replies or draft streaming
title: "Streaming and Chunking"
---
# 流式传输 + 分块

OpenClaw 具有两个独立的“流式传输”层：

- **块流式传输（通道）：** 在助手编写时发出完整的**块**。这些是正常的通道消息（不是令牌增量）。
- **类似令牌的流式传输（仅限 Telegram）：** 在生成时使用部分文本更新**草稿气泡**；最终消息在结束时发送。

目前没有真正的**令牌流式传输**到外部通道消息。Telegram 草稿流式传输是唯一的部分流表面。

## 块流式传输（通道消息）

块流式传输会在助手输出可用时以粗粒度块的形式发送输出。

```
Model output
  └─ text_delta/events
       ├─ (blockStreamingBreak=text_end)
       │    └─ chunker emits blocks as buffer grows
       └─ (blockStreamingBreak=message_end)
            └─ chunker flushes at message_end
                   └─ channel send (block replies)
```

图例：

- `text_delta/events`: 模型流事件（对于非流式模型可能是稀疏的）。
- `chunker`: 应用最小/最大边界 + 断点首选项的 `EmbeddedBlockChunker`。
- `channel send`: 实际的出站消息（块回复）。

**控制：**

- `agents.defaults.blockStreamingDefault`: `"on"`/`"off"`（默认关闭）。
- 通道覆盖：`*.blockStreaming`（以及每个账户的变体）以强制每个通道的 `"on"`/`"off"`。
- `agents.defaults.blockStreamingBreak`: `"text_end"` 或 `"message_end"`。
- `agents.defaults.blockStreamingChunk`: `{ minChars, maxChars, breakPreference? }`。
- `agents.defaults.blockStreamingCoalesce`: `{ minChars?, maxChars?, idleMs? }`（在发送前合并流式传输的块）。
- 通道硬限制：`*.textChunkLimit`（例如，`channels.whatsapp.textChunkLimit`）。
- 通道块模式：`*.chunkMode`（默认为 `length`，`newline` 在长度分块前按空白行拆分）。
- Discord 软限制：`channels.discord.maxLinesPerMessage`（默认 17）拆分高回复以避免 UI 裁剪。

**边界语义：**

- `text_end`: 一旦分块器发出就流式传输块；在每个 `text_end` 上刷新。
- `message_end`: 等待助手消息完成，然后刷新缓冲输出。

`message_end` 如果缓冲文本超过 `maxChars` 仍然会使用分块器，因此可以在末尾发出多个块。

## 分块算法（低/高界限）

块分块由 `EmbeddedBlockChunker` 实现：

- **低界限：** 不要发出直到缓冲区 >= `minChars`（除非被强制）。
- **高界限：** 尽量在 `maxChars` 之前拆分；如果被强制，则在 `maxChars` 拆分。
- **断点首选项：** `paragraph` → `newline` → `sentence` → `whitespace` → 强制断开。
- **代码围栏：** 永不在围栏内拆分；当在 `maxChars` 被强制时，关闭并重新打开围栏以保持 Markdown 有效。

`maxChars` 受通道 `textChunkLimit` 的限制，因此不能超过每个通道的上限。

## 合并（合并流式传输的块）

启用块流式传输时，OpenClaw 可以在发送之前**合并连续的块块**。
这减少了“单行垃圾信息”，同时仍提供渐进式输出。

- 合并等待**空闲间隔** (`idleMs`) 之后刷新。
- 缓冲区受 `maxChars` 限制，如果超出则刷新。
- `minChars` 防止小片段在积累足够文本之前发送（最终刷新总是发送剩余文本）。
- 连接符派生自 `blockStreamingChunk.breakPreference`
  (`paragraph` → `\n\n`，`newline` → `\n`，`sentence` → 空格)。
- 通过 `*.blockStreamingCoalesce` 提供通道覆盖（包括每个账户的配置）。
- 默认合并 `minChars` 对于 Signal/Slack/Discord 提升到 1500，除非被覆盖。

## 块之间的类人节奏

启用块流式传输时，你可以在**块回复之间添加随机暂停**（在第一个块之后）。这使得多气泡响应感觉更自然。

- 配置：`agents.defaults.humanDelay`（通过 `agents.list[].humanDelay` 按代理覆盖）。
- 模式：`off`（默认），`natural`（800–2500毫秒），`custom` (`minMs`/`maxMs`)。
- 仅适用于**块回复**，不适用于最终回复或工具摘要。

## “流式传输块或全部”

这映射到：

- **流式传输块：** `blockStreamingDefault: "on"` + `blockStreamingBreak: "text_end"`（边生成边发送）。非 Telegram 通道还需要 `*.blockStreaming: true`。
- **结束时流式传输全部：** `blockStreamingBreak: "message_end"`（刷新一次，如果非常长可能会有多个块）。
- **无块流式传输：** `blockStreamingDefault: "off"`（仅最终回复）。

**通道说明：** 对于非 Telegram 通道，块流式传输**除非**显式设置 `*.blockStreaming` 为 `true` 否则是**关闭**的。Telegram 可以流式传输草稿（`channels.telegram.streamMode`）而无需块回复。

配置位置提醒：`blockStreaming*` 默认位于
`agents.defaults`，而不是根配置。

## Telegram 草稿流式传输（类似令牌）

Telegram 是唯一具有草稿流式传输的通道：

- 使用 Bot API `sendMessageDraft` 在**带有主题的私人聊天**中。
- `channels.telegram.streamMode: "partial" | "block" | "off"`。
  - `partial`: 使用最新的流式文本更新草稿。
  - `block`: 使用分块块更新草稿（相同的分块规则）。
  - `off`: 无草稿流式传输。
- 草稿块配置（仅适用于 `streamMode: "block"`）：`channels.telegram.draftChunk`（默认值：`minChars: 200`，`maxChars: 800`）。
- 草稿流式传输与块流式传输分开；块回复默认关闭，仅通过 `*.blockStreaming: true` 在非 Telegram 通道上启用。
- 最终回复仍然是正常消息。
- `/reasoning stream` 将推理写入草稿气泡（仅限 Telegram）。

当草稿流式传输处于活动状态时，OpenClaw 会禁用该回复的块流式传输以避免双重流式传输。

```
Telegram (private + topics)
  └─ sendMessageDraft (draft bubble)
       ├─ streamMode=partial → update latest text
       └─ streamMode=block   → chunker updates draft
  └─ final reply → normal message
```

图例：

- `sendMessageDraft`: Telegram 草稿气泡（不是真实消息）。
- `final reply`: 正常的 Telegram 消息发送。