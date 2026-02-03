---
summary: "TypeBox schemas as the single source of truth for the gateway protocol"
read_when:
  - Updating protocol schemas or codegen
title: "TypeBox"
---
# TypeBox 作为协议的单一真实来源

最后更新时间：2026-01-10

TypeBox 是一个以 TypeScript 为核心的模式库。我们使用它来定义 **网关 WebSocket 协议**（握手、请求/响应、服务器事件）。这些模式驱动 **运行时验证**、**JSON Schema 导出** 以及 **macOS 应用的 Swift 代码生成**。一个单一真实来源；其他一切内容均通过生成方式实现。

如果你想了解更高层次的协议上下文，请从 [网关架构](/concepts/architecture) 开始。

## 思维模型（30 秒）

每个网关 WebSocket 消息都是以下三种帧之一：

- **请求**：`{ type: "req", id, method, params }`
- **响应**：`{ type: "res", id, ok, payload | error }`
- **事件**：`{ type: "event", event, payload, seq?, stateVersion? }`

第一个帧 **必须** 是一个 `connect` 请求。之后，客户端可以调用方法（例如 `health`、`send`、`chat.send`）并订阅事件（例如 `presence`、`tick`、`agent`）。

连接流程（最小化）：

```
客户端                    网关
  |---- req:connect -------->|
  |<---- res:hello-ok --------|
  |<---- event:tick ----------|
  |---- req:health ---------->|
  |<---- res:health ----------|
```

常用方法 + 事件：

| 分类  | 示例                                                  | 说明                              |
| --------- | --------------------------------------------------------- | ---------------------------------- |
| 核心      | `connect`, `health`, `status`                             | `connect` 必须为第一个            |
| 消息     | `send`, `poll`, `agent`, `agent.wait`                     | 副作用需要 `idempotencyKey` |
| 聊天      | `chat.history`, `chat.send`, `chat.abort`, `chat.inject`  | WebChat 使用这些                 |
| 会话     | `sessions.list`, `sessions.patch`, `sessions.delete`      | 会话管理                      |
| 节点     | `node.list`, `node.invoke`, `node.pair.*`                 | 网关 WebSocket + 节点操作          |
| 事件    | `tick`, `presence`, `agent`, `chat`, `health`, `shutdown` | 服务器推送                        |

权威列表位于 `src/gateway/server.ts` (`METHODS`, `EVENTS`)。

## 模式所在位置

- 来源: `src/gateway/protocol/schema.ts`
- 运行时验证器 (AJV): `src/gateway/protocol/index.ts`
- 服务器握手 + 方法分发: `src/gateway/server.ts`
- 节点客户端: `src/gateway/client.ts`
- 生成的 JSON Schema: `dist/protocol.schema.json`
- 生成的 Swift 模型: `apps/macos/Sources/OpenClawProtocol/GatewayModels.swift`

## 当前流水线

- `pnpm protocol:gen`
  - 将 JSON Schema (draft‑07) 写入 `dist/protocol.schema.json`
- `pnpm protocol:gen:swift`
  - 生成 Swift 网关模型
- `pnpm protocol:check`
  - 运行两个生成器并验证输出是否已提交

## 模式在运行时的使用方式

- **服务器端**：每个入站帧均通过 AJV 进行验证。握手仅接受 `connect` 请求，其参数需匹配 `ConnectParams`。
- **客户端**：JS 客户端在使用前验证事件和响应帧。
- **方法接口**：网关在 `hello-ok` 中公布支持的 `methods` 和 `events`。

## 示例帧

连接（第一个消息）：

```json
{
  "type": "req",
  "id": "c1",
  "method": "connect",
  "params": {
    "minProtocol": 2,
    "maxProtocol": 2,
    "client": {
      "id": "openclaw-macos",
      "displayName": "macos",
      "version": "1.0.0",
      "platform": "macos 15.1",
      "mode": "ui",
      "instanceId": "A1B2"
    }
  }
}
```

Hello-ok 响应：

```json
{
  "type": "res",
  "id": "c1",
  "ok": true,
  "payload": {
    "type": "hello-ok",
    "protocol": 2,
    "server": { "version": "dev", "id": "openclaw" },
    "timestamp": 1680000000
  }
}
```

请求/响应示例：

```json
{
  "type": "res",
  "id": "req123",
  "ok": true,
  "payload": {
    "data": "response data"
  }
}
```

事件示例：

```json
{
  "type": "event