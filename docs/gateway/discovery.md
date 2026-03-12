---
summary: "Node discovery and transports (Bonjour, Tailscale, SSH) for finding the gateway"
read_when:
  - Implementing or changing Bonjour discovery/advertising
  - Adjusting remote connection modes (direct vs SSH)
  - Designing node discovery + pairing for remote nodes
title: "Discovery and Transports"
---
# 发现与传输

OpenClaw 存在两个表面上相似、但本质不同的问题：

1. **操作员远程控制**：macOS 菜单栏应用控制运行在其他位置的网关。
2. **节点配对**：iOS/Android（以及未来节点）发现网关并安全配对。

设计目标是将所有网络发现/广播功能保留在 **节点网关**（`openclaw gateway`）中，并使客户端（mac 应用、iOS）仅作为消费者。

## 术语

- **网关（Gateway）**：一个长期运行的单一网关进程，负责管理状态（会话、配对、节点注册表）并运行通道。大多数部署每台主机使用一个网关；隔离的多网关部署也是可行的。
- **网关 WebSocket（控制平面，Gateway WS）**：默认位于 `127.0.0.1:18789` 的 WebSocket 端点；可通过 `gateway.bind` 绑定到局域网（LAN）或 Tailscale 网络（tailnet）。
- **直连 WebSocket 传输（Direct WS transport）**：面向局域网/尾部网络（tailnet）的网关 WebSocket 端点（不经过 SSH）。
- **SSH 传输（回退方案，SSH transport）**：通过 SSH 转发 `127.0.0.1:18789` 实现远程控制。
- **传统 TCP 桥接（已弃用/移除，Legacy TCP bridge）**：旧版节点传输方式（参见 [桥接协议](/gateway/bridge-protocol)）；不再用于发现广播。

协议细节：

- [网关协议](/gateway/protocol)
- [桥接协议（旧版）](/gateway/bridge-protocol)

## 为何同时保留“直连”和 SSH 方案

- **直连 WebSocket** 在同一局域网及 Tailscale 网络内提供最佳用户体验：
  - 通过 Bonjour 在局域网内自动发现；
  - 配对令牌与访问控制列表（ACL）均由网关统一管理；
  - 无需 Shell 访问权限；协议面可保持精简且易于审计。
- **SSH** 仍是通用回退方案：
  - 只要有 SSH 访问权限即可工作（甚至跨越互不相关的网络）；
  - 不受组播/mDNS 故障影响；
  - 除 SSH 端口外，无需开放任何新的入站端口。

## 发现输入（客户端如何获知网关位置）

### 1）Bonjour / mDNS（仅限局域网）

Bonjour 是尽力而为型机制，无法跨网络。仅用于“同处一局域网”的便捷场景。

目标方向：

- **网关** 通过 Bonjour 广播其 WebSocket 端点；
- 客户端浏览并显示“选择一个网关”列表，然后保存所选端点。

排错与信标详情请参阅：[Bonjour](/gateway/bonjour)。

#### 服务信标详情

- 服务类型：
  - `_openclaw-gw._tcp`（网关传输信标）
- TXT 键（非密钥）：
  - `role=gateway`
  - `lanHost=<hostname>.local`
  - `sshPort=22`（或实际广播的任意值）
  - `gatewayPort=18789`（网关 WebSocket + HTTP）
  - `gatewayTls=1`（仅当启用 TLS 时）
  - `gatewayTlsSha256=<sha256>`（仅当启用 TLS 且指纹可用时）
  - `canvasPort=<port>`（Canvas 主机端口；当前在启用 Canvas 主机时与 `gatewayPort` 相同）
  - `cliPath=<path>`（可选；指向可执行的 `openclaw` 入口点或二进制文件的绝对路径）
  - `tailnetDns=<magicdns>`（可选提示；Tailscale 可用时自动检测）

安全说明：

- Bonjour/mDNS TXT 记录**未经身份验证**。客户端必须仅将 TXT 值视为用户界面提示。
- 路由（主机/端口）应优先采用**解析出的服务端点**（SRV + A/AAAA），而非 TXT 中提供的 `lanHost`、`tailnetDns` 或 `gatewayPort`。
- TLS 证书固定（pinning）绝不可允许广告中声明的 `gatewayTlsSha256` 覆盖先前已存储的 pin。
- iOS/Android 节点应将基于发现的直连视为**仅限 TLS**，并在首次存储 pin 前要求明确的“信任此指纹”确认（需带外验证）。

禁用/覆盖方式：

- `OPENCLAW_DISABLE_BONJOUR=1` 禁用广播。
- `gateway.bind` 在 `~/.openclaw/openclaw.json` 中控制网关绑定模式。
- `OPENCLAW_SSH_PORT` 覆盖 TXT 中广播的 SSH 端口（默认为 22）。
- `OPENCLAW_TAILNET_DNS` 发布一个 `tailnetDns` 提示（MagicDNS）。
- `OPENCLAW_CLI_PATH` 覆盖广播的 CLI 路径。

### 2）Tailnet（跨网络）

对于伦敦/维也纳式部署，Bonjour 将不起作用。推荐的“直连”目标为：

- Tailscale MagicDNS 名称（首选）或稳定的 tailnet IP 地址。

若网关能检测到自身正运行于 Tailscale 下，它将发布 `tailnetDns` 作为客户端（包括广域信标）的可选提示。

### 3）手动 / SSH 目标

当不存在直连路径（或直连已被禁用）时，客户端始终可通过 SSH 转发本地回环网关端口实现连接。

详见 [远程访问](/gateway/remote)。

## 传输方式选择（客户端策略）

推荐的客户端行为如下：

1. 若已配置且可达已配对的直连端点，则使用该端点；
2. 否则，若 Bonjour 在局域网中发现网关，则提供一键式“使用此网关”选项，并将其保存为直连端点；
3. 否则，若已配置 tailnet DNS/IP，则尝试直连；
4. 否则，回退至 SSH。

## 配对与认证（直连传输）

网关是节点/客户端准入的唯一权威来源。

- 配对请求的创建、批准与拒绝均在网关中完成（参见 [网关配对](/gateway/pairing)）；
- 网关强制执行以下策略：
  - 认证（令牌 / 密钥对）；
  - 权限范围/访问控制列表（ACL）（网关并非所有方法的原始代理）；
  - 速率限制。

## 各组件职责划分

- **网关**：广播发现信标、主导配对决策、托管 WebSocket 端点；
- **macOS 应用**：协助您选择网关、显示配对提示，并仅在必要时回退使用 SSH；
- **iOS/Android 节点**：将 Bonjour 浏览作为便利手段，并连接至已配对的网关 WebSocket。