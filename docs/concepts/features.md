---
summary: "OpenClaw capabilities across channels, routing, media, and UX."
read_when:
  - You want a full list of what OpenClaw supports
title: "Features"
---
## 亮点

<Columns>
  <Card title="Channels" icon="message-square">
    WhatsApp, Telegram, Discord, and iMessage with a single Gateway.
  </Card>
  <Card title="Plugins" icon="plug">
    Add Mattermost and more with extensions.
  </Card>
  <Card title="Routing" icon="route">
    Multi-agent routing with isolated sessions.
  </Card>
  <Card title="Media" icon="image">
    Images, audio, and documents in and out.
  </Card>
  <Card title="Apps and UI" icon="monitor">
    Web Control UI and macOS companion app.
  </Card>
  <Card title="Mobile nodes" icon="smartphone">
    iOS and Android nodes with pairing, voice/chat, and rich device commands.
  </Card>
</Columns>

## 完整列表

- 通过 WhatsApp Web 集成 WhatsApp (Baileys)
- Telegram 机器人支持 (grammY)
- Discord 机器人支持 (channels.discord.js)
- Mattermost 机器人支持 (plugin)
- 通过本地 imsg CLI 集成 iMessage (macOS)
- 支持工具流式传输的 Pi RPC 模式 Agent 桥接
- 长响应的流式传输和分块处理
- 每个工作区或发送者隔离会话的多 Agent 路由
- 通过 OAuth 进行 Anthropic 和 OpenAI 的订阅认证
- 会话：直接聊天合并为共享的 `main`；群组是隔离的
- 支持基于提及激活的群组聊天
- 支持图片、音频和文档媒体
- 可选的语音笔记转录钩子
- WebChat 和 macOS 菜单栏应用
- iOS 节点，具备配对、Canvas、相机、屏幕录制、位置和语音功能
- Android 节点，具备配对、Connect 标签页、聊天会话、voice 标签页、Canvas/相机/屏幕，以及设备、通知、联系人/日历、运动、照片、SMS 和应用更新命令

<Note>
Legacy Claude, Codex, Gemini, and Opencode paths have been removed. Pi is the only
coding agent path.
</Note>