---
summary: "Image and media handling rules for send, gateway, and agent replies"
read_when:
  - Modifying media pipeline or attachments
title: "Image and Media Support"
---
# 图像与媒体支持 — 2025-12-05

WhatsApp 通道通过 **Baileys Web** 运行。本文件记录了当前的媒体处理规则，包括发送、网关和代理回复。

## 目标

- 通过 `openclaw message send --media` 发送带有可选标题的媒体。
- 允许网页收件箱中的自动回复包含文本和媒体。
- 保持每种类型的限制合理且可预测。

## 命令行界面

- `openclaw message send --media <path-or-url> [--message <caption>]`
  - `--media` 可选；仅发送媒体时标题可以为空。
  - `--dry-run` 打印解析后的负载；`--json` 发出 `{ channel, to, messageId, mediaUrl, caption }`。

## WhatsApp Web 通道行为

- 输入：本地文件路径 **或** HTTP(S) URL。
- 流程：加载到 Buffer，检测媒体类型，并构建正确的负载：
  - **图像：** 调整大小并重新压缩为 JPEG（最大边长 2048px），目标为 `agents.defaults.mediaMaxMb`（默认 5 MB），上限为 6 MB。
  - **音频/语音/视频：** 最大 16 MB 的直通；音频作为语音消息发送 (`ptt: true`)。
  - **文档：** 任何其他文件，最大 100 MB，当可用时保留文件名。
- WhatsApp GIF 风格播放：发送带有 `gifPlayback: true` 的 MP4（CLI: `--gif-playback`) 以便移动客户端内联循环播放。
- MIME 检测优先使用魔数字节，然后是头信息，最后是文件扩展名。
- 标题来自 `--message` 或 `reply.text`；允许空标题。
- 日志记录：非详细模式显示 `↩️`/`✅`；详细模式包括大小和源路径/URL。

## 自动回复管道

- `getReplyFromConfig` 返回 `{ text?, mediaUrl?, mediaUrls? }`。
- 当存在媒体时，网页发送者使用与 `openclaw message send` 相同的管道解析本地路径或 URL。
- 如果提供多个媒体条目，则按顺序发送。

## 入站媒体到命令（Pi）

- 当入站网页消息包含媒体时，OpenClaw 下载到临时文件并暴露模板变量：
  - `{{MediaUrl}}` 入站媒体的伪 URL。
  - `{{MediaPath}}` 在运行命令之前写入的本地临时路径。
- 当启用每个会话的 Docker 沙盒时，入站媒体被复制到沙盒工作区，并将 `MediaPath`/`MediaUrl` 重写为类似 `media/inbound/<filename>` 的相对路径。
- 媒体理解（如果通过 `tools.media.*` 或共享 `tools.media.models` 配置）在模板化之前运行，并可以在 `Body` 中插入 `[Image]`、`[Audio]` 和 `[Video]` 块。
  - 音频设置 `{{Transcript}}` 并使用转录本进行命令解析，因此斜杠命令仍然有效。
  - 视频和图像描述保留任何标题文本以供命令解析。
- 默认情况下只处理第一个匹配的图像/音频/视频附件；设置 `tools.media.<cap>.attachments` 以处理多个附件。

## 限制与错误

**出站发送限制（WhatsApp Web 发送）**

- 图像：重新压缩后的上限约为 6 MB。
- 音频/语音/视频：16 MB 上限；文档：100 MB 上限。
- 超尺寸或无法读取的媒体 → 日志中清晰错误，回复被跳过。

**媒体理解限制（转录/描述）**

- 图像默认：10 MB (`tools.media.image.maxBytes`)。
- 音频默认：20 MB (`tools.media.audio.maxBytes`)。
- 视频默认：50 MB (`tools.media.video.maxBytes`)。
- 超尺寸媒体跳过理解，但回复仍会通过原始正文。

## 测试注意事项

- 覆盖图像/音频/文档情况的发送 + 回复流程。
- 验证图像的重新压缩（大小限制）和音频的语音消息标志。
- 确保多媒体回复按顺序发送。