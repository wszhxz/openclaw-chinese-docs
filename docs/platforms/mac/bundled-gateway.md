---
summary: "Gateway runtime on macOS (external launchd service)"
read_when:
  - Packaging OpenClaw.app
  - Debugging the macOS gateway launchd service
  - Installing the gateway CLI for macOS
title: "Gateway on macOS"
---
# macOS上的Gateway (外部launchd)

OpenClaw.app不再捆绑Node/Bun或Gateway运行时。macOS应用程序
期望一个**外部** `openclaw` CLI安装，不作为子进程启动Gateway，并管理每个用户的launchd服务以保持Gateway运行（或者如果已经有正在运行的本地Gateway，则附加到该Gateway）。

## 安装CLI（本地模式必需）

你需要在Mac上安装Node 22+，然后全局安装`openclaw`：

```bash
npm install -g openclaw@<version>
```

macOS应用程序的**Install CLI**按钮通过npm/pnpm运行相同的流程（不推荐使用bun作为Gateway运行时）。

## Launchd (Gateway作为LaunchAgent)

标签：

- `bot.molt.gateway` (或 `bot.molt.<profile>`；旧版 `com.openclaw.*` 可能仍然存在)

Plist位置（每个用户）：

- `~/Library/LaunchAgents/bot.molt.gateway.plist`
  (或 `~/Library/LaunchAgents/bot.molt.<profile>.plist`)

管理器：

- macOS应用程序在本地模式下拥有LaunchAgent的安装/更新。
- CLI也可以安装它：`openclaw gateway install`。

行为：

- “OpenClaw Active”启用/禁用LaunchAgent。
- 应用程序退出**不会**停止网关（launchd会保持其运行）。
- 如果配置端口上已经有一个Gateway正在运行，应用程序将附加到该Gateway而不是启动一个新的。

日志记录：

- launchd stdout/err: `/tmp/openclaw/openclaw-gateway.log`

## 版本兼容性

macOS应用程序会检查网关版本是否与其自身版本兼容。如果不兼容，请将全局CLI更新为与应用程序版本匹配。

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