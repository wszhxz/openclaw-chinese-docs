---
summary: "Image and media handling rules for send, gateway, and agent replies"
read_when:
  - Modifying media pipeline or attachments
title: "Image and Media Support"
---
identity<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context and the key terms. The document is about WhatsApp channel support, specifically focusing on media handling rules, CLI commands, and various technical specifications.

First, I'll note the main sections: Goals, CLI Surface, WhatsApp Web channel behavior, Auto-Reply Pipeline, Inbound Media to Commands (Pi), Limits & Errors, and Notes for Tests. Each section has specific terminology and technical details that need accurate translation.

For the "Goals" section, terms like "send media with optional captions" should be translated to convey the optional nature. I'll make sure to use the correct technical terms for commands like `openclaw message send --media`. 

In the "CLI Surface" part, the command-line interface elements need to be translated carefully. For example, `--dry-run` and `--json` should remain as they are, but the descriptions should be in Chinese. I'll check if there are standard translations for these CLI options.

The "WhatsApp Web channel behavior" section has detailed media processing rules. Terms like "resize & recompress to JPEG" need precise translation. I'll ensure that technical specifications like "max side 2048px" are correctly converted to Chinese units and terms. Also, the mention of `agents.defaults.mediaMaxMb` and other variables should be kept as they are, possibly with explanations in parentheses if needed.

In the "Auto-Reply Pipeline" section, terms like "getReplyFromConfig" and "Docker sandbox" should be translated accurately. I'll need to make sure that the flow of the pipeline is clear in Chinese, especially when explaining how media is resolved and sent.

The "Inbound Media to Commands (Pi)" section involves templating variables and media processing. Terms like `{{MediaUrl}}` and `{{MediaPath}}` are placeholders and should remain as they are, but their descriptions need to be in Chinese. I'll also ensure that the explanation of how media is handled in a Docker sandbox is clear.

For the "Limits & Errors" section, the size limits and error handling need to be accurately translated. Terms like "oversize or unreadable media" should be translated to convey the technical issue clearly. The mention of specific file size limits (e.g., 10 MB, 20 MB) should be converted to Chinese units, and the note about skipping understanding for oversized media must be precise.

In the "Notes for Tests" section, the instructions for testing scenarios should be translated to maintain their original intent. Terms like "cover send + reply flows" and "validate recompression" need to be clear in Chinese to ensure testers understand the requirements.

Throughout the translation, I'll maintain the structure and formatting of the original document, ensuring that headings, bullet points, and code snippets are preserved. I'll also check for consistency in terminology, especially for repeated terms like "media" and "CLI." Proper nouns like "Baileys Web" and "OpenClaw" should remain in their original form, possibly with a brief explanation if needed.

I need to be cautious with technical jargon and ensure that the translated terms are standard in the Chinese technical community. For example, "MIME detection" should be translated to the appropriate technical term in Chinese. Also, terms like "dry-run" and "json" might not have direct translations, so I'll use the original terms with Chinese explanations if necessary.

Finally, I'll review the entire translation to ensure that it's accurate, maintains the original meaning, and is grammatically correct in Chinese. I'll check for any missed terms or formatting issues to ensure the document is clear and professional.
</think>

# 图像与媒体支持 — 2025-12-05

WhatsApp 通道通过 **Baileys Web** 运行。本文档记录了当前发送、网关和代理回复的媒体处理规则。

## 目标

- 通过 `openclaw message send --media` 发送带有可选说明文字的媒体。
- 允许网页收件箱的自动回复包含媒体与文本。
- 保持每类媒体的限制合理且可预测。

## CLI 接口

- `openclaw message send --media <路径或URL> [--message <说明文字>]`
  - `--media` 为可选参数；媒体仅发送时说明文字可为空。
  - `--dry-run` 会打印解析后的负载；`--json` 会输出 `{ channel, to, messageId, mediaUrl, caption }`。

## WhatsApp Web 通道行为

- 输入：本地文件路径 **或** HTTP(S) URL。
- 流程：加载到 Buffer 中，检测媒体类型，并构建正确的负载：
  - **图像**：调整大小并重新压缩为 JPEG（最大边长 2048 像素），目标为 `agents.defaults.mediaMaxMb`（默认 5 MB），上限为 6 MB。
  - **音频/语音/视频**：通过 16 MB 传输；音频以语音备忘录形式发送（`ptt: true`）。
  - **文档**：其他内容，上限为 100 MB，有文件名时保留原始文件名。
- WhatsApp GIF 风格播放：发送带有 `gifPlayback: true` 的 MP4（CLI：`--gif-playback`），以便移动端内联循环播放。
- MIME 检测优先使用魔术字节，然后是头部，最后是文件扩展名。
- 说明文字来自 `--message` 或 `reply.text`；允许空说明文字。
- 日志：非详细模式显示 `↩️`/`✅`；详细模式包含大小和源路径/URL。

## 自动回复流程

- `getReplyFromConfig` 返回 `{ text?, mediaUrl?, mediaUrls? }`。
- 当存在媒体时，网页发送方使用与 `openclaw message send` 相同的流程解析本地路径或 URL。
- 若提供多个媒体条目，将按顺序发送。

## 入站媒体到命令（Pi）

- 当入站网页消息包含媒体时，OpenClaw 会下载到临时文件，并暴露模板变量：
  - `{{MediaUrl}}` 伪 URL 表示入站媒体。
  - `{{MediaPath}}` 是运行命令前写入的本地临时路径。
- 当启用会话级 Docker 沙箱时，入站媒体会被复制到沙箱工作区，`MediaPath`/`MediaUrl` 会被重写为相对路径如 `media/inbound/<文件名>`。
- 媒体理解（若通过 `tools.media.*` 或共享 `tools.media.models` 配置）在模板化前运行，可将 `[Image]`、`[Audio]` 和 `[Video]` 块插入 `Body`。
  - 音频设置 `{{Transcript}}`，并使用转录内容进行命令解析，以便斜杠命令仍可使用。
  - 视频和图像描述保留任何说明文字供命令解析使用。
- 默认仅处理第一个匹配的图像/音频/视频附件；设置 `tools.media.<cap>.attachments` 可处理多个附件。

## 限制与错误

**出站发送限制（WhatsApp Web 发送）**

- 图像：重新压缩后约 6 MB 限制。
- 音频/语音/视频：16 MB 限制；文档：100 MB 限制。
- 超大或无法读取的媒体 → 日志中显示清除错误，回复将被跳过。

**媒体理解限制（转录/描述）**

- 图像默认：10 MB (`tools.media.image.maxBytes`)。
- 音频默认：20 MB (`tools.media.audio.maxBytes`)。
- 视频默认：50 MB (`tools.media.video.maxBytes`)。
- 超大媒体跳过理解，但回复仍使用原始正文进行。

## 测试注意事项

- 覆盖图像/音频/文档的发送 + 回复流程。
- 验证图像的重新压缩（大小限制）和音频的语音备忘录标志。
- 确保多媒体回复按顺序发送。