---
title: "Configuration Reference"
description: "Complete field-by-field reference for ~/.openclaw/openclaw.json"
summary: "Complete reference for every OpenClaw config key, defaults, and channel settings"
read_when:
  - You need exact field-level config semantics or defaults
  - You are validating channel, model, gateway, or tool config blocks
---
# 配置参考

``~/.openclaw/openclaw.json`` 中可用的所有字段。如需面向任务的概览，请参阅 [配置](/gateway/configuration)。

配置格式为 **JSON5**（允许注释和末尾逗号）。所有字段均为可选 —— 若未指定，OpenClaw 将使用安全的默认值。

---

## 通道（Channels）

只要其配置节存在，每个通道便会自动启动（除非设置了 ``enabled: false``）。

### 私聊（DM）与群组访问

所有通道均支持私聊策略和群组策略：

| 私聊策略           | 行为                                                                 |
| ------------------- | -------------------------------------------------------------------- |
| ``pairing``（默认） | 未知发送者将获得一次性配对码；需所有者批准                             |
| ``allowlist``         | 仅允许 ``allowFrom`` 中的发送者（或已配对并存入白名单的发送者）     |
| ``open``              | 允许所有入站私聊（需启用 ``allowFrom: ["*"]``）                         |
| ``disabled``          | 忽略所有入站私聊                                                     |

| 群组策略            | 行为                                                         |
| --------------------- | ------------------------------------------------------------ |
| ``allowlist``（默认） | 仅允许匹配所配置白名单的群组                                 |
| ``open``                | 绕过群组白名单（提及门控机制仍生效）                           |
| ``disabled``            | 拦截所有群组/聊天室消息                                      |

<Note>
__CODE_BLOCK_11__ sets the default when a provider's __CODE_BLOCK_12__ is unset.
Pairing codes expire after 1 hour. Pending DM pairing requests are capped at **3 per channel**.
If a provider block is missing entirely (__CODE_BLOCK_13__ absent), runtime group policy falls back to __CODE_BLOCK_14__ (fail-closed) with a startup warning.
</Note>

### 通道模型覆盖（Channel model overrides）

使用 ``channels.modelByChannel`` 可将特定通道 ID 固定绑定至某个模型。其值接受 ``provider/model`` 或已配置的模型别名。当会话尚未存在模型覆盖（例如，未通过 ``/model`` 设置）时，该通道映射才会生效。

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

### 通道默认值与心跳（Channel defaults and heartbeat）

使用 ``channels.defaults`` 可在各提供商间共享群组策略与心跳行为：

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

- ``channels.defaults.groupPolicy``：当提供商层级的 ``groupPolicy`` 未设置时，作为群组策略的回退选项。
- ``channels.defaults.heartbeat.showOk``：在心跳输出中包含健康通道的状态。
- ``channels.defaults.heartbeat.showAlerts``：在心跳输出中包含降级/错误状态。
- ``channels.defaults.heartbeat.useIndicator``：以紧凑的指示器风格渲染心跳输出。

### WhatsApp

WhatsApp 通过网关的 Web 通道（Baileys Web）运行。当存在已关联的会话时，它将自动启动。

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

<Accordion title="多账号 WhatsApp">

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

- 出站命令默认使用账号 ``default``（若存在）；否则使用按字典序排列的第一个已配置账号 ID。
- 可选的 ``channels.whatsapp.defaultAccount`` 可在匹配某个已配置账号 ID 时，覆盖上述默认账号选择逻辑。
- 遗留的单账号 Baileys 认证目录由 ``openclaw doctor`` 迁移至 ``whatsapp/default``。
- 每账号覆盖项：``channels.whatsapp.accounts.<id>.sendReadReceipts``、``channels.whatsapp.accounts.<id>.dmPolicy``、``channels.whatsapp.accounts.<id>.allowFrom``。

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

- Bot Token：使用 ``channels.telegram.botToken`` 或 ``channels.telegram.tokenFile``，若未指定则对默认账号回退使用 ``TELEGRAM_BOT_TOKEN``。
- 可选的 ``channels.telegram.defaultAccount`` 可在匹配某个已配置账号 ID 时，覆盖默认账号选择逻辑。
- 在多账号配置（含 2 个及以上账号 ID）中，应显式设置默认账号（``channels.telegram.defaultAccount`` 或 ``channels.telegram.accounts.default``），以避免回退路由；若缺失或无效，``openclaw doctor`` 将发出警告。
- ``configWrites: false`` 将阻止 Telegram 发起的配置写入操作（如超级群组 ID 迁移、``/config set|unset``）。
- 顶层 ``bindings[]`` 条目中若包含 ``type: "acp"``，则用于为论坛主题配置持久化的 ACP 绑定（请在 ``match.peer.id`` 中使用规范的 ``chatId:topic:topicId``）。字段语义详见 [ACP Agents](/tools/acp-agents#channel-specific-settings)。
- Telegram 流式预览使用 ``sendMessage`` + ``editMessageText``（适用于私聊与群组聊天）。
- 重试策略：参见 [重试策略](/concepts/retry)。

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

- 令牌：`channels.discord.token`，默认账户回退至 `DISCORD_BOT_TOKEN`。  
- 可选的 `channels.discord.defaultAccount` 在匹配已配置账户 ID 时，覆盖默认账户选择。  
- 投递目标使用 `user:<id>`（私信）或 `channel:<id>`（服务器频道）；纯数字 ID 将被拒绝。  
- 服务器 slug 全小写，空格替换为 `-`；频道键使用 slug 化名称（不含 `#`）。优先使用服务器 ID。  
- 默认忽略机器人发送的消息。启用 `allowBots: true` 可接收所有机器人消息；使用 `allowBots: "mentions"` 则仅接受提及本机器人的机器人消息（自身发送的消息仍被过滤）。  
- `channels.discord.guilds.<id>.ignoreOtherMentions`（及频道级覆盖项）将丢弃提及了其他用户或角色但未提及本机器人的消息（排除 @everyone/@here）。  
- `maxLinesPerMessage`（默认值为 17）会在消息高度超标时进行分段，即使总长度未达 2000 字符。  
- `channels.discord.threadBindings` 控制 Discord 线程绑定式路由：  
  - `enabled`：Discord 对线程绑定会话功能的覆盖设置（包括 `/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`，以及绑定投递/路由）  
  - `idleHours`：Discord 对非活跃状态自动失焦（单位：小时）的覆盖设置（`0` 禁用该行为）  
  - `maxAgeHours`：Discord 对硬性最大存活时长（单位：小时）的覆盖设置（`0` 禁用该行为）  
  - `spawnSubagentSessions`：用于 `sessions_spawn({ thread: true })` 自动创建/绑定线程的可选开关  
- 顶层 `bindings[]` 条目中若含 `type: "acp"`，则为频道与线程配置持久化 ACP 绑定（在 `match.peer.id` 中填入频道/线程 ID）。字段语义详见 [ACP Agents](/tools/acp-agents#channel-specific-settings)。  
- `channels.discord.ui.components.accentColor` 设置 Discord 组件 v2 容器的强调色。  
- `channels.discord.voice` 启用 Discord 语音频道对话，并支持可选的自动加入及 TTS 覆盖设置。  
- `channels.discord.voice.daveEncryption` 和 `channels.discord.voice.decryptionFailureTolerance` 直接透传至 `@discordjs/voice` 的 DAVE 选项（默认为 `true` 和 `24`）。  
- OpenClaw 还会在多次解密失败后，通过退出并重新加入语音会话的方式尝试恢复语音接收。  
- `channels.discord.streaming` 是标准流模式键。旧版 `streamMode` 及布尔型 `streaming` 值将自动迁移。  
- `channels.discord.autoPresence` 将运行时可用性映射为机器人在线状态（健康 → 在线，降级 → 空闲，耗尽 → 忙碌），并支持可选的状态文本覆盖。  
- `channels.discord.dangerouslyAllowNameMatching` 重新启用可变名称/标签匹配（应急兼容模式）。  

**表情反应通知模式：** `off`（无）、`own`（仅机器人发送的消息，默认）、`all`（所有消息）、`allowlist`（从 `guilds.<id>.users` 开始的所有消息）。  

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

- 服务账号 JSON：内联方式（`serviceAccount`）或文件方式（`serviceAccountFile`）。  
- 也支持服务账号 SecretRef（`serviceAccountRef`）。  
- 环境变量回退：`GOOGLE_CHAT_SERVICE_ACCOUNT` 或 `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`。  
- 投递目标使用 `spaces/<spaceId>` 或 `users/<userId>`。  
- `channels.googlechat.dangerouslyAllowNameMatching` 重新启用可变邮箱主体匹配（应急兼容模式）。  

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

- **Socket 模式** 需同时配置 `botToken` 和 `appToken`（默认账户环境变量回退需配合 `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN`）。  
- **HTTP 模式** 需配置 `botToken` 加上 `signingSecret`（可在根层级或按账户分别配置）。  
- `configWrites: false` 阻止 Slack 发起的配置写入操作。  
- 可选的 `channels.slack.defaultAccount` 在匹配已配置账户 ID 时，覆盖默认账户选择。  
- `channels.slack.streaming` 是标准流模式键。旧版 `streamMode` 及布尔型 `streaming` 值将自动迁移。  
- 投递目标使用 `user:<id>`（私信）或 `channel:<id>`。  

**表情反应通知模式：** `off`、`own`（默认）、`all`、`allowlist`（从 `reactionAllowlist` 开始）。  

**线程会话隔离：** `thread.historyScope` 为每线程独立（默认）或跨频道共享。`thread.inheritParent` 将父频道对话记录复制到新线程中。  

- `typingReaction` 在回复处理期间，为入站 Slack 消息临时添加一个表情反应，处理完成后移除。请使用 Slack 表情短代码，例如 `"hourglass_flowing_sand"`。  

| 动作组     | 默认值  | 说明                     |  
| ------------ | ------- | -------------------------- |  
| reactions    | enabled | 表情反应 + 列出表情反应     |  
| messages     | enabled | 读取/发送/编辑/删除消息     |  
| pins         | enabled | 置顶/取消置顶/列出置顶项    |  
| memberInfo   | enabled | 成员信息                   |  
| emojiList    | enabled | 自定义表情列表              |  

### Mattermost  

Mattermost 以插件形式提供：`openclaw plugins install @openclaw/mattermost`。  

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

聊天模式：`oncall`（仅在 @ 提及本机器人时响应，默认）、`onmessage`（每条消息均响应）、`onchar`（仅响应以触发前缀开头的消息）。  

当启用 Mattermost 原生命令时：  

- `commands.callbackPath` 必须为路径（例如 `/api/channels/mattermost/command`），而非完整 URL。  
- `commands.callbackUrl` 必须解析为 OpenClaw 网关端点，且 Mattermost 服务器必须能访问该地址。  
- 对于私有网络/尾部网络/内部回调主机，Mattermost 可能要求  
  `ServiceSettings.AllowedUntrustedInternalConnections` 中包含回调主机名/域名。  
  请仅填写主机名/域名，勿填完整 URL。  
- `channels.mattermost.configWrites`：允许或禁止 Mattermost 发起的配置写入。  
- `channels.mattermost.requireMention`：在频道中回复前，强制要求 `@mention`。  
- 可选的 `channels.mattermost.defaultAccount` 在匹配已配置账户 ID 时，覆盖默认账户选择。  

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

**表情反应通知模式：** `off`、`own`（默认）、`all`、`allowlist`（从 `reactionAllowlist` 开始）。  

- `channels.signal.account`：将频道启动固定至特定 Signal 账户身份。  
- `channels.signal.configWrites`：允许或禁止 Signal 发起的配置写入。  
- 可选的 `channels.signal.defaultAccount` 在匹配已配置账户 ID 时，覆盖默认账户选择。  

### BlueBubbles  

BlueBubbles 是推荐的 iMessage 接入路径（由插件支持，配置位于 `channels.bluebubbles` 下）。  

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

- 此处涵盖的核心密钥路径：`channels.bluebubbles`、`channels.bluebubbles.dmPolicy`。  
- 可选的 `channels.bluebubbles.defaultAccount` 在匹配已配置账户 ID 时，覆盖默认账户选择。  
- BlueBubbles 频道的完整配置详见 [BlueBubbles](/channels/bluebubbles)。  

### iMessage  

OpenClaw 启动 `imsg rpc`（基于 stdio 的 JSON-RPC）。无需守护进程或端口监听。

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

- 可选的 `channels.imessage.defaultAccount` 在匹配已配置的账号 ID 时，会覆盖默认账号选择。

- 需要对“信息”数据库（Messages DB）授予“完全磁盘访问权限”（Full Disk Access）。
- 优先使用 `chat_id:<id>` 目标；使用 `imsg chats --limit 20` 列出聊天会话。
- `cliPath` 可指向 SSH 封装脚本；为通过 SCP 获取附件，请设置 `remoteHost`（即 `host` 或 `user@host`）。
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

- 此处涵盖的核心密钥路径：`channels.msteams`、`channels.msteams.configWrites`。
- 完整的 Teams 配置（含凭据、Webhook、私聊/群聊策略，以及按团队/按频道的覆盖配置）详见 [Microsoft Teams](/channels/msteams)。

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

- 此处涵盖的核心密钥路径：`channels.irc`、`channels.irc.dmPolicy`、`channels.irc.configWrites`、`channels.irc.nickserv.*`。
- 可选的 `channels.irc.defaultAccount` 在匹配已配置的账号 ID 时，会覆盖默认账号选择。
- 完整的 IRC 频道配置（含主机/端口/TLS/频道列表/白名单/提及门控）详见 [IRC](/channels/irc)。

### 多账号（所有频道）

每个频道可运行多个账号（每个账号拥有独立的 `accountId`）：

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

- 当未指定 `accountId`（命令行界面 + 路由）时，使用 `default`。
- 环境变量令牌（Env tokens）仅适用于**默认账号**。
- 基础频道设置适用于所有账号，除非为各账号单独覆盖。
- 使用 `bindings[].match.accountId` 可将每个账号路由至不同代理（agent）。
- 若在仍采用单账号顶层频道配置的情况下，通过 `openclaw channels add`（或频道接入流程）添加非默认账号，OpenClaw 会首先将账号作用域内的顶层单账号值移入 `channels.<channel>.accounts.default`，以确保原始账号继续正常工作。
- 已存在的仅限频道的绑定（不含 `accountId`）仍将匹配默认账号；账号作用域的绑定仍为可选项。
- `openclaw doctor --fix` 还可通过在存在命名账号但缺少 `default` 时，将账号作用域内的顶层单账号值移入 `accounts.default`，来修复混合配置形态。

### 其他扩展频道

许多扩展频道被配置为 `channels.<id>`，并在其专属频道页面中提供文档说明（例如飞书 Feishu、Matrix、LINE、Nostr、Zalo、Nextcloud Talk、Synology Chat 和 Twitch）。
参见完整频道索引：[Channels](/channels)。

### 群聊提及门控（Mention Gating）

群组消息默认**要求提及**（metadata 提及或正则表达式模式）。该机制适用于 WhatsApp、Telegram、Discord、Google Chat 和 iMessage 的群组聊天。

**提及类型：**

- **Metadata 提及**：平台原生的 @-提及。在 WhatsApp 自聊模式下会被忽略。
- **文本模式**：`agents.list[].groupChat.mentionPatterns` 中定义的正则表达式模式。始终进行检查。
- 仅当检测可行时（即存在原生提及，或至少配置了一个模式），才强制执行提及门控。

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

`messages.groupChat.historyLimit` 设置全局默认值。各频道可通过 `channels.<channel>.historyLimit`（或按账号）覆盖该设置。设置 `0` 可禁用该功能。

#### 私聊历史记录限制（DM history limits）

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

解决顺序：按私聊覆盖 → 提供商默认值 → 无限制（全部保留）。

支持的渠道：`telegram`、`whatsapp`、`discord`、`slack`、`signal`、`imessage`、`msteams`。

#### 自聊模式（Self-chat mode）

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
- `native: "auto"` 为 Discord/Telegram 启用原生命令，但 Slack 默认关闭。
- 按频道覆盖：`channels.discord.commands.native`（布尔值或 `"auto"`）。`false` 将清除此前已注册的命令。
- `channels.telegram.customCommands` 为 Telegram 机器人菜单添加额外条目。
- `bash: true` 启用 `! <cmd>`（用于宿主 shell）。需同时启用 `tools.elevated.enabled`，且发送者须在 `tools.elevated.allowFrom.<channel>` 中。
- `config: true` 启用 `/config`（读写 `openclaw.json`）。对于网关 `chat.send` 客户端，若需持久化 `/config set|unset` 写入，还需启用 `operator.admin`；只读的 `/config show` 对普通写作用域的操作员客户端保持可用。
- `channels.<provider>.configWrites` 按频道控制配置变更的门控（默认：true）。
- `allowFrom` 是按提供商设置的。一旦启用，它将成为**唯一**的授权来源（频道白名单/配对及 `useAccessGroups` 将被忽略）。
- `useAccessGroups: false` 允许命令在未设置 `allowFrom` 时绕过访问组策略。

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

系统提示符（system prompt）中“运行时”（Runtime）行所显示的可选仓库根目录。若未设置，OpenClaw 将从工作区向上遍历自动检测。

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skipBootstrap`

禁用工作区启动文件（bootstrap files）的自动创建（即 `AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、`BOOTSTRAP.md`）。

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.bootstrapMaxChars`

工作区启动文件在截断前的最大字符数。默认值：`20000`。

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

所有工作区启动文件注入内容的总字符数上限。默认值：`150000`。

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

控制在启动上下文被截断时，向代理可见的警告文本行为。
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

在向提供商发起调用前，对话记录/工具图像块中图像最长边的最大像素尺寸。
默认值：`1200`。

较低的值通常可减少视觉 token 消耗，并减小截图密集型任务的请求负载大小；
较高的值则能保留更多视觉细节。

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

系统提示符上下文所用的时区（非消息时间戳）。若未设置，则回退至主机时区。

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

- `model`：接受字符串（`"provider/model"`）或对象（`{ primary, fallbacks }`）。
  - 字符串形式仅设置主模型。
  - 对象形式设置主模型及有序的故障转移模型。
- `imageModel`：接受字符串（`"provider/model"`）或对象（`{ primary, fallbacks }`）。
  - 由 `image` 工具路径用作其视觉模型配置。
  - 同时也作为备选路由机制，当所选/默认模型无法接受图像输入时启用。
- `pdfModel`：接受字符串（`"provider/model"`）或对象（`{ primary, fallbacks }`）。
  - 由 `pdf` 工具用于模型路由。
  - 若未指定，则 PDF 工具将回退至 `imageModel`，再进一步回退至尽力而为的提供商默认值。
- `pdfMaxBytesMb`：当调用时未传入 `maxBytesMb` 时，`pdf` 工具所采用的默认 PDF 大小限制。
- `pdfMaxPages`：`pdf` 工具在提取回退模式下默认考虑的最大页数。
- `model.primary`：格式为 `provider/model`（例如 `anthropic/claude-opus-4-6`）。若省略提供商，OpenClaw 将假定为 `anthropic`（已弃用）。
- `models`：为 `/model` 配置的模型目录与白名单。每个条目可包含 `alias`（快捷方式）和 `params`（提供商特定字段，例如 `temperature`、`maxTokens`、`cacheRetention`、`context1m`）。
- `params` 合并优先级（配置）：`agents.defaults.models["provider/model"].params` 为基底，随后 `agents.list[].params`（匹配 agent ID）按键覆盖。
- 修改这些字段的配置编写器（例如 `/models set`、`/models set-image` 及回退增删命令）会保存标准的对象形式，并尽可能保留现有回退列表。
- `maxConcurrent`：跨会话的最大并行 agent 运行数（各会话内部仍为串行）。默认值：1。

**内置别名快捷方式**（仅当模型位于 `agents.defaults.models` 中时生效）：

| 别名           | 模型                            |
| -------------- | ------------------------------- |
| `opus`         | `anthropic/claude-opus-4-6`     |
| `sonnet`       | `anthropic/claude-sonnet-4-5`   |
| `gpt`          | `openai/gpt-5.2`                |
| `gpt-mini`     | `openai/gpt-5-mini`             |
| `gemini`       | `google/gemini-3.1-pro-preview` |
| `gemini-flash` | `google/gemini-3-flash-preview` |

您所配置的别名始终优先于默认值。

Z.AI GLM-4.x 模型默认自动启用思考模式，除非您设置了 `--thinking off` 或自行定义了 `agents.defaults.models["zai/<model>"].params.thinking`。
Z.AI 模型默认为工具调用流式传输启用 `tool_stream`。将 `agents.defaults.models["zai/<model>"].params.tool_stream` 设为 `false` 可禁用该功能。
Anthropic Claude 4.6 模型在未显式设定思考级别时，默认采用 `adaptive` 思考模式。

### `agents.defaults.cliBackends`

面向纯文本回退运行（无工具调用）的可选 CLI 后端。当 API 提供商失效时，可用作备用方案。

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

- CLI 后端以文本为先；工具始终被禁用。
- 当设置 `sessionArg` 时支持会话。
- 当 `imageArg` 接受文件路径时，支持图像透传。

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

- `every`：持续时间字符串（毫秒/秒/分/小时）。默认值：`30m`。
- `suppressToolErrorWarnings`：设为 `true` 时，在心跳运行期间抑制工具错误警告载荷。
- `directPolicy`：直接/私信投递策略。`allow`（默认）允许直接目标投递。`block` 抑制直接目标投递，并发出 `reason=dm-blocked`。
- `lightContext`：设为 `true` 时，心跳运行使用轻量级引导上下文，并仅从工作区引导文件中保留 `HEARTBEAT.md`。
- 每个 agent 级别：设置 `agents.list[].heartbeat`。当任一 agent 定义了 `heartbeat` 时，**仅有这些 agent** 执行心跳。
- 心跳执行完整的 agent 轮次——间隔越短，消耗的 token 越多。

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

- `mode`：`default` 或 `safeguard`（针对长历史记录的分块摘要）。参见 [压缩（Compaction）](/concepts/compaction)。
- `identifierPolicy`：`strict`（默认）、`off` 或 `custom`。`strict` 在压缩摘要过程中前置内置不透明标识符保留指导。
- `identifierInstructions`：当启用 `identifierPolicy=custom` 时使用的可选自定义标识符保留文本。
- `postCompactionSections`：压缩后重新注入的可选 AGENTS.md H2/H3 章节名称。默认为 `["Session Startup", "Red Lines"]`；将 `[]` 设为 `false` 可禁用重新注入。若未设置或显式设为此默认对，则旧版 `Every Session`/`Safety` 标题也将作为向后兼容的备选方案被接受。
- `memoryFlush`：自动压缩前的静默 agent 轮次，用于持久化存储记忆。当工作区为只读时跳过此步骤。

### `agents.defaults.contextPruning`

在发送至大语言模型（LLM）前，从内存上下文中修剪**旧的工具结果**。**不会**修改磁盘上的会话历史。

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

- `mode: "cache-ttl"` 启用修剪操作。
- `ttl` 控制修剪再次运行的时间间隔（自上次缓存访问起）。
- 修剪首先软裁剪尺寸过大的工具结果，必要时再硬清除更早的工具结果。

**软裁剪**保留开头 + 结尾，并在中间插入 `...`。

**硬清除** 将整个工具结果替换为占位符。

注意事项：

- 图像块永远不会被裁剪或清除。
- 比例基于字符数（近似值），而非精确的 token 数。
- 若助理消息少于 `keepLastAssistants` 条，则跳过修剪。

</Accordion>

详见 [会话修剪（Session Pruning）](/concepts/session-pruning) 获取详细行为说明。

### 分块流式传输（Block streaming）

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

- 非 Telegram 渠道需显式启用 `*.blockStreaming: true` 才能支持分块回复。
- 渠道级覆盖项：`channels.<channel>.blockStreamingCoalesce`（及每账户变体）。Signal / Slack / Discord / Google Chat 默认为 `minChars: 1500`。
- `humanDelay`：分块回复之间的随机暂停时间。`natural` = 800–2500 毫秒。每 agent 覆盖项：`agents.list[].humanDelay`。

详见 [流式传输（Streaming）](/concepts/streaming) 获取行为与分块细节。

### 输入提示指示器（Typing indicators）

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

- 默认值：直接聊天/提及场景下为 `instant`，未提及的群聊场景下为 `message`。
- 每会话覆盖项：`session.typingMode`、`session.typingIntervalSeconds`。

详见 [输入提示指示器（Typing Indicators）](/concepts/typing-indicators)。

### `agents.defaults.sandbox`

嵌入式代理的可选 **Docker 沙箱化** 功能。完整指南请参阅 [沙箱化](/gateway/sandboxing)。

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

<Accordion title="沙箱详情">

**工作区访问：**

- `none`：在 `~/.openclaw/sandboxes` 下按作用域隔离的沙箱工作区  
- `ro`：沙箱工作区位于 `/workspace`，代理工作区以只读方式挂载至 `/agent`  
- `rw`：代理工作区以读写方式挂载至 `/workspace`

**作用域：**

- `session`：每个会话一个容器 + 工作区  
- `agent`：每个代理一个容器 + 工作区（默认）  
- `shared`：共享容器与工作区（无跨会话隔离）

**`setupCommand`** 在容器创建后仅运行一次（通过 `sh -lc` 触发）。需要网络出口、可写的根文件系统及 root 用户权限。

**容器默认使用 `network: "none"`** —— 若代理需外网访问，请将其设为 `"bridge"`（或自定义桥接网络）。  
`"host"` 被屏蔽。除非显式设置 `sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`（应急通道），否则 `"container:<id>"` 默认被屏蔽。

**入站附件** 将暂存至活动工作区中的 `media/inbound/*`。

**`docker.binds`** 用于挂载额外的宿主机目录；全局绑定与每代理绑定将被合并。

**沙箱化浏览器**（`sandbox.browser.enabled`）：容器内的 Chromium + CDP。noVNC URL 将注入系统提示词中。无需在 `openclaw.json` 中启用 `browser.enabled`。  
noVNC 观察者访问默认使用 VNC 认证，OpenClaw 则生成一个短期有效的令牌 URL（而非在共享 URL 中暴露密码）。

- `allowHostControl: false`（默认）阻止沙箱化会话访问宿主机浏览器。  
- `network` 默认为 `openclaw-sandbox-browser`（专用桥接网络）。仅当明确需要全局桥接连通性时，才设为 `bridge`。  
- `cdpSourceRange` 可选择性地在容器边缘限制 CDP 入站流量，仅允许指定 CIDR 网段（例如 `172.21.0.1/32`）。  
- `sandbox.browser.binds` 仅向沙箱化浏览器容器挂载额外的宿主机目录。一旦设置（包括 `[]`），它将替代浏览器容器的 `docker.binds`。  
- 启动默认值定义于 `scripts/sandbox-browser-entrypoint.sh`，并针对容器宿主机进行了调优：  
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
  - `--disable-3d-apis`、`--disable-software-rasterizer` 和 `--disable-gpu` 默认启用；若 WebGL/3D 使用场景有特殊需求，可通过 `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` 显式禁用。  
  - 若工作流依赖扩展程序，可使用 `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` 重新启用扩展。  
  - 可通过 `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` 修改 `--renderer-process-limit=2`；将 `0` 设为 `null` 即可采用 Chromium 默认进程数限制。  
  - 当启用 `noSandbox` 时，还将启用 `--no-sandbox` 和 `--disable-setuid-sandbox`。  
  - 默认值基于容器镜像基线；如需修改容器默认行为，请使用带自定义入口点（entrypoint）的浏览器自定义镜像。

</Accordion>

构建镜像：

```bash
scripts/sandbox-setup.sh           # main sandbox image
scripts/sandbox-browser-setup.sh   # optional browser image
```

### `agents.list`（每代理覆盖配置）

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

- `id`：稳定的代理 ID（必需）。  
- `default`：当设置多个时，首个生效（并记录警告日志）；若未设置，则列表首项为默认值。  
- `model`：字符串形式仅覆盖 `primary`；对象形式 `{ primary, fallbacks }` 同时覆盖两者（其中 `[]` 将禁用全局回退机制）。仅覆盖 `primary` 的定时任务仍继承默认回退机制，除非显式设置 `fallbacks: []`。  
- `params`：每代理流参数，将合并覆盖 `agents.defaults.models` 中所选模型条目。可用于代理特定的覆盖配置（如 `cacheRetention`、`temperature` 或 `maxTokens`），而无需复制整个模型目录。  
- `runtime`：可选的每代理运行时描述符。当代理应默认使用 ACP harness 会话时，请结合 `type: "acp"` 与 `runtime.acp` 默认值（`agent`、`backend`、`mode`、`cwd`）使用。  
- `identity.avatar`：工作区相对路径、`http(s)` URL 或 `data:` URI。  
- `identity` 推导默认值：`ackReaction` 来自 `emoji`，`mentionPatterns` 来自 `name`/`emoji`。  
- `subagents.allowAgents`：`sessions_spawn` 的代理 ID 白名单（`["*"]` = 任意；默认：仅限同一代理）。  
- 沙箱继承防护：若请求方会话已沙箱化，则 `sessions_spawn` 将拒绝目标代理以非沙箱模式运行。

---

## 多代理路由

在一个 Gateway 内运行多个相互隔离的代理。详见 [多代理](/concepts/multi-agent)。

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

- `type`（可选）：`route` 用于常规路由（缺失类型默认为 route），`acp` 用于持久化 ACP 对话绑定。  
- `match.channel`（必需）  
- `match.accountId`（可选；`*` = 任意账号；省略 = 默认账号）  
- `match.peer`（可选；`{ kind: direct|group|channel, id }`）  
- `match.guildId` / `match.teamId`（可选；频道特定）  
- `acp`（可选；仅适用于 `type: "acp"`）：`{ mode, label, cwd, backend }`

**确定性匹配顺序：**

1. `match.peer`  
2. `match.guildId`  
3. `match.teamId`  
4. `match.accountId`（精确匹配，不涉及 peer/guild/team）  
5. `match.accountId: "*"`（频道范围）  
6. 默认代理  

在每一层级内，首个匹配的 `bindings` 条目胜出。

对于 `type: "acp"` 条目，OpenClaw 依据精确对话身份（`match.channel` + 账号 + `match.peer.id`）进行解析，不采用上述路由绑定层级顺序。

### 每代理访问配置

<Accordion title="完全访问（无沙箱）">

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

<Accordion>

<Accordion title="无文件系统访问（仅限消息传递）">

```yaml
# 示例配置
sandbox:
  filesystem: false
```

</Accordion>

有关优先级详情，请参阅[多智能体沙箱与工具](/tools/multi-agent-sandbox-tools)。

---

## 会话（Session）

```yaml
session:
  # 会话隔离策略
  isolation: "per-channel-sender"
  # 跨渠道会话共享的对等方映射
  peer_map:
    canonical_id_1: "provider1:peer1"
  # 重置策略
  reset_policy: "daily"
  daily_reset_time: "03:00"
  inactivity_timeout_hours: 72
  # 按类型覆盖的重置策略
  type_overrides:
    thread: "inactivity"
    dm: "daily"
  # 分叉线程会话的最大父会话深度
  max_fork_depth: 5
  # 主直接聊天存储桶（已弃用）
  main_bucket: "direct-chat"
  # 会话匹配规则（拒绝优先）
  match_rules:
    - deny: { sender_id: "blocked-user-123" }
  # 会话存储清理与保留控制
  cleanup:
    mode: "warn"
    stale_age_days: 30
    max_entries: 10000
    rotate_size_mb: 100
    transcript_retention_days: 90
    disk_budget_mb: 5000
    budget_mode: "warn"
    budget_target: "50%"
  # 线程绑定会话功能的全局默认值
  thread_defaults:
    enabled: true
    auto_unfocus_hours: 2
    hard_max_age_hours: 168
```

<Accordion title="会话字段详情">

- **`isolation`**: DM（直接消息）的分组方式。
  - `shared`: 所有 DM 共享主会话。
  - `by-sender-id`: 跨渠道按发送者 ID 隔离。
  - `per-channel-sender`: 按渠道 + 发送者隔离（推荐用于多用户收件箱）。
  - `per-account-channel-sender`: 按账号 + 渠道 + 发送者隔离（推荐用于多账号场景）。
- **`peer_map`**: 将规范 ID 映射为带提供方前缀的对等方，以支持跨渠道会话共享。
- **`reset_policy`**: 主重置策略。`daily` 在 `daily_reset_time` 指定的本地时间重置；`inactivity` 在 `inactivity_timeout_hours` 后重置。若两者均配置，则以先到期者为准。
- **`type_overrides`**: 按类型覆盖的重置策略（`thread`、`dm`、`group`）。旧版 `reset_type` 作为 `type_overrides` 的别名仍被接受。
- **`max_fork_depth`**: 创建分叉线程会话时允许的最大父会话 `depth`（默认 `5`）。
  - 若父会话 `depth` 超过该值，OpenClaw 将启动一个全新的线程会话，而非继承父会话的对话历史。
  - 设置 `max_fork_depth: 0` 可禁用此保护机制，并始终允许父会话分叉。
- **`main_bucket`**: 已弃用字段。运行时现在始终使用 `direct-chat` 作为主直接聊天存储桶。
- **`match_rules`**: 按 `sender_id`、`channel_id`（含旧版 `provider_id` 别名）、`account_id` 或 `peer_id` 匹配。首个 `deny` 规则优先生效。
- **`cleanup`**: 会话存储清理与保留控制。
  - `mode`: `warn` 仅发出警告；`apply` 执行实际清理。
  - `stale_age_days`: 过期条目的年龄阈值（默认 `30` 天）。
  - `max_entries`: `session_store` 中最大条目数（默认 `10000`）。
  - `rotate_size_mb`: 当 `transcript_log` 超过该大小时执行轮转（默认 `100` MB）。
  - `transcript_retention_days`: 对话存档的保留天数，默认为 `90`；设为 `0` 可禁用。
  - `disk_budget_mb`: 可选的会话目录磁盘预算。在 `warn` 模式下仅记录警告；在 `apply` 模式下优先删除最旧的产物/会话。
  - `budget_target`: 预算清理后的目标占用率，默认为 `50%` 的 `disk_budget_mb`。
- **`thread_defaults`**: 线程绑定会话功能的全局默认值。
  - `enabled`: 主开关（各提供方可覆盖；Discord 使用 `false`）。
  - `auto_unfocus_hours`: 默认非活跃自动失焦小时数（`0` 表示禁用；各提供方可覆盖）。
  - `hard_max_age_hours`: 默认硬性最大存活小时数（`0` 表示禁用；各提供方可覆盖）。

</Accordion>

---

## 消息（Messages）

```yaml
messages:
  # 响应前缀模板
  response_prefix: "{{model_short}}:"
  # 每渠道/账号覆盖项
  channel_response_prefix: {}
  account_response_prefix: {}
  # 确认反应
  ack_reaction: "✅"
  channel_ack_reaction: {}
  account_ack_reaction: {}
  # 入站防抖
  inbound_debounce_ms: 1000
  # TTS（文本转语音）
  tts:
    enabled: true
    session_override: false
    auto_summary_override: false
    voice: "alloy"
    model: "tts-1"
    api_key: ""
    endpoint: ""
```

### 响应前缀

每渠道/账号覆盖项：`channel_response_prefix`、`account_response_prefix`。

解析顺序（最具体者胜出）：账号 → 渠道 → 全局。`response_prefix: null` 禁用并终止级联。`response_prefix: ""` 推导出 `{{model_short}}:`。

**模板变量：**

| 变量 | 描述 | 示例 |
| ---- | ---- | ---- |
| `{{model_short}}` | 短模型名称 | `gpt-4o` |
| `{{model_id}}` | 完整模型标识符 | `gpt-4o-2024-05-13` |
| `{{provider}}` | 提供方名称 | `openai` |
| `{{thinking_level}}` | 当前思维层级 | `low`、`medium`、`high` |
| `{{identity}}` | 智能体身份名称 | （同 `{{model_short}}`） |

变量不区分大小写。`{{model}}` 是 `{{model_short}}` 的别名。

### 确认反应（Ack reaction）

- 默认使用活跃智能体的 `ack_reaction`，否则回退至 `✅`。设置 `ack_reaction: null` 可禁用。
- 每渠道覆盖项：`channel_ack_reaction`、`account_ack_reaction`。
- 解析顺序：账号 → 渠道 → `ack_reaction` → 身份回退。
- 作用范围：`all`（默认）、`thread`、`dm`、`group`。
- `ack_remove_on_reply`：在回复后移除确认反应（仅 Slack/Discord/Telegram/Google Chat 支持）。

### 入站防抖（Inbound debounce）

将来自同一发送者的快速纯文本消息批处理为单个智能体回合。媒体/附件立即刷新。控制命令绕过防抖。

### TTS（文本转语音）

```yaml
tts:
  enabled: true
  session_override: false
  auto_summary_override: false
  voice: "alloy"
  model: "tts-1"
  api_key: ""
  endpoint: ""
```

- `enabled` 控制自动 TTS。`session_override` 可按会话覆盖。
- `auto_summary_override` 覆盖 `voice` 用于自动摘要。
- `voice` 默认启用；`model` 默认为 `tts-1`（选择性启用）。
- API 密钥依次回退至 `OPENAI_API_KEY`/`AZURE_OPENAI_API_KEY` 和 `TTS_API_KEY`。
- `endpoint` 覆盖 OpenAI TTS 端点。解析顺序为配置项 → `OPENAI_BASE_URL` → `TTS_ENDPOINT`。
- 当 `endpoint` 指向非 OpenAI 端点时，OpenClaw 将其视为兼容 OpenAI 的 TTS 服务器，并放宽模型/语音校验。

---

## Talk

Talk 模式（macOS/iOS/Android）的默认配置。

```yaml
talk:
  voice: "alloy"
  model: "tts-1"
  api_key: ""
  endpoint: ""
  voice_fallback: "nova"
  model_fallback: "tts-1-hd"
  directives:
    use_friendly_names: true
```

- 语音 ID 回退至 `voice_fallback` 或 `model_fallback`。
- `api_key` 和 `endpoint` 支持明文字符串或 SecretRef 对象。
- `voice_fallback` 仅在未配置 Talk API 密钥时生效。
- `directives.use_friendly_names` 允许 Talk 指令使用友好名称。

---

## 工具

### 工具配置文件

`tools.profile` 在 `tools.allow`/`tools.deny` 之前设置基础白名单：

本地接入（onboarding）在未显式设置时，默认将新的本地配置设为 `tools.profile: "coding"`（已存在的显式配置文件保持不变）。

| 配置文件     | 包含内容                                                                                  |
| ----------- | ----------------------------------------------------------------------------------------- |
| `minimal`   | 仅包含 `session_status`                                                                     |
| `coding`    | 包含 `group:fs`、`group:runtime`、`group:sessions`、`group:memory`、`image`                    |
| `messaging` | 包含 `group:messaging`、`sessions_list`、`sessions_history`、`sessions_send`、`session_status` |
| `full`      | 无限制（等同于未设置）                                                            |

### 工具分组

| 分组              | 工具                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec`、`process`（其中 `bash` 被接受为 `exec` 的别名）                            |
| `group:fs`         | `read`、`write`、`edit`、`apply_patch`                                                   |
| `group:sessions`   | `sessions_list`、`sessions_history`、`sessions_send`、`sessions_spawn`、`session_status` |
| `group:memory`     | `memory_search`、`memory_get`                                                            |
| `group:web`        | `web_search`、`web_fetch`                                                                |
| `group:ui`         | `browser`、`canvas`                                                                      |
| `group:automation` | `cron`、`gateway`                                                                        |
| `group:messaging`  | `message`                                                                                |
| `group:nodes`      | `nodes`                                                                                  |
| `group:openclaw`   | 所有内置工具（不包括提供方插件）                                           |

### `tools.allow` / `tools.deny`

全局工具允许/拒绝策略（拒绝优先）。不区分大小写，支持 `*` 通配符。即使 Docker 沙箱关闭时也生效。

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

进一步针对特定提供方或模型限制可用工具。应用顺序：基础配置文件 → 提供方配置文件 → 允许/拒绝策略。

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

控制提升权限的（宿主机）执行访问：

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

- 每代理覆盖项（`agents.list[].tools.elevated`）只能进一步收紧限制。
- `/elevated on|off|ask|full` 按会话存储状态；内联指令仅对单条消息生效。
- 提升权限的 `exec` 在宿主机上运行，绕过沙箱机制。

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

工具循环安全检查**默认禁用**。设置 `enabled: true` 可启用检测功能。  
相关设置可在全局配置 `tools.loopDetection` 中定义，并可在每个代理级别通过 `agents.list[].tools.loopDetection` 进行覆盖。

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

- `historySize`：为循环分析保留的最大工具调用历史记录数。
- `warningThreshold`：触发警告的“无进展重复模式”阈值。
- `criticalThreshold`：用于阻断关键循环的更高重复阈值。
- `globalCircuitBreakerThreshold`：对任意无进展运行实施硬性终止的阈值。
- `detectors.genericRepeat`：对重复调用相同工具及相同参数的情况发出警告。
- `detectors.knownPollNoProgress`：对已知轮询类工具（如 `process.poll`、`command_status` 等）发出警告或阻止。
- `detectors.pingPong`：对交替出现的无进展成对模式发出警告或阻止。
- 若 `warningThreshold >= criticalThreshold` 或 `criticalThreshold >= globalCircuitBreakerThreshold`，验证失败。

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

配置入站媒体理解能力（图像/音频/视频）：

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

<Accordion title="媒体模型入口字段">

**提供方入口**（`type: "provider"` 或省略）：

- `provider`：API 提供方 ID（如 `openai`、`anthropic`、`google`/`gemini`、`groq` 等）
- `model`：模型 ID 覆盖项
- `profile` / `preferredProfile`：选择 `auth-profiles.json` 配置文件

**CLI 入口**（`type: "cli"`）：

- `command`：要运行的可执行程序
- `args`：模板化参数（支持 `{{MediaPath}}`、`{{Prompt}}`、`{{MaxChars}}` 等）

**通用字段：**

- `capabilities`：可选列表（`image`、`audio`、`video`）。默认值：`openai`/`anthropic`/`minimax` → 图像，`google` → 图像+音频+视频，`groq` → 音频。
- `prompt`、`maxChars`、`maxBytes`、`timeoutSeconds`、`language`：各入口项的覆盖设置。
- 出错时自动回退至下一个入口项。

提供方认证遵循标准顺序：`auth-profiles.json` → 环境变量 → `models.providers.*.apiKey`。

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

控制哪些会话可被会话工具（`sessions_list`、`sessions_history`、`sessions_send`）所指向。

默认值：`tree`（当前会话 + 当前会话派生的会话，例如子代理）。

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

说明：

- `self`：仅限当前会话密钥。
- `tree`：当前会话 + 当前会话所派生的会话（子代理）。
- `agent`：属于当前代理 ID 的任意会话（若以同一代理 ID 运行按发送者划分的会话，则可能包含其他用户）。
- `all`：任意会话。跨代理指向仍需满足 `tools.agentToAgent`。
- 沙箱限制：当当前会话处于沙箱中且启用 `agents.defaults.sandbox.sessionToolsVisibility="spawned"` 时，可见性强制设为 `tree`，即使 `tools.sessions.visibility="all"` 已配置。

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

说明：

- 附件仅支持 `runtime: "subagent"`。ACP 运行时会拒绝附件。
- 文件将在子工作区的 `.openclaw/attachments/<uuid>/` 处实例化，并附带一个 `.manifest.json`。
- 附件内容会自动从对话记录持久化中脱敏（redacted）。
- Base64 输入经严格字母表/填充校验，并设有预解码尺寸保护。
- 目录的文件权限为 `0700`，文件的权限为 `0600`。
- 清理遵循 `cleanup` 策略：`delete` 始终移除附件；`keep` 仅在 `retainOnSessionKeep: true` 时保留附件。

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

- `model`：为派生子代理指定的默认模型。若省略，子代理将继承调用者的模型。
- `runTimeoutSeconds`：当工具调用未指定 `runTimeoutSeconds` 时，`sessions_spawn` 的默认超时时间（单位：秒）。`0` 表示无超时限制。
- 子代理级工具策略：`tools.subagents.tools.allow` / `tools.subagents.tools.deny`。

---

## 自定义提供方与基础 URL

OpenClaw 使用 pi-coding-agent 模型目录。可通过配置中的 `models.providers` 或 `~/.openclaw/agents/<agentId>/agent/models.json` 添加自定义提供方。

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

- 对于自定义身份验证需求，请使用 `authHeader: true` + `headers`。
- 使用 `OPENCLAW_AGENT_DIR`（或 `PI_CODING_AGENT_DIR`）覆盖代理配置根目录。
- 匹配提供程序 ID 的合并优先级规则如下：
  - 非空的代理 `models.json` `baseUrl` 值具有最高优先级。
  - 非空的代理 `apiKey` 值仅在当前配置/认证配置文件上下文中该提供程序**未**由 SecretRef 管理时才生效。
  - 由 SecretRef 管理的提供程序 `apiKey` 值将从源标记（`ENV_VAR_NAME` 表示环境变量引用，`secretref-managed` 表示文件/执行引用）动态刷新，而非持久化已解析的密钥。
  - 若代理的 `apiKey`/`baseUrl` 为空或缺失，则回退至配置中的 `models.providers`。
  - 对于匹配的模型 `contextWindow`/`maxTokens`，采用显式配置值与隐式目录值中的较大者。
  - 当您希望配置完全重写 `models.json` 时，请使用 `models.mode: "replace"`。

### 提供程序字段详情

- `models.mode`：提供程序目录行为（`merge` 或 `replace`）。
- `models.providers`：以提供程序 ID 为键的自定义提供程序映射。
- `models.providers.*.api`：请求适配器（`openai-completions`、`openai-responses`、`anthropic-messages`、`google-generative-ai` 等）。
- `models.providers.*.apiKey`：提供程序凭据（推荐使用 SecretRef 或环境变量替换）。
- `models.providers.*.auth`：认证策略（`api-key`、`token`、`oauth`、`aws-sdk`）。
- `models.providers.*.injectNumCtxForOpenAICompat`：对于 Ollama + `openai-completions`，向请求中注入 `options.num_ctx`（默认值：`true`）。
- `models.providers.*.authHeader`：在必要时强制通过 `Authorization` 请求头传输凭据。
- `models.providers.*.baseUrl`：上游 API 基础 URL。
- `models.providers.*.headers`：用于代理/租户路由的额外静态请求头。
- `models.providers.*.models`：显式的提供程序模型目录条目。
- `models.providers.*.models.*.compat.supportsDeveloperRole`：可选的兼容性提示。对于 `api: "openai-completions"`，若其非空且非原生 `baseUrl`（主机名不为 `api.openai.com`），OpenClaw 将在运行时强制设为 `false`。若 `baseUrl` 为空或省略，则保持默认 OpenAI 行为。
- `models.bedrockDiscovery`：Bedrock 自动发现设置根节点。
- `models.bedrockDiscovery.enabled`：启用或禁用发现轮询。
- `models.bedrockDiscovery.region`：用于发现的 AWS 区域。
- `models.bedrockDiscovery.providerFilter`：可选的提供程序 ID 过滤器，用于定向发现。
- `models.bedrockDiscovery.refreshInterval`：发现刷新的轮询间隔。
- `models.bedrockDiscovery.defaultContextWindow`：为已发现模型指定的回退上下文窗口大小。
- `models.bedrockDiscovery.defaultMaxTokens`：为已发现模型指定的回退最大输出 token 数。

### 提供程序示例

<Accordion title="Cerebras（GLM 4.6 / 4.7）">

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

对 Cerebras 使用 `cerebras/zai-glm-4.7`；对 Z.AI 直连使用 `zai/glm-4.7`。

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

<Accordion title="Z.AI（GLM-4.7）">

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

- 通用端点：`https://api.z.ai/api/paas/v4`
- 编码端点（默认）：`https://api.z.ai/api/coding/paas/v4`
- 对于通用端点，请使用基础 URL 覆盖定义一个自定义提供程序。

</Accordion>

<Accordion title="Moonshot AI（Kimi）">

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

针对中国地区端点：使用 `baseUrl: "https://api.moonshot.cn/v1"` 或 `openclaw onboard --auth-choice moonshot-api-key-cn`。

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

Anthropic 兼容型内置提供程序。快捷方式：`openclaw onboard --auth-choice kimi-code-api-key`。

</Accordion>

<Accordion title="Synthetic（Anthropic 兼容）">

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

基础 URL 应省略 `/v1`（Anthropic 客户端会自动追加）。快捷方式：`openclaw onboard --auth-choice synthetic-api-key`。

</Accordion>

<Accordion title="MiniMax M2.5（直连）">

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

<Accordion title="本地模型（LM Studio）">

参见 [本地模型](/gateway/local-models)。简而言之：在高性能硬件上通过 LM Studio Responses API 运行 MiniMax M2.5；同时保留托管模型以供回退使用。

</Accordion>

---

## 技能（Skills）

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

- `allowBundled`：仅针对捆绑技能的可选白名单（托管/工作区技能不受影响）。
- `entries.<skillKey>.enabled: false`：即使技能已被捆绑或安装，也将其禁用。
- `entries.<skillKey>.apiKey`：为声明了主环境变量的技能提供便利（支持明文字符串或 SecretRef 对象）。

---

## 插件（Plugins）

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
- `plugins.entries.<id>.config`：由插件定义的配置对象（依据插件 schema 进行校验）。
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
- 控制服务：仅限回环（端口由 `gateway.port` 推导，默认为 `18791`）。
- `extraArgs` 为本地 Chromium 启动追加额外的启动标志（例如 `--disable-gpu`、窗口尺寸调整或调试标志）。

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

- `seamColor`：原生应用 UI 外观的强调色（如“对话模式”气泡色调等）。
- `assistant`：控制 UI 身份覆盖项。若未设置，则回退至当前代理身份。

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
- **遗留绑定别名**：请在 `gateway.bind`（`auto`、`loopback`、`lan`、`tailnet`、`custom`）中使用绑定模式值，而非主机别名（`0.0.0.0`、`127.0.0.1`、`localhost`、`::`、`::1`）。
- **Docker 注意事项**：默认的 `loopback` 绑定在容器内监听 `127.0.0.1`。在 Docker 桥接网络（`-p 18789:18789`）下，流量到达的是 `eth0`，因此网关不可达。请改用 `--network host`，或设置 `bind: "lan"`（或配合 `customBindHost: "0.0.0.0"` 使用 `bind: "custom"`），以监听所有接口。
- **认证（Auth）**：默认必需。非回环绑定需提供共享令牌/密码。初始配置向导默认会生成一个令牌。
- 若同时配置了 `gateway.auth.token` 和 `gateway.auth.password`（包括 SecretRefs），则必须显式设置 `gateway.auth.mode` 为 `token` 或 `password`。当两者均被配置且未设置模式时，启动及服务安装/修复流程将失败。
- `gateway.auth.mode: "none"`：显式的无认证模式。仅适用于受信任的本地回环环境；此模式不会出现在初始配置向导中。
- `gateway.auth.mode: "trusted-proxy"`：将认证委托给具备身份感知能力的反向代理，并信任来自 `gateway.trustedProxies` 的身份头（参见 [可信代理认证](/gateway/trusted-proxy-auth)）。
- `gateway.auth.allowTailscale`：当启用 `true` 时，Tailscale Serve 的身份头可满足控制 UI/WebSocket 认证（通过 `tailscale whois` 验证）；但 HTTP API 端点仍需令牌/密码认证。该免令牌流程假设网关主机是受信任的。当启用 `tailscale.mode = "serve"` 时，默认为 `true`。
- `gateway.auth.rateLimit`：可选的认证失败限流器。按客户端 IP 及认证范围（共享密钥与设备令牌分别独立追踪）进行限制。被阻止的尝试返回 `429` + `Retry-After`。
  - `gateway.auth.rateLimit.exemptLoopback` 默认为 `true`；若您有意对本地回环流量也启用速率限制（例如测试环境或严格代理部署），请设置 `false`。
- 来自浏览器的 WebSocket 认证尝试始终受限，且回环豁免被禁用（纵深防御，防止基于浏览器的本地回环暴力破解）。
- `tailscale.mode`：`serve`（仅限 tailnet，回环绑定）或 `funnel`（公网访问，需认证）。
- `controlUi.allowedOrigins`：针对网关 WebSocket 连接的浏览器来源显式白名单。当预期有来自非回环来源的浏览器客户端时，此项为必需。
- `controlUi.dangerouslyAllowHostHeaderOriginFallback`：危险模式，启用 Host 头来源回退，适用于明确依赖 Host 头来源策略的部署。
- `remote.transport`：`ssh`（默认）或 `direct`（ws/wss）。对于 `direct`，`remote.url` 必须为 `ws://` 或 `wss://`。
- `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`：客户端侧应急覆盖机制，允许对受信任私有网络 IP 使用明文 `ws://`；明文默认仍仅限回环。
- `gateway.remote.token` / `.password` 是远程客户端凭据字段。它们本身并不配置网关认证。
- 本地网关调用路径可在 `gateway.auth.*` 未设置时，使用 `gateway.remote.*` 作为后备。
- `trustedProxies`：终止 TLS 的反向代理 IP。仅列出您可控的代理。
- `allowRealIpFallback`：当启用 `true` 时，若缺少 `X-Forwarded-For`，网关将接受 `X-Real-IP`。默认为 `false`，以实现故障关闭行为。
- `gateway.tools.deny`：针对 HTTP `POST /tools/invoke` 额外屏蔽的工具名称（扩展默认拒绝列表）。
- `gateway.tools.allow`：从默认 HTTP 拒绝列表中移除工具名称。

</Accordion>

### 兼容 OpenAI 的端点

- 聊天补全（Chat Completions）：默认禁用。通过 `gateway.http.endpoints.chatCompletions.enabled: true` 启用。
- 响应 API：`gateway.http.endpoints.responses.enabled`。
- 响应 URL 输入加固：
  - `gateway.http.endpoints.responses.maxUrlParts`
  - `gateway.http.endpoints.responses.files.urlAllowlist`
  - `gateway.http.endpoints.responses.images.urlAllowlist`
- 可选响应加固头：
  - `gateway.http.securityHeaders.strictTransportSecurity`（仅对您可控的 HTTPS 来源设置；参见 [可信代理认证](/gateway/trusted-proxy-auth#tls-termination-and-hsts)）

### 多实例隔离

在同一主机上运行多个网关，需使用唯一端口和状态目录：

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json \
OPENCLAW_STATE_DIR=~/.openclaw-a \
openclaw gateway --port 19001
```

便捷标志：`--dev`（使用 `~/.openclaw-dev` + 端口 `19001`）、`--profile <name>`（使用 `~/.openclaw-<name>`）。

参见 [多个网关](/gateway/multiple-gateways)。

---

## 钩子（Hooks）

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
    maxBodyBytes: 262144,
    defaultSessionKey: "hook:ingress",
    allowRequestSessionKey: false,
    allowedSessionKeyPrefixes: ["hook:"],
    allowedAgentIds: ["hooks", "main"],
    presets: ["gmail"],
    transformsDir: "~/.openclaw/hooks/transforms",
    mappings: [
      {
        match: { path: "gmail" },
        action: "agent",
        agentId: "hooks",
        wakeMode: "now",
        name: "Gmail",
        sessionKey: "hook:gmail:{{messages[0].id}}",
        messageTemplate: "From: {{messages[0].from}}\nSubject: {{messages[0].subject}}\n{{messages[0].snippet}}",
        deliver: true,
        channel: "last",
        model: "openai/gpt-5.2-mini",
      },
    ],
  },
}
```

认证方式：`Authorization: Bearer <token>` 或 `x-openclaw-token: <token>`。

**端点（Endpoints）：**

- `POST /hooks/wake` → `{ text, mode?: "now"|"next-heartbeat" }`
- `POST /hooks/agent` → `{ message, name?, agentId?, sessionKey?, wakeMode?, deliver?, channel?, to?, model?, thinking?, timeoutSeconds? }`
  - 请求负载（request payload）中的 `sessionKey` 仅在 `hooks.allowRequestSessionKey=true` 为真时被接受（默认值：`false`）。
- `POST /hooks/<name>` → 通过 `hooks.mappings` 解析

<Accordion title="映射详情">

- `match.path` 匹配 `/hooks` 后的子路径（例如：`/hooks/gmail` → `gmail`）。
- `match.source` 匹配通用路径的负载字段。
- 类似 `{{messages[0].subject}}` 的模板从请求负载中读取内容。
- `transform` 可指向一个返回钩子动作（hook action）的 JS/TS 模块。
  - `transform.module` 必须为相对路径，且必须位于 `hooks.transformsDir` 范围内（绝对路径和路径遍历将被拒绝）。
- `agentId` 将请求路由至特定智能体（agent）；未知 ID 将回退至默认智能体。
- `allowedAgentIds`：限制显式路由（`*` 或省略 = 允许全部，`[]` = 拒绝全部）。
- `defaultSessionKey`：可选的固定会话密钥，用于在未显式指定 `sessionKey` 时运行钩子智能体。
- `allowRequestSessionKey`：允许 `/hooks/agent` 调用方设置 `sessionKey`（默认值：`false`）。
- `allowedSessionKeyPrefixes`：可选的显式 `sessionKey` 值（请求 + 映射）前缀白名单，例如 `["hook:"]`。
- `deliver: true` 将最终响应发送至某通道；`channel` 默认为 `last`。
- `model` 覆盖本次钩子运行所使用的 LLM（若已配置模型目录，则该模型必须被允许）。

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

- 网关（Gateway）在启动时自动启用 `gog gmail watch serve`（如已配置）。设置 `OPENCLAW_SKIP_GMAIL_WATCHER=1` 可禁用此功能。
- 请勿在网关之外单独运行 `gog gmail watch serve`。

---

## Canvas 主机（Canvas host）

```json5
{
  canvasHost: {
    root: "~/.openclaw/workspace/canvas",
    liveReload: true,
    // enabled: false, // or OPENCLAW_SKIP_CANVAS_HOST=1
  },
}
```

- 在网关端口下通过 HTTP 提供可由智能体编辑的 HTML/CSS/JS 及 A2UI：
  - `http://<gateway-host>:<gateway.port>/__openclaw__/canvas/`
  - `http://<gateway-host>:<gateway.port>/__openclaw__/a2ui/`
- 仅限本地访问：保持 `gateway.bind: "loopback"`（默认）。
- 绑定非环回地址（non-loopback binds）：Canvas 路由需经网关认证（token/密码/可信代理），与其他网关 HTTP 接口一致。
- Node WebViews 通常不发送认证头；节点完成配对并连接后，网关将广播面向该节点的、可用于访问 Canvas/A2UI 的能力 URL（capability URLs）。
- 能力 URL 与当前节点 WebSocket 会话绑定，并快速过期；不使用基于 IP 的回退机制。
- 向所服务的 HTML 中注入实时重载（live-reload）客户端。
- 目录为空时自动创建初始 `index.html`。
- 同时在 `/__openclaw__/a2ui/` 提供 A2UI。
- 配置变更需重启网关。
- 对于大型目录或出现 `EMFILE` 错误时，可禁用实时重载。

---

## 发现机制（Discovery）

### mDNS（Bonjour）

```json5
{
  discovery: {
    mdns: {
      mode: "minimal", // minimal | full | off
    },
  },
}
```

- `minimal`（默认）：从 TXT 记录中省略 `cliPath` 和 `sshPort`。
- `full`：包含 `cliPath` 和 `sshPort`。
- 主机名默认为 `openclaw`；可通过 `OPENCLAW_MDNS_HOSTNAME` 覆盖。

### 广域网（Wide-area，DNS-SD）

```json5
{
  discovery: {
    wideArea: { enabled: true },
  },
}
```

在 `~/.openclaw/dns/` 下写入单播 DNS-SD 区域。如需跨网络发现，请配合 DNS 服务器（推荐 CoreDNS）及 Tailscale 分割 DNS（split DNS）使用。

配置方法：`openclaw dns setup --apply`。

---

## 环境变量（Environment）

### `env`（内联环境变量）

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

- 内联环境变量仅在进程环境缺失对应键时生效。
- `.env` 文件：当前工作目录（CWD）下的 `.env` 与 `~/.openclaw/.env`（二者均不会覆盖已有变量）。
- `shellEnv`：从您的登录 Shell 配置文件中导入缺失的预期键。
- 完整优先级顺序参见 [环境变量](/help/environment)。

### 环境变量替换（Env var substitution）

可在任意配置字符串中通过 `${VAR_NAME}` 引用环境变量：

```json5
{
  gateway: {
    auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" },
  },
}
```

- 仅匹配大写名称：`[A-Z_][A-Z0-9_]*`。
- 缺失或为空的变量将在配置加载时引发错误。
- 使用 `$${VAR}` 转义以获得字面量 `${VAR}`。
- 支持与 `$include` 一同使用。

---

## 密钥（Secrets）

密钥引用（Secret refs）为累加式：明文值仍有效。

### `SecretRef`

采用一种对象结构：

```json5
{ source: "env" | "file" | "exec", provider: "default", id: "..." }
```

校验规则：

- `provider` 模式：`^[a-z][a-z0-9_-]{0,63}$`
- `source: "env"` ID 模式：`^[A-Z][A-Z0-9_]{0,127}$`
- `source: "file"` ID：绝对 JSON 指针（例如 `"/providers/openai/apiKey"`）
- `source: "exec"` ID 模式：`^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$`

### 支持的凭据表面（Supported credential surface）

- 标准矩阵：[SecretRef 凭据表面](/reference/secretref-credential-surface)
- `secrets apply` 目标支持 `openclaw.json` 凭据路径。
- `auth-profiles.json` 引用将纳入运行时解析及审计覆盖范围。

### 密钥提供程序配置（Secret providers config）

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

注意事项：

- `file` 提供程序支持 `mode: "json"` 和 `mode: "singleValue"`（单值模式下 `id` 必须为 `"value"`）。
- `exec` 提供程序要求绝对 `command` 路径，并通过 stdin/stdout 使用协议负载。
- 默认情况下拒绝符号链接命令路径。设置 `allowSymlinkCommand: true` 可允许符号链接路径，同时验证其解析后的目标路径。
- 若配置了 `trustedDirs`，则可信目录检查将应用于解析后的目标路径。
- `exec` 子进程环境默认极简；需显式通过 `passEnv` 传入所需变量。
- 密钥引用在激活时解析为内存快照，后续请求路径仅读取该快照。
- 激活期间应用活跃表面（active-surface）过滤：启用表面上未解析的引用将导致启动/重载失败；非活跃表面则跳过处理并输出诊断信息。

---

## 认证存储（Auth storage）

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

- 每个智能体的配置文件存储于 `<agentDir>/auth-profiles.json`。
- `auth-profiles.json` 支持值级别引用（value-level refs）（`keyRef` 用于 `api_key`，`tokenRef` 用于 `token`）。
- 静态运行时凭据来自内存中已解析的快照；发现后将清除遗留的静态 `auth.json` 条目。
- 遗留 OAuth 凭据从 `~/.openclaw/credentials/oauth.json` 导入。
- 参见 [OAuth](/concepts/oauth)。
- 密钥运行时行为及 `audit/configure/apply` 工具链：[密钥管理](/gateway/secrets)。

---

## 日志（Logging）

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
- 设置 `logging.file` 可指定稳定路径。
- `consoleLevel` 在 `--verbose` 时提升至 `debug`。

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

- `cli.banner.taglineMode` 控制横幅标语（banner tagline）样式：
  - `"random"`（默认）：轮换显示幽默/应季标语。
  - `"default"`：固定中性标语（`All your chats, one OpenClaw.`）。
  - `"off"`：不显示标语文本（横幅标题/版本仍显示）。
- 若要隐藏整个横幅（而不仅是标语），请设置环境变量 `OPENCLAW_HIDE_BANNER=1`。

---

## 向导（Wizard）

CLI 向导（`onboard`、`configure`、`doctor`）所写入的元数据：

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

## 身份（Identity）

由 macOS 入门助手编写。推导默认值：

- `messages.ackReaction` 来自 `identity.emoji`（若不可用则回退为 👀）
- `mentionPatterns` 来自 `identity.name`/`identity.emoji`
- `avatar` 接受：工作区相对路径、`http(s)` URL 或 `data:` URI

---

## Bridge（旧版，已移除）

当前版本不再包含 TCP bridge。节点通过 Gateway WebSocket 连接。`bridge.*` 密钥已不再属于配置模式的一部分（验证将在其被移除前持续失败；可使用 `openclaw doctor --fix` 剥离未知密钥）。

<Accordion title="旧版 bridge 配置（历史参考）">

```json
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
```

</Accordion>

---

## Cron

```json5
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
```

- `sessionRetention`：已完成的独立 cron 运行会话在从 `sessions.json` 中清理前保留的时间长度。同时也控制已归档的已删除 cron 转录文本的清理。默认值：`24h`；设置 `false` 可禁用该功能。
- `runLog.maxBytes`：单个运行日志文件（`cron/runs/<jobId>.jsonl`）在触发清理前的最大大小。默认值：`2_000_000` 字节。
- `runLog.keepLines`：当触发运行日志清理时所保留的最新行数。默认值：`2000`。
- `webhookToken`：用于 cron webhook POST 请求交付（`delivery.mode = "webhook"`）的 Bearer Token；若省略，则不发送认证头。
- `webhook`：已弃用的旧版备用 webhook URL（http/https），仅用于仍含有 `notify: true` 的已保存任务。

参见 [Cron 任务](/automation/cron-jobs)。

---

## 媒体模型模板变量

在 `tools.media.models[].args` 中展开的模板占位符：

| 变量           | 描述                                       |
| ------------------ | ------------------------------------------------- |
| `{{Body}}`         | 完整的入站消息正文                         |
| `{{RawBody}}`      | 原始正文（不含历史记录/发送者包装）             |
| `{{BodyStripped}}` | 已移除群组提及的正文                 |
| `{{From}}`         | 发送者标识符                                 |
| `{{To}}`           | 目标标识符                            |
| `{{MessageSid}}`   | 频道消息 ID                                |
| `{{SessionId}}`    | 当前会话 UUID                              |
| `{{IsNewSession}}` | `"true"`（创建新会话时）                 |
| `{{MediaUrl}}`     | 入站媒体伪 URL                          |
| `{{MediaPath}}`    | 本地媒体路径                                  |
| `{{MediaType}}`    | 媒体类型（image/audio/document/…）               |
| `{{Transcript}}`   | 音频转录文本                                  |
| `{{Prompt}}`       | CLI 条目中解析出的媒体提示             |
| `{{MaxChars}}`     | CLI 条目中解析出的最大输出字符数         |
| `{{ChatType}}`     | `"direct"` 或 `"group"`                           |
| `{{GroupSubject}}` | 群组主题（尽力而为）                       |
| `{{GroupMembers}}` | 群组成员预览（尽力而为）               |
| `{{SenderName}}`   | 发送者显示名称（尽力而为）                 |
| `{{SenderE164}}`   | 发送者电话号码（尽力而为）                 |
| `{{Provider}}`     | 提供商提示（whatsapp、telegram、discord 等） |

---

## 配置包含项（`$include`）

将配置拆分为多个文件：

```json5
// ~/.openclaw/openclaw.json
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
  broadcast: {
    $include: ["./clients/mueller.json5", "./clients/schmidt.json5"],
  },
}
```

**合并行为：**

- 单个文件：替换其所处对象。
- 文件数组：按顺序深度合并（后项覆盖前项）。
- 同级键：在包含项之后合并（覆盖已包含的值）。
- 嵌套包含：最多支持 10 层深度。
- 路径：相对于包含该配置的文件进行解析，但必须保留在顶层配置目录内（即 `dirname` 的 `openclaw.json`）。仅当绝对路径/`../` 形式仍能解析到该边界内时才允许使用。
- 错误：对缺失文件、解析错误及循环包含提供清晰的错误信息。

---

相关文档：[配置](/gateway/configuration) · [配置示例](/gateway/configuration-examples) · [Doctor](/gateway/doctor)