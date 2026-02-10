---
summary: "All configuration options for ~/.openclaw/openclaw.json with examples"
read_when:
  - Adding or modifying config fields
title: "Configuration"
---
# 配置 🔧

OpenClaw 从 `~/.openclaw/openclaw.json` 读取一个可选的 **JSON5** 配置文件（允许注释和尾随逗号）。

如果文件缺失，OpenClaw 使用相对安全的默认设置（嵌入式 Pi 代理 + 按发送者会话 + 工作区 `~/.openclaw/workspace`）。您通常只需要一个配置来：

- 限制谁可以触发机器人 (`channels.whatsapp.allowFrom`, `channels.telegram.allowFrom` 等)
- 控制组白名单 + 提及行为 (`channels.whatsapp.groups`, `channels.telegram.groups`, `channels.discord.guilds`, `agents.list[].groupChat`)
- 自定义消息前缀 (`messages`)
- 设置代理的工作区 (`agents.defaults.workspace` 或 `agents.list[].workspace`)
- 调整嵌入式代理的默认设置 (`agents.defaults`) 和会话行为 (`session`)
- 设置每个代理的身份 (`agents.list[].identity`)

> **首次配置？** 查看 [配置示例](/gateway/configuration-examples) 指南以获取带有详细说明的完整示例！

## 严格的配置验证

OpenClaw 仅接受与架构完全匹配的配置。
未知键、格式错误的类型或无效值会导致网关 **拒绝启动** 以确保安全。

当验证失败时：

- 网关不会启动。
- 仅允许诊断命令（例如：`openclaw doctor`, `openclaw logs`, `openclaw health`, `openclaw status`, `openclaw service`, `openclaw help`）。
- 运行 `openclaw doctor` 查看确切的问题。
- 运行 `openclaw doctor --fix`（或 `--yes`）以应用迁移/修复。

Doctor 除非您明确选择 `--fix`/`--yes`，否则不会写入更改。

## 架构 + UI 提示

网关通过 `config.schema` 暴露配置的 JSON 架构表示，供 UI 编辑器使用。
控制 UI 根据此架构渲染表单，并提供一个 **原始 JSON** 编辑器作为逃生舱口。

通道插件和扩展可以注册其配置的架构 + UI 提示，因此通道设置
在应用程序之间保持架构驱动，而无需硬编码表单。

提示（标签、分组、敏感字段）与架构一起发布，以便客户端可以渲染
更好的表单而无需硬编码配置知识。

## 应用 + 重启（RPC）

使用 `config.apply` 在一步中验证 + 写入完整配置并重启网关。
它写入一个重启哨兵并在网关恢复后 ping 最后一个活动会话。

警告：`config.apply` 替换 **整个配置**。如果您只想更改一些键，
使用 `config.patch` 或 `openclaw config set`。备份 `~/.openclaw/openclaw.json`。

参数：

- `raw` (字符串) — 整个配置的 JSON5 负载
- `baseHash` (可选) — 来自 `config.get` 的配置哈希（当配置已存在时必需）
- `sessionKey` (可选) — 唤醒 ping 的最后一个活动会话密钥
- `note` (可选) — 包含在重启哨兵中的注释
- `restartDelayMs` (可选) — 重启前的延迟（默认 2000）

示例（通过 `gateway call`）：

```bash
openclaw gateway call config.get --params '{}' # capture payload.hash
openclaw gateway call config.apply --params '{
  "raw": "{\\n  agents: { defaults: { workspace: \\"~/.openclaw/workspace\\" } }\\n}\\n",
  "baseHash": "<hash-from-config.get>",
  "sessionKey": "agent:main:whatsapp:dm:+15555550123",
  "restartDelayMs": 1000
}'
```

## 部分更新 (RPC)

使用 `config.patch` 将部分更新合并到现有配置中而不覆盖无关键。它应用 JSON 合并补丁语义：

- 对象递归合并
- `null` 删除键
- 数组替换
  类似于 `config.apply`，它会验证、写入配置、存储重启哨兵并计划
  网关重启（在提供 `sessionKey` 时可选唤醒）。

参数：

- `raw` (string) — 仅包含要更改的键的 JSON5 负载
- `baseHash` (必需) — 来自 `config.get` 的配置哈希
- `sessionKey` (可选) — 唤醒 ping 的最后一个活动会话密钥
- `note` (可选) — 包含在重启哨兵中的注释
- `restartDelayMs` (可选) — 重启前的延迟（默认 2000）

示例：

```bash
openclaw gateway call config.get --params '{}' # capture payload.hash
openclaw gateway call config.patch --params '{
  "raw": "{\\n  channels: { telegram: { groups: { \\"*\\": { requireMention: false } } } }\\n}\\n",
  "baseHash": "<hash-from-config.get>",
  "sessionKey": "agent:main:whatsapp:dm:+15555550123",
  "restartDelayMs": 1000
}'
```

## 最小配置（推荐起点）

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

使用以下命令构建默认镜像一次：

```bash
scripts/sandbox-setup.sh
```

## 自我对话模式（推荐用于群组控制）

防止机器人在群组中响应 WhatsApp @提及（仅响应特定文本触发器）：

```json5
{
  agents: {
    defaults: { workspace: "~/.openclaw/workspace" },
    list: [
      {
        id: "main",
        groupChat: { mentionPatterns: ["@openclaw", "reisponde"] },
      },
    ],
  },
  channels: {
    whatsapp: {
      // Allowlist is DMs only; including your own number enables self-chat mode.
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
}
```

## 配置包含 (`$include`)

使用 `$include` 指令将配置拆分为多个文件。这在以下情况下很有用：

- 组织大型配置（例如，每个客户端代理定义）
- 在环境中共享通用设置
- 保持敏感配置独立

### 基本用法

```json5
// ~/.openclaw/openclaw.json
{
  gateway: { port: 18789 },

  // Include a single file (replaces the key's value)
  agents: { $include: "./agents.json5" },

  // Include multiple files (deep-merged in order)
  broadcast: {
    $include: ["./clients/mueller.json5", "./clients/schmidt.json5"],
  },
}
```

```json5
// ~/.openclaw/agents.json5
{
  defaults: { sandbox: { mode: "all", scope: "session" } },
  list: [{ id: "main", workspace: "~/.openclaw/workspace" }],
}
```

### 合并行为

- **单个文件**: 替换包含 `$include` 的对象
- **文件数组**: 按顺序深度合并文件（后面的文件会覆盖前面的文件）
- **带有兄弟键**: 兄弟键在包含后合并（覆盖包含的值）
- **兄弟键 + 数组/基本类型**: 不支持（包含的内容必须是对象）

```json5
// Sibling keys override included values
{
  $include: "./base.json5", // { a: 1, b: 2 }
  b: 99, // Result: { a: 1, b: 99 }
}
```

### 嵌套包含

包含的文件本身可以包含 `$include` 指令（最多嵌套10层）：

```json5
// clients/mueller.json5
{
  agents: { $include: "./mueller/agents.json5" },
  broadcast: { $include: "./mueller/broadcast.json5" },
}
```

### 路径解析

- **相对路径**: 相对于包含文件进行解析
- **绝对路径**: 直接使用
- **父目录**: `../` 引用按预期工作

```json5
{ "$include": "./sub/config.json5" }      // relative
{ "$include": "/etc/openclaw/base.json5" } // absolute
{ "$include": "../shared/common.json5" }   // parent dir
```

### 错误处理

- **缺失文件**: 显示解析后的路径错误
- **解析错误**: 显示哪个包含的文件失败
- **循环包含**: 检测并报告包含链

### 示例: 多客户端法律设置

```json5
// ~/.openclaw/openclaw.json
{
  gateway: { port: 18789, auth: { token: "secret" } },

  // Common agent defaults
  agents: {
    defaults: {
      sandbox: { mode: "all", scope: "session" },
    },
    // Merge agent lists from all clients
    list: { $include: ["./clients/mueller/agents.json5", "./clients/schmidt/agents.json5"] },
  },

  // Merge broadcast configs
  broadcast: {
    $include: ["./clients/mueller/broadcast.json5", "./clients/schmidt/broadcast.json5"],
  },

  channels: { whatsapp: { groupPolicy: "allowlist" } },
}
```

```json5
// ~/.openclaw/clients/mueller/agents.json5
[
  { id: "mueller-transcribe", workspace: "~/clients/mueller/transcribe" },
  { id: "mueller-docs", workspace: "~/clients/mueller/docs" },
]
```

```json5
// ~/.openclaw/clients/mueller/broadcast.json5
{
  "120363403215116621@g.us": ["mueller-transcribe", "mueller-docs"],
}
```

## 常见选项

### 环境变量 + `.env`

OpenClaw 从父进程读取环境变量（shell、launchd/systemd、CI 等）。

此外，它还会加载：

- 当前工作目录中的 `.env`（如果存在）
- 全局后备 `.env` 从 `~/.openclaw/.env`（即 `$OPENCLAW_STATE_DIR/.env`）

`.env` 文件不会覆盖现有的环境变量。

你还可以在配置中提供内联环境变量。这些仅在进程环境缺少该键时应用（相同的非覆盖规则）：

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: {
      GROQ_API_KEY: "gsk-...",
    },
  },
}
```

请参阅 [/environment](/help/environment) 以获取完整的优先级和来源。

### `env.shellEnv` (可选)

选择加入的便利性：如果启用且尚未设置任何预期的键，OpenClaw 将运行您的登录 shell 并仅导入缺失的预期键（从不覆盖）。
这实际上会加载您的 shell 配置文件。

```json5
{
  env: {
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

环境变量等效：

- `OPENCLAW_LOAD_SHELL_ENV=1`
- `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`

### 配置中的环境变量替换

您可以在任何配置字符串值中直接引用环境变量，使用 `${VAR_NAME}` 语法。变量在配置加载时进行替换，在验证之前。

```json5
{
  models: {
    providers: {
      "vercel-gateway": {
        apiKey: "${VERCEL_GATEWAY_API_KEY}",
      },
    },
  },
  gateway: {
    auth: {
      token: "${OPENCLAW_GATEWAY_TOKEN}",
    },
  },
}
```

**规则：**

- 仅匹配大写的环境变量名称：`[A-Z_][A-Z0-9_]*`
- 缺少或为空的环境变量在配置加载时会抛出错误
- 使用 `$${VAR}` 转义以输出字面的 `${VAR}`
- 支持 `$include`（包含的文件也会进行替换）

**内联替换：**

```json5
{
  models: {
    providers: {
      custom: {
        baseUrl: "${CUSTOM_API_BASE}/v1", // → "https://api.example.com/v1"
      },
    },
  },
}
```

### 认证存储（OAuth + API 密钥）

OpenClaw 存储 **每个代理** 的认证配置文件（OAuth + API 密钥）在：

- `<agentDir>/auth-profiles.json`（默认：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`）

另见：[/concepts/oauth](/concepts/oauth)

旧版 OAuth 导入：

- `~/.openclaw/credentials/oauth.json`（或 `$OPENCLAW_STATE_DIR/credentials/oauth.json`）

嵌入的 Pi 代理维护一个运行时缓存：

- `<agentDir>/auth.json`（自动管理；请勿手动编辑）

旧版代理目录（多代理之前）：

- `~/.openclaw/agent/*`（由 `openclaw doctor` 迁移到 `~/.openclaw/agents/<defaultAgentId>/agent/*`）

覆盖：

- OAuth 目录（仅限旧版导入）：`OPENCLAW_OAUTH_DIR`
- 代理目录（默认代理根目录覆盖）：`OPENCLAW_AGENT_DIR`（首选），`PI_CODING_AGENT_DIR`（旧版）

首次使用时，OpenClaw 将 `oauth.json` 条目导入到 `auth-profiles.json`。

### `auth`

认证配置文件的可选元数据。这不会存储机密信息；它将
配置文件 ID 映射到提供程序 + 模式（以及可选的电子邮件），并定义用于故障转移的提供程序轮换顺序。

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

### `agents.list[].identity`

每个代理的可选标识符，用于默认设置和用户体验。这是由 macOS 入门助手编写的。

如果已设置，OpenClaw 将推导默认设置（仅当您未显式设置时）：

- `messages.ackReaction` from the **active agent**’s `identity.emoji` (falls back to 👀)
- `agents.list[].groupChat.mentionPatterns` from the agent’s `identity.name`/`identity.emoji` (so “@Samantha” works in groups across Telegram/Slack/Discord/Google Chat/iMessage/WhatsApp)
- `identity.avatar` accepts a workspace-relative image path or a remote URL/data URL. Local files must live inside the agent workspace.

`identity.avatar` accepts:

- Workspace-relative path (must stay within the agent workspace)
- `http(s)` URL
- `data:` URI

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

### `wizard`

Metadata written by CLI wizards (`onboard`, `configure`, `doctor`).

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

### `logging`

- Default log file: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`
- If you want a stable path, set `logging.file` to `/tmp/openclaw/openclaw.log`.
- Console output can be tuned separately via:
  - `logging.consoleLevel` (defaults to `info`, bumps to `debug` when `--verbose`)
  - `logging.consoleStyle` (`pretty` | `compact` | `json`)
- Tool summaries can be redacted to avoid leaking secrets:
  - `logging.redactSensitive` (`off` | `tools`, default: `tools`)
  - `logging.redactPatterns` (array of regex strings; overrides defaults)

```json5
{
  logging: {
    level: "info",
    file: "/tmp/openclaw/openclaw.log",
    consoleLevel: "info",
    consoleStyle: "pretty",
    redactSensitive: "tools",
    redactPatterns: [
      // Example: override defaults with your own rules.
      "\\bTOKEN\\b\\s*[=:]\\s*([\"']?)([^\\s\"']+)\\1",
      "/\\bsk-[A-Za-z0-9_-]{8,}\\b/gi",
    ],
  },
}
```

### `channels.whatsapp.dmPolicy`

Controls how WhatsApp direct chats (DMs) are handled:

- `"pairing"` (default): unknown senders get a pairing code; owner must approve
- `"allowlist"`: only allow senders in `channels.whatsapp.allowFrom` (or paired allow store)
- `"open"`: allow all inbound DMs (**requires** `channels.whatsapp.allowFrom` to include `"*"`)
- `"disabled"`: ignore all inbound DMs

Pairing codes expire after 1 hour; the bot only sends a pairing code when a new request is created. Pending DM pairing requests are capped at **3 per channel** by default.

Pairing approvals:

- `openclaw pairing list whatsapp`
- `openclaw pairing approve whatsapp <code>`

### `channels.whatsapp.allowFrom`

Allowlist of E.164 phone numbers that may trigger WhatsApp auto-replies (**DMs only**).
If empty and `channels.whatsapp.dmPolicy="pairing"`, unknown senders will receive a pairing code.
For groups, use `channels.whatsapp.groupPolicy` + `channels.whatsapp.groupAllowFrom`.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000, // optional outbound chunk size (chars)
      chunkMode: "length", // optional chunking mode (length | newline)
      mediaMaxMb: 50, // optional inbound media cap (MB)
    },
  },
}
```

### `channels.whatsapp.sendReadReceipts`

控制传入的WhatsApp消息是否被标记为已读（蓝色勾号）。默认值: `true`。

自我聊天模式始终跳过已读回执，即使已启用。

按账户覆盖: `channels.whatsapp.accounts.<id>.sendReadReceipts`。

```json5
{
  channels: {
    whatsapp: { sendReadReceipts: false },
  },
}
```

### `channels.whatsapp.accounts` (多账户)

在一个网关中运行多个WhatsApp账户：

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: {}, // optional; keeps the default id stable
        personal: {},
        biz: {
          // Optional override. Default: ~/.openclaw/credentials/whatsapp/biz
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

注意事项：

- 如果存在，则外发命令默认使用账户 `default`；否则使用第一个配置的账户ID（按排序）。
- 旧的单账户Baileys认证目录由 `openclaw doctor` 迁移到 `whatsapp/default`。

### `channels.telegram.accounts` / `channels.discord.accounts` / `channels.googlechat.accounts` / `channels.slack.accounts` / `channels.mattermost.accounts` / `channels.signal.accounts` / `channels.imessage.accounts`

每个通道运行多个账户（每个账户有自己的 `accountId` 和可选的 `name`）：

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

注意事项：

- 当省略 `accountId` 时使用 `default`（CLI + 路由）。
- 环境令牌仅适用于 **默认** 账户。
- 基本通道设置（群组策略、提及门控等）适用于所有账户，除非按账户进行覆盖。
- 使用 `bindings[].match.accountId` 将每个账户路由到不同的代理.defaults。

### 群聊提及门控 (`agents.list[].groupChat` + `messages.groupChat`)

群组消息默认为 **需要提及**（元数据提及或正则表达式模式）。适用于WhatsApp、Telegram、Discord、Google Chat和iMessage群组聊天。

**提及类型：**

- **元数据提及**：平台原生@提及（例如，WhatsApp点击提及）。在WhatsApp自我聊天模式下忽略（见 `channels.whatsapp.allowFrom`）。
- **文本模式**：在 `agents.list[].groupChat.mentionPatterns` 中定义的正则表达式模式。无论自我聊天模式如何，始终检查。
- 提及门控仅在可能检测到提及时强制执行（原生提及或至少一个 `mentionPattern`）。

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

`messages.groupChat.historyLimit` 设置全局默认的组历史上下文。频道可以使用 `channels.<channel>.historyLimit` 覆盖（或使用 `channels.<channel>.accounts.*.historyLimit` 用于多账户）。设置 `0` 以禁用历史记录换行。

#### DM 历史记录限制

DM 对话使用由代理管理的基于会话的历史记录。您可以限制每个 DM 会话保留的用户轮次数量：

```json5
{
  channels: {
    telegram: {
      dmHistoryLimit: 30, // limit DM sessions to 30 user turns
      dms: {
        "123456789": { historyLimit: 50 }, // per-user override (user ID)
      },
    },
  },
}
```

解析顺序：

1. 每个 DM 的覆盖：`channels.<provider>.dms[userId].historyLimit`
2. 提供程序默认值：`channels.<provider>.dmHistoryLimit`
3. 无限制（保留所有历史记录）

支持的提供程序：`telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`.

每个代理的覆盖（设置时优先，即使设置了 `[]`）：

```json5
{
  agents: {
    list: [
      { id: "work", groupChat: { mentionPatterns: ["@workbot", "\\+15555550123"] } },
      { id: "personal", groupChat: { mentionPatterns: ["@homebot", "\\+15555550999"] } },
    ],
  },
}
```

提及门控默认值按频道存在 (`channels.whatsapp.groups`, `channels.telegram.groups`, `channels.imessage.groups`, `channels.discord.guilds`)。当设置了 `*.groups` 时，它还充当组允许列表；包含 `"*"` 以允许所有组。

仅响应特定文本触发器（忽略原生 @-提及）：

```json5
{
  channels: {
    whatsapp: {
      // Include your own number to enable self-chat mode (ignore native @-mentions).
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          // Only these text patterns will trigger responses
          mentionPatterns: ["reisponde", "@openclaw"],
        },
      },
    ],
  },
}
```

### 组策略（每个频道）

使用 `channels.*.groupPolicy` 控制是否接受组/房间消息：

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
    telegram: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["tg:123456789", "@alice"],
    },
    signal: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
    imessage: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["chat_id:123"],
    },
    msteams: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["user@org.com"],
    },
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        GUILD_ID: {
          channels: { help: { allow: true } },
        },
      },
    },
    slack: {
      groupPolicy: "allowlist",
      channels: { "#general": { allow: true } },
    },
  },
}
```

注意事项:

- `"open"`: 组绕过白名单；提及门控仍然适用。
- `"disabled"`: 阻止所有组/房间消息。
- `"allowlist"`: 仅允许与配置的白名单匹配的组/房间。
- `channels.defaults.groupPolicy` 设置当提供者的 `groupPolicy` 未设置时的默认值。
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams 使用 `groupAllowFrom`（回退：显式 `allowFrom`）。
- Discord/Slack 使用频道白名单 (`channels.discord.guilds.*.channels`, `channels.slack.channels`)。
- 组DM（Discord/Slack）仍然由 `dm.groupEnabled` + `dm.groupChannels` 控制。
- 默认是 `groupPolicy: "allowlist"`（除非被 `channels.defaults.groupPolicy` 覆盖）；如果没有配置白名单，则阻止组消息。

### 多代理路由 (`agents.list` + `bindings`)

在一个网关内部运行多个隔离的代理（单独的工作区, `agentDir`, 会话）。
入站消息通过绑定路由到代理。

- `agents.list[]`: 每个代理的覆盖设置。
  - `id`: 稳定的代理ID（必需）。
  - `default`: 可选；当设置多个时，第一个生效并记录警告。
    如果没有设置任何值，则列表中的**第一个条目**为默认代理。
  - `name`: 代理的显示名称。
  - `workspace`: 默认 `~/.openclaw/workspace-<agentId>`（对于 `main`，回退到 `agents.defaults.workspace`）。
  - `agentDir`: 默认 `~/.openclaw/agents/<agentId>/agent`。
  - `model`: 每个代理的默认模型，覆盖该代理的 `agents.defaults.model`。
    - 字符串形式：`"provider/model"`，仅覆盖 `agents.defaults.model.primary`
    - 对象形式：`{ primary, fallbacks }`（回退覆盖 `agents.defaults.model.fallbacks`；`[]` 禁用该代理的全局回退）
  - `identity`: 每个代理的名称/主题/表情符号（用于提及模式 + 确认反应）。
  - `groupChat`: 每个代理的提及门控 (`mentionPatterns`)。
  - `sandbox`: 每个代理的沙盒配置（覆盖 `agents.defaults.sandbox`）。
    - `mode`: `"off"` | `"non-main"` | `"all"`
    - `workspaceAccess`: `"none"` | `"ro"` | `"rw"`
    - `scope`: `"session"` | `"agent"` | `"shared"`
    - `workspaceRoot`: 自定义沙盒工作区根目录
    - `docker`: 每个代理的Docker覆盖设置（例如 `image`，`network`，`env`，`setupCommand`，限制；当 `scope: "shared"` 时忽略）
    - `browser`: 每个代理的沙盒浏览器覆盖设置（当 `scope: "shared"` 时忽略）
    - `prune`: 每个代理的沙盒修剪覆盖设置（当 `scope: "shared"` 时忽略）
  - `subagents`: 每个代理的子代理默认设置。
    - `allowAgents`: 允许从该代理访问的代理ID列表 `sessions_spawn` (`["*"]` = 允许任何；默认：仅相同代理)
  - `tools`: 每个代理的工具限制（在沙盒工具策略之前应用）。
    - `profile`: 基础工具配置文件（在允许/拒绝之前应用）
    - `allow`: 允许的工具名称数组
    - `deny`: 拒绝的工具名称数组（拒绝优先）
- `agents.defaults`: 共享代理默认设置（模型、工作区、沙盒等）。
- `bindings[]`: 将传入消息路由到一个 `agentId`。
  - `match.channel`（必需）
  - `match.accountId`（可选；`*` = 任意账户；省略 = 默认账户）
  - `match.peer`（可选；`{ kind: direct|group|channel, id }`）
  - `match.guildId` / `match.teamId`（可选；特定于频道）

确定性匹配顺序：

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId`（精确匹配，无对等体/公会/团队）
5. `match.accountId: "*"`（频道范围，无对等体/公会/团队）
6. 默认代理 (`agents.list[].default`，否则列表中的第一个条目，否则 `"main"`)

在每个匹配层级中，`bindings` 中的第一个匹配条目获胜。

#### 每个代理的访问配置文件（多代理）

每个代理可以携带自己的沙盒 + 工具策略。使用此功能在一个网关中混合访问级别：

- **完全访问**（个人代理）
- **只读** 工具 + 工作区
- **无文件系统访问**（仅消息/会话工具）

请参阅 [Multi-Agent Sandbox & Tools](/tools/multi-agent-sandbox-tools) 获取先例和
更多示例。

完全访问（无沙箱）：

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

只读工具 + 只读工作区：

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "ro",
        },
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

无文件系统访问（启用消息/会话工具）：

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "none",
        },
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

示例：两个 WhatsApp 账户 → 两个代理：

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
  channels: {
    whatsapp: {
      accounts: {
        personal: {},
        biz: {},
      },
    },
  },
}
```

### `tools.agentToAgent`（可选）

代理间消息传递是可选的：

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

### `messages.queue`

控制当代理运行已激活时传入消息的行为。

```json5
{
  messages: {
    queue: {
      mode: "collect", // steer | followup | collect | steer-backlog (steer+backlog ok) | interrupt (queue=steer legacy)
      debounceMs: 1000,
      cap: 20,
      drop: "summarize", // old | new | summarize
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
        discord: "collect",
        imessage: "collect",
        webchat: "collect",
      },
    },
  },
}
```

### `messages.inbound`

对来自**同一发送者**的快速传入消息进行防抖处理，使多个连续的消息合并为单个代理回合。防抖处理按通道 + 对话进行范围限定，并使用最近的消息进行回复线程/ID处理。

```json5
{
  messages: {
    inbound: {
      debounceMs: 2000, // 0 disables
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
        discord: 1500,
      },
    },
  },
}
```

注意事项：

- 防抖处理仅限**纯文本**消息；媒体/附件会立即刷新。
- 控制命令（例如 `/queue`, `/new`）绕过防抖处理，因此保持独立。

### `commands` (聊天命令处理)

控制跨连接器启用聊天命令的方式。

```json5
{
  commands: {
    native: "auto", // register native commands when supported (auto)
    text: true, // parse slash commands in chat messages
    bash: false, // allow ! (alias: /bash) (host-only; requires tools.elevated allowlists)
    bashForegroundMs: 2000, // bash foreground window (0 backgrounds immediately)
    config: false, // allow /config (writes to disk)
    debug: false, // allow /debug (runtime-only overrides)
    restart: false, // allow /restart + gateway restart tool
    allowFrom: {
      "*": ["user1"], // optional per-provider command allowlist
      discord: ["user:123"],
    },
    useAccessGroups: true, // enforce access-group allowlists/policies for commands
  },
}
```

注意事项：

- 文本命令必须作为**独立**消息发送，并使用前导 `/`（不使用纯文本别名）。
- `commands.text: false` 禁用解析聊天消息中的命令。
- `commands.native: "auto"`（默认）启用Discord/Telegram的原生命令，并关闭Slack；不支持的频道保持纯文本。
- 设置 `commands.native: true|false` 强制所有频道，或通过 `channels.discord.commands.native`，`channels.telegram.commands.native`，`channels.slack.commands.native`（布尔值或 `"auto"`）按频道覆盖。`false` 在启动时清除Discord/Telegram上先前注册的命令；Slack命令在Slack应用中管理。
- `channels.telegram.customCommands` 添加额外的Telegram机器人菜单条目。名称会被标准化；与原生命令冲突的会被忽略。
- `commands.bash: true` 启用 `! <cmd>` 运行主机shell命令（`/bash <cmd>` 也可以作为别名）。需要 `tools.elevated.enabled` 并在 `tools.elevated.allowFrom.<channel>` 中允许发送者。
- `commands.bashForegroundMs` 控制bash在后台运行前等待的时间。当bash作业正在运行时，新的 `! <cmd>` 请求会被拒绝（一次一个）。
- `commands.config: true` 启用 `/config`（读写 `openclaw.json`）。
- `channels.<provider>.configWrites` 控制该频道发起的配置变更（默认：true）。这适用于 `/config set|unset` 以及特定提供商的自动迁移（Telegram超级群组ID更改，Slack频道ID更改）。
- `commands.debug: true` 启用 `/debug`（仅运行时覆盖）。
- `commands.restart: true` 启用 `/restart` 和网关工具重启操作。
- `commands.allowFrom` 为命令执行设置每个提供商的白名单。配置后，它是**唯一**
  的授权来源，命令和指令（频道白名单/配对和 `commands.useAccessGroups` 被忽略）。
  使用 `"*"` 设置全局默认值；特定提供商的键（例如 `discord`）会覆盖它。
- `commands.useAccessGroups: false` 允许命令绕过访问组白名单/策略，当 `commands.allowFrom`
  未设置时。
- 斜杠命令和指令仅对**授权发送者**有效。如果设置了 `commands.allowFrom`，
  授权仅来自该列表；否则，它从频道白名单/配对加上
  `commands.useAccessGroups` 派生。

### `web`（WhatsApp Web频道运行时）

WhatsApp 通过网关的Web频道（Baileys Web）运行。当存在链接会话时，它会自动启动。
设置 `web.enabled: false` 默认情况下将其关闭。

```json5
{
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

### `channels.telegram`（机器人传输）

OpenClaw 仅在存在 `channels.telegram` 配置部分时启动 Telegram。机器人令牌从 `channels.telegram.botToken`（或 `channels.telegram.tokenFile`）解析，使用 `TELEGRAM_BOT_TOKEN` 作为默认账户的备用。
设置 `channels.telegram.enabled: false` 以禁用自动启动。
多账户支持位于 `channels.telegram.accounts` 下（参见上方的多账户部分）。环境令牌仅适用于默认账户。
设置 `channels.telegram.configWrites: false` 以阻止 Telegram 初始化的配置写入（包括超级群组ID迁移和 `/config set|unset`）。

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["tg:123456789"], // optional; "open" requires ["*"]
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
      historyLimit: 50, // include last N group messages as context (0 disables)
      replyToMode: "first", // off | first | all
      linkPreview: true, // toggle outbound link previews
      streamMode: "partial", // off | partial | block (draft streaming; separate from block streaming)
      draftChunk: {
        // optional; only for streamMode=block
        minChars: 200,
        maxChars: 800,
        breakPreference: "paragraph", // paragraph | newline | sentence
      },
      actions: { reactions: true, sendMessage: true }, // tool action gates (false disables)
      reactionNotifications: "own", // off | own | all
      mediaMaxMb: 5,
      retry: {
        // outbound retry policy
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: {
        // transport overrides
        autoSelectFamily: false,
      },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook", // requires webhookSecret
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

草稿流式传输说明：

- 使用 Telegram `sendMessageDraft`（草稿气泡，不是真实消息）。
- 需要 **私人聊天主题**（DM中的 message_thread_id；机器人已启用主题）。
- `/reasoning stream` 将推理流式传输到草稿中，然后发送最终答案。
重试策略的默认设置和行为记录在 [重试策略](/concepts/retry) 中。

### `channels.discord`（机器人传输）

通过设置bot token和可选的门控来配置Discord bot：
多账号支持位于 `channels.discord.accounts`（参见上方的多账号部分）。Env tokens仅适用于默认账号。

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 8, // clamp inbound media size
      allowBots: false, // allow bot-authored messages
      actions: {
        // tool action gates (false disables)
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
      dm: {
        enabled: true, // disable all DMs when false
        policy: "pairing", // pairing | allowlist | open | disabled
        allowFrom: ["1234567890", "steipete"], // optional DM allowlist ("open" requires ["*"])
        groupEnabled: false, // enable group DMs
        groupChannels: ["openclaw-dm"], // optional group DM allowlist
      },
      guilds: {
        "123456789012345678": {
          // guild id (preferred) or slug
          slug: "friends-of-openclaw",
          requireMention: false, // per-guild default
          reactionNotifications: "own", // off | own | all | allowlist
          users: ["987654321098765432"], // optional per-guild user allowlist
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
      historyLimit: 20, // include last N guild messages as context
      textChunkLimit: 2000, // optional outbound text chunk size (chars)
      chunkMode: "length", // optional chunking mode (length | newline)
      maxLinesPerMessage: 17, // soft max lines per message (Discord UI clipping)
      retry: {
        // outbound retry policy
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

OpenClaw 仅在存在 `channels.discord` 配置部分时启动 Discord。令牌从 `channels.discord.token` 解析，使用 `DISCORD_BOT_TOKEN` 作为默认账户的备用（除非 `channels.discord.enabled` 是 `false`）。指定 cron/CLI 命令的传递目标时使用 `user:<id>`（私信）或 `channel:<id>`（服务器频道）；纯数字ID是模糊的且会被拒绝。
服务器别名是小写，空格替换为 `-`；频道键使用连字符化的频道名称（不带前导 `#`）。优先使用服务器ID作为键以避免重命名歧义。
默认忽略机器人发送的消息。通过启用 `channels.discord.allowBots` 来开启（自己的消息仍然会被过滤以防止自我回复循环）。
反应通知模式：

- `off`：无反应事件。
- `own`：对机器人自身消息的反应（默认）。
- `all`：所有消息的所有反应。
- `allowlist`：来自 `guilds.<id>.users` 的所有消息的反应（空列表禁用）。
  发送的文本按 `channels.discord.textChunkLimit` 分块（默认2000）。设置 `channels.discord.chunkMode="newline"` 以在长度分块之前按空白行（段落边界）拆分。Discord 客户端可能会截断非常长的消息，因此即使少于2000个字符，`channels.discord.maxLinesPerMessage`（默认17）也会拆分长的多行回复。
  重试策略的默认值和行为记录在 [Retry policy](/concepts/retry) 中。

### `channels.googlechat` (聊天API Webhook)

Google Chat 通过带有应用级身份验证（服务账户）的HTTP Webhook 运行。
多账户支持位于 `channels.googlechat.accounts` 下（参见上述多账户部分）。环境变量仅适用于默认账户。

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url", // app-url | project-number
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890", // optional; improves mention detection
      dm: {
        enabled: true,
        policy: "pairing", // pairing | allowlist | open | disabled
        allowFrom: ["users/1234567890"], // optional; "open" requires ["*"]
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

注意事项：

- 服务账户JSON可以内联 (`serviceAccount`) 或基于文件 (`serviceAccountFile`)。
- 默认账户的环境变量回退：`GOOGLE_CHAT_SERVICE_ACCOUNT` 或 `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`。
- `audienceType` + `audience` 必须与聊天应用的Webhook身份验证配置匹配。
- 设置传递目标时使用 `spaces/<spaceId>` 或 `users/<userId|email>`。

### `channels.slack` (套接字模式)

Slack 运行在套接字模式下，并需要一个机器人令牌和应用令牌：

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",
      dm: {
        enabled: true,
        policy: "pairing", // pairing | allowlist | open | disabled
        allowFrom: ["U123", "U456", "*"], // optional; "open" requires ["*"]
        groupEnabled: false,
        groupChannels: ["G123"],
      },
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
      historyLimit: 50, // include last N channel/group messages as context (0 disables)
      allowBots: false,
      reactionNotifications: "own", // off | own | all | allowlist
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
      mediaMaxMb: 20,
    },
  },
}
```

多账户支持位于 `channels.slack.accounts` 下（参见上方的多账户部分）。Env 令牌仅适用于默认账户。

当提供者启用且两个令牌均设置好（通过 config 或 `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN`）时，OpenClaw 启动 Slack。使用 `user:<id>`（私信）或 `channel:<id>` 指定时钟/CLI 命令的交付目标。
设置 `channels.slack.configWrites: false` 以阻止 Slack 初始化的配置写入（包括频道 ID 迁移和 `/config set|unset`）。

默认情况下忽略机器人发送的消息。通过 `channels.slack.allowBots` 或 `channels.slack.channels.<id>.allowBots` 启用。

反应通知模式：

- `off`：无反应事件。
- `own`：对机器人的消息进行反应（默认）。
- `all`：对所有消息的所有反应。
- `allowlist`：对所有消息来自 `channels.slack.reactionAllowlist` 的反应（空列表禁用）。

线程会话隔离：

- `channels.slack.thread.historyScope` 控制线程历史记录是按线程 (`thread`，默认) 还是在整个频道中共享 (`channel`)。
- `channels.slack.thread.inheritParent` 控制新线程会话是否继承父频道的对话记录（默认：false）。

Slack 动作组（门控 `slack` 工具动作）：

| 动作组 | 默认值 | 备注                  |
| ------------ | ------- | ---------------------- |
| reactions    | enabled | React + 列出反应 |
| messages     | enabled | 读取/发送/编辑/删除  |
| pins         | enabled | 固定/取消固定/列出         |
| memberInfo   | enabled | 成员信息            |
| emojiList    | enabled | 自定义表情符号列表      |

### `channels.mattermost` (bot token)

Mattermost 作为一个插件提供，并不包含在核心安装中。
首先安装它：`openclaw plugins install @openclaw/mattermost` （或从 git 检出 `./extensions/mattermost`）。

Mattermost 需要一个 bot token 加上你的服务器的基础 URL：

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

当账户配置好（bot token + 基础 URL）并启用时，OpenClaw 启动 Mattermost。token + 基础 URL 从 `channels.mattermost.botToken` + `channels.mattermost.baseUrl` 或 `MATTERMOST_BOT_TOKEN` + `MATTERMOST_URL` 解析，默认账户（除非 `channels.mattermost.enabled` 是 `false`）。

聊天模式：

- `oncall` （默认）：仅在被 @ 提及时响应频道消息。
- `onmessage`：响应每个频道消息。
- `onchar`：当消息以触发前缀开头时响应 (`channels.mattermost.oncharPrefixes`，默认 `[">", "!"]`)。

访问控制：

- 默认私信：`channels.mattermost.dmPolicy="pairing"` （未知发送者收到配对码）。
- 公共私信：`channels.mattermost.dmPolicy="open"` 加上 `channels.mattermost.allowFrom=["*"]`。
- 群组：默认 `channels.mattermost.groupPolicy="allowlist"` （提及门控）。使用 `channels.mattermost.groupAllowFrom` 来限制发送者。

多账户支持位于 `channels.mattermost.accounts` 下（参见上面的多账户部分）。环境变量仅适用于默认账户。
指定交付目标时使用 `channel:<id>` 或 `user:<id>` （或 `@username`）；裸 ID 被视为频道 ID。

### `channels.signal` (signal-cli)

Signal 反应可以发出系统事件（共享反应工具）：

```json5
{
  channels: {
    signal: {
      reactionNotifications: "own", // off | own | all | allowlist
      reactionAllowlist: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      historyLimit: 50, // include last N group messages as context (0 disables)
    },
  },
}
```

反应通知模式：

- `off`：无反应事件。
- `own`：机器人自己消息上的反应（默认）。
- `all`：所有消息上的所有反应。
- `allowlist`：所有消息上的来自 `channels.signal.reactionAllowlist` 的反应（空列表禁用）。

### `channels.imessage` (imsg CLI)

OpenClaw 启动 `imsg rpc` （通过 stdio 的 JSON-RPC）。无需守护进程或端口。

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host", // SCP for remote attachments when using SSH wrapper
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123"],
      historyLimit: 50, // include last N group messages as context (0 disables)
      includeAttachments: false,
      mediaMaxMb: 16,
      service: "auto",
      region: "US",
    },
  },
}
```

多账户支持位于 `channels.imessage.accounts` 下（参见上方的多账户部分）。

注意事项：

- 需要对Messages数据库进行完全磁盘访问。
- 第一次发送时会提示请求Messages自动化权限。
- 偏好使用 `chat_id:<id>` 目标。使用 `imsg chats --limit 20` 列出聊天。
- `channels.imessage.cliPath` 可以指向一个包装脚本（例如 `ssh` 到运行 `imsg rpc` 的另一台Mac）；使用SSH密钥以避免密码提示。
- 对于远程SSH包装器，在启用 `includeAttachments` 时设置 `channels.imessage.remoteHost` 通过SCP获取附件。

示例包装器：

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

### `agents.defaults.workspace`

设置代理用于文件操作的**单一全局工作区目录**。

默认值：`~/.openclaw/workspace`。

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

如果启用了 `agents.defaults.sandbox`，非主会话可以在 `agents.defaults.sandbox.workspaceRoot` 下用自己的每个作用域工作区覆盖此设置。

### `agents.defaults.repoRoot`

可选的仓库根目录，显示在系统提示的运行时行中。如果未设置，OpenClaw会尝试从工作区（和当前工作目录）向上查找 `.git` 目录。路径必须存在才能使用。

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skipBootstrap`

禁用工作区引导文件（`AGENTS.md`，`SOUL.md`，`TOOLS.md`，`IDENTITY.md`，`USER.md`，`HEARTBEAT.md` 和 `BOOTSTRAP.md`）的自动创建。

在工作区文件来自仓库的预置部署中使用此选项。

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.bootstrapMaxChars`

在截断前注入到系统提示中的每个工作区引导文件的最大字符数。默认值：`20000`。

当文件超出此限制时，OpenClaw会记录警告并注入带有标记的截断头/尾。

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.userTimezone`

设置用户的时区以供**系统提示上下文**使用（不用于消息信封中的时间戳）。如果未设置，OpenClaw会在运行时使用主机时区。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

控制系统提示中“当前日期和时间”部分显示的**时间格式**。
默认值: `auto` (操作系统偏好)。

```json5
{
  agents: { defaults: { timeFormat: "auto" } }, // auto | 12 | 24
}
```

### `messages`

控制入站/出站前缀和可选的确认反应。
有关排队、会话和流式上下文的信息，请参阅[消息](/concepts/messages)。

```json5
{
  messages: {
    responsePrefix: "🦞", // or "auto"
    ackReaction: "👀",
    ackReactionScope: "group-mentions",
    removeAckAfterReply: false,
  },
}
```

`responsePrefix` 应用于所有渠道的**所有出站回复**（工具摘要、块流式传输、最终回复），除非已经存在。

可以按渠道和账户进行覆盖配置：

- `channels.<channel>.responsePrefix`
- `channels.<channel>.accounts.<id>.responsePrefix`

覆盖顺序（最具体的优先）：

1. `channels.<channel>.accounts.<id>.responsePrefix`
2. `channels.<channel>.responsePrefix`
3. `messages.responsePrefix`

语义：

- `undefined` 转到下一级。
- `""` 显式禁用前缀并停止级联。
- `"auto"` 为路由代理派生 `[{identity.name}]`。

覆盖适用于所有渠道，包括扩展，并适用于每种类型的出站回复。

如果 `messages.responsePrefix` 未设置，默认不应用前缀。WhatsApp 自我聊天回复是例外：当设置时，默认为 `[{identity.name}]`，否则为 `[openclaw]`，以便同一手机上的对话保持可读性。
将其设置为 `"auto"` 以派生 `[{identity.name}]` 为路由代理（当设置时）。

#### 模板变量

`responsePrefix` 字符串可以包含动态解析的模板变量：

| 变量          | 描述            | 示例                     |
| ----------------- | ---------------------- | --------------------------- |
| `{model}`         | 简短模型名称       | `claude-opus-4-6`, `gpt-4o` |
| `{modelFull}`     | 完整模型标识符  | `anthropic/claude-opus-4-6` |
| `{provider}`      | 提供商名称          | `anthropic`, `openai`       |
| `{thinkingLevel}` | 当前思考级别 | `high`, `low`, `off`        |
| `{identity.name}` | 代理身份名称    | （与 `"auto"` 模式相同）     |

变量不区分大小写 (`{MODEL}` = `{model}`)。`{think}` 是 `{thinkingLevel}` 的别名。
未解析的变量保持为字面文本。

```json5
{
  messages: {
    responsePrefix: "[{model} | think:{thinkingLevel}]",
  },
}
```

示例输出: `[claude-opus-4-6 | think:high] Here's my response...`

WhatsApp 入站前缀通过 `channels.whatsapp.messagePrefix` 进行配置（已弃用：`messages.messagePrefix`)。默认值**保持不变**：当 `channels.whatsapp.allowFrom` 为空时为 `"[openclaw]"`，否则为 `""`（无前缀）。使用 `"[openclaw]"` 时，OpenClaw 将改为使用 `[{identity.name}]` 当路由代理设置了 `identity.name`。

`ackReaction` 发送最佳努力的表情符号反应以确认支持反应的渠道上的传入消息（Slack/Discord/Telegram/Google Chat）。默认使用活动代理的 `identity.emoji`，否则使用 `"👀"`。设置为 `""` 以禁用。

`ackReactionScope` 控制何时触发反应：

- `group-mentions`（默认）：仅当群组/房间需要提及 **且** 机器人被提及时
- `group-all`：所有群组/房间消息
- `direct`：仅直接消息
- `all`：所有消息

`removeAckAfterReply` 在发送回复后移除机器人的确认反应（仅限 Slack/Discord/Telegram/Google Chat）。默认：`false`。

#### `messages.tts`

启用出站回复的文本转语音功能。开启后，OpenClaw 使用 ElevenLabs 或 OpenAI 生成音频并将其附加到响应中。Telegram 使用 Opus 语音便签；其他渠道发送 MP3 音频。

```json5
{
  messages: {
    tts: {
      auto: "always", // off | always | inbound | tagged
      mode: "final", // final | all (include tool/block replies)
      provider: "elevenlabs",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: {
        enabled: true,
      },
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

注意事项：

- `messages.tts.auto` 控制自动 TTS（`off`，`always`，`inbound`，`tagged`）。
- `/tts off|always|inbound|tagged` 设置会话级别的自动模式（覆盖配置）。
- `messages.tts.enabled` 是旧版；医生将其迁移到 `messages.tts.auto`。
- `prefsPath` 存储本地覆盖（提供商/限制/摘要）。
- `maxTextLength` 是 TTS 输入的硬性上限；摘要会被截断以适应。
- `summaryModel` 覆盖 `agents.defaults.model.primary` 的自动摘要。
  - 接受 `provider/model` 或来自 `agents.defaults.models` 的别名。
- `modelOverrides` 启用模型驱动的覆盖，如 `[[tts:...]]` 标签（默认开启）。
- `/tts limit` 和 `/tts summary` 控制每个用户的摘要设置。
- `apiKey` 的值回退到 `ELEVENLABS_API_KEY`/`XI_API_KEY` 和 `OPENAI_API_KEY`。
- `elevenlabs.baseUrl` 覆盖 ElevenLabs API 基础 URL。
- `elevenlabs.voiceSettings` 支持 `stability`/`similarityBoost`/`style` (0..1)，
  `useSpeakerBoost`，和 `speed` (0.5..2.0)。

### `talk`

Talk模式（macOS/iOS/Android）的默认设置。Voice IDs 在未设置时回退到 `ELEVENLABS_VOICE_ID` 或 `SAG_VOICE_ID`。
`apiKey` 在未设置时回退到 `ELEVENLABS_API_KEY`（或网关的shell配置文件）。
`voiceAliases` 允许Talk指令使用友好名称（例如 `"voice":"Clawd"`）。

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

### `agents.defaults`

控制嵌入代理运行时（模型/思考/详细输出/超时）。
`agents.defaults.models` 定义配置的模型目录（并作为 `/model` 的白名单）。
`agents.defaults.model.primary` 设置默认模型；`agents.defaults.model.fallbacks` 是全局备用选项。
`agents.defaults.imageModel` 是可选的，**仅在主模型缺乏图像输入时使用**。
每个 `agents.defaults.models` 条目可以包括：

- `alias`（可选模型快捷方式，例如 `/opus`）。
- `params`（可选提供程序特定的API参数传递给模型请求）。

`params` 也应用于流式运行（嵌入代理 + 压缩）。当前支持的键：`temperature`，`maxTokens`。这些与调用时选项合并；调用者提供的值优先。`temperature` 是一个高级设置——除非你知道模型的默认值并且需要更改，否则不要设置。

示例：

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-sonnet-4-5-20250929": {
          params: { temperature: 0.6 },
        },
        "openai/gpt-5.2": {
          params: { maxTokens: 8192 },
        },
      },
    },
  },
}
```

Z.AI GLM-4.x 模型会自动启用思考模式，除非你：

- 设置 `--thinking off`，或
- 自定义 `agents.defaults.models["zai/<model>"].params.thinking`。

OpenClaw 还附带了一些内置别名缩写。默认值仅在模型已经存在于 `agents.defaults.models` 中时应用：

- `opus` -> `anthropic/claude-opus-4-6`
- `sonnet` -> `anthropic/claude-sonnet-4-5`
- `gpt` -> `openai/gpt-5.2`
- `gpt-mini` -> `openai/gpt-5-mini`
- `gemini` -> `google/gemini-3-pro-preview`
- `gemini-flash` -> `google/gemini-3-flash-preview`

如果你自己配置了相同的别名名称（不区分大小写），你的值会生效（默认值永远不会覆盖）。

示例：Opus 4.6 主模型，MiniMax M2.1 备用模型（托管 MiniMax）：

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
    },
  },
}
```

MiniMax 认证：设置 `MINIMAX_API_KEY`（环境变量）或配置 `models.providers.minimax`。

#### `agents.defaults.cliBackends`（CLI 备用）

可选的CLI后端用于仅文本的回退运行（不调用工具）。当API提供商失败时，这些后端很有用。当你配置一个`imageArg`以接受文件路径时，支持图像直通。

注意事项：

- CLI后端是**文本优先**的；工具总是被禁用。
- 当`sessionArg`设置时，支持会话；每个后端会持久化会话ID。
- 对于`claude-cli`，默认值已连接。如果PATH最小化（launchd/systemd），请覆盖命令路径。

示例：

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

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "anthropic/claude-sonnet-4-1": { alias: "Sonnet" },
        "openrouter/deepseek/deepseek-r1:free": {},
        "zai/glm-4.7": {
          alias: "GLM",
          params: {
            thinking: {
              type: "enabled",
              clear_thinking: false,
            },
          },
        },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: [
          "openrouter/deepseek/deepseek-r1:free",
          "openrouter/meta-llama/llama-3.3-70b-instruct:free",
        ],
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
      heartbeat: {
        every: "30m",
        target: "last",
      },
      maxConcurrent: 3,
      subagents: {
        model: "minimax/MiniMax-M2.1",
        maxConcurrent: 1,
        archiveAfterMinutes: 60,
      },
      exec: {
        backgroundMs: 10000,
        timeoutSec: 1800,
        cleanupMs: 1800000,
      },
      contextTokens: 200000,
    },
  },
}
```

#### `agents.defaults.contextPruning`（工具结果修剪）

`agents.defaults.contextPruning`在向LLM发送请求之前从内存上下文中修剪**旧的工具结果**。
它**不会**修改磁盘上的会话历史记录（`*.jsonl`保持完整）。

这旨在减少随着时间积累大量工具输出的对话代理的令牌使用量。

高层次：

- 永不触碰用户/助手消息。
- 保护最后的 `keepLastAssistants` 助手消息（在此点之后的所有工具结果都不会被修剪）。
- 保护引导前缀（第一个用户消息之前的内容不会被修剪）。
- 模式：
  - `adaptive`: 当估算的上下文比例超过 `softTrimRatio` 时，对过大的工具结果进行软修剪（保留头部和尾部）。然后当估算的上下文比例超过 `hardClearRatio` **并且**
    存在足够的可修剪的工具结果总量 (`minPrunableToolChars`) 时，硬清除最旧的合格工具结果。
  - `aggressive`: 在截止时间之前总是用 `hardClear.placeholder` 替换合格的工具结果（不进行比例检查）。

软修剪与硬修剪（发送到LLM的上下文中的变化）：

- **软修剪**：仅适用于 _过大的_ 工具结果。保留开头和结尾，并在中间插入 `...`。
  - 之前: `toolResult("…very long output…")`
  - 之后: `toolResult("HEAD…\n...\n…TAIL\n\n[Tool result trimmed: …]")`
- **硬清除**：将整个工具结果替换为占位符。
  - 之前: `toolResult("…very long output…")`
  - 之后: `toolResult("[Old tool result content cleared]")`

注意事项 / 当前限制：

- 目前包含 **图像块** 的工具结果会被跳过（从不修剪/清除）。
- 估算的“上下文比例”基于 **字符**（近似），而不是确切的标记。
- 如果会话中还没有至少 `keepLastAssistants` 条助手消息，则跳过修剪。
- 在 `aggressive` 模式下，忽略 `hardClear.enabled`（合格的工具结果总是被替换为 `hardClear.placeholder`）。

默认（自适应）：

```json5
{
  agents: { defaults: { contextPruning: { mode: "adaptive" } } },
}
```

要禁用：

```json5
{
  agents: { defaults: { contextPruning: { mode: "off" } } },
}
```

默认值（当 `mode` 是 `"adaptive"` 或 `"aggressive"` 时）：

- `keepLastAssistants`: `3`
- `softTrimRatio`: `0.3`（仅自适应）
- `hardClearRatio`: `0.5`（仅自适应）
- `minPrunableToolChars`: `50000`（仅自适应）
- `softTrim`: `{ maxChars: 4000, headChars: 1500, tailChars: 1500 }`（仅自适应）
- `hardClear`: `{ enabled: true, placeholder: "[Old tool result content cleared]" }`

示例（激进，最小化）：

```json5
{
  agents: { defaults: { contextPruning: { mode: "aggressive" } } },
}
```

示例（自适应调优）：

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "adaptive",
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Old tool result content cleared]" },
        // Optional: restrict pruning to specific tools (deny wins; supports "*" wildcards)
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

参见 [/concepts/session-pruning](/concepts/session-pruning) 获取行为详情。

#### `agents.defaults.compaction` (reserve headroom + memory flush)

`agents.defaults.compaction.mode` 选择压缩摘要策略。默认为 `default`；设置 `safeguard` 以启用非常长历史记录的分块摘要。参见 [/concepts/compaction](/concepts/compaction)。

`agents.defaults.compaction.reserveTokensFloor` 强制 Pi 压缩的最小 `reserveTokens` 值（默认：`20000`）。将其设置为 `0` 以禁用下限。

`agents.defaults.compaction.memoryFlush` 在自动压缩之前运行一个 **静默** 代理回合，指示模型将持久化内存存储到磁盘（例如 `memory/YYYY-MM-DD.md`）。当会话令牌估计值超过压缩限制下的软阈值时触发。

旧版默认值：

- `memoryFlush.enabled`: `true`
- `memoryFlush.softThresholdTokens`: `4000`
- `memoryFlush.prompt` / `memoryFlush.systemPrompt`: 内置默认值使用 `NO_REPLY`
- 注意：当会话工作区为只读时跳过内存刷新（`agents.defaults.sandbox.workspaceAccess: "ro"` 或 `"none"`）。

示例（调优）：

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard",
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

块流式传输：

- `agents.defaults.blockStreamingDefault`: `"on"`/`"off"`（默认关闭）。
- 通道覆盖：`*.blockStreaming`（以及每个账户的变体）以强制块流式传输开启/关闭。
  非 Telegram 通道需要显式 `*.blockStreaming: true` 以启用块回复。
- `agents.defaults.blockStreamingBreak`: `"text_end"` 或 `"message_end"`（默认：text_end）。
- `agents.defaults.blockStreamingChunk`: 流式传输块的软分块。默认为
  800–1200 字符，优先段落换行 (`\n\n`)，然后换行符，然后句子。
  示例：

  ```json5
  {
    agents: { defaults: { blockStreamingChunk: { minChars: 800, maxChars: 1200 } } },
  }
  ```

- `agents.defaults.blockStreamingCoalesce`: 合并在发送之前流式传输的块。
  默认为 `{ idleMs: 1000 }` 并从 `blockStreamingChunk` 继承 `minChars`
  且 `maxChars` 限制在频道文本限制内。Signal/Slack/Discord/Google Chat 默认
  为 `minChars: 1500` 除非被覆盖。
  频道覆盖: `channels.whatsapp.blockStreamingCoalesce`, `channels.telegram.blockStreamingCoalesce`,
  `channels.discord.blockStreamingCoalesce`, `channels.slack.blockStreamingCoalesce`, `channels.mattermost.blockStreamingCoalesce`,
  `channels.signal.blockStreamingCoalesce`, `channels.imessage.blockStreamingCoalesce`, `channels.msteams.blockStreamingCoalesce`,
  `channels.googlechat.blockStreamingCoalesce`
  （以及每个账户的变体）。
- `agents.defaults.humanDelay`: 第一条回复之后的 **块回复** 之间的随机暂停。
  模式: `off`（默认），`natural`（800–2500毫秒），`custom`（使用 `minMs`/`maxMs`）。
  每个代理覆盖: `agents.list[].humanDelay`。
  示例:

  ```json5
  {
    agents: { defaults: { humanDelay: { mode: "natural" } } },
  }
  ```

  请参阅 [/concepts/streaming](/concepts/streaming) 获取行为和分块详细信息。

输入指示器：

- `agents.defaults.typingMode`: `"never" | "instant" | "thinking" | "message"`。默认为
  直接聊天/提及时为 `instant`，未提及的群聊时为 `message`。
- `session.typingMode`: 每个会话的模式覆盖。
- `agents.defaults.typingIntervalSeconds`: 输入信号刷新的频率（默认：6秒）。
- `session.typingIntervalSeconds`: 每个会话的刷新间隔覆盖。
  请参阅 [/concepts/typing-indicators](/concepts/typing-indicators) 获取行为详细信息。

`agents.defaults.model.primary` 应设置为 `provider/model`（例如 `anthropic/claude-opus-4-6`）。
别名来自 `agents.defaults.models.*.alias`（例如 `Opus`）。
如果您省略提供者，OpenClaw 目前假设 `anthropic` 作为临时
弃用回退。
Z.AI 模型可用作 `zai/<model>`（例如 `zai/glm-4.7`）并需要
环境中的 `ZAI_API_KEY`（或旧版 `Z_AI_API_KEY`）。

`agents.defaults.heartbeat` 配置周期性心跳运行：

- `every`: 持续时间字符串 (`ms`, `s`, `m`, `h`)；默认单位分钟。默认:
  `30m`。设置 `0m` 以禁用。
- `model`: 可选的心跳运行覆盖模型 (`provider/model`)。
- `includeReasoning`: 当 `true` 时，心跳也会在可用时发送单独的 `Reasoning:` 消息（与 `/reasoning on` 形状相同）。默认: `false`。
- `session`: 可选的会话密钥以控制心跳运行的会话。默认: `main`。
- `to`: 可选的接收者覆盖（特定于通道的ID，例如 WhatsApp 的 E.164，Telegram 的聊天 ID）。
- `target`: 可选的交付通道 (`last`, `whatsapp`, `telegram`, `discord`, `slack`, `msteams`, `signal`, `imessage`, `none`)。默认: `last`。
- `prompt`: 可选的心跳体覆盖（默认: `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`)。覆盖内容将原样发送；如果仍然需要读取文件，请包含一行 `Read HEARTBEAT.md`。
- `ackMaxChars`: 在交付前允许的最大字符数 `HEARTBEAT_OK`（默认: 300）。

每个代理的心跳：

- 设置 `agents.list[].heartbeat` 以启用或覆盖特定代理的心跳设置。
- 如果任何代理条目定义了 `heartbeat`，**只有这些代理** 运行心跳；默认值
  成为这些代理的共享基线。

心跳运行完整的代理轮次。较短的时间间隔会消耗更多的令牌；注意 `every`，保持 `HEARTBEAT.md` 小巧，并/或选择一个更便宜的 `model`。

`tools.exec` 配置后台执行默认设置：

- `backgroundMs`: 自动后台的时间（毫秒，默认 10000）
- `timeoutSec`: 自动终止的运行时间（秒，默认 1800）
- `cleanupMs`: 在内存中保留已完成会话的时间（毫秒，默认 1800000）
- `notifyOnExit`: 当后台执行退出时排队系统事件并请求心跳（默认 true）
- `applyPatch.enabled`: 启用实验性 `apply_patch`（仅适用于 OpenAI/OpenAI Codex；默认 false）
- `applyPatch.allowModels`: 可选的模型ID白名单（例如 `gpt-5.2` 或 `openai/gpt-5.2`）
  注意: `applyPatch` 仅在 `tools.exec` 下有效。

`tools.web` 配置网络搜索 + 获取工具：

- `tools.web.search.enabled` (default: true 当键存在时)
- `tools.web.search.apiKey` (推荐: 通过 `openclaw configure --section web` 设置，或使用 `BRAVE_API_KEY` 环境变量)
- `tools.web.search.maxResults` (1–10, 默认 5)
- `tools.web.search.timeoutSeconds` (默认 30)
- `tools.web.search.cacheTtlMinutes` (默认 15)
- `tools.web.fetch.enabled` (默认 true)
- `tools.web.fetch.maxChars` (默认 50000)
- `tools.web.fetch.maxCharsCap` (默认 50000; 从配置/工具调用中限制 maxChars)
- `tools.web.fetch.timeoutSeconds` (默认 30)
- `tools.web.fetch.cacheTtlMinutes` (默认 15)
- `tools.web.fetch.userAgent` (可选覆盖)
- `tools.web.fetch.readability` (默认 true; 禁用以仅使用基本 HTML 清理)
- `tools.web.fetch.firecrawl.enabled` (当设置 API 密钥时默认为 true)
- `tools.web.fetch.firecrawl.apiKey` (可选; 默认为 `FIRECRAWL_API_KEY`)
- `tools.web.fetch.firecrawl.baseUrl` (默认 [https://api.firecrawl.dev](https://api.firecrawl.dev))
- `tools.web.fetch.firecrawl.onlyMainContent` (默认 true)
- `tools.web.fetch.firecrawl.maxAgeMs` (可选)
- `tools.web.fetch.firecrawl.timeoutSeconds` (可选)

`tools.media` 配置入站媒体理解（图像/音频/视频）：

- `tools.media.models`: 共享模型列表（按功能标签标记；在每个功能列表之后使用）。
- `tools.media.concurrency`: 最大并发功能运行数（默认为2）。
- `tools.media.image` / `tools.media.audio` / `tools.media.video`:
  - `enabled`: 排除开关（当配置模型时默认为true）。
  - `prompt`: 可选提示覆盖（图像/视频自动附加`maxChars`提示）。
  - `maxChars`: 最大输出字符数（图像/视频默认为500；音频未设置）。
  - `maxBytes`: 发送的最大媒体大小（默认：图像10MB，音频20MB，视频50MB）。
  - `timeoutSeconds`: 请求超时时间（默认：图像60秒，音频60秒，视频120秒）。
  - `language`: 可选音频提示。
  - `attachments`: 附件策略 (`mode`, `maxAttachments`, `prefer`)。
  - `scope`: 可选门控（第一个匹配获胜）使用 `match.channel`, `match.chatType`, 或 `match.keyPrefix`。
  - `models`: 按顺序排列的模型条目；失败或媒体过大则回退到下一个条目。
- 每个 `models[]` 条目：
  - 提供商条目 (`type: "provider"` 或省略)：
    - `provider`: API提供商ID (`openai`, `anthropic`, `google`/`gemini`, `groq` 等)。
    - `model`: 模型ID覆盖（图像必需；音频提供商默认为 `gpt-4o-mini-transcribe`/`whisper-large-v3-turbo`，视频默认为 `gemini-3-flash-preview`）。
    - `profile` / `preferredProfile`: 认证配置文件选择。
  - CLI条目 (`type: "cli"`)：
    - `command`: 要运行的可执行文件。
    - `args`: 模板参数（支持 `{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}` 等）。
  - `capabilities`: 可选列表 (`image`, `audio`, `video`) 用于门控共享条目。省略时默认：`openai`/`anthropic`/`minimax` → 图像, `google` → 图像+音频+视频, `groq` → 音频。
  - `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language` 可以按条目覆盖。

如果没有配置模型（或 `enabled: false`），理解步骤将被跳过；模型仍然会收到原始附件。

提供商认证遵循标准模型认证顺序（认证配置文件、环境变量如 `OPENAI_API_KEY`/`GROQ_API_KEY`/`GEMINI_API_KEY` 或 `models.providers.*.apiKey`）。

示例：

```json5
{
  tools: {
    media: {
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

`agents.defaults.subagents` 配置子代理默认值：

- `model`: 子代理生成时的默认模型（字符串或 `{ primary, fallbacks }`）。如果省略，则子代理继承调用者的模型，除非每个代理或每次调用时被覆盖。
- `maxConcurrent`: 最大并发子代理运行数（默认 1）
- `archiveAfterMinutes`: 子代理会话在 N 分钟后自动归档（默认 60；设置 `0` 以禁用）
- 每个子代理工具策略：`tools.subagents.tools.allow` / `tools.subagents.tools.deny`（拒绝优先）

`tools.profile` 在 `tools.allow`/`tools.deny` 之前设置一个 **基础工具白名单**：

- `minimal`: 仅 `session_status`
- `coding`: `group:fs`, `group:runtime`, `group:sessions`, `group:memory`, `image`
- `messaging`: `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`
- `full`: 无限制（与未设置相同）

每个代理覆盖：`agents.list[].tools.profile`。

示例（默认仅限消息传递，允许 Slack 和 Discord 工具）：

```json5
{
  tools: {
    profile: "messaging",
    allow: ["slack", "discord"],
  },
}
```

示例（编码配置文件，但拒绝所有地方的 exec/process）：

```json5
{
  tools: {
    profile: "coding",
    deny: ["group:runtime"],
  },
}
```

`tools.byProvider` 允许您对特定提供商（或单个 `provider/model`）**进一步限制**工具。
每个代理覆盖：`agents.list[].tools.byProvider`。

顺序：基础配置文件 → 提供商配置文件 → 允许/拒绝策略。
提供商键接受 `provider`（例如 `google-antigravity`）或 `provider/model`
（例如 `openai/gpt-5.2`）。

示例（保持全局编码配置文件，但 Google Antigravity 的工具最少）：

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
  },
}
```

示例（提供商/模型特定的白名单）：

```json5
{
  tools: {
    allow: ["group:fs", "group:runtime", "sessions_list"],
    byProvider: {
      "openai/gpt-5.2": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

`tools.allow` / `tools.deny` 配置全局工具允许/拒绝策略（拒绝优先）。
匹配不区分大小写，并支持 `*` 通配符（`"*"` 表示所有工具）。
即使 Docker 沙盒**关闭**时也会应用此策略。

示例（禁用所有地方的浏览器/画布）：

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

工具组（简写）在**全局**和**每个代理**工具策略中工作：

- `group:runtime`: `exec`, `bash`, `process`
- `group:fs`: `read`, `write`, `edit`, `apply_patch`
- `group:sessions`: `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status`
- `group:memory`: `memory_search`, `memory_get`
- `group:web`: `web_search`, `web_fetch`
- `group:ui`: `browser`, `canvas`
- `group:automation`: `cron`, `gateway`
- `group:messaging`: `message`
- `group:nodes`: `nodes`
- `group:openclaw`: 所有内置的 OpenClaw 工具（排除提供商插件）

`tools.elevated` 控制提升（主机）exec 访问权限：

- `enabled`: allow elevated mode (default true)
- `allowFrom`: per-channel allowlists (empty = disabled)
  - `whatsapp`: E.164 numbers
  - `telegram`: chat ids or usernames
  - `discord`: user ids or usernames (falls back to `channels.discord.dm.allowFrom` if omitted)
  - `signal`: E.164 numbers
  - `imessage`: handles/chat ids
  - `webchat`: session ids or usernames

示例:

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

每个代理的覆盖（进一步限制）:

```json5
{
  agents: {
    list: [
      {
        id: "family",
        tools: {
          elevated: { enabled: false },
        },
      },
    ],
  },
}
```

注意事项:

- `tools.elevated` 是全局基线。`agents.list[].tools.elevated` 只能进一步限制（两者都必须允许）。
- `/elevated on|off|ask|full` 按会话密钥存储状态；内联指令适用于单个消息。
- 提升的 `exec` 在主机上运行并绕过沙盒。
- 工具策略仍然适用；如果 `exec` 被拒绝，则无法使用提升。

`agents.defaults.maxConcurrent` 设置可以跨会话并行执行的最大嵌入代理运行次数。每个会话仍然是串行的（每个会话密钥一次运行）。默认值：1。

### `agents.defaults.sandbox`

可选的 **Docker 沙盒** 用于嵌入代理。旨在用于非主会话，以便它们无法访问您的主机系统。

详细信息：[沙盒](/gateway/sandboxing)

默认值（如果启用）：

- 作用域：`"agent"`（每个代理一个容器 + 工作区）
- 基于 Debian bookworm-slim 的镜像
- 代理工作区访问：`workspaceAccess: "none"`（默认）
  - `"none"`: 使用 `~/.openclaw/sandboxes` 下的按作用域沙盒工作区
- `"ro"`: 将沙盒工作区保留在 `/workspace`，并将代理工作区以只读方式挂载到 `/agent`（禁用 `write`/`edit`/`apply_patch`）
  - `"rw"`: 将代理工作区以读写方式挂载到 `/workspace`
- 自动清理：空闲 > 24小时 或 年龄 > 7天
- 工具策略：仅允许 `exec`，`process`，`read`，`write`，`edit`，`apply_patch`，`sessions_list`，`sessions_history`，`sessions_send`，`sessions_spawn`，`session_status`（拒绝优先）
  - 通过 `tools.sandbox.tools` 配置，通过 `agents.list[].tools.sandbox.tools` 每个代理覆盖
  - 沙盒策略中支持的工具组缩写：`group:runtime`，`group:fs`，`group:sessions`，`group:memory`（参见 [沙盒 vs 工具策略 vs 提升](/gateway/sandbox-vs-tool-policy-vs-elevated#tool-groups-shorthands)）
- 可选的沙盒浏览器（Chromium + CDP，noVNC 观察者）
- 硬化选项：`network`，`user`，`pidsLimit`，`memory`，`cpus`，`ulimits`，`seccompProfile`，`apparmorProfile`

警告：`scope: "shared"` 表示共享容器和共享工作区。没有跨会话隔离。使用 `scope: "session"` 进行每个会话的隔离。

遗留：`perSession` 仍然受支持 (`true` → `scope: "session"`，`false` → `scope: "shared"`)。

`setupCommand` 在容器创建后**运行一次**（通过 `sh -lc` 在容器内部）。
对于包安装，请确保网络出口、可写的根文件系统以及root用户。

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        scope: "agent", // session | agent | shared (agent is default)
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
          // Per-agent override (multi-agent): agents.list[].sandbox.docker.*
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
          binds: ["/var/run/docker.sock:/var/run/docker.sock", "/home/user/source:/source:rw"],
        },
        browser: {
          enabled: false,
          image: "openclaw-sandbox-browser:bookworm-slim",
          containerPrefix: "openclaw-sbx-browser-",
          cdpPort: 9222,
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          allowHostControl: false,
          allowedControlUrls: ["http://10.0.0.42:18791"],
          allowedControlHosts: ["browser.lab.local", "10.0.0.42"],
          allowedControlPorts: [18791],
          autoStart: true,
          autoStartTimeoutMs: 12000,
        },
        prune: {
          idleHours: 24, // 0 disables idle pruning
          maxAgeDays: 7, // 0 disables max-age pruning
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

使用以下命令构建默认沙盒镜像一次：

```bash
scripts/sandbox-setup.sh
```

注意：沙盒容器默认使用 `network: "none"`；如果代理需要外部访问，请将 `agents.defaults.sandbox.docker.network`
设置为 `"bridge"`（或您自定义的网络）。

注意：传入的附件会被暂存到活动工作区的 `media/inbound/*`。使用 `workspaceAccess: "rw"`，这意味着文件会被写入代理工作区。

注意：`docker.binds` 挂载额外的主机目录；全局和每个代理的绑定会合并。

使用以下命令构建可选的浏览器镜像：

```bash
scripts/sandbox-browser-setup.sh
```

当 `agents.defaults.sandbox.browser.enabled=true`，浏览器工具使用一个沙盒化的
Chromium 实例（CDP）。如果启用了 noVNC（headless=false 时默认启用），
noVNC URL 会被注入到系统提示中，以便代理可以引用它。
这不需要在主配置中设置 `browser.enabled`；沙盒控制
URL 是按会话注入的。

`agents.defaults.sandbox.browser.allowHostControl`（默认：false）允许
沙盒化会话显式地通过浏览器工具 (`target: "host"`) 目标化 **主机** 浏览器控制服务器。
如果你想要严格的沙盒隔离，请勿启用此选项。

远程控制的白名单：

- `allowedControlUrls`：允许用于 `target: "custom"` 的精确控制 URL。
- `allowedControlHosts`：允许的主机名（仅主机名，不包括端口）。
- `allowedControlPorts`：允许的端口（默认：http=80, https=443）。
  默认：所有白名单均未设置（无限制）。`allowHostControl` 默认为 false。

### `models`（自定义提供商 + 基础 URL）

OpenClaw 使用 **pi-coding-agent** 模型目录。你可以通过编写
`~/.openclaw/agents/<agentId>/agent/models.json` 或在 OpenClaw 配置下的 `models.providers`
定义相同的架构来添加自定义提供商。
按提供商概述 + 示例：[/concepts/model-providers](/concepts/model-providers)。

当存在 `models.providers` 时，OpenClaw 在启动时将 `models.json` 写入/合并到
`~/.openclaw/agents/<agentId>/agent/`：

- 默认行为：**合并**（保留现有提供商，按名称覆盖）
- 设置 `models.mode: "replace"` 以覆盖文件内容

通过 `agents.defaults.model.primary`（提供商/模型）选择模型。

```json5
{
  agents: {
    defaults: {
      model: { primary: "custom-proxy/llama-3.1-8b" },
      models: {
        "custom-proxy/llama-3.1-8b": {},
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions",
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

### OpenCode Zen（多模型代理）

OpenCode Zen 是一个多模型网关，每个模型都有独立的端点。OpenClaw 使用
pi-ai 内置的 `opencode` 提供商；设置 `OPENCODE_API_KEY`（或
`OPENCODE_ZEN_API_KEY`）来自 [https://opencode.ai/auth](https://opencode.ai/auth)。

注意事项：

- 模型引用使用 `opencode/<modelId>`（示例：`opencode/claude-opus-4-6`）。
- 如果通过 `agents.defaults.models` 启用允许列表，请添加您计划使用的每个模型。
- 快捷方式：`openclaw onboard --auth-choice opencode-zen`。

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

### Z.AI (GLM-4.7) — 支持提供商别名

Z.AI 模型可通过内置的 `zai` 提供商获得。在您的环境中设置 `ZAI_API_KEY`
并通过 provider/model 引用模型。

快捷方式：`openclaw onboard --auth-choice zai-api-key`。

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

注意事项：

- 接受 `z.ai/*` 和 `z-ai/*` 作为别名，并标准化为 `zai/*`。
- 如果缺少 `ZAI_API_KEY`，对 `zai/*` 的请求将在运行时因认证错误而失败。
- 示例错误：`No API key found for provider "zai".`
- Z.AI 的通用 API 端点是 `https://api.z.ai/api/paas/v4`。GLM 编码
  请求使用专用的编码端点 `https://api.z.ai/api/coding/paas/v4`。
  内置的 `zai` 提供商使用编码端点。如果您需要通用
  端点，请在 `models.providers` 中定义一个自定义提供商并覆盖基础 URL
  （参见上面的自定义提供商部分）。
- 在文档/配置中使用虚假占位符；从不提交真实的 API 密钥。

### Moonshot AI (Kimi)

使用 Moonshot 的 OpenAI 兼容端点：

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

注意事项：

- 在环境中设置 `MOONSHOT_API_KEY` 或使用 `openclaw onboard --auth-choice moonshot-api-key`。
- 模型引用：`moonshot/kimi-k2.5`。
- 对于中国端点，可以：
  - 运行 `openclaw onboard --auth-choice moonshot-api-key-cn`（向导将设置 `https://api.moonshot.cn/v1`），或
  - 手动在 `models.providers.moonshot` 中设置 `baseUrl: "https://api.moonshot.cn/v1"`。

### Kimi Coding

使用 Moonshot AI 的 Kimi Coding 端点（Anthropic 兼容，内置提供商）：

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

注意事项：

- 在环境中设置 `KIMI_API_KEY` 或使用 `openclaw onboard --auth-choice kimi-code-api-key`。
- 模型引用：`kimi-coding/k2p5`。

### 合成（兼容Anthropic）

使用合成的兼容Anthropic端点：

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

注意事项：

- 设置 `SYNTHETIC_API_KEY` 或使用 `openclaw onboard --auth-choice synthetic-api-key`。
- 模型引用：`synthetic/hf:MiniMaxAI/MiniMax-M2.1`。
- 基础URL应省略 `/v1`，因为Anthropic客户端会附加它。

### 本地模型（LM Studio）—— 推荐设置

请参阅 [/gateway/local-models](/gateway/local-models) 获取当前的本地指南。简而言之：在严肃硬件上通过LM Studio Responses API运行MiniMax M2.1；保留托管模型以备回退。

### MiniMax M2.1

直接使用MiniMax M2.1而无需LM Studio：

```json5
{
  agent: {
    model: { primary: "minimax/MiniMax-M2.1" },
    models: {
      "anthropic/claude-opus-4-6": { alias: "Opus" },
      "minimax/MiniMax-M2.1": { alias: "Minimax" },
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
            // Pricing: update in models.json if you need exact cost tracking.
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

注意事项：

- 设置 `MINIMAX_API_KEY` 环境变量或使用 `openclaw onboard --auth-choice minimax-api`。
- 可用模型：`MiniMax-M2.1`（默认）。
- 如果需要精确的成本跟踪，请在 `models.json` 中更新定价。

### Cerebras (GLM 4.6 / 4.7)

通过其OpenAI兼容端点使用Cerebras：

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

注意事项：

- 使用 `cerebras/zai-glm-4.7` 用于 Cerebras；使用 `zai/glm-4.7` 用于 Z.AI 直连。
- 在环境中或配置中设置 `CEREBRAS_API_KEY`。

注意事项：

- 支持的 API: `openai-completions`, `openai-responses`, `anthropic-messages`,
  `google-generative-ai`
- 使用 `authHeader: true` + `headers` 以满足自定义认证需求。
- 如果希望将 `models.json` 存储在其他位置（默认：`~/.openclaw/agents/main/agent`），请使用 `OPENCLAW_AGENT_DIR`（或 `PI_CODING_AGENT_DIR`）覆盖代理配置根目录。

### `session`

控制会话范围、重置策略、重置触发器以及会话存储的写入位置。

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main",
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 60,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetTriggers: ["/new", "/reset"],
    // Default is already per-agent under ~/.openclaw/agents/<agentId>/sessions/sessions.json
    // You can override with {agentId} templating:
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    maintenance: {
      mode: "warn",
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
    },
    // Direct chats collapse to agent:<agentId>:<mainKey> (default: "main").
    mainKey: "main",
    agentToAgent: {
      // Max ping-pong reply turns between requester/target (0–5).
      maxPingPongTurns: 5,
    },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

字段：

- `mainKey`: direct-chat bucket key (默认: `"main"`)。当你想“重命名”主要DM线程而不更改`agentId`时很有用。
  - 沙盒说明: `agents.defaults.sandbox.mode: "non-main"` 使用此密钥检测主会话。任何与`mainKey`（群组/频道）不匹配的会话密钥都会被隔离。
- `dmScope`: 如何对DM会话进行分组（默认: `"main"`）。
  - `main`: 所有DM共享主会话以保持连续性。
  - `per-peer`: 根据发送者ID在频道之间隔离DM。
  - `per-channel-peer`: 按频道+发送者隔离DM（适用于多用户收件箱推荐）。
  - `per-account-channel-peer`: 按账户+频道+发送者隔离DM（适用于多账户收件箱推荐）。
  - 安全DM模式（推荐）：当多人可以向机器人发送DM（共享收件箱、多人白名单或`dmPolicy: "open"`）时设置`session.dmScope: "per-channel-peer"`。
- `identityLinks`: 将规范ID映射到带有提供程序前缀的对等体，以便在使用`per-peer`、`per-channel-peer`或`per-account-channel-peer`时，同一个人在不同频道中共享一个DM会话。
  - 示例: `alice: ["telegram:123456789", "discord:987654321012345678"]`。
- `reset`: 主重置策略。默认为网关主机本地时间每天凌晨4:00重置。
  - `mode`: `daily` 或 `idle`（当存在`reset`时默认为`daily`）。
  - `atHour`: 每日重置边界的本地小时（0-23）。
  - `idleMinutes`: 滑动空闲窗口（分钟）。当同时配置了每日和空闲时，先过期的生效。
- `resetByType`: 对于`direct`、`group`和`thread`的每个会话覆盖。接受旧版`dm`键作为`direct`的别名。
  - 如果仅设置了旧版`session.idleMinutes`而没有`reset`/`resetByType`，OpenClaw出于兼容性原因保持仅空闲模式。
- `heartbeatIdleMinutes`: 可选的心跳检查空闲覆盖（启用时仍适用每日重置）。
- `agentToAgent.maxPingPongTurns`: 请求者/目标之间的最大回复轮次（0–5，默认5）。
- `sendPolicy.default`: 当没有规则匹配时，`allow` 或 `deny` 回退。
- `sendPolicy.rules[]`: 按`channel`、`chatType` (`direct|group|room`) 或 `keyPrefix`（例如 `cron:`）匹配。首先拒绝获胜；否则允许。
- `maintenance`: 用于修剪、限制和轮换的会话存储维护设置。
  - `mode`: `"warn"`（默认）在不强制维护的情况下警告活动会话（尽力交付），`"enforce"` 应用修剪和轮换。
  - `pruneAfter`: 删除早于此持续时间的条目（例如 `"30m"`，`"1h"`，`"30d"`）。默认 "30d"。
  - `maxEntries`: 限制保留的会话条目数量（默认500）。
  - `rotateBytes`: 当超过此大小时轮换`sessions.json`（例如 `"10kb"`，`"1mb"`，`"10mb"`）。默认 "10mb"。

### `skills`（技能配置）

控制捆绑的白名单、安装偏好、额外技能文件夹以及每个技能的覆盖设置。适用于**捆绑**技能和`~/.openclaw/skills`（工作区技能在名称冲突时仍然优先）。

字段：

- `allowBundled`: 仅适用于**捆绑**技能的可选白名单。如果设置，则只有这些捆绑技能有资格（管理/工作区技能不受影响）。
- `load.extraDirs`: 额外的技能目录以扫描（优先级最低）。
- `install.preferBrew`: 当可用时优先使用brew安装程序（默认：true）。
- `install.nodeManager`: node安装程序偏好 (`npm` | `pnpm` | `yarn`, 默认：npm)。
- `entries.<skillKey>`: 每个技能的配置覆盖。

每个技能的字段：

- `enabled`: 设置`false`以禁用技能，即使它是捆绑/已安装的。
- `env`: 代理运行时注入的环境变量（仅当未设置时）。
- `apiKey`: 对于声明了主要环境变量的技能的可选便利设置（例如 `nano-banana-pro` → `GEMINI_API_KEY`）。

示例：

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills", "~/Projects/oss/some-skill-pack/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm",
    },
    entries: {
      "nano-banana-pro": {
        apiKey: "GEMINI_KEY_HERE",
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

### `plugins` (扩展)

控制插件发现、允许/拒绝以及每个插件的配置。插件从`~/.openclaw/extensions`，`<workspace>/.openclaw/extensions`加载，
以及任何`plugins.load.paths`条目。**配置更改需要网关重启。**
有关完整用法，请参阅[/plugin](/tools/plugin)。

字段：

- `enabled`: 插件加载的主开关（默认：true）。
- `allow`: 可选的插件ID白名单；如果设置，则只有列出的插件加载。
- `deny`: 可选的插件ID黑名单（拒绝优先）。
- `load.paths`: 额外的插件文件或目录以加载（绝对路径或`~`）。
- `entries.<pluginId>`: 每个插件的覆盖。
  - `enabled`: 设置`false`以禁用。
  - `config`: 插件特定的配置对象（如果提供则由插件验证）。

示例：

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    load: {
      paths: ["~/Projects/oss/voice-call-extension"],
    },
    entries: {
      "voice-call": {
        enabled: true,
        config: {
          provider: "twilio",
        },
      },
    },
  },
}
```

### `browser` (openclaw管理的浏览器)

OpenClaw可以启动一个**专用、隔离**的Chrome/Brave/Edge/Chromium实例用于openclaw，并暴露一个小的回环控制服务。
配置文件可以指向一个**远程**的基于Chromium的浏览器通过`profiles.<name>.cdpUrl`。远程
配置文件仅支持附加（启动/停止/重置被禁用）。

`browser.cdpUrl`保留在旧的单配置文件中，并作为仅设置了`cdpPort`的配置文件的基础
方案/主机。

默认值：

- enabled: `true`
- evaluateEnabled: `true` (设置 `false` 以禁用 `act:evaluate` 和 `wait --fn`)
- control service: 仅回环（端口从 `gateway.port` 派生，默认 `18791`）
- CDP URL: `http://127.0.0.1:18792` (control service + 1, 旧版单配置文件)
- profile color: `#FF4500` (龙虾橙色)
- 注意：控制服务器由正在运行的网关启动（OpenClaw.app 菜单栏，或 `openclaw gateway`）。
- 自动检测顺序：如果基于 Chromium，则为默认浏览器；否则 Chrome → Brave → Edge → Chromium → Chrome Canary。

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    // cdpUrl: "http://127.0.0.1:18792", // legacy single-profile override
    defaultProfile: "chrome",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    color: "#FF4500",
    // Advanced:
    // headless: false,
    // noSandbox: false,
    // executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    // attachOnly: false, // set true when tunneling a remote CDP to localhost
  },
}
```

### `ui` (外观)

原生应用程序用于用户界面框架的可选强调颜色（例如 Talk Mode 气泡色调）。

如果未设置，客户端将回退到柔和的浅蓝色。

```json5
{
  ui: {
    seamColor: "#FF4500", // hex (RRGGBB or #RRGGBB)
    // Optional: Control UI assistant identity override.
    // If unset, the Control UI uses the active agent identity (config or IDENTITY.md).
    assistant: {
      name: "OpenClaw",
      avatar: "CB", // emoji, short text, or image URL/data URI
    },
  },
}
```

### `gateway` (网关服务器模式 + 绑定)

使用 `gateway.mode` 明确声明此机器是否应运行网关。

默认值：

- mode: **unset**（视为“不自动启动”）
- bind: `loopback`
- port: `18789`（WS + HTTP 的单一端口）

```json5
{
  gateway: {
    mode: "local", // or "remote"
    port: 18789, // WS + HTTP multiplex
    bind: "loopback",
    // controlUi: { enabled: true, basePath: "/openclaw" }
    // auth: { mode: "token", token: "your-token" } // token gates WS + Control UI access
    // tailscale: { mode: "off" | "serve" | "funnel" }
  },
}
```

控制 UI 基础路径：

- `gateway.controlUi.basePath` 设置提供 Control UI 的 URL 前缀。
- 示例：`"/ui"`, `"/openclaw"`, `"/apps/openclaw"`。
- 默认：根 (`/`)（不变）。
- `gateway.controlUi.root` 设置 Control UI 资产的文件系统根目录（默认：`dist/control-ui`）。
- `gateway.controlUi.allowInsecureAuth` 允许在省略设备身份时仅使用令牌进行 Control UI 认证（通常通过 HTTP）。默认：`false`。建议使用 HTTPS（Tailscale Serve）或 `127.0.0.1`。
- `gateway.controlUi.dangerouslyDisableDeviceAuth` 禁用 Control UI 的设备身份检查（仅令牌/密码）。默认：`false`。仅限紧急情况。

相关文档：

- [控制UI](/web/control-ui)
- [Web概述](/web)
- [Tailscale](/gateway/tailscale)
- [远程访问](/gateway/remote)

受信任的代理：

- `gateway.trustedProxies`: 终止Gateway前面TLS的反向代理IP列表。
- 当连接来自这些IP之一时，OpenClaw使用`x-forwarded-for`（或`x-real-ip`）来确定客户端IP以进行本地配对检查和HTTP认证/本地检查。
- 仅列出您完全控制的代理，并确保它们**覆盖**传入的`x-forwarded-for`。

注意事项：

- `openclaw gateway`除非`gateway.mode`设置为`local`（或您传递了覆盖标志），否则拒绝启动。
- `gateway.port`控制用于WebSocket + HTTP（控制UI、钩子、A2UI）的单个复用端口。
- OpenAI Chat Completions端点：**默认禁用**；使用`gateway.http.endpoints.chatCompletions.enabled: true`启用。
- 优先级：`--port` > `OPENCLAW_GATEWAY_PORT` > `gateway.port` > 默认`18789`。
- 默认需要网关认证（令牌/密码或Tailscale Serve身份）。非回环绑定需要共享令牌/密码。
- 入门向导默认生成网关令牌（即使在回环上也是如此）。
- `gateway.remote.token`仅用于远程CLI调用；它不会启用本地网关认证。忽略`gateway.token`。

认证和Tailscale：

- `gateway.auth.mode`设置握手要求（`token`或`password`）。未设置时，假定使用令牌认证。
- `gateway.auth.token`存储令牌认证的共享令牌（同一台机器上的CLI使用）。
- 当设置了`gateway.auth.mode`时，仅接受该方法（加上可选的Tailscale标头）。
- `gateway.auth.password`可以在这里设置，或通过`OPENCLAW_GATEWAY_PASSWORD`（推荐）。
- `gateway.auth.allowTailscale`允许Tailscale Serve身份标头
  (`tailscale-user-login`)在请求到达回环时满足认证条件
  带有`x-forwarded-for`，`x-forwarded-proto`，和`x-forwarded-host`。OpenClaw
  在接受之前通过`tailscale whois`解析`x-forwarded-for`地址以验证身份。当`true`时，Serve请求不需要
  令牌/密码；设置`false`以要求显式凭据。当`tailscale.mode = "serve"`和认证模式不是`password`时，默认为
  `true`。
- `gateway.tailscale.mode: "serve"`使用Tailscale Serve（仅限尾网，回环绑定）。
- `gateway.tailscale.mode: "funnel"`公开仪表板；需要认证。
- `gateway.tailscale.resetOnExit`在关闭时重置Serve/Funnel配置。

远程客户端默认值（CLI）：

- `gateway.remote.url` 设置默认的Gateway WebSocket URL用于CLI调用，当 `gateway.mode = "remote"`。
- `gateway.remote.transport` 选择macOS远程传输方式 (`ssh` 默认, `direct` 用于ws/wss)。当 `direct`，`gateway.remote.url` 必须是 `ws://` 或 `wss://`。`ws://host` 默认端口为 `18789`。
- `gateway.remote.token` 提供远程调用的token（留空则不进行认证）。
- `gateway.remote.password` 提供远程调用的密码（留空则不进行认证）。

macOS应用行为：

- OpenClaw.app 监视 `~/.openclaw/openclaw.json` 并在 `gateway.mode` 或 `gateway.remote.url` 发生变化时实时切换模式。
- 如果 `gateway.mode` 未设置但 `gateway.remote.url` 已设置，macOS应用将其视为远程模式。
- 当你在macOS应用中更改连接模式时，它会将 `gateway.mode`（以及远程模式下的 `gateway.remote.url` + `gateway.remote.transport`）写回配置文件。

```json5
{
  gateway: {
    mode: "remote",
    remote: {
      url: "ws://gateway.tailnet:18789",
      token: "your-token",
      password: "your-password",
    },
  },
}
```

直接传输示例（macOS应用）：

```json5
{
  gateway: {
    mode: "remote",
    remote: {
      transport: "direct",
      url: "wss://gateway.example.ts.net",
      token: "your-token",
    },
  },
}
```

### `gateway.reload` (配置热重载)

Gateway监视 `~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）并自动应用更改。

模式：

- `hybrid`（默认）：热应用安全更改；对于关键更改，请重启Gateway。
- `hot`：仅应用热安全更改；记录需要重启时的情况。
- `restart`：对任何配置更改都重启Gateway。
- `off`：禁用热重载。

```json5
{
  gateway: {
    reload: {
      mode: "hybrid",
      debounceMs: 300,
    },
  },
}
```

#### 热重载矩阵（文件 + 影响）

监视的文件：

- `~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）

热应用（无需完全重启Gateway）：

- `hooks`（webhook认证/路径/映射）+ `hooks.gmail`（重启Gmail监视器）
- `browser`（重启浏览器控制服务器）
- `cron`（重启cron服务 + 更新并发性）
- `agents.defaults.heartbeat`（重启心跳运行器）
- `web`（重启WhatsApp Web通道）
- `telegram`，`discord`，`signal`，`imessage`（重启通道）
- `agent`，`models`，`routing`，`messages`，`session`，`whatsapp`，`logging`，`skills`，`ui`，`talk`，`identity`，`wizard`（动态读取）

需要完全重启Gateway：

- `gateway`（端口/绑定/认证/控制UI/tailscale）
- `bridge`（旧版）
- `discovery`
- `canvasHost`
- `plugins`
- 任何未知/不受支持的配置路径（出于安全考虑，默认为重启）

### 多实例隔离

在同一主机上运行多个Gateway（用于冗余或救援机器人），请隔离每个实例的状态 + 配置并使用唯一端口：

- `OPENCLAW_CONFIG_PATH`（每个实例的配置）
- `OPENCLAW_STATE_DIR`（会话/凭证）
- `agents.defaults.workspace`（记忆）
- `gateway.port`（每个实例唯一）

便利标志 (CLI):

- `openclaw --dev …` → 使用 `~/.openclaw-dev` + 将端口从基础 `19001` 偏移
- `openclaw --profile <name> …` → 使用 `~/.openclaw-<name>` (端口通过 config/env/flags 配置)

参见 [网关运行手册](/gateway) 获取派生的端口映射 (gateway/browser/canvas)。
参见 [多个网关](/gateway/multiple-gateways) 获取浏览器/CDP 端口隔离详情。

示例:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json \
OPENCLAW_STATE_DIR=~/.openclaw-a \
openclaw gateway --port 19001
```

### `hooks` (网关 Webhook)

在网关 HTTP 服务器上启用一个简单的 HTTP Webhook 终点。

默认值:

- enabled: `false`
- path: `/hooks`
- maxBodyBytes: `262144` (256 KB)

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
    presets: ["gmail"],
    transformsDir: "~/.openclaw/hooks",
    mappings: [
      {
        match: { path: "gmail" },
        action: "agent",
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

请求必须包含 hook token:

- `Authorization: Bearer <token>` **或**
- `x-openclaw-token: <token>`

端点:

- `POST /hooks/wake` → `{ text, mode?: "now"|"next-heartbeat" }`
- `POST /hooks/agent` → `{ message, name?, sessionKey?, wakeMode?, deliver?, channel?, to?, model?, thinking?, timeoutSeconds? }`
- `POST /hooks/<name>` → 通过 `hooks.mappings` 解析

`/hooks/agent` 总是将摘要发布到主会话（并且可以选择通过 `wakeMode: "now"` 触发立即的心跳）。

映射说明:

- `match.path` 匹配 `/hooks` 之后的子路径（例如 `/hooks/gmail` → `gmail`）。
- `match.source` 匹配负载字段（例如 `{ source: "gmail" }`），因此您可以使用通用的 `/hooks/ingest` 路径。
- 模板如 `{{messages[0].subject}}` 从负载中读取。
- `transform` 可以指向一个返回 hook 动作的 JS/TS 模块。
- `deliver: true` 将最终回复发送到一个通道；`channel` 默认为 `last`（回退到 WhatsApp）。
- 如果没有先前的交付路由，请显式设置 `channel` + `to`（对于 Telegram/Discord/Google Chat/Slack/Signal/iMessage/MS Teams 是必需的）。
- `model` 覆盖此 hook 运行的 LLM (`provider/model` 或别名；如果设置了 `agents.defaults.models`，则必须允许）。

Gmail 辅助配置（由 `openclaw webhooks gmail setup` / `run` 使用）:

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

      // Optional: use a cheaper model for Gmail hook processing
      // Falls back to agents.defaults.model.fallbacks, then primary, on auth/rate-limit/timeout
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      // Optional: default thinking level for Gmail hooks
      thinking: "off",
    },
  },
}
```

Gmail钩子的模型覆盖：

- `hooks.gmail.model` 指定用于Gmail钩子处理的模型（默认为会话主模型）。
- 接受来自 `agents.defaults.models` 的 `provider/model` 引用或别名。
- 在认证/速率限制/超时情况下，回退到 `agents.defaults.model.fallbacks`，然后是 `agents.defaults.model.primary`。
- 如果设置了 `agents.defaults.models`，则将钩子模型包含在允许列表中。
- 启动时，如果配置的模型不在模型目录或允许列表中，则发出警告。
- `hooks.gmail.thinking` 设置Gmail钩子的默认思考级别，并被每个钩子的 `thinking` 覆盖。

网关自动启动：

- 如果设置了 `hooks.enabled=true` 和 `hooks.gmail.account`，网关将在启动时启动 `gog gmail watch serve` 并自动续订监视。
- 设置 `OPENCLAW_SKIP_GMAIL_WATCHER=1` 以禁用自动启动（用于手动运行）。
- 避免在网关旁边运行单独的 `gog gmail watch serve`；它将
  失败并显示 `listen tcp 127.0.0.1:8788: bind: address already in use`。

注意：当 `tailscale.mode` 开启时，OpenClaw 默认将 `serve.path` 设置为 `/`，以便 Tailscale 可以正确代理 `/gmail-pubsub`（它会剥离设置的路径前缀）。
如果您需要后端接收带前缀的路径，请将 `hooks.gmail.tailscale.target` 设置为完整URL（并调整 `serve.path`）。

### `canvasHost`（LAN/tailnet Canvas文件服务器 + 实时重载）

网关通过HTTP提供一个HTML/CSS/JS目录，因此iOS/Android节点可以简单地 `canvas.navigate` 到它。

默认根目录：`~/.openclaw/workspace/canvas`  
默认端口：`18793`（选择此端口以避免openclaw浏览器CDP端口 `18792`）  
服务器监听 **网关绑定主机**（LAN或Tailnet），以便节点可以访问它。

服务器：

- 提供 `canvasHost.root` 下的文件
- 将一个小的实时重载客户端注入到提供的HTML中
- 监视目录并通过WebSocket端点 `/__openclaw__/ws` 广播重载
- 当目录为空时自动生成一个起始 `index.html`（这样您会立即看到一些内容）
- 还在 `/__openclaw__/a2ui/` 提供A2UI，并将其通告给节点作为 `canvasHostUrl`
  （节点始终用于Canvas/A2UI）

禁用实时重载（和文件监视），如果目录很大或者你遇到 `EMFILE`:

- config: `canvasHost: { liveReload: false }`

```json5
{
  canvasHost: {
    root: "~/.openclaw/workspace/canvas",
    port: 18793,
    liveReload: true,
  },
}
```

对 `canvasHost.*` 的更改需要网关重启（配置重新加载会重启）。

禁用方式：

- config: `canvasHost: { enabled: false }`
- env: `OPENCLAW_SKIP_CANVAS_HOST=1`

### `bridge` (旧版TCP桥接，已移除)

当前构建不再包含TCP桥接监听器；`bridge.*` 配置键被忽略。
节点通过网关WebSocket连接。此部分仅用于历史参考。

旧版行为：

- 网关可以为节点（iOS/Android）暴露一个简单的TCP桥接，通常在端口 `18790`。

默认值：

- enabled: `true`
- port: `18790`
- bind: `lan` (绑定到 `0.0.0.0`)

绑定模式：

- `lan`: `0.0.0.0` (可通过任何接口访问，包括LAN/Wi‑Fi和Tailscale)
- `tailnet`: 仅绑定到机器的Tailscale IP（推荐用于Vienna ⇄ London）
- `loopback`: `127.0.0.1` (仅本地)
- `auto`: 如果存在则优先使用tailnet IP，否则 `lan`

TLS：

- `bridge.tls.enabled`: 启用桥接连接的TLS（启用时仅支持TLS）。
- `bridge.tls.autoGenerate`: 当没有证书/密钥时生成自签名证书（默认：true）。
- `bridge.tls.certPath` / `bridge.tls.keyPath`: 桥接证书+私钥的PEM路径。
- `bridge.tls.caPath`: 可选的PEM CA包（自定义根或未来的mTLS）。

当启用TLS时，网关会在发现TXT记录中广播 `bridgeTls=1` 和 `bridgeTlsSha256`，以便节点可以固定证书。手动连接时如果没有存储指纹，则使用首次使用时的信任。
自动生成的证书需要 `openssl` 在PATH中；如果生成失败，桥接将不会启动。

```json5
{
  bridge: {
    enabled: true,
    port: 18790,
    bind: "tailnet",
    tls: {
      enabled: true,
      // Uses ~/.openclaw/bridge/tls/bridge-{cert,key}.pem when omitted.
      // certPath: "~/.openclaw/bridge/tls/bridge-cert.pem",
      // keyPath: "~/.openclaw/bridge/tls/bridge-key.pem"
    },
  },
}
```

### `discovery.mdns` (Bonjour / mDNS广播模式)

控制LAN mDNS发现广播 (`_openclaw-gw._tcp`)。

- `minimal` (默认): 从TXT记录中省略 `cliPath` + `sshPort`
- `full`: 在TXT记录中包含 `cliPath` + `sshPort`
- `off`: 完全禁用mDNS广播
- 主机名: 默认为 `openclaw` (广播 `openclaw.local`)。使用 `OPENCLAW_MDNS_HOSTNAME` 覆盖。

```json5
{
  discovery: { mdns: { mode: "minimal" } },
}
```

### `discovery.wideArea` (广域Bonjour / 单播DNS-SD)

启用时，网关使用配置的发现域（示例：`openclaw.internal.`）为 `_openclaw-gw._tcp` 在 `~/.openclaw/dns/` 下写入单播DNS-SD区域。

要使iOS/Android跨网络发现（Vienna ⇄ London），请与以下配合使用：

- 网关主机上的一个DNS服务器，用于服务您选择的域名（推荐使用CoreDNS）
- Tailscale **split DNS** 以便客户端通过网关DNS服务器解析该域名

一次性设置助手（网关主机）：

```bash
openclaw dns setup --apply
```

```json5
{
  discovery: { wideArea: { enabled: true } },
}
```

## 媒体模型模板变量

模板占位符在 `tools.media.*.models[].args` 和 `tools.media.models[].args` 中展开（以及任何未来的模板化参数字段）。

| 变量           | 描述                                                                     |
| ------------------ | ------------------------------------------------------------------------------- | -------- | ------- | ---------- | ----- | ------ | -------- | ------- | ------- | --- |
| `{{Body}}`         | 完整的入站消息正文                                                       |
| `{{RawBody}}`      | 原始入站消息正文（无历史/发件人包装；最适合命令解析） |
| `{{BodyStripped}}` | 剔除群组提及后的正文（最适合代理的默认值）                     |
| `{{From}}`         | 发件人标识符（WhatsApp为E.164；可能因渠道而异）                  |
| `{{To}}`           | 目标标识符                                                          |
| `{{MessageSid}}`   | 渠道消息ID（如有）                                             |
| `{{SessionId}}`    | 当前会话UUID                                                            |
| `{{IsNewSession}}` | `"true"` 当创建新会话时                                         |
| `{{MediaUrl}}`     | 入站媒体伪URL（如存在）                                           |
| `{{MediaPath}}`    | 本地媒体路径（如已下载）                                                |
| `{{MediaType}}`    | 媒体类型（图像/音频/文档/…）                                             |
| `{{Transcript}}`   | 音频转录（如启用）                                                 |
| `{{Prompt}}`       | 解析后的媒体提示符用于CLI条目                                           |
| `{{MaxChars}}`     | 解析后的CLI条目最大输出字符数                                       |
| `{{ChatType}}`     | `"direct"` 或 `"group"`                                                         |
| `{{GroupSubject}}` | 群组主题（尽力而为）                                                     |
| `{{GroupMembers}}` | 群组成员预览（尽力而为）                                             |
| `{{SenderName}}`   | 发件人显示名称（尽力而为）                                               |
| `{{SenderE164}}`   | 发件人电话号码（尽力而为）                                               |
| `{{Provider}}`     | 提供商提示（whatsapp                                                         | telegram | discord | googlechat | slack | signal | imessage | msteams | webchat | …)  |

## Cron (网关调度器)

Cron 是一个由网关拥有的调度器，用于唤醒和定时任务。有关功能概述和CLI示例，请参阅 [Cron 任务](/automation/cron-jobs)。

```json5
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 2,
    sessionRetention: "24h",
  },
}
```

字段：

- `sessionRetention`: 在修剪之前保留已完成的cron运行会话的时间长度。接受一个持续时间字符串，如 `"24h"` 或 `"7d"`。使用 `false` 禁用修剪。默认值为24h。

---

_接下来: [代理运行时](/concepts/agent)_ 🦞