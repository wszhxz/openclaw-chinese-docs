---
summary: "Streaming + chunking behavior (block replies, channel preview streaming, mode mapping)"
read_when:
  - Explaining how streaming or chunking works on channels
  - Changing block streaming or channel chunking behavior
  - Debugging duplicate/early block replies or channel preview streaming
title: "Streaming and Chunking"
---
# 流式传输 + 分块

OpenClaw 有两个独立的流式传输层：

- **块流式传输（频道）：** 随着助手写入内容，发出已完成的**块**。这些是正常的频道消息（不是 token 增量）。
- **预览流式传输（Telegram/Discord/Slack）：** 生成时更新临时**预览消息**。

目前**没有真正的 token 增量流式传输**到频道消息。预览流式传输是基于消息的（发送 + 编辑/追加）。

## 块流式传输（频道消息）

块流式传输在助手输出可用时，以粗粒度块的形式发送。

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

- `text_delta/events`：模型流事件（对于非流式模型可能稀疏）。
- `chunker`：`EmbeddedBlockChunker` 应用最小/最大边界 + 断点偏好。
- `channel send`：实际出站消息（块回复）。

**控制项：**

- `agents.defaults.blockStreamingDefault`：`"on"`/`"off"`（默认关闭）。
- 频道覆盖：`*.blockStreaming`（及每账户变体）以强制每个频道的 `"on"`/`"off"`。
- `agents.defaults.blockStreamingBreak`：`"text_end"` 或 `"message_end"`。
- `agents.defaults.blockStreamingChunk`：`{ minChars, maxChars, breakPreference? }`。
- `agents.defaults.blockStreamingCoalesce`：`{ minChars?, maxChars?, idleMs? }`（发送前合并流式块）。
- 频道硬上限：`*.textChunkLimit`（例如，`channels.whatsapp.textChunkLimit`）。
- 频道分块模式：`*.chunkMode`（`length` 默认，`newline` 在长度分块前按空行（段落边界）分割）。
- Discord 软上限：`channels.discord.maxLinesPerMessage`（默认 17）分割长回复以避免 UI 裁剪。

**边界语义：**

- `text_end`：分块器发出后立即流式传输块；每次 `text_end` 刷新。
- `message_end`：等待助手消息完成，然后刷新缓冲输出。

`message_end` 仍会使用分块器，如果缓冲文本超过 `maxChars`，因此它可以在结束时发出多个块。

## 分块算法（低/高边界）

块分块由 `EmbeddedBlockChunker` 实现：

- **低边界：** 除非强制，否则直到缓冲区 >= `minChars` 才发出。
- **高边界：** 优先在 `maxChars` 之前分割；如果强制，在 `maxChars` 分割。
- **断点偏好：** `paragraph` → `newline` → `sentence` → `whitespace` → 硬断点。
- **代码围栏：** 绝不在围栏内分割；当在 `maxChars` 强制时，关闭 + 重新打开围栏以保持 Markdown 有效。

`maxChars` 被限制在频道 `textChunkLimit` 范围内，因此您不能超过每频道上限。

## 合并（合并流式块）

启用块流式传输时，OpenClaw 可以**合并连续的块片段**
在发送它们之前。这减少了“单行垃圾信息”，同时仍提供
渐进式输出。

- 合并等待**空闲间隙**（`idleMs`）后再刷新。
- 缓冲区由 `maxChars` 限制，如果超过将刷新。
- `minChars` 防止微小片段发送，直到积累足够文本
  （最终刷新总是发送剩余文本）。
- 连接符源自 `blockStreamingChunk.breakPreference`
  （`paragraph` → `\n\n`，`newline` → `\n`，`sentence` → 空格）。
- 可通过 `*.blockStreamingCoalesce` 使用频道覆盖（包括每账户配置）。
- 默认合并 `minChars` 对于 Signal/Slack/Discord 提升至 1500，除非被覆盖。

## 块之间的人性化节奏

启用块流式传输时，您可以在之间添加**随机暂停**
块回复（第一个块之后）。这使得多气泡回复感觉
更自然。

- 配置：`agents.defaults.humanDelay`（通过 `agents.list[].humanDelay` 每代理覆盖）。
- 模式：`off`（默认），`natural` (800–2500ms)，`custom` (`minMs`/`maxMs`)。
- 仅适用于**块回复**，不适用于最终回复或工具摘要。

## “流式传输块或全部内容”

这映射到：

- **流式传输块：** `blockStreamingDefault: "on"` + `blockStreamingBreak: "text_end"`（边生成边发出）。非 Telegram 频道还需要 `*.blockStreaming: true`。
- **结束时流式传输全部内容：** `blockStreamingBreak: "message_end"`（刷新一次，如果非常长可能是多个块）。
- **无块流式传输：** `blockStreamingDefault: "off"`（仅最终回复）。

**频道注意：** 块流式传输**关闭，除非**
`*.blockStreaming` 显式设置为 `true`。频道可以流式传输实时预览
（`channels.<channel>.streaming`）而不进行块回复。

配置位置提醒：`blockStreaming*` 默认值位于
`agents.defaults` 下，而不是根配置。

## 预览流式传输模式

规范键：`channels.<channel>.streaming`

模式：

- `off`：禁用预览流式传输。
- `partial`：单个预览，被最新文本替换。
- `block`：预览以分块/追加步骤更新。
- `progress`：生成期间的进度/状态预览，完成时显示最终答案。

### 频道映射

| Channel  | `off` | `partial` | `block` | `progress`        |
| -------- | ----- | --------- | ------- | ----------------- |
| Telegram | ✅    | ✅        | ✅      | 映射到 `partial` |
| Discord  | ✅    | ✅        | ✅      | 映射到 `partial` |
| Slack    | ✅    | ✅        | ✅      | ✅                |

仅 Slack：

- `channels.slack.nativeStreaming` 当 `streaming=partial` 时切换 Slack 原生流式传输 API 调用（默认：`true`）。

旧键迁移：

- Telegram：`streamMode` + 布尔值 `streaming` 自动迁移到 `streaming` 枚举。
- Discord：`streamMode` + 布尔值 `streaming` 自动迁移到 `streaming` 枚举。
- Slack：`streamMode` 自动迁移到 `streaming` 枚举；布尔值 `streaming` 自动迁移到 `nativeStreaming`。

### 运行时行为

Telegram：

- 可用时在 DMs 中使用 Bot API `sendMessageDraft`，并使用 `sendMessage` + `editMessageText` 进行群组/主题预览更新。
- 当显式启用 Telegram 块流式传输时，跳过预览流式传输（以避免双重流式传输）。
- `/reasoning stream` 可以将推理写入预览。

Discord：

- 使用发送 + 编辑预览消息。
- `block` 模式使用草稿分块（`draftChunk`）。
- 当显式启用 Discord 块流式传输时，跳过预览流式传输。

Slack：

- `partial` 可用时可以使用 Slack 原生流式传输（`chat.startStream`/`append`/`stop`）。
- `block` 使用追加式草稿预览。
- `progress` 使用状态预览文本，然后是最终答案。