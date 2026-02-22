---
summary: "Gateway WebSocket protocol: handshake, frames, versioning"
read_when:
  - Implementing or updating gateway WS clients
  - Debugging protocol mismatches or connect failures
  - Regenerating protocol schema/models
title: "Gateway Protocol"
---
# 网关协议 (WebSocket)

网关 WS 协议是 OpenClaw 的 **单一控制平面 + 节点传输**。所有客户端（CLI、Web UI、macOS 应用、iOS/Android 节点、无头节点）通过 WebSocket 连接并在握手时声明它们的 **角色** + **范围**。

## 传输

- WebSocket，带有 JSON 有效负载的文本帧。
- 第一帧 **必须** 是 `connect` 请求。

## 握手（连接）

网关 → 客户端（预连接挑战）：

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

客户端 → 网关：

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

网关 → 客户端：

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": { "type": "hello-ok", "protocol": 3, "policy": { "tickIntervalMs": 15000 } }
}
```

当设备令牌被颁发时，`hello-ok` 也包括：

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

### 节点示例

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## 帧格式

- **请求**: `{type:"req", id, method, params}`
- **响应**: `{type:"res", id, ok, payload|error}`
- **事件**: `{type:"event", event, payload, seq?, stateVersion?}`

具有副作用的方法需要 **幂等键**（参见架构）。

## 角色 + 范围

### 角色

- `operator` = 控制平面客户端（CLI/UI/自动化）。
- `node` = 能力主机（相机/屏幕/画布/system.run）。

### 范围（操作员）

常见范围：

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`

### 能力/命令/权限（节点）

节点在连接时声明能力声明：

- `caps`: 高级能力类别。
- `commands`: 调用的命令白名单。
- `permissions`: 细粒度开关（例如 `screen.record`, `camera.capture`）。

网关将这些视为 **声明** 并强制执行服务器端白名单。

## 在线状态

- `system-presence` 返回按设备身份键入的条目。
- 在线状态条目包括 `deviceId`, `roles`, 和 `scopes`，以便 UI 可以为每个设备显示一行
  即使它同时作为 **操作员** 和 **节点** 连接。

### 节点辅助方法

- 节点可以调用 `skills.bins` 来获取当前的技能可执行文件列表
  用于自动允许检查。

## 执行批准

- 当执行请求需要批准时，网关广播 `exec.approval.requested`。
- 操作员客户端通过调用 `exec.approval.resolve` 解决（需要 `operator.approvals` 范围）。

## 版本控制

- `PROTOCOL_VERSION` 存在于 `src/gateway/protocol/schema.ts`。
- 客户端发送 `minProtocol` + `maxProtocol`；服务器拒绝不匹配的情况。
- 架构 + 模型从 TypeBox 定义生成：
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

## 认证

- 如果设置了 `OPENCLAW_GATEWAY_TOKEN`（或 `--token`），则 `connect.params.auth.token`
  必须匹配，否则关闭套接字。
- 配对后，网关会根据连接角色 + 范围颁发一个 **设备令牌**。它在 `hello-ok.auth.deviceToken` 中返回，并应由客户端保存以备将来连接使用。
- 设备令牌可以通过 `device.token.rotate` 和
  `device.token.revoke` 旋转/撤销（需要 `operator.pairing` 范围）。

## 设备身份 + 配对

- 节点应包含一个稳定的设备身份 (`device.id`)，该身份派生自密钥对指纹。
- 网关为每个设备 + 角色颁发令牌。
- 新设备 ID 需要配对批准，除非启用了本地自动批准。
- **本地** 连接包括回环和网关主机自身的尾网地址
  （因此同一主机的尾网绑定仍然可以自动批准）。
- 所有 WS 客户端必须在 `connect` 期间包含 `device` 身份（操作员 + 节点）。
  控制 UI 只有在启用 `gateway.controlUi.dangerouslyDisableDeviceAuth`
  时才能省略它，用于紧急情况。
- 非本地连接必须对服务器提供的 `connect.challenge` 随机数进行签名。

## TLS + 固定

- 支持 WS 连接的 TLS。
- 客户端可以选择固定网关证书指纹（参见 `gateway.tls`
  配置加上 `gateway.remote.tlsFingerprint` 或 CLI `--tls-fingerprint`）。

## 范围

此协议暴露了 **完整的网关 API**（状态、通道、模型、聊天、代理、会话、节点、批准等）。确切的接口由 `src/gateway/protocol/schema.ts` 中的 TypeBox 架构定义。