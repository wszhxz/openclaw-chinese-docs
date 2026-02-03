---
summary: "Setup guide: keep your OpenClaw setup tailored while staying up-to-date"
read_when:
  - Setting up a new machine
  - You want “latest + greatest” without breaking your personal setup
title: "Setup"
---
# 设置

最后更新时间：2026-01-01

## TL;DR

- **定制内容位于仓库外部**：`~/.openclaw/workspace`（工作区）+ `~/.openclaw/openclaw.json`（配置文件）。
- **稳定工作流程**：安装 macOS 应用程序；让其运行捆绑的网关。
- **前沿工作流程**：通过 `pnpm gateway:watch` 手动运行网关，然后让 macOS 应用程序以本地模式附加。

## 先决条件（从源码安装）

- Node `>=22`
- `pnpm`
- Docker（可选；仅用于容器化设置/e2e — 参见 [Docker](/install/docker)）

## 定制策略（防止更新破坏）

如果你想实现“100% 个性化” _and_ 简单更新，请将你的定制内容保存在以下位置：

- **配置**：`~/.openclaw/openclaw.json`（JSON/JSON5 类似格式）
- **工作区**：`~/.openclaw/workspace`（技能、提示、记忆；将其设为私有 Git 仓库）

首次设置：

```bash
openclaw setup
```

在该仓库内使用本地 CLI 入口：

```bash
openclaw setup
```

如果你尚未全局安装，通过 `pnpm openclaw setup` 运行。

## 稳定工作流程（macOS 应用程序优先）

1. 安装并启动 **OpenClaw.app**（菜单栏）。
2. 完成引导/权限检查清单（TCC 提示）。
3. 确保网关为 **本地** 并正在运行（应用程序会管理此过程）。
4. 绑定界面（示例：WhatsApp）：

```bash
openclaw channels login
```

5. 简单检查：

```bash
openclaw health
```

如果构建中未提供引导功能：

- 运行 `openclaw setup`，然后 `openclaw channels login`，然后手动启动网关（`openclaw gateway`）。

## 前沿工作流程（网关在终端中）

目标：在 TypeScript 网关上工作，实现热重载，并保持 macOS 应用程序 UI 附加。

### 0)（可选）也从源码运行 macOS 应用程序

如果你想在前沿版本中使用 macOS 应用程序：

```bash
./scripts/restart-mac.sh
```

### 1) 启动开发网关

```bash
pnpm install
pnpm gateway:watch
```

`gateway:watch` 以监听模式运行网关，并在 TypeScript 变化时重新加载。

### 2) 将 macOS 应用程序指向你正在运行的网关

在 **OpenClaw.app** 中：

- 连接模式：**本地**
  应用程序将连接到配置端口上的运行中的网关。

### 3) 验证

- 应用程序内的网关状态应显示为 **“使用现有网关 …”**
- 或通过 CLI：

```bash
openclaw health
```

## 常见陷阱

- **错误端口**：网关 WS 默认为 `ws://127.0.0.1:18789`；请保持应用程序和 CLI 在同一端口。
- **状态存储位置**：
  - 凭据：`~/.openclaw/credentials/`
  - 会话：`~/.openclaw/agents/<agentId>/sessions/`
  - 日志：`/tmp/openclaw/`

## 凭据存储映射

调试认证或决定备份内容时使用以下信息：

- **WhatsApp**：`~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
- **Telegram 机器人令牌**：配置/环境或 `channels.telegram.tokenFile`
- **Discord 机器人令牌**：配置/环境（令牌文件尚未支持）
- **Slack 令牌**：配置/环境（`channels.slack.*`）
- **配对允许列表**：`~/.openclaw/credentials/<channel>-allowFrom.json`
- **模型认证配置文件**：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **传统 OAuth 导入**：`~/.openclaw/credentials/oauth.json`
  更多详情：[安全](/gateway/security#credential-storage-map)。

## 更新（不破坏你的设置）

- 保持 `~/.openclaw/workspace` 和 `~/.openclaw/` 作为“你的内容”；不要将个人提示/配置文件放入 `openclaw` 仓库中。
- 更新源码：`git pull` + `pnpm install`（当锁定文件更改时）+ 保持使用 `pnpm gateway:watch`。

## Linux（systemd 用户服务）

Linux 安装使用 **systemd 用户服务**。默认情况下，systemd 在注销/空闲时停止用户服务，这会终止网关。引导尝试为你启用持续运行（可能需要 sudo 提示）。如果仍未启用，运行：

```bash
sudo loginctl enable-linger $USER
```

对于始终运行或多人使用的服务器，考虑使用 **系统** 服务而非用户服务（无需持续运行）。参见 [网关运行手册](/gateway) 中的 systemd 说明。

## 相关文档

- [网关运行手册](/gateway)（标志、监督、端口）
- [网关配置](/gateway/configuration)（配置模式 + 示例）
- [Discord](/channels/discord) 和 [Telegram](/channels/telegram)（回复标签 + 回复模式设置）
- [OpenClaw 助手设置](/start/openclaw)
- [macOS 应用程序](/platforms/macos)（网关生命周期）