---
summary: "Bridge protocol (legacy nodes): TCP JSONL, pairing, scoped RPC"
read_when:
  - Building or debugging node clients (iOS/Android/macOS node mode)
  - Investigating pairing or bridge auth failures
  - Auditing the node surface exposed by the gateway
title: "Bridge Protocol"
---
# 桥接协议（遗留节点传输）

桥接协议是一种**遗留**节点传输协议（TCP JSONL）。新节点客户端应使用统一的网关 WebSocket 协议。

如果您正在构建操作员或节点客户端，请使用 [网关协议](/gateway/protocol)。

**注意：** 当前 OpenClaw 构建版本不再包含 TCP 桥接监听器；此文档仅用于历史参考。遗留的 `bridge.*` 配置键已不再属于配置模式的一部分。

## 为何同时存在两种协议

- **安全边界**：桥接协议仅暴露一个较小的白名单，而非完整的网关 API 接口。
- **配对 + 节点身份**：节点准入由网关控制，并与每个节点的令牌绑定。
- **发现用户体验**：节点可通过 Bonjour 在局域网中发现网关，或直接通过 tailnet 连接。
- **环回 WebSocket**：完整的 WebSocket 控制平面除非通过 SSH 隧道，否则保持本地化。

## 传输方式

- TCP，每行一个 JSON 对象（JSONL）。
- 可选 TLS（当 `bridge.tls.enabled` 为 true 时）。
- 遗留默认监听端口为 `18790`（当前构建版本不再启动 TCP 桥接）。

当 TLS 启用时，发现 TXT 记录包含 `bridgeTls=1` 和 `bridgeTlsSha265`，以便节点可以固定证书。

## 握手 + 配对

1. 客户端发送 `hello` 包含节点元数据 + 令牌（如果已配对）。
2. 如果未配对，网关回复 `error`（`NOT_PAIRED`/`UNAUTHORIZED`）。
3. 客户端发送 `pair-request`。
4. 网关等待批准，然后发送 `pair-ok` 和 `hello-ok`。

`hello-ok` 返回 `serverName`，并可能包含 `canvasHostUrl`。

## 帧

客户端 → 网关：

- `req` / `res`：作用域网关 RPC（聊天、会话、配置、健康、语音唤醒、技能.bins）
- `event`：节点信号（语音转录、代理请求、聊天订阅、执行生命周期）

网关 → 客户端：

- `invoke` / `invoke-res`：节点命令（`canvas.*`、`camera.*`、`screen.record`、`location.get`、`sms.send`）
- `event`：订阅会话的聊天更新
- `ping` / `pong`：保持连接

遗留白名单强制执行功能位于 `src/gateway/server-bridge.ts`（已删除）。

## 执行生命周期事件

节点可以发出 `exec.finished` 或 `exec.denied` 事件以显示系统运行活动。这些事件在网关中映射为系统事件。（旧版节点仍可能发出 `exec.started`。）

负载字段（所有字段可选，除非另有说明）：

- `sessionKey`（必需）：接收系统事件的代理会话。
- `runId`：用于分组的唯一执行 ID。
- `command`：原始或格式化的命令字符串。
- `exitCode`、`timedOut`、`success`、`output`：完成详情（仅在完成时）。
- `reason`：拒绝原因（仅在拒绝时）。

## Tailnet 使用

- 绑定桥接到 tailnet IP：在 `~/.openclaw/openclaw.json` 中设置 `bridge.bind: "tailnet"`。
- 客户端通过 MagicDNS 名称或 tailnet IP 连接。
- Bonjour **不会** 跨网络；需要时使用手动主机/端口或广域 DNS-SD。

## 版本控制

桥接协议目前为 **隐式 v1**（无最小/最大协商）。预期向后兼容；在任何破坏性更改前添加桥接协议版本字段。