---
summary: "Routing rules per channel (WhatsApp, Telegram, Discord, Slack) and shared context"
read_when:
  - Changing channel routing or inbox behavior
title: "Channel Routing"
---
# 通道与路由

OpenClaw 将回复 **路由回消息来源的通道**。模型不选择通道；路由是确定性的，由主机配置控制。

## 关键术语

- **Channel**: `telegram`, `whatsapp`, `discord`, `irc`, `googlechat`, `slack`, `signal`, `imessage`, `line`, 以及扩展通道。`webchat` 是内部 WebChat UI 通道，不是可配置的外发通道。
- **AccountId**: 每通道账户实例（如支持）。
- 可选通道默认账户：当外发路径未指定 `accountId` 时，`channels.<channel>.defaultAccount` 选择使用的账户。
  - 在多账户设置中，当配置了两个或更多账户时，请设置明确的默认值（`defaultAccount` 或 `accounts.default`）。如果没有设置，回退路由可能会选择第一个标准化后的账户 ID。
- **AgentId**: 隔离的工作区 + 会话存储（“大脑”）。
- **SessionKey**: 用于存储上下文和控制并发的桶键。

## 会话键形状（示例）

直接消息合并到代理的 **主** 会话：

- `agent:<agentId>:<mainKey>`（默认值：`agent:main:main`）

群组和通道按通道保持隔离：

- 群组：`agent:<agentId>:<channel>:group:<id>`
- 通道/房间：`agent:<agentId>:<channel>:channel:<id>`

线程：

- Slack/Discord 线程在基础键后追加 `:thread:<threadId>`。
- Telegram 论坛主题在群组键中嵌入 `:topic:<topicId>`。

示例：

- `agent:main:telegram:group:-1001234567890:topic:42`
- `agent:main:discord:channel:123456:thread:987654`

## 主 DM 路由固定

当 `session.dmScope` 为 `main` 时，直接消息可能共享一个主会话。为防止会话的 `lastRoute` 被非所有者 DM 覆盖，当满足以下条件时，OpenClaw 从 `allowFrom` 推断固定的所有者：

- `allowFrom` 恰好有一个非通配符条目。
- 该条目可以归一化为该通道的具体发送者 ID。
- 传入 DM 发送者与那个固定的所有者不匹配。

在不匹配的情况下，OpenClaw 仍会记录传入会话元数据，但会跳过更新主会话 `lastRoute`。

## 路由规则（如何选择代理）

路由为每条传入消息选择 **一个代理**：

1. **精确对等匹配**（`bindings` 配合 `peer.kind` + `peer.id`）。
2. **父级对等匹配**（线程继承）。
3. **公会 + 角色匹配**（Discord）通过 `guildId` + `roles`。
4. **公会匹配**（Discord）通过 `guildId`。
5. **团队匹配**（Slack）通过 `teamId`。
6. **账户匹配**（通道上的 `accountId`）。
7. **通道匹配**（该通道上的任何账户，`accountId: "*"`）。
8. **默认代理**（`agents.list[].default`，否则列表第一项，回退至 `main`）。

当绑定包含多个匹配字段（`peer`, `guildId`, `teamId`, `roles`）时，**所有提供的字段必须匹配**该绑定才生效。

匹配的代理决定使用哪个工作区和会话存储。

## 广播组（运行多个代理）

广播组允许您针对同一对等体运行 **多个代理**，条件是 **OpenClaw 通常会回复**（例如：在 WhatsApp 群组中，提及/激活门控之后）。

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

## 配置概览

- `agents.list`: 命名代理定义（工作区、模型等）。
- `bindings`: 将传入通道/账户/对等体映射到代理。

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

会话存储位于状态目录之下（默认 `~/.openclaw`）：

- `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- JSONL 转录文件与存储并存

您可以通过 `session.store` 和 `{agentId}` 模板化来覆盖存储路径。

网关和 ACP 会话发现还会扫描默认 `agents/` 根目录下的磁盘支持代理存储，以及模板化的 `session.store` 根目录下的存储。发现的存储必须保留在该解析后的代理根目录下，并使用常规的 `sessions.json` 文件。符号链接和根目录外的路径将被忽略。

## WebChat 行为

WebChat 附加到 **选定的代理**，并默认为代理的主会话。因此，WebChat 让您可以在一处查看该代理的跨通道上下文。

## 回复上下文

传入回复包括：

- 可用时包括 `ReplyToId`, `ReplyToBody` 和 `ReplyToSender`。
- 引用上下文作为 `[Replying to ...]` 块追加到 `Body`。

这在所有通道上都是一致的。