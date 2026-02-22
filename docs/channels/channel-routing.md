---
summary: "Routing rules per channel (WhatsApp, Telegram, Discord, Slack) and shared context"
read_when:
  - Changing channel routing or inbox behavior
title: "Channel Routing"
---
# 通道与路由

OpenClaw 将回复**发送到消息来源的通道**。模型不会选择通道；路由是确定性的，并由主机配置控制。

## 关键术语

- **通道**: `whatsapp`, `telegram`, `discord`, `slack`, `signal`, `imessage`, `webchat`.
- **AccountId**: 每个通道的账户实例（当支持时）。
- **AgentId**: 独立的工作区 + 会话存储（“大脑”）。
- **SessionKey**: 用于存储上下文和控制并发的桶键。

## 会话键形状（示例）

直接消息合并到代理的**主**会话：

- `agent:<agentId>:<mainKey>` （默认：`agent:main:main`）

群组和通道按通道保持隔离：

- 群组：`agent:<agentId>:<channel>:group:<id>`
- 通道/房间：`agent:<agentId>:<channel>:channel:<id>`

线程：

- Slack/Discord 线程在基础键后附加 `:thread:<threadId>`。
- Telegram 论坛主题在群组键中嵌入 `:topic:<topicId>`。

示例：

- `agent:main:telegram:group:-1001234567890:topic:42`
- `agent:main:discord:channel:123456:thread:987654`

## 路由规则（如何选择代理）

路由为每个传入消息选择**一个代理**：

1. **精确对等匹配** (`bindings` 与 `peer.kind` + `peer.id`)。
2. **父对等匹配**（线程继承）。
3. **公会 + 角色匹配**（Discord）通过 `guildId` + `roles`。
4. **公会匹配**（Discord）通过 `guildId`。
5. **团队匹配**（Slack）通过 `teamId`。
6. **账户匹配**（通道上的 `accountId`）。
7. **通道匹配**（该通道上的任何账户，`accountId: "*"`）。
8. **默认代理** (`agents.list[].default`，否则列表中的第一个条目，回退到 `main`)。

当绑定包含多个匹配字段 (`peer`, `guildId`, `teamId`, `roles`) 时，**所有提供的字段必须匹配**才能应用该绑定。

匹配的代理决定了使用哪个工作区和会话存储。

## 广播组（运行多个代理）

广播组允许你在 OpenClaw 通常会回复的情况下为同一对等体运行**多个代理**（例如：在 WhatsApp 群组中，在提及/激活门控之后）。

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

参见：[广播组](/channels/broadcast-groups)。

## 配置概述

- `agents.list`: 命名代理定义（工作区、模型等）。
- `bindings`: 将传入的通道/账户/对等体映射到代理。

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
- JSONL 对话记录与存储并存

你可以通过 `session.store` 和 `{agentId}` 模板化覆盖存储路径。

## WebChat 行为

WebChat 连接到**选定的代理**，默认使用代理的主会话。因此，WebChat 允许你在一个地方查看该代理的跨通道上下文。

## 回复上下文

传入的回复包括：

- 当可用时，包括 `ReplyToId`, `ReplyToBody`, 和 `ReplyToSender`。
- 引用的上下文作为 `[Replying to ...]` 块附加到 `Body`。

这在所有通道中保持一致。