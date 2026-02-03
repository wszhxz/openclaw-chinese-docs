---
summary: "Webhook ingress for wake and isolated agent runs"
read_when:
  - Adding or changing webhook endpoints
  - Wiring external systems into OpenClaw
title: "Webhooks"
---
# Webhook

网关可以暴露一个小型的 HTTP Webhook 端点以供外部触发。

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

说明：

- `hooks.token` 在 `hooks.enabled=true` 时是必需的。
- `hooks.path` 默认为 `/hooks`。

## 认证

每个请求必须包含 Hook Token。建议使用以下头部：

- `Authorization: Bearer <token>`（推荐）
- `x-openclaw-token: <token>`
- `?token=<token>`（已弃用；会记录警告并在未来主要版本中移除）

## 端点

### `POST /hooks/wake`

载荷：

```json
{ "text": "系统行", "mode": "now" }
```

- `text` **必需**（字符串）：事件的描述（例如："新邮件收到"）。
- `mode` 可选（`now` | `next-heartbeat`）：是否立即触发心跳（默认 `now`）或等待下一次周期性检查。

效果：

- 将系统事件入队到 **主会话**
- 如果 `mode=now`，立即触发心跳

### `POST /hooks/agent`

载荷：

```json
{
  "message": "运行此操作",
  "name": "邮件",
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

- `message` **必需**（字符串）：代理处理的提示或消息。
- `name` 可选（字符串）：钩子的可读名称（例如："GitHub"），用于会话摘要中的前缀。
- `sessionKey` 可选（字符串）：用于标识代理会话的键。默认为随机的 `hook:<uuid>`。使用一致的键可在钩子上下文中实现多轮对话。
- `wakeMode` 可选（`now` | `next-heartbeat`）：是否立即触发心跳（默认 `now`）或等待下一次周期性检查。
- `deliver` 可选（布尔值）：如果为 `true`，代理的响应将发送到消息通道。默认为 `true`。仅心跳确认的响应将自动跳过。
- `channel` 可选（字符串）：用于交付的消息通道。可选值包括：`last`、`whatsapp`、`telegram`、`discord`、`slack`、`mattermost`（插件）、`signal`、`imessage`、`msteams`。默认为 `last`。
- `to` 可选（字符串）：通道的接收者标识符（例如：WhatsApp/Signal 的电话号码、Telegram 的聊天 ID、Discord/Slack/Mattermost（插件）的频道 ID、MS Teams 的对话 ID）。默认为主会话的最后一个接收者。
- `model` 可选（字符串）：模型覆盖（例如：`anthropic/claude-3-5-sonnet` 或别名）。如果受限，必须在允许的模型列表中。
- `thinking` 可选（字符串）：思考级别覆盖（例如：`low`、`medium`、`high`）。
- `timeoutSeconds` 可选（数字）：代理运行的最大持续时间（以秒为单位）。

效果：

- 运行一个 **隔离的** 代理回合（自己的会话键）
- 始终将摘要发布到 **主会话**
- 如果 `wakeMode=now`，立即触发心跳

### `POST /hooks/<name>`（映射）

自定义钩子名称通过 `hooks.mappings` 解析（参见配置）。映射可以将任意载荷转换为 `wake` 或 `agent` 操作，可选模板或代码转换。

映射选项（摘要）：

- `hooks.presets: ["gmail"]` 启用内置的 Gmail 映射。
- `hooks.mappings` 允许你在配置中定义 `match`、`action` 和模板。
- `hooks.transformsDir` + `transform.module` 加载 JS/TS 模块以实现自定义逻辑。
- 使用 `match.source` 保留通用的接收端点（基于载荷的路由）。
- TS 转换需要 TS 加载器（例如 `bun` 或 `tsx`）或运行时预编译的 `.js`。
- 在映射中设置 `deliver: true` + `channel`/`to` 可以将回复路由到聊天界面（`channel` 默认为 `last`，若未设置则回退到 WhatsApp）。
- `allowUnsafeExternalContent: true` 禁用该钩子的外部内容安全包装器（危险；仅限受信任的内部源）。
- `openclaw webhooks gmail setup` 为 `openclaw webhooks gmail run` 写入 `hooks.gmail` 配置。查看 [Gmail Pub/Sub](/automation/gmail-pubsub) 以了解完整的 Gmail 监听流程。

## 响应

- `/hooks/wake` 返回 `200`
- `/hooks/agent` 返回 `202`（异步运行已启动）
- 认证失败返回 `401`
- 无效载荷返回 `400`
- 载荷过大返回 `413`

## 示例

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"text":"新邮件收到","mode":"now"}'
```

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'x-openclaw-token: SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"总结收件箱","name":"Email","wakeMode":"next-heartbeat"}'
```

### 使用不同的模型

在代理载荷（或映射）中添加 `model` 以覆盖该运行的模型：

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'x-openclaw-token: SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"总结收件箱","name":"Email","model":"openai/gpt