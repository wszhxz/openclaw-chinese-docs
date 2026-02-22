---
summary: "Webhook ingress for wake and isolated agent runs"
read_when:
  - Adding or changing webhook endpoints
  - Wiring external systems into OpenClaw
title: "Webhooks"
---
# Webhooks

Gateway 可以暴露一个小的 HTTP webhook 端点供外部触发。

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

注意事项：

- 当 `hooks.enabled=true` 时，`hooks.token` 是必需的。
- `hooks.path` 默认为 `/hooks`。

## 认证

每个请求必须包含 hook token。建议使用头部信息：

- `Authorization: Bearer <token>` （推荐）
- `x-openclaw-token: <token>`
- 查询字符串中的 token 将被拒绝 (`?token=...` 返回 `400`)。

## 端点

### `POST /hooks/wake`

负载：

```json
{ "text": "System line", "mode": "now" }
```

- `text` **必需** (字符串): 事件的描述（例如，“收到新邮件”）。
- `mode` 可选 (`now` | `next-heartbeat`)：是否立即触发心跳（默认 `now`）或等待下一次定期检查。

效果：

- 为主会话排队一个系统事件
- 如果 `mode=now`，触发立即心跳

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

- `message` **必需** (字符串): 代理处理的提示或消息。
- `name` 可选 (字符串): hook 的人类可读名称（例如，“GitHub”），在会话摘要中用作前缀。
- `agentId` 可选 (字符串): 将此 hook 路由到特定代理。未知 ID 回退到默认代理。设置后，hook 使用解析后的代理的工作区和配置运行。
- `sessionKey` 可选 (字符串): 用于标识代理会话的键。默认情况下，除非 `hooks.allowRequestSessionKey=true`，否则此字段会被拒绝。
- `wakeMode` 可选 (`now` | `next-heartbeat`)：是否立即触发心跳（默认 `now`）或等待下一次定期检查。
- `deliver` 可选 (布尔值): 如果 `true`，代理的响应将发送到消息通道。默认为 `true`。仅心跳确认的响应会自动跳过。
- `channel` 可选 (字符串): 交付的消息通道。选项包括：`last`, `whatsapp`, `telegram`, `discord`, `slack`, `mattermost` (插件), `signal`, `imessage`, `msteams`。默认为 `last`。
- `to` 可选 (字符串): 通道的接收者标识符（例如，WhatsApp/Signal 的电话号码，Telegram 的聊天 ID，Discord/Slack/Mattermost (插件) 的频道 ID，MS Teams 的对话 ID）。默认为主会话的最后一个接收者。
- `model` 可选 (字符串): 模型覆盖（例如，`anthropic/claude-3-5-sonnet` 或别名）。如果受限，必须在允许的模型列表中。
- `thinking` 可选 (字符串): 思考级别覆盖（例如，`low`, `medium`, `high`）。
- `timeoutSeconds` 可选 (数字): 代理运行的最大持续时间（秒）。

效果：

- 运行一个 **隔离** 的代理回合（自己的会话键）
- 始终在 **主** 会话中发布摘要
- 如果 `wakeMode=now`，触发立即心跳

## 会话键策略（重大变更）

默认情况下，禁用 `/hooks/agent` 负载 `sessionKey` 覆盖。

- 推荐：设置一个固定的 `hooks.defaultSessionKey` 并关闭请求覆盖。
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

兼容性配置（旧行为）：

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

### `POST /hooks/<name>` (映射)

自定义 hook 名称通过 `hooks.mappings` 解析（参见配置）。映射可以
将任意负载转换为 `wake` 或 `agent` 操作，带有可选模板或
代码转换。

映射选项（摘要）：

- `hooks.presets: ["gmail"]` 启用内置的 Gmail 映射。
- `hooks.mappings` 允许你在配置中定义 `match`, `action` 和模板。
- `hooks.transformsDir` + `transform.module` 加载一个 JS/TS 模块以实现自定义逻辑。
  - 如果设置了 `hooks.transformsDir`，它必须位于你的 OpenClaw 配置目录下的 transforms 根目录下（通常是 `~/.openclaw/hooks/transforms`）。
  - `transform.module` 必须在有效的 transforms 目录内解析（拒绝遍历/转义路径）。
- 使用 `match.source` 保持一个通用的摄取端点（负载驱动路由）。
- TS 转换需要一个 TS 加载器（例如 `bun` 或 `tsx`）或预编译的 `.js` 在运行时。
- 在映射上设置 `deliver: true` + `channel`/`to` 以将回复路由到聊天界面
  (`channel` 默认为 `last` 并回退到 WhatsApp)。
- `agentId` 将 hook 路由到特定代理；未知 ID 回退到默认代理。
- `hooks.allowedAgentIds` 限制显式 `agentId` 路由。省略它（或包含 `*`）以允许任何代理。设置 `[]` 以拒绝显式 `agentId` 路由。
- `hooks.defaultSessionKey` 设置 hook 代理运行的默认会话，如果没有提供显式键。
- `hooks.allowRequestSessionKey` 控制 `/hooks/agent` 负载是否可以设置 `sessionKey`（默认：`false`）。
- `hooks.allowedSessionKeyPrefixes` 可选地限制来自请求负载和映射的显式 `sessionKey` 值。
- `allowUnsafeExternalContent: true` 禁用该 hook 的外部内容安全包装器
  （危险；仅用于受信任的内部源）。
- `openclaw webhooks gmail setup` 为 `openclaw webhooks gmail run` 写入 `hooks.gmail` 配置。
  有关完整的 Gmail watch 流，请参阅 [Gmail Pub/Sub](/automation/gmail-pubsub)。

## 响应

- `200` 对于 `/hooks/wake`
- `202` 对于 `/hooks/agent`（异步运行已启动）
- `401` 在认证失败时
- `429` 在同一客户端多次认证失败后（检查 `Retry-After`）
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

在代理负载（或映射）中添加 `model` 以覆盖该运行的模型：

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'x-openclaw-token: SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","model":"openai/gpt-5.2-mini"}'
```

如果你强制执行 `agents.defaults.models`，请确保覆盖模型包含在其中。

```bash
curl -X POST http://127.0.0.1:18789/hooks/gmail \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"source":"gmail","messages":[{"from":"Ada","subject":"Hello","snippet":"Hi"}]}'
```

## 安全

- 将 hook 端点置于回环、tailnet 或受信任的反向代理之后。
- 使用专用的 hook token；不要重用网关认证 token。
- 按客户端地址对重复认证失败进行速率限制以减缓暴力破解尝试。
- 如果你使用多代理路由，请设置 `hooks.allowedAgentIds` 以限制显式 `agentId` 选择。
- 除非你需要调用者选择的会话，否则保留 `hooks.allowRequestSessionKey=false`。
- 如果你启用请求 `sessionKey`，请限制 `hooks.allowedSessionKeyPrefixes`（例如，`["hook:"]`）。
- 避免在 webhook 日志中包含敏感的原始负载。
- 默认情况下，hook 负载被视为不受信任并用安全边界包裹。
  如果你必须为特定 hook 禁用此功能，请在该 hook 的映射中设置 `allowUnsafeExternalContent: true`
  （危险）。