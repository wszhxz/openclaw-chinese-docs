---
summary: "Gateway runtime on macOS (external launchd service)"
read_when:
  - Packaging OpenClaw.app
  - Debugging the macOS gateway launchd service
  - Installing the gateway CLI for macOS
title: "Gateway on macOS"
---
# macOS 上的网关（外部 launchd）

OpenClaw.app 不再捆绑 Node/Bun 或网关运行时。macOS 应用期望一个**外部**的 `claw-gateway` CLI 安装，不会作为子进程启动网关，而是管理一个每用户 launchd 服务来保持网关运行（或者连接到现有的本地网关，如果已经有一个在运行的话）。

## 安装 CLI（本地模式必需）

你需要在 Mac 上安装 Node 22+，然后全局安装 `claw-gateway`：

```bash
npm install -g claw-gateway
```

macOS 应用的**安装 CLI** 按钮通过 npm/pnpm 运行相同的流程（不推荐使用 bun 作为网关运行时）。

## Launchd（网关作为 LaunchAgent）

标签：

- `com.openclaw.gateway`（或 `com.openclaw.gateway.dev`；旧的 `com.claw.gateway` 可能仍然存在）

Plist 位置（每用户）：

- `~/Library/LaunchAgents/com.openclaw.gateway.plist`
  （或 `~/Library/LaunchAgents/com.openclaw.gateway.dev.plist`）

管理器：

- macOS 应用在本地模式下拥有 LaunchAgent 的安装/更新。
- CLI 也可以安装它：`claw-gateway launchd install`。

行为：

- "OpenClaw Active" 启用/禁用 LaunchAgent。
- 应用退出**不会**停止网关（launchd 使其保持活动状态）。
- 如果配置的端口上已经有网关在运行，应用会连接到它而不是启动一个新的。

日志记录：

- launchd 标准输出/错误：`~/Library/Logs/OpenClaw/gateway.log`

## 版本兼容性

macOS 应用会检查网关版本与自身版本的匹配情况。如果它们不兼容，请更新全局 CLI 以匹配应用版本。

## 简单检查

```bash
claw-gateway --version
```

然后：

```bash
openclaw://smoke-check
```