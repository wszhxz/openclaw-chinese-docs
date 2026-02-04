---
summary: "Node discovery and transports (Bonjour, Tailscale, SSH) for finding the gateway"
read_when:
  - Implementing or changing Bonjour discovery/advertising
  - Adjusting remote connection modes (direct vs SSH)
  - Designing node discovery + pairing for remote nodes
title: "Discovery and Transports"
---
# 发现与传输

OpenClaw 存在两个表面上看似相似的问题：

1. **操作员远程控制**：通过运行在其他位置的网关控制的 macOS 菜单栏应用程序。
2. **节点配对**：iOS/Android（以及未来的节点）查找网关并安全配对。

设计目标是将所有网络发现/广告保留在 **Node Gateway** (`openclaw gateway`) 中，并将客户端（mac 应用程序、iOS）作为消费者。

## 术语

- **网关**：一个单一的长期运行的网关进程，拥有状态（会话、配对、节点注册表）并运行通道。大多数设置每台主机使用一个；可能有隔离的多网关设置。
- **网关 WS（控制平面）**：默认情况下是 `127.0.0.1:18789` 上的 WebSocket 终点；可以通过 `gateway.bind` 绑定到局域网/尾网。
- **直接 WS 传输**：面向局域网/尾网的网关 WS 终点（无 SSH）。
- **SSH 传输（回退）**：通过转发 `127.0.0.1:18789` 进行远程控制。
- **旧版 TCP 桥接（已弃用/移除）**：旧版节点传输（参见 [桥接协议](/gateway/bridge-protocol)）；不再用于发现。

协议细节：

- [网关协议](/gateway/protocol)
- [桥接协议（旧版）](/gateway/bridge-protocol)

## 为什么我们同时保留“直接”和 SSH

- **直接 WS** 在同一网络和尾网中提供最佳用户体验：
  - 通过 Bonjour 自动发现局域网
  - 网关拥有的配对令牌 + ACL
  - 不需要 shell 访问；协议表面可以保持紧凑且可审计
- **SSH** 仍然是通用的回退方案：
  - 适用于任何你有 SSH 访问的地方（甚至跨不相关的网络）
  - 能够应对组播/mDNS 问题
  - 除了 SSH 之外不需要新的入站端口

## 发现输入（客户端如何知道网关的位置）

### 1) Bonjour / mDNS（仅限局域网）

Bonjour 是尽力而为的，不会跨越网络。它仅用于“同一局域网”的便利性。

目标方向：

- **网关** 通过 Bonjour 广告其 WS 终点。
- 客户端浏览并显示一个“选择网关”列表，然后存储所选的终点。

故障排除和信标详细信息：[Bonjour](/gateway/bonjour)。

#### 服务信标详细信息

- 服务类型：
  - `_openclaw-gw._tcp`（网关传输信标）
- TXT 键（非机密）：
  - `role=gateway`
  - `lanHost=<hostname>.local`
  - `sshPort=22`（或任何被广告的）
  - `gatewayPort=18789`（网关 WS + HTTP）
  - `gatewayTls=1`（仅当启用 TLS 时）
  - `gatewayTlsSha256=<sha256>`（仅当启用 TLS 且指纹可用时）
  - `canvasPort=18793`（默认画布主机端口；提供 `/__openclaw__/canvas/`）
  - `cliPath=<path>`（可选；可执行的 `openclaw` 入口点或二进制文件的绝对路径）
  - `tailnetDns=<magicdns>`（可选提示；当 Tailscale 可用时自动检测）

禁用/覆盖：

- `OPENCLAW_DISABLE_BONJOUR=1` 禁用广告。
- `gateway.bind` 在 `~/.openclaw/openclaw.json` 中控制网关绑定模式。
- `OPENCLAW_SSH_PORT` 覆盖 TXT 中广告的 SSH 端口（默认为 22）。
- `OPENCLAW_TAILNET_DNS` 发布一个 `tailnetDns` 提示（MagicDNS）。
- `OPENCLAW_CLI_PATH` 覆盖广告的 CLI 路径。

### 2) 尾网（跨网络）

对于伦敦/维也纳风格的设置，Bonjour 无法帮助。推荐的“直接”目标是：

- Tailscale 的 MagicDNS 名称（首选）或稳定的尾网 IP。

如果网关能够检测到它正在运行在 Tailscale 下，它会发布 `tailnetDns` 作为客户端（包括广域信标）的可选提示。

### 3) 手动 / SSH 目标

当没有直接路由（或直接被禁用）时，客户端始终可以通过 SSH 连接，通过转发环回网关端口。

参见 [远程访问](/gateway/remote)。

## 传输选择（客户端策略）

推荐的客户端行为：

1. 如果配置并可达的直接终点存在，则使用它。
2. 否则，如果 Bonjour 在局域网中找到网关，则提供一个一键“使用此网关”的选项并将其保存为直接终点。
3. 否则，如果配置了尾网 DNS/IP，则尝试直接连接。
4. 否则，回退到 SSH。

## 配对 + 认证（直接传输）

网关是节点/客户端准入的真相来源。

- 配对请求在网关中创建/批准/拒绝（参见 [网关配对](/gateway/pairing)）。
- 网关强制执行：
  - 认证（令牌 / 密钥对）
  - 范围/ACL（网关不是每个方法的原始代理）
  - 速率限制

## 按组件的责任

- **网关**：广告发现信标，拥有配对决策，并托管 WS 终点。
- **macOS 应用程序**：帮助你选择网关，显示配对提示，并仅作为回退使用 SSH。
- **iOS/Android 节点**：浏览 Bonjour 作为便利性，并连接到配对的网关 WS。