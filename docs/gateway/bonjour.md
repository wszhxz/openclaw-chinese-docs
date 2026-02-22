---
summary: "Bonjour/mDNS discovery + debugging (Gateway beacons, clients, and common failure modes)"
read_when:
  - Debugging Bonjour discovery issues on macOS/iOS
  - Changing mDNS service types, TXT records, or discovery UX
title: "Bonjour Discovery"
---
# Bonjour / mDNS 发现

OpenClaw 使用 Bonjour (mDNS / DNS‑SD) 作为 **仅限局域网的便捷方式** 来发现活动网关（WebSocket 终点）。这是一种尽力而为的方法，并**不**替代 SSH 或 Tailnet 基础的连接。

## 跨区域 Bonjour（单播 DNS‑SD）通过 Tailscale

如果节点和网关位于不同的网络中，组播 mDNS 将无法跨越边界。您可以通过切换到 **单播 DNS‑SD**（“跨区域 Bonjour”）通过 Tailscale 来保持相同的发现用户体验。

高层次步骤：

1. 在网关主机上运行一个 DNS 服务器（可通过 Tailnet 访问）。
2. 在专用区域下发布 `_openclaw-gw._tcp` 的 DNS‑SD 记录（示例：`openclaw.internal.`）。
3. 配置 Tailscale **拆分 DNS**，使选定的域名通过该 DNS 服务器解析客户端（包括 iOS）的请求。

OpenClaw 支持任何发现域名；`openclaw.internal.` 只是一个示例。
iOS/Android 节点会浏览 `local.` 和您配置的跨区域域名。

### 网关配置（推荐）

```json5
{
  gateway: { bind: "tailnet" }, // tailnet-only (recommended)
  discovery: { wideArea: { enabled: true } }, // enables wide-area DNS-SD publishing
}
```

### 一次性 DNS 服务器设置（网关主机）

```bash
openclaw dns setup --apply
```

这将安装 CoreDNS 并配置它以：

- 仅在网关的 Tailscale 接口上监听端口 53
- 从 `~/.openclaw/dns/<domain>.db` 提供您选择的域名（示例：`openclaw.internal.`）

从 Tailnet 连接的机器验证：

```bash
dns-sd -B _openclaw-gw._tcp openclaw.internal.
dig @<TAILNET_IPV4> -p 53 _openclaw-gw._tcp.openclaw.internal PTR +short
```

### Tailscale DNS 设置

在 Tailscale 管理控制台中：

- 添加一个指向网关 Tailnet IP 的名称服务器（UDP/TCP 53）。
- 添加拆分 DNS，使您的发现域名使用该名称服务器。

一旦客户端接受 Tailnet DNS，iOS 节点可以在您的发现域名中浏览 `_openclaw-gw._tcp` 而无需组播。

### 网关监听器安全（推荐）

默认情况下，网关 WS 端口（默认 `18789`）绑定到回环地址。为了局域网/Tailnet 访问，请显式绑定并保持身份验证启用。

对于仅 Tailnet 设置：

- 在 `~/.openclaw/openclaw.json` 中设置 `gateway.bind: "tailnet"`。
- 重启网关（或重启 macOS 菜单栏应用程序）。

## 广告来源

只有网关会广告 `_openclaw-gw._tcp`。

## 服务类型

- `_openclaw-gw._tcp` — 网关传输信标（由 macOS/iOS/Android 节点使用）。

## TXT 键（非机密提示）

网关会广告一些小的非机密提示，以使用户界面流程更方便：

- `role=gateway`
- `displayName=<friendly name>`
- `lanHost=<hostname>.local`
- `gatewayPort=<port>`（网关 WS + HTTP）
- `gatewayTls=1`（仅当启用 TLS 时）
- `gatewayTlsSha256=<sha256>`（仅当启用 TLS 且指纹可用时）
- `canvasPort=<port>`（仅当启用画布主机时；目前与 `gatewayPort` 相同）
- `sshPort=<port>`（默认为 22，除非被覆盖）
- `transport=gateway`
- `cliPath=<path>`（可选；可执行 `openclaw` 入口点的绝对路径）
- `tailnetDns=<magicdns>`（仅当 Tailnet 可用时的可选提示）

安全注意事项：

- Bonjour/mDNS TXT 记录是**未经过身份验证的**。客户端不应将 TXT 视为权威路由。
- 客户端应使用解析的服务端点（SRV + A/AAAA）进行路由。将 `lanHost`、`tailnetDns`、`gatewayPort` 和 `gatewayTlsSha256` 视为提示。
- TLS 锚定绝不能允许广告的 `gatewayTlsSha256` 覆盖先前存储的锚定。
- iOS/Android 节点应将基于发现的直接连接视为**仅 TLS**，并在信任首次指纹之前需要明确的用户确认。

## macOS 上的调试

有用的内置工具：

- 浏览实例：

  ```bash
  dns-sd -B _openclaw-gw._tcp local.
  ```

- 解析一个实例（替换 `<instance>`）：

  ```bash
  dns-sd -L "<instance>" _openclaw-gw._tcp local.
  ```

如果浏览正常但解析失败，通常是遇到了局域网策略或 mDNS 解析器问题。

## 网关日志中的调试

网关写入一个滚动日志文件（启动时打印为 `gateway log file: ...`）。查找 `bonjour:` 行，特别是：

- `bonjour: advertise failed ...`
- `bonjour: ... name conflict resolved` / `hostname conflict resolved`
- `bonjour: watchdog detected non-announced service ...`

## iOS 节点上的调试

iOS 节点使用 `NWBrowser` 来发现 `_openclaw-gw._tcp`。

要捕获日志：

- 设置 → 网关 → 高级 → **发现调试日志**
- 设置 → 网关 → 高级 → **发现日志** → 复现 → **复制**

日志包括浏览器状态转换和结果集变化。

## 常见故障模式

- **Bonjour 不跨越网络**：使用 Tailnet 或 SSH。
- **组播被阻止**：某些 Wi‑Fi 网络禁用 mDNS。
- **睡眠 / 接口变化**：macOS 可能会临时丢弃 mDNS 结果；重试。
- **浏览正常但解析失败**：保持机器名称简单（避免表情符号或标点符号），然后重启网关。服务实例名称派生自主机名，因此过于复杂的名称可能会让某些解析器感到困惑。

## 转义实例名称 (`\032`)

Bonjour/DNS‑SD 通常将服务实例名称中的字节转义为十进制 `\DDD` 序列（例如空格变为 `\032`）。

- 这在协议级别是正常的。
- 用户界面应解码以显示（iOS 使用 `BonjourEscapes.decode`）。

## 禁用 / 配置

- `OPENCLAW_DISABLE_BONJOUR=1` 禁用广告（旧版：`OPENCLAW_DISABLE_BONJOUR`）。
- `gateway.bind` 在 `~/.openclaw/openclaw.json` 中控制网关绑定模式。
- `OPENCLAW_SSH_PORT` 覆盖 TXT 中广告的 SSH 端口（旧版：`OPENCLAW_SSH_PORT`）。
- `OPENCLAW_TAILNET_DNS` 在 TXT 中发布 MagicDNS 提示（旧版：`OPENCLAW_TAILNET_DNS`）。
- `OPENCLAW_CLI_PATH` 覆盖广告的 CLI 路径（旧版：`OPENCLAW_CLI_PATH`）。

## 相关文档

- 发现策略和传输选择：[Discovery](/gateway/discovery)
- 节点配对 + 批准：[Gateway pairing](/gateway/pairing)