---
summary: "Bridge protocol (legacy nodes): TCP JSONL, pairing, scoped RPC"
read_when:
  - Building or debugging node clients (iOS/Android/macOS node mode)
  - Investigating pairing or bridge auth failures
  - Auditing the node surface exposed by the gateway
title: "Bridge Protocol"
---
# 桥接协议（传统节点传输）

桥接协议是一种**传统**的节点传输方式（基于 TCP 的 JSONL）。新的节点客户端应改用统一的网关 WebSocket 协议。

如果您正在构建操作员或节点客户端，请使用[网关协议](/gateway/protocol)。

**注意：** 当前 OpenClaw 版本不再附带 TCP 桥接监听器；本文档仅作历史参考之用。传统的 `bridge.*` 配置项已不再属于配置模式。

## 为何同时存在两种协议

- **安全边界**：桥接协议仅暴露一个较小的白名单，而非完整的网关 API 接口面。
- **配对 + 节点身份认证**：节点准入由网关负责，并与每个节点专属的令牌绑定。
- **发现体验（Discovery UX）**：节点可通过局域网中的 Bonjour 发现网关，或直接通过 Tailnet 连接。
- **回环 WebSocket（Loopback WS）**：完整的 WebSocket 控制平面保持本地运行，除非通过 SSH 隧道转发。

## 传输层

- TCP 协议，每行一个 JSON 对象（JSONL）。
- 可选 TLS（当 `bridge.tls.enabled` 为 `true` 时启用）。
- 传统默认监听端口为 `18790`（当前版本不启动 TCP 桥接服务）。

启用 TLS 后，服务发现 TXT 记录中将包含 `bridgeTls=1` 及非密钥提示 `bridgeTlsSha256`。请注意，Bonjour/mDNS TXT 记录未经身份验证；客户端不得将所广播的指纹视为权威绑定依据，除非获得用户明确授权或其他带外验证机制支持。

## 握手与配对流程

1. 客户端发送 `hello`，其中包含节点元数据及令牌（若已配对）。
2. 若尚未配对，网关返回 `error`（对应 `NOT_PAIRED`/`UNAUTHORIZED`）。
3. 客户端发送 `pair-request`。
4. 网关等待人工批准后，发送 `pair-ok` 和 `hello-ok`。

`hello-ok` 返回 `serverName`，并可选包含 `canvasHostUrl`。

## 帧结构（Frames）

客户端 → 网关：

- `req` / `res`：作用域限定的网关 RPC（聊天、会话、配置、健康状态、语音唤醒、skills.bins）
- `event`：节点信号（语音转录文本、代理请求、聊天订阅、执行生命周期事件）

网关 → 客户端：

- `invoke` / `invoke-res`：节点指令（`canvas.*`、`camera.*`、`screen.record`、`location.get`、`sms.send`）
- `event`：已订阅会话的聊天更新
- `ping` / `pong`：保活信号（keepalive）

传统白名单强制执行逻辑位于 `src/gateway/server-bridge.ts`（已移除）。

## 执行生命周期事件（Exec lifecycle events）

节点可发出 `exec.finished` 或 `exec.denied` 事件，以反映 `system.run` 活动。这些事件在网关中映射为系统事件。（传统节点可能仍会发出 `exec.started`。）

载荷字段（所有字段均为可选，除非特别注明）：

- `sessionKey`（必需）：接收该系统事件的代理会话。
- `runId`：用于分组的唯一执行 ID。
- `command`：原始或格式化后的命令字符串。
- `exitCode`、`timedOut`、`success`、`output`：完成详情（仅在“已完成”状态下存在）。
- `reason`：拒绝原因（仅在“被拒绝”状态下存在）。

## Tailnet 使用方式

- 将桥接服务绑定至 Tailnet IP：在 `~/.openclaw/openclaw.json` 中设置 `bridge.bind: "tailnet"`。
- 客户端通过 MagicDNS 名称或 Tailnet IP 连接。
- Bonjour **无法跨网络工作**；如需广域网支持，请手动指定主机名/端口，或使用广域 DNS‑SD。

## 版本控制

桥接协议当前为**隐式 v1 版本**（无最小/最大版本协商）。预期保持向后兼容性；任何破坏性变更前，须先添加桥接协议版本字段。