---
summary: "Routing rules per channel (WhatsApp, Telegram, Discord, Slack) and shared context"
read_when:
  - Changing channel routing or inbox behavior
title: "Channel Routing"
---
# 通道与路由

OpenClaw 会将回复**路由回消息来源的通道**。模型不会选择通道；路由是确定性的，并由主机配置控制。

## 关键术语

- **通道**：`whatsapp`、`telegram`、`discord`、`slack`、`signal`、`imessage`、`webchat`。
- **AccountId**：每个通道的账户实例（当支持时）。
- **AgentId**：一个隔离的工作区 + 会话存储（“大脑”）。
- **SessionKey**：用于存储上下文和控制并发的桶键。

## SessionKey 格式（示例）

直接消息会合并到代理的**主会话**：

- `agent:<agentId>:<mainKey>`（默认：`agent:main:main`）

群组和通道保持按通道隔离：

- 群组：`agent:<agentId>:<channel>:group:<id>`
- 通道/房间：`agent:<agentId>:<channel>:channel:<id>`

线程：

- Slack/Discord 线程会在基础键后附加 `:thread:<threadId>`。
- Telegram 论坛主题会在群组键中嵌入 `:topic:<topicId>`。

示例：

- `agent:main:telegram:group:-1001234567890:topic:42`
- `agent:main:discord:channel:123456:thread:987654`

## 路由规则（如何选择代理）

每条入站消息会选择**一个代理**：

1. **精确对等匹配**（通过 `peer.kind` + `peer.id` 的 `bindings`）。
2. **公会匹配**（Discord）通过 `guildId`。
3. **团队匹配**（Slack）通过 `teamId`。
4. **账户匹配**（通道上的 `accountId`）。
5. **通道匹配**（该通道上的任意账户）。
6. **默认代理**（`agents.list[].default`，否则使用列表中的第一个条目，回退到 `main`）。

匹配的代理决定了使用哪个工作区和会话存储。

## 广播群组（运行多个代理）

广播群组允许在 OpenClaw 通常会回复的情况下为同一对等体**运行多个代理**（例如：在 WhatsApp 群组中，提及/激活后）。

配置：

```json5
{
  broadcast: {
    strategy: "parallel",
    "120363403215116621@g.us": ["alfred", "baerbel"],
    "+15555550123": ["support", "logger"],
  },
}
```

参见：[广播群组](/broadcast-groups)。

## 配置概览

- `agents.list`：命名的代理定义（工作区、模型等）。
- `bindings`：将入站通道/账户/对等体映射到代理。

示例：

```json5
{
  agents: {
    list: [{ id: "support", name: "Support", workspace: "~/.openclaw/workspace-support" }],
  },
  bindings: [
    { match: { channel: "slack", teamId: "T123" }, agentId: "support" },
    { match: { channel: "telegram", peer: { kind: "group", id: "-100123" } }, agentId: "support" },
  ],
}
```

## 会话存储

会话存储位于状态目录下（默认 `~/.openclaw`）：

- `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- JSONL 录音文件与存储文件位于同一目录

您可以通过 `session.store` 和 `{agentId}` 模板覆盖存储路径。

## WebChat 行为

WebChat 会连接到**选定的代理**，并默认使用代理的主会话。因此，WebChat 允许您在一个地方查看该代理的**跨通道上下文**。

## 回复上下文

入站回复包含：

- 当可用时，`ReplyToId`、`ReplyToBody` 和 `ReplyToSender`。
- 引用上下文会作为 `[Replying to ...]` 块附加到 `Body`。

这在所有通道中保持一致。