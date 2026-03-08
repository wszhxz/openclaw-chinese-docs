---
summary: "Messaging platforms OpenClaw can connect to"
read_when:
  - You want to choose a chat channel for OpenClaw
  - You need a quick overview of supported messaging platforms
title: "Chat Channels"
---
# 聊天频道

OpenClaw 可以通过您正在使用的任何聊天应用与您交流。每个频道均通过 Gateway 连接。
所有平台均支持文本；媒体和反应因频道而异。

## 支持的频道

- [BlueBubbles](/channels/bluebubbles) — **推荐用于 iMessage**；使用 BlueBubbles macOS 服务器 REST API，支持完整功能（编辑、撤回、特效、反应、群组管理 — 编辑功能目前在 macOS 26 Tahoe 上不可用）。
- [Discord](/channels/discord) — Discord Bot API + Gateway；支持服务器、频道和 DM。
- [Feishu](/channels/feishu) — 通过 WebSocket 的 Feishu/Lark Bot（plugin，单独安装）。
- [Google Chat](/channels/googlechat) — 通过 HTTP webhook 的 Google Chat API 应用。
- [iMessage (legacy)](/channels/imessage) — 通过 imsg CLI 的旧版 macOS 集成（已弃用，新设置请使用 BlueBubbles）。
- [IRC](/channels/irc) — 经典 IRC 服务器；频道 + DM，支持配对/allowlist 控制。
- [LINE](/channels/line) — LINE Messaging API Bot（plugin，单独安装）。
- [Matrix](/channels/matrix) — Matrix 协议（plugin，单独安装）。
- [Mattermost](/channels/mattermost) — Bot API + WebSocket；频道、群组、DM（plugin，单独安装）。
- [Microsoft Teams](/channels/msteams) — Bot Framework；企业支持（plugin，单独安装）。
- [Nextcloud Talk](/channels/nextcloud-talk) — 通过 Nextcloud Talk 的自托管聊天（plugin，单独安装）。
- [Nostr](/channels/nostr) — 通过 NIP-04 的去中心化 DM（plugin，单独安装）。
- [Signal](/channels/signal) — signal-cli；注重隐私。
- [Synology Chat](/channels/synology-chat) — 通过 outgoing+incoming webhooks 的 Synology NAS Chat（plugin，单独安装）。
- [Slack](/channels/slack) — Bolt SDK；工作区应用。
- [Telegram](/channels/telegram) — 通过 grammY 的 Bot API；支持群组。
- [Tlon](/channels/tlon) — 基于 Urbit 的即时通讯工具（plugin，单独安装）。
- [Twitch](/channels/twitch) — 通过 IRC 连接的 Twitch 聊天（plugin，单独安装）。
- [WebChat](/web/webchat) — 基于 WebSocket 的 Gateway WebChat UI。
- [WhatsApp](/channels/whatsapp) — 最流行；使用 Baileys 并需要 QR pairing。
- [Zalo](/channels/zalo) — Zalo Bot API；越南流行的即时通讯工具（plugin，单独安装）。
- [Zalo Personal](/channels/zalouser) — 通过 QR login 的 Zalo 个人账户（plugin，单独安装）。

## 注意事项

- 频道可以同时运行；配置多个频道后，OpenClaw 将根据聊天进行路由。
- 最快的设置通常是 **Telegram**（简单的 bot token）。WhatsApp 需要 QR pairing 并在磁盘上存储更多 state。
- 群组行为因频道而异；请参见 [群组](/channels/groups)。
- 为确保安全，将强制执行 DM pairing 和 allowlist；请参见 [安全性](/gateway/security)。
- 故障排除：[频道故障排除](/channels/troubleshooting)。
- 模型提供商有单独文档；请参见 [模型提供商](/providers/models)。