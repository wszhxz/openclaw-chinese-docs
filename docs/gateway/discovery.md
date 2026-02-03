---
summary: "Node discovery and transports (Bonjour, Tailscale, SSH) for finding the gateway"
read_when:
  - Implementing or changing Bonjour discovery/advertising
  - Adjusting remote connection modes (direct vs SSH)
  - Designing node discovery + pairing for remote nodes
title: "Discovery and Transports"
---
为什么<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context and the key terms. The document is about OpenClaw's discovery and transport mechanisms, so I need to make sure the technical terms are accurately translated.

First, the title "Discovery & transports" becomes "发现与传输". Then, the introduction mentions two distinct problems. The first is "Operator remote control" which translates to "操作员远程控制". The second is "Node pairing" which is "节点配对". 

Looking at the design goal section, "keep all network discovery/advertising in the Node Gateway" should be "将所有网络发现/广告功能保留在节点网关中". The term "Node Gateway" is a specific term, so I'll keep it as "节点网关" in Chinese. 

The Terms section has several definitions. "Gateway" is translated as "网关", and I need to ensure that the explanations are clear. For example, "a single long-running gateway process" becomes "一个长期运行的网关进程". 

The section about "Gateway WS (control plane)" mentions the default WebSocket endpoint. I'll translate "WebSocket endpoint" as "WebSocket端点" and note the port number. The term "control plane" is "控制平面", so the full term is "网关控制平面 (控制平面)".

The "Direct WS transport" and "SSH transport (fallback)" need precise translation. "Direct WS transport" becomes "直接WS传输", and "SSH transport (fallback)" is "SSH传输 (备用)". 

In the section explaining why both direct and SSH are kept, I need to ensure that the technical terms like "protocol surface" are translated accurately. "Protocol surface" could be "协议接口" or "协议表面积", but I'll check for consistency. 

The Discovery inputs section has different methods like Bonjour/mDNS and Tailnet. "Bonjour / mDNS (LAN only)" translates to "Bonjour / mDNS (仅限局域网)". I need to make sure that the terms like "TXT keys" are correctly translated as "TXT键".

For the Service beacon details, terms like "service types" become "服务类型", and "TXT keys (non-secret)" as "TXT键 (非秘密)". The specific keys like "role=gateway" should remain as they are, but the labels need to be in Chinese. 

In the section about Tailnet (cross-network), "Tailscale MagicDNS name" is "Tailscale MagicDNS名称", and "stable tailnet IP" is "稳定的尾网IP地址". 

The Manual / SSH target section mentions "loopback gateway port" which is "环回网关端口". 

Transport selection (client policy) has a recommended client behavior. I'll translate the steps into clear instructions, ensuring that terms like "paired direct endpoint" are accurately translated as "已配对的直接端点".

Pairing + auth (direct transport) section needs to clarify that the gateway is the source of truth. Terms like "pairing requests" become "配对请求", and "scopes/ACLs" as "作用域/ACL".

Responsibilities by component section lists the roles of each component. "macOS app" is "macOS应用", and "iOS/Android nodes" as "iOS/Android节点". 

Throughout the translation, I'll maintain technical accuracy while ensuring the text flows naturally in Chinese. I'll also check for consistency in terminology and ensure that all specific terms are correctly translated without losing their original meaning. Finally, I'll review the entire translation to make sure there are no errors and that the structure matches the original document.
</think>

# 发现与传输

OpenClaw 有两个看似相似但本质不同的问题：

1. **操作员远程控制**：通过 macOS 状态栏应用控制运行在其他位置的网关。
2. **节点配对**：iOS/Android（及未来节点）寻找网关并安全配对。

设计目标是将所有网络发现/广告功能保留在 **节点网关**（`openclaw gateway`）中，并保持客户端（mac 应用、iOS）作为消费者。

## 术语

- **网关**：一个长期运行的网关进程，拥有状态（会话、配对、节点注册表）并运行通道。大多数配置使用每个主机一个；隔离的多网关配置也是可能的。
- **网关 WS（控制平面）**：默认在 `127.0.0.1:18789` 上的 WebSocket 端点；可通过 `gateway.bind` 绑定到 LAN/tailnet。
- **直接 WS 传输**：面向 LAN/tailnet 的网关 WS 端点（不通过 SSH）。
- **SSH 传输（备用）**：通过 SSH 转发 `127.0.0.1:18789` 实现远程控制。
- **旧 TCP 桥接（已弃用/移除）**：旧的节点传输方式（参见 [桥接协议](/gateway/bridge-protocol)）；不再用于发现。

协议细节：

- [网关协议](/gateway/protocol)
- [桥接协议（旧版）](/gateway/bridge-protocol)

## 为何同时保留“直接”和 SSH

- **直接 WS** 是在相同网络和 tailnet 中的最佳用户体验：
  - 通过 Bonjour 实现 LAN 内的自动发现
  - 配对令牌 + ACL 由网关拥有
  - 不需要 shell 访问；协议接口可以保持紧凑且可审计
- **SSH** 仍然是通用的备用方案：
  - 在任何有 SSH 访问权限的地方均可使用（甚至跨无关网络）
  - 可抵御多播/mDNS 问题
  - 除了 SSH 外无需新增入站端口

## 发现输入（客户端如何了解网关位置）

### 1) Bonjour / mDNS（仅限局域网）

Bonjour 是尽力而为的，无法跨网络。它仅用于“同一局域网”的便捷性。

目标方向：

- **网关** 通过 Bonjour 广告其 WS 端点。
- 客户端浏览并显示“选择网关”列表，然后存储所选端点。

故障排查和信标详情：[Bonjour](/gateway/bonjour)。

#### 服务信标详情

- 服务类型：
  - `_openclaw-gw._tcp`（网关传输信标）
- TXT 键（非秘密）：
  - `role=gateway`
  - `lanHost=<hostname>.local`
  - `sshPort=22`（或广告的任意端口）
  - `gatewayPort=18789`（网关 WS + HTTP）
  - `gatewayTls=1`（仅在 TLS 启用时）
  - `gatewayTlsSha256=<sha256>`（仅在 TLS 启用且指纹可用时）
  - `canvasPort=18793`（默认画布主机端口；提供 `/__openclaw__/canvas/`）
  - `cliPath=<path>`（可选；指向可运行的 `openclaw` 入口点或二进制文件的绝对路径）
  - `tailnetDns=<magicdns>`（可选提示；当 Tailscale 可用时自动检测）

禁用/覆盖：

- `OPENCLAW_DISABLE_BONJOUR=1` 禁用广告。
- `~/.openclaw/openclaw.json` 中的 `gateway.bind` 控制网关绑定模式。
- `OPENCLAW_SSH_PORT` 覆盖 TXT 中广告的 SSH 端口（默认为 22）。
- `OPENCLAW_TAILNET_DNS` 发布 `tailnetDns` 提示（MagicDNS）。
- `OPENCLAW_CLI_PATH` 覆盖广告的 CLI 路径。

### 2) Tailnet（跨网络）

对于伦敦/维也纳风格的配置，Bonjour 无法帮助。推荐的“直接”目标是：

- Tailscale MagicDNS 名称（首选）或稳定的 tailnet IP 地址。

如果网关能检测到其在 Tailscale 下运行，它会将 `tailnetDns` 作为可选提示发布给客户端（包括广域信标）。

### 3) 手动 / SSH 目标

当没有直接路由（或直接路由被禁用）时，客户端始终可以通过 SSH 转发环回网关端口进行连接。

参见 [远程访问](/gateway/remote)。

## 传输选择（客户端策略）

推荐的客户端行为：

1. 如果已配置且可达的已配对直接端点，使用它。
2. 否则，如果 Bonjour 在 LAN 上找到网关，提供“使用此网关”的一键选择并将其保存为直接端点。
3. 否则，如果配置了 tailnet DNS/IP，尝试直接连接。
4. 否则，回退到 SSH。

## 配对 + 认证（直接传输）

网关是节点/客户端准入的权威来源。

- 配对请求在网关中创建/批准/拒绝（参见 [网关配对](/gateway/pairing)）。
- 网关强制执行：
  - 认证（令牌 / 密钥对）
  - 作用域/ACL（网关不是所有方法的原始代理）