---
summary: "Multi-agent routing: isolated agents, channel accounts, and bindings"
title: Multi-Agent Routing
read_when: "You want multiple isolated agents (workspaces + auth) in one gateway process."
status: active
---
# 多智能体路由

目标：多个 _隔离_ 的智能体（单独的工作区 + `agentDir` + 会话），以及一个运行中的网关中的多个渠道账户（例如两个WhatsApp）。入站消息通过绑定路由到智能体。

## 什么是“一个智能体”？

一个 **智能体** 是一个具有自己独立的：

- **工作区**（文件，AGENTS.md/SOUL.md/USER.md，本地笔记，角色规则）。
- **状态目录** (`agentDir`) 用于身份验证配置文件、模型注册表和每个智能体的配置。
- **会话存储** (`~/.openclaw/agents/<agentId>/sessions`) 下的聊天历史和路由状态。

身份验证配置文件是 **每个智能体** 独立的。每个智能体从自己的读取：

```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

主智能体的凭证 **不会** 自动共享。不要在智能体之间重用 `agentDir`
（会导致身份验证/会话冲突）。如果你想共享凭证，
将 `auth-profiles.json` 复制到另一个智能体的 `agentDir`。

技能是通过每个工作区的 `skills/` 文件夹按智能体划分的，共享技能可以从 `~/.openclaw/skills` 访问。参见 [技能：每个智能体与共享](/tools/skills#per-agent-vs-shared-skills)。

网关可以托管 **一个智能体**（默认）或并排托管 **多个智能体**。

**工作区说明：** 每个智能体的工作区是 **默认的当前工作目录**，而不是硬沙盒。相对路径在工作区内解析，但绝对路径可以访问其他主机位置，除非启用了沙盒。参见
[沙盒](/gateway/sandboxing)。

## 路径（快速映射）

- 配置: `~/.openclaw/openclaw.json` (或 `OPENCLAW_CONFIG_PATH`)
- 状态目录: `~/.openclaw` (或 `OPENCLAW_STATE_DIR`)
- 工作区: `~/.openclaw/workspace` (或 `~/.openclaw/workspace-<agentId>`)
- 智能体目录: `~/.openclaw/agents/<agentId>/agent` (或 `agents.list[].agentDir`)
- 会话: `~/.openclaw/agents/<agentId>/sessions`

### 单智能体模式（默认）

如果你什么都不做，OpenClaw 运行一个单智能体：

- `agentId` 默认为 **`main`**。
- 会话以 `agent:main:<mainKey>` 键入。
- 工作区默认为 `~/.openclaw/workspace`（或当 `OPENCLAW_PROFILE` 设置时为 `~/.openclaw/workspace-<profile>`）。
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

## 多个智能体 = 多个人，多个个性

使用 **多个智能体**，每个 `agentId` 成为一个 **完全隔离的角色**：

- **不同的电话号码/账户**（每个渠道 `accountId`）。
- **不同的个性**（每个智能体的工作区文件如 `AGENTS.md` 和 `SOUL.md`）。
- **独立的身份验证 + 会话**（除非显式启用，否则没有交叉通信）。

这允许 **多个人** 共享一个网关服务器，同时保持他们的AI“大脑”和数据隔离。

## 一个WhatsApp号码，多个人（DM拆分）

您可以将**不同的WhatsApp DM**路由到不同的代理，同时使用**一个WhatsApp账户**。通过发送者的E.164号码（如 `+15551234567`）与 `peer.kind: "dm"` 匹配。回复仍然来自同一个WhatsApp号码（没有每个代理的单独发送者身份）。

重要细节：直接聊天会合并到代理的**主会话密钥**，因此真正的隔离需要**每个人员一个代理**。

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
    { agentId: "alex", match: { channel: "whatsapp", peer: { kind: "dm", id: "+15551230001" } } },
    { agentId: "mia", match: { channel: "whatsapp", peer: { kind: "dm", id: "+15551230002" } } },
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

- DM访问控制是**每个WhatsApp账户**（配对/白名单）级别的，而不是每个代理。
- 对于共享群组，将群组绑定到一个代理或使用[广播群组](/broadcast-groups)。

## 路由规则（消息如何选择代理）

绑定是**确定性的**且**最具体的匹配优先**：

1. `peer` 匹配（精确的DM/群组/频道ID）
2. `guildId`（Discord）
3. `teamId`（Slack）
4. 频道匹配 `accountId`
5. 频道级别匹配 (`accountId: "*"`)
6. 回退到默认代理 (`agents.list[].default`，否则第一个列表条目，默认：`main`)

## 多个账户/电话号码

支持**多个账户**的渠道（例如WhatsApp）使用 `accountId` 来标识每个登录。每个 `accountId` 可以路由到不同的代理，因此一台服务器可以托管多个电话号码而不会混合会话。

## 概念

- `agentId`：一个“大脑”（工作区，每个代理的身份验证，每个代理的会话存储）。
- `accountId`：一个渠道账户实例（例如WhatsApp账户 `"personal"` 对比 `"biz"`）。
- `binding`：根据 `(channel, accountId, peer)` 和可选的公会/团队ID将传入消息路由到一个 `agentId`。
- 直接聊天合并到 `agent:<agentId>:<mainKey>`（每个代理的“主”；`session.mainKey`）。

## 示例：两个WhatsApp → 两个代理

`~/.openclaw/openclaw.json`（JSON5）：

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

  // 确定性路由：第一个匹配获胜（最具体的优先）。
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },

// 可选的每个对等体覆盖（示例：将特定群组发送到工作代理）。
{
  agentId: "work",
  match: {
    channel: "whatsapp",
    accountId: "personal",
    peer: { kind: "group", id: "1203630...@g.us" },
  },
},
],

// 默认关闭：代理到代理的消息传递必须显式启用并列入白名单。
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
        // 可选覆盖。默认：~/.openclaw/credentials/whatsapp/personal
        // authDir: "~/.openclaw/credentials/whatsapp/personal",
      },
      biz: {
        // 可选覆盖。默认：~/.openclaw/credentials/whatsapp/biz
        // authDir: "~/.openclaw/credentials/whatsapp/biz",
      },
    },
  },
},
```

## Example: WhatsApp daily chat + Telegram deep work

Split by channel: route WhatsApp to a fast everyday agent and Telegram to an Opus agent.

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
        model: "anthropic/claude-opus-4-5",
      },
    ],
  },
  bindings: [
    { agentId: "chat", match: { channel: "whatsapp" } },
    { agentId: "opus", match: { channel: "telegram" } },
  ],
}
```

Notes:

- If you have multiple accounts for a channel, add `accountId` to the binding (for example `{ channel: "whatsapp", accountId: "personal" }`).
- To route a single DM/group to Opus while keeping the rest on chat, add a `match.peer` binding for that peer; peer matches always win over channel-wide rules.

## Example: same channel, one peer to Opus

Keep WhatsApp on the fast agent, but route one DM to Opus:

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
        model: "anthropic/claude-opus-4-5",
      },
    ],
  },
  bindings: [
    { agentId: "opus", match: { channel: "whatsapp", peer: { kind: "dm", id: "+15551234567" } } },
    { agentId: "chat", match: { channel: "whatsapp" } },
  ],
}
```

对等体绑定总是优先，因此将其置于通道范围规则之上。

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

- 工具允许/拒绝列表是 **tools**，而不是技能。如果一个技能需要运行一个二进制文件，请确保 `exec` 是被允许的，并且该二进制文件存在于沙箱中。
- 为了更严格的控制，设置 `agents.list[].groupChat.mentionPatterns` 并保持
  渠道的组允许列表启用。

## 每个代理的沙箱和工具配置

从 v2026.1.6 开始，每个代理可以有自己的沙箱和工具限制：

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

注意：`setupCommand` 存在于 `sandbox.docker` 下，并在容器创建时运行一次。
每个代理的 `sandbox.docker.*` 覆盖在解析范围为 `"shared"` 时会被忽略。

**优点：**

- **安全隔离**：限制不受信任代理的工具
- **资源控制**：对特定代理进行沙箱处理，而其他代理保留在主机上
- **灵活的策略**：每个代理不同的权限

注意：`tools.elevated` 是 **全局** 的且基于发送者；它不能按代理进行配置。
如果您需要每个代理的边界，请使用 `agents.list[].tools` 来拒绝 `exec`。
对于组目标，请使用 `agents.list[].groupChat.mentionPatterns` 以便 @提及能够干净地映射到预期的代理。

参见 [多代理沙箱 & 工具](/multi-agent-sandbox-tools) 获取详细示例。