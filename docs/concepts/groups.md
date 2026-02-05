---
summary: "Group chat behavior across surfaces (WhatsApp/Telegram/Discord/Slack/Signal/iMessage/Microsoft Teams)"
read_when:
  - Changing group chat behavior or mention gating
title: "Groups"
---
# 组群

OpenClaw 在所有平台（WhatsApp, Telegram, Discord, Slack, Signal, iMessage, Microsoft Teams）上一致地处理群聊。

## 初学者入门（2分钟）

OpenClaw“生活”在你自己的消息账户中。没有单独的 WhatsApp 机器人用户。
如果你**在某个群组中**，OpenClaw 可以看到该群组并在其中响应。

默认行为：

- 群组被限制 (`groupPolicy: "allowlist"`)。
- 回复需要提及，除非你明确禁用提及门控。

翻译：允许名单中的发送者可以通过提及触发 OpenClaw。

> TL;DR
>
> - **私信访问**由 `*.allowFrom` 控制。
> - **群组访问**由 `*.groupPolicy` + 允许名单 (`*.groups`, `*.groupAllowFrom`) 控制。
> - **回复触发**由提及门控 (`requireMention`, `/activation`) 控制。

快速流程（群组消息发生的情况）：

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

![群组消息流程](/images/groups-flow.svg)

如果你想...
| 目标 | 设置内容 |
|------|-------------|
| 允许所有群组但仅在@提及时回复 | `groups: { "*": { requireMention: true } }` |
| 禁用所有群组回复 | `groupPolicy: "disabled"` |
| 仅特定群组 | `groups: { "<group-id>": { ... } }` （无 `"*"` 键） |
| 仅你能触发群组中的响应 | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## 会话密钥

- 群组会话使用 `agent:<agentId>:<channel>:group:<id>` 会话密钥（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）。
- Telegram 论坛主题会在群组 ID 中添加 `:topic:<threadId>`，因此每个主题都有自己的会话。
- 直接聊天使用主会话（或按发送者配置）。
- 群组会话跳过心跳。

## 模式：个人私信 + 公共群组（单代理）

是的——如果你的“个人”流量是**私信**，而你的“公共”流量是**群组**，这会工作得很好。

原因：在单代理模式下，私信通常落在**主**会话密钥 (`agent:main:main`) 中，而群组始终使用**非主**会话密钥 (`agent:main:<channel>:group:<id>`)。如果你启用沙盒模式 `mode: "non-main"`，这些群组会话将在 Docker 中运行，而你的主私信会话保留在主机上。

这为你提供了一个代理“大脑”（共享工作区 + 内存），但两种执行姿势：

- **私信**：完整工具（主机）
- **群组**：沙盒 + 受限工具（Docker）

> 如果你需要完全分离的工作区/身份（“个人”和“公共”绝不能混合），请使用第二个代理 + 绑定。参见 [多代理路由](/concepts/multi-agent)。

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

希望使用“组只能查看文件夹X”而不是“无主机访问”？保留`workspaceAccess: "none"`并将仅允许的路径挂载到沙箱中：

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
- 调试工具被阻止的原因：[沙箱与工具策略与提升权限](/gateway/sandbox-vs-tool-policy-vs-elevated)
- 绑定挂载详细信息：[沙箱](/gateway/sandboxing#custom-bind-mounts)

## 显示标签

- 当可用时，UI标签使用`displayName`，格式为`<channel>:<token>`。
- `#room`保留用于房间/频道；群聊使用`g-<slug>`（小写，空格 -> `-`，保留`#@+._-`）。

## 组策略

按频道控制组/房间消息的处理方式：

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
| `"open"`      | 组绕过白名单；提及门控仍然适用。      |
| `"disabled"`  | 完全阻止所有组消息。                           |
| `"allowlist"` | 仅允许与配置的白名单匹配的组/房间。 |

注意：

- `groupPolicy` 与提及门控（需要@提及）是分开的。
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams：使用 `groupAllowFrom`（备用：显式 `allowFrom`）。
- Discord：白名单使用 `channels.discord.guilds.<id>.channels`。
- Slack：白名单使用 `channels.slack.channels`。
- Matrix：白名单使用 `channels.matrix.groups`（房间ID、别名或名称）。使用 `channels.matrix.groupAllowFrom` 来限制发件人；每个房间的 `users` 白名单也受支持。
- 组DM由单独控制 (`channels.discord.dm.*`, `channels.slack.dm.*`)。
- Telegram白名单可以匹配用户ID (`"123456789"`, `"telegram:123456789"`, `"tg:123456789"`) 或用户名 (`"@alice"` 或 `"alice"`)；前缀不区分大小写。
- 默认是 `groupPolicy: "allowlist"`；如果您的组白名单为空，则阻止组消息。

快速思维模型（组消息的评估顺序）：

1. `groupPolicy`（开放/禁用/白名单）
2. 组白名单 (`*.groups`, `*.groupAllowFrom`, 频道特定白名单)
3. 提及门控 (`requireMention`, `/activation`)

## 提及门控（默认）

组消息需要提及，除非按组重写。默认值在每个子系统下位于 `*.groups."*"`。

回复机器人消息被视为隐式提及（当频道支持回复元数据时）。这适用于Telegram、WhatsApp、Slack、Discord和Microsoft Teams。

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
- 提供显式提及的表面仍然通过；模式是后备选项。
- 每个代理覆盖：`agents.list[].groupChat.mentionPatterns`（当多个代理共享一个组时很有用）。
- 提及门控仅在可能检测到提及时强制执行（原生提及或 `mentionPatterns` 已配置）。
- Discord 默认设置位于 `channels.discord.guilds."*"`（每个服务器/频道可覆盖）。
- 组历史上下文在各个频道中统一包装，并且是 **仅待处理** 的（由于提及门控而跳过的消息）；使用 `messages.groupChat.historyLimit` 设置全局默认值，并使用 `channels.<channel>.historyLimit`（或 `channels.<channel>.accounts.*.historyLimit`）进行覆盖。设置 `0` 以禁用。

## 组/频道工具限制（可选）

某些频道配置支持限制哪些工具在 **特定组/房间/频道** 内可用。

- `tools`：允许/拒绝整个组的工具。
- `toolsBySender`：组内的发件人覆盖（键是发件人ID/用户名/电子邮件/电话号码，具体取决于频道）。使用 `"*"` 作为通配符。

解析顺序（最具体的优先）：

1. 组/频道 `toolsBySender` 匹配
2. 组/频道 `tools`
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

- 组/频道工具限制与全局/代理工具策略（拒绝仍然优先）一起应用。
- 某些频道使用不同的嵌套方式用于房间/频道（例如，Discord `guilds.*.channels.*`，Slack `channels.*`，MS Teams `teams.*.channels.*`）。

## 组白名单

当配置了 `channels.whatsapp.groups`，`channels.telegram.groups` 或 `channels.imessage.groups` 时，键充当组白名单。使用 `"*"` 允许所有组，同时设置默认提及行为。

常见意图（复制/粘贴）：

1. 禁用所有组回复

```json5
{
  channels: { whatsapp: { groupPolicy: "disabled" } },
}
```

2. 仅允许特定组（WhatsApp）

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

3. 允许所有组但需要提及（显式）

```json5
{
  channels: {
    whatsapp: {
      groups: { "*": { requireMention: true } },
    },
  },
}
```

4. 仅群主可以在组中触发（WhatsApp）

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

## 激活（仅限群主）

组主可以切换每个组的激活状态：

- `/activation mention`
- `/activation always`

Owner 由 `channels.whatsapp.allowFrom` 确定（或当未设置时机器人的自我 E.164）。将命令作为独立消息发送。其他界面目前忽略 `/activation`。

## 上下文字段

群组传入的有效载荷设置：

- `ChatType=group`
- `GroupSubject`（如果已知）
- `GroupMembers`（如果已知）
- `WasMentioned`（提及门控结果）
- Telegram 论坛主题还包括 `MessageThreadId` 和 `IsForum`。

代理系统提示在新群组会话的第一轮包含群组介绍。它提醒模型像人类一样回应，避免使用 Markdown 表格，并避免输入字面的 `\n` 序列。

## iMessage 特定信息

- 路由或允许列表时优先使用 `chat_id:<id>`。
- 列出聊天：`imsg chats --limit 20`。
- 群组回复总是回到同一个 `chat_id`。

## WhatsApp 特定信息

请参阅 [群组消息](/concepts/group-messages) 以了解 WhatsApp 的特定行为（历史注入、提及处理详情）。