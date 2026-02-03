---
summary: "Expose an OpenAI-compatible /v1/chat/completions HTTP endpoint from the Gateway"
read_when:
  - Integrating tools that expect OpenAI Chat Completions
title: "OpenAI Chat Completions"
---
"`<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context. The content is about setting up an OpenAI-compatible Chat Completions endpoint using OpenClaw's Gateway. There are sections on enabling/disabling the endpoint, authentication, choosing an agent, session behavior, streaming, and examples.

First, I'll translate the headings. "OpenAI Chat Completions (HTTP)" becomes "OpenAI 聊天完成（HTTP）". The next section is about the Gateway serving the endpoint, so I'll make sure to keep the technical terms accurate. Terms like "disabled by default" should be "默认禁用".

I need to be careful with the code snippets and URLs. For example, "POST /v1/chat/completions" remains the same but in Chinese context, maybe add the protocol. Also, the JSON configuration examples need to be translated but keep the structure. Terms like "bearer token" are usually translated as "Bearer 令牌" but I should check if there's a standard term in Chinese tech docs.

Authentication section mentions "gateway.auth.mode" which should stay as is but with Chinese labels. The examples with curl commands should have the URLs and parameters translated where necessary, but the actual command syntax remains the same. 

For the streaming section, "Server-Sent Events (SSE)" is commonly known as "服务器发送事件（SSE）" in Chinese tech contexts. I'll ensure that the technical terms are consistent with common translations.

I should also check for any specific terms related to OpenClaw and OpenAI that might have established translations. For instance, "agent" might be translated as "代理" but in some contexts, it's kept as "agent". Need to maintain consistency.

Finally, I'll review the entire translation to ensure that the technical accuracy is preserved, and the structure matches the original. Making sure that all code blocks and configuration examples are correctly formatted and that the instructions are clear in Chinese.
</think>

# OpenAI 聊天完成（HTTP）

OpenClaw 的网关可以提供一个小型的 OpenAI 兼容的聊天完成端点。

此端点默认是**禁用的**。请先在配置中启用它。

- `POST /v1/chat/completions`
- 与网关相同端口（WS + HTTP 多路复用）：`http://<gateway-host>:<port>/v1/chat/completions`

在内部，请求会作为正常的网关代理运行（与 `openclaw agent` 使用相同的代码路径），因此路由/权限/配置与您的网关保持一致。

## 认证

使用网关的认证配置。发送一个 Bearer 令牌：

- `Authorization: Bearer <token>`

注意事项：

- 当 `gateway.auth.mode="token"` 时，使用 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 当 `gateway.auth.mode="password"` 时，使用 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。

## 选择代理

无需自定义头信息：在 OpenAI 的 `model` 字段中编码代理 ID：

- `model: "openclaw:<agentId>"`（示例：`"openclaw:main"`，`"openclaw:beta"`）
- `model: "agent:<agentId>"`（别名）

或者通过头信息指定特定的 OpenClaw 代理：

- `x-openclaw-agent-id: <agentId>`（默认：`main`）

高级用法：

- `x-openclob-session-key: <sessionKey>` 以完全控制会话路由。

## 启用端点

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

## 禁用端点

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

默认情况下，该端点是**无状态的**（每次调用生成新的会话密钥）。

如果请求包含 OpenAI 的 `user` 字符串，网关会从其推导出稳定的会话密钥，因此重复调用可以共享代理会话。

## 流式传输（SSE）

设置 `stream: true` 以接收服务器发送事件（SSE）：

- `Content-Type: text/event-stream`
- 每个事件行是 `data: <json>`
- 流式传输以 `data: [DONE]` 结束

## 示例

非流式传输：

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

流式传输：

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