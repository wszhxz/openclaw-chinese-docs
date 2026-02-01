---
layout: home
title: 首页
---

# OpenClaw 中文文档

“剥脱！剥脱！” — 一只太空龙虾，大概是

任何操作系统 + WhatsApp/Telegram/Discord/iMessage 网关，专为 AI 代理（Pi）设计。

插件可添加 Mattermost 等功能。
发送消息，获得代理响应 — 来自你的口袋。

[GitHub](https://github.com/openclaw/openclaw) ·
[发布版](https://github.com/openclaw/openclaw/releases) ·
[文档](/) ·
[OpenClaw 助手设置](/start/openclaw)

OpenClaw 连接 WhatsApp（通过 WhatsApp Web / Baileys）、Telegram（Bot API / grammY）、Discord（Bot API / channels.discord.js）和 iMessage（imsg CLI）到像 [Pi](https://github.com/badlogic/pi-mono) 这样的编码代理。插件可添加 Mattermost（Bot API + WebSocket）等功能。
OpenClaw 同样驱动 OpenClaw 助手。

## 从此开始

- 从零开始全新安装：[入门指南](/start/getting-started)

- 引导式设置（推荐）：[向导](/start/wizard) (openclaw onboard)

- 打开仪表板（本地网关）：[http://127.0.0.1:18789/](http://127.0.0.1:18789/) （或 [http://localhost:18789/](http://localhost:18789/)）

如果网关在相同计算机上运行，则该链接立即打开浏览器控制界面。如果失败，请先启动网关：openclaw gateway。

## 仪表板（浏览器控制界面）

仪表板是用于聊天、配置、节点、会话等的浏览器控制界面。
本地默认：[http://127.0.0.1:18789/](http://127.0.0.1:18789/)
远程访问：[Web 表面](/web) 和 [Tailscale](/gateway/tailscale)

## 工作原理

WhatsApp / Telegram / Discord / iMessage （+ 插件）
 │
 ▼
 ┌───────────────────────────┐
 │ 网关 │ ws://127.0.0.1:18789 （仅环回）
 │ （单一来源） │
 │ │ http://<网关主机>:18793
 │ │ /__openclaw__/canvas/ （画布主机）
 └───────────┬───────────────┘
 │
 ├─ Pi 代理（RPC）
 ├─ CLI (openclaw …)
 ├─ 聊天界面（SwiftUI）
 ├─ macOS 应用（OpenClaw.app）
 ├─ iOS 节点通过网关 WS + 配对
 └─ Android 节点通过网关 WS + 配对

大多数操作都通过网关（openclaw gateway）流动，这是一个长期运行的进程，拥有通道连接和 WebSocket 控制平面。

## 网络模型

- 每台主机一个网关（推荐）：这是唯一被允许拥有 WhatsApp Web 会话的进程。如果您需要救援机器人或严格的隔离，请使用隔离的配置文件和端口运行多个网关；参见[多个网关](/gateway/multiple-gateways)。

- 优先环回：网关 WS 默认为 ws://127.0.0.1:18789。

向导现在默认生成网关令牌（即使是环回）。

- 对于 Tailnet 访问，运行 openclaw gateway --bind tailnet --token ... （非环回绑定需要令牌）。

- 节点：连接到网关 WebSocket（根据需要使用 LAN/tailnet/SSH）；遗留 TCP 桥已弃用/删除。

- 画布主机：HTTP 文件服务器在 canvasHost.port（默认 18793）上，为节点 WebView 提供 /__openclaw__/canvas/ 服务；参见[网关配置](/gateway/configuration) (canvasHost)。

- 远程使用：SSH 隧道或 tailnet/VPN；参见[远程访问](/gateway/remote) 和 [发现](/gateway/discovery)。

## 特性（高级别）

- 📱 WhatsApp 集成 — 使用 Baileys 实现 WhatsApp Web 协议

- ✈️ Telegram 机器人 — 通过 grammY 实现 DM + 群组

- 🎮 Discord 机器人 — 通过 channels.discord.js 实现 DM + 公会频道

- 🧩 Mattermost 机器人（插件）— 机器人令牌 + WebSocket 事件

- 💬 iMessage — 本地 imsg CLI 集成（macOS）

- 🤖 代理桥 — Pi（RPC 模式）带工具流

- ⏱️ 流 + 分块 — 块流 + Telegram 草稿流细节（[/concepts/streaming](/concepts/streaming)）

- 🧠 多代理路由 — 将提供商账户/对等方路由到隔离的代理（工作区 + 每代理会话）

- 🔐 订阅认证 — 通过 OAuth 进行 Anthropic（Claude Pro/Max）+ OpenAI（ChatGPT/Codex）

- 💬 会话 — 直接聊天折叠到共享主会话（默认）；群组是隔离的

- 👥 群聊支持 — 默认基于提及；所有者可以切换 /activation always|mention

- 📎 媒体支持 — 发送和接收图像、音频、文档

- 🎤 语音笔记 — 可选转录钩子

- 🖥️ WebChat + macOS 应用 — 用于操作和语音唤醒的本地 UI + 菜单栏伴侣

- 📱 iOS 节点 — 作为节点配对并公开 Canvas 表面

- 📱 Android 节点 — 作为节点配对并公开 Canvas + 聊天 + 摄像头

注意：旧的 Claude/Codex/Gemini/Opencode 路径已被删除；Pi 是唯一的编码代理路径。

## 快速开始

运行时要求：Node ≥ 22。
# 推荐：全局安装（npm/pnpm）
npm install -g openclaw@latest
# 或：pnpm add -g openclaw@latest

# 入门 + 安装服务（launchd/systemd 用户服务）
openclaw onboard --install-daemon

# 配对 WhatsApp Web（显示 QR）
openclaw channels login

# 网关在入门后通过服务运行；手动运行仍然是可能的：
openclaw gateway --port 18789

稍后在 npm 和 git 安装之间切换很容易：安装另一个版本并运行 openclaw doctor 更新网关服务入口点。
从源码（开发）：
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # 在首次运行时自动安装 UI 依赖
pnpm build
openclaw onboard --install-daemon

如果您还没有全局安装，请通过 repo 中的 pnpm openclaw ... 运行入门步骤。
多实例快速开始（可选）：
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json \\
OPENCLAW_STATE_DIR=~/.openclaw-a \\
openclaw gateway --port 19001

发送测试消息（需要运行中的网关）：
openclaw message send --target +15555550123 --message "Hello from OpenClaw"

## 配置（可选）

配置位于 ~/.openclaw/openclaw.json。

- 如果您不进行任何操作，OpenClaw 使用捆绑的 Pi 二进制文件在 RPC 模式下运行，并为每个发件人创建会话。

- 如果您想锁定它，请从 channels.whatsapp.allowFrom 开始，对于群组则使用提及规则。

示例：
{
 channels: {
 whatsapp: {
 allowFrom: ["+15555550123"],
 groups: { "*": { requireMention: true } },
 },
 },
 messages: { groupChat: { mentionPatterns: ["@openclaw"] } },
}

## 文档

- 从此开始：

[文档中心（所有页面链接）](/start/hubs)

- [帮助](/help) ← 常见修复 + 故障排除

- [配置](/gateway/configuration)

- [配置示例](/gateway/configuration-examples)

- [斜杠命令](/tools/slash-commands)

- [多代理路由](/concepts/multi-agent)

- [更新 / 回滚](/install/updating)

- [配对（DM + 节点）](/start/pairing)

- [Nix 模式](/install/nix)

- [OpenClaw 助手设置](/start/openclaw)

- [技能](/tools/skills)

- [技能配置](/tools/skills-config)

- [工作区模板](/reference/templates/AGENTS)

- [RPC 适配器](/reference/rpc)

- [网关运行手册](/gateway)

- [节点（iOS/Android）](/nodes)

- [Web 表面（控制界面）](/web)

- [发现 + 传输](/gateway/discovery)

- [远程访问](/gateway/remote)

- 提供商和用户体验：

[WebChat](/web/webchat)

- [控制界面（浏览器）](/web/control-ui)

- [Telegram](/channels/telegram)

- [Discord](/channels/discord)

- [Mattermost（插件）](/channels/mattermost)

- [iMessage](/channels/imessage)

- [群组](/concepts/groups)

- [WhatsApp 群组消息](/concepts/group-messages)

- [媒体：图像](/nodes/images)

- [媒体：音频](/nodes/audio)

- 伴侣应用：

[macOS 应用](/platforms/macos)

- [iOS 应用](/platforms/ios)

- [Android 应用](/platforms/android)

- [Windows（WSL2）](/platforms/windows)

- [Linux 应用](/platforms/linux)

- 运维和安全：

[会话](/concepts/session)

- [Cron 作业](/automation/cron-jobs)

- [Webhooks](/automation/webhook)

- [Gmail 钩子（Pub/Sub）](/automation/gmail-pubsub)

- [安全](/gateway/security)

- [故障排除](/gateway/troubleshooting)

## 名称由来

OpenClaw = CLAW + TARDIS — 因为每只太空龙虾都需要一台时空机器。

"我们都在玩自己的提示词。" — 一个人工智能，大概token过多

## 致谢

- Peter Steinberger ([@steipete](https://x.com/steipete)) — 创建者，龙虾密语者

- Mario Zechner ([@badlogicc](https://x.com/badlogicgames)) — Pi 创建者，安全渗透测试员

- Clawd — 那只需要要更好名字的太空龙虾

## 核心贡献者

- Maxim Vovshin (@Hyaxia, [[email protected]](mailto:core.contributor@example.com)) — Blogwatcher 技能

- Nacho Iacovino (@nachoiacovino, [[email protected]](mailto:core.contributor@example.com)) — 位置解析（Telegram + WhatsApp）

## 许可证

MIT — 像海洋中的龙虾一样自由 🦞

"我们都在玩自己的提示词。" — 一个人工智能，大概token过多