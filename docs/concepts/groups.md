---
summary: "Group chat behavior across surfaces (WhatsApp/Telegram/Discord/Slack/Signal/iMessage/Microsoft Teams)"
read_when:
  - Changing group chat behavior or mention gating
title: "Groups"
---
# 群组

OpenClaw 在各个平台上一致地处理群聊：WhatsApp、Telegram、Discord、Slack、Signal、iMessage、Microsoft Teams。

## 初学者介绍（2分钟）

OpenClaw "居住"在您自己的消息账户上。没有单独的 WhatsApp 机器人用户。
如果**您**在群组中，OpenClaw 就可以看到该群组并在那里回复。

默认行为：

- 群组是受限的（`groupPolicy: "allowlist"`）。
- 回复需要提及，除非您明确禁用提及网关。

翻译：允许列表中的发送者可以通过提及来触发 OpenClaw。

> TL;DR
>
> - **私信访问**由 `*.allowFrom` 控制。
> - **群组访问**由 `*.groupPolicy` + 允许列表（`*.groups`，`*.groupAllowFrom`）控制。
> - **回复触发**由提及网关（`requireMention`，`/activation`）控制。

快速流程（群组消息发生什么）：

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

![群组消息流程](/images/groups-flow.svg)

如果您想要...
| 目标 | 设置什么 |
|------|-------------|
| 允许所有群组但只在@提及回复 | `groups: { "*": { requireMention: true } }` |
| 禁用所有群组回复 | `groupPolicy: "disabled"` |
| 仅特定群组 | `groups: { "<group-id>": { ... } }`（无 `"*"` 键） |
| 只有您可以触发群组 | `groupPolicy: "allowlist"`，`groupAllowFrom: ["+1555..."]` |

## 会话密钥

- 群组会话使用 `agent:<agentId>:<channel>:group:<id>` 会话密钥（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）。
- Telegram 论坛主题向群组 ID 添加 `:topic:<threadId>`，因此每个主题都有自己的会话。
- 直接聊天使用主会话（或按发送者配置）。
- 群组会话跳过心跳检测。

## 模式：个人私信 + 公开群组（单代理）

是的——如果您的"个人"流量是**私信**而"公开"流量是**群组**，这工作得很好。

原因：在单代理模式下，私信通常落在**主**会话密钥（`agent:main:main`）中，而群组总是使用**非主**会话密钥（`agent:main:<channel>:group:<id>`）。如果您启用 `mode: "non-main"` 的沙箱功能，那些群组会话在 Docker 中运行，而您的主私信会话保留在主机上。

这给您一个代理"大脑"（共享工作区 + 内存），但有两种执行姿态：

- **私信**：完整工具（主机）
- **群组**：沙箱 + 受限工具（Docker）

> 如果您需要真正独立的工作空间/角色（"个人"和"公开"绝不能混合），请使用第二个代理 + 绑定。参见[多代理路由](/concepts/multi-agent)。

示例（私信在主机上，群组沙箱化 + 仅消息工具）：

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

想要"组只能看到文件夹X"而不是"无主机访问权限"？保留 `workspaceAccess: "none"` 并且只将允许列表中的路径挂载到沙箱中：

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

相关链接：

- 配置键和默认值：[网关配置](/gateway/configuration#agentsdefaultssandbox)
- 调试工具被阻止的原因：[沙箱 vs 工具策略 vs 提升权限](/gateway/sandbox-vs-tool-policy-vs-elevated)
- 绑定挂载详情：[沙箱化](/gateway/sandboxing#custom-bind-mounts)

## 显示标签

- UI标签在可用时使用 `displayName`，格式为 `<channel>:<token>`。
- `#room` 保留用于房间/频道；群聊使用 `g-<slug>` （小写，空格 -> `-`，保留 `#@+._-`）。

## 群组策略

控制每个频道中群组/房间消息的处理方式：

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

| 策略          | 行为                                                         |
| ------------- | ------------------------------------------------------------ |
| `open`        | 组绕过白名单；提及门控仍然适用。                             |
| `disabled`    | 完全阻止所有组消息。                                         |
| `allowlist`   | 仅允许与配置的白名单匹配的组/房间。                          |

注意事项：

- `allowlist` 与提及门控（需要@提及）是分开的。
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams：使用 `allowlist`（回退：显式 `disabled`）。
- Discord：白名单使用 `guild_id`。
- Slack：白名单使用 `channel_id`。
- Matrix：白名单使用 `room`（房间ID、别名或名称）。使用 `sender` 限制发送者；也支持按房间的 `allowlist` 白名单。
- 群组DM由单独控制（`group_dm_allowlist`，`group_dm_denylist`）。
- Telegram白名单可以匹配用户ID（`id:123456`，`tg://user?id=123456`，`https://t.me/userid?start=123456`）或用户名（`@username` 或 `tg://resolve?domain=username`）；前缀不区分大小写。
- 默认值为 `open`；如果您的组白名单为空，则组消息被阻止。

快速心理模型（组消息的评估顺序）：

1. `group_policy`（open/disabled/allowlist）
2. 组白名单（`allowlist`，`denylist`，特定频道白名单）
3. 提及门控（`require_mention`，`require_mention_group`）

## 提及门控（默认）

组消息需要提及，除非每个组覆盖。默认值在 `defaults` 子系统下。

回复机器人消息算作隐式提及（当频道支持回复元数据时）。这适用于Telegram、WhatsApp、Slack、Discord和Microsoft Teams。

```
# Per-channel overrides (use channel IDs)
telegram:
  require_mention_group:
    '123456789': false  # Always allow in this group
    '987654321': true   # Always require mention in this group
```

注意事项：

- `mentionPatterns` 是不区分大小写的正则表达式。
- 提供明确提及的界面仍然会通过；模式是备用方案。
- 每个代理覆盖：`agents.list[].groupChat.mentionPatterns`（当多个代理共享一个组时很有用）。
- 只有在可以进行提及检测时（原生提及或已配置 `mentionPatterns`）才会强制执行提及门控。
- Discord 默认值位于 `channels.discord.guilds."*"` 中（每个公会/频道可覆盖）。
- 组历史上下文在各个频道中统一包装，并且是**仅待处理**的（由于提及门控而跳过的消息）；使用 `messages.groupChat.historyLimit` 作为全局默认值，使用 `channels.<channel>.historyLimit`（或 `channels.<channel>.accounts.*.historyLimit`）进行覆盖。设置 `0` 以禁用。

## 群组/频道工具限制（可选）

某些频道配置支持限制在**特定群组/房间/频道内部**可用的工具。

- `tools`：允许/拒绝整个群组的工具。
- `toolsBySender`：群组内的每个发送者覆盖（键根据频道而定，可能是发送者ID/用户名/电子邮件/电话号码）。使用 `"*"` 作为通配符。

解析顺序（最具体的有效）：

1. 群组/频道 `toolsBySender` 匹配
2. 群组/频道 `tools`
3. 默认（`"*"`）`toolsBySender` 匹配
4. 默认（`"*"`）`tools`

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

注意事项：

- 群组/频道工具限制是在全局/代理工具策略基础上应用的（拒绝仍然有效）。
- 某些频道对房间/频道使用不同的嵌套方式（例如，Discord `guilds.*.channels.*`，Slack `channels.*`，MS Teams `teams.*.channels.*`）。

## 群组白名单

当配置了 `channels.whatsapp.groups`、`channels.telegram.groups` 或 `channels.imessage.groups` 时，这些键将作为群组白名单。使用 `"*"` 来允许所有群组，同时仍设置默认提及行为。

常见意图（复制/粘贴）：

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

3. 允许所有群组但需要提及（显式）

```json5
{
  channels: {
    whatsapp: {
      groups: { "*": { requireMention: true } },
    },
  },
}
```

4. 仅所有者可以在群组中触发（WhatsApp）

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

群组所有者可以切换每个群组的激活状态：

- `/activation mention`
- `/activation always`

所有者由 `channels.whatsapp.allowFrom` 确定（或在未设置时使用机器人的自我 E.164）。将命令作为独立消息发送。其他界面当前会忽略 `/activation`。

## 上下文字段

群组入站负载设置：

- `ChatType=group`
- `GroupSubject`（如果已知）
- `GroupMembers`（如果已知）
- `WasMentioned`（提及网关结果）
- Telegram 论坛主题还包括 `MessageThreadId` 和 `IsForum`。

代理系统提示在新群组会话的第一个回合中包含群组介绍。它提醒模型像人类一样回应，避免 Markdown 表格，并避免输入字面的 `\n` 序列。

## iMessage 特定信息

- 路由或允许列表时优先使用 `chat_id:<id>`。
- 列出聊天：`imsg chats --limit 20`。
- 群组回复总是返回到同一个 `chat_id`。

## WhatsApp 特定信息

有关 WhatsApp 专用行为（历史注入、提及处理详情），请参见 [群组消息](/concepts/group-messages)。