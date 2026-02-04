---
summary: "Group chat behavior across surfaces (WhatsApp/Telegram/Discord/Slack/Signal/iMessage/Microsoft Teams)"
read_when:
  - Changing group chat behavior or mention gating
title: "Groups"
---
# 群组

OpenClaw 在所有平台（WhatsApp、Telegram、Discord、Slack、Signal、iMessage、Microsoft Teams）上一致地处理群聊。

## 初学者入门（2 分钟）

OpenClaw“运行”在您自己的消息账户上。没有单独的 WhatsApp 机器人用户。
如果您在某个群组中，OpenClaw 可以看到该群组并在其中响应。

默认行为：

- 群组被限制 (`groupPolicy: "allowlist"`)。
- 回复需要提及，除非您明确禁用提及门控。

翻译：允许名单中的发送者可以通过提及触发 OpenClaw。

> 简而言之
>
> - **私信访问** 由 `*.allowFrom` 控制。
> - **群组访问** 由 `*.groupPolicy` + 允许名单 (`*.groups`, `*.groupAllowFrom`) 控制。
> - **回复触发** 由提及门控 (`requireMention`, `/activation`) 控制。

快速流程（群组消息发生的情况）：

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

![群组消息流程](/images/groups-flow.svg)

如果您希望...
| 目标 | 设置内容 |
|------|-------------|
| 允许所有群组但仅在提及时回复 | `groups: { "*": { requireMention: true } }` |
| 禁用所有群组回复 | `groupPolicy: "disabled"` |
| 仅特定群组 | `groups: { "<group-id>": { ... } }` （无 `"*"` 键） |
| 仅您可以在群组中触发 | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## 会话密钥

- 群组会话使用 `agent:<agentId>:<channel>:group:<id>` 会话密钥（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）。
- Telegram 论坛主题会在群组 ID 中添加 `:topic:<threadId>`，因此每个主题都有自己的会话。
- 直接聊天使用主会话（或根据配置按发送者区分）。
- 群组会话跳过心跳检测。

## 模式：个人私信 + 公共群组（单代理）

是的——如果您的“个人”流量是 **私信**，而“公共”流量是 **群组**，这工作得很好。

原因：在单代理模式下，私信通常落在 **主** 会话密钥 (`agent:main:main`) 中，而群组始终使用 **非主** 会话密钥 (`agent:main:<channel>:group:<id>`)。如果您启用沙盒模式 `mode: "non-main"`，这些群组会话将在 Docker 中运行，而您的主私信会话保留在主机上。

这为您提供了一个代理“大脑”（共享工作区 + 内存），但两种执行姿势：

- **私信**：完整工具（主机）
- **群组**：沙盒 + 受限工具（Docker）

> 如果您需要真正分离的工作区/身份（“个人”和“公共”绝不能混合），请使用第二个代理 + 绑定。参见 [多代理路由](/concepts/multi-agent)。

示例（私信在主机上，群组沙盒化 + 仅消息工具）：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // groups/channels are non-main -> sandboxed
        scope: "session", // strongest isolation (one container per group/channel)
        workspaceAccess: "none",
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        // If allow is non-empty, everything else is blocked (deny still wins).
        allow: ["group:messaging", "group:sessions"],
        deny: ["group:runtime", "group:fs", "group:ui", "nodes", "cron", "gateway"],
      },
    },
  },
}
```

希望“群组只能看到文件夹 X”而不是“无主机访问”？保留 `workspaceAccess: "none"` 并仅将允许名单路径挂载到沙盒中：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
        docker: {
          binds: [
            // hostPath:containerPath:mode
            "~/FriendsShared:/data:ro",
          ],
        },
      },
    },
  },
}
```

相关：

- 配置键和默认值：[网关配置](/gateway/configuration#agentsdefaultssandbox)
- 调试工具被阻止的原因：[沙盒 vs 工具策略 vs 提升](/gateway/sandbox-vs-tool-policy-vs-elevated)
- 绑定挂载详情：[沙盒化](/gateway/sandboxing#custom-bind-mounts)

## 显示标签

- 用户界面标签使用 `displayName`（如果有），格式为 `<channel>:<token>`。
- `#room` 保留给房间/频道；群聊使用 `g-<slug>`（小写，空格 -> `-`，保留 `#@+._-`）。

## 群组策略

按通道控制群组/房间消息的处理方式：

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "disabled", // "open" | "disabled" | "allowlist"
      groupAllowFrom: ["+15551234567"],
    },
    telegram: {
      groupPolicy: "disabled",
      groupAllowFrom: ["123456789", "@username"],
    },
    signal: {
      groupPolicy: "disabled",
      groupAllowFrom: ["+15551234567"],
    },
    imessage: {
      groupPolicy: "disabled",
      groupAllowFrom: ["chat_id:123"],
    },
    msteams: {
      groupPolicy: "disabled",
      groupAllowFrom: ["user@org.com"],
    },
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        GUILD_ID: { channels: { help: { allow: true } } },
      },
    },
    slack: {
      groupPolicy: "allowlist",
      channels: { "#general": { allow: true } },
    },
    matrix: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["@owner:example.org"],
      groups: {
        "!roomId:example.org": { allow: true },
        "#alias:example.org": { allow: true },
      },
    },
  },
}
```

| 策略        | 行为                                                     |
| ------------- | ------------------------------------------------------------ |
| `"open"`      | 群组绕过允许名单；提及门控仍然适用。      |
| `"disabled"`  | 完全阻止所有群组消息。                           |
| `"allowlist"` | 仅允许与配置的允许名单匹配的群组/房间。 |

注意：

- `groupPolicy` 独立于提及门控（后者需要 @提及）。
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams：使用 `groupAllowFrom`（回退：显式 `allowFrom`）。
- Discord：允许名单使用 `channels.discord.guilds.<id>.channels`。
- Slack：允许名单使用 `channels.slack.channels`。
- Matrix：允许名单使用 `channels.matrix.groups`（房间 ID、别名或名称）。使用 `channels.matrix.groupAllowFrom` 限制发送者；每个房间的 `users` 允许名单也受支持。
- 群组私信单独控制 (`channels.discord.dm.*`, `channels.slack.dm.*`)。
- Telegram 允许名单可以匹配用户 ID (`"123456789"`, `"telegram:123456789"`, `"tg:123456789"`) 或用户名 (`"@alice"` 或 `"alice"`)；前缀不区分大小写。
- 默认是 `groupPolicy: "allowlist"`；如果您的群组允许名单为空，则群组消息被阻止。

快速思维模型（群组消息的评估顺序）：

1. `groupPolicy`（打开/禁用/允许名单）
2. 群组允许名单 (`*.groups`, `*.groupAllowFrom`, 通道特定允许名单）
3. 提及门控 (`requireMention`, `/activation`)

## 提及门控（默认）

群组消息需要提及，除非按群组重写。默认设置位于每个子系统下的 `*.groups."*"`。

回复机器人的消息被视为隐式提及（当通道支持回复元数据时）。这适用于 Telegram、WhatsApp、Slack、Discord 和 Microsoft Teams。

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
        "123@g.us": { requireMention: false },
      },
    },
    telegram: {
      groups: {
        "*": { requireMention: true },
        "123456789": { requireMention: false },
      },
    },
    imessage: {
      groups: {
        "*": { requireMention: true },
        "123": { requireMention: false },
      },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          mentionPatterns: ["@openclaw", "openclaw", "\\+15555550123"],
          historyLimit: 50,
        },
      },
    ],
  },
}
```

注意：

- `mentionPatterns` 是不区分大小写的正则表达式。
- 提供显式提及的表面仍然通过；模式是后备。
- 按代理重写：`agents.list[].groupChat.mentionPatterns`（当多个代理共享一个群组时有用）。
- 仅在可能检测提及的情况下强制执行提及门控（原生提及或 `mentionPatterns` 已配置）。
- Discord 的默认设置位于 `channels.discord.guilds."*"`（按服务器/通道可重写）。
- 群组历史上下文在通道之间统一包装，并且是 **仅待处理** 的（由于提及门控跳过的消息）；使用 `messages.groupChat.historyLimit` 进行全局默认设置，使用 `channels.<channel>.historyLimit`（或 `channels.<channel>.accounts.*.historyLimit`）进行重写。设置 `0` 以禁用。

## 群组/频道工具限制（可选）

某些通道配置支持限制哪些工具在 **特定群组/房间/频道** 内可用。

- `tools`：允许/拒绝整个群组的工具。
- `toolsBySender`：群组内的按发送者重写（键是发送者 ID/用户名/电子邮件/电话号码，具体取决于通道）。使用 `"*"` 作为通配符。

解析顺序（最具体者获胜）：

1. 群组/频道 `toolsBySender` 匹配
2. 群组/频道 `tools`
3. 默认 (`"*"`) `toolsBySender` 匹配
4. 默认 (`"*"`) `tools`

示例（Telegram）：

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { tools: { deny: ["exec"] } },
        "-1001234567890": {
          tools: { deny: ["exec", "read", "write"] },
          toolsBySender: {
            "123456789": { alsoAllow: ["exec"] },
          },
        },
      },
    },
  },
}
```

注意：

- 群组/频道工具限制除了全局/代理工具策略外还会应用（拒绝仍然优先）。
- 某些通道使用不同的嵌套结构用于房间/频道（例如，Discord `guilds.*.channels.*`，Slack `channels.*`，MS Teams `teams.*.channels.*`）。

## 群组允许名单

当配置了 `channels.whatsapp.groups`、`channels.telegram.groups` 或 `channels.imessage.groups` 时，键充当群组允许名单。使用 `"*"` 允许所有群组同时设置默认提及行为。

常见意图（复制粘贴）：

1. 禁用所有群组回复

```json5
{
  channels: { whatsapp: { groupPolicy: "disabled" } },
}
```

2. 仅允许特定群组（WhatsApp）

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "123@g.us": { requireMention: true },
        "456@g.us": { requireMention: false },
      },
    },
  },
}
```

3. 允许所有群组但要求提及（显式）

```json5
{
  channels: {
    whatsapp: {
      groups: { "*": { requireMention: true } },
    },
  },
}
```

4. 仅群主可以在群组中触发（WhatsApp）

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
      groups: { "*": { requireMention: true } },
    },
  },
}
```

## 激活（仅群主）

群主可以切换每个群组的激活状态：

- `/activation mention`
- `/activation always`

群主由 `channels.whatsapp.allowFrom` 确定（或未设置时机器人的自我 E.164）。作为独立消息发送命令。其他表面目前忽略 `/activation`。

## 上下文字段

群组传入负载设置：

- `ChatType=group`
- `GroupSubject`（如果已知）
- `GroupMembers`（如果已知）
- `WasMentioned`（提及门控结果）
- Telegram 论坛主题还包括 `MessageThreadId` 和 `IsForum`。

代理系统提示包括新群组会话的第一轮中的群组介绍。它提醒模型像人类一样回应，避免使用 Markdown 表格，并避免输入字面 `\n` 序列。

## iMessage 特定

- 路由或允许名单时优先使用 `chat_id:<id>`。
- 列出聊天：`imsg chats --limit 20`。
- 群组回复总是回到同一个 `chat_id`。

## WhatsApp 特定

有关 WhatsApp 专属行为（历史注入、提及处理细节），请参阅 [群组消息](/concepts/group-messages)。