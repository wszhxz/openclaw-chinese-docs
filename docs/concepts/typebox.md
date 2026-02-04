---
summary: "TypeBox schemas as the single source of truth for the gateway protocol"
read_when:
  - Updating protocol schemas or codegen
title: "TypeBox"
---
# TypeBox 作为协议的唯一真相来源

最后更新时间: 2026-01-10

TypeBox 是一个以 TypeScript 为主的模式库。我们使用它来定义 **Gateway WebSocket 协议**（握手、请求/响应、服务器事件）。这些模式驱动 **运行时验证**、**JSON Schema 导出** 和 **Swift 代码生成** 用于 macOS 应用。一个唯一的真相来源；其他一切均自动生成。

如果您需要更高级别的协议上下文，请从 [Gateway 架构](/concepts/architecture) 开始。

## 思维模型（30 秒）

每个 Gateway WS 消息都是三种帧之一：

- **请求**: `{ type: "req", id, method, params }`
- **响应**: `{ type: "res", id, ok, payload | error }`
- **事件**: `{ type: "event", event, payload, seq?, stateVersion? }`

第一帧 **必须** 是 `connect` 请求。之后，客户端可以调用方法（例如 `health`, `send`, `chat.send`）并订阅事件（例如 `presence`, `tick`, `agent`）。

连接流程（最小）：

```
Client                    Gateway
  |---- req:connect -------->|
  |<---- res:hello-ok --------|
  |<---- event:tick ----------|
  |---- req:health ---------->|
  |<---- res:health ----------|
```

常用的方法和事件：

| 类别  | 示例                                                  | 备注                              |
| --------- | --------------------------------------------------------- | ---------------------------------- |
| 核心      | `connect`, `health`, `status`                             | `connect` 必须是第一个            |
| 消息传递 | `send`, `poll`, `agent`, `agent.wait`                     | 需要副作用 `idempotencyKey` |
| 聊天      | `chat.history`, `chat.send`, `chat.abort`, `chat.inject`  | WebChat 使用这些                 |
| 会话  | `sessions.list`, `sessions.patch`, `sessions.delete`      | 会话管理员                      |
| 节点     | `node.list`, `node.invoke`, `node.pair.*`                 | Gateway WS + 节点操作          |
| 事件    | `tick`, `presence`, `agent`, `chat`, `health`, `shutdown` | 服务器推送                        |

权威列表位于 `src/gateway/server.ts` (`METHODS`, `EVENTS`)。

## 模式存储位置

- 源码: `src/gateway/protocol/schema.ts`
- 运行时验证器 (AJV): `src/gateway/protocol/index.ts`
- 服务器握手 + 方法分派: `src/gateway/server.ts`
- 节点客户端: `src/gateway/client.ts`
- 生成的 JSON Schema: `dist/protocol.schema.json`
- 生成的 Swift 模型: `apps/macos/Sources/OpenClawProtocol/GatewayModels.swift`

## 当前流水线

- `pnpm protocol:gen`
  - 将 JSON Schema (draft‑07) 写入 `dist/protocol.schema.json`
- `pnpm protocol:gen:swift`
  - 生成 Swift 网关模型
- `pnpm protocol:check`
  - 运行两个生成器并验证输出已提交

## 运行时如何使用模式

- **服务器端**: 每个传入帧都使用 AJV 进行验证。握手仅接受一个 `connect` 请求，其参数匹配 `ConnectParams`。
- **客户端**: JS 客户端在使用之前验证事件和响应帧。
- **方法表面**: Gateway 在 `hello-ok` 中宣布支持的 `methods` 和 `events`。

## 示例帧

连接（第一个消息）:

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

Hello-ok 响应:

```json
{
  "type": "res",
  "id": "c1",
  "ok": true,
  "payload": {
    "type": "hello-ok",
    "protocol": 2,
    "server": { "version": "dev", "connId": "ws-1" },
    "features": { "methods": ["health"], "events": ["tick"] },
    "snapshot": {
      "presence": [],
      "health": {},
      "stateVersion": { "presence": 0, "health": 0 },
      "uptimeMs": 0
    },
    "policy": { "maxPayload": 1048576, "maxBufferedBytes": 1048576, "tickIntervalMs": 30000 }
  }
}
```

请求 + 响应:

```json
{ "type": "req", "id": "r1", "method": "health" }
```

```json
{ "type": "res", "id": "r1", "ok": true, "payload": { "ok": true } }
```

事件:

```json
{ "type": "event", "event": "tick", "payload": { "ts": 1730000000 }, "seq": 12 }
```

## 最小客户端 (Node.js)

最小有用流程：连接 + 健康检查。

```ts
import { WebSocket } from "ws";

const ws = new WebSocket("ws://127.0.0.1:18789");

ws.on("open", () => {
  ws.send(
    JSON.stringify({
      type: "req",
      id: "c1",
      method: "connect",
      params: {
        minProtocol: 3,
        maxProtocol: 3,
        client: {
          id: "cli",
          displayName: "example",
          version: "dev",
          platform: "node",
          mode: "cli",
        },
      },
    }),
  );
});

ws.on("message", (data) => {
  const msg = JSON.parse(String(data));
  if (msg.type === "res" && msg.id === "c1" && msg.ok) {
    ws.send(JSON.stringify({ type: "req", id: "h1", method: "health" }));
  }
  if (msg.type === "res" && msg.id === "h1") {
    console.log("health:", msg.payload);
    ws.close();
  }
});
```

## 实际示例：端到端添加一个方法

示例：添加一个新的 `system.echo` 请求，返回 `{ ok: true, text }`。

1. **模式（唯一真相来源）**

添加到 `src/gateway/protocol/schema.ts`:

```ts
export const SystemEchoParamsSchema = Type.Object(
  { text: NonEmptyString },
  { additionalProperties: false },
);

export const SystemEchoResultSchema = Type.Object(
  { ok: Type.Boolean(), text: NonEmptyString },
  { additionalProperties: false },
);
```

将两者添加到 `ProtocolSchemas` 并导出类型:

```ts
  SystemEchoParams: SystemEchoParamsSchema,
  SystemEchoResult: SystemEchoResultSchema,
```

```ts
export type SystemEchoParams = Static<typeof SystemEchoParamsSchema>;
export type SystemEchoResult = Static<typeof SystemEchoResultSchema>;
```

2. **验证**

在 `src/gateway/protocol/index.ts` 中导出 AJV 验证器:

```ts
export const validateSystemEchoParams = ajv.compile<SystemEchoParams>(SystemEchoParamsSchema);
```

3. **服务器行为**

在 `src/gateway/server-methods/system.ts` 中添加一个处理程序:

```ts
export const systemHandlers: GatewayRequestHandlers = {
  "system.echo": ({ params, respond }) => {
    const text = String(params.text ?? "");
    respond(true, { ok: true, text });
  },
};
```

在 `src/gateway/server-methods.ts` 中注册它（已经合并了 `systemHandlers`），
然后将 `"system.echo"` 添加到 `METHODS` 在 `src/gateway/server.ts` 中。

4. **重新生成**

```bash
pnpm protocol:check
```

5. **测试 + 文档**

在 `src/gateway/server.*.test.ts` 中添加一个服务器测试并在文档中记录该方法。

## Swift 代码生成行为

Swift 生成器发出：

- `GatewayFrame` 枚举带有 `req`, `res`, `event`, 和 `unknown` 情况
- 强类型负载结构体/枚举
- `ErrorCode` 值和 `GATEWAY_PROTOCOL_VERSION`

未知帧类型被保留为原始负载以实现向前兼容性。

## 版本控制 + 兼容性

- `PROTOCOL_VERSION` 存在于 `src/gateway/protocol/schema.ts`。
- 客户端发送 `minProtocol` + `maxProtocol`；服务器拒绝不匹配的情况。
- Swift 模型保留未知帧类型以避免破坏旧客户端。

## 模式模式和约定

- 大多数对象使用 `additionalProperties: false` 进行严格的负载。
- `NonEmptyString` 是 ID 和方法/事件名称的默认值。
- 顶级 `GatewayFrame` 在 `type` 上使用 **判别器**。
- 具有副作用的方法通常需要在参数中包含 `idempotencyKey`（示例：`send`, `poll`, `agent`, `chat.send`）。

## 实时模式 JSON

生成的 JSON Schema 在仓库中的 `dist/protocol.schema.json`。发布的原始文件通常可在以下位置获取：

- https://raw.githubusercontent.com/openclaw/openclaw/main/dist/protocol.schema.json

## 当您更改模式时

1. 更新 TypeBox 模式。
2. 运行 `pnpm protocol:check`。
3. 提交重新生成的模式 + Swift 模型。