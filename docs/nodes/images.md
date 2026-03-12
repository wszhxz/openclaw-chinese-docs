---
summary: "Image and media handling rules for send, gateway, and agent replies"
read_when:
  - Modifying media pipeline or attachments
title: "Image and Media Support"
---
# 图像与媒体支持 — 2025-12-05

WhatsApp 通道通过 **Baileys Web** 运行。本文档汇总了当前针对发送、网关及坐席回复的媒体处理规则。

## 目标

- 通过 `openclaw message send --media` 发送带可选说明文字的媒体。
- 允许网页收件箱的自动回复同时包含媒体和文本。
- 保持各类型媒体的限制合理且可预期。

## CLI 接口

- `openclaw message send --media <path-or-url> [--message <caption>]`
  - `--media` 为可选参数；说明文字可为空，以实现纯媒体发送。
  - `--dry-run` 打印解析后的有效载荷；`--json` 发出 `{ channel, to, messageId, mediaUrl, caption }`。

## WhatsApp Web 通道行为

- 输入：本地文件路径 **或** HTTP(S) URL。
- 流程：加载为 Buffer，检测媒体类型，并构建对应的有效载荷：
  - **图像：** 调整尺寸并重新压缩为 JPEG 格式（最长边不超过 2048 像素），目标大小为 `agents.defaults.mediaMaxMb`（默认 5 MB），上限为 6 MB。
  - **音频/语音/视频：** 直通传输，上限为 16 MB；音频以语音便签形式发送（`ptt: true`）。
  - **文档：** 其余所有类型，上限为 100 MB；若可用，则保留原始文件名。
- WhatsApp GIF 风格播放：发送 MP4 文件并设置 `gifPlayback: true`（CLI 中为 `--gif-playback`），使移动端客户端支持内联循环播放。
- MIME 类型检测优先依据魔数（magic bytes），其次为响应头，最后为文件扩展名。
- 说明文字来源于 `--message` 或 `reply.text`；允许说明文字为空。
- 日志记录：非详细模式仅显示 `↩️`/`✅`；详细模式额外包含媒体大小及源路径/URL。

## 自动回复流程

- `getReplyFromConfig` 返回 `{ text?, mediaUrl?, mediaUrls? }`。
- 当存在媒体时，网页发送器使用与 `openclaw message send` 相同的流程解析本地路径或 URL。
- 若提供多个媒体条目，则按顺序依次发送。

## 入站媒体转为命令（Pi）

- 当入站网页消息包含媒体时，OpenClaw 将其下载至临时文件，并暴露以下模板变量：
  - `{{MediaUrl}}`：入站媒体的伪 URL。
  - `{{MediaPath}}`：运行命令前已写入的本地临时路径。
- 当启用每会话 Docker 沙箱时，入站媒体将被复制进沙箱工作区，且 `MediaPath`/`MediaUrl` 将被重写为类似 `media/inbound/<filename>` 的相对路径。
- 媒体理解（若通过 `tools.media.*` 或共享的 `tools.media.models` 启用）在模板渲染前执行，并可向 `Body` 插入 `[Image]`、`[Audio]` 和 `[Video]` 块：
  - 音频设置 `{{Transcript}}`，并使用语音转文字结果进行命令解析，从而确保斜杠命令仍可正常工作。
  - 视频与图像描述将保留原始说明文字，用于命令解析。
- 默认仅处理首个匹配的图像/音频/视频附件；如需处理多个附件，请设置 `tools.media.<cap>.attachments`。

## 限制与错误

**出站发送限制（WhatsApp Web 发送）**

- 图像：重压缩后上限约为 6 MB。
- 音频/语音/视频：上限为 16 MB；文档：上限为 100 MB。
- 超出尺寸限制或无法读取的媒体 → 日志中输出明确错误，该回复将被跳过。

**媒体理解限制（语音转文字 / 图像描述）**

- 图像默认上限：10 MB（`tools.media.image.maxBytes`）。
- 音频默认上限：20 MB（`tools.media.audio.maxBytes`）。
- 视频默认上限：50 MB（`tools.media.video.maxBytes`）。
- 超出尺寸限制的媒体将跳过理解步骤，但回复仍将照常发出，仅使用原始正文内容。

## 测试注意事项

- 覆盖图像/音频/文档三类场景的发送与回复流程。
- 验证图像的重压缩效果（尺寸约束）及音频的语音便签标志。
- 确保多媒体报道按顺序展开为多次独立发送。