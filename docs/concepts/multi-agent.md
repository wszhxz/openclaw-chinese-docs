---
summary: "Multi-agent routing: isolated agents, channel accounts, and bindings"
title: Multi-Agent Routing
read_when: "You want multiple isolated agents (workspaces + auth) in one gateway process."
status: active
---
# 多智能体路由

目标：多个 _隔离的_ 智能体（独立的工作区 + `agentDir` + 会话），以及在一个运行的网关中拥有多个渠道账户（例如两个 WhatsApp）。入站消息通过绑定规则路由到智能体。

## 什么是“一个智能体”？

一个 **智能体** 是一个具有完整范围的思维大脑，拥有自己的：

- **工作区**（文件、AGENTS.md/SOUL.md/USER.md、本地笔记、人格规则）。
- **状态目录** (`agentDir`) 用于认证配置文件、模型注册表和每个智能体的配置。
- **会话存储**（聊天历史 + 路由状态）位于 `~/.openclaw/agents/<agentId>/sessions` 下。

认证配置文件是 **每个智能体独立的**。每个智能体读取其自己的：

```text
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

主智能体凭证 **不** 自动共享。切勿在智能体之间重复使用 `agentDir`（这会导致认证/会话冲突）。如果您想共享凭证，请将 `auth-profiles.json` 复制到另一个智能体的 `agentDir` 中。

技能是每个智能体独立的，通过每个工作区的 `skills/` 文件夹，共享技能可从 `~/.openclaw/skills` 获取。参见 [技能：每个智能体与共享](/tools/skills#per-agent-vs-shared-skills)。

网关可以托管 **一个智能体**（默认）或 **多个智能体** 并排运行。

**工作区注意：** 每个智能体的工作区是 **默认当前工作目录**，而不是硬沙箱。相对路径在工作区内解析，但除非启用沙箱，否则绝对路径可能访问其他主机位置。参见 [沙箱化](/gateway/sandboxing)。

## 路径（快速映射）

- 配置：`~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）
- 状态目录：`~/.openclaw`（或 `OPENCLAW_STATE_DIR`）
- 工作区：`~/.openclaw/workspace`（或 `~/.openclaw/workspace-<agentId>`）
- 智能体目录：`~/.openclaw/agents/<agentId>/agent`（或 `agents.list[].agentDir`）
- 会话：`~/.openclaw/agents/<agentId>/sessions`

### 单智能体模式（默认）

如果您什么都不做，OpenClaw 将运行一个智能体：

- `agentId` 默认为 **`main`**。
- 会话键为 `agent:main:<mainKey>`。
- 工作区默认为 `~/.openclaw/workspace`（当设置 `OPENCLAW_PROFILE` 时为 `~/.openclaw/workspace-<profile>`）。
- 状态默认为 `~/.openclaw/agents/main/agent`。

## 智能体助手

使用智能体向导添加一个新的隔离智能体：

```bash
openclaw agents add work
```

然后添加 `bindings`（或让向导完成）以路由入站消息。

验证命令：

```bash
openclaw agents list --bindings
```

## 快速开始

<Steps>
  <Step title="Create each agent workspace">

Use the wizard or create workspaces manually:

__CODE_BLOCK_28__

Each agent gets its own workspace with __CODE_BLOCK_29__, __CODE_BLOCK_30__, and optional __CODE_BLOCK_31__, plus a dedicated __CODE_BLOCK_32__ and session store under __CODE_BLOCK_33__.

  </Step>

  <Step title="Create channel accounts">

Create one account per agent on your preferred channels:

- Discord: one bot per agent, enable Message Content Intent, copy each token.
- Telegram: one bot per agent via BotFather, copy each token.
- WhatsApp: link each phone number per account.

__CODE_BLOCK_34__

See channel guides: [Discord](/channels/discord), [Telegram](/channels/telegram), [WhatsApp](/channels/whatsapp).

  </Step>

  <Step title="Add agents, accounts, and bindings">

Add agents under __CODE_BLOCK_35__, channel accounts under __CODE_BLOCK_36__, and connect them with __CODE_BLOCK_37__ (examples below).

  </Step>

  <Step title="Restart and verify">

__CODE_BLOCK_38__

  </Step>
</Steps>

## 多个智能体 = 多人，多重人格

使用 **多个智能体** 时，每个 `agentId` 都成为一个 **完全隔离的人格**：

- **不同的电话号码/账户**（每个渠道 `accountId`）。
- **不同的人格**（每个智能体的工作区文件，如 `AGENTS.md` 和 `SOUL.md`）。
- **独立的认证 + 会话**（除非明确启用，否则无交叉通信）。

这使得 **多人** 可以共享一个网关服务器，同时保持他们的 AI“大脑”和数据隔离。

## 一个 WhatsApp 号码，多人（私聊分离）

您可以将 **不同的 WhatsApp 私聊** 路由到不同的智能体，同时保持在 **一个 WhatsApp 账户** 上。匹配发送者 E.164（如 `+15551234567`），使用 `peer.kind: "direct"`。回复仍然来自同一个 WhatsApp 号码（没有每个智能体的发送者身份）。

重要细节：直接聊天会合并到智能体的 **主会话键**，因此真正的隔离需要 **每人一个智能体**。

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

- DM 访问控制是 **每个 WhatsApp 账户全局的**（配对/白名单），而不是每个智能体。
- 对于共享群组，将群组绑定到一个智能体或使用 [广播群组](/channels/broadcast-groups)。

## 路由规则（消息如何选择智能体）

绑定规则是 **确定性的** 且 **最具体者优先**：

1. `peer` 匹配（精确的 DM/群组/渠道 ID）
2. `parentPeer` 匹配（线程继承）
3. `guildId + roles`（Discord 角色路由）
4. `guildId`（Discord）
5. `teamId`（Slack）
6. 针对渠道的 `accountId` 匹配
7. 渠道级别匹配 (`accountId: "*"`)
8. 回退到默认智能体 (`agents.list[].default`，否则列表第一项，默认：`main`)

如果同一层级的多个绑定匹配，配置顺序中的第一个获胜。
如果一个绑定设置了多个匹配字段（例如 `peer` + `guildId`），则所有指定字段都是必需的 (`AND` 语义)。

重要的账户范围细节：

- 省略 `accountId` 的绑定仅匹配默认账户。
- 使用 `accountId: "*"` 作为所有账户的渠道级回退。
- 如果您稍后为同一智能体添加了带有显式账户 ID 的相同绑定，OpenClaw 会将现有的仅限渠道的绑定升级为账户范围，而不是复制它。

## 多个账户 / 电话号码

支持 **多个账户** 的渠道（例如 WhatsApp）使用 `accountId` 来标识每次登录。每个 `accountId` 可以路由到不同的智能体，因此一台服务器可以托管多个电话号码而不会混合会话。

如果您希望在省略 `accountId` 时有一个渠道级默认账户，请设置 `channels.<channel>.defaultAccount`（可选）。当未设置时，OpenClaw 如果存在则回退到 `default`，否则为第一个配置的账户 ID（排序后）。

支持此模式的常见渠道包括：

- `whatsapp`, `telegram`, `discord`, `slack`, `signal`, `imessage`
- `irc`, `line`, `googlechat`, `mattermost`, `matrix`, `nextcloud-talk`
- `bluebubbles`, `zalo`, `zalouser`, `nostr`, `feishu`

## 概念

- `agentId`：一个“大脑”（工作区、每个智能体的认证、每个智能体的会话存储）。
- `accountId`：一个渠道账户实例（例如 WhatsApp 账户 `"personal"` 对比 `"biz"`）。
- `binding`：根据 `(channel, accountId, peer)` 将入站消息路由到 `agentId`，并可选择性地根据 guild/team ID。
- 直接聊天合并到 `agent:<agentId>:<mainKey>`（每个智能体的“主”；`session.mainKey`）。

## 平台示例

### 每个智能体的 Discord 机器人

每个 Discord 机器人账户映射到唯一的 `accountId`。将每个账户绑定到一个智能体，并为每个机器人维护白名单。

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

注意：

- 邀请每个机器人加入服务器并启用消息内容意图。
- 令牌存储在 `channels.discord.accounts.<id>.token`（默认账户可以使用 `DISCORD_BOT_TOKEN`）。

### 每个智能体的 Telegram 机器人

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

注意：

- 使用 BotFather 为每个智能体创建一个机器人并复制每个令牌。
- 令牌存储在 `channels.telegram.accounts.<id>.botToken`（默认账户可以使用 `TELEGRAM_BOT_TOKEN`）。

### 每个智能体的 WhatsApp 号码

启动网关之前链接每个账户：

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

## 示例：WhatsApp 日常聊天 + Telegram 深度工作

按 channel 拆分：将 WhatsApp 路由到快速日常 agent，将 Telegram 路由到 Opus agent。

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

注意：

- 如果一个 channel 有多个 accounts，在 binding 中添加 `accountId`（例如 `{ channel: "whatsapp", accountId: "personal" }`）。
- 要将单个 DM/group 路由到 Opus 同时保持其余在 chat 上，为该 peer 添加一个 `match.peer` binding；peer 匹配总是优于 channel-wide 规则。

## 示例：同一 channel，一个 peer 到 Opus

保持 WhatsApp 在快速 agent 上，但将一个 DM 路由到 Opus：

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

Peer bindings 总是胜出，所以将它们保持在 channel-wide 规则之上。

## 绑定到 WhatsApp group 的 Family agent

将专用的 family agent 绑定到单个 WhatsApp group，带有 mention gating
和更严格的 tool policy：

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

注意：

- Tool allow/deny lists 是 **tools**，不是 skills。如果一个 skill 需要运行
  binary，确保 `exec` 被允许且 binary 存在于 sandbox 中。
- 对于更严格的 gating，设置 `agents.list[].groupChat.mentionPatterns` 并保持
  channel 的 group allowlists 启用。

## Per-Agent Sandbox 和 Tool 配置

从 v2026.1.6 开始，每个 agent 可以拥有自己的 sandbox 和 tool 限制：

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

注意：`setupCommand` 位于 `sandbox.docker` 下，并在 container 创建时运行一次。
当 resolved scope 为 `"shared"` 时，Per-agent `sandbox.docker.*`  overrides 被忽略。

**优势**：

- **安全隔离**：为不可信的 agents 限制 tools
- **资源控制**：Sandbox 特定 agents 同时保持 others 在 host 上
- **灵活策略**：每个 agent 不同的 permissions

注意：`tools.elevated` 是 **global** 且基于 sender 的；它不可 per agent 配置。
如果你需要 per-agent 边界，使用 `agents.list[].tools` 来 deny `exec`。
对于 group targeting，使用 `agents.list[].groupChat.mentionPatterns` 以便 @mentions 清晰映射到预期的 agent。

参见 [Multi-Agent Sandbox & Tools](/tools/multi-agent-sandbox-tools) 获取详细示例。