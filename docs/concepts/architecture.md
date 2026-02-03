---
summary: "WebSocket gateway architecture, components, and client flows"
read_when:
  - Working on gateway protocol, clients, or transports
title: "Gateway Architecture"
---
# 网关架构

最后更新：2026-01-22

## 概述

- 一个**网关**长期运行，拥有所有消息接口（通过Baileys的WhatsApp、通过grammY的Telegram、Slack、Discord、Signal、iMessage、WebChat）。
- 控制平面客户端（macOS应用、CLI、Web UI、自动化工具）通过**WebSocket**连接到网关，连接地址为配置的绑定主机（默认`127.0.0.1:18789`）。
- **节点**（macOS/iOS/Android/无头模式）也通过**WebSocket**连接，但声明`role: node`并显式指定权限/命令。
- 每个主机一个网关；它是唯一开启WhatsApp会话的地方。
- **画布主机**（默认`18793`）提供可编辑的HTML和A2UI。

## 组件和流程

### 网关（守护进程）

- 维护提供者连接。
- 暴露类型化的WS API（请求、响应、服务器推送事件）。
- 验证入站帧是否符合JSON Schema。
- 触发事件如`agent`、`chat`、`presence`、`health`、`heartbeat`、`cron`。

### 客户端（mac应用 / CLI / Web管理）

- 每个客户端一个WS连接。
- 发送请求（`health`、`status`、`send`、`agent`、`system-presence`）。
- 订阅事件（`tick`、`agent`、`presence`、`shutdown`）。

### 节点（macOS / iOS / Android / 无头模式）

- 通过**同一WS服务器**连接，使用`role: node`。
- 在`connect`中提供设备身份；配对是**基于设备**（角色`node`）的，批准存储在设备配对存储中。
- 暴露命令如`canvas.*`、`camera.*`、`screen.record`、`location.get`。

协议细节：

- [网关协议](/gateway/protocol)

### WebChat

- 静态UI，通过网关WS API用于聊天历史和发送。
- 在远程设置中，通过与其它客户端相同的SSH/Tailscale隧道连接。

## 连接生命周期（单个客户端）

```
客户端                    网关
  |                          |
  |---- req:connect -------->|
  |<------ res (ok) ---------|   （或 res error + close）
  |   （payload=hello-ok 包含快照：presence + health）
  |                          |
  |<------ event:presence ---|
  |<------ event:tick -------|
  |                          |
  |------- req:agent ------->|
  |<------ res:agent --------|   （ack: {runId,status:"accepted"}）
  |<------ event:agent ------|   （流式传输）
  |<------ res:None --------|   （最终: {runId,status,summary}）
  |                          |
```

## 通信协议（摘要）

- 传输：WebSocket，文本帧带有JSON负载。
- 首帧**必须**为`connect`。
- 握手后：
  - 请求：`{type:"req", id, method, params}` → `{type:"res", id, ok, payload|error}`
  - 事件：`{type:"event", event, payload, seq?, stateVersion?}`
- 如果设置了`OPENCLAW_GATEWAY_TOKEN`（或`--token`），`connect.params.auth.token`必须匹配，否则连接关闭。
- 对具有副作用的方法（如`send`、`agent`）需要使用幂等性键以安全重试；服务器维护一个短生命周期的去重缓存。
- 节点必须在`connect`中包含`role: "node"`以及caps/commands/权限。

## 配对 + 本地信任

- 所有WS客户端（操作员 + 节点）在`connect`时包含**设备身份**。
- 新设备ID需要配对批准；网关为后续连接颁发**设备令牌**。
- **本地**连接（环回或网关主机自身的tailnet地址）可自动批准以保持同主机用户体验流畅。
- **非本地**连接必须签署`connect.challenge`随机数并需要显式批准。
- 网关认证（`gateway.auth.*`）仍适用于**所有**连接，无论本地或远程。

详情：[网关协议](/gateway/protocol)，[配对](/start/pairing)，[安全](/gateway/security)。

## 协议类型和代码生成

- TypeBox schema定义协议。
- JSON Schema由这些schema生成。
- Swift模型由JSON Schema生成。

## 远程访问

- 推荐：Tailscale或VPN。
- 替代方案：SSH隧道
  ```bash
  ssh -N -L 18789:127.0.0.1:18789 user@host
  ```
- 通过隧道同样适用相同的握手 + 认证令牌。
- 在远程设置中可启用TLS + 可选的固定。

## 操作快照

- 启动：`openclaw gateway`（前台运行，日志输出到stdout）。
- 健康检查：通过WS发送`health`（也包含在`hello-ok`中）。
- 监督：使用launchd/systemd实现自动重启。

## 不变性

- 每个主机由**恰好一个**网关控制单个Baileys会话。
- 握手是强制性的；任何非JSON或非`connect`的首帧将导致强制关闭。
- 事件不会重播；客户端在间隙时需刷新。