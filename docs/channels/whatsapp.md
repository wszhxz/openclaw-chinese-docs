---
summary: "WhatsApp (web channel) integration: login, inbox, replies, media, and ops"
read_when:
  - Working on WhatsApp/web channel behavior or inbox routing
title: "WhatsApp"
---
翻译

# 译文

## 翻译

## 限制

- 出站文本按 `channels.whatsapp.textChunkLimit` 分块（默认 4000）。
- 可选换行分块：设置 `channels.whatsapp.chunkMode="newline"` 以在长度分块前按空白行（段落边界）拆分。
- 入站媒体保存受 `channels.whatsapp.mediaMaxMb` 限制（默认 50 MB）。
- 出站媒体项受 `agents.defaults.mediaMaxMb` 限制（默认 5 MB）。

## 出站发送（文本 + 媒体）

- 使用活动的 Web 监听器；如果网关未运行则报错。
- 文本分块：每条消息最大 4k（可通过 `channels.whatsapp.textChunkLimit` 配置，可选 `channels.whatsapp.chunkMode`）。
- 媒体：
  - 支持图像/视频/音频/文档。
  - 音频以 PTT 发送；`audio/ogg` => `audio/ogg; codecs=opus`。
  - 仅在第一个媒体项上显示标题。
  - 媒体获取支持 HTTP(S) 和本地路径。
  - 动画 GIF：WhatsApp 期望 MP4 且 `gifPlayback: true` 以实现内联循环。
    - CLI：`openclaw message send --media <mp4> --gif-playback`
    - 网关：`send` 参数包括 `gifPlayback: true`

## 语音备忘录（PTT 音频）

WhatsApp 以 **语音备忘录**（PTT 气泡）发送音频。

- 最佳效果：OGG/Opus。OpenClaw 将 `audio/ogg` 重写为 `audio/ogg; codecs=opus`。
- `[[audio_as_voice]]` 对 WhatsApp 无效（音频已作为语音备忘录发送）。

## 媒体限制 + 优化

- 默认出站限制：5 MB（每项媒体）。
- 覆盖：`agents.defaults.mediaMaxMb`。
- 图像在限制内自动优化为 JPEG（调整大小 + 质量扫描）。
- 超大媒体 => 错误；媒体回复回退为文本警告。

## 心跳

- **网关心跳** 记录连接健康状态（`web.heartbeatSeconds`，默认 60 秒）。
- **代理心跳** 可按代理配置（`agents.list[].heartbeat`）或全局（`agents.defaults.heartbeat`）设置（当无代理条目时作为回退）。
  - 使用配置的心跳提示（默认：`Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`）+ `HEARTBEAT_OK` 跳过行为。
  - 默认发送至上次使用的通道（或配置的目标）。

## 重连行为

- 退避策略：`web.reconnect`：
  - `initialMs`, `maxMs`, `factor`, `jitter`, `maxAttempts`。
- 如果达到 `maxAttempts`，Web 监控停止（降级）。
- 未登录 => 停止并要求重新链接。

## 配置快速映射

- `channels.whatsapp.dmPolicy`（DM 策略：配对/允许列表/开放/禁用）。
- `channels.whatsapp.selfChatMode`（同机设置；机器人使用您的个人 WhatsApp 号码）。
- `channels.whatsapp.allowFrom`（DM 允许列表）。WhatsApp 使用 E.164 电话号码（无用户名）。
- `channels.whatsapp.mediaMaxMb`（入站媒体保存限制）。
- `channels.whatsapp.ackReaction`（消息接收时的自动反应：`{emoji, direct, group}`）。
- `channels.whatsapp.accounts.<accountId>.*`（按账户设置 + 可选 `authDir`）。
- `channels.whatsapp.accounts.<accountId>.mediaMaxMb`（按账户入站媒体限制）。
- `channels.whatsapp.accounts.<accountId>.ackReaction`（按账户确认反应覆盖）。
- `channels.whatsapp.groupAllowFrom`（群发送允许列表）。
- `channels.whatsapp.groupPolicy`（群策略）。
- `channels.whatsapp.historyLimit` / `channels.whatsapp.accounts.<accountId>.historyLimit`（群历史上下文；`0` 禁用）。
- `channels.whatsapp.dmHistoryLimit`（DM 历史限制在用户回合中）。按用户覆盖：`channels.whatsapp.dms["<phone>"].historyLimit`。
- `channels.whatsapp.groups`（群允许列表 + 提及门控默认值；使用 `"*"` 允许所有）。
- `channels.whatsapp.actions.reactions`（门控 WhatsApp 工具反应）。
- `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）。
- `messages.groupChat.historyLimit`。
- `channels.whatsapp.messagePrefix`（入站前缀；按账户：`channels.whatsapp.accounts.<accountId>.messagePrefix`；已弃用：`messages.messagePrefix`）。
- `messages.responsePrefix`（出站前缀）。
- `agents.defaults.mediaMaxMb`。
- `agents.defaults.heartbeat.every`。
- `agents.defaults.heartbeat.model`（可选覆盖）。
- `agents.defaults.heartbeat.target`。
- `agents.defaults.heartbeat.to`。
- `agents.defaults.heartbeat.session`。
- `agents.list[].heartbeat.*`（按代理覆盖）。
- `session.*`（范围、空闲、存储、主键）。
- `web.enabled`（当为 false 时禁用通道启动）。
- `web.heartbeatSeconds`。
- `web.reconnect.*`。

## 日志 + 故障排除

- 子系统：`whatsapp/inbound`, `whatsapp/outbound`, `web-heartbeat`, `web-reconnect`。
- 日志文件：`/tmp/openclaw/openclaw-YYYY-MM-DD.log`（可