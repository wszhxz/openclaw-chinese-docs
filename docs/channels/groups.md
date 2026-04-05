---
summary: "Group chat behavior across surfaces (Discord/iMessage/Matrix/Microsoft Teams/Signal/Slack/Telegram/WhatsApp/Zalo)"
read_when:
  - Changing group chat behavior or mention gating
title: "Groups"
---
# 群组

OpenClaw 在各个平台上一致地处理群聊：Discord、iMessage、Matrix、Microsoft Teams、Signal、Slack、Telegram、WhatsApp、Zalo。

## 初学者简介（2 分钟）

OpenClaw“运行”在您自己的消息账户上。没有单独的 WhatsApp 机器人用户。
如果**您**在某个群组中，OpenClaw 可以看到该群组并在那里回复。

默认行为：

- 群组受到限制 (`groupPolicy: "allowlist"`)。
- 回复需要提及，除非您明确禁用提及门控。

含义：白名单发送者可以通过提及来触发 OpenClaw。

> 太长不看版
>
> - **私聊访问** 由 `*.allowFrom` 控制。
> - **群组访问** 由 `*.groupPolicy` + 白名单 (`*.groups`, `*.groupAllowFrom`) 控制。
> - **回复触发** 由提及门控 (`requireMention`, `/activation`) 控制。

快速流程（群消息发生了什么）：

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

## 上下文可见性与白名单

群组安全涉及两个不同的控制：

- **触发授权**：谁可以触发代理 (`groupPolicy`, `groups`, `groupAllowFrom`, 特定通道的白名单)。
- **上下文可见性**：哪些补充上下文被注入到模型中（回复文本、引用、线程历史、转发元数据）。

默认情况下，OpenClaw 优先考虑正常的聊天行为，并保持上下文基本与接收时一致。这意味着白名单主要决定谁可以触发动作，而不是每个引用或历史片段的通用屏蔽边界。

当前行为因通道而异：

- 某些通道已经在特定路径中对补充上下文应用了基于发送者的过滤（例如 Slack 线程播种，Matrix 回复/线程查找）。
- 其他通道仍然按接收原样传递引用/回复/转发上下文。

加固方向（计划中）：

- `contextVisibility: "all"`（默认）保持当前的按接收原样行为。
- `contextVisibility: "allowlist"` 将补充上下文过滤为白名单发送者。
- `contextVisibility: "allowlist_quote"` 是 `allowlist` 加上一个明确的引用/回复例外。

在此加固模型在所有通道上一致实现之前，请预期不同平台之间存在差异。

![Group message flow](/images/groups-flow.svg)

如果您想要...

| 目标                                         | 设置什么                                                |
| -------------------------------------------- | ---------------------------------------------------------- |
| 允许所有群组但仅在 @提及 时回复 | `groups: { "*": { requireMention: true } }`                |
| 禁用所有群组回复                    | `groupPolicy: "disabled"`                                  |
| 仅特定群组                         | `groups: { "<group-id>": { ... } }` (无 `"*"` 键)         |
| 只有您可以在群组中触发               | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## 会话密钥

- 群组会话使用 `agent:<agentId>:<channel>:group:<id>` 会话密钥（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）。
- Telegram 论坛主题向群组 ID 添加 `:topic:<threadId>`，以便每个主题都有自己的会话。
- 直接聊天使用主会话（如果配置则按发送者）。
- 群组会话跳过心跳检测。

<a id="pattern-personal-dms-public-groups-single-agent"></a>

## 模式：个人私聊 + 公共群组（单代理）

是的——如果您的“个人”流量是 **私聊**，而“公共”流量是 **群组**，这效果很好。

原因：在单代理模式下，私聊通常进入 **主** 会话密钥 (`agent:main:main`)，而群组始终使用 **非主** 会话密钥 (`agent:main:<channel>:group:<id>`)。如果您使用 `mode: "non-main"` 启用沙箱，这些群组会话将在 Docker 中运行，而您的主私聊会话保留在主机上。

这为您提供了一个代理“大脑”（共享工作区 + 内存），但有两种执行模式：

- **私聊**：完整工具（主机）
- **群组**：沙箱 + 受限工具（Docker）

> 如果您需要真正独立的工作区/角色（“个人”和“公共”绝不能混合），请使用第二个代理 + 绑定。参见 [多代理路由](/concepts/multi-agent)。

示例（主机上的私聊，沙箱化的群组 + 仅限消息工具）：

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

想要“群组只能看到文件夹 X"而不是“无主机访问”？保留 `workspaceAccess: "none"` 并将仅允许的路径挂载到沙箱中：

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

- 配置键和默认值：[网关配置](/gateway/configuration-reference#agentsdefaultssandbox)
- 调试工具为何被阻止：[沙箱与工具策略与提升权限](/gateway/sandbox-vs-tool-policy-vs-elevated)
- 绑定挂载详情：[沙箱化](/gateway/sandboxing#custom-bind-mounts)

## 显示标签

- UI 标签在可用时使用 `displayName`，格式化为 `<channel>:<token>`。
- `#room` 保留给房间/频道；群聊使用 `g-<slug>`（小写，空格 -> `-`，保留 `#@+._-`）。

## 群组策略

控制每个通道如何处理群组/房间消息：

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
| `"open"`      | 群组绕过白名单；提及门控仍然适用。      |
| `"disabled"`  | 完全阻止所有群组消息。                           |
| `"allowlist"` | 仅允许匹配配置的白名单的群组/房间。 |

注意：

- `groupPolicy` 独立于提及门控（后者需要 @提及）。
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams/Zalo：使用 `groupAllowFrom`（回退：显式 `allowFrom`）。
- 私聊配对批准 (`*-allowFrom` 存储条目) 仅适用于私聊访问；群组发送者授权保留为群组白名单的显式部分。
- Discord：白名单使用 `channels.discord.guilds.<id>.channels`。
- Slack：白名单使用 `channels.slack.channels`。
- Matrix：白名单使用 `channels.matrix.groups`。首选房间 ID 或别名；已加入房间的名称查找是尽力而为的，未解析的名称在运行时会被忽略。使用 `channels.matrix.groupAllowFrom` 限制发送者；也支持每房间的 `users` 白名单。
- 群组私聊单独控制 (`channels.discord.dm.*`, `channels.slack.dm.*`)。
- Telegram 白名单可以匹配用户 ID (`"123456789"`, `"telegram:123456789"`, `"tg:123456789"`) 或用户名 (`"@alice"` 或 `"alice"`)；前缀不区分大小写。
- 默认为 `groupPolicy: "allowlist"`；如果您的群组白名单为空，群组消息将被阻止。
- 运行时安全：当提供程序块完全缺失 (`channels.<provider>` 不存在) 时，群组策略会回退到故障关闭模式（通常为 `allowlist`），而不是继承 `channels.defaults.groupPolicy`。

快速心智模型（群组消息评估顺序）：

1. `groupPolicy`（开放/禁用/白名单）
2. 群组白名单 (`*.groups`, `*.groupAllowFrom`, 特定通道白名单)
3. 提及门控 (`requireMention`, `/activation`)

## 提及门控（默认）

群组消息需要提及，除非按群组覆盖。默认值位于每个子系统下的 `*.groups."*"`。

回复机器人消息算作隐式提及（当通道支持回复元数据时）。这适用于 Telegram、WhatsApp、Slack、Discord 和 Microsoft Teams。

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

- `mentionPatterns` 是不区分大小写的安全正则表达式模式；无效模式和存在风险的嵌套重复形式将被忽略。
- 提供显式提及的渠道仍然通过；模式是后备方案。
- 每代理覆盖：`agents.list[].groupChat.mentionPatterns`（当多个代理共享一个群组时很有用）。
- 提及限制仅在可以检测提及时强制执行（已配置原生提及或 `mentionPatterns`）。
- Discord 默认值位于 `channels.discord.guilds."*"`（可按公会/频道覆盖）。
- 群组历史上下文在所有频道中统一包装，且为 **仅待处理**（因提及限制而跳过的消息）；使用 `messages.groupChat.historyLimit` 作为全局默认值，使用 `channels.<channel>.historyLimit`（或 `channels.<channel>.accounts.*.historyLimit`）进行覆盖。设置 `0` 以禁用。

## 群组/频道工具限制（可选）

某些频道配置支持限制在 **特定群组/房间/频道内** 可用的工具。

- `tools`：允许/拒绝整个群组的工具。
- `toolsBySender`：群组内的每发送者覆盖。
  使用显式键前缀：
  `id:<senderId>`、`e164:<phone>`、`username:<handle>`、`name:<displayName>` 和 `"*"` 通配符。
  旧版无前缀键仍被接受，但仅匹配为 `id:`。

解析顺序（最具体的优先）：

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
            "id:123456789": { alsoAllow: ["exec"] },
          },
        },
      },
    },
  },
}
```

注意：

- 群组/频道工具限制应用于全局/代理工具策略之外（拒绝仍然优先）。
- 某些频道对房间/频道使用不同的嵌套（例如，Discord `guilds.*.channels.*`、Slack `channels.*`、Microsoft Teams `teams.*.channels.*`）。

## 群组白名单

当配置了 `channels.whatsapp.groups`、`channels.telegram.groups` 或 `channels.imessage.groups` 时，这些键充当群组白名单。使用 `"*"` 允许所有群组，同时仍设置默认提及行为。

常见混淆：DM 配对批准与群组授权不同。
对于支持 DM 配对的频道，配对存储仅解锁 DM。群组命令仍需来自配置白名单（如 `groupAllowFrom`）或该频道的文档配置后备方案的显式群组发送者授权。

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

4. 只有所有者可以在群组中触发（WhatsApp）

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

所有者由 `channels.whatsapp.allowFrom` 确定（或未设置时为机器人的自身 E.164）。将命令作为独立消息发送。其他渠道目前忽略 `/activation`。

## 上下文字段

群组入站负载设置：

- `ChatType=group`
- `GroupSubject`（如果已知）
- `GroupMembers`（如果已知）
- `WasMentioned`（提及限制结果）
- Telegram 论坛主题还包括 `MessageThreadId` 和 `IsForum`。

频道特定说明：

- BlueBubbles 可以选择性地从本地联系人数据库中丰富未命名的 macOS 群组参与者，然后再填充 `GroupMembers`。默认关闭，且仅在正常群组限制通过后运行。

代理系统提示在新群组会话的第一轮中包含群组介绍。它提醒模型像人类一样回复，避免使用 Markdown 表格，并避免输入字面量 `\n` 序列。

## iMessage 特定事项

- 路由或白名单时优先使用 `chat_id:<id>`。
- 列出聊天：`imsg chats --limit 20`。
- 群组回复总是返回到相同的 `chat_id`。

## WhatsApp 特定事项

有关 WhatsApp 独有行为（历史注入、提及处理细节），请参阅 [群组消息](/channels/group-messages)。