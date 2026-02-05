---
summary: "Image and media handling rules for send, gateway, and agent replies"
read_when:
  - Modifying media pipeline or attachments
title: "Image and Media Support"
---
# 图像与媒体支持 — 2025-12-05

WhatsApp渠道通过**Baileys Web**运行。本文档记录了发送、网关和代理回复的当前媒体处理规则。

## 目标

- 通过`openclaw message send --media`发送带有可选标题的媒体。
- 允许网页收件箱的自动回复包含媒体和文本。
- 保持每种类型的限制合理且可预测。

## CLI界面

- `openclaw message send --media <path-or-url> [--message <caption>]`
  - `--media` 可选；仅发送媒体时标题可以为空。
  - `--dry-run` 打印解析后的负载；`--json` 发出`{ channel, to, messageId, mediaUrl, caption }`。

## WhatsApp Web渠道行为

- 输入：本地文件路径**或**HTTP(S) URL。
- 流程：加载到Buffer中，检测媒体类型，并构建正确的负载：
  - **图像：** 调整大小并重新压缩为JPEG（最大边长2048px），目标为`agents.defaults.mediaMaxMb`（默认5 MB），上限为6 MB。
  - **音频/语音/视频：** 直通最多16 MB；音频作为语音消息发送（`ptt: true`）。
  - **文档：** 其他所有内容，最多100 MB，在可用时保留文件名。
- WhatsApp GIF式播放：发送带有`gifPlayback: true`的MP4（CLI：`--gif-playback`），以便移动客户端内联循环播放。
- MIME检测优先级：魔数位、然后是头部、最后是文件扩展名。
- 标题来自`--message`或`reply.text`；允许空标题。
- 日志记录：非详细模式显示`↩️`/`✅`；详细模式包括大小和源路径/URL。

## 自动回复管道

- `getReplyFromConfig` 返回`{ text?, mediaUrl?, mediaUrls? }`。
- 当存在媒体时，网页发送器使用与`openclaw message send`相同的管道解析本地路径或URL。
- 如果提供多个媒体条目，则按顺序发送。

## 入站媒体到命令（Pi）

- 当入站网页消息包含媒体时，OpenClaw下载到临时文件并暴露模板变量：
  - `{{MediaUrl}}` 入站媒体的伪URL。
  - `{{MediaPath}}` 运行命令前写入的本地临时路径。
- 当启用每个会话的Docker沙箱时，入站媒体被复制到沙箱工作区，`MediaPath`/`MediaUrl`被重写为类似`media/inbound/<filename>`的相对路径。
- 媒体理解（如果通过`tools.media.*`或共享`tools.media.models`配置）在模板化之前运行，可以将`[Image]`、`[Audio]`和`[Video]`块插入到`Body`中。
  - 音频设置`{{Transcript}}`并使用转录进行命令解析，因此斜杠命令仍然有效。
  - 视频和图像描述在命令解析中保留任何标题文本。
- 默认情况下只处理第一个匹配的图像/音频/视频附件；设置`tools.media.<cap>.attachments`以处理多个附件。

## 限制和错误

**出站发送限制（WhatsApp网页发送）**

- 图像：重新压缩后约6 MB限制。
- 音频/语音/视频：16 MB限制；文档：100 MB限制。
- 超大或不可读的媒体 → 日志中显示清晰错误，回复被跳过。

**媒体理解限制（转录/描述）**

- 图像默认值：10 MB（`tools.media.image.maxBytes`）。
- 音频默认值：20 MB（`tools.media.audio.maxBytes`）。
- 视频默认值：50 MB（`tools.media.video.maxBytes`）。
- 超大媒体跳过理解，但回复仍通过原始正文发送。

## 测试注意事项

- 涵盖图像/音频/文档情况的发送+回复流程。
- 验证图像的重新压缩（大小限制）和音频的语音消息标志。
- 确保多媒体回复作为顺序发送展开。