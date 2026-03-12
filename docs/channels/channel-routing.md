---
summary: "Routing rules per channel (WhatsApp, Telegram, Discord, Slack) and shared context"
read_when:
  - Changing channel routing or inbox behavior
title: "Channel Routing"
---
# 通道与路由

OpenClaw 将回复**路由回消息来源的通道**。模型本身不选择通道；路由是确定性的，由宿主配置控制。

## 关键术语

- **通道（Channel）**：`whatsapp`、`telegram`、`discord`、`slack`、`signal`、`imessage`、`webchat`。
- **AccountId**：每个通道对应的账户实例（若支持）。
- 可选的通道默认账户：`channels.<channel>.defaultAccount` 决定当出站路径未指定 `accountId` 时使用哪个账户。
  - 在多账户配置中，若已配置两个或更多账户，请显式设置默认账户（`defaultAccount` 或 `accounts.default`）。否则，回退路由可能选取第一个标准化的账户 ID。
- **AgentId**：一个隔离的工作区 + 会话存储（即“大脑”）。
- **SessionKey**：用于存储上下文并控制并发性的存储桶密钥。

## SessionKey 的结构形式（示例）

私信（Direct messages）合并至代理的 **main** 会话：

- `agent:<agentId>:<mainKey>`（默认：`agent:main:main`）

群组与通道则按通道保持隔离：

- 群组：`agent:<agentId>:<channel>:group:<id>`
- 通道/聊天室：`agent:<agentId>:<channel>:channel:<id>`

线程（Threads）：

- Slack/Discord 线程在基础密钥后追加 `:thread:<threadId>`。
- Telegram 论坛主题将 `:topic:<topicId>` 嵌入群组密钥中。

示例：

- `agent:main:telegram:group:-1001234567890:topic:42`
- `agent:main:discord:channel:123456:thread:987654`

## 主私信路由绑定（Main DM route pinning）

当 `session.dmScope` 为 `main` 时，私信可共享一个主会话。  
为防止该会话的 `lastRoute` 被非所有者的私信覆盖，OpenClaw 在满足以下全部条件时，从 `allowFrom` 推断一个绑定的所有者：

- `allowFrom` 恰好包含一个非通配符条目；
- 该条目可被标准化为该通道下的具体发送方 ID；
- 当前入站私信的发送方与该绑定所有者不匹配。

在此类不匹配情形下，OpenClaw 仍会记录入站会话元数据，但**跳过更新主会话的 `lastRoute`**。

## 路由规则（如何选择代理）

路由为每条入站消息**选择一个代理**：

1. **精确对等体匹配**（`bindings` 匹配 `peer.kind` + `peer.id`）；
2. **父级对等体匹配**（线程继承）；
3. **服务器 + 角色匹配**（Discord），通过 `guildId` + `roles`；
4. **服务器匹配**（Discord），通过 `guildId`；
5. **团队匹配**（Slack），通过 `teamId`；
6. **账户匹配**（通道上的 `accountId`）；
7. **通道匹配**（该通道上任意账户，`accountId: "*"`）；
8. **默认代理**（`agents.list[].default`；否则取列表首项；最终回退至 `main`）。

当某条绑定规则包含多个匹配字段（`peer`、`guildId`、`teamId`、`roles`）时，**所有提供的字段均需匹配，该绑定才生效**。

所匹配的代理决定了将使用哪个工作区和会话存储。

## 广播组（同时运行多个代理）

广播组允许你在 OpenClaw **本应进行回复时**（例如：WhatsApp 群组中，在提及/激活门控之后），为同一对等体**运行多个代理**。

配置如下：

```json5
{
  broadcast: {
    strategy: "parallel",
    "120363403215116621@g.us": ["alfred", "baerbel"],
    "+15555550123": ["support", "logger"],
  },
}
```

参见：[广播组（Broadcast Groups）](/channels/broadcast-groups)。

## 配置概览

- `agents.list`：命名代理定义（工作区、模型等）；
- `bindings`：将入站通道/账户/对等体映射至代理。

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

会话存储位于状态目录下（默认为 `~/.openclaw`）：

- `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- JSONL 格式的对话记录与存储共存

可通过 `session.store` 和 `{agentId}` 模板化方式覆盖存储路径。

## WebChat 行为

WebChat 绑定至**选定的代理**，并默认使用该代理的主会话。因此，WebChat 允许你在单一界面中查看该代理的跨通道上下文。

## 回复上下文

入站回复包含：

- 在可用时提供 `ReplyToId`、`ReplyToBody` 和 `ReplyToSender`；
- 引用的上下文作为 `[Replying to ...]` 块追加至 `Body`。

该行为在所有通道中保持一致。