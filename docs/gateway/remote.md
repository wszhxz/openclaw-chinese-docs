---
summary: "Remote access using SSH tunnels (Gateway WS) and tailnets"
read_when:
  - Running or troubleshooting remote gateway setups
title: "Remote Access"
---
# 远程访问 (SSH, 隧道和尾网)

此仓库通过在专用主机（桌面/服务器）上运行单个网关（主节点）并连接客户端到它来支持“通过 SSH 的远程访问”。

- 对于 **操作员（您/ macOS 应用程序）**：SSH 隧道是通用的回退方案。
- 对于 **节点（iOS/Android 和未来设备）**：连接到网关 **WebSocket**（根据需要使用 LAN/尾网或 SSH 隧道）。

## 核心理念

- 网关 WebSocket 绑定到您配置的端口上的 **回环** 地址（默认为 18789）。
- 用于远程访问时，您可以通过 SSH 转发该回环端口（或使用尾网/VPN 并减少隧道使用）。

## 常见的 VPN/尾网设置（代理的位置）

将 **网关主机** 视为“代理的位置”。它拥有会话、身份验证配置文件、通道和状态。
您的笔记本电脑/桌面（以及节点）连接到该主机。

### 1) 尾网中的始终在线网关（VPS 或家庭服务器）

在持久化主机上运行网关并通过 **Tailscale** 或 SSH 访问它。

- **最佳用户体验**：保留 `gateway.bind: "loopback"` 并使用 **Tailscale Serve** 作为控制界面。
- **回退方案**：保留回环地址并通过任何需要访问的机器进行 SSH 隧道。
- **示例**：[exe.dev](/platforms/exe-dev)（易于使用的虚拟机）或 [Hetzner](/platforms/hetzner)（生产 VPS）。

当您的笔记本电脑经常休眠但希望代理始终保持在线时，这是理想的选择。

### 2) 家庭桌面运行网关，笔记本电脑为远程控制

笔记本电脑 **不** 运行代理。它远程连接：

- 使用 macOS 应用程序的 **通过 SSH 的远程访问** 模式（设置 → 常规 → “OpenClaw 运行”）。
- 应用程序打开并管理隧道，因此 WebChat 和健康检查“正常工作”。

操作指南：[macOS 远程访问](/platforms/mac/remote)。

### 3) 笔记本电脑运行网关，其他机器远程访问

保持网关本地但安全地暴露它：

- 从其他机器通过 SSH 隧道到笔记本电脑，或
- 通过 Tailscale Serve 提供控制界面并保持网关仅限回环地址。

指南：[Tailscale](/gateway/tailscale) 和 [Web 概述](/web)。

## 命令流（什么在哪里运行）

一个网关服务拥有状态和通道。节点是外设。

流示例（Telegram → 节点）：

- Telegram 消息到达 **网关**。
- 网关运行 **代理** 并决定是否调用节点工具。
- 网关通过网关 WebSocket (`node.*` RPC) 调用 **节点**。
- 节点返回结果；网关通过 Telegram 回复。

注意：

- **节点不运行网关服务**。除非有意运行隔离配置文件（参见 [多个网关](/gateway/multiple-gateways)），否则每个主机应只运行一个网关。
- macOS 应用程序的“节点模式”只是通过网关 WebSocket 的节点客户端。

## SSH 隧道（CLI + 工具）

创建到远程网关 WS 的本地隧道：

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

建立隧道后：

- `openclaw health` 和 `openclaw status --deep` 现在通过 `ws://127.0.0.1:18789` 访问远程网关。
- 根据需要，`openclaw gateway {status,health,send,agent,call}` 也可以通过 `--url` 目标转发的 URL。

注意：将 `18789` 替换为您的配置的 `gateway.port`（或 `--port`/`OPENCLAW_GATEWAY_PORT`）。
注意：当您传递 `--url` 时，CLI 不会回退到配置或环境凭据。
显式包含 `--token` 或 `--password`。缺少显式凭据是错误。

## CLI 远程默认值

您可以持久化远程目标，使 CLI 命令默认使用它：

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

当网关仅限回环地址时，保持 URL 为 `ws://127.0.0.1:18789` 并首先打开 SSH 隧道。

## 通过 SSH 的聊天界面

WebChat 不再使用单独的 HTTP 端口。SwiftUI 聊天界面直接连接到网关 WebSocket。

- 通过 SSH 转发 `18789`（参见上述内容），然后将客户端连接到 `ws://127.0.0.1:18789`。
- 在 macOS 上，优先使用应用程序的“通过 SSH 的远程访问”模式，该模式会自动管理隧道。

## macOS 应用程序“通过 SSH 的远程访问”

macOS 菜单栏应用程序可以端到端驱动相同的设置（远程状态检查、WebChat 和语音唤醒转发）。

操作指南：[macOS 远程访问](/platforms/mac/remote)。

## 安全规则（远程/VPN）

简而言之：**除非确定需要绑定，否则保持网关仅限回环地址**。

- **回环 + SSH/Tailscale Serve** 是最安全的默认设置（无公共暴露）。
- **非回环绑定** (`lan`/`tailnet`/`custom`，或当回环不可用时使用 `auto`) 必须使用认证令牌/密码。
- `gateway.remote.token` **仅** 用于远程 CLI 调用 — 它 **不** 启用本地认证。
- `gateway.remote.tlsFingerprint` 在使用 `wss://` 时固定远程 TLS 证书。
- 当 `gateway.auth.allowTailscale: true` 时，**Tailscale Serve** 可以通过身份头进行认证。
  如果您希望使用令牌/密码，请将其设置为 `false`。
- 将浏览器控制视为操作员访问：仅限尾网 + 故意的节点配对。

深入探讨：[安全性](/gateway/security)。