---
summary: "Setup guide: keep your OpenClaw setup tailored while staying up-to-date"
read_when:
  - Setting up a new machine
  - You want “latest + greatest” without breaking your personal setup
title: "Setup"
---
# 设置

最后更新时间：2026-01-01

## 概述

- **仓库外的生活定制:** `~/.openclaw/workspace` (工作区) + `~/.openclaw/openclaw.json` (配置).
- **稳定的工作流:** 安装macOS应用程序；让它运行捆绑的Gateway。
- **前沿的工作流:** 通过`pnpm gateway:watch`自行运行Gateway，然后让macOS应用程序以本地模式附加。

## 先决条件（从源码）

- Node `>=22`
- `pnpm`
- Docker（可选；仅用于容器化设置/e2e — 请参阅[Docker](/install/docker)）

## 定制策略（使更新无痛）

如果您希望“100% 专为我定制” _且_ 更新简单，请将自定义内容保留在：

- **配置:** `~/.openclaw/openclaw.json` (JSON/JSON5风格)
- **工作区:** `~/.openclaw/workspace` (技能、提示、记忆；将其设为私有git仓库)

初始化一次：

```bash
openclaw setup
```

从此仓库内部，使用本地CLI入口：

```bash
openclaw setup
```

如果您还没有全局安装，可以通过`pnpm openclaw setup`运行它。

## 稳定的工作流（先安装macOS应用程序）

1. 安装并启动 **OpenClaw.app**（菜单栏）。
2. 完成入站/权限检查表（TCC提示）。
3. 确保Gateway是**本地**并正在运行（应用程序会管理它）。
4. 链接表面（示例：WhatsApp）：

```bash
openclaw channels login
```

5. 健康检查：

```bash
openclaw health
```

如果您的构建中没有入站功能：

- 运行 `openclaw setup`，然后 `openclaw channels login`，然后手动启动Gateway (`openclaw gateway`)。

## 前沿的工作流（终端中的Gateway）

目标：在TypeScript Gateway上工作，获取热重载，保持macOS应用程序UI附加。

### 0) （可选）也从源码运行macOS应用程序

如果您也希望macOS应用程序处于前沿：

```bash
./scripts/restart-mac.sh
```

### 1) 启动开发Gateway

```bash
pnpm install
pnpm gateway:watch
```

`gateway:watch` 以监视模式运行网关，并在TypeScript更改时重新加载。

### 2) 将macOS应用程序指向正在运行的Gateway

在 **OpenClaw.app** 中：

- 连接模式：**本地**
  应用程序将附加到配置端口上的正在运行的网关。

### 3) 验证

- 应用程序内的网关状态应显示 **“使用现有网关 …”**
- 或者通过CLI：

```bash
openclaw health
```

### 常见陷阱

- **错误的端口:** Gateway WS默认为 `ws://127.0.0.1:18789`；保持应用程序和CLI在同一端口。
- **状态存储位置:**
  - 凭据: `~/.openclaw/credentials/`
  - 会话: `~/.openclaw/agents/<agentId>/sessions/`
  - 日志: `/tmp/openclaw/`

## 凭据存储映射

调试身份验证或决定要备份什么时使用此映射：

- **WhatsApp**: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
- **Telegram机器人令牌**: config/env 或 `channels.telegram.tokenFile`
- **Discord机器人令牌**: config/env（尚不支持令牌文件）
- **Slack令牌**: config/env (`channels.slack.*`)
- **配对允许列表**: `~/.openclaw/credentials/<channel>-allowFrom.json`
- **模型身份验证配置文件**: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **旧版OAuth导入**: `~/.openclaw/credentials/oauth.json`
  更多详情: [安全性](/gateway/security#credential-storage-map)。

## 更新（不破坏您的设置）

- 将 `~/.openclaw/workspace` 和 `~/.openclaw/` 作为“您的东西”；不要将个人提示/配置放入 `openclaw` 仓库。
- 更新源代码: `git pull` + `pnpm install`（当锁文件更改时）+ 继续使用 `pnpm gateway:watch`。

## Linux（systemd用户服务）

Linux安装使用systemd **用户**服务。默认情况下，systemd在注销/空闲时停止用户服务，这会终止Gateway。入站尝试为您启用持久性（可能需要sudo权限）。如果仍然关闭，请运行：

```bash
sudo loginctl enable-linger $USER
```

对于始终在线或多用户服务器，考虑使用**系统**服务而不是用户服务（不需要持久性）。请参阅[Gateway运行手册](/gateway)中的systemd说明。

## 相关文档

- [Gateway运行手册](/gateway)（标志、监督、端口）
- [Gateway配置](/gateway/configuration)（配置架构 + 示例）
- [Discord](/channels/discord) 和 [Telegram](/channels/telegram)（回复标签 + replyToMode设置）
- [OpenClaw助手设置](/start/openclaw)
- [macOS应用程序](/platforms/macos)（网关生命周期）