---
summary: "Group chat behavior across surfaces (WhatsApp/Telegram/Discord/Slack/Signal/iMessage/Microsoft Teams/Zalo)"
read_when:
  - Changing group chat behavior or mention gating
title: "Groups"
---
# 群组

OpenClaw 在所有支持的平台（WhatsApp、Telegram、Discord、Slack、Signal、iMessage、Microsoft Teams、Zalo）上对群聊采用一致的处理方式。

## 入门简介（2 分钟）

OpenClaw “运行”在您自己的消息账户之上，**不存在独立的 WhatsApp 机器人用户**。  
只要**您本人**身处某个群组中，OpenClaw 就能看见该群组，并在其中响应。

默认行为如下：

- 群组访问受限制（`groupPolicy: "allowlist"`）。  
- 回复需通过 @提及 触发，除非您显式禁用提及门控（mention gating）。

翻译说明：仅允许列表（allowlisted）中的发送者可通过 @提及 触发 OpenClaw。

> 简而言之（TL;DR）
>
> - **私信（DM）访问**由 `*.allowFrom` 控制。  
> - **群组访问**由 `*.groupPolicy` + 允许列表（`*.groups`、`*.groupAllowFrom`）共同控制。  
> - **回复触发机制**由提及门控（`requireMention`、`/activation`）控制。

快速流程（一条群组消息的处理过程）：

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

![群组消息流程图](/images/groups-flow.svg)

如果您希望实现以下目标……

| 目标                                             | 应设置的配置项                                               |
| ------------------------------------------------ | ------------------------------------------------------------ |
| 允许所有群组，但仅在被 @提及 时回复               | `groups: { "*": { requireMention: true } }`                |
| 完全禁用所有群组回复                              | `groupPolicy: "disabled"`                                  |
| 仅允许特定群组                                    | `groups: { "<group-id>": { ... } }`（不配置 `"*"` 键）         |
| 仅限您本人可在群组中触发 OpenClaw                 | `groupPolicy: "allowlist"`、`groupAllowFrom: ["+1555..."]` |

## 会话密钥（Session keys）

- 群组会话使用 `agent:<agentId>:<channel>:group:<id>` 会话密钥（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）。  
- Telegram 论坛主题会在群组 ID 后附加 `:topic:<threadId>`，从而为每个主题分配独立的会话。  
- 私信（Direct chats）使用主会话（或按发送者单独配置的会话）。  
- 群组会话跳过心跳检测（heartbeats）。

## 模式：个人私信 + 公开群组（单代理）

是的——当您的“个人”流量为**私信（DMs）**、而“公开”流量为**群组**时，该模式效果良好。

原因：在单代理（single-agent）模式下，私信通常落入**主**会话密钥（`agent:main:main`），而群组始终使用**非主**会话密钥（`agent:main:<channel>:group:<id>`）。若您启用带 `mode: "non-main"` 的沙箱机制，则这些群组会话将在 Docker 中运行，而您的主私信会话则保留在宿主机上。

这使您拥有一个代理“大脑”（共享工作区与记忆），但具备两种执行姿态：

- **私信（DMs）**：完整工具集（宿主机）  
- **群组**：沙箱环境 + 受限工具集（Docker）

> 若您需要真正隔离的工作区/角色（“个人”与“公开”内容绝不可混用），请使用第二个代理 + 绑定配置。参见 [多代理路由（Multi-Agent Routing）](/concepts/multi-agent)。

示例（私信运行于宿主机，群组运行于沙箱并仅启用消息类工具）：

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

若希望实现“群组仅可访问文件夹 X”，而非“完全禁止宿主机访问”，请保留 `workspaceAccess: "none"`，并仅将允许列表中的路径挂载进沙箱：

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

相关文档：

- 配置项及默认值：[网关配置（Gateway configuration）](/gateway/configuration#agentsdefaultssandbox)  
- 调试工具被拦截原因：[沙箱 vs 工具策略 vs 提权（Sandbox vs Tool Policy vs Elevated）](/gateway/sandbox-vs-tool-policy-vs-elevated)  
- 绑定挂载（bind mounts）详情：[沙箱化（Sandboxing）](/gateway/sandboxing#custom-bind-mounts)

## 显示标签（Display labels）

- UI 标签在可用时使用 `displayName`，格式化为 `<channel>:<token>`。  
- `#room` 专用于房间/频道；群聊使用 `g-<slug>`（小写，空格替换为 `-`，保留 `#@+._-`）。

## 群组策略（Group policy）

控制各通道中群组/房间消息的处理方式：

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

| 策略             | 行为                                                         |
| ---------------- | ------------------------------------------------------------ |
| `"open"`      | 群组绕过允许列表；但仍受 @提及 门控约束。                      |
| `"disabled"`  | 完全屏蔽所有群组消息。                                       |
| `"allowlist"` | 仅允许匹配已配置允许列表的群组/房间。                         |

注意事项：

- `groupPolicy` 与提及门控（要求 @提及）相互独立。  
- WhatsApp / Telegram / Signal / iMessage / Microsoft Teams / Zalo：使用 `groupAllowFrom`（回退方案：显式指定 `allowFrom`）。  
- 私信配对审批（`*-allowFrom` 存储条目）仅适用于私信访问；群组发送者授权仍严格依赖群组允许列表。  
- Discord：允许列表使用 `channels.discord.guilds.<id>.channels`。  
- Slack：允许列表使用 `channels.slack.channels`。  
- Matrix：允许列表使用 `channels.matrix.groups`（房间 ID、别名或名称）；使用 `channels.matrix.groupAllowFrom` 限制发送者；也支持按房间配置 `users` 允许列表。  
- 群组私信（Group DMs）由独立配置项控制（`channels.discord.dm.*`、`channels.slack.dm.*`）。  
- Telegram 允许列表可匹配用户 ID（`"123456789"`、`"telegram:123456789"`、`"tg:123456789"`）或用户名（`"@alice"` 或 `"alice"`）；前缀不区分大小写。  
- 默认策略为 `groupPolicy: "allowlist"`；若您的群组允许列表为空，则所有群组消息均被屏蔽。  
- 运行时安全性：当某提供方（provider）配置块完全缺失（`channels.<provider>` 缺失）时，群组策略将回退至“失败即关闭（fail-closed）”模式（通常为 `allowlist`），而非继承 `channels.defaults.groupPolicy`。

快速心智模型（群组消息评估顺序）：

1. `groupPolicy`（open / disabled / allowlist）  
2. 群组允许列表（`*.groups`、`*.groupAllowFrom`、频道专属允许列表）  
3. 提及门控（`requireMention`、`/activation`）

## 提及门控（Mention gating，默认启用）

除非针对特定群组显式覆盖，否则群组消息必须包含 @提及 才能触发回复。默认配置按子系统分别定义于 `*.groups."*"` 下。

对机器人消息的回复（reply）在渠道支持回复元数据（reply metadata）时，视为隐式 @提及。该机制适用于 Telegram、WhatsApp、Slack、Discord 和 Microsoft Teams。

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

注意事项：

- `mentionPatterns` 是不区分大小写的正则表达式。  
- 提供原生 @提及 功能的平台仍会正常传递提及信息；正则匹配仅为回退方案。  
- 每代理覆盖配置：`agents.list[].groupChat.mentionPatterns`（多个代理共用同一群组时非常有用）。  
- 仅当提及检测可行时（原生提及功能或已配置 `mentionPatterns`）才强制执行提及门控。  
- Discord 默认配置位于 `channels.discord.guilds."*"`（可按服务器/频道单独覆盖）。  
- 群组历史上下文在各渠道中统一包装，且为**仅待处理（pending-only）**（因提及门控而跳过的消息不计入）；全局默认值使用 `messages.groupChat.historyLimit`，覆盖配置使用 `channels.<channel>.historyLimit`（或 `channels.<channel>.accounts.*.historyLimit`）；设为 `0` 可禁用该功能。

## 群组/频道工具限制（可选）

部分渠道配置支持限制**特定群组/房间/频道内**可用的工具。

- `tools`：为整个群组设置工具允许/拒绝规则。  
- `toolsBySender`：为群组内不同发送者分别设置覆盖规则。  
  使用显式键前缀：  
  `id:<senderId>`、`e164:<phone>`、`username:<handle>`、`name:<displayName>`，以及通配符 `"*"`。  
  旧版无前缀键仍被接受，且仅匹配为 `id:`。

解析顺序（最具体者优先）：

1. 群组/频道级 `toolsBySender` 匹配  
2. 群组/频道级 `tools`  
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
            "id:123456789": { alsoAllow: ["exec"] },
          },
        },
      },
    },
  },
}
```

注意事项：

- 群组/频道工具限制在全局/代理工具策略之外额外应用（拒绝策略始终优先生效）。
- 某些渠道对房间/频道采用不同的嵌套结构（例如，Discord 使用 `guilds.*.channels.*`，Slack 使用 `channels.*`，Microsoft Teams 使用 `teams.*.channels.*`）。

## 群组白名单

当配置了 `channels.whatsapp.groups`、`channels.telegram.groups` 或 `channels.imessage.groups` 时，这些键将作为群组白名单。可使用 `"*"` 允许所有群组，同时仍设置默认的提及行为。

常见意图（可直接复制粘贴）：

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

3. 允许所有群组，但要求必须提及（显式触发）

```json5
{
  channels: {
    whatsapp: {
      groups: { "*": { requireMention: true } },
    },
  },
}
```

4. 仅群组所有者可在群组中触发（WhatsApp）

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

## 启用控制（仅限所有者）

群组所有者可针对每个群组单独启用或禁用：

- `/activation mention`
- `/activation always`

所有者身份由 `channels.whatsapp.allowFrom` 决定（若未设置，则使用机器人自身的 E.164 号码）。请将该命令作为独立消息发送。当前其他界面会忽略 `/activation`。

## 上下文字段

群组入站载荷中设置以下字段：

- `ChatType=group`
- `GroupSubject`（如已知）
- `GroupMembers`（如已知）
- `WasMentioned`（提及门控结果）
- Telegram 论坛主题还包含 `MessageThreadId` 和 `IsForum`。

代理系统提示词（system prompt）在新群组会话的首轮交互中包含一段群组介绍。该介绍会提醒模型以人类方式作答、避免使用 Markdown 表格，并避免输出字面意义上的 `\n` 序列。

## iMessage 特性

- 在路由或白名单配置中，优先使用 `chat_id:<id>`。
- 列出聊天：`imsg chats --limit 20`。
- 群组回复始终返回至同一 `chat_id`。

## WhatsApp 特性

有关 WhatsApp 独有的行为（如历史记录注入、提及处理细节），请参阅 [群组消息](/channels/group-messages)。