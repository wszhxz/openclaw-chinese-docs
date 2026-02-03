---
summary: "Gateway runtime on macOS (external launchd service)"
read_when:
  - Packaging OpenClaw.app
  - Debugging the macOS gateway launchd service
  - Installing the gateway CLI for macOS
title: "Gateway on macOS"
---
# macOS 上的网关（外部 launchd）

OpenClaw.app 不再捆绑 Node.js/Bun 或网关运行时。macOS 应用程序期望一个**外部**的 `openclaw` 命令行工具安装，不会将网关作为子进程启动，并管理一个用户级的 launchd 服务以保持网关运行（或连接到已运行的本地网关）。

## 安装 CLI（本地模式必需）

您需要在 Mac 上安装 Node.js 22+，然后全局安装 `openclaw`：

```bash
npm install -g openclaw@<version>
```

macOS 应用程序的 **安装 CLI** 按钮通过 npm/pnpm 运行相同的流程（不推荐使用 bun 作为网关运行时）。

## launchd（作为 LaunchAgent 的网关）

标签：

- `bot.molt.gateway`（或 `bot.molt.<profile>`；旧版 `com.openclaw.*` 可能保留）

plist 文件位置（用户级）：

- `~/Library/LaunchAgents/bot.molt.gateway.plist`
  （或 `~/Library/LaunchAgents/bot.molt.<profile>.plist`）

管理器：

- macOS 应用程序在本地模式下拥有 LaunchAgent 的安装/更新权限。
- CLI 也可以安装它：`openclaw gateway install`。

行为：

- “OpenClaw 已激活”启用/禁用 LaunchAgent。
- 应用程序退出不会停止网关（launchd 会保持其运行）。
- 如果配置端口上已运行网关，应用程序会连接到它而不是启动一个新的。

日志：

- launchd 标准输出/错误日志：`/tmp/openclaw/openclaw-gateway.log`

## 版本兼容性

macOS 应用程序会检查网关版本与其自身版本的兼容性。如果版本不兼容，请更新全局 CLI 以匹配应用程序版本。

## 简易检查

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