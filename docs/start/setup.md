---
summary: "Advanced setup and development workflows for OpenClaw"
read_when:
  - Setting up a new machine
  - You want “latest + greatest” without breaking your personal setup
title: "Setup"
---
# 安装配置

<Note>
If you are setting up for the first time, start with [Getting Started](/start/getting-started).
For wizard details, see [Onboarding Wizard](/start/wizard).
</Note>

最后更新：2026-01-01

## 快速概览（TL;DR）

- **定制化内容独立于代码仓库之外**：`~/.openclaw/workspace`（工作区） + `~/.openclaw/openclaw.json`（配置文件）。
- **稳定工作流**：安装 macOS 应用；由其自动运行内置的 Gateway。
- **前沿工作流（Bleeding edge）**：通过 `pnpm gateway:watch` 手动运行 Gateway，然后让 macOS 应用以本地模式（Local mode）连接。

## 前置依赖（从源码构建）

- Node `>=22`
- `pnpm`
- Docker（可选；仅用于容器化部署/端到端测试 — 参见 [Docker](/install/docker)）

## 定制化策略（确保升级不破坏现有配置）

若你希望实现“100% 专属定制”且同时便于后续升级，请将所有自定义内容保留在以下位置：

- **配置文件**：`~/.openclaw/openclaw.json`（JSON / 类 JSON5 格式）
- **工作区**：`~/.openclaw/workspace`（含技能、提示词、记忆等；建议设为私有 Git 仓库）

首次初始化引导：

```bash
openclaw setup
```

在本仓库内，使用本地 CLI 入口：

```bash
openclaw setup
```

若尚未全局安装 CLI，请通过 `pnpm openclaw setup` 运行。

## 从本仓库运行 Gateway

执行 `pnpm build` 后，可直接运行打包好的 CLI：

```bash
node openclaw.mjs gateway --port 18789 --verbose
```

## 稳定工作流（先安装 macOS 应用）

1. 安装并启动 **OpenClaw.app**（位于菜单栏）。
2. 完成初始设置与权限检查清单（系统会弹出 TCC 权限提示）。
3. 确保 Gateway 处于 **本地（Local）模式** 且正在运行（应用会自动管理）。
4. 绑定通信渠道（例如：WhatsApp）：

```bash
openclaw channels login
```

5. 基础验证：

```bash
openclaw health
```

若当前构建版本中未提供初始设置流程：

- 依次运行 `openclaw setup` 和 `openclaw channels login`，然后手动启动 Gateway（`openclaw gateway`）。

## 前沿工作流（Gateway 运行于终端中）

目标：开发 TypeScript 版 Gateway，支持热重载，并保持 macOS 应用 UI 持续连接。

### 0）（可选）同样从源码运行 macOS 应用

如你也希望 macOS 应用保持前沿版本：

```bash
./scripts/restart-mac.sh
```

### 1）启动开发版 Gateway

```bash
pnpm install
pnpm gateway:watch
```

`gateway:watch` 以监听模式运行 Gateway，并在 TypeScript 文件变更时自动重载。

### 2）将 macOS 应用指向你正在运行的 Gateway

在 **OpenClaw.app** 中：

- 连接模式：**本地（Local）**  
  应用将连接至指定端口上正在运行的 Gateway。

### 3）验证连接状态

- 应用内 Gateway 状态应显示为 **“正在使用已有 Gateway …”**
- 或通过 CLI 验证：

```bash
openclaw health
```

### 常见陷阱（Footguns）

- **端口错误**：Gateway WebSocket 默认端口为 `ws://127.0.0.1:18789`；请确保应用与 CLI 使用相同端口。
- **状态数据存储位置**：
  - 凭据：`~/.openclaw/credentials/`
  - 会话：`~/.openclaw/agents/<agentId>/sessions/`
  - 日志：`/tmp/openclaw/`

## 凭据存储映射表

调试认证问题或决定备份范围时请参考此表：

- **WhatsApp**：`~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
- **Telegram 机器人令牌（bot token）**：配置文件/环境变量 或 `channels.telegram.tokenFile`
- **Discord 机器人令牌（bot token）**：配置文件/环境变量 或 SecretRef（支持 env/file/exec 提供器）
- **Slack 令牌**：配置文件/环境变量（`channels.slack.*`）
- **配对白名单（Pairing allowlists）**：
  - `~/.openclaw/credentials/<channel>-allowFrom.json`（默认账户）
  - `~/.openclaw/credentials/<channel>-<accountId>-allowFrom.json`（非默认账户）
- **模型认证配置集（Model auth profiles）**：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **基于文件的密钥载荷（可选）**：`~/.openclaw/secrets.json`
- **旧版 OAuth 导入数据**：`~/.openclaw/credentials/oauth.json`  
  更多详情参见：[安全性](/gateway/security#credential-storage-map)

## 升级指南（避免破坏现有配置）

- 将 `~/.openclaw/workspace` 和 `~/.openclaw/` 视为“你的专属内容”；切勿将个人提示词或配置放入 `openclaw` 仓库中。
- 升级源码时：执行 `git pull` + 当 lockfile 变更时执行 `pnpm install` + 继续使用 `pnpm gateway:watch`。

## Linux（systemd 用户服务）

Linux 安装使用 systemd 的 **用户级（user）服务**。默认情况下，systemd 在用户登出或空闲时会停止用户服务，从而终止 Gateway。初始设置流程会尝试为你启用 `lingering`（可能需要 sudo 权限）。若仍未启用，请运行：

```bash
sudo loginctl enable-linger $USER
```

对于需长期运行或支持多用户的服务器，建议改用 **系统级（system）服务**（无需启用 lingering）。详见 [Gateway 运维手册](/gateway) 中的 systemd 相关说明。

## 相关文档

- [Gateway 运维手册](/gateway)（命令行参数、进程监管、端口配置）
- [Gateway 配置说明](/gateway/configuration)（配置结构与示例）
- [Discord](/channels/discord) 和 [Telegram](/channels/telegram)（回复标签与 replyToMode 设置）
- [OpenClaw 助手安装指南](/start/openclaw)
- [macOS 应用](/platforms/macos)（Gateway 生命周期管理）