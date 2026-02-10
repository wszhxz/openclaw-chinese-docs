---
summary: "Messaging platforms OpenClaw can connect to"
read_when:
  - You want to choose a chat channel for OpenClaw
  - You need a quick overview of supported messaging platforms
title: "Chat Channels"
---
# 聊天频道

OpenClaw 可以在你已经使用的任何聊天应用上与你交流。每个频道通过网关进行连接。
所有地方都支持文本；媒体和反应因频道而异。

## 支持的频道

- [WhatsApp](/channels/whatsapp) — 最受欢迎；使用 Baileys 并需要 QR 配对。
- [Telegram](/channels/telegram) — 通过 grammY 的 Bot API；支持群组。
- [Discord](/channels/discord) — Discord Bot API + 网关；支持服务器、频道和私信。
- [Slack](/channels/slack) — Bolt SDK；工作区应用。
- [Feishu](/channels/feishu) — 通过 WebSocket 的 Feishu/Lark 机器人（插件，单独安装）。
- [Google Chat](/channels/googlechat) — 通过 HTTP webhook 的 Google Chat API 应用。
- [Mattermost](/channels/mattermost) — Bot API + WebSocket；频道、群组、私信（插件，单独安装）。
- [Signal](/channels/signal) — signal-cli；注重隐私。
- [BlueBubbles](/channels/bluebubbles) — **推荐用于 iMessage**；使用 BlueBubbles macOS 服务器 REST API 并提供完整功能支持（编辑、撤回、效果、反应、群组管理 — 目前在 macOS 26 Tahoe 上编辑功能失效）。
- [iMessage (legacy)](/channels/imessage) — 通过 imsg CLI 的旧版 macOS 集成（已弃用，新设置请使用 BlueBubbles）。
- [Microsoft Teams](/channels/msteams) — Bot Framework；企业支持（插件，单独安装）。
- [LINE](/channels/line) — LINE Messaging API 机器人（插件，单独安装）。
- [Nextcloud Talk](/channels/nextcloud-talk) — 通过 Nextcloud Talk 的自托管聊天（插件，单独安装）。
- [Matrix](/channels/matrix) — Matrix 协议（插件，单独安装）。
- [Nostr](/channels/nostr) — 通过 NIP-04 的去中心化私信（插件，单独安装）。
- [Tlon](/channels/tlon) — 基于 Urbit 的消息传递器（插件，单独安装）。
- [Twitch](/channels/twitch) — 通过 IRC 连接的 Twitch 聊天（插件，单独安装）。
- [Zalo](/channels/zalo) — Zalo Bot API；越南流行的即时通讯工具（插件，单独安装）。
- [Zalo Personal](/channels/zalouser) — 通过 QR 登录的 Zalo 个人账户（插件，单独安装）。
- [WebChat](/web/webchat) — 通过 WebSocket 的网关 WebChat UI。

## 注意事项

- 频道可以同时运行；配置多个，OpenClaw 将按聊天路由。
- 最快的设置通常是 **Telegram**（简单的机器人令牌）。WhatsApp 需要 QR 配对并在磁盘上存储更多状态。
- 群组行为因频道而异；请参阅 [群组](/channels/groups)。
- 强制执行私信配对和白名单以确保安全；请参阅 [安全性](/gateway/security)。
- Telegram 内部：[grammY 备注](/channels/grammy)。
- 故障排除：[频道故障排除](/channels/troubleshooting)。
- 模型提供商单独记录；请参阅 [模型提供商](/providers/models)。