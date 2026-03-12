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

- **块流式传输（频道）**：在助手书写过程中，按完成的 **块（blocks）** 发送。这些是常规频道消息（非 token 差量）。
- **预览流式传输（Telegram/Discord/Slack）**：在生成过程中持续更新一条临时的 **预览消息（preview message）**。

目前**尚无真正的 token 差量流式传输**至频道消息。预览流式传输基于消息（发送 + 编辑/追加）。

## 块流式传输（频道消息）

块流式传输将助手输出以粗粒度分块方式，在内容就绪时即刻发出。

```
Model output
  └─ text_delta/events
       ├─ (blockStreamingBreak=text_end)
       │    └─ chunker emits blocks as buffer grows
       └─ (blockStreamingBreak=message_end)
            └─ chunker flushes at message_end
                   └─ channel send (block replies)
```

图例说明：

- `text_delta/events`：模型流事件（对非流式模型可能较稀疏）。
- `chunker`：`EmbeddedBlockChunker` 应用最小/最大边界值及断点偏好设置。
- `channel send`：实际外发消息（块式回复）。

**控制项：**

- `agents.defaults.blockStreamingDefault`：`"on"`/`"off"`（默认关闭）。
- 频道覆盖配置：`*.blockStreaming`（及其按账号变体），用于强制每频道启用 `"on"`/`"off"`。
- `agents.defaults.blockStreamingBreak`：`"text_end"` 或 `"message_end"`。
- `agents.defaults.blockStreamingChunk`：`{ minChars, maxChars, breakPreference? }`。
- `agents.defaults.blockStreamingCoalesce`：`{ minChars?, maxChars?, idleMs? }`（在发送前合并已流式传输的块）。
- 频道硬性上限：`*.textChunkLimit`（例如：`channels.whatsapp.textChunkLimit`）。
- 频道分块模式：`*.chunkMode`（默认为 `length`；`newline` 在空白行（段落边界）处分割，再进行长度分块）。
- Discord 软性上限：`channels.discord.maxLinesPerMessage`（默认为 17），用于分割过长回复，避免 UI 截断。

**边界语义：**

- `text_end`：分块器一旦输出块即刻流式发送；每次遇到 `text_end` 即刷新。
- `message_end`：等待助手消息完全结束，再刷新缓冲输出。

即使启用 `message_end`，若缓冲文本超出 `maxChars`，仍会使用分块器，因此可在结尾处发出多个块。

## 分块算法（低/高边界）

块分块由 `EmbeddedBlockChunker` 实现：

- **低边界**：缓冲区未达 `minChars` 时不发出（除非强制）。
- **高边界**：优先在 `maxChars` 之前分割；若强制分割，则在 `maxChars` 处切分。
- **断点偏好**：`paragraph` → `newline` → `sentence` → `whitespace` → 强制断点。
- **代码围栏（code fences）**：绝不在围栏内部分割；若在 `maxChars` 处强制分割，则先关闭再重新打开围栏，以确保 Markdown 有效性。

`maxChars` 会被限制在频道的 `textChunkLimit` 范围内，因此无法超出各频道设定的上限。

## 合并（合并已流式传输的块）

启用块流式传输时，OpenClaw 可在发送前**合并连续的块分块**。  
此举可减少“单行刷屏”，同时仍提供渐进式输出。

- 合并机制等待**空闲间隔（idle gaps）**（`idleMs`）后才刷新。
- 缓冲区受 `maxChars` 限制，超出即强制刷新。
- `minChars` 防止微小片段过早发送，直至积累足够文本（最终刷新总会发送剩余文本）。
- 连接符（joiner）源自 `blockStreamingChunk.breakPreference`（`paragraph` → `\n\n`，`newline` → `\n`，`sentence` → 空格）。
- 频道覆盖配置可通过 `*.blockStreamingCoalesce` 设置（含按账号配置）。
- 默认合并 `minChars` 对 Signal/Slack/Discord 提升至 1500，除非另行覆盖。

## 块间类人节奏控制

启用块流式传输时，可在**块回复之间（首块之后）添加随机化暂停**，使多气泡回复更显自然。

- 配置项：`agents.defaults.humanDelay`（可通过 `agents.list[].humanDelay` 按代理覆盖）。
- 模式：`off`（默认）、`natural`（800–2500ms）、`custom`（`minMs`/`maxMs`）。
- 仅适用于 **块回复**，不适用于最终回复或工具摘要。

## “流式传输分块 or 全部一次性传输”

对应关系如下：

- **流式传输分块**：`blockStreamingDefault: "on"` + `blockStreamingBreak: "text_end"`（边生成边发出）。非 Telegram 频道还需启用 `*.blockStreaming: true`。
- **全部于结尾流式传输**：`blockStreamingBreak: "message_end"`（仅刷新一次；若内容极长，可能仍分多个块）。
- **禁用块流式传输**：`blockStreamingDefault: "off"`（仅发送最终回复）。

**频道说明**：块流式传输**默认关闭**，除非显式将 `*.blockStreaming` 设为 `true`。频道可在不启用块回复的前提下，流式传输实时预览（`channels.<channel>.streaming`）。

配置位置提示：`blockStreaming*` 的默认值位于 `agents.defaults` 下，而非根配置中。

## 预览流式传输模式

标准键名：`channels.<channel>.streaming`

模式：

- `off`：禁用预览流式传输。
- `partial`：单条预览消息，始终被最新文本替换。
- `block`：预览消息以分块/追加方式逐步更新。
- `progress`：生成期间显示进度/状态预览，完成后呈现最终答案。

### 频道映射表

| 频道     | `off` | `partial` | `block` | `progress`        |
| -------- | ----- | --------- | ------- | ----------------- |
| Telegram | ✅    | ✅        | ✅      | 映射至 `partial` |
| Discord  | ✅    | ✅        | ✅      | 映射至 `partial` |
| Slack    | ✅    | ✅        | ✅      | ✅                |

Slack 专属功能：

- `channels.slack.nativeStreaming` 在启用 `streaming=partial`（默认：`true`）时，切换 Slack 原生流式传输 API 调用。

旧版键名迁移说明：

- Telegram：`streamMode` + 布尔型 `streaming` 自动迁移至枚举型 `streaming`。
- Discord：`streamMode` + 布尔型 `streaming` 自动迁移至枚举型 `streaming`。
- Slack：`streamMode` 自动迁移至枚举型 `streaming`；布尔型 `streaming` 自动迁移至 `nativeStreaming`。

### 运行时行为

Telegram：

- 私聊（DMs）中，若可用则使用 Bot API 的 `sendMessageDraft`；群组/主题中则使用 `sendMessage` + `editMessageText` 更新预览。
- 当 Telegram 块流式传输被显式启用时，跳过预览流式传输（避免双重流式）。
- `/reasoning stream` 可将推理过程写入预览。

Discord：

- 使用发送 + 编辑预览消息。
- `block` 模式采用草稿分块（`draftChunk`）。
- 当 Discord 块流式传输被显式启用时，跳过预览流式传输。

Slack：

- `partial` 在可用时可启用 Slack 原生流式传输（`chat.startStream`/`append`/`stop`）。
- `block` 使用追加式草稿预览。
- `progress` 使用状态预览文本，完成后展示最终答案。