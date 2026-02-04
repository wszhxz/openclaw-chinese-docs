---
summary: "Webhook ingress for wake and isolated agent runs"
read_when:
  - Adding or changing webhook endpoints
  - Wiring external systems into OpenClaw
title: "Webhooks"
---
# Webhooks

Gateway 可以暴露一个小的 HTTP webhook 端点用于外部触发。

## 启用

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
  },
}
```

注意事项：

- 当 `hooks.enabled=true` 时，`hooks.token` 是必需的。
- `hooks.path` 默认为 `/hooks`。

## 认证

每个请求必须包含 hook token。建议使用头部信息：

- `Authorization: Bearer <token>`（推荐）
- `x-openclaw-token: <token>`
- `?token=<token>`（已弃用；记录警告并在未来的主要版本中移除）

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
- `sessionKey` 可选 (字符串): 用于标识代理会话的键。默认为随机 `hook:<uuid>`。使用一致的键允许在 hook 上下文中进行多轮对话。
- `wakeMode` 可选 (`now` | `next-heartbeat`)：是否立即触发心跳（默认 `now`）或等待下一次定期检查。
- `deliver` 可选 (布尔值): 如果 `true`，代理的响应将发送到消息通道。默认为 `true`。仅心跳确认的响应会自动跳过。
- `channel` 可选 (字符串): 发送消息的通道。可以是：`last`，`whatsapp`，`telegram`，`discord`，`slack`，`mattermost`（插件），`signal`，`imessage`，`msteams`。默认为 `last`。
- `to` 可选 (字符串): 通道的接收者标识符（例如，WhatsApp/Signal 的电话号码，Telegram 的聊天 ID，Discord/Slack/Mattermost（插件）的频道 ID，MS Teams 的对话 ID）。默认为主会话中的最后一个接收者。
- `model` 可选 (字符串): 模型覆盖（例如，`anthropic/claude-3-5-sonnet` 或别名）。如果受限，则必须在允许的模型列表中。
- `thinking` 可选 (字符串): 思考级别覆盖（例如，`low`，`medium`，`high`）。
- `timeoutSeconds` 可选 (数字): 代理运行的最大持续时间（秒）。

效果：

- 运行一个 **隔离** 的代理回合（自己的会话键）
- 始终在 **主** 会话中发布摘要
- 如果 `wakeMode=now`，触发立即心跳

### `POST /hooks/<name>`（映射）

自定义 hook 名称通过 `hooks.mappings` 解析（参见配置）。映射可以
将任意负载转换为 `wake` 或 `agent` 操作，带有可选模板或
代码转换。

映射选项（摘要）：

- `hooks.presets: ["gmail"]` 启用内置的 Gmail 映射。
- `hooks.mappings` 允许你在配置中定义 `match`，`action` 和模板。
- `hooks.transformsDir` + `transform.module` 加载一个 JS/TS 模块以实现自定义逻辑。
- 使用 `match.source` 保持一个通用的摄取端点（负载驱动路由）。
- TS 转换需要一个 TS 加载器（例如 `bun` 或 `tsx`）或运行时预编译的 `.js`。
- 在映射上设置 `deliver: true` + `channel`/`to` 以将回复路由到聊天界面
  (`channel` 默认为 `last` 并回退到 WhatsApp)。
- `allowUnsafeExternalContent: true` 禁用该 hook 的外部内容安全包装器
  （危险；仅适用于受信任的内部来源）。
- `openclaw webhooks gmail setup` 为 `openclaw webhooks gmail run` 写入 `hooks.gmail` 配置。
  请参阅 [Gmail Pub/Sub](/automation/gmail-pubsub) 获取完整的 Gmail 监视流。

## 响应

- `200` 对于 `/hooks/wake`
- `202` 对于 `/hooks/agent`（异步运行已启动）
- `401` 在认证失败时
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

## 安全性

- 将 hook 端点置于回环、tailnet 或受信任的反向代理之后。
- 使用专用的 hook token；不要重用网关认证 token。
- 避免在 webhook 日志中包含敏感的原始负载。
- 默认情况下，hook 负载被视为不可信，并用安全边界包裹。
  如果您必须为此特定 hook 禁用此功能，请在该 hook 的映射中设置 `allowUnsafeExternalContent: true`
  （危险）。