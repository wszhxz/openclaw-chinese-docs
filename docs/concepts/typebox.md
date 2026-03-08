---
summary: "TypeBox schemas as the single source of truth for the gateway protocol"
read_when:
  - Updating protocol schemas or codegen
title: "TypeBox"
---
# TypeBox 作为 protocol 的 source of truth

最后更新时间：2026-01-10

TypeBox 是一个 TypeScript 优先的 schema 库。我们用它来定义 **Gateway WebSocket protocol**（handshake、request/response、server events）。这些 schema 驱动 **runtime validation**、**JSON Schema export** 以及 macOS 应用的 **Swift codegen**。单一 source of truth；其他所有内容均由此生成。

如果您想了解更高层的 protocol 上下文，请参阅 [Gateway architecture](/concepts/architecture)。

## 心智模型（30 秒）

每个 Gateway WS 消息都是以下三种 frame 之一：

- **Request**: `{ type: "req", id, method, params }`
- **Response**: `{ type: "res", id, ok, payload | error }`
- **Event**: `{ type: "event", event, payload, seq?, stateVersion? }`

第一个 frame **必须** 是一个 `connect` request。之后，clients 可以调用 methods（例如 `health`、`send`、`chat.send`）并订阅 events（例如 `presence`、`tick`、`agent`）。

连接 flow（最小化）：

```
Client                    Gateway
  |---- req:connect -------->|
  |<---- res:hello-ok --------|
  |<---- event:tick ----------|
  |---- req:health ---------->|
  |<---- res:health ----------|
```

常用 methods + events：

| 类别  | 示例                                                  | 备注                              |
| --------- | --------------------------------------------------------- | ---------------------------------- |
| Core      | `connect`, `health`, `status`                             | `connect` 必须是第一个            |
| Messaging | `send`, `poll`, `agent`, `agent.wait`                     | side-effects 需要 `idempotencyKey` |
| Chat      | `chat.history`, `chat.send`, `chat.abort`, `chat.inject`  | WebChat 使用这些                 |
| Sessions  | `sessions.list`, `sessions.patch`, `sessions.delete`      | session admin                      |
| Nodes     | `node.list`, `node.invoke`, `node.pair.*`                 | Gateway WS + node actions          |
| Events    | `tick`, `presence`, `agent`, `chat`, `health`, `shutdown` | server push                        |

权威列表位于 `src/gateway/server.ts` (`METHODS`, `EVENTS`)。

## Schema 存放位置

- 源：`src/gateway/protocol/schema.ts`
- Runtime validators (AJV): `src/gateway/protocol/index.ts`
- Server handshake + method dispatch: `src/gateway/server.ts`
- Node client: `src/gateway/client.ts`
- Generated JSON Schema: `dist/protocol.schema.json`
- Generated Swift models: `apps/macos/Sources/OpenClawProtocol/GatewayModels.swift`

## 当前 pipeline

- `pnpm protocol:gen`
  - 写入 JSON Schema (draft‑07) 至 `dist/protocol.schema.json`
- `pnpm protocol:gen:swift`
  - 生成 Swift gateway models
- `pnpm protocol:check`
  - 运行两个 generators 并验证 output 已 commit

## Schema 在 runtime 的使用方式

- **Server side**：每个 inbound frame 都使用 AJV 进行 validation。handshake 仅接受 params 匹配 `ConnectParams` 的 `connect` request。
- **Client side**：JS client 在使用 event 和 response frames 之前会对其进行 validation。
- **Method surface**：Gateway 在 `hello-ok` 中通告支持的 `methods` 和 `events`。

## Frame 示例

Connect（第一条消息）：

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

Hello-ok response：

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

Request + response：

```json
{ "type": "req", "id": "r1", "method": "health" }
```

```json
{ "type": "res", "id": "r1", "ok": true, "payload": { "ok": true } }
```

Event：

```json
{ "type": "event", "event": "tick", "payload": { "ts": 1730000000 }, "seq": 12 }
```

## 最小化 client (Node.js)

最小可用 flow：connect + health。

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

## 完整示例：端到端添加一个 method

示例：添加一个新的返回 `{ ok: true, text }` 的 `system.echo` request。

1. **Schema (source of truth)**

添加至 `src/gateway/protocol/schema.ts`：

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

将两者都添加至 `ProtocolSchemas` 并 export types：

```ts
  SystemEchoParams: SystemEchoParamsSchema,
  SystemEchoResult: SystemEchoResultSchema,
```

```ts
export type SystemEchoParams = Static<typeof SystemEchoParamsSchema>;
export type SystemEchoResult = Static<typeof SystemEchoResultSchema>;
```

2. **Validation**

在 `src/gateway/protocol/index.ts` 中，export 一个 AJV validator：

```ts
export const validateSystemEchoParams = ajv.compile<SystemEchoParams>(SystemEchoParamsSchema);
```

3. **Server behavior**

在 `src/gateway/server-methods/system.ts` 中添加一个 handler：

```ts
export const systemHandlers: GatewayRequestHandlers = {
  "system.echo": ({ params, respond }) => {
    const text = String(params.text ?? "");
    respond(true, { ok: true, text });
  },
};
```

在 `src/gateway/server-methods.ts` 中注册它（已合并 `systemHandlers`），
然后将 `"system.echo"` 添加至 `src/gateway/server.ts` 中的 `METHODS`。

4. **Regenerate**

```bash
pnpm protocol:check
```

5. **Tests + docs**

在 `src/gateway/server.*.test.ts` 中添加一个 server test 并在 docs 中注明该 method。

## Swift codegen 行为

Swift generator 输出：

- 带有 `req`、`res`、`event` 和 `unknown` cases 的 `GatewayFrame` enum
- 强类型 payload structs/enums
- `ErrorCode` 值和 `GATEWAY_PROTOCOL_VERSION`

未知 frame 类型会作为 raw payloads 保留以实现向前兼容。

## 版本控制 + 兼容性

- `PROTOCOL_VERSION` 位于 `src/gateway/protocol/schema.ts`。
- Clients 发送 `minProtocol` + `maxProtocol`；server 会拒绝不匹配的情况。
- Swift models 保留未知的 frame 类型以避免破坏旧 clients。

## Schema 模式和约定

- 大多数对象使用 `additionalProperties: false` 用于严格 payloads。
- `NonEmptyString` 是 IDs 和 method/event 名称的默认值。
- 顶层 `GatewayFrame` 在 `type` 上使用 **discriminator**。
- 带有 side effects 的 methods 通常在 params 中需要 `idempotencyKey`
  （例如：`send`、`poll`、`agent`、`chat.send`）。
- `agent` 接受可选的 `internalEvents` 用于 runtime-generated orchestration context
  （例如 subagent/cron task completion handoff）；将此视为 internal API surface。

## 实时 schema JSON

生成的 JSON Schema 位于仓库的 `dist/protocol.schema.json`。
发布的 raw 文件通常位于：

- [https://raw.githubusercontent.com/openclaw/openclaw/main/dist/protocol.schema.json](https://raw.githubusercontent.com/openclaw/openclaw/main/dist/protocol.schema.json)

## 当您更改 schemas 时

1. 更新 TypeBox schemas。
2. 运行 `pnpm protocol:check`。
3. Commit 再生的 schema + Swift models。