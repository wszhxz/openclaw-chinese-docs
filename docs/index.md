---
summary: "Top-level overview of OpenClaw, features, and purpose"
read_when:
  - Introducing OpenClaw to newcomers
title: "OpenClaw"
---
# OpenClaw 🦞

> _"EXFOLIATE! EXFOLIATE!"_ — 一个太空龙虾，大概

<p align="center">
    <img
        src="/assets/openclaw-logo-text-dark.png"
        alt="OpenClaw"
        width="500"
        class="dark:hidden"
    />
    <img
        src="/assets/openclaw-logo-text.png"
        alt="OpenClaw"
        width="500"
        class="hidden dark:block"
    />
</p>

<p align="center">
  <strong>Any OS + WhatsApp/Telegram/Discord/iMessage gateway for AI agents (Pi).</strong><br />
  插件添加 Mattermost 等。
  发送消息，获取代理响应 — 在你的口袋里。
</p>

<p align="center">
  <a href="https://github.com/openclaw/openclaw">GitHub</a> ·
  <a href="https://github.com/openclaw/openclaw/releases">Releases</a> ·
  <a href="/">Docs</a> ·
  <a href="/start/openclaw">OpenClaw assistant setup</a>
</p>

OpenClaw 将 WhatsApp（通过 WhatsApp Web / Baileys），Telegram（Bot API / grammY），Discord（Bot API / channels.discord.js），和 iMessage（imsg CLI）连接到编码代理如 [Pi](https://github.com/badlogic/pi-mono)。插件添加 Mattermost（Bot API + WebSocket）等。
OpenClaw 还驱动 OpenClaw 助手。

## 从这里开始

- **全新安装：** [入门指南](/start/getting-started)
- **引导式设置（推荐）：** [向导](/start/wizard) (`openclaw onboard`)
- **打开仪表板（本地网关）：** http://127.0.0.1:18789/ (或 http://localhost:18789/)

如果网关在同一台计算机上运行，该链接会立即打开浏览器控制界面。
如果失败，请先启动网关：`openclaw gateway`。

## 仪表板（浏览器控制界面）

仪表板是聊天、配置、节点、会话等的浏览器控制界面。
本地默认：http://127.0.0.1:18789/
远程访问：[Web 表面](/web) 和 [Tailscale](/gateway/tailscale)

<p align="center">
  <img src="whatsapp-openclaw.jpg" alt="OpenClaw" width="420" />
</p>

## 工作原理

```
WhatsApp / Telegram / Discord / iMessage (+ plugins)
        │
        ▼
  ┌───────────────────────────┐
  │          Gateway          │  ws://127.0.0.1:18789 (loopback-only)
  │     (single source)       │
  │                           │  http://<gateway-host>:18793
  │                           │    /__openclaw__/canvas/ (Canvas host)
  └───────────┬───────────────┘
              │
              ├─ Pi agent (RPC)
              ├─ CLI (openclaw …)
              ├─ Chat UI (SwiftUI)
              ├─ macOS app (OpenClaw.app)
              ├─ iOS node via Gateway WS + pairing
              └─ Android node via Gateway WS + pairing
```

大多数操作通过 **网关** (`openclaw gateway`) 流动，这是一个单一的长期运行进程，拥有通道连接和 WebSocket 控制平面。

## 网络模型

- **每主机一个网关（推荐）：** 它是唯一允许拥有 WhatsApp Web 会话的进程。如果你需要救援机器人或严格的隔离，请使用隔离的配置文件和端口运行多个网关；参见 [多个网关](/gateway/multiple-gateways)。
- **优先回环：** 网关 WS 默认为 `ws://127.0.0.1:18789`。
  - 向导现在默认生成网关令牌（即使对于回环）。
  - 对于 Tailnet 访问，请运行 `openclaw gateway --bind tailnet --token ...`（非回环绑定需要令牌）。
- **节点：** 连接到网关 WebSocket（根据需要使用 LAN/tailnet/SSH）；传统的 TCP 桥接已弃用/移除。
- **画布主机：** HTTP 文件服务器在 `canvasHost.port` 上（默认 `18793`），提供 `/__openclaw__/canvas/` 给节点 WebView；参见 [网关配置](/gateway/configuration) (`canvasHost`)。
- **远程使用：** SSH 隧道或 tailnet/VPN；参见 [远程访问](/gateway/remote) 和 [发现](/gateway/discovery)。

## 特性（高层次）

- 📱 **WhatsApp 集成** — 使用 Baileys 进行 WhatsApp Web 协议
- ✈️ **Telegram 机器人** — 私信 + 群组通过 grammY
- 🎮 **Discord 机器人** — 私信 + 服务器频道通过 channels.discord.js
- 🧩 **Mattermost 机器人（插件）** — 机器人令牌 + WebSocket 事件
- 💬 **iMessage** — 本地 imsg CLI 集成（macOS）
- 🤖 **代理桥接** — Pi（RPC 模式）带工具流
- ⏱️ **流式传输 + 分块** — 块流式传输 + Telegram 草稿流式传输详情（[/concepts/streaming](/concepts/streaming)）
- 🧠 **多代理路由** — 将提供商账户/对等点路由到隔离的代理（工作区 + 每代理会话）
- 🔐 **订阅认证** — Anthropic (Claude Pro/Max) + OpenAI (ChatGPT/Codex) 通过 OAuth
- 💬 **会话** — 直接聊天合并为共享 `main`（默认）；群组是隔离的
- 👥 **群聊支持** — 默认基于提及；所有者可以切换 `/activation always|mention`
- 📎 **媒体支持** — 发送和接收图片、音频、文档
- 🎤 **语音笔记** — 可选转录钩子
- 🖥️ **WebChat + macOS 应用** — 本地界面 + 菜单栏伴侣用于操作和语音唤醒
- 📱 **iOS 节点** — 成对作为节点并暴露画布表面
- 📱 **Android 节点** — 成对作为节点并暴露画布 + 聊天 + 相机

注意：旧版 Claude/Codex/Gemini/Opencode 路径已被移除；Pi 是唯一的编码代理路径。

## 快速开始

运行时要求：**Node ≥ 22**。

```bash
# Recommended: global install (npm/pnpm)
npm install -g openclaw@latest
# or: pnpm add -g openclaw@latest

# Onboard + install the service (launchd/systemd user service)
openclaw onboard --install-daemon

# Pair WhatsApp Web (shows QR)
openclaw channels login

# Gateway runs via the service after onboarding; manual run is still possible:
openclaw gateway --port 18789
```

稍后在 npm 和 git 安装之间切换很容易：安装另一种方式并运行 `openclaw doctor` 来更新网关服务入口点。

从源码（开发）：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # auto-installs UI deps on first run
pnpm build
openclaw onboard --install-daemon
```

如果你还没有全局安装，请通过 `pnpm openclaw ...` 从仓库运行入站步骤。

多实例快速开始（可选）：

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json \
OPENCLAW_STATE_DIR=~/.openclaw-a \
openclaw gateway --port 19001
```

发送测试消息（需要运行中的网关）：

```bash
openclaw message send --target +15555550123 --message "Hello from OpenClaw"
```

## 配置（可选）

配置位于 `~/.openclaw/openclaw.json`。

- 如果你 **什么都不做**，OpenClaw 使用捆绑的 Pi 二进制文件以 RPC 模式运行，并为每个发送者创建会话。
- 如果你想锁定它，从 `channels.whatsapp.allowFrom` 开始，并（对于群组）使用提及规则。

示例：

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  messages: { groupChat: { mentionPatterns: ["@openclaw"] } },
}
```

## Docs

- 从这里开始：
  - [Docs 中心（所有页面链接）](/start/hubs)
  - [帮助](/help) ← _常见修复 + 故障排除_
  - [配置](/gateway/configuration)
  - [配置示例](/gateway/configuration-examples)
  - [斜杠命令](/tools/slash-commands)
  - [多代理路由](/concepts/multi-agent)
  - [更新 / 回滚](/install/updating)
  - [配对（私信 + 节点）](/start/pairing)
  - [Nix 模式](/install/nix)
  - [OpenClaw assistant setup](/start/openclaw)
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
  - [WebChat](/web/webchat)
  - [控制界面（浏览器）](/web/control-ui)
  - [Telegram](/channels/telegram)
  - [Discord](/channels/discord)
  - [Mattermost（插件）](/channels/mattermost)
  - [BlueBubbles（iMessage）](/channels/bluebubbles)
  - [iMessage（旧版）](/channels/imessage)
  - [群组](/concepts/groups)
  - [WhatsApp 群组消息](/concepts/group-messages)
  - [媒体：图片](/nodes/images)
  - [媒体：音频](/nodes/audio)
- 伴侣应用：
  - [macOS 应用](/platforms/macos)
  - [iOS 应用](/platforms/ios)
  - [Android 应用](/platforms/android)
  - [Windows (WSL2)](/platforms/windows)
  - [Linux 应用](/platforms/linux)
- 操作和安全：
  - [会话](/concepts/session)
  - [Cron 作业](/automation/cron-jobs)
  - [Webhook](/automation/webhook)
  - [Gmail 钩子（Pub/Sub）](/automation/gmail-pubsub)
  - [安全](/gateway/security)
  - [故障排除](/gateway/troubleshooting)

## 名称

**OpenClaw = CLAW + TARDIS** — 因为每个太空龙虾都需要一台时空机器。

---

_"我们都在玩自己的提示词."_ — 一个 AI，大概对令牌上瘾了

## 致谢

- **Peter Steinberger** ([@steipete](https://x.com/steipete)) — 创造者，龙虾密语者
- **Mario Zechner** ([@badlogicc](https://x.com/badlogicgames)) — Pi 创造者，安全渗透测试人员
- **Clawd** — 要求更好名字的太空龙虾

## 核心贡献者

- **Maxim Vovshin** (@Hyaxia, 36747317+Hyaxia@users.noreply.github.com) — Blogwatcher 技能
- **Nacho Iacovino** (@nachoiacovino, nacho.iacovino@gmail.com) — 地点解析（Telegram + WhatsApp）

## 许可证

MIT — 自由如海洋中的龙虾 🦞

---

_"我们都在玩自己的提示词."_ — 一个 AI，大概对令牌上瘾了