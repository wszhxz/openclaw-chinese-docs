---
summary: "Messaging platforms OpenClaw can connect to"
read_when:
  - You want to choose a chat channel for OpenClaw
  - You need a quick overview of supported messaging platforms
title: "Chat Channels"
---
# 聊天频道

OpenClaw 可以在您已使用的任何聊天应用上与您对话。每个频道都通过 Gateway 连接。
文本在所有地方都受支持；媒体和反应因频道而异。

## 支持的频道

- [BlueBubbles](/channels/bluebubbles) — **推荐用于 iMessage**；使用 BlueBubbles macOS 服务器 REST API，支持完整功能（捆绑插件；编辑、撤回、特效、反应、群组管理——目前在 macOS 26 Tahoe 上编辑功能存在故障）。
- [Discord](/channels/discord) — Discord Bot API + Gateway；支持服务器、频道和私聊。
- [Feishu](/channels/feishu) — 通过 WebSocket 的 Feishu/Lark bot（捆绑插件）。
- [Google Chat](/channels/googlechat) — 通过 HTTP webhook 的 Google Chat API 应用。
- [iMessage (旧版)](/channels/imessage) — 通过 imsg CLI 的旧版 macOS 集成（已弃用，新设置请使用 BlueBubbles）。
- [IRC](/channels/irc) — 经典 IRC 服务器；频道 + 私聊，带有配对/白名单控制。
- [LINE](/channels/line) — LINE Messaging API bot（捆绑插件）。
- [Matrix](/channels/matrix) — Matrix 协议（捆绑插件）。
- [Mattermost](/channels/mattermost) — Bot API + WebSocket；频道、群组、私聊（捆绑插件）。
- [Microsoft Teams](/channels/msteams) — Bot Framework；企业支持（捆绑插件）。
- [Nextcloud Talk](/channels/nextcloud-talk) — 通过 Nextcloud Talk 的自托管聊天（捆绑插件）。
- [Nostr](/channels/nostr) — 通过 NIP-04 的去中心化私聊（捆绑插件）。
- [QQ Bot](/channels/qqbot) — QQ Bot API；私聊、群聊和富媒体（捆绑插件）。
- [Signal](/channels/signal) — signal-cli；注重隐私。
- [Slack](/channels/slack) — Bolt SDK；工作区应用。
- [Synology Chat](/channels/synology-chat) — 通过传出+传入 webhook 的 Synology NAS Chat（捆绑插件）。
- [Telegram](/channels/telegram) — 通过 grammY 的 Bot API；支持群组。
- [Tlon](/channels/tlon) — 基于 Urbit 的信使（捆绑插件）。
- [Twitch](/channels/twitch) — 通过 IRC 连接的 Twitch 聊天（捆绑插件）。
- [语音通话](/plugins/voice-call) — 通过 Plivo 或 Twilio 的电话服务（插件，单独安装）。
- [Web 聊天](/web/webchat) — 基于 WebSocket 的 Gateway Web 聊天 UI。
- [WeChat](https://www.npmjs.com/package/@tencent-weixin/openclaw-weixin) — 通过 QR 登录的 Tencent iLink Bot 插件；仅限私聊。
- [WhatsApp](/channels/whatsapp) — 最受欢迎；使用 Baileys 并需要 QR 配对。
- [Zalo](/channels/zalo) — Zalo Bot API；越南流行的信使（捆绑插件）。
- [Zalo Personal](/channels/zalouser) — 通过 QR 登录的 Zalo 个人账户（捆绑插件）。

## 注意事项

- 频道可以同时运行；配置多个后，OpenClaw 将按聊天进行路由。
- 最快的设置通常是 **Telegram**（简单的机器人令牌）。WhatsApp 需要 QR 配对并在磁盘上存储更多状态。
- 群组行为因频道而异；参见 [群组](/channels/groups)。
- 出于安全考虑，强制执行私聊配对和白名单；参见 [安全](/gateway/security)。
- 故障排除：[频道故障排除](/channels/troubleshooting)。
- 模型提供商有单独的文档；参见 [模型提供商](/providers/models)。