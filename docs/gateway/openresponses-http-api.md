---
summary: "Expose an OpenResponses-compatible /v1/responses HTTP endpoint from the Gateway"
read_when:
  - Integrating clients that speak the OpenResponses API
  - You want item-based inputs, client tool calls, or SSE events
title: "OpenResponses API"
---
# OpenResponses API（HTTP）

OpenClaw 的网关可以提供一个兼容 OpenResponses 的 `POST /v1/responses` 接口。

该接口默认是**禁用的**。请先在配置中启用它。

- `POST /v1/responses`
- 与网关相同端口（WS + HTTP 多路复用）：`http://<gateway-host>:<port>/v1/responses`

在内部，请求会以正常的网关代理运行方式执行（与 `openclaw agent` 使用相同的代码路径），因此路由/权限/配置与您的网关保持一致。

## 认证

使用网关的认证配置。发送一个 Bearer Token：

- `Authorization: Bearer <token>`

说明：

- 当 `gateway.auth.mode="token"` 时，使用 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 当 `gateway.auth.mode="password"` 时，使用 `gateway.auth.password`（或 `OPENCLAW_GATEWAY_PASSWORD`）。

## 选择代理

无需自定义头：在 OpenResponses 的 `model` 字段中编码代理 ID：

- `model: "openclaw:<agentId>"`（示例：`"openclaw:main"`，`"openclaw:beta"`）
- `model: "agent:<agentId>"`（别名）

或通过头指定特定的 OpenClaw 代理：

- `x-openclaw-agent-id: <agentId>`（默认：`main`）

高级用法：

- `x-openclaw-session-key: <sessionKey>` 以完全控制会话路由。

## 启用接口

将 `gateway.http.endpoints.responses.enabled` 设置为 `true`：

```json5
{
  gateway: {
    http: {
      endpoints: {
        responses: { enabled: true },
      },
    },
  },
}
```

## 禁用接口

将 `gateway.http.endpoints.responses.enabled` 设置为 `false`：

```json5
{
  gateway: {
    http: {
      endpoints: {
        responses: { enabled: false },
      },
    },
  },
}
```

## 会话行为

默认情况下，该接口是**无状态的**（每次调用生成新的会话密钥）。

如果请求包含 OpenResponses 的 `user` 字符串，网关会从该字符串推导出稳定的会话密钥，因此重复调用可以共享代理会话。

## 请求格式（支持）

请求遵循 OpenResponses API 的基于项的输入。当前支持：

- `input`：字符串或项对象数组。
- `instructions`：合并到系统提示中。
- `tools`：客户端工具定义（函数工具）。
- `tool_choice`：过滤或要求客户端工具。
- `stream`：启用 SSE 流式传输。
- `max_output_tokens`：最佳努力输出限制（取决于提供方）。
- `user`：稳定会话路由。

接受但**当前忽略**：

- `max_tool_calls`
- `reasoning`
- `metadata`
- `store`
- `previous_response_id`
- `truncation`

## 项（输入）

### `message`

角色：`system`、`developer`、`user`、`assistant`。

- `system` 和 `developer` 会附加到系统提示中。
- 最近的 `user` 或 `function_call_output` 项成为“当前消息”。
- 更早的用户/助手消息作为上下文历史包含。

### `function_call_output`（回合制工具）

将工具结果返回给模型：

```json
{
  "type": "function_call_output",
  "call_id": "call_123",
  "output": "{\"temperature\": \"72F\"}"
}
```

### `reasoning` 和 `item_reference`

为兼容性接受，但在构建提示时忽略。

## 工具（客户端函数工具）

通过 `tools: [{ type: "function", function: { name, description?, parameters? } }]` 提供工具。

如果代理决定调用工具，响应会返回一个 `function_call` 输出项。然后您发送一个带有 `function_call_output` 的后续请求以继续回合。

## 图像（`input_image`）

支持 base64 或 URL 源：

```json
{
  "type": "input_image",
  "source": { "type": "url", "url": "https://example.com/image.png" }
}
```

允许的 MIME 类型（当前）：`image/jpeg`、`image/png`、`image/gif`、`image/webp`。
最大尺寸（当前）：10MB。

## 文件（`input_file`）

支持 base64 或 URL 源：

```json
{
  "type": "input_file",
  "source": {
    "type": "base64",
    "media_type": "text/plain",
    "data": "SGVsbG8gV29ybGQh",
    "filename": "hello.txt"
  }
}
```

允许的 MIME 类型（当前）：`text/plain`、`text/markdown`、`text/html`、`text/csv`、
`application/json`、`application/pdf`。

最大尺寸（当前）：5MB。

当前行为：

- 文件内容会被解码并添加到**系统提示**中，而不是用户消息，
  因此它保持临时性（不持久化到会话历史）。
- PDF 会被解析为文本。如果找到的文本很少，前几页会被栅格化为图像
  并传递给模型。

PDF 解析使用 Node 友好的 `pdfjs-dist` 旧版构建（无 worker）。现代 PDF.js 构建期望浏览器 worker/DOM 全局变量，因此在网关中未使用。

URL 获取默认值：

- `files.allowUrl`: `true`
- `images.allowUrl`: `true`
- 请求受保护（DNS 解析、私有 IP 阻止、重定向限制、超时）。

## 文件 + 图像限制（配置）

默认值可以在 `gateway.http.endpoints.responses` 下调整：

```json5
{
  gateway: {
    http: {
      endpoints: {
        responses: {
          enabled: true,