---
summary: "Streaming + chunking behavior (block replies, channel preview streaming, mode mapping)"
read_when:
  - Explaining how streaming or chunking works on channels
  - Changing block streaming or channel chunking behavior
  - Debugging duplicate/early block replies or channel preview streaming
title: "Streaming and Chunking"
---
# 流式传输 + 分块

OpenClaw 具有两个独立的流式传输层：

- **块流式传输（通道）：** 在助手编写时发出完整的**块**。这些是正常的通道消息（不是令牌增量）。
- **预览流式传输（Telegram/Discord/Slack）：** 在生成时更新临时**预览消息**。

目前没有真正的**令牌增量流式传输**到通道消息。预览流式传输是基于消息的（发送 + 编辑/追加）。

## 块流式传输（通道消息）

块流式传输在助手输出可用时以粗粒度块的形式发送。

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

- `text_delta/events`: 模型流事件（对于非流式传输模型可能是稀疏的）。
- `chunker`: `EmbeddedBlockChunker` 应用最小/最大边界 + 断点偏好。
- `channel send`: 实际的出站消息（块回复）。

**控制：**

- `agents.defaults.blockStreamingDefault`: `"on"`/`"off"`（默认关闭）。
- 通道覆盖：`*.blockStreaming`（以及每个账户的变体）以强制每个通道的 `"on"`/`"off"`。
- `agents.defaults.blockStreamingBreak`: `"text_end"` 或 `"message_end"`。
- `agents.defaults.blockStreamingChunk`: `{ minChars, maxChars, breakPreference? }`。
- `agents.defaults.blockStreamingCoalesce`: `{ minChars?, maxChars?, idleMs? }`（在发送前合并流式传输的块）。
- 通道硬限制：`*.textChunkLimit`（例如，`channels.whatsapp.textChunkLimit`）。
- 通道分块模式：`*.chunkMode`（默认为 `length`，`newline` 在长度分块前按空白行拆分）。
- Discord 软限制：`channels.discord.maxLinesPerMessage`（默认 17）拆分高回复以避免界面裁剪。

**边界语义：**

- `text_end`: 一旦分块器发出就流式传输块；在每个 `text_end` 处刷新。
- `message_end`: 等待助手消息完成，然后刷新缓冲的输出。

`message_end` 如果缓冲的文本超过 `maxChars`，仍然使用分块器，因此可以在末尾发出多个块。

## 分块算法（低/高边界）

块分块由 `EmbeddedBlockChunker` 实现：

- **低边界：** 不要发出直到缓冲区 >= `minChars`（除非强制）。
- **高边界：** 尽量在 `maxChars` 之前拆分；如果强制，则在 `maxChars` 拆分。
- **断点偏好：** `paragraph` → `newline` → `sentence` → `whitespace` → 强制断点。
- **代码围栏：** 永不拆分围栏内部；当在 `maxChars` 强制拆分时，关闭并重新打开围栏以保持 Markdown 有效。

`maxChars` 受通道 `textChunkLimit` 的限制，因此不能超出每个通道的限制。

## 合并（合并流式传输的块）

当启用块流式传输时，OpenClaw 可以在发送之前**合并连续的块块**。
这减少了“单行垃圾信息”，同时仍提供渐进输出。

- 合并等待**空闲间隔** (`idleMs`) 之后刷新。
- 缓冲区受 `maxChars` 限制，如果超过则刷新。
- `minChars` 防止在积累足够的文本之前发送微小片段（最终刷新总是发送剩余文本）。
- 连接符派生自 `blockStreamingChunk.breakPreference`
  (`paragraph` → `\n\n`，`newline` → `\n`，`sentence` → 空格)。
- 通过 `*.blockStreamingCoalesce` 提供通道覆盖（包括每个账户的配置）。
- 默认合并 `minChars` 对于 Signal/Slack/Discord 提升到 1500，除非被覆盖。

## 块之间的类人节奏

当启用块流式传输时，你可以在**块回复之间添加随机暂停**（在第一个块之后）。这使多气泡响应感觉更自然。

- 配置：`agents.defaults.humanDelay`（通过 `agents.list[].humanDelay` 按代理覆盖）。
- 模式：`off`（默认），`natural`（800–2500毫秒），`custom` (`minMs`/`maxMs`)。
- 仅适用于**块回复**，不适用于最终回复或工具摘要。

## “流式传输块或全部”

这映射到：

- **流式传输块：** `blockStreamingDefault: "on"` + `blockStreamingBreak: "text_end"`（逐个发出）。非 Telegram 通道还需要 `*.blockStreaming: true`。
- **结束时流式传输全部：** `blockStreamingBreak: "message_end"`（刷新一次，如果非常长可能有多个块）。
- **无块流式传输：** `blockStreamingDefault: "off"`（仅最终回复）。

**通道说明：** 块流式传输**除非**显式设置 `*.blockStreaming` 为 `true` 否则**关闭**。通道可以流式传输实时预览 (`channels.<channel>.streaming`) 而不进行块回复。

配置位置提醒：`blockStreaming*` 默认位于
`agents.defaults` 下，而不是根配置。

## 预览流式传输模式

规范键：`channels.<channel>.streaming`

模式：

- `off`: 禁用预览流式传输。
- `partial`: 单个预览，被最新的文本替换。
- `block`: 分块/追加步骤中的预览更新。
- `progress`: 生成期间的进度/状态预览，完成时给出最终答案。

### 通道映射

| 通道   | `off` | `partial` | `block` | `progress`        |
| ------ | ----- | --------- | ------- | ----------------- |
| Telegram | ✅    | ✅        | ✅      | 映射到 `partial` |
| Discord  | ✅    | ✅        | ✅      | 映射到 `partial` |
| Slack    | ✅    | ✅        | ✅      | ✅                |

仅限 Slack：

- `channels.slack.nativeStreaming` 在 `streaming=partial` 时切换 Slack 原生流式传输 API 调用（默认：`true`）。

遗留键迁移：

- Telegram: `streamMode` + 布尔值 `streaming` 自动迁移到 `streaming` 枚举。
- Discord: `streamMode` + 布尔值 `streaming` 自动迁移到 `streaming` 枚举。
- Slack: `streamMode` 自动迁移到 `streaming` 枚举；布尔值 `streaming` 自动迁移到 `nativeStreaming`。

### 运行时行为

Telegram：

- 使用 Bot API `sendMessage` + `editMessageText`。
- 当显式启用 Telegram 块流式传输时跳过预览流式传输（以避免双重流式传输）。
- `/reasoning stream` 可以在预览中写入推理。

Discord：

- 使用发送 + 编辑预览消息。
- `block` 模式使用草稿分块 (`draftChunk`)。
- 当显式启用 Discord 块流式传输时跳过预览流式传输。

Slack：

- `partial` 可以在可用时使用 Slack 原生流式传输 (`chat.startStream`/`append`/`stop`)。
- `block` 使用追加样式的草稿预览。
- `progress` 使用状态预览文本，然后给出最终答案。