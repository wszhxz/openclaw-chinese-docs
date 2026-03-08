---
summary: "Group chat behavior across surfaces (WhatsApp/Telegram/Discord/Slack/Signal/iMessage/Microsoft Teams/Zalo)"
read_when:
  - Changing group chat behavior or mention gating
title: "Groups"
---
# 群组

OpenClaw 在所有平台上对群聊的处理保持一致：WhatsApp、Telegram、Discord、Slack、Signal、iMessage、Microsoft Teams、Zalo。

## 新手入门（2 分钟）

OpenClaw“驻留”在您自己的消息账户上。没有单独的 WhatsApp 机器人用户。
如果**您**在群组中，OpenClaw 可以看到该群组并在那里响应。

默认行为：

- 群组受限 (`groupPolicy: "allowlist"`)。
- 回复需要提及，除非您明确禁用提及门控。

翻译：允许列表中的发送者可以通过提及它来触发 OpenClaw。

> 简而言之
>
> - **DM 访问**由 `*.allowFrom` 控制。
> - **群组访问**由 `*.groupPolicy` + 允许列表 (`*.groups`, `*.groupAllowFrom`) 控制。
> - **回复触发**由提及门控 (`requireMention`, `/activation`) 控制。

快速流程（群组消息发生了什么）：

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

![Group message flow](/images/groups-flow.svg)

如果您想要...

| 目标                                         | 设置内容                                                |
| -------------------------------------------- | ---------------------------------------------------------- |
| 允许所有群组但仅在@提及时回复                | `groups: { "*": { requireMention: true } }`                |
| 禁用所有群组回复                             | `groupPolicy: "disabled"`                                  |
| 仅特定群组                                   | `groups: { "<group-id>": { ... } }` (无 `"*"` 键)         |
| 仅您可触发群组                               | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## 会话密钥

- 群组会话使用 `agent:<agentId>:<channel>:group:<id>` 会话密钥（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）。
- Telegram 论坛主题将 `:topic:<threadId>` 添加到群组 ID，以便每个主题拥有独立的会话。
- 直接聊天使用主会话（或按发件人配置）。
- 群组会话跳过心跳检测。

## 模式：个人 DM + 公共群组（单代理）

是的——如果您的“个人”流量是 **DM**，“公共”流量是 **群组**，这效果很好。

原因：在单代理模式下，DM 通常落在 **主** 会话密钥 (`agent:main:main`) 中，而群组始终使用 **非主** 会话密钥 (`agent:main:<channel>:group:<id>`)。如果您启用 `mode: "non-main"` 的沙箱功能，这些群组会话将在 Docker 中运行，而您的主 DM 会话保留在主机上。

这为您提供了一个代理“大脑”（共享工作区 + 内存），但有两个执行姿态：

- **DM**：完整工具（主机）
- **群组**：沙箱 + 受限工具（Docker）

> 如果您需要真正独立的工作区/身份（“个人”和“公共”绝不能混合），请使用第二个代理 + 绑定。请参阅 [多代理路由](/concepts/multi-agent)。

示例（DM 在主机上，群组沙箱化 + 仅消息工具）：

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

想要“群组只能查看文件夹 X"而不是“无主机访问”？保留 `workspaceAccess: "none"` 并将仅允许列表的路径挂载到沙箱中：

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
            "/home/user/FriendsShared:/data:ro",
          ],
        },
      },
    },
  },
}
```

相关：

- 配置键和默认值：[网关配置](/gateway/configuration#agentsdefaultssandbox)
- 调试工具被阻止的原因：[沙箱 vs 工具策略 vs 提升权限](/gateway/sandbox-vs-tool-policy-vs-elevated)
- 绑定挂载详情：[沙箱化](/gateway/sandboxing#custom-bind-mounts)

## 显示标签

- UI 标签在可用时使用 `displayName`，格式化为 `<channel>:<token>`。
- `#room` 保留用于房间/频道；群聊使用 `g-<slug>`（小写，空格 -> `-`，保留 `#@+._-`）。

## 群组策略

按频道控制如何处理群组/房间消息：

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "disabled", // "open" | "disabled" | "allowlist"
      groupAllowFrom: ["+15551234567"],
    },
    telegram: {
      groupPolicy: "disabled",
      groupAllowFrom: ["123456789"], // numeric Telegram user id (wizard can resolve @username)
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
| `"open"`      | 群组绕过允许列表；提及门控仍然适用。      |
| `"disabled"`  | 完全阻止所有群组消息。                           |
| `"allowlist"` | 仅允许匹配配置允许列表的群组/房间。 |

注意：

- `groupPolicy` 与提及门控（需要@提及）是分开的。
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams/Zalo：使用 `groupAllowFrom`（回退：显式 `allowFrom`）。
- DM 配对批准 (`*-allowFrom` 存储条目) 仅适用于 DM 访问；群组发件人授权保持显式于群组允许列表。
- Discord：允许列表使用 `channels.discord.guilds.<id>.channels`。
- Slack：允许列表使用 `channels.slack.channels`。
- Matrix：允许列表使用 `channels.matrix.groups`（房间 ID、别名或名称）。使用 `channels.matrix.groupAllowFrom` 限制发件人；也支持每个房间的 `users` 允许列表。
- 群组 DM 单独控制 (`channels.discord.dm.*`, `channels.slack.dm.*`)。
- Telegram 允许列表可以匹配用户 ID (`"123456789"`, `"telegram:123456789"`, `"tg:123456789"`) 或用户名 (`"@alice"` 或 `"alice"`)；前缀不区分大小写。
- 默认为 `groupPolicy: "allowlist"`；如果您的群组允许列表为空，则阻止群组消息。
- 运行时安全：当提供者块完全缺失 (`channels.<provider>` 不存在) 时，群组策略回退到故障关闭模式（通常为 `allowlist`），而不是继承 `channels.defaults.groupPolicy`。

快速心智模型（群组消息的评估顺序）：

1. `groupPolicy`（开放/禁用/允许列表）
2. 群组允许列表 (`*.groups`, `*.groupAllowFrom`, 频道特定允许列表)
3. 提及门控 (`requireMention`, `/activation`)

## 提及门控（默认）

群组消息需要提及，除非每组覆盖。默认值位于每个子系统下的 `*.groups."*"`。

回复机器人消息算作隐式提及（当频道支持回复元数据时）。这适用于 Telegram、WhatsApp、Slack、Discord 和 Microsoft Teams。

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
- 提供显式提及的表面仍然通过；模式是回退方案。
- 每代理覆盖：`agents.list[].groupChat.mentionPatterns`（当多个代理共享一个群组时有用）。
- 仅在可能检测提及时强制执行提及门控（配置了原生提及或 `mentionPatterns`）。
- Discord 默认值位于 `channels.discord.guilds."*"`（可按公会/频道覆盖）。
- 群组历史记录上下文在各频道中统一包装，并且是 **仅待处理**（因提及门控而跳过的消息）；使用 `messages.groupChat.historyLimit` 作为全局默认值，使用 `channels.<channel>.historyLimit`（或 `channels.<channel>.accounts.*.historyLimit`）进行覆盖。设置 `0` 以禁用。

## 群组/频道工具限制（可选）

某些频道配置支持限制在 **特定群组/房间/频道内** 可用的工具。

- `tools`：允许/拒绝整个群组的工具。
- `toolsBySender`：群组内的每发件人覆盖。
  使用显式键前缀：
  `id:<senderId>`, `e164:<phone>`, `username:<handle>`, `name:<displayName>` 和 `"*"` 通配符。
  旧的无前缀键仍被接受，并仅匹配为 `id:`。

解析顺序（最具体者优先）：

1. 群组/频道 `toolsBySender` 匹配
2. 群组/频道 `tools`
3. 默认 (`"*"`) `toolsBySender` 匹配
4. 默认 (`"*"`) `tools`

示例（Telegram）：

注意：

- 组/频道工具限制将在全局/代理工具策略的基础上额外应用（拒绝优先）。
- 某些频道对房间/频道的嵌套方式不同（例如，Discord `guilds.*.channels.*`，Slack `channels.*`，MS Teams `teams.*.channels.*`）。

## 组允许列表

当配置了 `channels.whatsapp.groups`、`channels.telegram.groups` 或 `channels.imessage.groups` 时，这些键充当组允许列表。使用 `"*"` 允许所有组，同时设置默认提及行为。

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

4. 仅所有者可在组内触发（WhatsApp）

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

## 激活（仅限所有者）

组所有者可以切换每个组的激活状态：

- `/activation mention`
- `/activation always`

所有者由 `channels.whatsapp.allowFrom` 确定（如果未设置，则为机器人的自 E.164）。将命令作为独立消息发送。其他渠道目前忽略 `/activation`。

## 上下文字段

组入站负载设置：

- `ChatType=group`
- `GroupSubject`（如果已知）
- `GroupMembers`（如果已知）
- `WasMentioned`（提及门控结果）
- Telegram 论坛主题还包括 `MessageThreadId` 和 `IsForum`。

代理系统提示包含新组会话首次交互时的组介绍。它提醒模型像人类一样响应，避免 Markdown 表格，并避免输入字面量 `\n` 序列。

## iMessage 特定说明

- 路由或允许列表时优先使用 `chat_id:<id>`。
- 列出聊天：`imsg chats --limit 20`。
- 组回复总是返回到相同的 `chat_id`。

## WhatsApp 特定说明

有关仅适用于 WhatsApp 的行为（历史注入、提及处理详情），请参阅 [Group messages](/channels/group-messages)。