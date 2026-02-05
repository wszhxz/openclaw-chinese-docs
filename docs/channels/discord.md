---
summary: "Discord bot support status, capabilities, and configuration"
read_when:
  - Working on Discord channel features
title: "Discord"
---
# Discord (Bot API)

状态：通过官方Discord机器人网关已准备好用于私信和服务器文本频道。

## 快速设置（初学者）

1. 创建一个Discord机器人并复制机器人的令牌。
2. 在Discord应用设置中，启用**消息内容意图**（如果计划使用白名单或名称查找，则还需启用**服务器成员意图**）。
3. 为OpenClaw设置令牌：
   - 环境变量: `DISCORD_BOT_TOKEN=...`
   - 或配置文件: `channels.discord.token: "..."`。
   - 如果两者都设置了，配置文件优先（环境变量回退仅适用于默认账户）。
4. 使用消息权限邀请机器人到您的服务器（如果您只想使用私信，可以创建一个私人服务器）。
5. 启动网关。
6. 默认情况下私信访问是配对的；首次联系时批准配对代码。

最小配置：

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "YOUR_BOT_TOKEN",
    },
  },
}
```

## 目标

- 通过Discord私信或服务器频道与OpenClaw对话。
- 直接聊天会合并到代理的主要会话中（默认`agent:main:main`）；服务器频道保持隔离作为`agent:<agentId>:discord:channel:<channelId>`（显示名称使用`discord:<guildSlug>#<channelSlug>`）。
- 默认忽略群组私信；通过`channels.discord.dm.groupEnabled`启用，并可选地通过`channels.discord.dm.groupChannels`进行限制。
- 保持路由的确定性：回复总是回到收到消息的频道。

## 工作原理

1. 创建一个Discord应用程序 → Bot，启用所需的intents（私信 + 频道消息 + 消息内容），并获取bot令牌。
2. 使用所需的权限邀请机器人加入您的服务器，以便在您希望使用机器人的位置读取/发送消息。
3. 使用`channels.discord.token`配置OpenClaw（或`DISCORD_BOT_TOKEN`作为备用）。
4. 运行网关；当令牌可用时（优先配置，其次环境变量），它会自动启动Discord频道，并且`channels.discord.enabled`不是`false`。
   - 如果您更喜欢环境变量，请设置`DISCORD_BOT_TOKEN`（配置块是可选的）。
5. 直接聊天：在发送时使用`user:<id>`（或`<@id>`提及）；所有回合都会进入共享的`main`会话。纯数字ID不明确且会被拒绝。
6. 频道聊天：使用`channel:<channelId>`进行发送。默认需要提及，并且可以按服务器或按频道设置。
7. 直接聊天：默认通过`channels.discord.dm.policy`安全（默认：`"pairing"`）。未知发送者会收到配对码（1小时后过期）；通过`openclaw pairing approve discord <code>`批准。
   - 要保持旧的“对任何人开放”行为：设置`channels.discord.dm.policy="open"`和`channels.discord.dm.allowFrom=["*"]`。
   - 要硬白名单：设置`channels.discord.dm.policy="allowlist"`并在`channels.discord.dm.allowFrom`中列出发送者。
   - 要忽略所有私信：设置`channels.discord.dm.enabled=false`或`channels.discord.dm.policy="disabled"`。
8. 默认忽略群组私信；通过`channels.discord.dm.groupEnabled`启用，并可选地通过`channels.discord.dm.groupChannels`限制。
9. 可选服务器规则：通过服务器ID（首选）或slug设置`channels.discord.guilds`，并包含每个频道的规则。
10. 可选原生命令：`commands.native`默认为`"auto"`（Discord/Telegram开启，Slack关闭）。使用`channels.discord.commands.native: true|false|"auto"`覆盖；`false`清除先前注册的命令。文本命令由`commands.text`控制，并必须作为独立的`/...`消息发送。使用`commands.useAccessGroups: false`绕过命令的访问组检查。
    - 完整命令列表 + 配置：[斜杠命令](/tools/slash-commands)
11. 可选服务器上下文历史记录：设置`channels.discord.historyLimit`（默认20，回退到`messages.groupChat.historyLimit`）以在回复提及时包含最后N条服务器消息作为上下文。设置`0`以禁用。
12. 反应：代理可以通过`discord`工具触发反应（受`channels.discord.actions.*`限制）。
    - 反应移除语义：参见[/tools/reactions](/tools/reactions)。
    - `discord`工具仅在当前频道为Discord时暴露。
13. 原生命令使用隔离的会话密钥(`agent:<agentId>:discord:slash:<userId>`)而不是共享的`main`会话。

注意：Name → id 解析使用公会成员搜索并需要 Server Members Intent；如果机器人无法搜索成员，请使用 ids 或 `<@id>` 提及。
注意：Slugs 为小写，空格替换为 `-`。频道名称在 slug 化时不包括前导 `#`。
注意：公会上下文 `[from:]` 行包含 `author.tag` + `id` 以方便制作可 ping 的回复。

## 配置写入

默认情况下，Discord 允许写入由 `/config set|unset` 触发的配置更新（需要 `commands.config: true`）。

禁用方法：

```json5
{
  channels: { discord: { configWrites: false } },
}
```

## 如何创建自己的机器人

这是在服务器（公会）频道如 `#help` 中运行 OpenClaw 的“Discord 开发者门户”设置。

### 1) 创建 Discord 应用程序 + 机器人用户

1. Discord 开发者门户 → **应用程序** → **新建应用程序**
2. 在你的应用程序中：
   - **机器人** → **添加机器人**
   - 复制 **机器人令牌**（这就是你要放入 `DISCORD_BOT_TOKEN` 的内容）

### 2) 启用 OpenClaw 所需的网关意图

除非你明确启用，否则 Discord 会阻止“特权意图”。

在 **机器人** → **特权网关意图** 中启用：

- **消息内容意图**（在大多数公会中读取消息文本是必需的；没有它你会看到“使用了不允许的意图”或机器人会连接但不会对消息作出反应）
- **服务器成员意图**（推荐；在公会中进行某些成员/用户查找和允许列表匹配是必需的）

你通常不需要 **存在意图**。设置机器人的自身存在状态 (`setPresence` 操作) 使用网关 OP3 并不需要此意图；只有当你想要接收其他公会成员的存在状态更新时才需要它。

### 3) 生成邀请 URL（OAuth2 URL 生成器）

在你的应用程序中：**OAuth2** → **URL 生成器**

**范围**

- ✅ `bot`
- ✅ `applications.commands`（原生命令所需）

**机器人权限**（最小基线）

- ✅ 查看频道
- ✅ 发送消息
- ✅ 读取消息历史记录
- ✅ 嵌入链接
- ✅ 附加文件
- ✅ 添加反应（可选但推荐）
- ✅ 使用外部表情符号/贴纸（可选；仅如果你想要它们）

除非你在调试并且完全信任机器人，否则避免使用 **管理员**。

复制生成的 URL，打开它，选择你的服务器，并安装机器人。

### 4) 获取 id（公会/用户/频道）

Discord 在任何地方都使用数字 id；OpenClaw 配置更喜欢使用 id。

1. Discord（桌面/网页）→ **用户设置** → **高级** → 启用 **开发者模式**
2. 右键点击：
   - 服务器名称 → **复制服务器 ID**（公会 id）
   - 频道（例如 `#help`）→ **复制频道 ID**
   - 你的用户 → **复制用户 ID**

### 5) 配置 OpenClaw

#### 令牌

通过环境变量设置机器人令牌（服务器上推荐）：

- `DISCORD_BOT_TOKEN=...`

或者通过配置：

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "YOUR_BOT_TOKEN",
    },
  },
}
```

多账户支持：使用 `channels.discord.accounts` 和每个账户的令牌以及可选的 `name`。请参阅[`gateway/configuration`](/gateway/configuration#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 以获取共享模式。

#### 允许列表 + 频道路由

示例“单服务器，仅允许我，仅允许 #help”：

```json5
{
  channels: {
    discord: {
      enabled: true,
      dm: { enabled: false },
      guilds: {
        YOUR_GUILD_ID: {
          users: ["YOUR_USER_ID"],
          requireMention: true,
          channels: {
            help: { allow: true, requireMention: true },
          },
        },
      },
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

注意事项：

- `requireMention: true` 表示机器人仅在被提及时回复（建议用于共享频道）。
- `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）也作为公会消息中的提及。
- 多代理覆盖：在 `agents.list[].groupChat.mentionPatterns` 上设置每个代理的模式。
- 如果存在 `channels`，任何未列出的频道默认被拒绝。
- 使用 `"*"` 频道条目以跨所有频道应用默认设置；显式频道条目会覆盖通配符。
- 线程继承父频道配置（允许列表、`requireMention`、技能、提示等），除非您显式添加线程频道 ID。
- 默认忽略机器人生成的消息；设置 `channels.discord.allowBots=true` 以允许它们（自己的消息仍然会被过滤）。
- 警告：如果您允许回复其他机器人 (`channels.discord.allowBots=true`)，请使用 `requireMention`、`channels.discord.guilds.*.channels.<id>.users` 允许列表，并/或清除 `AGENTS.md` 和 `SOUL.md` 中的防护措施以防止机器人之间的回复循环。

### 6) 验证其是否正常工作

1. 启动网关。
2. 在您的服务器频道中发送：`@Krill hello`（或您机器人的名称）。
3. 如果没有发生任何事情：请检查下方的**故障排除**。

### 故障排除

- 首先：运行 `openclaw doctor` 和 `openclaw channels status --probe`（可操作的警告 + 快速审计）。
- **“Used disallowed intents”**：在开发者门户中启用 **Message Content Intent**（和可能的 **Server Members Intent**），然后重启网关。
- **机器人连接但从未在服务器频道中回复**：
  - 缺少 **Message Content Intent**，或
  - 机器人缺少频道权限（查看/发送/读取历史记录），或
  - 你的配置需要提及而你没有提及，或
  - 你的服务器/频道白名单拒绝了该频道/用户。
- **`requireMention: false` 但仍然没有回复**：
- `channels.discord.groupPolicy` 默认为 **allowlist**；设置为 `"open"` 或在 `channels.discord.guilds` 下添加一个服务器条目（可选地在 `channels.discord.guilds.<id>.channels` 下列出频道以进行限制）。
  - 如果你只设置了 `DISCORD_BOT_TOKEN` 而从未创建 `channels.discord` 部分，运行时会将 `groupPolicy` 默认为 `open`。添加 `channels.discord.groupPolicy`，
    `channels.defaults.groupPolicy`，或服务器/频道白名单以锁定它。
- `requireMention` 必须位于 `channels.discord.guilds`（或特定频道）下。顶级的 `channels.discord.requireMention` 将被忽略。
- **权限审计** (`channels status --probe`) 仅检查数字频道ID。如果你使用别名/名称作为 `channels.discord.guilds.*.channels` 键，审计无法验证权限。
- **私信不起作用**：`channels.discord.dm.enabled=false`，`channels.discord.dm.policy="disabled"`，或你尚未获得批准 (`channels.discord.dm.policy="pairing"`)。
- **Discord 中的执行批准**：Discord 支持在私信中使用 **按钮UI** 进行执行批准（允许一次 / 始终允许 / 拒绝）。`/approve <id> ...` 仅用于转发批准，不会解决 Discord 的按钮提示。如果你看到 `❌ Failed to submit approval: Error: unknown approval id` 或 UI 从未显示，请检查：
  - 配置中的 `channels.discord.execApprovals.enabled: true`。
  - 你的 Discord 用户ID 是否列在 `channels.discord.execApprovals.approvers` 中（UI 仅发送给审批者）。
  - 使用私信提示中的按钮（**允许一次**，**始终允许**，**拒绝**）。
  - 查看 [执行批准](/tools/exec-approvals) 和 [斜杠命令](/tools/slash-commands) 以获取更广泛的批准和命令流程。

## 功能与限制

- DMs 和公会文本频道（线程被视为单独的频道；不支持语音）。
- 输入指示符以最佳努力发送；消息分块使用 `channels.discord.textChunkLimit`（默认 2000）并通过行数分割长回复 (`channels.discord.maxLinesPerMessage`，默认 17）。
- 可选换行分块：设置 `channels.discord.chunkMode="newline"` 以在长度分块之前按空白行（段落边界）分割。
- 支持最多配置的 `channels.discord.mediaMaxMb` 大小的文件上传（默认 8 MB）。
- 默认情况下，公会回复由提及触发以避免嘈杂的机器人。
- 当一条消息引用另一条消息时（引用内容 + ID），注入回复上下文。
- 原生回复线程默认是 **关闭** 的；通过 `channels.discord.replyToMode` 启用并使用回复标签。

## 重试策略

出站 Discord API 调用在遇到速率限制（429）时使用 Discord `retry_after` 进行重试（如果可用），采用指数退避和抖动。通过 `channels.discord.retry` 配置。参见 [重试策略](/concepts/retry)。

## 配置

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "abc.123",
      groupPolicy: "allowlist",
      guilds: {
        "*": {
          channels: {
            general: { allow: true },
          },
        },
      },
      mediaMaxMb: 8,
      actions: {
        reactions: true,
        stickers: true,
        emojiUploads: true,
        stickerUploads: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        roles: false,
        channelInfo: true,
        channels: true,
        voiceStatus: true,
        events: true,
        moderation: false,
        presence: false,
      },
      replyToMode: "off",
      dm: {
        enabled: true,
        policy: "pairing", // pairing | allowlist | open | disabled
        allowFrom: ["123456789012345678", "steipete"],
        groupEnabled: false,
        groupChannels: ["openclaw-dm"],
      },
      guilds: {
        "*": { requireMention: true },
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
          reactionNotifications: "own",
          users: ["987654321098765432", "steipete"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["search", "docs"],
              systemPrompt: "Keep answers short.",
            },
          },
        },
      },
    },
  },
}
```

全局通过 `messages.ackReaction` +
`messages.ackReactionScope` 控制确认反应。使用 `messages.removeAckAfterReply` 在机器人回复后清除确认反应。

- `dm.enabled`: 将 `false` 设置为忽略所有DM（默认 `true`）。- `dm.policy`: DM访问控制（推荐使用 `pairing`）。`"open"` 需要 `dm.allowFrom=["*"]`。- `dm.allowFrom`: DM白名单（用户ID或名称）。由 `dm.policy="allowlist"` 使用，并用于 `dm.policy="open"` 验证。向导接受用户名并在机器人可以搜索成员时将其解析为ID。- `dm.groupEnabled`: 启用群组DM（默认 `false`）。- `dm.groupChannels`: 群组DM频道ID或别名的可选白名单。- `groupPolicy`: 控制服务器频道处理（`open|disabled|allowlist`）；`allowlist` 需要频道白名单。- `guilds`: 按服务器ID（首选）或别名键入的每个服务器规则。- `guilds."*"`: 当没有显式条目时应用的默认每个服务器设置。- `guilds.<id>.slug`: 用于显示名称的可选友好别名。- `guilds.<id>.users`: 每个服务器的可选用户白名单（ID或名称）。- `guilds.<id>.tools`: 当通道覆盖缺失时使用的每个服务器工具策略重写（`allow`/`deny`/`alsoAllow`）。- `guilds.<id>.toolsBySender`: 在服务器级别对每个发送者的工具策略重写（当通道覆盖缺失时适用；支持 `"*"` 通配符）。- `guilds.<id>.channels.<channel>.allow`: 当 `groupPolicy="allowlist"` 时允许/拒绝通道。- `guilds.<id>.channels.<channel>.requireMention`: 通道提及门控。- `guilds.<id>.channels.<channel>.tools`: 每个通道的可选工具策略重写（`allow`/`deny`/`alsoAllow`）。- `guilds.<id>.channels.<channel>.toolsBySender`: 通道内的每个发送者工具策略重写（支持 `"*"` 通配符）。- `guilds.<id>.channels.<channel>.users`: 每个通道的可选用户白名单。- `guilds.<id>.channels.<channel>.skills`: 技能过滤器（省略=所有技能，空=无）。- `guilds.<id>.channels.<channel>.systemPrompt`: 通道的额外系统提示（与通道主题结合）。- `guilds.<id>.channels.<channel>.enabled`: 将 `false` 设置为禁用通道。- `guilds.<id>.channels`: 通道规则（键为通道别名或ID）。- `guilds.<id>.requireMention`: 每个服务器提及要求（可按通道重写）。- `guilds.<id>.reactionNotifications`: 反应系统事件模式（`off`, `own`, `all`, `allowlist`）。- `textChunkLimit`: 出站文本块大小（字符）。默认：2000。- `chunkMode`: `length`（默认）仅在超过 `textChunkLimit` 时拆分；`newline` 在长度分块之前按空白行（段落边界）拆分。- `maxLinesPerMessage`: 每条消息的软最大行数。默认：17。- `mediaMaxMb`: 限制保存到磁盘的传入媒体。- `historyLimit`: 回复提及时包含的最近服务器消息数量作为上下文（默认20；回退到 `messages.groupChat.historyLimit`；`0` 禁用）。- `dmHistoryLimit`: 用户轮次的DM历史记录限制。每个用户的重写：`dms["<user_id>"].historyLimit`。

- `retry`: 对外发送的Discord API调用的重试策略（attempts, minDelayMs, maxDelayMs, jitter）。 - `pluralkit`: 解析PluralKit代理的消息，使系统成员显示为不同的发送者。 - `actions`: 每个操作的工具门；省略以允许所有（设置`false`以禁用）。 - `reactions`（包括react + 读取反应）
  - `stickers`, `emojiUploads`, `stickerUploads`, `polls`, `permissions`, `messages`, `threads`, `pins`, `search`
  - `memberInfo`, `roleInfo`, `channelInfo`, `voiceStatus`, `events`
  - `channels`（创建/编辑/删除频道 + 类别 + 权限）
  - `roles`（角色添加/移除，默认`false`）
  - `moderation`（超时/踢出/封禁，默认`false`）
  - `presence`（机器人状态/活动，默认`false`）
- `execApprovals`: 仅限Discord的执行批准DM（按钮UI）。支持`enabled`, `approvers`, `agentFilter`, `sessionFilter`..

反应通知使用 `guilds.<id>.reactionNotifications`:

- `off`: 无反应事件。
- `own`: 机器人自身消息上的反应（默认）。
- `all`: 所有消息上的所有反应。
- `allowlist`: 来自 `guilds.<id>.users` 的所有消息上的反应（空列表禁用）。

### PluralKit (PK) 支持

启用 PK 查询，以便代理消息解析为底层系统 + 成员。
启用后，OpenClaw 使用成员身份进行白名单，并将发送者标记为 `Member (PK:System)` 以避免意外的 Discord 提及。

```json5
{
  channels: {
    discord: {
      pluralkit: {
        enabled: true,
        token: "pk_live_...", // optional; required for private systems
      },
    },
  },
}
```

白名单说明（启用 PK）：

- 在 `dm.allowFrom`、`guilds.<id>.users` 或每个频道的 `users` 中使用 `pk:<memberId>`。
- 成员显示名称也按名称/别名匹配。
- 查询使用 **原始** Discord 消息 ID（代理前的消息），因此
  PK API 仅在 30 分钟窗口内解析它。
- 如果 PK 查询失败（例如，没有令牌的私有系统），代理消息被视为机器人消息并被丢弃，除非 `channels.discord.allowBots=true`。

### 工具操作默认设置

| 操作组       | 默认值   | 备注                               |
| -------------- | -------- | ---------------------------------- |
| reactions      | enabled  | React + 列出反应 + emojiList |
| stickers       | enabled  | 发送贴纸                      |
| emojiUploads   | enabled  | 上传表情符号                      |
| stickerUploads | enabled  | 上传贴纸                    |
| polls          | enabled  | 创建投票                       |
| permissions    | enabled  | 频道权限快照        |
| messages       | enabled  | 读取/发送/编辑/删除              |
| threads        | enabled  | 创建/列出/回复                  |
| pins           | enabled  | 固定/取消固定/列出                     |
| search         | enabled  | 消息搜索（预览功能）   |
| memberInfo     | enabled  | 成员信息                        |
| roleInfo       | enabled  | 角色列表                          |
| channelInfo    | enabled  | 频道信息 + 列表                |
| channels       | enabled  | 频道/类别管理        |
| voiceStatus    | enabled  | 语音状态查询                 |
| events         | enabled  | 列出/创建计划事件       |
| roles          | disabled | 添加/移除角色                    |
| moderation     | disabled | 超时/踢出/封禁                   |
| presence       | disabled | 机器人状态/活动（setPresence）  |

- `replyToMode`: `off`（默认），`first`，或 `all`。 仅当模型包含回复标签时适用。

## 回复标签

要请求线程回复，模型可以在其输出中包含一个标签：

- `[[reply_to_current]]` — 回复触发的Discord消息。
- `[[reply_to:<id>]]` — 回复上下文/历史中的特定消息ID。
  当前消息ID会附加到提示中作为`[message_id: …]`；历史条目已经包含ID。

行为由`channels.discord.replyToMode`控制：

- `off`: 忽略标签。
- `first`: 只有第一个出站块/附件是回复。
- `all`: 每个出站块/附件都是回复。

允许列表匹配说明：

- `allowFrom`/`users`/`groupChannels` 接受ID、名称、标签或提及如`<@id>`。
- 支持类似`discord:`/`user:`（用户）和`channel:`（群组DM）的前缀。
- 使用`*`允许任何发送者/频道。
- 当存在`guilds.<id>.channels`时，默认拒绝未列出的频道。
- 当省略`guilds.<id>.channels`时，允许白名单服务器中的所有频道。
- 要允许**无频道**，设置`channels.discord.groupPolicy: "disabled"`（或保持空白名单）。
- 配置向导接受`Guild/Channel`名称（公共+私有），并在可能的情况下将其解析为ID。
- 启动时，OpenClaw将白名单中的频道/用户名解析为ID（当机器人可以搜索成员时）
  并记录映射；无法解析的条目保持原样。

本机命令说明：

- 注册的命令镜像OpenClaw的聊天命令。
- 本机命令遵循与DM/guild消息相同的允许列表规则（`channels.discord.dm.allowFrom`，`channels.discord.guilds`，每个频道的规则）。
- 即使未被允许列表的用户也可能在Discord UI中看到斜杠命令；OpenClaw在执行时强制允许列表并回复“未授权”。

## 工具操作

代理可以使用`discord`调用操作，例如：

- `react` / `reactions`（添加或列出反应）
- `sticker`，`poll`，`permissions`
- `readMessages`，`sendMessage`，`editMessage`，`deleteMessage`
- 读取/搜索/固定工具有效负载包括标准化的`timestampMs`（UTC纪元毫秒）和`timestampUtc`以及原始的Discord `timestamp`。
- `threadCreate`，`threadList`，`threadReply`
- `pinMessage`，`unpinMessage`，`listPins`
- `searchMessages`，`memberInfo`，`roleInfo`，`roleAdd`，`roleRemove`，`emojiList`
- `channelInfo`，`channelList`，`voiceStatus`，`eventList`，`eventCreate`
- `timeout`，`kick`，`ban`
- `setPresence`（机器人活动和在线状态）

Discord消息ID在注入的上下文中显示（`[discord message id: …]`和历史行），因此代理可以针对它们。
表情符号可以是Unicode（例如`✅`）或自定义表情符号语法如`<:party_blob:1234567890>`。

## 安全与运维

- 将机器人令牌视为密码；在受监督的主机上优先使用`DISCORD_BOT_TOKEN`环境变量或锁定配置文件权限。
- 仅授予机器人所需的权限（通常是读取消息/发送消息）。
- 如果机器人卡住或受到速率限制，在确认没有其他进程拥有Discord会话后重启网关(`openclaw gateway --force`)。