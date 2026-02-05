---
summary: "WebSocket gateway architecture, components, and client flows"
read_when:
  - Working on gateway protocol, clients, or transports
title: "Gateway Architecture"
---
# 网关架构

最后更新：2026-01-22

## 概述

- 单个长期运行的**网关**拥有所有消息传递界面（通过Baileys的WhatsApp，
  通过grammY的Telegram，Slack，Discord，Signal，iMessage，WebChat）。
- 控制平面客户端（macOS应用，CLI，网页界面，自动化工具）通过**WebSocket**连接到
  配置的绑定主机上的网关（默认为`127.0.0.1:18789`）。
- **节点**（macOS/iOS/Android/无头模式）也通过**WebSocket**连接，但
  使用明确的caps/commands声明`role: node`。
- 每台主机一个网关；这是唯一打开WhatsApp会话的地方。
- **画布主机**（默认为`18793`）提供代理可编辑的HTML和A2UI。

## 组件和流程

### 网关（守护进程）

- 维护提供商连接。
- 暴露类型化的WS API（请求，响应，服务器推送事件）。
- 根据JSON Schema验证传入帧。
- 发出诸如`agent`、`chat`、`presence`、`health`、`heartbeat`、`cron`等事件。

### 客户端（mac应用/CLI/网页管理）

- 每个客户端一个WS连接。
- 发送请求（`health`、`status`、`send`、`agent`、`system-presence`）。
- 订阅事件（`tick`、`agent`、`presence`、`shutdown`）。

### 节点（macOS/iOS/Android/无头模式）

- 使用`role: node`连接到**相同的WS服务器**。
- 在`connect`中提供设备身份；配对是**基于设备的**（角色为`node`）且
  批准信息保存在设备配对存储中。
- 暴露诸如`canvas.*`、`camera.*`、`screen.record`、`location.get`等命令。

协议详情：

- [网关协议](/gateway/protocol)

### WebChat

- 使用网关WS API进行聊天历史记录和发送的静态UI。
- 在远程设置中，通过与其他客户端相同的SSH/Tailscale隧道连接。

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

## 线路协议（摘要）

- 传输：WebSocket，带有JSON负载的文本帧。
- 第一帧**必须**为`connect`。
- 握手后：
  - 请求：`{type:"req", id, method, params}` → `{type:"res", id, ok, payload|error}`
  - 事件：`{type:"event", event, payload, seq?, stateVersion?}`
- 如果设置了`OPENCLAW_GATEWAY_TOKEN`（或`--token`），则`connect.params.auth.token`
  必须匹配，否则套接字关闭。
- 副作用方法（`send`、`agent`）需要幂等性键以
  安全重试；服务器保持短期去重缓存。
- 节点必须在`connect`中包含`role: "node"`以及caps/commands/permissions。

## 配对+本地信任

- 所有WS客户端（操作员+节点）在`connect`上包含**设备身份**。
- 新设备ID需要配对批准；网关为后续连接颁发**设备令牌**。
- **本地**连接（回环或网关主机自己的tailnet地址）可以自动批准以保持同主机用户体验流畅。
- **非本地**连接必须签署`connect.challenge`随机数并需要显式批准。
- 网关认证（`gateway.auth.*`）仍适用于**所有**连接，无论本地还是
  远程。

详细信息：[网关协议](/gateway/protocol)、[配对](/start/pairing)、
[安全](/gateway/security)。

## 协议类型化和代码生成

- TypeBox模式定义协议。
- JSON Schema从这些模式生成。
- Swift模型从JSON Schema生成。

## 远程访问

- 首选：Tailscale或VPN。
- 替代方案：SSH隧道
  ```bash
  ssh -N -L 18789:127.0.0.1:18789 user@host
  ```
- 隧道上应用相同的握手+认证令牌。
- 在远程设置中可以为WS启用TLS+可选固定。

## 操作快照

- 启动：`openclaw gateway`（前台，日志输出到stdout）。
- 健康检查：通过WS的`health`（也包含在`hello-ok`中）。
- 监督：launchd/systemd用于自动重启。

## 不变性

- 每台主机恰好有一个网关控制单个Baileys会话。
- 握手是强制性的；任何非JSON或非连接的第一帧都是硬关闭。
- 事件不会重播；客户端必须在出现间隙时刷新。