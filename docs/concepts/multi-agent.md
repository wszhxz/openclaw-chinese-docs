---
summary: "Multi-agent routing: isolated agents, channel accounts, and bindings"
title: Multi-Agent Routing
read_when: "You want multiple isolated agents (workspaces + auth) in one gateway process."
status: active
---
# 多智能体路由

目标：在单个运行中的网关（Gateway）中支持多个_隔离的_智能体（各自拥有独立的工作区 + `agentDir` + 会话），以及多个渠道账号（例如两个 WhatsApp 账号）。入站消息通过绑定规则路由至指定智能体。

## 什么是“一个智能体”？

一个**智能体**是一个完全作用域隔离的“大脑”，拥有其自身的：

- **工作区**（文件、AGENTS.md/SOUL.md/USER.md、本地笔记、角色规则）。
- **状态目录**（`agentDir`），用于存放认证配置文件、模型注册表及每个智能体的专属配置。
- **会话存储**（聊天历史记录 + 路由状态），位于 `~/.openclaw/agents/<agentId>/sessions` 下。

认证配置文件是**按智能体划分的**。每个智能体仅读取其自身的：

```text
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

主智能体的凭据**不会**自动共享。切勿在不同智能体之间复用 `agentDir`（否则将导致认证/会话冲突）。如需共享凭据，请将 `auth-profiles.json` 复制到其他智能体的 `agentDir` 中。

技能按智能体划分，由各工作区下的 `skills/` 文件夹管理；共享技能则统一存放在 `~/.openclaw/skills` 中。详见 [技能：按智能体 vs 共享](/tools/skills#per-agent-vs-shared-skills)。

网关可托管**一个智能体**（默认）或**多个智能体**并行运行。

**工作区说明**：每个智能体的工作区是其**默认当前工作目录（cwd）**，而非强制沙箱。相对路径在工作区内解析，但绝对路径仍可访问主机上的其他位置——除非启用了沙箱机制。参见 [沙箱机制](/gateway/sandboxing)。

## 路径速查表

- 配置文件：`~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）
- 状态目录：`~/.openclaw`（或 `OPENCLAW_STATE_DIR`）
- 工作区：`~/.openclaw/workspace`（或 `~/.openclaw/workspace-<agentId>`）
- 智能体目录：`~/.openclaw/agents/<agentId>/agent`（或 `agents.list[].agentDir`）
- 会话：`~/.openclaw/agents/<agentId>/sessions`

### 单智能体模式（默认）

若不做任何配置，OpenClaw 将以单智能体模式运行：

- `agentId` 默认为 **`main`**。
- 会话键名为 `agent:main:<mainKey>`。
- 工作区默认为 `~/.openclaw/workspace`（当设置了 `OPENCLAW_PROFILE` 时则为 `~/.openclaw/workspace-<profile>`）。
- 状态目录默认为 `~/.openclaw/agents/main/agent`。

## 智能体辅助工具

使用智能体向导添加一个新的隔离智能体：

```bash
openclaw agents add work
```

然后添加 `bindings`（或交由向导自动完成），以实现入站消息路由。

验证方式如下：

```bash
openclaw agents list --bindings
```

## 快速入门

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

## 多智能体 = 多人 + 多人格

启用**多智能体**后，每个 `agentId` 都成为一个**完全隔离的人格**：

- **不同的电话号码/账号**（每个渠道对应一个 `accountId`）。
- **不同的人格特征**（每个智能体工作区内的文件，如 `AGENTS.md` 和 `SOUL.md`）。
- **独立的认证与会话**（除非显式启用，否则无跨智能体交互）。

这使得**多个用户**可以共用一台网关服务器，同时保持各自的 AI “大脑” 与数据相互隔离。

## 一个 WhatsApp 号码，服务多人（私信分流）

您可在**仅使用一个 WhatsApp 账号**的前提下，将**不同的 WhatsApp 私信（DM）** 分流至不同智能体。通过发信人 E.164 号码（例如 `+15551234567`）配合 `peer.kind: "direct"` 实现匹配。回复仍将统一显示为该 WhatsApp 号码发出（不支持按智能体区分发信人身份）。

重要细节：直接私信会合并至智能体的**主会话键名**，因此要实现真正隔离，必须确保**一人一智能体**。

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

注意事项：

- 私信访问控制是**按 WhatsApp 账号全局生效**（配对/白名单），而非按智能体粒度。
- 对于共享群组，请将群组绑定至单一智能体，或使用 [广播群组](/channels/broadcast-groups)。

## 路由规则（消息如何选择智能体）

绑定规则是**确定性的**，且**最具体者优先**：

1. `peer` 匹配（精确匹配私信/群组/渠道 ID）
2. `parentPeer` 匹配（线程继承）
3. `guildId + roles`（Discord 角色路由）
4. `guildId`（Discord）
5. `teamId`（Slack）
6. 按渠道匹配 `accountId`
7. 渠道级匹配（`accountId: "*"`）
8. 回退至默认智能体（`agents.list[].default`；否则取列表首项，默认为 `main`）

若同一层级存在多个匹配的绑定规则，则按配置文件中定义的**顺序取第一个**生效。  
若某条绑定规则设定了多个匹配字段（例如 `peer` + `guildId`），则所有指定字段均须满足（即逻辑“与”语义，`AND`）。

关于账号作用域的重要说明：

- 若绑定规则中未指定 `accountId`，则仅匹配默认账号。
- 使用 `accountId: "*"` 可实现跨所有账号的渠道级回退。
- 若后续为同一智能体添加了含显式账号 ID 的相同绑定规则，OpenClaw 将把已有的仅渠道绑定升级为带账号作用域的绑定，而非重复创建。

## 多账号 / 多电话号码

支持**多账号**的渠道（例如 WhatsApp）使用 `accountId` 来标识每次登录。每个 `accountId` 均可路由至不同智能体，因此单台服务器可托管多个电话号码，且互不混杂会话。

若您希望在未指定 `accountId` 时启用渠道级默认账号，请设置 `channels.<channel>.defaultAccount`（可选）。若未设置，OpenClaw 将回退至 `default`（若存在），否则采用首个配置的账号 ID（按字典序排序）。

支持此模式的常见渠道包括：

- `whatsapp`、`telegram`、`discord`、`slack`、`signal`、`imessage`
- `irc`、`line`、`googlechat`、`mattermost`、`matrix`、`nextcloud-talk`
- `bluebubbles`、`zalo`、`zalouser`、`nostr`、`feishu`

## 核心概念

- `agentId`：一个“大脑”（工作区、按智能体划分的认证、按智能体划分的会话存储）。
- `accountId`：一个渠道账号实例（例如 WhatsApp 账号 `"personal"` 与 `"biz"`）。
- `binding`：依据 `(channel, accountId, peer)`（及可选的服务器/团队 ID）将入站消息路由至某个 `agentId`。
- 直接私信会合并至 `agent:<agentId>:<mainKey>`（每个智能体的“主会话”；`session.mainKey`）。

## 平台示例

### 每个智能体对应一个 Discord 机器人

每个 Discord 机器人账号映射到唯一的 `accountId`。将每个账号绑定至一个智能体，并为每个机器人单独维护白名单。

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

- 请分别邀请各机器人加入服务器，并启用“消息内容意图（Message Content Intent）”。
- Token 存放于 `channels.discord.accounts.<id>.token`（默认账号可使用 `DISCORD_BOT_TOKEN`）。

### 每个智能体对应一个 Telegram 机器人

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

- 请为每个智能体通过 BotFather 创建一个专属机器人，并复制其 Token。
- Token 存放于 `channels.telegram.accounts.<id>.botToken`（默认账号可使用 `TELEGRAM_BOT_TOKEN`）。

### 每个智能体对应一个 WhatsApp 号码

启动网关前，请先完成各账号的绑定：

```bash
openclaw channels login --channel whatsapp --account personal
openclaw channels login --channel whatsapp --account biz
```

`~/.openclaw/openclaw.json`（JSON5）：

```text
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

按渠道拆分：将 WhatsApp 路由至快速日常代理，Telegram 路由至 Opus 代理。

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

备注：

- 如果某个渠道有多个账号，请在绑定中添加 `accountId`（例如 `{ channel: "whatsapp", accountId: "personal" }`）。
- 若希望仅将某一个私信/群组路由至 Opus，而其余消息仍走普通聊天通道，请为该对等端（peer）添加一个 `match.peer` 绑定；对等端匹配规则始终优先于渠道级规则。

## 示例：同一渠道，仅一个对等端路由至 Opus

保持 WhatsApp 使用快速代理，但将某一条私信路由至 Opus：

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

对等端绑定始终具有更高优先级，因此请将其置于渠道级规则之上。

## 家庭代理绑定至 WhatsApp 群组

将专用家庭代理绑定至单个 WhatsApp 群组，并启用提及（@mention）触发机制及更严格的工具策略：

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

备注：

- 工具允许/拒绝列表针对的是 **工具**，而非技能（skills）。如果某项技能需运行二进制程序，请确保已允许 `exec`，且该二进制文件存在于沙箱中。
- 如需更严格的触发控制，请设置 `agents.list[].groupChat.mentionPatterns`，并保持该渠道的群组允许列表处于启用状态。

## 每代理沙箱与工具配置

自 v2026.1.6 版本起，每个代理均可拥有独立的沙箱环境与工具限制：

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

注意：`setupCommand` 位于 `sandbox.docker` 下，在容器创建时仅运行一次。  
当解析的作用域为 `"shared"` 时，每代理的 `sandbox.docker.*` 覆盖配置将被忽略。

**优势：**

- **安全隔离**：为不可信代理限制可用工具  
- **资源管控**：为特定代理启用沙箱，其余代理仍可使用宿主机环境  
- **灵活策略**：为不同代理配置差异化权限  

注意：`tools.elevated` 是 **全局性** 的，且基于发送方（sender）生效；它无法按代理单独配置。  
如需实现每代理边界控制，请使用 `agents.list[].tools` 来拒绝 `exec`。  
对于群组定向场景，请使用 `agents.list[].groupChat.mentionPatterns`，以确保 @提及能准确映射到目标代理。

详见 [多代理沙箱与工具](/tools/multi-agent-sandbox-tools) 获取详细示例。
```