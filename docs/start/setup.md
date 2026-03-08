---
summary: "Advanced setup and development workflows for OpenClaw"
read_when:
  - Setting up a new machine
  - You want “latest + greatest” without breaking your personal setup
title: "Setup"
---
# 设置

<Note>
If you are setting up for the first time, start with [Getting Started](/start/getting-started).
For wizard details, see [Onboarding Wizard](/start/wizard).
</Note>

最后更新：2026-01-01

## 简要总结

- **定制内容存放在 repo 之外：** `~/.openclaw/workspace` (workspace) + `~/.openclaw/openclaw.json` (config)。
- **稳定工作流：** 安装 macOS app；让它运行 bundled Gateway。
- **前沿工作流：** 通过 `pnpm gateway:watch` 自行运行 Gateway，然后让 macOS app 以 Local mode 连接。

## 前置条件（源码）

- Node `>=22`
- `pnpm`
- Docker（可选；仅用于 containerized setup/e2e — 参见 [Docker](/install/docker)）

## 定制策略（以免更新受影响）

如果你想要"100% 个性化定制”_且_ 易于更新，请将自定义内容保存在：

- **Config:** `~/.openclaw/openclaw.json` (JSON/JSON5-ish)
- **Workspace:** `~/.openclaw/workspace` (skills, prompts, memories; 使其成为一个 private git repo)

Bootstrap 一次：

```bash
openclaw setup
```

在此 repo 内部，使用本地 CLI 入口：

```bash
openclaw setup
```

如果你还没有 global install，请通过 `pnpm openclaw setup` 运行。

## 从此 repo 运行 Gateway

在 `pnpm build` 之后，你可以直接运行 packaged CLI：

```bash
node openclaw.mjs gateway --port 18789 --verbose
```

## 稳定工作流（优先 macOS app）

1. 安装 + 启动 **OpenClaw.app**（menu bar）。
2. 完成 onboarding/permissions 清单（TCC prompts）。
3. 确保 Gateway 处于 **Local** 状态且正在运行（app 会管理它）。
4. 连接 surfaces（例如：WhatsApp）：

```bash
openclaw channels login
```

5. Sanity check：

```bash
openclaw health
```

如果 onboarding 在你的 build 中不可用：

- 运行 `openclaw setup`，然后 `openclaw channels login`，然后手动启动 Gateway (`openclaw gateway`)。

## 前沿工作流（在终端中运行 Gateway）

目标：开发 TypeScript Gateway，获得 hot reload，保持 macOS app UI 连接。

### 0)（可选）也从源码运行 macOS app

如果你也希望 macOS app 处于前沿版本：

```bash
./scripts/restart-mac.sh
```

### 1) 启动 dev Gateway

```bash
pnpm install
pnpm gateway:watch
```

`gateway:watch` 以 watch mode 运行 gateway，并在 TypeScript 更改时 reload。

### 2) 将 macOS app 指向你运行的 Gateway

在 **OpenClaw.app** 中：

- Connection Mode: **Local**
  app 将连接到 configured port 上运行的 gateway。

### 3) 验证

- App 内 Gateway 状态应显示 **"Using existing gateway …"**
- 或通过 CLI：

```bash
openclaw health
```

### 常见陷阱

- **端口错误：** Gateway WS 默认为 `ws://127.0.0.1:18789`；保持 app + CLI 在同一端口。
- **状态存储位置：**
  - Credentials: `~/.openclaw/credentials/`
  - Sessions: `~/.openclaw/agents/<agentId>/sessions/`
  - Logs: `/tmp/openclaw/`

## 凭据存储映射

在调试 auth 或决定备份内容时使用此映射：

- **WhatsApp**: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
- **Telegram bot token**: config/env 或 `channels.telegram.tokenFile`
- **Discord bot token**: config/env 或 SecretRef (env/file/exec providers)
- **Slack tokens**: config/env (`channels.slack.*`)
- **Pairing allowlists**:
  - `~/.openclaw/credentials/<channel>-allowFrom.json` (default account)
  - `~/.openclaw/credentials/<channel>-<accountId>-allowFrom.json` (non-default accounts)
- **Model auth profiles**: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **File-backed secrets payload (optional)**: `~/.openclaw/secrets.json`
- **Legacy OAuth import**: `~/.openclaw/credentials/oauth.json`
  更多详情：[安全](/gateway/security#credential-storage-map)。

## 更新（而不破坏你的设置）

- 将 `~/.openclaw/workspace` 和 `~/.openclaw/` 保留为"你的内容"；不要将个人 prompts/config 放入 `openclaw` repo。
- 更新源码：`git pull` + `pnpm install` (当 lockfile 更改时) + 继续使用 `pnpm gateway:watch`。

## Linux (systemd user service)

Linux 安装使用 systemd **user** service。默认情况下，systemd 会在 logout/idle 时停止 user
services，这会杀死 Gateway。Onboarding 会尝试为你 enable
lingering（可能会提示 sudo）。如果仍然关闭，请运行：

```bash
sudo loginctl enable-linger $USER
```

对于 always-on 或 multi-user 服务器，请考虑使用 **system** service 而不是
user service（不需要 lingering）。参见 [Gateway runbook](/gateway) 获取 systemd 说明。

## 相关文档

- [Gateway runbook](/gateway) (flags, supervision, ports)
- [Gateway configuration](/gateway/configuration) (config schema + examples)
- [Discord](/channels/discord) 和 [Telegram](/channels/telegram) (reply tags + replyToMode settings)
- [OpenClaw assistant setup](/start/openclaw)
- [macOS app](/platforms/macos) (gateway lifecycle)