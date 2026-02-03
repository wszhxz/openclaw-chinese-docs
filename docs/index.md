---
summary: "Top-level overview of OpenClaw, features, and purpose"
read_when:
  - Introducing OpenClaw to newcomers
title: "OpenClaw"
---
# OpenClaw 🦞

> _"EXFOLIATE! EXFOLIATE!"_ — 一只太空龙虾，大概

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
  <strong>任何操作系统 + WhatsApp/Telegram/Discord/iMessage 网关，用于 AI 代理（Pi）。</strong><br />
  插件可添加 Mattermost 和更多功能。
  发送一条消息，即可获得代理的响应 —— 从你的口袋中。
</p>

<p align="center">
  <a href="https://github.com/openclaw/openclaw">GitHub</a> ·
  <a href="https://github.com/openclaw/openclaw/releases">发布版本</a> ·
  <a href="/">文档</a> ·
  <a href="/start/openclaw">OpenClaw 代理设置</a>
</p>

OpenClaw 将 WhatsApp（通过 WhatsApp Web / Baileys）、Telegram（Bot API / grammY）、Discord（Bot API / channels.discord.js）和 iMessage（imsg CLI）连接到编码代理，如 [Pi](https://github.com/badlogic/pi-mono)。插件可添加 Mattermost（Bot API + WebSocket）和更多功能。
OpenClaw 同时也支持 OpenClaw 代理。

## 从这里开始

- **从零开始安装：** [入门指南](/start/getting-started)
- **引导式设置（推荐）：** [向导](/start/wizard) (`openclaw onboard`)
- **打开仪表板（本地网关）：** http://127.0.0.1:18789/（或 http://localhost:18789/）

如果网关在同台电脑上运行，该链接会立即打开浏览器控制界面。
如果失败，请先启动网关：`openclaw`

## 仪表板

仪表板是通过浏览器进行的控制界面。它提供了对所有连接平台的集中管理，包括消息接收、代理配置和状态监控。通过仪表板，用户可以实时查看和调整代理的行为，确保其按照预期运行。

## 如何运作

以下是 OpenClaw 的工作原理：

1. **消息接收：** 用户通过 WhatsApp、Telegram、Discord 或 iMessage 发送消息。
2. **消息路由：** 消息被路由到 OpenClaw 的网关，根据配置的规则进行处理。
3. **代理处理：** 消息被传递给相应的 AI 代理（如 Pi），进行处理和响应生成。
4. **响应发送：** 生成的响应通过相同的平台返回给用户。

## 网络模型

- **网关：** 网关是 OpenClaw 的核心组件，负责消息的接收和路由。
- **回环优先：** 网关优先使用本地网络接口，确保低延迟和高可靠性。
- **节点：** 节点是代理的运行环境，可以是本地或远程服务器。
- **画布主机：** 画布主机是用于渲染和展示代理输出的服务器。
- **远程访问：** 用户可以通过远程连接访问网关和代理，实现跨地域的协作。

## 功能

- **📱 WhatsApp 集成：** 支持通过 WhatsApp 发送和接收消息。
- **📲 Telegram 集成：** 支持通过 Telegram 发送和接收消息。
- **💬 Discord 集成：** 支持通过 Discord 发送和接收消息。
- **📲 iMessage 集成：** 支持通过 iMessage 发送和接收消息。
- **🔌 插件支持：** 支持多种插件，扩展功能。
- **⚙️ 高度可配置：** 提供丰富的配置选项，满足不同需求。
- **🔒 安全性：** 采用多种安全措施，保护用户数据。

## 快速开始

1. **安装 OpenClaw：**
   ```bash
   npm install -g openclaw
   ```

2. **启动网关：**
   ```bash
   openclaw start
   ```

3. **配置代理：**
   ```bash
   openclaw config set proxy pi
   ```

4. **发送消息：**
   ```bash
   openclaw send "Hello, OpenClaw!"
   ```

## 配置

```json
{
  "channels": {
    "whatsapp": {
      "allowFrom": ["+1234567890"]
    }
  }
}
```

## 文档

- **从这里开始：**
  - [入门指南](/start/getting-started)
  - [引导式设置](/start/wizard)
  - [OpenClaw 代理