---
summary: "Bridge protocol (legacy nodes): TCP JSONL, pairing, scoped RPC"
read_when:
  - Building or debugging node clients (iOS/Android/macOS node mode)
  - Investigating pairing or bridge auth failures
  - Auditing the node surface exposed by the gateway
title: "Bridge Protocol"
---
# 桥接协议（旧版节点传输）

桥接协议是一个 **旧版** 节点传输（TCP JSONL）。新的节点客户端应使用统一的网关 WebSocket 协议。

如果您正在构建操作员或节点客户端，请使用 [网关协议](/gateway/protocol)。

**注意：** 当前的 OpenClaw 构建不再包含 TCP 桥接监听器；此文档仅用于历史参考。旧版 `bridge.*` 配置键不再属于配置架构。

## 为什么同时存在两种协议

- **安全边界**：桥接暴露一个小型允许列表而不是完整的网关 API 表面。
- **配对 + 节点身份**：节点准入由网关控制，并与每个节点的令牌相关联。
- **发现用户体验**：节点可以通过 LAN 上的 Bonjour 发现网关，或者直接通过尾网连接。
- **本地回环 WS**：完整的 WS 控制平面保持本地，除非通过 SSH 隧道传输。

## 传输

- TCP，每行一个 JSON 对象（JSONL）。
- 可选 TLS（当 `bridge.tls.enabled` 为真时）。
- 旧版默认监听端口是 `18790`（当前构建不启动 TCP 桥接）。

启用 TLS 时，发现 TXT 记录包括 `bridgeTls=1` 加上 `bridgeTlsSha256`，以便节点可以固定证书。

## 握手 + 配对

1. 客户端发送 `hello` 包含节点元数据 + 令牌（如果已配对）。
2. 如果未配对，网关回复 `error` (`NOT_PAIRED`/`UNAUTHORIZED`)。
3. 客户端发送 `pair-request`。
4. 网关等待批准，然后发送 `pair-ok` 和 `hello-ok`。

`hello-ok` 返回 `serverName` 并可能包括 `canvasHostUrl`。

## 帧

客户端 → 网关：

- `req` / `res`：范围限定的网关 RPC（聊天、会话、配置、健康状况、语音唤醒、技能.bin）
- `event`：节点信号（语音记录、代理请求、聊天订阅、执行生命周期）

网关 → 客户端：

- `invoke` / `invoke-res`：节点命令 (`canvas.*`, `camera.*`, `screen.record`,
  `location.get`, `sms.send`)
- `event`：已订阅会话的聊天更新
- `ping` / `pong`：心跳

旧版允许列表强制执行位于 `src/gateway/server-bridge.ts`（已移除）。

## 执行生命周期事件

节点可以发出 `exec.finished` 或 `exec.denied` 事件以显示 system.run 活动。
这些被映射到网关中的系统事件。（旧版节点可能仍然发出 `exec.started`。）

负载字段（除非注明，否则全部可选）：

- `sessionKey`（必需）：接收系统事件的代理会话。
- `runId`：用于分组的唯一执行 ID。
- `command`：原始或格式化的命令字符串。
- `exitCode`, `timedOut`, `success`, `output`：完成详情（仅完成时）。
- `reason`：拒绝原因（仅拒绝时）。

## 尾网使用

- 将桥接绑定到尾网 IP：`bridge.bind: "tailnet"` 在 `~/.openclaw/openclaw.json` 中。
- 客户端通过 MagicDNS 名称或尾网 IP 连接。
- Bonjour 不跨网络；在需要时使用手动主机/端口或广域 DNS-SD。

## 版本控制

桥接当前是 **隐式 v1**（没有最小/最大协商）。预期向后兼容；在任何重大更改之前添加桥接协议版本字段。