---
summary: "Remote access using SSH tunnels (Gateway WS) and tailnets"
read_when:
  - Running or troubleshooting remote gateway setups
title: "Remote Access"
---
# 远程访问（SSH、隧道和尾网）

此仓库通过在专用主机（桌面/服务器）上运行一个网关（主节点）并让客户端连接到它，支持“通过SSH远程访问”。

- 对于**操作者（您/ macOS应用）**：SSH隧道是通用的后备方案。
- 对于**节点（iOS/Android及未来设备）**：连接到网关的**WebSocket**（LAN/尾网或根据需要使用SSH隧道）。

## 核心思想

- 网关的WebSocket绑定到您配置的端口上的**回环接口**（默认为18789）。
- 对于远程使用，您需通过SSH将该回环端口转发（或使用尾网/VPN并无需隧道）。

## 常见的VPN/尾网设置（代理所在位置）

将**网关主机**视为“代理所在位置”。它拥有会话、认证配置文件、通道和状态。
您的笔记本电脑/桌面（以及节点）连接到该主机。

### 1) 您的尾网中始终运行的网关（VPS或家庭服务器）

在持久化主机上运行网关并通过**Tailscale**或SSH访问它。

- **最佳用户体验**：保持`gateway.bind: "loopback"`，并使用**Tailscale Serve**进行控制界面。
- **备用方案**：保持回环接口 + 从任何需要访问的机器通过SSH隧道连接。
- **示例**：[exe.dev](/platforms/exe-dev)（简易虚拟机）或 [Hetzner](/platforms/hetzner)（生产级VPS）。

当您的笔记本电脑经常休眠但希望代理始终运行时，这是理想选择。

### 2) 家庭桌面运行网关，笔记本电脑作为远程控制

笔记本电脑**不**运行代理。它通过远程连接：

- 使用macOS应用的**通过SSH远程访问**模式（设置 → 通用 → “OpenClaw运行”）。
- 应用程序打开并管理隧道，因此网页聊天 + 健康检查“正常运行”。

操作手册：[macOS远程访问](/platforms/mac/remote)。

### 3) 笔记本电脑运行网关，从其他机器进行远程访问

保持网关本地但安全地暴露：

- 从其他机器通过SSH隧道连接到笔记本电脑，或
- 通过Tailscale Serve控制界面并保持网关仅回环接口。

指南：[Tailscale](/gateway/tailscale) 和 [网页概览](/web)。

## 命令流程（哪些服务在何处运行）

一个网关服务拥有状态 + 通道。节点是外围设备。

流程示例（Telegram → 节点）：

- Telegram消息到达**网关**。
- 网关运行**代理**并决定是否调用节点工具。
- 网关通过网关WebSocket调用**节点**（`node.*` RPC）。
- 节点返回结果；网关将结果回复回Telegram。

说明：

- **节点不运行网关服务。** 每个主机仅应运行一个网关，除非您有意运行隔离的配置文件（参见 [多个网关](/gateway/multiple-gateways)）。
- macOS应用的“节点模式”只是通过网关WebSocket的节点客户端。

## SSH隧道（CLI + 工具）

创建到远程网关WebSocket的本地隧道：

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

隧道建立后：

- `openclaw health` 和 `openclaw status --deep` 现在通过 `ws://127.0.0.1:18789` 连接到远程网关。
- `openclaw gateway {status,health,send,agent,call}` 也可通过 `--url` 参数指定转发的URL。

注意：将 `18789` 替换为您配置的 `gateway.port`（或 `--port`/`OPENCLAW_GATEWAY_PORT`）。

## CLI远程默认设置

您可以持久化远程目标，使CLI命令默认使用它：

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

当网关仅回环接口时，保持URL为 `ws://127.0.0.1:18789` 并首先打开SSH隧道。

## 通过SSH的聊天UI

WebChat不再使用单独的HTTP端口。SwiftUI聊天UI直接连接到网关WebSocket。

- 通过SSH转发 `18789`（参见上方），然后将客户端连接到 `ws://127.0.0.1:18789`。
- 在macOS上，优先使用应用的“通过SSH远程访问”模式，该模式会自动管理隧道。

## macOS应用“通过SSH远程访问”

macOS菜单栏应用可以端到端驱动相同设置（远程状态检查、WebChat和语音唤醒转发）。

操作手册：[macOS远程访问](/platforms/mac/remote)。

## 安全规则（远程/VPN）

简短版本：**保持网关仅回环接口**，除非您确定需要绑定。

- **回环接口 + SSH/Tailscale Serve** 是最安全的默认设置（无公网暴露）。
- **非回环接口绑定**（`lan`/`tailnet`/`custom`，或 `auto` 当回环不可用）必须使用认证令牌/密码。
- `gateway.remote.token` **仅** 用于远程CLI调用 — 它 **不** 启用本地认证。
- `gateway.remote.tlsFingerprint` 在使用 `wss://` 时固定远程TLS证书。
- **Tailscale Serve** 可以通过身份头进行认证，当 `gateway.auth.allowTailscale: true`。
  如果您想使用令牌/密码，请将其设为 `false`。
- 将浏览器控制视为操作员访问：仅尾网 + 故意节点配对。

深入阅读：[安全](/gateway/security)。