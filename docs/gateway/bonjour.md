---
summary: "Bonjour/mDNS discovery + debugging (Gateway beacons, clients, and common failure modes)"
read_when:
  - Debugging Bonjour discovery issues on macOS/iOS
  - Changing mDNS service types, TXT records, or discovery UX
title: "Bonjour Discovery"
---
# Bonjour / mDNS 发现

OpenClaw 使用 Bonjour（mDNS / DNS‑SD）作为**仅限局域网的便捷功能**，用于发现正在运行的网关（WebSocket 端点）。该机制为尽力而为式实现，**不能替代** SSH 或基于 Tailnet 的连接。

## 通过 Tailscale 实现广域 Bonjour（单播 DNS‑SD）

如果节点与网关位于不同网络中，组播 mDNS 将无法跨越网络边界。您可通过切换至 **单播 DNS‑SD**（即“广域 Bonjour”）在 Tailscale 上保持相同的发现用户体验。

高层步骤如下：

1. 在网关主机上运行一个 DNS 服务器（需可通过 Tailnet 访问）。
2. 在专用区域下为 `_openclaw-gw._tcp` 发布 DNS‑SD 记录  
   （示例：`openclaw.internal.`）。
3. 配置 Tailscale 的**拆分 DNS（split DNS）**，使您的自定义域名对客户端（包括 iOS 设备）解析时指向该 DNS 服务器。

OpenClaw 支持任意发现域名；`openclaw.internal.` 仅为示例。iOS/Android 节点会同时浏览 `local.` 及您配置的广域域名。

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

此操作将安装 CoreDNS，并将其配置为：

- 仅在网关的 Tailscale 接口上监听端口 53；
- 从 `~/.openclaw/dns/<domain>.db` 为您的自定义域名（例如：`openclaw.internal.`）提供服务。

在已接入 tailnet 的机器上验证：

```bash
dns-sd -B _openclaw-gw._tcp openclaw.internal.
dig @<TAILNET_IPV4> -p 53 _openclaw-gw._tcp.openclaw.internal PTR +short
```

### Tailscale DNS 设置

在 Tailscale 管理控制台中：

- 添加一个名称服务器，指向网关的 tailnet IP 地址（UDP/TCP 53）；
- 添加拆分 DNS 规则，使您的发现域名通过该名称服务器解析。

一旦客户端接受 tailnet DNS，iOS 节点即可在您的发现域名下浏览  
`_openclaw-gw._tcp`，无需依赖组播。

### 网关监听器安全性（推荐）

网关 WebSocket 端口（默认为 `18789`）默认绑定到回环地址（loopback）。如需支持局域网或 tailnet 访问，请显式绑定，并保持身份验证启用。

对于仅使用 tailnet 的部署：

- 在 `~/.openclaw/openclaw.json` 中设置 `gateway.bind: "tailnet"`；
- 重启网关（或重启 macOS 菜单栏应用）。

## 广播内容说明

仅网关广播 `_openclaw-gw._tcp`。

## 服务类型

- `_openclaw-gw._tcp` — 网关传输信标（由 macOS/iOS/Android 节点使用）。

## TXT 键（非敏感提示信息）

网关广播少量非敏感提示信息，以提升 UI 流程体验：

- `role=gateway`
- `displayName=<friendly name>`
- `lanHost=<hostname>.local`
- `gatewayPort=<port>`（网关 WebSocket + HTTP）
- `gatewayTls=1`（仅当启用 TLS 时）
- `gatewayTlsSha256=<sha256>`（仅当启用 TLS 且可获取指纹时）
- `canvasPort=<port>`（仅当启用画布主机时；当前值与 `gatewayPort` 相同）
- `sshPort=<port>`（若未覆盖，则默认为 22）
- `transport=gateway`
- `cliPath=<path>`（可选；指向可执行的 `openclaw` 入口点的绝对路径）
- `tailnetDns=<magicdns>`（可选提示，当 Tailnet 可用时）

安全注意事项：

- Bonjour/mDNS TXT 记录是**未经认证的**。客户端不得将 TXT 内容视为权威路由依据。
- 客户端应依据解析出的服务端点（SRV + A/AAAA）进行路由。请仅将 `lanHost`、`tailnetDns`、`gatewayPort` 和 `gatewayTlsSha256` 视为提示信息。
- TLS 证书固定（pinning）绝不可允许广告中提供的 `gatewayTlsSha256` 覆盖先前存储的 pin。
- iOS/Android 节点应将基于发现的直连视为**仅限 TLS** 连接，并在信任首次出现的证书指纹前，要求用户明确确认。

## 在 macOS 上调试

可用的内置工具：

- 浏览实例：

  ```bash
  dns-sd -B _openclaw-gw._tcp local.
  ```

- 解析单个实例（替换 `<instance>`）：

  ```bash
  dns-sd -L "<instance>" _openclaw-gw._tcp local.
  ```

若浏览成功但解析失败，通常表明存在局域网策略限制或 mDNS 解析器问题。

## 在网关日志中调试

网关会写入一个滚动日志文件（启动时打印为  
`gateway log file: ...`）。请查找含 `bonjour:` 的日志行，尤其是：

- `bonjour: advertise failed ...`
- `bonjour: ... name conflict resolved` / `hostname conflict resolved`
- `bonjour: watchdog detected non-announced service ...`

## 在 iOS 节点上调试

iOS 节点使用 `NWBrowser` 发现 `_openclaw-gw._tcp`。

捕获日志方法：

- 设置 → 网关 → 高级 → **发现调试日志**
- 设置 → 网关 → 高级 → **发现日志** → 复现问题 → **复制**

日志包含浏览器状态转换及结果集变更信息。

## 常见故障模式

- **Bonjour 无法跨网络工作**：请改用 Tailnet 或 SSH。
- **组播被阻止**：部分 Wi‑Fi 网络禁用了 mDNS。
- **休眠 / 接口频繁变动**：macOS 可能临时丢弃 mDNS 结果；请重试。
- **浏览成功但解析失败**：请保持机器名简洁（避免使用表情符号或标点符号），然后重启网关。服务实例名源自主机名，过于复杂的名称可能令某些解析器混淆。

## 已转义的实例名称（`\032`）

Bonjour/DNS‑SD 常将服务实例名称中的字节转义为十进制 `\DDD` 序列（例如空格变为 `\032`）。

- 此为协议层面的正常行为；
- UI 应解码后显示（iOS 使用 `BonjourEscapes.decode`）。

## 禁用 / 配置方式

- `OPENCLAW_DISABLE_BONJOUR=1` 可禁用广播（旧版：`OPENCLAW_DISABLE_BONJOUR`）；
- `gateway.bind` 在 `~/.openclaw/openclaw.json` 中控制网关绑定模式；
- `OPENCLAW_SSH_PORT` 可覆盖 TXT 中广播的 SSH 端口（旧版：`OPENCLAW_SSH_PORT`）；
- `OPENCLAW_TAILNET_DNS` 可在 TXT 中发布 MagicDNS 提示（旧版：`OPENCLAW_TAILNET_DNS`）；
- `OPENCLAW_CLI_PATH` 可覆盖广播的 CLI 路径（旧版：`OPENCLAW_CLI_PATH`）。

## 相关文档

- 发现策略与传输选择：[Discovery](/gateway/discovery)  
- 节点配对与审批：[Gateway pairing](/gateway/pairing)