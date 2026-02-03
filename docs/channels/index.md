---
summary: "Messaging platforms OpenClaw can connect to"
read_when:
  - You want to choose a chat channel for OpenClaw
  - You need a quick overview of supported messaging platforms
title: "Chat Channels"
---
# 聊天频道

OpenClaw 可以通过您已使用的任何聊天应用与您进行交流。每个频道均通过网关连接。
文本支持所有平台；媒体和表情反应因频道而异。

## 支持的频道

- [WhatsApp](/channels/whatsapp) — 最受欢迎的平台；使用 Baileys，需要二维码配对。
- [Telegram](/channels/telegram) — 通过 grammY 使用 Bot API；支持群组。
- [Discord](/channels/discord) — Discord Bot API + 网关；支持服务器、频道和单聊。
- [Slack](/channels/slack) — Bolt SDK；工作区应用。
- [Google Chat](/channels/googlechat) — 通过 HTTP webhook 使用 Google Chat API 应用。
- [Mattermost](/channels/mattermost) — Bot API + WebSocket；频道、群组、单聊（插件，需单独安装）。
- [Signal](/channels/signal) — signal-cli；注重隐私。
- [BlueBubbles](/channels/bluebubbles) — **适用于 iMessage 的推荐选择**；使用 BlueBubbles macOS 服务器 REST API，支持完整功能（编辑、撤回、特效、表情、群组管理 —— 编辑功能在 macOS 26 Tahoe 上目前损坏）。
- [iMessage](/channels/imessage) — 仅限 macOS；通过 imsg 实现原生集成（旧版，新设置建议使用 BlueBubbles）。
- [Microsoft Teams](/channels/msteams) — Bot Framework；企业支持（插件，需单独安装）。
- [LINE](/channels/line) — LINE 消息 API 机器人（插件，需单独安装）。
- [Nextcloud Talk](/channels/nextcloud-talk) — 通过 Nextcloud Talk 实现自托管聊天（插件，需单独安装）。
- [Matrix](/channels/matrix) — Matrix 协议（插件，需单独安装）。
- [Nostr](/channels/nostr) — 通过 NIP-04 实现去中心化单聊（插件，需单独安装）。
- [Tlon](/channels/tlon) — 基于 Urbit 的消息应用（插件，需单独安装）。
- [Twitch](/channels/twitch) — 通过 IRC 连接实现 Twitch 聊天（插件，需单独安装）。
- [Zalo](/channels/zalo) — Zalo Bot API；越南流行的聊天应用（插件，需单独安装）。
- [Zalo 个人](/channels/zalouser) — 通过二维码登录的 Zalo 个人账户（插件，需单独安装）。
- [WebChat](/web/webchat) — 通过 WebSocket 实现的网关 WebChat 界面。

## 注意事项

- 频道可以同时运行；配置多个频道后，OpenClaw 会根据聊天进行路由。
- 通常 **Telegram** 的设置速度最快（只需简单的机器人令牌）。WhatsApp 需要二维码配对，并且在磁盘上存储更多的状态信息。
- 群组行为因频道而异；请参阅 [群组](/concepts/groups)。
- 为了安全，单聊配对和允许列表是强制执行的；请参阅 [安全](/gateway/security)。
- Telegram 内部信息：[grammY 说明](/channels/grammy)。
- 故障排除：[频道故障排除](/channels/troubleshooting)。
- 模型提供者在单独文档中说明；请参阅 [模型提供者](/providers/models)。