---
summary: "Multi-agent routing: isolated agents, channel accounts, and bindings"
title: Multi-Agent Routing
read_when: "You want multiple isolated agents (workspaces + auth) in one gateway process."
status: active
---
# 多智能体路由

目标：多个 _隔离的_ 智能体（单独的工作区 + `agentDir` + 会话），以及一个运行中的网关中的多个渠道账户（例如两个WhatsApp）。入站消息通过绑定路由到智能体。

## 什么是“一个智能体”？

一个 **智能体** 是一个具有自己独立的：

- **工作区**（文件，AGENTS.md/SOUL.md/USER.md，本地笔记，角色规则）。
- **状态目录** (`agentDir`) 用于身份验证配置文件、模型注册表和每个智能体的配置。
- **会话存储** (`~/.openclaw/agents/<agentId>/sessions`) 下的聊天历史和路由状态。

身份验证配置文件是 **每个智能体** 的。每个智能体从自己的读取：

```text
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

主智能体的凭证 **不会** 自动共享。不要在智能体之间重用 `agentDir`
（会导致身份验证/会话冲突）。如果你想共享凭证，
将 `auth-profiles.json` 复制到另一个智能体的 `agentDir`。

技能是通过每个工作区的 `skills/` 文件夹按智能体划分的，共享技能可以从 `~/.openclaw/skills` 获取。参见 [技能：每个智能体与共享](/tools/skills#per-agent-vs-shared-skills)。

网关可以托管 **一个智能体**（默认）或并排托管 **多个智能体**。

**工作区说明：** 每个智能体的工作区是 **默认的当前工作目录**，而不是硬沙盒。相对路径在工作区内解析，但绝对路径可以到达其他主机位置，除非启用了沙盒。参见
[沙盒](/gateway/sandboxing)。

## 路径（快速映射）

- 配置: `~/.openclaw/openclaw.json` (或 `OPENCLAW_CONFIG_PATH`)
- 状态目录: `~/.openclaw` (或 `OPENCLAW_STATE_DIR`)
- 工作区: `~/.openclaw/workspace` (或 `~/.openclaw/workspace-<agentId>`)
- 智能体目录: `~/.openclaw/agents/<agentId>/agent` (或 `agents.list[].agentDir`)
- 会话: `~/.openclaw/agents/<agentId>/sessions`

### 单智能体模式（默认）

如果你什么都不做，OpenClaw 运行单个智能体：

- `agentId` 默认为 **`main`**。
- 会话以 `agent:main:<mainKey>` 为键。
- 工作区默认为 `~/.openclaw/workspace`（或 `~/.openclaw/workspace-<profile>` 当 `OPENCLAW_PROFILE` 设置时）。
- 状态默认为 `~/.openclaw/agents/main/agent`。

## 智能体助手

使用智能体向导添加新的隔离智能体：

```bash
openclaw agents add work
```

然后添加 `bindings`（或让向导完成）以路由入站消息。

验证：

```bash
openclaw agents list --bindings
```

## 快速开始

<Steps>
  <Step title="创建每个智能体的工作区">

使用向导或手动创建工作区：

```bash
openclaw agents add coding
openclaw agents add social
```

每个智能体获得自己的工作区，包含 `SOUL.md`，`AGENTS.md`，以及可选的 `USER.md`，加上专用的 `agentDir` 和会话存储在 `~/.openclaw/agents/<agentId>` 下。

  </Step>

  <Step title="创建渠道账户">

在你首选的渠道上为每个智能体创建一个账户：

- Discord: 每个代理一个机器人，启用Message Content Intent，复制每个token。
- Telegram: 每个代理通过BotFather创建一个机器人，复制每个token。
- WhatsApp: 每个账户链接一个电话号码。

```bash
openclaw channels login --channel whatsapp --account work
```

查看频道指南：[Discord](/channels/discord), [Telegram](/channels/telegram), [WhatsApp](/channels/whatsapp).

  </Step>

  <Step title="添加代理、账户和绑定">

在`agents.list`下添加代理，在`channels.<channel>.accounts`下添加频道账户，并使用`bindings`连接它们（示例见下文）。

  </Step>

  <Step title="重启并验证">

```bash
openclaw gateway restart
openclaw agents list --bindings
openclaw channels status --probe
```

  </Step>
</Steps>

## 多个代理 = 多个人，多个个性

使用**多个代理**时，每个`agentId`成为一个**完全隔离的人格**：

- **不同的电话号码/账户**（每个频道`accountId`）。
- **不同的个性**（每个代理的工作区文件如`AGENTS.md`和`SOUL.md`）。
- **独立的身份验证 + 会话**（除非显式启用，否则没有交叉通信）。

这使得**多个人**可以共享一个网关服务器，同时保持他们的AI“大脑”和数据隔离。

## 一个WhatsApp号码，多个人（DM拆分）

你可以在**一个WhatsApp账户**上路由**不同的WhatsApp DM**到不同的代理。根据发送者的E.164号码（如`+15551234567`）与`peer.kind: "direct"`匹配。回复仍然来自同一个WhatsApp号码（没有每个代理的发送者身份）。

重要细节：直接聊天会合并到代理的**主会话密钥**，因此真正的隔离需要**每人一个代理**。

示例：

```json5
{
  agents: {
    list: [
      { id: "alex", workspace: "~/.openclaw/workspace-alex" },
      { id: "mia", workspace: "~/.openclaw/workspace-mia" },
    ],
  },
  bindings: [
    {
      agentId: "alex",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551230001" } },
    },
    {
      agentId: "mia",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551230002" } },
    },
  ],
  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+15551230001", "+15551230002"],
    },
  },
}
```

注意：

- DM访问控制是**每个WhatsApp账户全局**（配对/白名单），而不是每个代理。
- 对于共享群组，将群组绑定到一个代理或使用[Broadcast groups](/channels/broadcast-groups)。

## 路由规则（消息如何选择代理）

绑定是**确定性的**且**最具体的规则优先**：

1. `peer` 匹配（精确的DM/群组/频道ID）
2. `parentPeer` 匹配（线程继承）
3. `guildId + roles`（Discord角色路由）
4. `guildId`（Discord）
5. `teamId`（Slack）
6. `accountId` 匹配一个频道
7. 频道级别匹配(`accountId: "*"`)
8. 回退到默认代理(`agents.list[].default`，否则列表中的第一个条目，默认：`main`)

如果同一层级中有多个绑定匹配，配置顺序中的第一个生效。
如果一个绑定设置了多个匹配字段（例如 `peer` + `guildId`)，则所有指定的字段都是必需的 (`AND` 语义)。

## 多个账户/电话号码

支持 **多个账户** 的渠道（例如 WhatsApp）使用 `accountId` 来识别
每个登录。每个 `accountId` 可以路由到不同的代理，因此一台服务器可以托管
多个电话号码而不会混淆会话。

## 概念

- `agentId`: 一个“大脑”（工作区，每个代理的身份验证，每个代理的会话存储）。
- `accountId`: 一个渠道账户实例（例如 WhatsApp 账户 `"personal"` 对比 `"biz"`）。
- `binding`: 根据 `(channel, accountId, peer)` 和可选的公会/团队 ID 将传入消息路由到一个 `agentId`。
- 直接聊天合并为 `agent:<agentId>:<mainKey>`（每个代理的“主”；`session.mainKey`）。

## 平台示例

### 每个代理的 Discord 机器人

每个 Discord 机器人账户映射到一个唯一的 `accountId`。将每个账户绑定到一个代理并为每个机器人保持白名单。

```json5
{
  agents: {
    list: [
      { id: "main", workspace: "~/.openclaw/workspace-main" },
      { id: "coding", workspace: "~/.openclaw/workspace-coding" },
    ],
  },
  bindings: [
    { agentId: "main", match: { channel: "discord", accountId: "default" } },
    { agentId: "coding", match: { channel: "discord", accountId: "coding" } },
  ],
  channels: {
    discord: {
      groupPolicy: "allowlist",
      accounts: {
        default: {
          token: "DISCORD_BOT_TOKEN_MAIN",
          guilds: {
            "123456789012345678": {
              channels: {
                "222222222222222222": { allow: true, requireMention: false },
              },
            },
          },
        },
        coding: {
          token: "DISCORD_BOT_TOKEN_CODING",
          guilds: {
            "123456789012345678": {
              channels: {
                "333333333333333333": { allow: true, requireMention: false },
              },
            },
          },
        },
      },
    },
  },
}
```

注意事项：

- 邀请每个机器人加入公会并启用消息内容意图。
- 令牌存储在 `channels.discord.accounts.<id>.token` 中（默认账户可以使用 `DISCORD_BOT_TOKEN`）。

### 每个代理的 Telegram 机器人

```json5
{
  agents: {
    list: [
      { id: "main", workspace: "~/.openclaw/workspace-main" },
      { id: "alerts", workspace: "~/.openclaw/workspace-alerts" },
    ],
  },
  bindings: [
    { agentId: "main", match: { channel: "telegram", accountId: "default" } },
    { agentId: "alerts", match: { channel: "telegram", accountId: "alerts" } },
  ],
  channels: {
    telegram: {
      accounts: {
        default: {
          botToken: "123456:ABC...",
          dmPolicy: "pairing",
        },
        alerts: {
          botToken: "987654:XYZ...",
          dmPolicy: "allowlist",
          allowFrom: ["tg:123456789"],
        },
      },
    },
  },
}
```

注意事项：

- 每个代理使用BotFather创建一个机器人并复制每个令牌。
- 令牌存储在 `channels.telegram.accounts.<id>.botToken` 中（默认账户可以使用 `TELEGRAM_BOT_TOKEN`）。

### 每个代理的WhatsApp号码

在启动网关之前链接每个账户：

```bash
openclaw channels login --channel whatsapp --account personal
openclaw channels login --channel whatsapp --account biz
```

`~/.openclaw/openclaw.json` (JSON5):

```js
{
  agents: {
    list: [
      {
        id: "home",
        default: true,
        name: "Home",
        workspace: "~/.openclaw/workspace-home",
        agentDir: "~/.openclaw/agents/home/agent",
      },
      {
        id: "work",
        name: "Work",
        workspace: "~/.openclaw/workspace-work",
        agentDir: "~/.openclaw/agents/work/agent",
      },
    ],
  },

  // Deterministic routing: first match wins (most-specific first).
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },

    // Optional per-peer override (example: send a specific group to work agent).
    {
      agentId: "work",
      match: {
        channel: "whatsapp",
        accountId: "personal",
        peer: { kind: "group", id: "1203630...@g.us" },
      },
    },
  ],

  // Off by default: agent-to-agent messaging must be explicitly enabled + allowlisted.
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },

  channels: {
    whatsapp: {
      accounts: {
        personal: {
          // Optional override. Default: ~/.openclaw/credentials/whatsapp/personal
          // authDir: "~/.openclaw/credentials/whatsapp/personal",
        },
        biz: {
          // Optional override. Default: ~/.openclaw/credentials/whatsapp/biz
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

## 示例：WhatsApp每日聊天 + Telegram深度工作

按渠道拆分：将WhatsApp路由到快速日常代理，将Telegram路由到Opus代理。

```json5
{
  agents: {
    list: [
      {
        id: "chat",
        name: "Everyday",
        workspace: "~/.openclaw/workspace-chat",
        model: "anthropic/claude-sonnet-4-5",
      },
      {
        id: "opus",
        name: "Deep Work",
        workspace: "~/.openclaw/workspace-opus",
        model: "anthropic/claude-opus-4-6",
      },
    ],
  },
  bindings: [
    { agentId: "chat", match: { channel: "whatsapp" } },
    { agentId: "opus", match: { channel: "telegram" } },
  ],
}
```

注意事项：

- 如果某个渠道有多个账户，请将 `accountId` 添加到绑定中（例如 `{ channel: "whatsapp", accountId: "personal" }`）。
- 要将单个DM/群组路由到Opus，同时保持其余部分在聊天中，请为该对等体添加一个 `match.peer` 绑定；对等体匹配总是会覆盖渠道范围的规则。

## 示例：同一渠道，一个对等体到Opus

保持WhatsApp在快速代理上，但将一个DM路由到Opus：

```json5
{
  agents: {
    list: [
      {
        id: "chat",
        name: "Everyday",
        workspace: "~/.openclaw/workspace-chat",
        model: "anthropic/claude-sonnet-4-5",
      },
      {
        id: "opus",
        name: "Deep Work",
        workspace: "~/.openclaw/workspace-opus",
        model: "anthropic/claude-opus-4-6",
      },
    ],
  },
  bindings: [
    {
      agentId: "opus",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551234567" } },
    },
    { agentId: "chat", match: { channel: "whatsapp" } },
  ],
}
```

对等绑定总是优先，因此将其置于频道范围规则之上。

## 绑定到WhatsApp群组的家庭代理

将专用家庭代理绑定到单个WhatsApp群组，并使用提及门控和更严格的工具策略：

```json5
{
  agents: {
    list: [
      {
        id: "family",
        name: "Family",
        workspace: "~/.openclaw/workspace-family",
        identity: { name: "Family Bot" },
        groupChat: {
          mentionPatterns: ["@family", "@familybot", "@Family Bot"],
        },
        sandbox: {
          mode: "all",
          scope: "agent",
        },
        tools: {
          allow: [
            "exec",
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          deny: ["write", "edit", "apply_patch", "browser", "canvas", "nodes", "cron"],
        },
      },
    ],
  },
  bindings: [
    {
      agentId: "family",
      match: {
        channel: "whatsapp",
        peer: { kind: "group", id: "120363999999999999@g.us" },
      },
    },
  ],
}
```

注意事项：

- 工具允许/拒绝列表是**工具**，不是技能。如果技能需要运行二进制文件，请确保`exec`被允许且二进制文件存在于沙箱中。
- 对于更严格的门控，请设置`agents.list[].groupChat.mentionPatterns`并保持
  频道的群组白名单启用。

## 每代理沙箱和工具配置

从v2026.1.6开始，每个代理可以有自己的沙箱和工具限制：

```js
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: {
          mode: "off",  // No sandbox for personal agent
        },
        // No tool restrictions - all tools available
      },
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: {
          mode: "all",     // Always sandboxed
          scope: "agent",  // One container per agent
          docker: {
            // Optional one-time setup after container creation
            setupCommand: "apt-get update && apt-get install -y git curl",
          },
        },
        tools: {
          allow: ["read"],                    // Only read tool
          deny: ["exec", "write", "edit", "apply_patch"],    // Deny others
        },
      },
    ],
  },
}
```

注意：`setupCommand` 位于 `sandbox.docker` 下，并在容器创建时运行一次。
每个代理的 `sandbox.docker.*` 覆盖在解析范围为 `"shared"` 时被忽略。

**优点：**

- **安全隔离**：限制不受信任代理使用的工具
- **资源控制**：对特定代理进行沙箱处理，同时将其他代理保留在主机上
- **灵活的策略**：每个代理不同的权限

注意：`tools.elevated` 是 **全局** 的且基于发送者；它不能按代理进行配置。
如果需要按代理的边界，请使用 `agents.list[].tools` 拒绝 `exec`。
对于组目标，请使用 `agents.list[].groupChat.mentionPatterns` 以便 @提及能够干净地映射到预期的代理。

参见 [Multi-Agent Sandbox & Tools](/tools/multi-agent-sandbox-tools) 获取详细示例。