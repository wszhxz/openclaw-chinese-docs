---
title: "Configuration Reference"
description: "Complete field-by-field reference for ~/.openclaw/openclaw.json"
---
# 配置参考

`~/.openclaw/openclaw.json`中可用的每个字段。有关任务导向的概述，请参阅[配置](/gateway/configuration)。

配置格式为**JSON5**（允许注释和尾随逗号）。所有字段都是可选的 — 当省略时，OpenClaw使用安全默认值。

---

## 通道

当其配置部分存在时，每个通道会自动启动（除非`enabled: false`）。

### 单聊和群组访问

所有通道都支持单聊策略和群组策略：

| 单聊策略           | 行为                                                        |
| ------------------- | --------------------------------------------------------------- |
| `pairing` (默认) | 未知发送者会收到一次性配对码；所有者必须批准 |
| `allowlist`         | 仅允许在`allowFrom`中的发送者（或已配对的存储）             |
| `open`              | 允许所有传入的单聊消息（需要`allowFrom: ["*"]`)             |
| `disabled`          | 忽略所有传入的单聊消息                                          |

| 群组策略          | 行为                                               |
| --------------------- | ------------------------------------------------------ |
| `allowlist` (默认) | 仅允许与配置的白名单匹配的群组          |
| `open`                | 绕过群组白名单（提及门控仍然适用） |
| `disabled`            | 阻止所有群组/房间消息                          |

<Note>
__CODE_BLOCK_11__ sets the default when a provider's __CODE_BLOCK_12__ is unset.
Pairing codes expire after 1 hour. Pending DM pairing requests are capped at **3 per channel**.
Slack/Discord have a special fallback: if their provider section is missing entirely, runtime group policy can resolve to __CODE_BLOCK_13__ (with a startup warning).
</Note>

### 通道模型覆盖

使用`channels.modelByChannel`将特定的通道ID固定到一个模型。值可以接受`provider/model`或配置的模型别名。通道映射适用于会话尚未具有模型覆盖的情况（例如，通过`/model`设置）。

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

### WhatsApp

WhatsApp通过网关的Web通道（Baileys Web）运行。当存在链接的会话时会自动启动。

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

<Accordion title="多账号WhatsApp">

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

- 如果存在，外发命令默认使用账号 `default`；否则使用第一个已配置的账号ID（按排序）。
- 旧的单账号Baileys认证目录由 `openclaw doctor` 迁移到 `whatsapp/default`。
- 每账号覆盖：`channels.whatsapp.accounts.<id>.sendReadReceipts`，`channels.whatsapp.accounts.<id>.dmPolicy`，`channels.whatsapp.accounts.<id>.allowFrom`。

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
      mediaMaxMb: 5,
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: { autoSelectFamily: false },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

- Bot token: `channels.telegram.botToken` 或 `channels.telegram.tokenFile`，默认账户的备用选项为 `TELEGRAM_BOT_TOKEN`。
- `configWrites: false` 块阻止由Telegram发起的配置写入（超级群组ID迁移，`/config set|unset`）。
- Telegram流预览使用 `sendMessage` + `editMessageText`（适用于直接聊天和群组聊天）。
- 重试策略：参见[重试策略](/concepts/retry)。

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
      allowFrom: ["1234567890", "steipete"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["openclaw-dm"] },
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
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
        ttlHours: 24,
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

- Token: `channels.discord.token`，默认账户使用 `DISCORD_BOT_TOKEN` 作为备用。
- 使用 `user:<id>` (DM) 或 `channel:<id>` (服务器频道) 作为交付目标；纯数字ID会被拒绝。
- 服务器缩略名是小写，空格替换为 `-`；频道键使用缩略名（无 `#`）。优先使用服务器ID。
- 默认忽略机器人发送的消息。`allowBots: true` 启用它们（自己的消息仍然会被过滤）。
- `maxLinesPerMessage`（默认17）即使在2000字符以下也会分割长消息。
- `channels.discord.threadBindings` 控制Discord线程绑定路由：
  - `enabled`：Discord覆盖线程绑定会话功能 (`/focus`，`/unfocus`，`/agents`，`/session ttl` 和绑定交付/路由)
  - `ttlHours`：Discord覆盖自动失焦TTL (`0` 禁用)
  - `spawnSubagentSessions`：选择加入 `sessions_spawn({ thread: true })` 自动线程创建/绑定
- `channels.discord.ui.components.accentColor` 设置Discord组件v2容器的强调颜色。
- `channels.discord.voice` 启用Discord语音频道对话，并可选自动加入+TTS覆盖。
- `channels.discord.streaming` 是规范的流模式键。旧版 `streamMode` 和布尔值 `streaming` 会自动迁移。

**反应通知模式：** `off`（无），`own`（机器人的消息，默认），`all`（所有消息），`allowlist`（来自 `guilds.<id>.users` 的所有消息）。

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

- 服务账号JSON：内联 (`serviceAccount`) 或文件基于 (`serviceAccountFile`)。
- 环境回退：`GOOGLE_CHAT_SERVICE_ACCOUNT` 或 `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`。
- 使用 `spaces/<spaceId>` 或 `users/<userId|email>` 作为交付目标。

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
      textChunkLimit: 4000,
      chunkMode: "length",
      streaming: "partial", // off | partial | block | progress (preview mode)
      nativeStreaming: true, // use Slack native streaming API when streaming=partial
      mediaMaxMb: 20,
    },
  },
}
```

- **Socket 模式** 需要 `botToken` 和 `appToken` (`SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` 用于默认账户环境回退)。
- **HTTP 模式** 需要 `botToken` 加上 `signingSecret` (在根目录或每个账户下)。
- `configWrites: false` 阻止 Slack 初始化的配置写入。
- `channels.slack.streaming` 是规范的流模式键。旧版 `streamMode` 和布尔值 `streaming` 会自动迁移。
- 使用 `user:<id>` (DM) 或 `channel:<id>` 作为交付目标。

**反应通知模式:** `off`, `own` (默认), `all`, `allowlist` (来自 `reactionAllowlist`)。

**线程会话隔离:** `thread.historyScope` 是每个线程 (默认) 或跨频道共享。`thread.inheritParent` 将父频道记录复制到新线程。

| 动作组     | 默认    | 备注                   |
| ---------- | ------- | ---------------------- |
| reactions  | enabled | 反应 + 列出反应        |
| messages   | enabled | 读/发/编辑/删除        |
| pins       | enabled | 固定/取消固定/列出     |
| memberInfo | enabled | 成员信息               |
| emojiList  | enabled | 自定义表情符号列表     |

### Mattermost

Mattermost 作为一个插件提供: `openclaw plugins install @openclaw/mattermost`。

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
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

聊天模式: `oncall` (通过@提及回复，默认)，`onmessage` (每条消息)，`onchar` (以触发前缀开头的消息)。

### 信号

```json5
{
  channels: {
    signal: {
      reactionNotifications: "own", // off | own | all | allowlist
      reactionAllowlist: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      historyLimit: 50,
    },
  },
}
```

**反应通知模式:** `off`, `own` (默认), `all`, `allowlist` (来自 `reactionAllowlist`)。

### iMessage

OpenClaw 启动 `imsg rpc` (通过 stdio 的 JSON-RPC)。无需守护进程或端口。

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

- 需要对“信息”数据库的完全磁盘访问权限。
- 偏好 `chat_id:<id>` 目标。使用 `imsg chats --limit 20` 列出聊天。
- `cliPath` 可以指向一个 SSH 包装器；设置 `remoteHost` (`host` 或 `user@host`) 用于获取 SCP 附件。
- `attachmentRoots` 和 `remoteAttachmentRoots` 限制传入附件路径（默认: `/Users/*/Library/Messages/Attachments`）。
- SCP 使用严格的主机密钥检查，因此确保中继主机密钥已经存在于 `~/.ssh/known_hosts` 中。

<Accordion title="iMessage SSH 包装器示例">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### 多账户（所有频道）

每个频道运行多个账户（每个账户有自己的 `accountId`）：

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

- 当省略 `accountId` 时使用 `default`（CLI + 路由）。
- 环境令牌仅适用于 **默认** 账户。
- 基本频道设置适用于所有账户，除非每个账户单独覆盖。
- 使用 `bindings[].match.accountId` 将每个账户路由到不同的代理。

### 群组聊天提及门控

群组消息默认为 **需要提及**（元数据提及或正则表达式模式）。适用于 WhatsApp、Telegram、Discord、Google Chat 和 iMessage 群组聊天。

**提及类型:**

- **元数据提及**: 平台原生的 @提及。在 WhatsApp 自我聊天模式下被忽略。
- **文本模式**: `agents.list[].groupChat.mentionPatterns` 中的正则表达式模式。始终会被检查。
- 提及门控仅在检测可能时强制执行（原生提及或至少一个模式）。

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

`messages.groupChat.historyLimit` 设置全局默认值。频道可以使用 `channels.<channel>.historyLimit` 覆盖（或按账户）。设置 `0` 以禁用。

#### DM 历史记录限制

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

解析：每个DM覆盖 → 提供程序默认值 → 无限制（全部保留）。

支持：`telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`.

#### 自我聊天模式

在 `allowFrom` 中包含您的号码以启用自我聊天模式（忽略原生@提及，仅响应文本模式）：

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

<Accordion title="命令详细信息">

- 文本命令必须是带有前导 `/` 的**独立**消息。
- `native: "auto"` 为Discord/Telegram启用原生命令，Slack保持关闭。
- 按频道覆盖：`channels.discord.commands.native`（布尔值或 `"auto"`）。`false` 清除先前注册的命令。
- `channels.telegram.customCommands` 添加额外的Telegram机器人菜单条目。
- `bash: true` 为主机shell启用 `! <cmd>`。需要 `tools.elevated.enabled` 和发件人在 `tools.elevated.allowFrom.<channel>` 中。
- `config: true` 启用 `/config`（读取/写入 `openclaw.json`）。
- `channels.<provider>.configWrites` 按频道限制配置更改（默认：true）。
- `allowFrom` 是按提供程序的。当设置时，它是**唯一**的授权源（频道白名单/配对和 `useAccessGroups` 被忽略）。
- `useAccessGroups: false` 允许命令绕过访问组策略，当 `allowFrom` 未设置时。

</Accordion>

---

## 代理默认值

### `agents.defaults.workspace`

默认：`~/.openclaw/workspace`。

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

可选的仓库根目录显示在系统提示符的运行时行中。如果未设置，OpenClaw会自动检测，从工作区向上遍历。

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skipBootstrap`

禁用工作区引导文件的自动创建 (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`)。

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.bootstrapMaxChars`

工作区引导文件在截断前的最大字符数。默认值: `20000`。

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

所有工作区引导文件中注入的最大总字符数。默认值: `150000`。

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.imageMaxDimensionPx`

转录/工具图像块中最长图像边的最大像素大小（在提供者调用之前）。
默认值: `1200`。

较低的值通常会减少视觉令牌的使用和截图密集型运行的请求负载大小。
较高的值会保留更多的视觉细节。

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

系统提示上下文的时间区域（不是消息时间戳）。回退到主机时间区域。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

系统提示中的时间格式。默认值: `auto` (操作系统偏好)。

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
        "minimax/MiniMax-M2.1": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.1"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
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

- `model.primary`: 格式 `provider/model` (例如 `anthropic/claude-opus-4-6`)。如果省略提供者，OpenClaw 假设 `anthropic`（已弃用）。
- `models`: 配置的模型目录和 `/model` 的允许列表。每个条目可以包括 `alias`（快捷方式）和 `params`（特定于提供者：`temperature`, `maxTokens`)。
- `imageModel`: 仅在主模型缺乏图像输入时使用。
- `maxConcurrent`: 跨会话的最大并行代理运行次数（每个会话仍然串行化）。默认值: 1。

**内置别名缩写**（仅当模型处于 `agents.defaults.models` 时适用）：

| 别名          | 模型                           |
| -------------- | ------------------------------- |
| `opus`         | `anthropic/claude-opus-4-6`     |
| `sonnet`       | `anthropic/claude-sonnet-4-5`   |
| `gpt`          | `openai/gpt-5.2`                |
| `gpt-mini`     | `openai/gpt-5-mini`             |
| `gemini`       | `google/gemini-3-pro-preview`   |
| `gemini-flash` | `google/gemini-3-flash-preview` |

您配置的别名始终优先于默认设置。

Z.AI GLM-4.x 模型会自动启用思考模式，除非您设置了 `--thinking off` 或自行定义了 `agents.defaults.models["zai/<model>"].params.thinking`。
Z.AI 模型默认启用 `tool_stream` 以支持工具调用流。设置 `agents.defaults.models["zai/<model>"].params.tool_stream` 为 `false` 以禁用它。

### `agents.defaults.cliBackends`

仅文本回退运行的可选 CLI 后端（无工具调用）。当 API 提供者失败时可用作备份。

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

- CLI 后端以文本为主；工具始终被禁用。
- 当设置了 `sessionArg` 时支持会话。
- 当 `imageArg` 接受文件路径时支持图像透传。

### `agents.defaults.heartbeat`

定期心跳运行。

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m disables
        model: "openai/gpt-5.2-mini",
        includeReasoning: false,
        session: "main",
        to: "+15555550123",
        target: "last", // last | whatsapp | telegram | discord | ... | none
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
      },
    },
  },
}
```

- `every`: 持续时间字符串（ms/s/m/h）。默认: `30m`。
- `suppressToolErrorWarnings`: 当为 true 时，在心跳运行期间抑制工具错误警告负载。
- 每个代理：设置 `agents.list[].heartbeat`。当任何代理定义了 `heartbeat` 时，**只有这些代理** 运行心跳。
- 心跳运行完整的代理回合 — 更短的时间间隔会消耗更多的令牌。

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        reserveTokensFloor: 24000,
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

- `mode`: `default` 或 `safeguard` (长历史记录的分块摘要). 参见[Compaction](/concepts/compaction).
- `memoryFlush`: 在自动压缩前进行静默代理转换以存储持久化记忆。当工作区为只读时跳过。

### `agents.defaults.contextPruning`

在发送到LLM之前从内存上下文中修剪**旧工具结果**。不会修改磁盘上的会话历史。

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
- `ttl` 控制修剪可以再次运行的频率（自上次缓存访问以来）。
- 修剪首先软修剪超大工具结果，如果需要则硬清除较旧的工具结果。

**软修剪**保留开头和结尾，并在中间插入 `...`。

**硬清除**将整个工具结果替换为占位符。

注意：

- 图像块永远不会被修剪或清除。
- 比率是基于字符的（近似值），不是确切的标记计数。
- 如果少于 `keepLastAssistants` 条助手消息存在，则跳过修剪。

</Accordion>

参见[Session Pruning](/concepts/session-pruning)获取行为详情。

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

- 非Telegram渠道需要显式启用 `*.blockStreaming: true` 以启用块回复。
- 渠道覆盖：`channels.<channel>.blockStreamingCoalesce`（以及每个账户的变体）。Signal/Slack/Discord/Google Chat 默认 `minChars: 1500`。
- `humanDelay`: 块回复之间的随机暂停。`natural` = 800–2500ms。每个代理的覆盖：`agents.list[].humanDelay`。

参见[Streaming](/concepts/streaming)获取行为和分块详情。

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

- 默认设置：直接聊天/提及时为 `instant`，未提及的群聊时为 `message`。
- 每个会话的覆盖：`session.typingMode`, `session.typingIntervalSeconds`。

参见[Typing Indicators](/concepts/typing-indicators)。

### `agents.defaults.sandbox`

可选的 **Docker 沙盒** 用于嵌入式代理。请参阅 [Sandboxing](/gateway/sandboxing) 获取完整指南。

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

- `none`: 每个范围的沙盒工作区位于 `~/.openclaw/sandboxes`
- `ro`: 沙盒工作区位于 `/workspace`，代理工作区以只读方式挂载在 `/agent`
- `rw`: 代理工作区以读写方式挂载在 `/workspace`

**范围：**

- `session`: 每会话容器 + 工作区
- `agent`: 每代理一个容器 + 工作区（默认）
- `shared`: 共享容器和工作区（无跨会话隔离）

**`setupCommand`** 在容器创建后运行一次（通过 `sh -lc`）。需要网络出口，可写的根目录，root 用户。

**容器默认为 `network: "none"`** —— 如果代理需要出站访问，请设置为 `"bridge"`。

**入站附件** 被暂存到活动工作区中的 `media/inbound/*`。

**`docker.binds`** 挂载额外的主机目录；全局和每个代理的绑定会合并。

**沙盒浏览器** (`sandbox.browser.enabled`)：容器中的Chromium + CDP。noVNC URL注入到系统提示中。不需要在主配置中使用 `browser.enabled`。
noVNC观察者访问默认使用VNC认证，并且OpenClaw发出一个短期令牌URL（而不是在共享URL中暴露密码）。

- `allowHostControl: false`（默认）阻止沙盒会话针对主机浏览器。
- `network` 默认为 `openclaw-sandbox-browser`（专用桥接网络）。仅在您明确需要全局桥接连接时设置为 `bridge`。
- `cdpSourceRange` 可选地限制容器边缘的CDP入口流量到CIDR范围（例如 `172.21.0.1/32`）。
- `sandbox.browser.binds` 仅将额外的主机目录挂载到沙盒浏览器容器中。当设置时（包括 `[]`），它会替换浏览器容器中的 `docker.binds`。

</Accordion>

构建镜像：

```bash
scripts/sandbox-setup.sh           # main sandbox image
scripts/sandbox-browser-setup.sh   # optional browser image
```

### `agents.list`（每个代理的覆盖）

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
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
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

- `id`：稳定的代理ID（必需）。
- `default`：当设置多个时，第一个生效（记录警告）。如果没有设置，第一个列表条目为默认。
- `model`：字符串形式仅覆盖 `primary`；对象形式 `{ primary, fallbacks }` 覆盖两者 (`[]` 禁用全局回退）。仅覆盖 `primary` 的Cron作业仍然继承默认回退，除非您设置了 `fallbacks: []`。
- `identity.avatar`：工作区相对路径，`http(s)` URL，或 `data:` URI。
- `identity` 推导默认值：`ackReaction` 从 `emoji`，`mentionPatterns` 从 `name`/`emoji`。
- `subagents.allowAgents`：允许的代理ID列表用于 `sessions_spawn` (`["*"]` = 任意；默认：仅相同代理）。

---

## 多代理路由

在一个网关中运行多个隔离的代理。参见[多代理](/concepts/multi-agent)。

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

- `match.channel` (必需)
- `match.accountId` (可选；`*` = 任意账户；省略 = 默认账户)
- `match.peer` (可选；`{ kind: direct|group|channel, id }`)
- `match.guildId` / `match.teamId` (可选；特定于频道)

**确定性匹配顺序：**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId` (精确匹配，无对等体/公会/团队)
5. `match.accountId: "*"` (频道范围)
6. 默认代理

在每个层级中，第一个匹配的 `bindings` 条目获胜。

### 每个代理的访问配置文件

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

<Accordion title="无文件系统访问（仅消息传递）">

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

有关优先级详细信息，请参阅 [多代理沙盒 & 工具](/tools/multi-agent-sandbox-tools)。

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
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
    },
    threadBindings: {
      enabled: true,
      ttlHours: 24, // default auto-unfocus TTL for thread-bound sessions (0 disables)
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

<Accordion title="会话字段详细信息">

- **`dmScope`**: 如何对DM进行分组。
  - `main`: 所有DM共享主会话。
  - `per-peer`: 跨频道按发送者ID隔离。
  - `per-channel-peer`: 按频道+发送者隔离（多用户收件箱推荐）。
  - `per-account-channel-peer`: 按账户+频道+发送者隔离（多账户推荐）。
- **`identityLinks`**: 将规范ID映射到带提供商前缀的对等体以实现跨频道会话共享。
- **`reset`**: 主重置策略。`daily` 在 `atHour` 当地时间重置；`idle` 在 `idleMinutes` 后重置。当两者都配置时，以先到期的为准。
- **`resetByType`**: 按类型覆盖 (`direct`, `group`, `thread`)。旧版 `dm` 作为 `direct` 的别名被接受。
- **`mainKey`**: 旧版字段。运行时现在始终使用 `"main"` 作为主直接聊天桶。
- **`sendPolicy`**: 按 `channel`, `chatType` (`direct|group|channel`, 带旧版 `dm` 别名), `keyPrefix`, 或 `rawKeyPrefix` 匹配。第一个拒绝优先。
- **`maintenance`**: `warn` 在驱逐时警告活动会话；`enforce` 应用修剪和轮换。
- **`threadBindings`**: 线程绑定会话功能的全局默认设置。
  - `enabled`: 主默认开关（提供商可以覆盖；Discord 使用 `channels.discord.threadBindings.enabled`）
  - `ttlHours`: 默认自动失焦TTL（小时）(`0` 禁用；提供商可以覆盖）

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

按频道/账户覆盖：`channels.<channel>.responsePrefix`, `channels.<channel>.accounts.<id>.responsePrefix`。

解析顺序（最具体者优先）：账户 → 频道 → 全局。`""` 禁用并停止级联。`"auto"` 派生自 `[{identity.name}]`。

**模板变量：**

| 变量          | 描述            | 示例                     |
| ----------------- | ---------------------- | --------------------------- |
| `{model}`         | 短模型名称       | `claude-opus-4-6`           |
| `{modelFull}`     | 完整模型标识符  | `anthropic/claude-opus-4-6` |
| `{provider}`      | 提供商名称          | `anthropic`                 |
| `{thinkingLevel}` | 当前思维水平 | `high`, `low`, `off`        |
| `{identity.name}` | 代理身份名称    | (与 `"auto"` 相同)          |

变量不区分大小写。`{think}` 是 `{thinkingLevel}` 的别名。

### 确认反应

- 默认为活动代理的 `identity.emoji`，否则为 `"👀"`。设置 `""` 以禁用。
- 按频道覆盖：`channels.<channel>.ackReaction`, `channels.<channel>.accounts.<id>.ackReaction`。
- 解析顺序：账户 → 频道 → `messages.ackReaction` → 身份回退。
- 作用域：`group-mentions`（默认），`group-all`, `direct`, `all`。
- `removeAckAfterReply`：回复后移除确认（仅限 Slack/Discord/Telegram/Google Chat）。

### 入站防抖

将同一发件人发送的快速纯文本消息批处理为单个代理回合。媒体/附件立即刷新。控制命令绕过防抖。

### TTS（文本转语音）

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
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
    },
  },
}
```

- `auto` 控制自动TTS。`/tts off|always|inbound|tagged` 覆盖每个会话。
- `summaryModel` 覆盖 `agents.defaults.model.primary` 的自动摘要。
- `modelOverrides` 默认启用；`modelOverrides.allowProvider` 默认为 `false`（选择加入）。
- API 密钥回退到 `ELEVENLABS_API_KEY`/`XI_API_KEY` 和 `OPENAI_API_KEY`。

---

## Talk

Talk 模式（macOS/iOS/Android）的默认设置。

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

- 声音ID 回退到 `ELEVENLABS_VOICE_ID` 或 `SAG_VOICE_ID`。
- `apiKey` 回退到 `ELEVENLABS_API_KEY`。
- `voiceAliases` 允许 Talk 指令使用友好名称。

---

## Tools

### 工具配置文件

`tools.profile` 在 `tools.allow`/`tools.deny` 之前设置基础白名单：

| 配置文件     | 包含                                                                                  |
| ----------- | ----------------------------------------------------------------------------------------- |
| `minimal`   | 仅 `session_status`                                                                     |
| `coding`    | `group:fs`, `group:runtime`, `group:sessions`, `group:memory`, `image`                    |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status` |
| `full`      | 无限制（与未设置相同）                                                            |

### 工具组

| 组              | 工具                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec`, `process` (`bash` 被接受为 `exec` 的别名)                            |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                   |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status` |
| `group:memory`     | `memory_search`, `memory_get`                                                            |
| `group:web`        | `web_search`, `web_fetch`                                                                |
| `group:ui`         | `browser`, `canvas`                                                                      |
| `group:automation` | `cron`, `gateway`                                                                        |
| `group:messaging`  | `message`                                                                                |
| `group:nodes`      | `nodes`                                                                                  |
| `group:openclaw`   | 所有内置工具（排除提供商插件）                                           |

### `tools.allow` / `tools.deny`

全局工具允许/拒绝策略（拒绝优先）。不区分大小写，支持 `*` 通配符。即使 Docker 沙盒关闭时也会应用。

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

控制提升（主机）执行访问权限：

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["steipete", "1234567890123"],
      },
    },
  },
}
```

- 每个代理覆盖 (`agents.list[].tools.elevated`) 只能进一步限制。
- `/elevated on|off|ask|full` 按会话存储状态；内联指令适用于单个消息。
- 提升的 `exec` 在主机上运行，绕过沙盒。

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

工具循环安全检查默认是**禁用**的。设置 `enabled: true` 以激活检测。
设置可以在 `tools.loopDetection` 中全局定义，并在每个代理的 `agents.list[].tools.loopDetection` 中进行覆盖。

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

- `historySize`: max tool-call history retained for loop analysis.
- `warningThreshold`: repeating no-progress pattern threshold for warnings.
- `criticalThreshold`: higher repeating threshold for blocking critical loops.
- `globalCircuitBreakerThreshold`: hard stop threshold for any no-progress run.
- `detectors.genericRepeat`: warn on repeated same-tool/same-args calls.
- `detectors.knownPollNoProgress`: warn/block on known poll tools (`process.poll`, `command_status`, etc.).
- `detectors.pingPong`: warn/block on alternating no-progress pair patterns.
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

<Accordion title="媒体模型入口字段">

**提供者入口** (`type: "provider"` 或省略)：

- `provider`: API 提供者 ID (`openai`, `anthropic`, `google`/`gemini`, `groq` 等)
- `model`: 模型 ID 覆盖
- `profile` / `preferredProfile`: 认证配置文件选择

**CLI 入口** (`type: "cli"`)：

- `command`: 要运行的可执行文件
- `args`: 模板化参数（支持 `{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}` 等）

**公共字段：**

- `capabilities`: 可选列表 (`image`, `audio`, `video`)。默认值：`openai`/`anthropic`/`minimax` → 图像, `google` → 图像+音频+视频, `groq` → 音频。
- `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`: 每个条目的覆盖。
- 失败时回退到下一个条目。

提供者认证遵循标准顺序：认证配置文件 → 环境变量 → `models.providers.*.apiKey`。

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

控制哪些会话可以被会话工具（`sessions_list`, `sessions_history`, `sessions_send`）定位。

默认值: `tree`（当前会话+由其生成的会话，例如子代理）。

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

注意事项：

- `self`：仅当前会话密钥。
- `tree`：当前会话+由当前会话生成的会话（子代理）。
- `agent`：属于当前代理ID的任何会话（如果您在同一代理ID下运行按发送者划分的会话，则可能包括其他用户）。
- `all`：任何会话。跨代理定位仍然需要`tools.agentToAgent`。
- 沙箱限制：当当前会话被沙箱化且`agents.defaults.sandbox.sessionToolsVisibility="spawned"`时，可见性会被强制设置为`tree`，即使`tools.sessions.visibility="all"`。

### `tools.subagents`

```json5
{
  agents: {
    defaults: {
      subagents: {
        model: "minimax/MiniMax-M2.1",
        maxConcurrent: 1,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

- `model`：生成的子代理的默认模型。如果省略，子代理将继承调用者的模型。
- 每个子代理工具策略：`tools.subagents.tools.allow` / `tools.subagents.tools.deny`。

---

## 自定义提供商和基础URL

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

- 使用 `authHeader: true` + `headers` 以满足自定义认证需求。
- 使用 `OPENCLAW_AGENT_DIR` 覆盖代理配置根（或 `PI_CODING_AGENT_DIR`）。

### 提供商示例

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

使用 `cerebras/zai-glm-4.7` 用于Cerebras；使用 `zai/glm-4.7` 用于Z.AI直接。

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

- 通用端点：`https://api.z.ai/api/paas/v4`
- 编码端点（默认）：`https://api.z.ai/api/coding/paas/v4`
- 对于通用端点，定义一个自定义提供者并覆盖基础URL。

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

对于中国端点：`baseUrl: "https://api.moonshot.cn/v1"` 或 `openclaw onboard --auth-choice moonshot-api-key-cn`。

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

兼容Anthropic的内置提供者。快捷方式：`openclaw onboard --auth-choice kimi-code-api-key`。

</Accordion>

<Accordion title="Synthetic (Anthropic-compatible)">

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.1" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.1": { alias: "MiniMax M2.1" } },
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
            id: "hf:MiniMaxAI/MiniMax-M2.1",
            name: "MiniMax M2.1",
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

基础URL应省略 `/v1`（Anthropic客户端会附加它）。快捷方式：`openclaw onboard --auth-choice synthetic-api-key`。

</Accordion>

<Accordion title="MiniMax M2.1 (直接)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.1" },
      models: {
        "minimax/MiniMax-M2.1": { alias: "Minimax" },
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
            id: "MiniMax-M2.1",
            name: "MiniMax M2.1",
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

参见 [本地模型](/gateway/local-models)。简而言之：在高性能硬件上通过LM Studio Responses API运行MiniMax M2.1；保留托管模型以备回退使用。

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
        apiKey: "GEMINI_KEY_HERE",
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: 仅适用于捆绑技能的可选白名单（管理/工作区技能不受影响）。
- `entries.<skillKey>.enabled: false` 即使捆绑/安装也会禁用技能。
- `entries.<skillKey>.apiKey`: 方便声明主要环境变量的技能。

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
        config: { provider: "twilio" },
      },
    },
  },
}
```

- 从 `~/.openclaw/extensions`、`<workspace>/.openclaw/extensions` 加载，加上 `plugins.load.paths`。
- **配置更改需要重启网关。**
- `allow`: 可选白名单（仅加载列出的插件）。`deny` 优先。

参见 [Plugins](/tools/plugin)。

---

## 浏览器

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    defaultProfile: "chrome",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    color: "#FF4500",
    // headless: false,
    // noSandbox: false,
    // executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    // attachOnly: false,
  },
}
```

- `evaluateEnabled: false` 禁用 `act:evaluate` 和 `wait --fn`。
- 远程配置文件仅支持附加（启动/停止/重置被禁用）。
- 自动检测顺序：默认浏览器（如果基于Chromium）→ Chrome → Brave → Edge → Chromium → Chrome Canary。
- 控制服务：仅限回环（端口从 `gateway.port` 派生，默认 `18791`）。

---

## 用户界面

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

- `seamColor`: 原生应用UI边框的强调色（对话模式气泡色调等）。
- `assistant`: 控制UI身份覆盖。回退到活动代理身份。

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

<Accordion title="网关字段详细信息">

- `mode`: `local` (运行网关) 或 `remote` (连接到远程网关). 网关除非 `local` 否则拒绝启动。
- `port`: 单个多路复用端口用于WS + HTTP。优先级: `--port` > `OPENCLAW_GATEWAY_PORT` > `gateway.port` > `18789`。
- `bind`: `auto`, `loopback` (默认), `lan` (`0.0.0.0`), `tailnet` (仅Tailscale IP), 或 `custom`。
- **Auth**: 默认需要。非回环绑定需要共享令牌/密码。入门向导默认生成一个令牌。
- `auth.mode: "none"`: 显式无认证模式。仅用于受信任的本地回环设置；此选项不会在入门提示中提供。
- `auth.mode: "trusted-proxy"`: 将认证委托给身份感知反向代理，并信任来自 `gateway.trustedProxies` 的身份头（参见 [可信代理认证](/gateway/trusted-proxy-auth)）。
- `auth.allowTailscale`: 当 `true` 时，Tailscale Serve 身份头可以满足控制UI/WebSocket认证（通过 `tailscale whois` 验证）；HTTP API 端点仍然需要令牌/密码认证。此无令牌流程假设网关主机是可信的。当 `tailscale.mode = "serve"` 时，默认为 `true`。
- `auth.rateLimit`: 可选的认证失败限制器。按客户端IP和认证范围（共享密钥和设备令牌独立跟踪）。被阻止的尝试返回 `429` + `Retry-After`。
  - `auth.rateLimit.exemptLoopback` 默认为 `true`；当您有意限制本地主机流量速率时设置 `false`（适用于测试设置或严格的代理部署）。
- `tailscale.mode`: `serve` (仅限尾网，回环绑定) 或 `funnel` (公共，需要认证)。
- `remote.transport`: `ssh` (默认) 或 `direct` (ws/wss)。对于 `direct`，`remote.url` 必须为 `ws://` 或 `wss://`。
- `gateway.remote.token` 仅用于远程CLI调用；不启用本地网关认证。
- `trustedProxies`: 终止TLS的反向代理IP。仅列出您控制的代理。
- `allowRealIpFallback`: 当 `true` 时，如果缺少 `X-Forwarded-For`，网关接受 `X-Real-IP`。默认 `false` 用于关闭失败行为。
- `gateway.tools.deny`: 额外的工具名称被阻止用于HTTP `POST /tools/invoke`（扩展默认拒绝列表）。
- `gateway.tools.allow`: 从默认HTTP拒绝列表中移除工具名称。

</Accordion>

### OpenAI兼容的端点

- 聊天补全: 默认禁用。使用 `gateway.http.endpoints.chatCompletions.enabled: true` 启用。
- 响应API: `gateway.http.endpoints.responses.enabled`。
- 响应URL输入强化:
  - `gateway.http.endpoints.responses.maxUrlParts`
  - `gateway.http.endpoints.responses.files.urlAllowlist`
  - `gateway.http.endpoints.responses.images.urlAllowlist`

### 多实例隔离

在同一主机上使用唯一端口和状态目录运行多个网关：

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json \
OPENCLAW_STATE_DIR=~/.openclaw-a \
openclaw gateway --port 19001
```

便捷标志: `--dev` (使用 `~/.openclaw-dev` + 端口 `19001`)，`--profile <name>` (使用 `~/.openclaw-<name>`)。

请参阅 [Multiple Gateways](/gateway/multiple-gateways).

---

## Hooks

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

Auth: `Authorization: Bearer <token>` 或 `x-openclaw-token: <token>`.

**Endpoints:**

- `POST /hooks/wake` → `{ text, mode?: "now"|"next-heartbeat" }`
- `POST /hooks/agent` → `{ message, name?, agentId?, sessionKey?, wakeMode?, deliver?, channel?, to?, model?, thinking?, timeoutSeconds? }`
  - 请求负载中的 `sessionKey` 仅在 `hooks.allowRequestSessionKey=true` (默认: `false`) 时被接受。
- `POST /hooks/<name>` → 通过 `hooks.mappings` 解析

<Accordion title="Mapping details">

- `match.path` 匹配 `/hooks` 之后的子路径（例如 `/hooks/gmail` → `gmail`）。
- `match.source` 匹配通用路径的负载字段。
- 类似于 `{{messages[0].subject}}` 的模板从负载中读取。
- `transform` 可以指向一个返回 hook 动作的 JS/TS 模块。
  - `transform.module` 必须是相对路径，并且保持在 `hooks.transformsDir` 内（拒绝绝对路径和遍历）。
- `agentId` 路由到特定代理；未知 ID 回退到默认。
- `allowedAgentIds`: 限制显式路由 (`*` 或省略 = 允许所有，`[]` = 拒绝所有)。
- `defaultSessionKey`: 可选的固定会话密钥，用于没有显式 `sessionKey` 的 hook 代理运行。
- `allowRequestSessionKey`: 允许 `/hooks/agent` 调用者设置 `sessionKey`（默认: `false`）。
- `allowedSessionKeyPrefixes`: 可选的显式 `sessionKey` 值（请求 + 映射）前缀白名单，例如 `["hook:"]`。
- `deliver: true` 将最终回复发送到通道；`channel` 默认为 `last`。
- `model` 覆盖此 hook 运行的 LLM（如果设置了模型目录，则必须允许）。

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

- Gateway 在启动时自动启动 `gog gmail watch serve`，当已配置时。设置 `OPENCLAW_SKIP_GMAIL_WATCHER=1` 以禁用。
- 不要在 Gateway 旁边运行单独的 `gog gmail watch serve`。

---

## Canvas host

```json5
{
  canvasHost: {
    root: "~/.openclaw/workspace/canvas",
    liveReload: true,
    // enabled: false, // or OPENCLAW_SKIP_CANVAS_HOST=1
  },
}
```

- 通过 Gateway 端口提供代理可编辑的 HTML/CSS/JS 和 A2UI：
  - `http://<gateway-host>:<gateway.port>/__openclaw__/canvas/`
  - `http://<gateway-host>:<gateway.port>/__openclaw__/a2ui/`
- 仅本地：保持 `gateway.bind: "loopback"`（默认）。
- 非回环绑定：canvas 路由需要 Gateway 认证（令牌/密码/受信任代理），与其他 Gateway HTTP 表面相同。
- Node WebViews 通常不发送认证头；在节点配对并连接后，Gateway 广告节点范围的能力 URL 用于 canvas/A2UI 访问。
- 能力 URL 绑定到活动节点 WS 会话并快速过期。不使用基于 IP 的回退。
- 将实时重载客户端注入提供的 HTML。
- 当为空时自动创建起始 `index.html`。
- 还在 `/__openclaw__/a2ui/` 提供 A2UI。
- 更改需要网关重启。
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

- `minimal`（默认）：从 TXT 记录中省略 `cliPath` + `sshPort`。
- `full`：包含 `cliPath` + `sshPort`。
- 主机名默认为 `openclaw`。使用 `OPENCLAW_MDNS_HOSTNAME` 覆盖。

### Wide-area (DNS-SD)

```json5
{
  discovery: {
    wideArea: { enabled: true },
  },
}
```

在 `~/.openclaw/dns/` 下写入单播 DNS-SD 区域。对于跨网络发现，请与 DNS 服务器（推荐 CoreDNS）+ Tailscale 分割 DNS 配对。

设置：`openclaw dns setup --apply`。

---

## Environment

### `env` (inline env vars)

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

- 内联环境变量仅在进程环境缺少该键时应用。
- `.env` 文件：CWD `.env` + `~/.openclaw/.env`（两者都不覆盖现有变量）。
- `shellEnv`：从登录 shell 配置文件导入缺失的预期键。
- 请参阅 [Environment](/help/environment) 了解完整的优先级。

### 环境变量替换

在任何配置字符串中引用环境变量，使用 `${VAR_NAME}`：

```json5
{
  gateway: {
    auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" },
  },
}
```

- 仅匹配大写名称：`[A-Z_][A-Z0-9_]*`。
- 缺少或空的变量在加载配置时会抛出错误。
- 使用 `$${VAR}` 转义以表示字面 `${VAR}`。
- 支持 `$include`。

---

## 认证存储

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

- 每个代理的认证配置文件存储在 `<agentDir>/auth-profiles.json`。
- 从 `~/.openclaw/credentials/oauth.json` 导入旧版 OAuth。
- 参见 [OAuth](/concepts/oauth)。

---

## 日志记录

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
- 设置 `logging.file` 以获得稳定的路径。
- 当 `--verbose` 发生变化时，`consoleLevel` 升级到 `debug`。

---

## 向导

由 CLI 向导 (`onboard`, `configure`, `doctor`) 写入的元数据：

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

## 身份

```json5
{
  agents: {
    list: [
      {
        id: "main",
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
      },
    ],
  },
}
```

由 macOS 入门助理编写。派生默认值：

- 从 `identity.emoji` 获取 `messages.ackReaction`（回退到 👀）
- 从 `identity.name`/`identity.emoji` 获取 `mentionPatterns`
- `avatar` 接受：工作区相对路径，`http(s)` URL 或 `data:` URI

---

## 桥接（旧版，已移除）

当前构建不再包含 TCP 桥接。节点通过网关 WebSocket 连接。`bridge.*` 密钥不再是配置架构的一部分（直到移除，验证才会失败；`openclaw doctor --fix` 可以剥离未知密钥）。

<Accordion title="旧版桥接配置（历史参考）">

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

## 定时任务

```json5
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 2,
    webhook: "https://example.invalid/legacy", // deprecated fallback for stored notify:true jobs
    webhookToken: "replace-with-dedicated-token", // optional bearer token for outbound webhook auth
    sessionRetention: "24h", // duration string or false
  },
}
```

- `sessionRetention`: 完成的cron会话保留多长时间。默认: `24h`。
- `webhookToken`: 用于cron webhook POST传递的bearer token (`delivery.mode = "webhook"`)，如果省略则不发送auth头。
- `webhook`: 已弃用的旧版回退webhook URL (http/https)，仅用于仍然具有`notify: true`的存储作业。

参见 [Cron Jobs](/automation/cron-jobs)。

---

## Media model模板变量

在`tools.media.*.models[].args`中展开的模板占位符：

| 变量           | 描述                                       |
| ------------------ | ------------------------------------------------- |
| `{{Body}}`         | 完整的入站消息体                         |
| `{{RawBody}}`      | 原始消息体（无历史/发件人包装）             |
| `{{BodyStripped}}` | 剔除群组提及的消息体                 |
| `{{From}}`         | 发件人标识符                                 |
| `{{To}}`           | 目标标识符                            |
| `{{MessageSid}}`   | 频道消息ID                                |
| `{{SessionId}}`    | 当前会话UUID                              |
| `{{IsNewSession}}` | `"true"` 当新会话创建时                 |
| `{{MediaUrl}}`     | 入站媒体伪URL                          |
| `{{MediaPath}}`    | 本地媒体路径                                  |
| `{{MediaType}}`    | 媒体类型 (image/audio/document/…)               |
| `{{Transcript}}`   | 音频转录                                  |
| `{{Prompt}}`       | 解析后的CLI条目的媒体提示             |
| `{{MaxChars}}`     | 解析后的CLI条目的最大输出字符数         |
| `{{ChatType}}`     | `"direct"` 或 `"group"`                           |
| `{{GroupSubject}}` | 群组主题（尽力而为）                       |
| `{{GroupMembers}}` | 群组成员预览（尽力而为）               |
| `{{SenderName}}`   | 发件人显示名称（尽力而为）                 |
| `{{SenderE164}}`   | 发件人电话号码（尽力而为）                 |
| `{{Provider}}`     | 提供商提示 (whatsapp, telegram, discord, 等) |

---

## 配置包含 (`$include`)

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

- 单个文件：替换包含对象。
- 文件数组：按顺序深度合并（后面的覆盖前面的）。
- 同级键：包含后合并（覆盖包含的值）。
- 嵌套包含：最多10层深。
- 路径：相对于包含文件解析，但必须保持在顶级配置目录内 (`dirname` 主配置文件）。仅允许绝对/`../` 形式当它们仍在该边界内解析时。
- 错误：缺失文件、解析错误和循环包含的清晰消息。

_Related: [Configuration](/gateway/configuration) · [Configuration Examples](/gateway/configuration-examples) · [Doctor](/gateway/doctor)_