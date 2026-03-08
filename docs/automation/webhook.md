---
summary: "Webhook ingress for wake and isolated agent runs"
read_when:
  - Adding or changing webhook endpoints
  - Wiring external systems into OpenClaw
title: "Webhooks"
---
# Webhooks

Gateway 可暴露一个小型 HTTP webhook 端点以供外部触发。

## 启用

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
    // Optional: restrict explicit `agentId` routing to this allowlist.
    // Omit or include "*" to allow any agent.
    // Set [] to deny all explicit `agentId` routing.
    allowedAgentIds: ["hooks", "main"],
  },
}
```

注意：

- 当 `hooks.enabled=true` 时，`hooks.token` 是必需的。
- `hooks.path` 默认为 `/hooks`。

## 认证

每个请求都必须包含钩子令牌。优先使用头部：

- `Authorization: Bearer <token>`（推荐）
- `x-openclaw-token: <token>`
- 查询字符串令牌会被拒绝（`?token=...` 返回 `400`）。

## 端点

### `POST /hooks/wake`

负载：

```json
{ "text": "System line", "mode": "now" }
```

- `text` **必需** (string): 事件的描述（例如："收到新邮件"）。
- `mode` 可选 (`now` | `next-heartbeat`): 是否触发即时心跳（默认 `now`）或等待下一次定期检查。

效果：

- 为 **main** 会话排队系统事件
- 如果 `mode=now`，则触发即时心跳

### `POST /hooks/agent`

负载：

```json
{
  "message": "Run this",
  "name": "Email",
  "agentId": "hooks",
  "sessionKey": "hook:email:msg-123",
  "wakeMode": "now",
  "deliver": true,
  "channel": "last",
  "to": "+15551234567",
  "model": "openai/gpt-5.2-mini",
  "thinking": "low",
  "timeoutSeconds": 120
}
```

- `message` **必需** (string): 供 Agent 处理的消息或提示。
- `name` 可选 (string): 钩子的人类可读名称（例如："GitHub"），用作会话摘要中的前缀。
- `agentId` 可选 (string): 将此钩子路由到特定 Agent。未知 ID 回退到默认 Agent。设置后，钩子使用解析出的 Agent 的工作区和配置运行。
- `sessionKey` 可选 (string): 用于标识 Agent 会话的键。默认情况下，除非 `hooks.allowRequestSessionKey=true`，否则此字段被拒绝。
- `wakeMode` 可选 (`now` | `next-heartbeat`): 是否触发即时心跳（默认 `now`）或等待下一次定期检查。
- `deliver` 可选 (boolean): 如果 `true`，Agent 的响应将发送到消息通道。默认为 `true`。仅作为心跳确认的响应将被自动跳过。
- `channel` 可选 (string): 用于交付的消息通道。其中之一：`last`, `whatsapp`, `telegram`, `discord`, `slack`, `mattermost`（Plugin）, `signal`, `imessage`, `msteams`。默认为 `last`。
- `to` 可选 (string): 通道的接收者标识符（例如：WhatsApp/Signal 的电话号码，Telegram 的聊天 ID，Discord/Slack/Mattermost（Plugin）的频道 ID，MS Teams 的对话 ID）。默认为主会话中的最后一名接收者。
- `model` 可选 (string): 模型覆盖（例如：`anthropic/claude-3-5-sonnet` 或别名）。如果受限，必须在允许的模型列表中。
- `thinking` 可选 (string): 思考级别覆盖（例如：`low`, `medium`, `high`）。
- `timeoutSeconds` 可选 (number): Agent 运行的最大持续时间（秒）。

效果：

- 运行一个 **isolated** Agent 回合（独立会话键）
- 始终将摘要发布到 **main** 会话
- 如果 `wakeMode=now`，则触发即时心跳

## 会话密钥策略（破坏性变更）

`/hooks/agent` 负载 `sessionKey` 覆盖功能默认禁用。

- 推荐：设置固定的 `hooks.defaultSessionKey` 并保持请求覆盖关闭。
- 可选：仅在需要时允许请求覆盖，并限制前缀。

推荐配置：

```json5
{
  hooks: {
    enabled: true,
    token: "${OPENCLAW_HOOKS_TOKEN}",
    defaultSessionKey: "hook:ingress",
    allowRequestSessionKey: false,
    allowedSessionKeyPrefixes: ["hook:"],
  },
}
```

兼容性配置（旧版行为）：

```json5
{
  hooks: {
    enabled: true,
    token: "${OPENCLAW_HOOKS_TOKEN}",
    allowRequestSessionKey: true,
    allowedSessionKeyPrefixes: ["hook:"], // strongly recommended
  },
}
```

### `POST /hooks/<name>`（已映射）

自定义钩子名称通过 `hooks.mappings` 解析（参见配置）。映射可以将任意负载转换为 `wake` 或 `agent` 操作，并支持可选模板或代码转换。

映射选项（摘要）：

- `hooks.presets: ["gmail"]` 启用内置的 Gmail 映射。
- `hooks.mappings` 允许您在配置中定义 `match`, `action` 和模板。
- `hooks.transformsDir` + `transform.module` 加载 JS/TS 模块以用于自定义逻辑。
  - `hooks.transformsDir`（如果设置）必须位于您的 OpenClaw 配置目录下的 transforms 根目录下（通常为 `~/.openclaw/hooks/transforms`）。
  - `transform.module` 必须在有效的 transforms 目录内解析（遍历/逃逸路径将被拒绝）。
- 使用 `match.source` 保留通用摄入端点（基于负载的路由）。
- TS 转换需要 TS 加载器（例如 `bun` 或 `tsx`）或运行时预编译的 `.js`。
- 在映射上设置 `deliver: true` + `channel`/`to` 以将回复路由到聊天界面
  （`channel` 默认为 `last` 并回退到 WhatsApp）。
- `agentId` 将钩子路由到特定 Agent；未知 ID 回退到默认 Agent。
- `hooks.allowedAgentIds` 限制显式 `agentId` 路由。省略它（或包含 `*`）以允许任何 Agent。设置 `[]` 以拒绝显式 `agentId` 路由。
- `hooks.defaultSessionKey` 设置钩子 Agent 运行的默认会话，当未提供显式键时。
- `hooks.allowRequestSessionKey` 控制 `/hooks/agent` 负载是否可以设置 `sessionKey`（默认：`false`）。
- `hooks.allowedSessionKeyPrefixes` 可选择性地限制来自请求负载和映射的显式 `sessionKey` 值。
- `allowUnsafeExternalContent: true` 禁用该钩子的外部内容安全包装
  （危险；仅用于受信任的内部源）。
- `openclaw webhooks gmail setup` 为 `openclaw webhooks gmail run` 写入 `hooks.gmail` 配置。
  有关完整的 Gmail 监控流程，请参阅 [Gmail Pub/Sub](/automation/gmail-pubsub)。

## 响应

- `200` 对应 `/hooks/wake`
- `200` 对应 `/hooks/agent`（接受异步运行）
- `401` 在认证失败时
- `429` 在来自同一客户端的重复认证失败后（检查 `Retry-After`）
- `400` 在无效负载时
- `413` 在负载过大时

## 示例

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"text":"New email received","mode":"now"}'
```

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'x-openclaw-token: SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","wakeMode":"next-heartbeat"}'
```

### 使用不同的模型

将 `model` 添加到 Agent 负载（或映射）中以覆盖该运行的模型：

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'x-openclaw-token: SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","model":"openai/gpt-5.2-mini"}'
```

如果您强制要求 `agents.defaults.models`，请确保覆盖模型包含在其中。

```bash
curl -X POST http://127.0.0.1:18789/hooks/gmail \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"source":"gmail","messages":[{"from":"Ada","subject":"Hello","snippet":"Hi"}]}'
```

## 安全

- 将钩子端点置于回环、tailnet 或受信任的反向代理之后。
- 使用专用的钩子令牌；不要重用 Gateway 认证令牌。
- 重复的认证失败会按客户端地址进行速率限制，以减缓暴力破解尝试。
- 如果您使用多 Agent 路由，设置 `hooks.allowedAgentIds` 以限制显式 `agentId` 选择。
- 保持 `hooks.allowRequestSessionKey=false`，除非您需要调用者选择的会话。
- 如果您启用请求 `sessionKey`，请限制 `hooks.allowedSessionKeyPrefixes`（例如，`["hook:"]`）。
- 避免在 Webhook 日志中包含敏感的原始负载。
- 钩子负载默认被视为不可信，并带有安全边界包装。
  如果您必须针对特定钩子禁用此功能，请在该钩子的映射中设置 `allowUnsafeExternalContent: true`
  （危险）。