---
summary: "Expose an OpenAI-compatible /v1/chat/completions HTTP endpoint from the Gateway"
read_when:
  - Integrating tools that expect OpenAI Chat Completions
title: "OpenAI Chat Completions"
---
# OpenAI 聊天补全（HTTP）

OpenClaw 的网关可提供一个小型的、与 OpenAI 兼容的聊天补全端点。

该端点**默认处于禁用状态**。请先在配置中启用它。

- `POST /v1/chat/completions`
- 与网关使用同一端口（WS + HTTP 多路复用）：`http://<gateway-host>:<port>/v1/chat/completions`

在底层，请求将作为一次常规的网关代理运行来执行（与 `openclaw agent` 使用相同的代码路径），因此路由、权限和配置均与您的网关保持一致。

## 认证

使用网关的认证配置。请发送一个 Bearer Token：

- `Authorization: Bearer <token>`

注意事项：

- 当 `gateway.auth.mode="token"` 时，使用 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 当 `gateway.auth.mode="password"` 时，使用 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。
- 如果配置了 `gateway.auth.rateLimit`，且发生过多认证失败，则该端点将返回 `429`，并附带 `Retry-After`。

## 安全边界（重要）

请将此端点视为该网关实例的**完整操作员访问面**。

- 此处的 HTTP Bearer 认证并非面向用户的细粒度作用域模型。
- 对于此端点有效的网关 Token/密码，应被视为所有者/操作员凭证。
- 请求通过与受信任操作员操作相同的控制平面代理路径执行。
- 此端点上不存在独立的非所有者/普通用户工具边界；一旦调用方在此处通过网关认证，OpenClaw 即视该调用方为该网关的受信任操作员。
- 若目标代理策略允许敏感工具，此端点亦可使用它们。
- 请仅将此端点部署于回环地址 / Tailnet / 私有入口网络中；切勿直接将其暴露于公共互联网。

参见 [安全性](/gateway/security) 和 [远程访问](/gateway/remote)。

## 选择代理

无需自定义请求头：在 OpenAI 的 `model` 字段中编码代理 ID：

- `model: "openclaw:<agentId>"`（示例：`"openclaw:main"`、`"openclaw:beta"`）
- `model: "agent:<agentId>"`（别名）

或通过请求头指定特定 OpenClaw 代理：

- `x-openclaw-agent-id: <agentId>`（默认值：`main`）

高级用法：

- 使用 `x-openclaw-session-key: <sessionKey>` 可完全控制会话路由。

## 启用该端点

将 `gateway.http.endpoints.chatCompletions.enabled` 设置为 `true`：

```json5
{
  gateway: {
    http: {
      endpoints: {
        chatCompletions: { enabled: true },
      },
    },
  },
}
```

## 禁用该端点

将 `gateway.http.endpoints.chatCompletions.enabled` 设置为 `false`：

```json5
{
  gateway: {
    http: {
      endpoints: {
        chatCompletions: { enabled: false },
      },
    },
  },
}
```

## 会话行为

默认情况下，该端点对每个请求均为**无状态**（每次调用均生成新的会话密钥）。

若请求中包含 OpenAI 的 `user` 字符串，网关将从中派生出一个稳定的会话密钥，从而使重复调用可共享同一个代理会话。

## 流式响应（SSE）

设置 `stream: true` 以接收服务端推送事件（SSE）：

- `Content-Type: text/event-stream`
- 每个事件行均为 `data: <json>`
- 流式响应以 `data: [DONE]` 结束

## 示例

非流式响应：

```bash
curl -sS http://127.0.0.1:18789/v1/chat/completions \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'x-openclaw-agent-id: main' \
  -d '{
    "model": "openclaw",
    "messages": [{"role":"user","content":"hi"}]
  }'
```

流式响应：

```bash
curl -N http://127.0.0.1:18789/v1/chat/completions \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'x-openclaw-agent-id: main' \
  -d '{
    "model": "openclaw",
    "stream": true,
    "messages": [{"role":"user","content":"hi"}]
  }'
```