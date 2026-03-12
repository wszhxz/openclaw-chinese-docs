---
summary: "Invoke a single tool directly via the Gateway HTTP endpoint"
read_when:
  - Calling tools without running a full agent turn
  - Building automations that need tool policy enforcement
title: "Tools Invoke API"
---
# 工具调用（HTTP）

OpenClaw 的网关提供了一个简单的 HTTP 端点，用于直接调用单个工具。该端点始终启用，但受网关身份验证和工具策略的限制。

- `POST /tools/invoke`
- 与网关使用相同端口（WS + HTTP 多路复用）：`http://<gateway-host>:<port>/tools/invoke`

默认最大有效载荷大小为 2 MB。

## 身份验证

使用网关的身份验证配置。请发送一个 Bearer Token：

- `Authorization: Bearer <token>`

注意事项：

- 当 `gateway.auth.mode="token"` 时，使用 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 当 `gateway.auth.mode="password"` 时，使用 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
- 如果配置了 `gateway.auth.rateLimit` 且发生了过多的身份验证失败，该端点将返回 `429`，并附带 `Retry-After`。

## 请求体

```json
{
  "tool": "sessions_list",
  "action": "json",
  "args": {},
  "sessionKey": "main",
  "dryRun": false
}
```

字段说明：

- `tool`（字符串，必需）：要调用的工具名称。
- `action`（字符串，可选）：若工具 Schema 支持 `action` 且请求体中未提供 `args`，则该字段将被映射为参数。
- `args`（对象，可选）：工具特定的参数。
- `sessionKey`（字符串，可选）：目标会话密钥。若省略或为 `"main"`，网关将使用已配置的主会话密钥（遵循 `session.mainKey` 和默认代理设置，或全局范围内的 `global`）。
- `dryRun`（布尔值，可选）：保留供将来使用；当前被忽略。

## 策略与路由行为

工具的可用性通过网关代理所使用的相同策略链进行过滤：

- `tools.profile` / `tools.byProvider.profile`
- `tools.allow` / `tools.byProvider.allow`
- `agents.<id>.tools.allow` / `agents.<id>.tools.byProvider.allow`
- 组策略（当会话密钥映射到某个组或频道时）
- 子代理策略（当使用子代理会话密钥进行调用时）

如果某工具因策略限制而未被允许，该端点将返回 **404**。

此外，网关 HTTP 默认还应用一个硬性拒绝列表（即使会话策略允许该工具）：

- `sessions_spawn`
- `sessions_send`
- `gateway`
- `whatsapp_login`

您可通过 `gateway.tools` 自定义此拒绝列表：

```json5
{
  gateway: {
    tools: {
      // Additional tools to block over HTTP /tools/invoke
      deny: ["browser"],
      // Remove tools from the default deny list
      allow: ["gateway"],
    },
  },
}
```

为帮助组策略解析上下文，您可以选择性地设置以下字段：

- `x-openclaw-message-channel: <channel>`（示例：`slack`、`telegram`）
- `x-openclaw-account-id: <accountId>`（当存在多个账户时）

## 响应

- `200` → `{ ok: true, result }`
- `400` → `{ ok: false, error: { type, message } }`（无效请求或工具输入错误）
- `401` → 未授权
- `429` → 身份验证被限流（已设置 `Retry-After`）
- `404` → 工具不可用（未找到或未加入白名单）
- `405` → 方法不被允许
- `500` → `{ ok: false, error: { type, message } }`（意外的工具执行错误；返回经脱敏处理的消息）

## 示例

```bash
curl -sS http://127.0.0.1:18789/tools/invoke \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "tool": "sessions_list",
    "action": "json",
    "args": {}
  }'
```