---
summary: "Webhook ingress for wake and isolated agent runs"
read_when:
  - Adding or changing webhook endpoints
  - Wiring external systems into OpenClaw
title: "Webhooks"
---
# Webhook

网关可以暴露一个小型 HTTP webhook 端点，用于外部触发。

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

- 当启用 `hooks.enabled=true` 时，必须配置 `hooks.token`。
- `hooks.path` 默认为 `/hooks`。

## 认证

每个请求都必须包含 hook token。推荐使用请求头方式传递：

- `Authorization: Bearer <token>`（推荐）
- `x-openclaw-token: <token>`
- 查询字符串中的 token 将被拒绝（`?token=...` 返回 `400`）。

## 端点

### `POST /hooks/wake`

请求体（Payload）：

```json
{ "text": "System line", "mode": "now" }
```

- `text` **必填**（字符串）：事件的描述（例如，“收到新邮件”）。
- `mode` 可选（`now` | `next-heartbeat`）：是否立即触发一次心跳（默认为 `now`），或等待下一次周期性检查。

效果：

- 将一条系统事件加入 **主** 会话队列
- 若启用了 `mode=now`，则立即触发一次心跳

### `POST /hooks/agent`

请求体（Payload）：

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

- `message` **必填**（字符串）：供 agent 处理的提示词或消息。
- `name` 可选（字符串）：该 hook 的人类可读名称（例如，“GitHub”），将作为会话摘要中的前缀使用。
- `agentId` 可选（字符串）：将此 hook 路由至指定 agent。未知 ID 将回退至默认 agent。设置后，该 hook 将使用已解析 agent 的工作区与配置运行。
- `sessionKey` 可选（字符串）：用于标识 agent 会话的密钥。默认情况下，除非启用 `hooks.allowRequestSessionKey=true`，否则该字段将被拒绝。
- `wakeMode` 可选（`now` | `next-heartbeat`）：是否立即触发一次心跳（默认为 `now`），或等待下一次周期性检查。
- `deliver` 可选（布尔值）：若设为 `true`，agent 的响应将发送至消息通道。默认为 `true`。仅含心跳确认的响应将自动跳过。
- `channel` 可选（字符串）：响应投递所用的消息通道。可选值包括：`last`、`whatsapp`、`telegram`、`discord`、`slack`、`mattermost`（插件）、`signal`、`imessage`、`msteams`。默认为 `last`。
- `to` 可选（字符串）：通道的接收方标识符（例如，WhatsApp/Signal 使用手机号，Telegram 使用 chat ID，Discord/Slack/Mattermost（插件）使用 channel ID，MS Teams 使用 conversation ID）。默认为 **主** 会话中最近一次的接收方。
- `model` 可选（字符串）：模型覆盖（例如 `anthropic/claude-3-5-sonnet` 或别名）。若启用了模型限制，则该模型必须在允许列表中。
- `thinking` 可选（字符串）：推理层级覆盖（例如 `low`、`medium`、`high`）。
- `timeoutSeconds` 可选（数字）：agent 运行的最大持续时间（单位：秒）。

效果：

- 执行一次 **隔离式** agent 轮次（拥有独立的会话密钥）
- 始终向 **主** 会话中发布摘要
- 若启用了 `wakeMode=now`，则立即触发一次心跳

## 会话密钥策略（破坏性变更）

默认禁用 `/hooks/agent` 请求体中的 `sessionKey` 覆盖功能。

- 推荐做法：设定固定的 `hooks.defaultSessionKey`，并关闭请求级覆盖。
- 可选做法：仅在必要时启用请求覆盖，并限制其前缀。

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

兼容性配置（沿用旧行为）：

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

### `POST /hooks/<name>`（映射）

自定义 hook 名称通过 `hooks.mappings` 解析（参见配置说明）。映射机制可将任意请求体转换为 `wake` 或 `agent` 动作，并支持可选模板或代码转换。

映射选项概览：

- `hooks.presets: ["gmail"]` 启用内置 Gmail 映射。
- `hooks.mappings` 允许你在配置中定义 `match`、`action` 和模板。
- `hooks.transformsDir` + `transform.module` 加载 JS/TS 模块以实现自定义逻辑。
  - 若设置了 `hooks.transformsDir`，其路径必须位于 OpenClaw 配置目录下的 transforms 根目录内（通常为 `~/.openclaw/hooks/transforms`）。
  - `transform.module` 必须能从实际生效的 transforms 目录中解析（禁止路径遍历或逃逸）。
- 使用 `match.source` 可保留一个通用的数据接入端点（基于请求体内容进行路由）。
- TS 转换需依赖 TS 加载器（例如 `bun` 或 `tsx`），或在运行时提供预编译的 `.js`。
- 在映射中设置 `deliver: true` + `channel`/`to`，可将回复路由至聊天界面。
  - `channel` 默认为 `last`，若未配置则回退至 WhatsApp。
- `agentId` 将该 hook 路由至特定 agent；未知 ID 将回退至默认 agent。
- `hooks.allowedAgentIds` 限制显式的 `agentId` 路由。如需允许任意 agent，请省略该字段或包含 `*`；设置 `[]` 则禁止显式的 `agentId` 路由。
- `hooks.defaultSessionKey` 设置当未提供显式密钥时，hook agent 运行所使用的默认会话。
- `hooks.allowRequestSessionKey` 控制 `/hooks/agent` 请求体是否允许设置 `sessionKey`（默认：`false`）。
- `hooks.allowedSessionKeyPrefixes` 可选地限制请求体和映射中显式的 `sessionKey` 值。
- `allowUnsafeExternalContent: true` 为该 hook 禁用外部内容安全包装器（危险；仅适用于可信的内部来源）。
- `openclaw webhooks gmail setup` 为 `openclaw webhooks gmail run` 写入 `hooks.gmail` 配置。
  完整的 Gmail watch 流程请参阅 [Gmail Pub/Sub](/automation/gmail-pubsub)。

## 响应

- `200` 表示 `/hooks/wake`
- `200` 表示 `/hooks/agent`（异步运行已接受）
- `401` 表示认证失败
- `429` 表示同一客户端重复认证失败后（请检查 `Retry-After`）
- `400` 表示请求体无效
- `413` 表示请求体过大

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

### 使用不同模型

在 agent 请求体（或映射）中添加 `model`，即可为本次运行覆盖模型：

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'x-openclaw-token: SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","model":"openai/gpt-5.2-mini"}'
```

若你启用了 `agents.defaults.models`，请确保覆盖所用模型已包含在该列表中。

```bash
curl -X POST http://127.0.0.1:18789/hooks/gmail \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"source":"gmail","messages":[{"from":"Ada","subject":"Hello","snippet":"Hi"}]}'
```

## 安全

- 将 webhook 端点置于回环地址（loopback）、Tailnet 或受信任的反向代理之后。
- 使用专用的 webhook token；切勿复用网关认证 token。
- 对来自同一客户端地址的重复认证失败行为实施速率限制，以减缓暴力破解尝试。
- 若使用多 agent 路由，请设置 `hooks.allowedAgentIds`，以限制显式的 `agentId` 选择。
- 除非需要调用方指定会话，否则请保持 `hooks.allowRequestSessionKey=false` 关闭。
- 若启用请求级 `sessionKey`，请限制 `hooks.allowedSessionKeyPrefixes`（例如，限定为 `["hook:"]`）。
- 避免在 webhook 日志中记录敏感的原始请求体。
- webhook 请求体默认被视为不可信内容，并自动包裹安全边界。
  若确需为某个特定 webhook 禁用该机制，请在该 webhook 的映射中设置 `allowUnsafeExternalContent: true`（危险操作）。