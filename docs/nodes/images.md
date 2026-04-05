---
summary: "Image and media handling rules for send, gateway, and agent replies"
read_when:
  - Modifying media pipeline or attachments
title: "Image and Media Support"
---
# 图像与媒体支持 (2025-12-05)

WhatsApp 渠道通过 **Baileys Web** 运行。本文档记录了当前用于发送、网关和代理回复的媒体处理规则。

## 目标

- 通过 `openclaw message send --media` 发送带可选说明文字的媒体。
- 允许来自网页收件箱的自动回复包含媒体和文本。
- 保持每种类型的限制合理且可预测。

## CLI 接口

- `openclaw message send --media <path-or-url> [--message <caption>]`
  - `--media` 为可选；仅发送媒体时说明文字可以为空。
  - `--dry-run` 打印解析后的负载；`--json` 输出 `{ channel, to, messageId, mediaUrl, caption }`。

## WhatsApp Web 渠道行为

- 输入：本地文件路径 **或** HTTP(S) URL。
- 流程：加载到 Buffer，检测媒体类型，并构建正确的负载：
  - **Images:** 调整大小并重新压缩为 JPEG（最大边长 2048px），目标为 `channels.whatsapp.mediaMaxMb`（默认：50 MB）。
  - **Audio/Voice/Video:** 透传至 16 MB；音频作为语音笔记发送 (`ptt: true`)。
  - **Documents:** 其他所有内容，最多 100 MB，在可用时保留文件名。
- WhatsApp GIF 风格播放：发送带有 `gifPlayback: true` 的 MP4（CLI: `--gif-playback`），以便移动客户端内联循环播放。
- MIME 检测优先使用魔术字节，然后是头部，最后是文件扩展名。
- 说明文字来自 `--message` 或 `reply.text`；允许空说明文字。
- 日志记录：非详细模式显示 `↩️`/`✅`；详细模式包括大小和源路径/URL。

## 自动回复管道

- `getReplyFromConfig` 返回 `{ text?, mediaUrl?, mediaUrls? }`。
- 当存在媒体时，网页发送器使用与 `openclaw message send` 相同的管道解析本地路径或 URL。
- 如果提供了多个媒体条目，则按顺序发送。

## 入站媒体到命令 (Pi)

- 当入站网页消息包含媒体时，OpenClaw 下载到临时文件并暴露模板变量：
  - `{{MediaUrl}}` 入站媒体的伪 URL。
  - `{{MediaPath}}` 运行命令前写入的本地临时路径。
- 当启用每会话 Docker 沙箱时，入站媒体被复制到沙箱工作区，并且 `MediaPath`/`MediaUrl` 被重写为类似 `media/inbound/<filename>` 的相对路径。
- 媒体理解（如果通过 `tools.media.*` 或共享 `tools.media.models` 配置）在模板化之前运行，并可以向 `Body` 插入 `[Image]`、`[Audio]` 和 `[Video]` 块。
  - 音频设置 `{{Transcript}}` 并使用转录进行命令解析，以便斜杠命令仍然有效。
  - 视频和图片描述保留任何说明文字以用于命令解析。
  - 如果活动的主图像模型原生支持视觉，OpenClaw 跳过 `[Image]` 摘要块，并将原始图像传递给模型。
- 默认情况下仅处理第一个匹配的图像/音频/视频附件；设置 `tools.media.<cap>.attachments` 以处理多个附件。

## 限制与错误

**出站发送上限 (WhatsApp web send)**

- 图像：重新压缩后最多 `channels.whatsapp.mediaMaxMb`（默认：50 MB）。
- 音频/语音/视频：16 MB 上限；文档：100 MB 上限。
- 超大或无法读取的媒体 → 日志中显示清晰错误，且跳过回复。

**媒体理解上限 (转录/描述)**

- 图像默认：10 MB (`tools.media.image.maxBytes`)。
- 音频默认：20 MB (`tools.media.audio.maxBytes`)。
- 视频默认：50 MB (`tools.media.video.maxBytes`)。
- 超大媒体跳过理解，但回复仍会通过原始正文发送。

## 测试注意事项

- 覆盖图像/音频/文档情况的发送 + 回复流程。
- 验证图像的重新压缩（大小限制）和音频的语音笔记标志。
- 确保多媒体回复像顺序发送一样分发。