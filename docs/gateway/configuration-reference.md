---
title: "Configuration Reference"
description: "Complete field-by-field reference for ~/.openclaw/openclaw.json"
summary: "Complete reference for every OpenClaw config key, defaults, and channel settings"
read_when:
  - You need exact field-level config semantics or defaults
  - You are validating channel, model, gateway, or tool config blocks
---
# 配置参考

`~/.openclaw/openclaw.json` 中可用的所有字段。有关面向任务的概述，请参阅 [配置](/gateway/configuration)。

配置格式为 **JSON5**（允许注释和尾随逗号）。所有字段均为可选 — 省略时 OpenClaw 会使用安全的默认值。

---

## 通道

当存在其配置部分时，每个通道会自动启动（除非 `enabled: false`）。

### DM 和群组访问

所有通道均支持 DM 策略和群组策略：

| DM 策略           | 行为                                                        |
| ------------------- | --------------------------------------------------------------- |
| `pairing`（默认） | 未知发送者会获得一次性配对码；所有者必须批准 |
| `allowlist`         | 仅 `allowFrom` 中的发送者（或配对的允许存储）             |
| `open`              | 允许所有入站 DM（需要 `allowFrom: ["*"]`）             |
| `disabled`          | 忽略所有入站 DM                                          |

| 群组策略          | 行为                                               |
| --------------------- | ------------------------------------------------------ |
| `allowlist`（默认） | 仅匹配配置允许列表的群组          |
| `open`                | 绕过群组允许列表（提及限制仍然适用） |
| `disabled`            | 阻止所有群组/房间消息                          |

<Note>
__CODE_BLOCK_11__ sets the default when a provider's __CODE_BLOCK_12__ is unset.
Pairing codes expire after 1 hour. Pending DM pairing requests are capped at **3 per channel**.
If a provider block is missing entirely (__CODE_BLOCK_13__ absent), runtime group policy falls back to __CODE_BLOCK_14__ (fail-closed) with a startup warning.
</Note>

### 通道模型覆盖

使用 `channels.modelByChannel` 将特定通道 ID 固定到模型。值接受 `provider/model` 或配置的模型别名。当会话尚未具有模型覆盖时（例如，通过 `/model` 设置），通道映射适用。

```json5
{
  channels: {
    modelByChannel: {
      discord: {
        "123456789012345678": "anthropic/claude-opus-4-6",
      },
      slack: {
        C1234567890: "openai/gpt-4.1",
      },
      telegram: {
        "-1001234567890": "openai/gpt-4.1-mini",
        "-1001234567890:topic:99": "anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

### 通道默认值和心跳

使用 `channels.defaults` 跨提供商共享群组策略和心跳行为：

```json5
{
  channels: {
    defaults: {
      groupPolicy: "allowlist", // open | allowlist | disabled
      heartbeat: {
        showOk: false,
        showAlerts: true,
        useIndicator: true,
      },
    },
  },
}
```

- `channels.defaults.groupPolicy`：当提供商级别的 `groupPolicy` 未设置时的回退群组策略。
- `channels.defaults.heartbeat.showOk`：在心跳输出中包含健康通道状态。
- `channels.defaults.heartbeat.showAlerts`：在心跳输出中包含降级/错误状态。
- `channels.defaults.heartbeat.useIndicator`：渲染紧凑指示器风格的心跳输出。

### WhatsApp

WhatsApp 通过网关的 Web 通道（Baileys Web）运行。当存在链接会话时，它会自动启动。

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // blue ticks (false in self-chat mode)
      groups: {
        "*": { requireMention: true },
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
  web: {
    enabled: true,
    heartbeatSeconds: 60,
    reconnect: {
      initialMs: 2000,
      maxMs: 120000,
      factor: 1.4,
      jitter: 0.2,
      maxAttempts: 0,
    },
  },
}
```

<Accordion title="多账户 WhatsApp">

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: {},
        personal: {},
        biz: {
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

- 出站命令默认为账户 `default`（如果存在）；否则为第一个配置的账户 id（排序后）。
- 可选的 `channels.whatsapp.defaultAccount` 在匹配配置的账户 id 时覆盖该回退默认账户选择。
- 遗留的单账户 Baileys auth 目录由 `openclaw doctor` 迁移到 `whatsapp/default`。
- 每账户覆盖：`channels.whatsapp.accounts.<id>.sendReadReceipts`、`channels.whatsapp.accounts.<id>.dmPolicy`、`channels.whatsapp.accounts.<id>.allowFrom`。

</Accordion>

### Telegram

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groups: {
        "*": { requireMention: true },
        "-1001234567890": {
          allowFrom: ["@admin"],
          systemPrompt: "Keep answers brief.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Stay on topic.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" },
      ],
      historyLimit: 50,
      replyToMode: "first", // off | first | all
      linkPreview: true,
      streaming: "partial", // off | partial | block | progress (default: off)
      actions: { reactions: true, sendMessage: true },
      reactionNotifications: "own", // off | own | all
      mediaMaxMb: 100,
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: {
        autoSelectFamily: true,
        dnsResultOrder: "ipv4first",
      },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

- Bot token：`channels.telegram.botToken` 或 `channels.telegram.tokenFile`，`TELEGRAM_BOT_TOKEN` 作为默认账户的回退。
- 可选的 `channels.telegram.defaultAccount` 在匹配配置的账户 id 时覆盖默认账户选择。
- 在多账户设置（2+ 账户 id）中，设置显式默认值（`channels.telegram.defaultAccount` 或 `channels.telegram.accounts.default`）以避免回退路由；`openclaw doctor` 在此缺失或无效时发出警告。
- `configWrites: false` 阻止 Telegram 发起的配置写入（超级群组 ID 迁移，`/config set|unset`）。
- 带有 `type: "acp"` 的顶层 `bindings[]` 条目为论坛主题配置持久 ACP 绑定（在 `match.peer.id` 中使用规范 `chatId:topic:topicId`）。字段语义在 [ACP 代理](/tools/acp-agents#channel-specific-settings) 中共享。
- Telegram 流预览使用 `sendMessage` + `editMessageText`（适用于直接聊天和群组聊天）。
- 重试策略：请参阅 [重试策略](/concepts/retry)。

### Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 8,
      allowBots: false,
      actions: {
        reactions: true,
        stickers: true,
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
        voiceStatus: true,
        events: true,
        moderation: false,
      },
      replyToMode: "off", // off | first | all
      dmPolicy: "pairing",
      allowFrom: ["1234567890", "123456789012345678"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["openclaw-dm"] },
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
          ignoreOtherMentions: true,
          reactionNotifications: "own",
          users: ["987654321098765432"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["docs"],
              systemPrompt: "Short answers only.",
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length", // length | newline
      streaming: "off", // off | partial | block | progress (progress maps to partial on Discord)
      maxLinesPerMessage: 17,
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // opt-in for sessions_spawn({ thread: true })
      },
      voice: {
        enabled: true,
        autoJoin: [
          {
            guildId: "123456789012345678",
            channelId: "234567890123456789",
          },
        ],
        daveEncryption: true,
        decryptionFailureTolerance: 24,
        tts: {
          provider: "openai",
          openai: { voice: "alloy" },
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

- Token：`channels.discord.token`，默认账户的回退选项为 `DISCORD_BOT_TOKEN`。
- 可选的 `channels.discord.defaultAccount` 在匹配配置的账户 ID 时会覆盖默认账户选择。
- 使用 `user:<id>`（私聊）或 `channel:<id>`（服务器频道）作为投递目标；纯数字 ID 将被拒绝。
- 服务器 slug 为小写，空格被替换为 `-`；频道键使用 slug 名称（不含 `#`）。优先使用服务器 ID。
- 默认忽略机器人发布的消息。`allowBots: true` 启用它们；使用 `allowBots: "mentions"` 仅接受提及该机器人的机器人消息（自己的消息仍被过滤）。
- `channels.discord.guilds.<id>.ignoreOtherMentions`（及频道覆盖）会丢弃提及另一个用户或角色但未提及机器人的消息（不包括 @everyone/@here）。
- `maxLinesPerMessage`（默认 17）即使消息低于 2000 字符也会分割长消息。
- `channels.discord.threadBindings` 控制 Discord 线程绑定路由：
  - `enabled`：Discord 线程绑定会话功能的覆盖（`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age` 及绑定投递/路由）
  - `idleHours`：Discord 无活动自动取消聚焦的小时数覆盖（`0` 禁用）
  - `maxAgeHours`：Discord 硬性最大存续时间的小时数覆盖（`0` 禁用）
  - `spawnSubagentSessions`：`sessions_spawn({ thread: true })` 自动线程创建/绑定的启用开关
- 顶层 `bindings[]` 条目配合 `type: "acp"` 配置频道和线程的持久化 ACP 绑定（在 `match.peer.id` 中使用频道/线程 ID）。字段语义在 [ACP Agents](/tools/acp-agents#channel-specific-settings) 中共享。
- `channels.discord.ui.components.accentColor` 设置 Discord components v2 容器的强调色。
- `channels.discord.voice` 启用 Discord 语音频道对话以及可选的自动加入 + TTS 覆盖。
- `channels.discord.voice.daveEncryption` 和 `channels.discord.voice.decryptionFailureTolerance` 透传给 `@discordjs/voice` DAVE 选项（默认为 `true` 和 `24`）。
- OpenClaw 还会在多次解密失败后尝试通过离开/重新加入语音会话来恢复语音接收。
- `channels.discord.streaming` 是规范流模式键。遗留的 `streamMode` 和布尔 `streaming` 值会自动迁移。
- `channels.discord.autoPresence` 将运行时可用性映射到机器人在线状态（healthy => online, degraded => idle, exhausted => dnd），并允许可选的状态文本覆盖。
- `channels.discord.dangerouslyAllowNameMatching` 重新启用可变名称/标签匹配（break-glass 兼容模式）。

**反应通知模式：** `off`（无）、`own`（机器人的消息，默认）、`all`（所有消息）、`allowlist`（来自 `guilds.<id>.users` 的所有消息）。

### Google Chat

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url", // app-url | project-number
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890",
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["users/1234567890"],
      },
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": { allow: true, requireMention: true },
      },
      actions: { reactions: true },
      typingIndicator: "message",
      mediaMaxMb: 20,
    },
  },
}
```

- 服务账户 JSON：内联 (`serviceAccount`) 或基于文件 (`serviceAccountFile`)。
- 也支持服务账户 SecretRef (`serviceAccountRef`)。
- 环境变量回退：`GOOGLE_CHAT_SERVICE_ACCOUNT` 或 `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`。
- 使用 `spaces/<spaceId>` 或 `users/<userId>` 作为投递目标。
- `channels.googlechat.dangerouslyAllowNameMatching` 重新启用可变电子邮件主体匹配（break-glass 兼容模式）。

### Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",
      dmPolicy: "pairing",
      allowFrom: ["U123", "U456", "*"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["G123"] },
      channels: {
        C123: { allow: true, requireMention: true, allowBots: false },
        "#general": {
          allow: true,
          requireMention: true,
          allowBots: false,
          users: ["U123"],
          skills: ["docs"],
          systemPrompt: "Short answers only.",
        },
      },
      historyLimit: 50,
      allowBots: false,
      reactionNotifications: "own",
      reactionAllowlist: ["U123"],
      replyToMode: "off", // off | first | all
      thread: {
        historyScope: "thread", // thread | channel
        inheritParent: false,
      },
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true,
      },
      slashCommand: {
        enabled: true,
        name: "openclaw",
        sessionPrefix: "slack:slash",
        ephemeral: true,
      },
      typingReaction: "hourglass_flowing_sand",
      textChunkLimit: 4000,
      chunkMode: "length",
      streaming: "partial", // off | partial | block | progress (preview mode)
      nativeStreaming: true, // use Slack native streaming API when streaming=partial
      mediaMaxMb: 20,
    },
  },
}
```

- **Socket mode** 需要 `botToken` 和 `appToken`（`SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` 用于默认账户环境变量回退）。
- **HTTP mode** 需要 `botToken` 加上 `signingSecret`（在根级别或每账户）。
- `configWrites: false` 阻止 Slack 发起的配置写入。
- 可选的 `channels.slack.defaultAccount` 在匹配配置的账户 ID 时会覆盖默认账户选择。
- `channels.slack.streaming` 是规范流模式键。遗留的 `streamMode` 和布尔 `streaming` 值会自动迁移。
- 使用 `user:<id>`（私聊）或 `channel:<id>` 作为投递目标。

**反应通知模式：** `off`、`own`（默认）、`all`、`allowlist`（来自 `reactionAllowlist`）。

**线程会话隔离：** `thread.historyScope` 为每线程（默认）或跨频道共享。`thread.inheritParent` 将父频道转录复制到新线程。

- `typingReaction` 在回复运行期间向传入的 Slack 消息添加临时反应，完成后移除。使用 Slack 表情符号短代码，例如 `"hourglass_flowing_sand"`。

| 操作组 | 默认 | 备注                  |
| ------------ | ------- | ---------------------- |
| reactions    | enabled | 反应 + 列出反应 |
| messages     | enabled | 读取/发送/编辑/删除  |
| pins         | enabled | 置顶/取消置顶/列出     |
| memberInfo   | enabled | 成员信息            |
| emojiList    | enabled | 自定义表情列表      |

### Mattermost

Mattermost 作为插件提供：`openclaw plugins install @openclaw/mattermost`。

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
      chatmode: "oncall", // oncall | onmessage | onchar
      oncharPrefixes: [">", "!"],
      commands: {
        native: true, // opt-in
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // Optional explicit URL for reverse-proxy/public deployments
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

聊天模式：`oncall`（在 @-mention 时响应，默认）、`onmessage`（每条消息）、`onchar`（以触发前缀开头的消息）。

启用 Mattermost 原生命令时：

- `commands.callbackPath` 必须是路径（例如 `/api/channels/mattermost/command`），而非完整 URL。
- `commands.callbackUrl` 必须解析到 OpenClaw 网关端点，并且 Mattermost 服务器可访问。
- 对于私有/tailnet/内部回调主机，Mattermost 可能需要
  `ServiceSettings.AllowedUntrustedInternalConnections` 包含回调主机/域名。
  使用主机/域名值，而非完整 URL。
- `channels.mattermost.configWrites`：允许或拒绝 Mattermost 发起的配置写入。
- `channels.mattermost.requireMention`：在频道中回复前需要 `@mention`。
- 可选的 `channels.mattermost.defaultAccount` 在匹配配置的账户 ID 时会覆盖默认账户选择。

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // optional account binding
      dmPolicy: "pairing",
      allowFrom: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      configWrites: true,
      reactionNotifications: "own", // off | own | all | allowlist
      reactionAllowlist: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      historyLimit: 50,
    },
  },
}
```

**反应通知模式：** `off`、`own`（默认）、`all`、`allowlist`（来自 `reactionAllowlist`）。

- `channels.signal.account`：将频道启动固定到特定的 Signal 账户身份。
- `channels.signal.configWrites`：允许或拒绝 Signal 发起的配置写入。
- 可选的 `channels.signal.defaultAccount` 在匹配配置的账户 ID 时会覆盖默认账户选择。

### BlueBubbles

BlueBubbles 是推荐的 iMessage 路径（基于插件，在 `channels.bluebubbles` 下配置）。

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl, password, webhookPath, group controls, and advanced actions:
      // see /channels/bluebubbles
    },
  },
}
```

- 此处涵盖的核心键路径：`channels.bluebubbles`、`channels.bluebubbles.dmPolicy`。
- 可选的 `channels.bluebubbles.defaultAccount` 在匹配配置的账户 ID 时会覆盖默认账户选择。
- 完整的 BlueBubbles 频道配置文档见 [BlueBubbles](/channels/bluebubbles)。

### iMessage

OpenClaw 生成 `imsg rpc`（基于 stdio 的 JSON-RPC）。无需守护进程或端口。

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host",
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123"],
      historyLimit: 50,
      includeAttachments: false,
      attachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      remoteAttachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      mediaMaxMb: 16,
      service: "auto",
      region: "US",
    },
  },
}
```

- 可选的 `channels.imessage.defaultAccount` 在匹配已配置账户 ID 时，会覆盖默认的账户选择。

- 需要对“信息”数据库（Messages DB）授予“完全磁盘访问”权限。
- 优先使用 `chat_id:<id>` 目标；使用 `imsg chats --limit 20` 列出聊天会话。
- `cliPath` 可指向一个 SSH 封装脚本；为通过 SCP 获取附件，请设置 `remoteHost`（`host` 或 `user@host`）。
- `attachmentRoots` 和 `remoteAttachmentRoots` 限制入站附件路径（默认值：`/Users/*/Library/Messages/Attachments`）。
- SCP 启用严格的主机密钥校验，因此请确保中继主机密钥已存在于 `~/.ssh/known_hosts` 中。
- `channels.imessage.configWrites`：允许或禁止由 iMessage 发起的配置写入操作。

<Accordion title="iMessage SSH 封装脚本示例">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Microsoft Teams

Microsoft Teams 基于扩展实现，其配置位于 `channels.msteams` 下。

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId, appPassword, tenantId, webhook, team/channel policies:
      // see /channels/msteams
    },
  },
}
```

- 此处涵盖的核心密钥路径有：`channels.msteams`、`channels.msteams.configWrites`。
- 完整的 Teams 配置（含凭据、Webhook、私信/群组策略，以及按团队/按频道的覆盖设置）详见 [Microsoft Teams](/channels/msteams)。

### IRC

IRC 基于扩展实现，其配置位于 `channels.irc` 下。

```json5
{
  channels: {
    irc: {
      enabled: true,
      dmPolicy: "pairing",
      configWrites: true,
      nickserv: {
        enabled: true,
        service: "NickServ",
        password: "${IRC_NICKSERV_PASSWORD}",
        register: false,
        registerEmail: "bot@example.com",
      },
    },
  },
}
```

- 此处涵盖的核心密钥路径有：`channels.irc`、`channels.irc.dmPolicy`、`channels.irc.configWrites`、`channels.irc.nickserv.*`。
- 可选的 `channels.irc.defaultAccount` 在匹配已配置账户 ID 时，会覆盖默认的账户选择。
- 完整的 IRC 频道配置（包括主机/端口/TLS/频道列表/白名单/提及门控）详见 [IRC](/channels/irc)。

### 多账户（所有频道）

每个频道可运行多个账户（每个账户拥有独立的 `accountId`）：

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "Primary bot",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "Alerts bot",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- 当未指定 `accountId` 时（CLI + 路由场景），使用 `default`。
- 环境变量令牌仅适用于**默认**账户。
- 基础频道设置适用于所有账户，除非为各账户单独覆盖。
- 使用 `bindings[].match.accountId` 可将每个账户路由至不同代理（agent）。
- 若在仍采用单账户顶层频道配置的情况下，通过 `openclaw channels add`（或频道接入流程）添加非默认账户，OpenClaw 会首先将账户作用域内的顶层单账户值移入 `channels.<channel>.accounts.default`，以确保原始账户继续正常工作。
- 已存在的仅限频道的绑定（不含 `accountId`）仍将匹配默认账户；账户作用域的绑定仍为可选项。
- `openclaw doctor --fix` 还可通过在存在命名账户但缺少 `default` 时，将账户作用域内的顶层单账户值移入 `accounts.default`，来修复混合结构问题。

### 其他扩展频道

许多扩展频道被配置为 `channels.<id>`，并在其专属频道页面中详细说明（例如：飞书 Feishu、Matrix、LINE、Nostr、Zalo、Nextcloud Talk、Synology Chat 和 Twitch）。
完整频道索引请参阅：[Channels](/channels)。

### 群聊提及门控（Mention Gating）

群组消息默认**要求提及**（即元数据提及或正则表达式匹配模式）。该机制适用于 WhatsApp、Telegram、Discord、Google Chat 和 iMessage 的群组聊天。

**提及类型：**

- **元数据提及**：平台原生的 @-提及。在 WhatsApp 自聊模式下会被忽略。
- **文本模式**：`agents.list[].groupChat.mentionPatterns` 中定义的正则表达式模式。始终执行检查。
- 仅当可检测到提及（原生提及或至少存在一个匹配模式）时，才强制执行提及门控。

```json5
{
  messages: {
    groupChat: { historyLimit: 50 },
  },
  agents: {
    list: [{ id: "main", groupChat: { mentionPatterns: ["@openclaw", "openclaw"] } }],
  },
}
```

`messages.groupChat.historyLimit` 设置全局默认值。各频道可通过 `channels.<channel>.historyLimit`（或按账户设置）进行覆盖。设置 `0` 可禁用该功能。

#### 私信历史记录限制

```json5
{
  channels: {
    telegram: {
      dmHistoryLimit: 30,
      dms: {
        "123456789": { historyLimit: 50 },
      },
    },
  },
}
```

解决顺序：每条私信覆盖 → 提供商默认值 → 无限制（全部保留）。

支持的渠道：`telegram`、`whatsapp`、`discord`、`slack`、`signal`、`imessage`、`msteams`。

#### 自聊模式

在 `allowFrom` 中包含您自己的号码，即可启用自聊模式（忽略原生 @-提及，仅响应文本模式）：

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: { mentionPatterns: ["reisponde", "@openclaw"] },
      },
    ],
  },
}
```

### 命令（聊天命令处理）

```json5
{
  commands: {
    native: "auto", // register native commands when supported
    text: true, // parse /commands in chat messages
    bash: false, // allow ! (alias: /bash)
    bashForegroundMs: 2000,
    config: false, // allow /config
    debug: false, // allow /debug
    restart: false, // allow /restart + gateway restart tool
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="命令详情">

- 文本命令必须是**独立**的消息，且以 `/` 开头。
- `native: "auto"` 为 Discord/Telegram 启用原生命令，但 Slack 保持关闭状态。
- 按频道覆盖：`channels.discord.commands.native`（布尔值或 `"auto"`）。`false` 将清除此前已注册的所有命令。
- `channels.telegram.customCommands` 为 Telegram 机器人菜单添加额外条目。
- `bash: true` 启用 `! <cmd>`（用于宿主 Shell）。需同时满足 `tools.elevated.enabled` 并确保发送者位于 `tools.elevated.allowFrom.<channel>` 中。
- `config: true` 启用 `/config`（读写 `openclaw.json`）。对于网关 `chat.send` 客户端，若需持久化 `/config set|unset` 写入，还需配置 `operator.admin`；而只读的 `/config show` 对普通写作用域的操作员客户端仍保持可用。
- `channels.<provider>.configWrites` 控制各频道对配置变更的门控（默认：true）。
- `allowFrom` 是按提供方设置的。一旦设定，它将成为**唯一**的授权来源（频道白名单/配对及 `useAccessGroups` 将被忽略）。
- 当未设置 `allowFrom` 时，`useAccessGroups: false` 允许命令绕过访问组策略。

</Accordion>

---

## 代理（Agent）默认值

### `agents.defaults.workspace`

默认值：`~/.openclaw/workspace`。

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

系统提示符“Runtime”行中显示的可选仓库根目录。若未设置，OpenClaw 将从工作区向上遍历自动检测。

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skipBootstrap`

禁用工作区引导文件（bootstrap files）的自动创建（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、`BOOTSTRAP.md`）。

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.bootstrapMaxChars`

工作区引导文件在截断前的最大字符数。默认值：`20000`。

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

所有工作区引导文件注入内容的总字符数上限。默认值：`150000`。

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

控制在引导上下文被截断时，向代理可见的警告文本行为。
默认值：`"once"`。

- `"off"`：永不将警告文本注入系统提示符。
- `"once"`：针对每个唯一的截断签名，仅注入一次警告（推荐）。
- `"always"`：只要存在截断，每次运行均注入警告。

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

在调用提供方接口前，对话记录/工具图像块中图像最长边的最大像素尺寸。
默认值：`1200`。

较低的值通常可减少视觉 Token 消耗，并降低截图密集型任务的请求负载大小；
较高的值则能保留更多视觉细节。

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

系统提示符上下文所使用的时区（非消息时间戳）。若未设置，则回退至主机时区。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

系统提示符中的时间格式。默认值：`auto`（操作系统偏好设置）。

```json5
{
  agents: { defaults: { timeFormat: "auto" } }, // auto | 12 | 24
}
```

### `agents.defaults.model`

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "minimax/MiniMax-M2.5": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.5"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5-mini"],
      },
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
      thinkingDefault: "low",
      verboseDefault: "off",
      elevatedDefault: "on",
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      contextTokens: 200000,
      maxConcurrent: 3,
    },
  },
}
```

- `model`: 接受字符串 (`"provider/model"`) 或对象 (`{ primary, fallbacks }`)。
  - 字符串形式仅设置主模型。
  - 对象形式设置主模型及有序故障转移模型。
- `imageModel`: 接受字符串 (`"provider/model"`) 或对象 (`{ primary, fallbacks }`)。
  - 由 `image` 工具路径用作其视觉模型配置。
  - 此外，当选定的/默认模型无法接受图像输入时，也用作回退路由。
- `pdfModel`: 接受字符串 (`"provider/model"`) 或对象 (`{ primary, fallbacks }`)。
  - 由 `pdf` 工具用于模型路由。
  - 如果省略，PDF 工具将回退到 `imageModel`，然后是尽力而为的提供商默认值。
- `pdfMaxBytesMb`: 当调用时未传递 `maxBytesMb` 时，`pdf` 工具的默认 PDF 大小限制。
- `pdfMaxPages`: `pdf` 工具中提取回退模式考虑的默认最大页数。
- `model.primary`: 格式 `provider/model`（例如 `anthropic/claude-opus-4-6`）。如果省略提供商，OpenClaw 假设使用 `anthropic`（已弃用）。
- `models`: 为 `/model` 配置的模型目录和白名单。每个条目可包含 `alias`（快捷方式）和 `params`（特定于提供商，例如 `temperature`, `maxTokens`, `cacheRetention`, `context1m`）。
- `params` 合并优先级（配置）：`agents.defaults.models["provider/model"].params` 是基础，然后 `agents.list[].params`（匹配代理 ID）按键覆盖。
- 修改这些字段的配置编写器（例如 `/models set`, `/models set-image` 以及回退添加/删除命令）会保存规范对象形式，并在可能时保留现有回退列表。
- `maxConcurrent`: 跨会话的最大并行代理运行数（每个会话仍串行化）。默认值：1。

**内置别名简写**（仅在模型位于 `agents.defaults.models` 时适用）：

| Alias          | Model                           |
| -------------- | ------------------------------- |
| `opus`         | `anthropic/claude-opus-4-6`     |
| `sonnet`       | `anthropic/claude-sonnet-4-5`   |
| `gpt`          | `openai/gpt-5.2`                |
| `gpt-mini`     | `openai/gpt-5-mini`             |
| `gemini`       | `google/gemini-3.1-pro-preview` |
| `gemini-flash` | `google/gemini-3-flash-preview` |

您配置的别名始终优于默认值。

Z.AI GLM-4.x 模型会自动启用思考模式，除非您设置 `--thinking off` 或自行定义 `agents.defaults.models["zai/<model>"].params.thinking`。
Z.AI 模型默认启用 `tool_stream` 以进行工具调用流式传输。将 `agents.defaults.models["zai/<model>"].params.tool_stream` 设置为 `false` 以禁用它。
Anthropic Claude 4.6 模型在未设置明确思考级别时默认为 `adaptive` 思考。

### `agents.defaults.cliBackends`

可选的 CLI 后端，用于纯文本回退运行（无工具调用）。当 API 提供商失败时，可作为备份使用。

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "claude-cli": {
          command: "/opt/homebrew/bin/claude",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          modelArg: "--model",
          sessionArg: "--session",
          sessionMode: "existing",
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
        },
      },
    },
  },
}
```

- CLI 后端优先处理文本；工具始终禁用。
- 当设置 `sessionArg` 时支持会话。
- 当 `imageArg` 接受文件路径时支持图像透传。

### `agents.defaults.heartbeat`

周期性心跳运行。

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m disables
        model: "openai/gpt-5.2-mini",
        includeReasoning: false,
        lightContext: false, // default: false; true keeps only HEARTBEAT.md from workspace bootstrap files
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (default) | block
        target: "none", // default: none | options: last | whatsapp | telegram | discord | ...
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
      },
    },
  },
}
```

- `every`: 持续时间字符串（ms/s/m/h）。默认值：`30m`。
- `suppressToolErrorWarnings`: 当为 true 时，在心跳运行期间抑制工具错误警告负载。
- `directPolicy`: 直接/私信投递策略。`allow`（默认）允许直接目标投递。`block` 抑制直接目标投递并发出 `reason=dm-blocked`。
- `lightContext`: 当为 true 时，心跳运行使用轻量级引导上下文，并仅从工作区引导文件中保留 `HEARTBEAT.md`。
- 按代理：设置 `agents.list[].heartbeat`。当任何代理定义 `heartbeat` 时，**仅这些代理**运行心跳。
- 心跳运行完整的代理回合——间隔越短消耗更多 token。

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "Preserve deployment IDs, ticket IDs, and host:port pairs exactly.", // used when identifierPolicy=custom
        postCompactionSections: ["Session Startup", "Red Lines"], // [] disables reinjection
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store.",
        },
      },
    },
  },
}
```

- `mode`: `default` 或 `safeguard`（长历史记录的分块摘要）。参见 [压缩](/concepts/compaction)。
- `identifierPolicy`: `strict`（默认），`off`，或 `custom`。`strict` 在压缩摘要期间预置内置的不透明标识符保留指南。
- `identifierInstructions`: 可选的自定义标识符保留文本，用于 `identifierPolicy=custom` 时。
- `postCompactionSections`: 可选的 AGENTS.md H2/H3 节名称，用于压缩后重新注入。默认为 `["Session Startup", "Red Lines"]`；设置 `[]` 以禁用重新注入。当未设置或显式设置为该默认对时，旧的 `Every Session`/`Safety` 标题也作为遗留回退被接受。
- `memoryFlush`: 自动压缩前的静默代理回合，用于存储持久记忆。当工作区为只读时跳过。

### `agents.defaults.contextPruning`

在发送给 LLM 之前，从内存上下文中**修剪旧工具结果**。不会修改磁盘上的会话历史记录。

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // duration (ms/s/m/h), default unit: minutes
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Old tool result content cleared]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="cache-ttl 模式行为">

- `mode: "cache-ttl"` 启用修剪过程。
- `ttl` 控制修剪可以再次运行的频率（在上次缓存接触之后）。
- 修剪首先软修剪过大的工具结果，然后在需要时硬清除旧的工具结果。

**软修剪**保留开头 + 结尾，并在中间插入 `...`。

**硬清除**将整个工具结果替换为占位符。

注意：

- 图像块永远不会被修剪/清除。
- 比率基于字符（近似），而非精确 token 计数。
- 如果助手消息少于 `keepLastAssistants` 条，则跳过修剪。

</Accordion>

有关行为详情，请参阅 [会话修剪](/concepts/session-pruning)。

### 块流式传输

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (use minMs/maxMs)
    },
  },
}
```

- 非 Telegram 频道需要明确的 `*.blockStreaming: true` 才能启用块回复。
- 频道覆盖：`channels.<channel>.blockStreamingCoalesce`（以及按账户变体）。Signal/Slack/Discord/Google Chat 默认为 `minChars: 1500`。
- `humanDelay`: 块回复之间的随机暂停。`natural` = 800–2500ms。按代理覆盖：`agents.list[].humanDelay`。

有关行为 + 分块详情，请参阅 [流式传输](/concepts/streaming)。

### 输入指示器

```json5
{
  agents: {
    defaults: {
      typingMode: "instant", // never | instant | thinking | message
      typingIntervalSeconds: 6,
    },
  },
}
```

- 默认值：直接聊天/提及使用 `instant`，未提及的群聊使用 `message`。
- 按会话覆盖：`session.typingMode`, `session.typingIntervalSeconds`。

请参阅 [输入指示器](/concepts/typing-indicators)。

### `agents.defaults.sandbox`

嵌入式代理的可选 **Docker 沙盒**。参见 [沙盒](/gateway/sandboxing) 获取完整指南。

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        scope: "agent", // session | agent | shared
        workspaceAccess: "none", // none | ro | rw
        workspaceRoot: "~/.openclaw/sandboxes",
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          containerPrefix: "openclaw-sbx-",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: {
            nofile: { soft: 1024, hard: 2048 },
            nproc: 256,
          },
          seccompProfile: "/path/to/seccomp.json",
          apparmorProfile: "openclaw-sandbox",
          dns: ["1.1.1.1", "8.8.8.8"],
          extraHosts: ["internal.service:10.0.0.5"],
          binds: ["/home/user/source:/source:rw"],
        },
        browser: {
          enabled: false,
          image: "openclaw-sandbox-browser:bookworm-slim",
          network: "openclaw-sandbox-browser",
          cdpPort: 9222,
          cdpSourceRange: "172.21.0.1/32",
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          allowHostControl: false,
          autoStart: true,
          autoStartTimeoutMs: 12000,
        },
        prune: {
          idleHours: 24,
          maxAgeDays: 7,
        },
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        allow: [
          "exec",
          "process",
          "read",
          "write",
          "edit",
          "apply_patch",
          "sessions_list",
          "sessions_history",
          "sessions_send",
          "sessions_spawn",
          "session_status",
        ],
        deny: ["browser", "canvas", "nodes", "cron", "discord", "gateway"],
      },
    },
  },
}
```

<Accordion title="沙盒详情">

**工作区访问：**

- `none`：`~/.openclaw/sandboxes` 下的每范围沙盒工作区
- `ro`：`/workspace` 处的沙盒工作区，代理工作区以只读方式挂载于 `/agent`
- `rw`：代理工作区以读/写方式挂载于 `/workspace`

**范围：**

- `session`：每会话容器 + 工作区
- `agent`：每个代理一个容器 + 工作区（默认）
- `shared`：共享容器和工作区（无跨会话隔离）

**`setupCommand`** 在容器创建后运行一次（通过 `sh -lc`）。需要网络出口、可写 root、root 用户。

**容器默认为 `network: "none"`** — 如果代理需要出站访问，则设置为 `"bridge"`（或自定义桥接网络）。
`"host"` 被阻止。`"container:<id>"` 默认被阻止，除非你显式设置
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`（紧急突破）。

**入站附件** 暂存于活动工作区中的 `media/inbound/*`。

**`docker.binds`** 挂载额外的主机目录；全局和每代理绑定已合并。

**沙盒浏览器** (`sandbox.browser.enabled`)：容器中的 Chromium + CDP。noVNC URL 注入到系统提示中。不需要 `openclaw.json` 中的 `browser.enabled`。
noVNC 观察者访问默认使用 VNC 认证，OpenClaw 发出一个短期有效的令牌 URL（而不是在共享 URL 中暴露密码）。

- `allowHostControl: false`（默认）阻止沙盒会话针对主机浏览器。
- `network` 默认为 `openclaw-sandbox-browser`（专用桥接网络）。仅当你显式需要全局桥接连接时设置为 `bridge`。
- `cdpSourceRange` 可选地将容器边缘的 CDP 入站限制为 CIDR 范围（例如 `172.21.0.1/32`）。
- `sandbox.browser.binds` 仅将额外的主机目录挂载到沙盒浏览器容器中。设置时（包括 `[]`），它将替换浏览器容器的 `docker.binds`。
- 启动默认值在 `scripts/sandbox-browser-entrypoint.sh` 中定义并针对容器主机进行调整：
  - `--remote-debugging-address=127.0.0.1`
  - `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
  - `--user-data-dir=${HOME}/.chrome`
  - `--no-first-run`
  - `--no-default-browser-check`
  - `--disable-3d-apis`
  - `--disable-gpu`
  - `--disable-software-rasterizer`
  - `--disable-dev-shm-usage`
  - `--disable-background-networking`
  - `--disable-features=TranslateUI`
  - `--disable-breakpad`
  - `--disable-crash-reporter`
  - `--renderer-process-limit=2`
  - `--no-zygote`
  - `--metrics-recording-only`
  - `--disable-extensions`（默认启用）
  - `--disable-3d-apis`、`--disable-software-rasterizer` 和 `--disable-gpu` 默认启用，如果 WebGL/3D 使用需要，可以使用 `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` 禁用。
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` 如果你的工作流依赖扩展，则重新启用扩展。
  - `--renderer-process-limit=2` 可以通过 `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` 更改；设置 `0` 以使用 Chromium 的默认进程限制。
  - 加上 `noSandbox` 启用时的 `--no-sandbox` 和 `--disable-setuid-sandbox`。
  - 默认值是容器镜像基线；使用带有自定义入口点的自定义浏览器镜像来更改容器默认值。

</Accordion>

构建镜像：

```bash
scripts/sandbox-setup.sh           # main sandbox image
scripts/sandbox-browser-setup.sh   # optional browser image
```

### `agents.list`（每代理覆盖）

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6", // or { primary, fallbacks }
        params: { cacheRetention: "none" }, // overrides matching defaults.models params by key
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
        subagents: { allowAgents: ["*"] },
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
          elevated: { enabled: true },
        },
      },
    ],
  },
}
```

- `id`：稳定的代理 id（必需）。
- `default`：当设置多个时，第一个获胜（记录警告）。如果未设置，列表第一个条目为默认。
- `model`：字符串形式仅覆盖 `primary`；对象形式 `{ primary, fallbacks }` 覆盖两者（`[]` 禁用全局回退）。仅覆盖 `primary` 的 Cron 作业仍继承默认回退，除非你设置 `fallbacks: []`。
- `params`：每代理流参数合并到 `agents.defaults.models` 中选定的模型条目上。用于代理特定的覆盖，如 `cacheRetention`、`temperature` 或 `maxTokens`，而无需复制整个模型目录。
- `runtime`：可选的每代理运行时描述符。当代理应默认为 ACP harness 会话时，使用 `type: "acp"` 配合 `runtime.acp` 默认值（`agent`、`backend`、`mode`、`cwd`）。
- `identity.avatar`：工作区相对路径、`http(s)` URL 或 `data:` URI。
- `identity` 派生默认值：`ackReaction` 来自 `emoji`，`mentionPatterns` 来自 `name`/`emoji`。
- `subagents.allowAgents`：`sessions_spawn` 的代理 id 允许列表（`["*"]` = 任意；默认：仅同一代理）。
- 沙盒继承保护：如果请求者会话是沙盒化的，`sessions_spawn` 拒绝将运行非沙盒化的目标。

---

## 多代理路由

在一个 Gateway 内运行多个隔离的代理。参见 [多代理](/concepts/multi-agent)。

```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

### 绑定匹配字段

- `type`（可选）：`route` 用于正常路由（缺失类型默认为 route），`acp` 用于持久 ACP 对话绑定。
- `match.channel`（必需）
- `match.accountId`（可选；`*` = 任意账户；省略 = 默认账户）
- `match.peer`（可选；`{ kind: direct|group|channel, id }`）
- `match.guildId` / `match.teamId`（可选；特定于渠道）
- `acp`（可选；仅用于 `type: "acp"`）：`{ mode, label, cwd, backend }`

**确定性匹配顺序：**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId`（精确，无 peer/guild/team）
5. `match.accountId: "*"`（渠道范围）
6. 默认代理

在每个层级内，第一个匹配的 `bindings` 条目获胜。

对于 `type: "acp"` 条目，OpenClaw 通过精确对话身份（`match.channel` + 账户 + `match.peer.id`）解析，不使用上述路由绑定层级顺序。

### 每代理访问配置文件

<Accordion title="完全访问（无沙盒）">

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="只读工具 + 工作区">

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "ro" },
        tools: {
          allow: [
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="无文件系统访问权限（仅消息）">

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "none" },
        tools: {
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
            "gateway",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

</Accordion>

请参阅 [Multi-Agent Sandbox & Tools](/tools/multi-agent-sandbox-tools) 了解优先级详情。

---

## 会话

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main", // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily", // daily | idle
      atHour: 4,
      idleMinutes: 60,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    parentForkMaxTokens: 100000, // skip parent-thread fork above this token count (0 disables)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // duration or false
      maxDiskBytes: "500mb", // optional hard budget
      highWaterBytes: "400mb", // optional cleanup target
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // default inactivity auto-unfocus in hours (`0` disables)
      maxAgeHours: 0, // default hard max age in hours (`0` disables)
    },
    mainKey: "main", // legacy (runtime always uses "main")
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="会话字段详情">

- **`dmScope`**：私信分组方式。
  - `main`：所有私信共享主会话。
  - `per-peer`：跨渠道按发送者 ID 隔离。
  - `per-channel-peer`：按渠道 + 发送者隔离（推荐用于多用户收件箱）。
  - `per-account-channel-peer`：按账户 + 渠道 + 发送者隔离（推荐用于多账户）。
- **`identityLinks`**：将规范 ID 映射到提供商前缀的对等体以实现跨渠道会话共享。
- **`reset`**：主要重置策略。`daily` 在 `atHour` 本地时间重置；`idle` 在 `idleMinutes` 后重置。当两者都配置时，先过期者生效。
- **`resetByType`**：每种类型的覆盖（`direct`、`group`、`thread`）。遗留 `dm` 接受作为 `direct` 的别名。
- **`parentForkMaxTokens`**：创建分支线程会话时允许的最大父会话 `totalTokens`（默认 `100000`）。
  - 如果父级 `totalTokens` 高于此值，OpenClaw 将启动一个新的线程会话，而不是继承父转录历史。
  - 设置 `0` 以禁用此保护并始终允许父级分支。
- **`mainKey`**：遗留字段。运行时现在始终使用 `"main"` 作为主直接聊天桶。
- **`sendPolicy`**：匹配依据 `channel`、`chatType`（`direct|group|channel`，带遗留 `dm` 别名）、`keyPrefix` 或 `rawKeyPrefix`。首个拒绝生效。
- **`maintenance`**：会话存储清理 + 保留控制。
  - `mode`：`warn` 仅发出警告；`enforce` 应用清理。
  - `pruneAfter`：陈旧条目的截止期限（默认 `30d`）。
  - `maxEntries`：`sessions.json` 中的最大条目数（默认 `500`）。
  - `rotateBytes`：当 `sessions.json` 超过此大小时轮换（默认 `10mb`）。
  - `resetArchiveRetention`：`*.reset.<timestamp>` 转录档案的保留。默认为 `pruneAfter`；设置 `false` 以禁用。
  - `maxDiskBytes`：可选的会话目录磁盘预算。在 `warn` 模式下记录警告；在 `enforce` 模式下首先移除最旧的工件/会话。
  - `highWaterBytes`：预算清理后的可选目标。默认为 `maxDiskBytes` 的 `80%`。
- **`threadBindings`**：线程绑定会话功能的全局默认值。
  - `enabled`：主默认开关（提供商可覆盖；Discord 使用 `channels.discord.threadBindings.enabled`）
  - `idleHours`：默认不活动自动取消聚焦小时数（`0` 禁用；提供商可覆盖）
  - `maxAgeHours`：默认硬最大年龄小时数（`0` 禁用；提供商可覆盖）

</Accordion>

---

## 消息

```json5
{
  messages: {
    responsePrefix: "🦞", // or "auto"
    ackReaction: "👀",
    ackReactionScope: "group-mentions", // group-mentions | group-all | direct | all
    removeAckAfterReply: false,
    queue: {
      mode: "collect", // steer | followup | collect | steer-backlog | steer+backlog | queue | interrupt
      debounceMs: 1000,
      cap: 20,
      drop: "summarize", // old | new | summarize
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
      },
    },
    inbound: {
      debounceMs: 2000, // 0 disables
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### 响应前缀

每渠道/账户覆盖：`channels.<channel>.responsePrefix`、`channels.<channel>.accounts.<id>.responsePrefix`。

解析（最具体者胜）：账户 → 渠道 → 全局。`""` 禁用并停止级联。`"auto"` 派生 `[{identity.name}]`。

**模板变量：**

| 变量 | 描述 | 示例 |
| ----------------- | ---------------------- | --------------------------- |
| `{model}` | 短模型名称 | `claude-opus-4-6` |
| `{modelFull}` | 完整模型标识符 | `anthropic/claude-opus-4-6` |
| `{provider}` | 提供商名称 | `anthropic` |
| `{thinkingLevel}` | 当前思考级别 | `high`、`low`、`off` |
| `{identity.name}` | 代理身份名称 | （与 `"auto"` 相同） |

变量不区分大小写。`{think}` 是 `{thinkingLevel}` 的别名。

### 确认反应

- 默认为活动代理的 `identity.emoji`，否则为 `"👀"`。设置 `""` 以禁用。
- 每渠道覆盖：`channels.<channel>.ackReaction`、`channels.<channel>.accounts.<id>.ackReaction`。
- 解析顺序：账户 → 渠道 → `messages.ackReaction` → 身份回退。
- 范围：`group-mentions`（默认）、`group-all`、`direct`、`all`。
- `removeAckAfterReply`：回复后移除确认（仅限 Slack/Discord/Telegram/Google Chat）。

### 入站防抖

将来自同一发送者的快速纯文本消息批处理为单个代理回合。媒体/附件立即刷新。控制命令绕过防抖。

### TTS (文本转语音)

```json5
{
  messages: {
    tts: {
      auto: "always", // off | always | inbound | tagged
      mode: "final", // final | all
      provider: "elevenlabs",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: { enabled: true },
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
      elevenlabs: {
        apiKey: "elevenlabs_api_key",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 42,
        applyTextNormalization: "auto",
        languageCode: "en",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          style: 0.0,
          useSpeakerBoost: true,
          speed: 1.0,
        },
      },
      openai: {
        apiKey: "openai_api_key",
        baseUrl: "https://api.openai.com/v1",
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
    },
  },
}
```

- `auto` 控制自动 TTS。`/tts off|always|inbound|tagged` 每会话覆盖。
- `summaryModel` 覆盖 `agents.defaults.model.primary` 用于自动摘要。
- `modelOverrides` 默认启用；`modelOverrides.allowProvider` 默认为 `false` (需主动启用)。
- API 密钥回退到 `ELEVENLABS_API_KEY`/`XI_API_KEY` 和 `OPENAI_API_KEY`。
- `openai.baseUrl` 覆盖 OpenAI TTS 端点。解析顺序为配置，然后是 `OPENAI_TTS_BASE_URL`，然后是 `https://api.openai.com/v1`。
- 当 `openai.baseUrl` 指向非 OpenAI 端点时，OpenClaw 将其视为 OpenAI 兼容的 TTS 服务器并放宽模型/语音验证。

---

## Talk

Talk 模式默认值 (macOS/iOS/Android)。

```json5
{
  talk: {
    voiceId: "elevenlabs_voice_id",
    voiceAliases: {
      Clawd: "EXAVITQu4vr4xnSDxMaL",
      Roger: "CwhRBWXzGAHq8TQ4Fs17",
    },
    modelId: "eleven_v3",
    outputFormat: "mp3_44100_128",
    apiKey: "elevenlabs_api_key",
    interruptOnSpeech: true,
  },
}
```

- 语音 ID 回退到 `ELEVENLABS_VOICE_ID` 或 `SAG_VOICE_ID`。
- `apiKey` 和 `providers.*.apiKey` 接受明文字符串或 SecretRef 对象。
- `ELEVENLABS_API_KEY` 回退仅当未配置 Talk API 密钥时应用。
- `voiceAliases` 让 Talk 指令使用友好名称。

---

## 工具

### 工具配置文件

`tools.profile` 在 `tools.allow`/`tools.deny` 之前设置基础允许列表：

本地引导在 unset 时将新本地配置默认为 `tools.profile: "coding"`（现有显式配置文件被保留）。

| 配置文件     | 包含                                                                                  |
| ----------- | ----------------------------------------------------------------------------------------- |
| `minimal`   | 仅 `session_status`                                                                     |
| `coding`    | `group:fs`、`group:runtime`、`group:sessions`、`group:memory`、`image`                    |
| `messaging` | `group:messaging`、`sessions_list`、`sessions_history`、`sessions_send`、`session_status` |
| `full`      | 无限制（同未设置）                                                            |

### 工具组

| 组              | 工具                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec`、`process`（`bash` 被接受为 `exec` 的别名）                            |
| `group:fs`         | `read`、`write`、`edit`、`apply_patch`                                                   |
| `group:sessions`   | `sessions_list`、`sessions_history`、`sessions_send`、`sessions_spawn`、`session_status` |
| `group:memory`     | `memory_search`、`memory_get`                                                            |
| `group:web`        | `web_search`、`web_fetch`                                                                |
| `group:ui`         | `browser`、`canvas`                                                                      |
| `group:automation` | `cron`、`gateway`                                                                        |
| `group:messaging`  | `message`                                                                                |
| `group:nodes`      | `nodes`                                                                                  |
| `group:openclaw`   | 所有内置工具（排除提供商插件）                                           |

### `tools.allow` / `tools.deny`

全局工具允许/拒绝策略（拒绝优先）。不区分大小写，支持 `*` 通配符。即使 Docker 沙箱关闭也适用。

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

进一步限制特定提供商或模型的工具。顺序：基础配置文件 → 提供商配置文件 → 允许/拒绝。

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.2": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

### `tools.elevated`

控制提升的（主机）执行访问权限：

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["1234567890123", "987654321098765432"],
      },
    },
  },
}
```

- 每代理覆盖（`agents.list[].tools.elevated`）只能进一步限制。
- `/elevated on|off|ask|full` 存储每会话状态；内联指令适用于单条消息。
- 提升的 `exec` 在主机上运行，绕过沙箱。

### `tools.exec`

```json5
{
  tools: {
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
      notifyOnExitEmptySuccess: false,
      applyPatch: {
        enabled: false,
        allowModels: ["gpt-5.2"],
      },
    },
  },
}
```

### `tools.loopDetection`

工具循环安全检查**默认禁用**。设置 `enabled: true` 以激活检测。
设置可以在 `tools.loopDetection` 中全局定义，并在 `agents.list[].tools.loopDetection` 处每代理覆盖。

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

- `historySize`：保留用于循环分析的最大工具调用历史。
- `warningThreshold`：用于警告的重复无进展模式阈值。
- `criticalThreshold`：用于阻塞关键循环的更高重复阈值。
- `globalCircuitBreakerThreshold`：任何无进展运行的硬停止阈值。
- `detectors.genericRepeat`：在重复的相同工具/相同参数调用时警告。
- `detectors.knownPollNoProgress`：在已知轮询工具（`process.poll`、`command_status` 等）上警告/阻塞。
- `detectors.pingPong`：在交替无进展对模式上警告/阻塞。
- 如果 `warningThreshold >= criticalThreshold` 或 `criticalThreshold >= globalCircuitBreakerThreshold`，验证失败。

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // or BRAVE_API_KEY env
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        maxChars: 50000,
        maxCharsCap: 50000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        userAgent: "custom-ua",
      },
    },
  },
}
```

### `tools.media`

配置入站媒体理解（图像/音频/视频）：

```json5
{
  tools: {
    media: {
      concurrency: 2,
      audio: {
        enabled: true,
        maxBytes: 20971520,
        scope: {
          default: "deny",
          rules: [{ action: "allow", match: { chatType: "direct" } }],
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { type: "cli", command: "whisper", args: ["--model", "base", "{{MediaPath}}"] },
        ],
      },
      video: {
        enabled: true,
        maxBytes: 52428800,
        models: [{ provider: "google", model: "gemini-3-flash-preview" }],
      },
    },
  },
}
```

<Accordion title="媒体模型输入字段">

**提供商条目**（`type: "provider"` 或省略）：

- `provider`：API 提供商 ID（`openai`、`anthropic`、`google`/`gemini`、`groq` 等）
- `model`：模型 ID 覆盖
- `profile` / `preferredProfile`：`auth-profiles.json` 配置文件选择

**CLI 条目**（`type: "cli"`）：

- `command`：要运行的可执行文件
- `args`：模板参数（支持 `{{MediaPath}}`、`{{Prompt}}`、`{{MaxChars}}` 等）

**通用字段：**

- `capabilities`：可选列表（`image`、`audio`、`video`）。默认值：`openai`/`anthropic`/`minimax` → 图像，`google` → 图像 + 音频 + 视频，`groq` → 音频。
- `prompt`、`maxChars`、`maxBytes`、`timeoutSeconds`、`language`：每条目覆盖。
- 失败回退到下一个条目。

提供商认证遵循标准顺序：`auth-profiles.json` → 环境变量 → `models.providers.*.apiKey`。

</Accordion>

### `tools.agentToAgent`

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },
}
```

### `tools.sessions`

控制哪些会话可以被会话工具（`sessions_list`、`sessions_history`、`sessions_send`）定位。

默认值：`tree`（当前会话 + 由其生成的会话，例如子代理）。

```json5
{
  tools: {
    sessions: {
      // "self" | "tree" | "agent" | "all"
      visibility: "tree",
    },
  },
}
```

注意：

- `self`：仅当前会话密钥。
- `tree`：当前会话 + 由当前会话生成的会话（子代理）。
- `agent`：属于当前代理 ID 的任何会话（如果在同一代理 ID 下运行每发送者会话，可能包括其他用户）。
- `all`：任何会话。跨代理定位仍然需要 `tools.agentToAgent`。
- 沙箱限制：当当前会话处于沙箱中且 `agents.defaults.sandbox.sessionToolsVisibility="spawned"` 时，即使 `tools.sessions.visibility="all"`，可见性也被强制为 `tree`。

### `tools.sessions_spawn`

控制 `sessions_spawn` 的内联附件支持。

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // opt-in: set true to allow inline file attachments
        maxTotalBytes: 5242880, // 5 MB total across all files
        maxFiles: 50,
        maxFileBytes: 1048576, // 1 MB per file
        retainOnSessionKeep: false, // keep attachments when cleanup="keep"
      },
    },
  },
}
```

注意：

- 附件仅支持 `runtime: "subagent"`。ACP 运行时拒绝它们。
- 文件在 `.openclaw/attachments/<uuid>/` 处以 `.manifest.json` 生成到子工作区中。
- 附件内容会自动从记录持久化中屏蔽。
- Base64 输入经过严格字母表/填充检查和解码前大小保护验证。
- 文件权限对于目录为 `0700`，对于文件为 `0600`。
- 清理遵循 `cleanup` 策略：`delete` 始终移除附件；`keep` 仅在 `retainOnSessionKeep: true` 时保留它们。

### `tools.subagents`

```json5
{
  agents: {
    defaults: {
      subagents: {
        model: "minimax/MiniMax-M2.5",
        maxConcurrent: 1,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

- `model`：生成子代理的默认模型。如果省略，子代理继承调用者的模型。
- `runTimeoutSeconds`：当工具调用省略 `runTimeoutSeconds` 时，`sessions_spawn` 的默认超时（秒）。`0` 表示无超时。
- 每子代理工具策略：`tools.subagents.tools.allow` / `tools.subagents.tools.deny`。

---

## 自定义提供商和基础 URL

OpenClaw 使用 pi-coding-agent 模型目录。通过配置中的 `models.providers` 或 `~/.openclaw/agents/<agentId>/agent/models.json` 添加自定义提供商。

```json5
{
  models: {
    mode: "merge", // merge (default) | replace
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions", // openai-completions | openai-responses | anthropic-messages | google-generative-ai
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

- 对于自定义 auth 需求，使用 `authHeader: true` + `headers`。
- 使用 `OPENCLAW_AGENT_DIR`（或 `PI_CODING_AGENT_DIR`）覆盖 agent config root。
- 匹配 provider IDs 的合并优先级：
  - 非空的 agent `models.json` `baseUrl` 值优先。
  - 仅当该 provider 在当前 config/auth-profile 上下文中未被 SecretRef 管理时，非空的 agent `apiKey` 值才优先。
  - SecretRef 管理的 provider `apiKey` 值会从源标记刷新（`ENV_VAR_NAME` 用于 env 引用，`secretref-managed` 用于 file/exec 引用），而不是持久化解析后的 secrets。
  - 空的或缺失的 agent `apiKey`/`baseUrl` 回退到 config 中的 `models.providers`。
  - 匹配的 model `contextWindow`/`maxTokens` 使用显式配置和隐式 catalog 值之间的较高值。
  - 当你希望 config 完全重写 `models.json` 时，使用 `models.mode: "replace"`。

### Provider 字段详情

- `models.mode`：provider catalog 行为（`merge` 或 `replace`）。
- `models.providers`：按 provider id 键入的 custom provider map。
- `models.providers.*.api`：request adapter（`openai-completions`、`openai-responses`、`anthropic-messages`、`google-generative-ai` 等）。
- `models.providers.*.apiKey`：provider credential（优先使用 SecretRef/env 替换）。
- `models.providers.*.auth`：auth strategy（`api-key`、`token`、`oauth`、`aws-sdk`）。
- `models.providers.*.injectNumCtxForOpenAICompat`：对于 Ollama + `openai-completions`，将 `options.num_ctx` 注入 requests（默认：`true`）。
- `models.providers.*.authHeader`：必要时强制在 `Authorization` header 中传输 credential。
- `models.providers.*.baseUrl`：上游 API base URL。
- `models.providers.*.headers`：用于 proxy/tenant 路由的额外 static headers。
- `models.providers.*.models`：显式的 provider model catalog 条目。
- `models.providers.*.models.*.compat.supportsDeveloperRole`：可选的 compatibility hint。对于具有非空非原生 `baseUrl` 的 `api: "openai-completions"`（host 不是 `api.openai.com`），OpenClaw 在运行时强制将其设为 `false`。空/省略的 `baseUrl` 保持默认 OpenAI 行为。
- `models.bedrockDiscovery`：Bedrock auto-discovery 设置根目录。
- `models.bedrockDiscovery.enabled`：开启/关闭 discovery polling。
- `models.bedrockDiscovery.region`：用于 discovery 的 AWS region。
- `models.bedrockDiscovery.providerFilter`：用于 targeted discovery 的可选 provider-id 过滤器。
- `models.bedrockDiscovery.refreshInterval`：discovery 刷新的 polling interval。
- `models.bedrockDiscovery.defaultContextWindow`：discovered models 的 fallback context window。
- `models.bedrockDiscovery.defaultMaxTokens`：discovered models 的 fallback max output tokens。

### Provider 示例

<Accordion title="Cerebras (GLM 4.6 / 4.7)">

```json5
{
  env: { CEREBRAS_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: {
        primary: "cerebras/zai-glm-4.7",
        fallbacks: ["cerebras/zai-glm-4.6"],
      },
      models: {
        "cerebras/zai-glm-4.7": { alias: "GLM 4.7 (Cerebras)" },
        "cerebras/zai-glm-4.6": { alias: "GLM 4.6 (Cerebras)" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      cerebras: {
        baseUrl: "https://api.cerebras.ai/v1",
        apiKey: "${CEREBRAS_API_KEY}",
        api: "openai-completions",
        models: [
          { id: "zai-glm-4.7", name: "GLM 4.7 (Cerebras)" },
          { id: "zai-glm-4.6", name: "GLM 4.6 (Cerebras)" },
        ],
      },
    },
  },
}
```

Cerebras 使用 `cerebras/zai-glm-4.7`；Z.AI 直连使用 `zai/glm-4.7`。

</Accordion>

<Accordion title="OpenCode Zen">

```json5
{
  agents: {
    defaults: {
      model: { primary: "opencode/claude-opus-4-6" },
      models: { "opencode/claude-opus-4-6": { alias: "Opus" } },
    },
  },
}
```

设置 `OPENCODE_API_KEY`（或 `OPENCODE_ZEN_API_KEY`）。快捷方式：`openclaw onboard --auth-choice opencode-zen`。

</Accordion>

<Accordion title="Z.AI (GLM-4.7)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "zai/glm-4.7" },
      models: { "zai/glm-4.7": {} },
    },
  },
}
```

设置 `ZAI_API_KEY`。`z.ai/*` 和 `z-ai/*` 是接受的别名。快捷方式：`openclaw onboard --auth-choice zai-api-key`。

- 通用 endpoint：`https://api.z.ai/api/paas/v4`
- 编码 endpoint（默认）：`https://api.z.ai/api/coding/paas/v4`
- 对于通用 endpoint，使用 base URL 覆盖定义 custom provider。

</Accordion>

<Accordion title="Moonshot AI (Kimi)">

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: { "moonshot/kimi-k2.5": { alias: "Kimi K2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 256000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

对于中国 endpoint：`baseUrl: "https://api.moonshot.cn/v1"` 或 `openclaw onboard --auth-choice moonshot-api-key-cn`。

</Accordion>

<Accordion title="Kimi Coding">

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi-coding/k2p5" },
      models: { "kimi-coding/k2p5": { alias: "Kimi K2.5" } },
    },
  },
}
```

Anthropic 兼容的内置 provider。快捷方式：`openclaw onboard --auth-choice kimi-code-api-key`。

</Accordion>

<Accordion title="Synthetic (Anthropic 兼容)">

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

Base URL 应省略 `/v1`（Anthropic 客户端会附加它）。快捷方式：`openclaw onboard --auth-choice synthetic-api-key`。

</Accordion>

<Accordion title="MiniMax M2.5 (直连)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.5" },
      models: {
        "minimax/MiniMax-M2.5": { alias: "Minimax" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: false,
            input: ["text"],
            cost: { input: 15, output: 60, cacheRead: 2, cacheWrite: 10 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

设置 `MINIMAX_API_KEY`。快捷方式：`openclaw onboard --auth-choice minimax-api`。

</Accordion>

<Accordion title="本地模型 (LM Studio)">

参见 [本地模型](/gateway/local-models)。简而言之：在高性能硬件上通过 LM Studio Responses API 运行 MiniMax M2.5；保留 hosted models 合并作为 fallback。

</Accordion>

---

## 技能

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm", // npm | pnpm | yarn
    },
    entries: {
      "nano-banana-pro": {
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // or plaintext string
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`：仅用于 bundled skills 的可选 allowlist（managed/workspace skills 不受影响）。
- `entries.<skillKey>.enabled: false` 禁用 skill，即使是 bundled/installed 的。
- `entries.<skillKey>.apiKey`：方便声明 primary env var 的 skills（plaintext string 或 SecretRef object）。

---

## 插件

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: [],
    load: {
      paths: ["~/Projects/oss/voice-call-extension"],
    },
    entries: {
      "voice-call": {
        enabled: true,
        hooks: {
          allowPromptInjection: false,
        },
        config: { provider: "twilio" },
      },
    },
  },
}
```

- 从 `~/.openclaw/extensions`、`<workspace>/.openclaw/extensions` 以及 `plugins.load.paths` 加载。
- **配置更改需要重启网关。**
- `allow`：可选的白名单（仅加载列表中列出的插件）。`deny` 优先级更高。
- `plugins.entries.<id>.apiKey`：插件级别的 API 密钥便捷字段（当插件支持时）。
- `plugins.entries.<id>.env`：插件作用域内的环境变量映射。
- `plugins.entries.<id>.hooks.allowPromptInjection`：当启用 `false` 时，核心会屏蔽 `before_prompt_build` 并忽略来自旧版 `before_agent_start` 的提示词修改字段，同时保留旧版 `modelOverride` 和 `providerOverride`。
- `plugins.entries.<id>.config`：由插件定义的配置对象（依据插件 Schema 进行校验）。
- `plugins.slots.memory`：选择激活的内存插件 ID，或设为 `"none"` 以禁用内存插件。
- `plugins.slots.contextEngine`：选择激活的上下文引擎插件 ID；默认为 `"legacy"`，除非您安装并选择了其他引擎。
- `plugins.installs`：CLI 管理的安装元数据，供 `openclaw plugins update` 使用。
  - 包含 `source`、`spec`、`sourcePath`、`installPath`、`version`、`resolvedName`、`resolvedVersion`、`resolvedSpec`、`integrity`、`shasum`、`resolvedAt`、`installedAt`。
  - 将 `plugins.installs.*` 视为受管状态；建议优先使用 CLI 命令而非手动编辑。

参见 [插件](/tools/plugin)。

---

## 浏览器

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    defaultProfile: "chrome",
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true, // default trusted-network mode
      // allowPrivateNetwork: true, // legacy alias
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    color: "#FF4500",
    // headless: false,
    // noSandbox: false,
    // extraArgs: [],
    // executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    // attachOnly: false,
  },
}
```

- `evaluateEnabled: false` 将禁用 `act:evaluate` 和 `wait --fn`。
- `ssrfPolicy.dangerouslyAllowPrivateNetwork` 在未设置时默认为 `true`（可信网络模型）。
- 设置 `ssrfPolicy.dangerouslyAllowPrivateNetwork: false` 以启用严格的仅限公网浏览器导航。
- `ssrfPolicy.allowPrivateNetwork` 仍作为遗留别名被支持。
- 在严格模式下，使用 `ssrfPolicy.hostnameAllowlist` 和 `ssrfPolicy.allowedHostnames` 显式指定例外情况。
- 远程配置文件仅支持附加（启动/停止/重置功能被禁用）。
- 自动检测顺序：默认浏览器（若基于 Chromium）→ Chrome → Brave → Edge → Chromium → Chrome Canary。
- 控制服务：仅限回环地址（端口由 `gateway.port` 推导，默认为 `18791`）。
- `extraArgs` 为本地 Chromium 启动追加额外的启动标志（例如
  `--disable-gpu`、窗口尺寸调整或调试标志）。

---

## 用户界面（UI）

```json5
{
  ui: {
    seamColor: "#FF4500",
    assistant: {
      name: "OpenClaw",
      avatar: "CB", // emoji, short text, image URL, or data URI
    },
  },
}
```

- `seamColor`：原生应用 UI 装饰（如“对话模式”气泡色调等）的强调色。
- `assistant`：控制 UI 身份覆盖项。若未设置，则回退至当前 Agent 的身份。

---

## 网关

```json5
{
  gateway: {
    mode: "local", // local | remote
    port: 18789,
    bind: "loopback",
    auth: {
      mode: "token", // none | token | password | trusted-proxy
      token: "your-token",
      // password: "your-password", // or OPENCLAW_GATEWAY_PASSWORD
      // trustedProxy: { userHeader: "x-forwarded-user" }, // for mode=trusted-proxy; see /gateway/trusted-proxy-auth
      allowTailscale: true,
      rateLimit: {
        maxAttempts: 10,
        windowMs: 60000,
        lockoutMs: 300000,
        exemptLoopback: true,
      },
    },
    tailscale: {
      mode: "off", // off | serve | funnel
      resetOnExit: false,
    },
    controlUi: {
      enabled: true,
      basePath: "/openclaw",
      // root: "dist/control-ui",
      // allowedOrigins: ["https://control.example.com"], // required for non-loopback Control UI
      // dangerouslyAllowHostHeaderOriginFallback: false, // dangerous Host-header origin fallback mode
      // allowInsecureAuth: false,
      // dangerouslyDisableDeviceAuth: false,
    },
    remote: {
      url: "ws://gateway.tailnet:18789",
      transport: "ssh", // ssh | direct
      token: "your-token",
      // password: "your-password",
    },
    trustedProxies: ["10.0.0.1"],
    // Optional. Default false.
    allowRealIpFallback: false,
    tools: {
      // Additional /tools/invoke HTTP denies
      deny: ["browser"],
      // Remove tools from the default HTTP deny list
      allow: ["gateway"],
    },
  },
}
```

<Accordion title="网关字段详情">

- `mode`：`local`（运行网关）或 `remote`（连接远程网关）。除非满足 `local`，否则网关拒绝启动。
- `port`：用于 WebSocket + HTTP 的单一多路复用端口。优先级顺序为：`--port` > `OPENCLAW_GATEWAY_PORT` > `gateway.port` > `18789`。
- `bind`：`auto`、`loopback`（默认）、`lan`（`0.0.0.0`）、`tailnet`（仅 Tailscale IP）或 `custom`。
- **遗留绑定别名**：请在 `gateway.bind` 中使用绑定模式值（`auto`、`loopback`、`lan`、`tailnet`、`custom`），而非主机别名（`0.0.0.0`、`127.0.0.1`、`localhost`、`::`、`::1`）。
- **Docker 注意事项**：默认的 `loopback` 绑定在容器内监听 `127.0.0.1`。在 Docker 桥接网络（`-p 18789:18789`）下，流量到达的是 `eth0`，因此网关不可达。请改用 `--network host`，或设置 `bind: "lan"`（或配合 `customBindHost: "0.0.0.0"` 使用 `bind: "custom"`）以监听所有接口。
- **认证（Auth）**：默认必需。非回环地址绑定需提供共享令牌/密码。初始配置向导默认生成一个令牌。
- 若同时配置了 `gateway.auth.token` 和 `gateway.auth.password`（包括 SecretRefs），则必须显式设置 `gateway.auth.mode` 为 `token` 或 `password`。当两者均被配置且未设置模式时，启动及服务安装/修复流程将失败。
- `gateway.auth.mode: "none"`：显式的无认证模式。仅适用于受信任的本地回环环境；此选项故意不在初始配置向导中提供。
- `gateway.auth.mode: "trusted-proxy"`：将认证委托给具备身份感知能力的反向代理，并信任来自 `gateway.trustedProxies` 的身份头字段（参见 [可信代理认证](/gateway/trusted-proxy-auth)）。
- `gateway.auth.allowTailscale`：当启用 `true` 时，Tailscale Serve 的身份头字段可满足控制界面/WebSocket 认证（通过 `tailscale whois` 验证）；但 HTTP API 端点仍需令牌/密码认证。该免令牌流程假设网关主机是受信任的。当启用 `tailscale.mode = "serve"` 时，默认为 `true`。
- `gateway.auth.rateLimit`：可选的认证失败限流器。按客户端 IP 及认证范围（共享密钥与设备令牌分别独立追踪）进行限制。被阻止的尝试返回 `429` + `Retry-After`。
  - `gateway.auth.rateLimit.exemptLoopback` 默认为 `true`；若您有意对本地回环流量也启用速率限制（例如测试环境或严格代理部署场景），请设置 `false`。
- 来自浏览器的 WebSocket 认证尝试始终受到节流限制，且不豁免回环地址（纵深防御，防止基于浏览器的本地回环暴力破解）。
- `tailscale.mode`：`serve`（仅限 Tailnet，回环绑定）或 `funnel`（公开访问，需认证）。
- `controlUi.allowedOrigins`：针对网关 WebSocket 连接的浏览器来源显式白名单。当预期有来自非回环地址的浏览器客户端时，此项为必需。
- `controlUi.dangerouslyAllowHostHeaderOriginFallback`：危险模式，为有意依赖 Host 头来源策略的部署启用 Host 头来源回退机制。
- `remote.transport`：`ssh`（默认）或 `direct`（ws/wss）。对于 `direct`，`remote.url` 必须为 `ws://` 或 `wss://`。
- `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`：客户端侧应急覆盖机制，允许明文 `ws://` 连接到受信任的私有网络 IP；明文连接的默认范围仍仅为回环地址。
- `gateway.remote.token` / `.password` 是远程客户端凭据字段。它们本身并不配置网关认证。
- 本地网关调用路径可在 `gateway.auth.*` 未设置时，使用 `gateway.remote.*` 作为回退方案。
- `trustedProxies`：终止 TLS 的反向代理 IP 地址。仅列出您可控的代理。
- `allowRealIpFallback`：当启用 `true` 时，若缺少 `X-Forwarded-For`，网关将接受 `X-Real-IP`。默认为 `false`，以实现故障关闭行为。
- `gateway.tools.deny`：针对 HTTP `POST /tools/invoke` 额外屏蔽的工具名称（扩展默认拒绝列表）。
- `gateway.tools.allow`：从默认 HTTP 拒绝列表中移除工具名称。

</Accordion>

### 兼容 OpenAI 的端点

- 聊天补全（Chat Completions）：默认禁用。通过 `gateway.http.endpoints.chatCompletions.enabled: true` 启用。
- 响应 API（Responses API）：`gateway.http.endpoints.responses.enabled`。
- 响应 URL 输入加固：
  - `gateway.http.endpoints.responses.maxUrlParts`
  - `gateway.http.endpoints.responses.files.urlAllowlist`
  - `gateway.http.endpoints.responses.images.urlAllowlist`
- 可选响应加固头字段：
  - `gateway.http.securityHeaders.strictTransportSecurity`（仅对您可控的 HTTPS 来源设置；参见 [可信代理认证](/gateway/trusted-proxy-auth#tls-termination-and-hsts)）

### 多实例隔离

在单台主机上运行多个网关，需使用不同的端口和状态目录：

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json \
OPENCLAW_STATE_DIR=~/.openclaw-a \
openclaw gateway --port 19001
```

便捷标志：`--dev`（使用 `~/.openclaw-dev` + 端口 `19001`）、`--profile <name>`（使用 `~/.openclaw-<name>`）。

参见 [多个网关](/gateway/multiple-gateways)。

---

## 钩子（Hooks）

Auth: `Authorization: Bearer <token>` 或 `x-openclaw-token: <token>`。

**Endpoints:**

- `POST /hooks/wake` → `{ text, mode?: "now"|"next-heartbeat" }`
- `POST /hooks/agent` → `{ message, name?, agentId?, sessionKey?, wakeMode?, deliver?, channel?, to?, model?, thinking?, timeoutSeconds? }`
  - 仅当 `hooks.allowRequestSessionKey=true` 时接受来自请求负载的 `sessionKey` (默认值：`false`)。
- `POST /hooks/<name>` → 通过 `hooks.mappings` 解析

<Accordion title="Mapping details">

- `match.path` 匹配 `/hooks` 后的子路径 (例如：`/hooks/gmail` → `gmail`)。
- `match.source` 为通用路径匹配一个负载字段。
- 像 `{{messages[0].subject}}` 这样的模板从负载中读取。
- `transform` 可以指向返回钩子操作的 JS/TS 模块。
  - `transform.module` 必须是相对路径且保持在 `hooks.transformsDir` 内 (绝对路径和遍历会被拒绝)。
- `agentId` 路由到特定 Agent；未知 ID 回退到默认值。
- `allowedAgentIds`：限制显式路由 (`*` 或未省略 = 允许所有，`[]` = 拒绝所有)。
- `defaultSessionKey`：用于没有显式 `sessionKey` 的钩子 Agent 运行的可选固定会话键。
- `allowRequestSessionKey`：允许 `/hooks/agent` 调用者设置 `sessionKey` (默认值：`false`)。
- `allowedSessionKeyPrefixes`：用于显式 `sessionKey` 值的可选前缀白名单 (请求 + 映射)，例如 `["hook:"]`。
- `deliver: true` 将最终回复发送到频道；`channel` 默认为 `last`。
- `model` 覆盖此钩子运行的 LLM (如果设置了模型目录则必须允许)。

</Accordion>

### Gmail 集成

```json5
{
  hooks: {
    gmail: {
      account: "openclaw@gmail.com",
      topic: "projects/<project-id>/topics/gog-gmail-watch",
      subscription: "gog-gmail-watch-push",
      pushToken: "shared-push-token",
      hookUrl: "http://127.0.0.1:18789/hooks/gmail",
      includeBody: true,
      maxBytes: 20000,
      renewEveryMinutes: 720,
      serve: { bind: "127.0.0.1", port: 8788, path: "/" },
      tailscale: { mode: "funnel", path: "/gmail-pubsub" },
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

- 配置的 Gateway 在启动时自动启动 `gog gmail watch serve`。设置 `OPENCLAW_SKIP_GMAIL_WATCHER=1` 以禁用。
- 不要与 Gateway 并行运行单独的 `gog gmail watch serve`。

---

## Canvas 主机

```json5
{
  canvasHost: {
    root: "~/.openclaw/workspace/canvas",
    liveReload: true,
    // enabled: false, // or OPENCLAW_SKIP_CANVAS_HOST=1
  },
}
```

- 在 Gateway 端口下通过 HTTP 提供 Agent 可编辑的 HTML/CSS/JS 和 A2UI：
  - `http://<gateway-host>:<gateway.port>/__openclaw__/canvas/`
  - `http://<gateway-host>:<gateway.port>/__openclaw__/a2ui/`
- 仅限本地：保持 `gateway.bind: "loopback"` (默认值)。
- 非回环绑定：Canvas 路由需要 Gateway 认证 (令牌/密码/可信代理)，与其他 Gateway HTTP 表面相同。
- Node WebViews 通常不发送认证头；节点配对并连接后，Gateway 会发布用于 Canvas/A2UI 访问的节点范围能力 URL。
- 能力 URL 绑定到活动的节点 WS 会话并快速过期。不使用基于 IP 的回退。
- 注入实时重载客户端到提供的 HTML 中。
- 为空时自动创建 Starter `index.html`。
- 还在 `/__openclaw__/a2ui/` 处提供 A2UI。
- 更改需要重启 Gateway。
- 对于大型目录或 `EMFILE` 错误，禁用实时重载。

---

## Discovery

### mDNS (Bonjour)

```json5
{
  discovery: {
    mdns: {
      mode: "minimal", // minimal | full | off
    },
  },
}
```

- `minimal` (默认值)：从 TXT 记录中省略 `cliPath` + `sshPort`。
- `full`：包含 `cliPath` + `sshPort`。
- 主机名默认为 `openclaw`。使用 `OPENCLAW_MDNS_HOSTNAME` 覆盖。

### 广域网 (DNS-SD)

```json5
{
  discovery: {
    wideArea: { enabled: true },
  },
}
```

在 `~/.openclaw/dns/` 下写入单播 DNS-SD 区域。为了实现跨网络发现，与 DNS 服务器 (推荐 CoreDNS) + Tailscale 拆分 DNS 配对。

设置：`openclaw dns setup --apply`。

---

## Environment

### `env` (内联环境变量)

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: {
      GROQ_API_KEY: "gsk-...",
    },
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

- 仅当进程 Env 缺少该键时才应用内联 Env Vars。
- `.env` 文件：CWD `.env` + `~/.openclaw/.env` (两者均不覆盖现有变量)。
- `shellEnv`：从您的登录 Shell 配置文件导入缺失的预期键。
- 有关完整优先级，请参阅 [Environment](/help/environment)。

### Env 变量替换

在任何 Config 字符串中使用 `${VAR_NAME}` 引用 Env Vars：

```json5
{
  gateway: {
    auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" },
  },
}
```

- 仅匹配大写名称：`[A-Z_][A-Z0-9_]*`。
- 缺失/空变量在 Config 加载时抛出错误。
- 使用 `$${VAR}` 转义以获得字面量 `${VAR}`。
- 适用于 `$include`。

---

## Secrets

Secret Refs 是累加的：明文值仍然有效。

### `SecretRef`

使用一种对象形状：

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

验证：

- `provider` 模式：`^[a-z][a-z0-9_-]{0,63}$`
- `source: "env"` ID 模式：`^[A-Z][A-Z0-9_]{0,127}$`
- `source: "file"` ID：绝对 JSON 指针 (例如 `"/providers/openai/apiKey"`)
- `source: "exec"` ID 模式：`^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$`

### 支持的 Credential Surface

- 标准矩阵：[SecretRef Credential Surface](/reference/secretref-credential-surface)
- `secrets apply` 目标支持 `openclaw.json` 凭证路径。
- `auth-profiles.json` Refs 包含在运行时解析和审计覆盖中。

### Secret Providers Config

```json5
{
  secrets: {
    providers: {
      default: { source: "env" }, // optional explicit env provider
      filemain: {
        source: "file",
        path: "~/.openclaw/secrets.json",
        mode: "json",
        timeoutMs: 5000,
      },
      vault: {
        source: "exec",
        command: "/usr/local/bin/openclaw-vault-resolver",
        passEnv: ["PATH", "VAULT_ADDR"],
      },
    },
    defaults: {
      env: "default",
      file: "filemain",
      exec: "vault",
    },
  },
}
```

注意：

- `file` Provider 支持 `mode: "json"` 和 `mode: "singleValue"` (`id` 在 singleValue 模式下必须为 `"value"`)。
- `exec` Provider 需要绝对 `command` 路径并使用协议负载在 stdin/stdout 上。
- 默认情况下，符号链接命令路径被拒绝。设置 `allowSymlinkCommand: true` 以允许符号链接路径同时验证解析的目标路径。
- 如果配置了 `trustedDirs`，则可信目录检查适用于解析的目标路径。
- `exec` 子环境默认最小；使用 `passEnv` 显式传递所需变量。
- Secret Refs 在激活时间解析为内存快照，然后请求路径仅读取快照。
- 活动表面过滤在激活期间应用：启用表面上未解析的 Refs 会导致启动/重载失败，而 inactive 表面会被跳过并带有诊断信息。

---

## Auth 存储

```json5
{
  auth: {
    profiles: {
      "anthropic:me@example.com": { provider: "anthropic", mode: "oauth", email: "me@example.com" },
      "anthropic:work": { provider: "anthropic", mode: "api_key" },
    },
    order: {
      anthropic: ["anthropic:me@example.com", "anthropic:work"],
    },
  },
}
```

- 每个 Agent 的 Profile 存储在 `<agentDir>/auth-profiles.json`。
- `auth-profiles.json` 支持值级 Refs (`keyRef` 用于 `api_key`，`tokenRef` 用于 `token`)。
- 静态运行时凭据来自内存解析快照；发现的遗留静态 `auth.json` 条目会被清除。
- 遗留 OAuth 导入自 `~/.openclaw/credentials/oauth.json`。
- 请参阅 [OAuth](/concepts/oauth)。
- Secrets 运行时行为和 `audit/configure/apply` 工具：[Secrets Management](/gateway/secrets)。

---

## Logging

```json5
{
  logging: {
    level: "info",
    file: "/tmp/openclaw/openclaw.log",
    consoleLevel: "info",
    consoleStyle: "pretty", // pretty | compact | json
    redactSensitive: "tools", // off | tools
    redactPatterns: ["\\bTOKEN\\b\\s*[=:]\\s*([\"']?)([^\\s\"']+)\\1"],
  },
}
```

- 默认日志文件：`/tmp/openclaw/openclaw-YYYY-MM-DD.log`。
- 设置 `logging.file` 以获得稳定路径。
- 当 `--verbose` 时，`consoleLevel` 升级到 `debug`。

---

## CLI

```json5
{
  cli: {
    banner: {
      taglineMode: "off", // random | default | off
    },
  },
}
```

- `cli.banner.taglineMode` 控制横幅标语样式：
  - `"random"` (默认值)：旋转的有趣/季节性标语。
  - `"default"`：固定的中性标语 (`All your chats, one OpenClaw.`)。
  - `"off"`：无标语文本 (仍显示横幅标题/版本)。
- 要隐藏整个横幅 (不仅仅是标语)，设置 Env `OPENCLAW_HIDE_BANNER=1`。

---

## Wizard

由 CLI 向导写入的元数据 (`onboard`, `configure`, `doctor`)：

```json5
{
  wizard: {
    lastRunAt: "2026-01-01T00:00:00.000Z",
    lastRunVersion: "2026.1.4",
    lastRunCommit: "abc1234",
    lastRunCommand: "configure",
    lastRunMode: "local",
  },
}
```

---

## Identity

由 macOS 启动向导编写。派生默认值：

- ``messages.ackReaction`` 来自 ``identity.emoji``（回退到 👀）
- ``mentionPatterns`` 来自 ``identity.name``/``identity.emoji``
- ``avatar`` 接受：工作区相对路径、``http(s)`` URL 或 ``data:`` URI

---

## 桥接（旧版，已移除）

当前版本不再包含 TCP 桥接。节点通过 Gateway WebSocket 连接。``bridge.*`` 键不再属于配置架构（在移除之前验证会失败；``openclaw doctor --fix`` 可以剥离未知键）。

<Accordion title="旧版桥接配置（历史参考）">

````json
{
  "bridge": {
    "enabled": true,
    "port": 18790,
    "bind": "tailnet",
    "tls": {
      "enabled": true,
      "autoGenerate": true
    }
  }
}
````

</Accordion>

---

## Cron

````json5
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 2,
    webhook: "https://example.invalid/legacy", // deprecated fallback for stored notify:true jobs
    webhookToken: "replace-with-dedicated-token", // optional bearer token for outbound webhook auth
    sessionRetention: "24h", // duration string or false
    runLog: {
      maxBytes: "2mb", // default 2_000_000 bytes
      keepLines: 2000, // default 2000
    },
  },
}
````

- ``sessionRetention``：在完成隔离的 cron 运行会话从 ``sessions.json`` 修剪前保留多长时间。还控制归档的已删除 cron 转录本的清理。默认值：``24h``；设置 ``false`` 以禁用。
- ``runLog.maxBytes``：每个运行日志文件的最大大小（``cron/runs/<jobId>.jsonl``），用于修剪前。默认值：``2_000_000`` 字节。
- ``runLog.keepLines``：触发运行日志修剪时保留的最新行数。默认值：``2000``。
- ``webhookToken``：用于 cron webhook POST 传递的 bearer token（``delivery.mode = "webhook"``），如果省略则不发送认证头。
- ``webhook``：弃用的旧版回退 webhook URL（http/https），仅用于仍具有 ``notify: true`` 的存储作业。

请参阅 [Cron Jobs](/automation/cron-jobs)。

---

## 媒体模型模板变量

在 ``tools.media.models[].args`` 中展开的模板占位符：

| Variable           | Description                                       |
| ------------------ | ------------------------------------------------- |
| ``{{Body}}``         | 完整入站消息体                         |
| ``{{RawBody}}``      | 原始主体（无历史记录/发件人包装器）             |
| ``{{BodyStripped}}`` | 去除群组提及的消息体                 |
| ``{{From}}``         | 发件人标识符                                 |
| ``{{To}}``           | 目标标识符                            |
| ``{{MessageSid}}``   | 频道消息 ID                                |
| ``{{SessionId}}``    | 当前会话 UUID                              |
| ``{{IsNewSession}}`` | 创建新会话时的 ``"true"``                 |
| ``{{MediaUrl}}``     | 入站媒体伪 URL                          |
| ``{{MediaPath}}``    | 本地媒体路径                                  |
| ``{{MediaType}}``    | 媒体类型（图像/音频/文档/…）               |
| ``{{Transcript}}``   | 音频转录                                  |
| ``{{Prompt}}``       | CLI 条目解析后的媒体提示             |
| ``{{MaxChars}}``     | CLI 条目解析后的最大输出字符数         |
| ``{{ChatType}}``     | ``"direct"`` 或 ``"group"``                           |
| ``{{GroupSubject}}`` | 群组主题（尽力而为）                       |
| ``{{GroupMembers}}`` | 群组成员预览（尽力而为）               |
| ``{{SenderName}}``   | 发件人显示名称（尽力而为）                 |
| ``{{SenderE164}}``   | 发件人电话号码（尽力而为）                 |
| ``{{Provider}}``     | 提供者提示（WhatsApp、Telegram、Discord 等） |

---

## 配置包含 (``$include``)

将配置拆分为多个文件：

````json5
// ~/.openclaw/openclaw.json
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
  broadcast: {
    $include: ["./clients/mueller.json5", "./clients/schmidt.json5"],
  },
}
````

**合并行为：**

- 单个文件：替换包含的对象。
- 文件数组：按顺序深度合并（后面的覆盖前面的）。
- 同级键：在包含之后合并（覆盖包含的值）。
- 嵌套包含：最多 10 层深。
- 路径：相对于包含文件解析，但必须保持在顶级配置目录内（``dirname`` 中的 ``openclaw.json``）。仅当它们仍然解析在该边界内时，才允许绝对/``../`` 形式。
- 错误：针对缺失文件、解析错误和循环包含的清晰消息。

---

_Related: [Configuration](/gateway/configuration) · [Configuration Examples](/gateway/configuration-examples) · [Doctor](/gateway/doctor)_