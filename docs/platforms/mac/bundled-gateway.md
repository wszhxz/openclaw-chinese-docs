---
summary: "Gateway runtime on macOS (external launchd service)"
read_when:
  - Packaging OpenClaw.app
  - Debugging the macOS gateway launchd service
  - Installing the gateway CLI for macOS
title: "Gateway on macOS"
---
# macOS上的网关 (外部 launchd)

OpenClaw.app 不再捆绑 Node/Bun 或网关运行时。macOS 应用程序
期望一个 **外部** `openclaw` CLI 安装，不会将网关作为子进程启动，并管理每个用户的 launchd 服务以保持网关运行（或者如果已经有一个本地网关在运行，则附加到该网关）。

## 安装 CLI（本地模式必需）

你需要在 Mac 上安装 Node 22+，然后全局安装 `openclaw`：

```bash
npm install -g openclaw@<version>
```

macOS 应用程序的 **Install CLI** 按钮通过 npm/pnpm 运行相同的流程（不建议使用 bun 作为网关运行时）。

## Launchd（网关作为 LaunchAgent）

标签：

- `bot.molt.gateway`（或 `bot.molt.<profile>`；旧版 `com.openclaw.*` 可能仍然存在）

Plist 位置（每个用户）：

- `~/Library/LaunchAgents/bot.molt.gateway.plist`
  （或 `~/Library/LaunchAgents/bot.molt.<profile>.plist`）

管理器：

- macOS 应用程序在本地模式下拥有 LaunchAgent 的安装/更新。
- CLI 也可以安装它：`openclaw gateway install`。

行为：

- “OpenClaw Active” 启用/禁用 LaunchAgent。
- 应用退出 **不会** 停止网关（launchd 会保持其运行）。
- 如果配置端口上已经有一个网关在运行，应用程序会附加到该网关而不是启动一个新的。

日志记录：

- launchd stdout/err: `/tmp/openclaw/openclaw-gateway.log`

## 版本兼容性

macOS 应用程序会检查网关版本是否与其自身版本兼容。如果不兼容，请更新全局 CLI 以匹配应用程序版本。

## 烟雾测试

```bash
openclaw --version

OPENCLAW_SKIP_CHANNELS=1 \
OPENCLAW_SKIP_CANVAS_HOST=1 \
openclaw gateway --port 18999 --bind loopback
```

然后：

```bash
openclaw gateway call health --url ws://127.0.0.1:18999 --timeout 3000
```