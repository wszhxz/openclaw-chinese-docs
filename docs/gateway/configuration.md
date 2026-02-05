---
summary: "All configuration options for ~/.openclaw/openclaw.json with examples"
read_when:
  - Adding or modifying config fields
title: "Configuration"
---
# 配置 🔧

OpenClaw 从 `~/.openclaw/openclaw.json` 读取一个可选的 **JSON5** 配置文件（允许注释和尾随逗号）。

如果文件缺失，OpenClaw 使用相对安全的默认设置（嵌入式 Pi 代理 + 按发送者会话 + 工作区 `~/.openclaw/workspace`）。您通常只需要配置来：

- 限制谁可以触发机器人 (`channels.whatsapp.allowFrom`, `channels.telegram.allowFrom` 等)
- 控制群组白名单 + 提及行为 (`channels.whatsapp.groups`, `channels.telegram.groups`, `channels.discord.guilds`, `agents.list[].groupChat`)
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
- 运行 `openclaw doctor --fix` (或 `--yes`) 应用迁移/修复。

Doctor 除非您明确选择 `--fix`/`--yes`，否则不会写入更改。

## 架构 + UI 提示

网关通过 `config.schema` 暴露配置的 JSON Schema 表示，供 UI 编辑器使用。
控制 UI 根据此架构渲染表单，并提供 **原始 JSON** 编辑器作为逃生舱。

通道插件和扩展可以注册其配置的架构 + UI 提示，因此通道设置
在应用程序之间保持架构驱动，而无需硬编码表单。

提示（标签、分组、敏感字段）与架构一起发布，以便客户端可以渲染
更好的表单而无需硬编码配置知识。

## 应用 + 重启 (RPC)

使用 `config.apply` 验证 + 写入完整配置并一步重启网关。
它写入一个重启哨兵并在网关启动后向最后活动的会话发送唤醒 ping。

警告：`config.apply` 替换 **整个配置**。如果您只想更改一些键，
使用 `config.patch` 或 `openclaw config set`。备份 `~/.openclaw/openclaw.json`。

参数：

- `raw` (字符串) — 整个配置的 JSON5 有效负载
- `baseHash` (可选) — 来自 `config.get` 的配置哈希（当已存在配置时必需）
- `sessionKey` (可选) — 唤醒 ping 的最后活动会话密钥
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

使用 `config.patch` 将部分更新合并到现有配置中而不覆盖
无关的键。它应用 JSON 合并补丁语义：

- 对象递归合并
- `null` 删除一个键
- 数组替换
  类似于 `config.apply`，它验证、写入配置、存储重启哨兵，并安排
  网关重启（当提供 `sessionKey` 时唤醒）。

参数：

- `raw` (字符串) — 仅包含要更改的键的 JSON5 有效负载
- `baseHash` (必需) — 来自 `config.get` 的配置哈希
- `sessionKey` (可选) — 唤醒 ping 的最后活动会话密钥
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

## 自我聊天模式（推荐用于群组控制）

防止机器人响应群组中的 WhatsApp @提及（仅响应特定文本触发器）：

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

- **单个文件**：替换包含 `$include` 的对象
- **文件数组**：按顺序深度合并文件（后面的文件覆盖前面的文件）
- **具有同级键**：包含后合并同级键（覆盖包含的值）
- **同级键 + 数组/原语**：不支持（包含的内容必须是对象）

```json5
// Sibling keys override included values
{
  $include: "./base.json5", // { a: 1, b: 2 }
  b: 99, // Result: { a: 1, b: 99 }
}
```

### 嵌套包含

包含的文件本身可以包含 `$include` 指令（最多 10 层深）：

```json5
// clients/mueller.json5
{
  agents: { $include: "./mueller/agents.json5" },
  broadcast: { $include: "./mueller/broadcast.json5" },
}
```

### 路径解析

- **相对路径**：相对于包含文件进行解析
- **绝对路径**：按原样使用
- **父目录**：`../` 引用按预期工作

```json5
{ "$include": "./sub/config.json5" }      // relative
{ "$include": "/etc/openclaw/base.json5" } // absolute
{ "$include": "../shared/common.json5" }   // parent dir
```

### 错误处理

- **缺少文件**：带有解析路径的清晰错误
- **解析错误**：显示哪个包含文件失败
- **循环包含**：检测并报告包含链

### 示例：多客户端法律设置

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

OpenClaw 从父进程（shell、launchd/systemd、CI 等）读取环境变量。

此外，它加载：

- 当前工作目录中的 `.env`（如果存在）
- 全局回退 `.env` 从 `~/.openclaw/.env`（即 `$OPENCLAW_STATE_DIR/.env`）

两个 `.env` 文件都不会覆盖现有的环境变量。

您还可以在配置中提供内联环境变量。这些仅在
进程环境缺少该键时应用（相同的非覆盖规则）：

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

参见 [/environment](/environment) 获取完整的优先级和来源。

### `env.shellEnv` (可选)

便利性选择：如果启用且尚未设置任何预期的键，OpenClaw 运行您的登录 shell 并仅导入缺失的预期键（从不覆盖）。
这实际上引用了您的 shell 配置文件。

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

您可以在任何配置字符串值中直接引用环境变量，使用
`${VAR_NAME}` 语法。变量在配置加载时进行替换，在验证之前。

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

- 仅匹配大写的环境变量名：`[A-Z_][A-Z0-9_]*`
- 缺少或空的环境变量在配置加载时抛出错误
- 使用 `$${VAR}` 输出字面量 `${VAR}`
- 与 `$include` 一起工作（包含的文件也会进行替换）

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

OpenClaw 将 **每个代理** 的认证配置文件（OAuth + API 密钥）存储在：

- `<agentDir>/auth-profiles.json`（默认：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`）

另请参见：[/concepts/oauth](/concepts/oauth)

旧版 OAuth 导入：

- `~/.openclaw/credentials/oauth.json`（或 `$OPENCLAW_STATE_DIR/credentials/oauth.json`）

嵌入式 Pi 代理在以下位置维护运行时缓存：

- `<agentDir>/auth.json`（自动管理；勿手动编辑）

旧版代理目录（多代理之前）：

- `~/.openclaw/agent/*`（由 `openclaw doctor` 迁移到 `~/.openclaw/agents/<defaultAgentId>/agent/*`）

覆盖：

- OAuth 目录（仅限旧版导入）：`OPENCLAW_OAUTH_DIR`
- 代理目录（默认代理根目录覆盖）：`OPENCLAW_AGENT_DIR`（首选），`PI_CODING_AGENT_DIR`（旧版）

首次使用时，OpenClaw 将 `oauth.json` 条目导入到 `auth-profiles.json`。

### `auth`

认证配置文件的可选元数据。这 **不** 存储机密信息；它将
配置文件 ID 映射到提供商 + 模式（以及可选电子邮件），并定义用于故障转移的提供商轮换顺序。

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

每个代理的可选身份，用于默认值和用户体验。这是由 macOS 入门助手编写的。

如果设置，OpenClaw 会派生默认值（仅当您未显式设置时）：

- `messages.ackReaction` 从 **活动代理** 的 `identity.emoji`（回退到 👀）
- `agents.list[].groupChat.mentionPatterns` 从代理的 `identity.name`/`identity.emoji`（因此“@Samantha”在 Telegram/Slack/Discord/Google Chat/iMessage/WhatsApp 群组中都有效）
- `identity.avatar` 接受工作区相对图像路径或远程 URL/data URL。本地文件必须位于代理工作区内部。

`identity.avatar` 接受：

- 工作区相对路径（必须保留在代理工作区内）
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

由 CLI 向导 (`onboard`, `configure`, `doctor`) 编写的元数据。

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

- 默认日志文件：`/tmp/openclaw/openclaw-YYYY-MM-DD.log`
- 如果需要稳定路径，请将 `logging.file` 设置为 `/tmp/openclaw/openclaw.log`。
- 控制台输出可以通过以下方式单独调整：
  - `logging.consoleLevel`（默认为 `info`，当 `--verbose` 时提升到 `debug`）
  - `logging.consoleStyle` (`pretty` | `compact` | `json`)
- 工具摘要可以被红acted 以避免泄露机密信息：
  - `logging.redactSensitive` (`off` | `tools`，默认：`tools`)
  - `logging.redactPatterns` (正则表达式字符串数组；覆盖默认值)

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

控制 WhatsApp 直接聊天（DM）的处理方式：

- `"pairing"`（默认）：未知发送者收到配对码；所有者必须批准
- `"allowlist"`：仅允许 `channels.whatsapp.allowFrom` 中的发送者（或配对允许存储）
- `"open"`：允许所有传入的 DM（**需要** `channels.whatsapp.allowFrom` 包含 `"*"`）
- `"disabled"`：忽略所有传入的 DM

配对码在 1 小时后过期；只有在创建新请求时，机器人才会发送配对码。待处理的 DM 配对请求默认每个通道最多 **3 个**。

配对批准：

- `openclaw pairing list whatsapp`
- `openclaw pairing approve whatsapp <code>`

### `channels.whatsapp.allowFrom`

允许触发 WhatsApp 自动回复（**仅限 DM**）的 E.164 电话号码白名单。
如果为空且 `channels.whatsapp.dmPolicy="pairing"`，未知发送者将收到配对码。
对于群组，使用 `channels.whatsapp.groupPolicy` + `channels.whatsapp.groupAllowFrom`。

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

控制传入的 WhatsApp 消息是否标记为已读（蓝色勾号）。默认：`true`。

自我聊天模式始终跳过已读回执，即使已启用。

按账户重写：`channels.whatsapp.accounts.<id>.sendReadReceipts`。

```json5
{
  channels: {
    whatsapp: { sendReadReceipts: false },
  },
}
```

### `channels.whatsapp.accounts` (多账户)

在一个网关中运行多个 WhatsApp 账户：

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

注意：

- 如果存在，出站命令默认使用账户 `default`；否则使用第一个配置的账户 ID（按排序）。
- 旧版单账户 Baileys 认证目录由 `openclaw doctor` 迁移到 `whatsapp/default`。

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

注意：

- 当省略 `default` 时使用（CLI + 路由）。
- 环境令牌仅适用于 **默认** 账户。
- 基本通道设置（群组策略、提及门控等）适用于所有账户，除非按账户重写。
- 使用 `bindings[].match.accountId` 将每个账户路由到不同的 agents.defaults。

### 群聊提及门控 (`agents.list[].groupChat` + `messages.groupChat`)

群组消息默认为 **需要提及**（元数据提及或正则表达式模式）。适用于 WhatsApp、Telegram、Discord、Google Chat 和 iMessage 群组聊天。

**提及类型：**

- **元数据提及**：平台原生的 @-提及（例如，WhatsApp 点击提及）。在 WhatsApp 自我聊天模式下忽略（参见 `channels.whatsapp.allowFrom`）。
- **文本模式**：在 `agents.list[].groupChat.mentionPatterns` 中定义的正则表达式模式。始终检查，无论是否处于自我聊天模式。
- 仅在提及检测可能时强制执行提及门控（原生提及或至少一个 `mentionPattern`）。

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

`messages.groupChat.historyLimit` 设置群组历史上下文的全局默认值。通道可以使用 `channels.<channel>.historyLimit` 覆盖（或 `channels.<channel>.accounts.*.historyLimit` 用于多账户）。设置 `0` 禁用历史包装。

#### DM 历史限制

DM 对话使用由代理管理的基于会话的历史记录。您可以限制每个 DM 会话保留的用户回合数：

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

1. 每个 DM 覆盖：`channels.<provider>.dms[userId].historyLimit`
2. 提供程序默认：`channels.<provider>.dmHistoryLimit`
3. 无限制（保留所有历史记录）

支持的提供程序：`telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`。

每个代理覆盖（设置时优先，甚至 `[]`）：

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

提及门控默认值按通道存储 (`channels.whatsapp.groups`, `channels.telegram.groups`, `channels.imessage.groups`, `channels.discord.guilds`)。当 `*.groups` 设置时，它还充当群组白名单；包括 `"*"` 以允许所有群组。

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

### 群组策略（按通道）

使用 `channels.*.groupPolicy` 控制是否接受群组/房间消息：

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

注意：

- `"open"`：群组绕过白名单；仍然应用提及门控。
- `"disabled"`：阻止所有群组/房间消息。
- `"allowlist"`：仅允许与配置的白名单