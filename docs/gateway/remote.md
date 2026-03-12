---
summary: "Remote access using SSH tunnels (Gateway WS) and tailnets"
read_when:
  - Running or troubleshooting remote gateway setups
title: "Remote Access"
---
# 远程访问（SSH、隧道和 Tailnet）

本仓库通过在专用主机（台式机/服务器）上持续运行一个网关（主网关），并让客户端连接该网关，来支持“通过 SSH 远程访问”。

- 对于 **运维人员（您 / macOS 应用）**：SSH 隧道是通用的备用方案。  
- 对于 **节点（iOS/Android 及未来设备）**：连接至网关的 **WebSocket**（局域网/Tailnet 或按需通过 SSH 隧道）。

## 核心思路

- 网关 WebSocket 绑定到您所配置端口上的 **回环地址（loopback）**（默认为 18789）。  
- 对于远程使用场景，您可通过 SSH 转发该回环端口（或借助 Tailnet/VPN 实现更少的隧道开销）。

## 常见的 VPN/Tailnet 部署方式（代理所在位置）

将 **网关主机** 视为“代理所在的位置”。它拥有会话、认证配置文件、通道及状态。  
您的笔记本电脑/台式机（以及节点）均连接至该主机。

### 1) 在您的 Tailnet 中常驻运行的网关（VPS 或家庭服务器）

在持久化主机上运行网关，并通过 **Tailscale** 或 SSH 访问它。

- **最佳用户体验**：保留 `gateway.bind: "loopback"`，并使用 **Tailscale Serve** 提供控制界面（Control UI）。  
- **备用方案**：保留回环绑定 + 从任何需要访问的机器建立 SSH 隧道。  
- **示例**：[exe.dev](/install/exe-dev)（简易虚拟机）或 [Hetzner](/install/hetzner)（生产级 VPS）。

当您的笔记本电脑频繁休眠，但您希望代理始终在线时，此方案最为理想。

### 2) 家庭台式机运行网关，笔记本作为远程控制器

笔记本 **不运行** 代理，仅远程连接：

- 使用 macOS 应用的 **Remote over SSH** 模式（设置 → 通用 → “OpenClaw 运行于”）。  
- 应用自动打开并管理隧道，因此 WebChat 和健康检查可“即开即用”。

操作指南：[macOS 远程访问](/platforms/mac/remote)。

### 3) 笔记本运行网关，其他机器远程访问

保持网关本地运行，但安全地对外暴露：

- 从其他机器向笔记本建立 SSH 隧道；或  
- 使用 Tailscale Serve 提供控制界面（Control UI），同时确保网关仅绑定回环地址。

参考指南：[Tailscale](/gateway/tailscale) 和 [Web 概览](/web)。

## 命令执行流程（各组件运行位置）

一个网关服务独占状态与通道管理。节点仅为外围设备。

流程示例（Telegram → 节点）：

- Telegram 消息抵达 **网关**。  
- 网关运行 **代理**，并决定是否调用某个节点工具。  
- 网关通过网关 WebSocket（`node.*` RPC）调用 **节点**。  
- 节点返回结果；网关再将响应转发回 Telegram。

注意事项：

- **节点不运行网关服务**。除非您有意运行隔离的配置文件（参见 [多个网关](/gateway/multiple-gateways)），否则每台主机上应仅运行一个网关。  
- macOS 应用的“节点模式”本质上只是通过网关 WebSocket 连接的节点客户端。

## SSH 隧道（CLI + 工具）

创建指向远程网关 WebSocket 的本地隧道：

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

隧道建立后：

- `openclaw health` 和 `openclaw status --deep` 即可通过 `ws://127.0.0.1:18789` 访问远程网关。  
- `openclaw gateway {status,health,send,agent,call}` 在必要时也可通过 `--url` 指向已转发的 URL。

注意：请将 `18789` 替换为您所配置的 `gateway.port`（或 `--port`/`OPENCLAW_GATEWAY_PORT`）。  
注意：当您传入 `--url` 时，CLI 不会回退至配置文件或环境变量中的凭据。  
请显式包含 `--token` 或 `--password`；缺少显式凭据将报错。

## CLI 远程默认值

您可以持久化一个远程目标，使 CLI 命令默认使用它：

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

当网关仅绑定回环地址时，请将 URL 保持为 `ws://127.0.0.1:18789`，并先开启 SSH 隧道。

## 凭据优先级

网关凭据解析在调用/探测/状态查询路径、Discord 执行审批监控以及节点-主机连接中，遵循统一规则：

- 显式凭据（`--token`、`--password` 或工具级 `gatewayToken`）在支持显式认证的调用路径中始终具有最高优先级。  
- URL 覆盖安全性：  
  - CLI URL 覆盖（`--url`）**绝不会**复用隐式配置/环境变量中的凭据。  
  - 环境变量 URL 覆盖（`OPENCLAW_GATEWAY_URL`）**仅可**使用环境变量凭据（`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`）。  
- 本地模式默认值：  
  - token：`OPENCLAW_GATEWAY_TOKEN` → `gateway.auth.token` → `gateway.remote.token`  
  - password：`OPENCLAW_GATEWAY_PASSWORD` → `gateway.auth.password` → `gateway.remote.password`  
- 远程模式默认值：  
  - token：`gateway.remote.token` → `OPENCLAW_GATEWAY_TOKEN` → `gateway.auth.token`  
  - password：`OPENCLAW_GATEWAY_PASSWORD` → `gateway.remote.password` → `gateway.auth.password`  
- 远程探测/状态查询的 token 检查默认为严格模式：在远程模式下，**仅使用 `gateway.remote.token`**（无本地 token 回退）。  
- 遗留的 `CLAWDBOT_GATEWAY_*` 环境变量仅用于兼容性调用路径；探测/状态/认证解析**仅使用 `OPENCLAW_GATEWAY_*`**。

## 通过 SSH 访问聊天界面（Chat UI）

WebChat 不再使用独立的 HTTP 端口。SwiftUI 聊天界面直接连接至网关 WebSocket。

- 通过 SSH 转发 `18789`（见上文），然后让客户端连接至 `ws://127.0.0.1:18789`。  
- 在 macOS 上，建议优先使用应用的“Remote over SSH”模式，该模式可自动管理隧道。

## macOS 应用“Remote over SSH”

macOS 菜单栏应用可端到端驱动整套设置（远程状态检查、WebChat 及语音唤醒转发）。

操作指南：[macOS 远程访问](/platforms/mac/remote)。

## 安全规则（远程/VPN）

简要版：**请始终将网关设为仅绑定回环地址（loopback-only）**，除非您明确需要绑定其他地址。

- **回环地址 + SSH/Tailscale Serve** 是最安全的默认配置（无公网暴露风险）。  
- 明文 `ws://` 默认仅绑定回环地址。在可信私有网络中，可在客户端进程设置 `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` 作为应急措施（break-glass）。  
- **非回环地址绑定**（`lan`/`tailnet`/`custom`，或当回环不可用时的 `auto`）必须启用身份令牌/密码认证。  
- `gateway.remote.token` / `.password` 是客户端凭据来源，**本身并不配置服务端认证**。  
- 本地调用路径可在 `gateway.auth.*` 未设置时，以 `gateway.remote.*` 作为回退选项。  
- 使用 `wss://` 时，`gateway.remote.tlsFingerprint` 用于固定远程 TLS 证书。  
- **Tailscale Serve** 可通过身份头（identity headers）对控制界面（Control UI）/WebSocket 流量进行身份验证（当 `gateway.auth.allowTailscale: true` 时）；HTTP API 接口仍需令牌/密码认证。该免令牌流程的前提是网关主机本身可信。若您希望所有位置均强制使用令牌/密码，请将其设为 `false`。  
- 将浏览器控制视为运维人员访问：仅限 Tailnet 内部 + 显式配对节点。

深入探讨：[安全性](/gateway/security)。