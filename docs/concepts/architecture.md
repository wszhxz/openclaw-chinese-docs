---
summary: "WebSocket gateway architecture, components, and client flows"
read_when:
  - Working on gateway protocol, clients, or transports
title: "Gateway Architecture"
---
# 网关架构

最后更新时间：2026-01-22

## 概述

- 单个长期运行的 **Gateway** 拥有所有消息接口（通过 Baileys 的 WhatsApp、通过 grammY 的 Telegram、Slack、Discord、Signal、iMessage、WebChat）。
- 控制平面客户端（macOS 应用、CLI、Web UI、自动化）通过 **WebSocket** 连接到配置的绑定主机上的网关（默认 `127.0.0.1:18789`）。
- **节点**（macOS/iOS/Android/无头模式）也通过 **WebSocket** 连接，但会声明 `role: node` 并明确指定功能/命令。
- 每个主机一个 Gateway；它是唯一打开 WhatsApp 会话的地方。
- **画布主机**（默认 `18793`）提供代理可编辑的 HTML 和 A2UI。

## 组件和流程

### 网关（守护进程）

- 维护提供商连接。
- 暴露类型化的 WS API（请求、响应、服务器推送事件）。
- 验证传入帧是否符合 JSON Schema。
- 发出事件如 `agent`，`chat`，`presence`，`health`，`heartbeat`，`cron`。

### 客户端（mac 应用 / CLI / Web 管理）

- 每个客户端一个 WS 连接。
- 发送请求 (`health`，`status`，`send`，`agent`，`system-presence`)。
- 订阅事件 (`tick`，`agent`，`presence`，`shutdown`)。

### 节点（macOS / iOS / Android / 无头模式）

- 使用 `role: node` 连接到 **相同的 WS 服务器**。
- 在 `connect` 提供设备身份；配对是 **基于设备** 的（角色 `node`），批准信息存储在设备配对存储中。
- 暴露命令如 `canvas.*`，`camera.*`，`screen.record`，`location.get`。

协议细节：

- [网关协议](/gateway/protocol)

### WebChat

- 静态 UI 使用网关 WS API 获取聊天历史并发送消息。
- 在远程设置中，通过与其他客户端相同的 SSH/Tailscale 隧道连接。

## 连接生命周期（单个客户端）

```
Client                    Gateway
  |                          |
  |---- req:connect -------->|
  |<------ res (ok) ---------|   (or res error + close)
  |   (payload=hello-ok carries snapshot: presence + health)
  |                          |
  |<------ event:presence ---|
  |<------ event:tick -------|
  |                          |
  |------- req:agent ------->|
  |<------ res:agent --------|   (ack: {runId,status:"accepted"})
  |<------ event:agent ------|   (streaming)
  |<------ res:agent --------|   (final: {runId,status,summary})
  |                          |
```

## 传输协议（概要）

- 传输：WebSocket，带有 JSON 有效负载的文本帧。
- 第一帧 **必须** 是 `connect`。
- 握手后：
  - 请求：`{type:"req", id, method, params}` → `{type:"res", id, ok, payload|error}`
  - 事件：`{type:"event", event, payload, seq?, stateVersion?}`
- 如果设置了 `OPENCLAW_GATEWAY_TOKEN`（或 `--token`），则 `connect.params.auth.token`
  必须匹配，否则套接字关闭。
- 对于具有副作用的方法（`send`，`agent`），需要幂等键以安全重试；服务器维护一个短暂的去重缓存。
- 节点必须包含 `role: "node"` 加上 `connect` 中的功能/命令/权限。

## 配对 + 本地信任

- 所有 WS 客户端（操作员 + 节点）在 `connect` 包含一个 **设备身份**。
- 新设备 ID 需要配对批准；网关会为后续连接颁发 **设备令牌**。
- **本地** 连接（回环或网关主机自身的尾网地址）可以自动批准以保持同一主机的用户体验流畅。
- **非本地** 连接必须签署 `connect.challenge` 随机数，并需要显式批准。
- 网关认证 (`gateway.auth.*`) 仍然适用于 **所有** 连接，无论是本地还是远程。

详情：[网关协议](/gateway/protocol)，[配对](/start/pairing)，[安全性](/gateway/security)。

## 协议类型化和代码生成

- TypeBox 模式定义协议。
- 从这些模式生成 JSON Schema。
- 从 JSON Schema 生成 Swift 模型。

## 远程访问

- 推荐：Tailscale 或 VPN。
- 备选：SSH 隧道
  ```bash
  ssh -N -L 18789:127.0.0.1:18789 user@host
  ```
- 隧道中使用相同的握手 + 认证令牌。
- 在远程设置中可以启用 WS 的 TLS + 可选的证书固定。

## 运营快照

- 启动：`openclaw gateway`（前台，日志输出到 stdout）。
- 健康检查：通过 WS 的 `health`（也包含在 `hello-ok` 中）。
- 监督：使用 launchd/systemd 自动重启。

## 不变量

- 每个主机由一个且仅一个 Gateway 控制单个 Baileys 会话。
- 握手是强制性的；任何非 JSON 或非连接的第一个帧都会导致硬关闭。
- 事件不会重播；客户端必须在断层时刷新。