---
summary: "Remote access using SSH tunnels (Gateway WS) and tailnets"
read_when:
  - Running or troubleshooting remote gateway setups
title: "Remote Access"
---
# 远程访问（SSH、tunnels 和 tailnets）

本仓库支持"remote over SSH"，通过在专用主机（桌面/服务器）上运行单个 Gateway（主控）并将客户端连接至它来实现。

- 对于**操作员（您 / macOS 应用）**：SSH tunneling 是通用的 fallback 方案。
- 对于**节点（iOS/Android 及未来设备）**：连接至 Gateway **WebSocket**（根据需要采用 LAN/tailnet 或 SSH tunnel）。

## 核心理念

- Gateway WebSocket 绑定到您配置端口的 **loopback**（默认为 18789）。
- 对于远程使用，您通过 SSH 转发该 loopback 端口（或使用 tailnet/VPN 并减少 tunnel 使用）。

## 常见 VPN/tailnet 设置（agent 所在位置）

将 **Gateway host** 视为"agent 所在位置”。它拥有 sessions、auth profiles、channels 和 state。
您的笔记本电脑/桌面（及节点）连接至该主机。

### 1) tailnet 中始终在线的 Gateway（VPS 或家庭服务器）

在持久化主机上运行 Gateway，并通过 **Tailscale** 或 SSH 访问它。

- **最佳用户体验：** 保留 `gateway.bind: "loopback"` 并使用 **Tailscale Serve** 用于 Control UI。
- **Fallback：** 保留 loopback + 从任何需要访问的机器建立 SSH tunnel。
- **示例：** [exe.dev](/install/exe-dev) (简易 VM) 或 [Hetzner](/install/hetzner) (生产环境 VPS)。

当您的笔记本电脑经常睡眠但您希望 agent 始终在线时，这是理想选择。

### 2) 家庭桌面运行 Gateway，笔记本电脑作为远程控制

笔记本电脑 **不** 运行 agent。它远程连接：

- 使用 macOS 应用的 **Remote over SSH** 模式（Settings → General →"OpenClaw runs"）。
- 应用打开并管理 tunnel，因此 WebChat + health checks“即可用”。

操作手册：[macOS 远程访问](/platforms/mac/remote)。

### 3) 笔记本电脑运行 Gateway，从其他机器远程访问

保持 Gateway 本地化但安全地暴露它：

- 从其他机器 SSH tunnel 到笔记本电脑，或
- Tailscale Serve Control UI 并保持 Gateway 仅 loopback。

指南：[Tailscale](/gateway/tailscale) 和 [Web 概览](/web)。

## 命令流（运行位置）

一个 gateway service 拥有 state + channels。Nodes 是外围设备。

流示例 (Telegram → node)：

- Telegram 消息到达 **Gateway**。
- Gateway 运行 **agent** 并决定是否调用 node tool。
- Gateway 通过 Gateway WebSocket (`node.*` RPC) 调用 **node**。
- Node 返回结果；Gateway 回复回 Telegram。

注意：

- **Nodes 不运行 gateway service。** 除非您有意运行隔离的 profiles（见 [多个 gateways](/gateway/multiple-gateways)），否则每台主机应只运行一个 gateway。
- macOS 应用"node mode"只是通过 Gateway WebSocket 的 node client。

## SSH tunnel (CLI + tools)

创建到远程 Gateway WS 的本地 tunnel：

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

Tunnel 建立后：

- `openclaw health` 和 `openclaw status --deep` 现在通过 `ws://127.0.0.1:18789` 到达远程 gateway。
- `openclaw gateway {status,health,send,agent,call}` 也可以在需要时通过 `--url` 定位转发的 URL。

注意：将 `18789` 替换为您配置的 `gateway.port`（或 `--port`/`OPENCLAW_GATEWAY_PORT`）。
注意：当您传递 `--url` 时，CLI 不会 fallback 到 config 或 environment credentials。
显式包含 `--token` 或 `--password`。缺少显式 credentials 是一个错误。

## CLI remote 默认值

您可以持久化一个 remote target，以便 CLI 命令默认使用它：

```json5
{
  gateway: {
    mode: "remote",
    remote: {
      url: "ws://127.0.0.1:18789",
      token: "your-token",
    },
  },
}
```

当 gateway 是 loopback-only 时，将 URL 保持在 `ws://127.0.0.1:18789` 并首先打开 SSH tunnel。

## Credential 优先级

Gateway credential 解析遵循一个共享契约，涵盖 call/probe/status 路径、Discord exec-approval 监控和 node-host 连接：

- 显式 credentials (`--token`, `--password`, 或 tool `gatewayToken`) 在接受显式 auth 的 call 路径上始终优先。
- URL override 安全：
  - CLI URL overrides (`--url`) 从不重用隐式 config/env credentials。
  - Env URL overrides (`OPENCLAW_GATEWAY_URL`) 可能仅使用 env credentials (`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`)。
- Local mode 默认值：
  - token: `OPENCLAW_GATEWAY_TOKEN` -> `gateway.auth.token` -> `gateway.remote.token`
  - password: `OPENCLAW_GATEWAY_PASSWORD` -> `gateway.auth.password` -> `gateway.remote.password`
- Remote mode 默认值：
  - token: `gateway.remote.token` -> `OPENCLAW_GATEWAY_TOKEN` -> `gateway.auth.token`
  - password: `OPENCLAW_GATEWAY_PASSWORD` -> `gateway.remote.password` -> `gateway.auth.password`
- Remote probe/status token 检查默认严格：当 targeting remote mode 时，它们仅使用 `gateway.remote.token`（无 local token fallback）。
- 遗留 `CLAWDBOT_GATEWAY_*` env vars 仅由 compatibility call 路径使用；probe/status/auth 解析仅使用 `OPENCLAW_GATEWAY_*`。

## Chat UI over SSH

WebChat 不再使用单独的 HTTP 端口。SwiftUI chat UI 直接连接至 Gateway WebSocket。

- 通过 SSH 转发 `18789`（见上文），然后将 clients 连接至 `ws://127.0.0.1:18789`。
- 在 macOS 上，首选应用的"Remote over SSH"模式，它自动管理 tunnel。

## macOS 应用"Remote over SSH"

macOS 菜单栏应用可以端到端驱动相同的设置（remote status checks、WebChat 和 Voice Wake forwarding）。

操作手册：[macOS 远程访问](/platforms/mac/remote)。

## 安全规则 (remote/VPN)

简短版本：**保持 Gateway loopback-only**，除非您确定需要 bind。

- **Loopback + SSH/Tailscale Serve** 是最安全的默认值（无公开暴露）。
- 明文 `ws://` 默认是 loopback-only。对于受信任的私有网络，
  在 client 进程上设置 `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` 作为 break-glass。
- **非 loopback binds** (`lan`/`tailnet`/`custom`，或当 loopback 不可用时使用 `auto`) 必须使用 auth tokens/passwords。
- `gateway.remote.token` / `.password` 是 client credential 来源。它们本身 **不** 配置 server auth。
- 当 `gateway.auth.*` 未设置时，Local call 路径可以使用 `gateway.remote.*` 作为 fallback。
- `gateway.remote.tlsFingerprint` 在使用 `wss://` 时固定远程 TLS cert。
- **Tailscale Serve** 可以通过 identity
  headers 在 `gateway.auth.allowTailscale: true` 时认证 Control UI/WebSocket 流量；HTTP API  endpoints 仍然
  需要 token/password auth。此 tokenless 流假设 gateway host 是
  受信任的。如果您希望 everywhere 都使用 tokens/passwords，将其设置为 `false`。
- 将 browser control 视为 operator access：仅 tailnet +  手动 node 配对。

深入探讨：[安全](/gateway/security)。