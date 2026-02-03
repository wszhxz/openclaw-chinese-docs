---
summary: "Multi-agent routing: isolated agents, channel accounts, and bindings"
title: Multi-Agent Routing
read_when: "You want multiple isolated agents (workspaces + auth) in one gateway process."
status: active
---
.<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context and key terms. The document is about multi-agent routing in a system called OpenClaw, explaining how multiple agents can be managed within a single gateway, their configurations, and routing rules.

First, I'll identify the main sections and headings. There's a section on "Multi-Agent Routing" with subheadings like "What is 'one agent'?" and "Paths (quick map)". There are also examples and code snippets in JSON format. I need to make sure that technical terms like "agentDir", "workspace", "bindings", and specific JSON keys are accurately translated while maintaining their meaning.

I should be careful with the structure, ensuring that headings and subheadings are correctly translated. For instance, "Multi-Agent Routing" becomes "多代理路由". Terms like "agent" should be consistently translated as "代理" or "代理程序" depending on context. 

Looking at the code examples, I need to preserve the JSON syntax and structure. The keys like "agentId", "workspace", "bindings", etc., should remain in English since they are part of the configuration. However, the surrounding text explaining these keys should be translated. For example, "agentId" is translated as "代理ID" but the key itself stays as "agentId".

I'll also pay attention to specific terms like "sandbox" which translates to "沙箱", and "tool restrictions" as "工具限制". The examples provided, such as the JSON configurations, need to be accurately translated in terms of their structure and content, ensuring that the meaning of each part is clear.

Another important aspect is maintaining the technical accuracy of the document. For instance, terms like "direct chats collapse to the agent’s main session key" should be translated in a way that conveys the technical process without losing the original meaning. 

I should also check for any specific jargon or acronyms that might need to be kept in English, such as "E.164" which is a standard for phone numbers. These should remain in their original form to avoid confusion.

Finally, I'll review the entire translation to ensure consistency in terminology, correct grammar, and that the flow of information matches the original document. This will help ensure that the translated document is both accurate and easy to understand for Chinese-speaking users.
</think>

# 多代理路由

目标：多个**隔离**的代理（独立工作区 + `agentDir` + 会话），以及在一个运行中的网关中多个通道账户（例如两个 WhatsApp）。入站消息通过绑定路由到某个代理。

## 什么是“一个代理”？

**代理**是一个完全作用域的“大脑”，拥有自己的：

- **工作区**（文件、AGENTS.md/SOUL.md/USER.md、本地笔记、人格规则）。
- **状态目录**（`agentDir`）用于认证配置文件、模型注册表和每个代理的配置。
- **会话存储**（聊天历史 + 路由状态）位于 `~/.openclaw/agents/<agentId>/sessions`。

认证配置文件是**每个代理独立**的。每个代理从自己的：

```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

读取。主代理的凭证**不会自动共享**。绝不要在不同代理之间复用 `agentDir`（会导致认证/会话冲突）。如果你想共享凭证，请将 `auth-profiles.json` 复制到其他代理的 `agentDir` 中。

技能是通过每个工作区的 `skills/` 文件夹实现的，共享技能可以从 `~/.openclaw/skills` 获取。详见 [技能：每个代理 vs 共享技能](/tools/skills#per-agent-vs-shared-skills)。

网关可以托管**一个代理**（默认）或**多个代理**并行运行。

**工作区说明**：每个代理的工作区是**默认当前工作目录**，不是严格的沙箱。相对路径在工作区内部解析，但绝对路径可以访问其他主机位置，除非启用了沙箱。详见 [沙箱](/gateway/sandboxing)。

## 路径（快速映射）

- 配置：`~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）
- 状态目录：`~/.openclaw`（或 `OPENCLAW_STATE_DIR`）
- 工作区：`~/.openclaw/workspace`（或 `~/.openclaw/workspace-<agentId>`）
- 代理目录：`~/.openclaw/agents/<agentId>/agent`（或 `agents.list[].agentDir`）
- 会话：`~/.openclaw/agents/<agentId>/sessions`

### 单代理模式（默认）

如果你不做任何操作，OpenClaw 将运行一个代理：

- `agentId` 默认为 **`main`**。
- 会话以 `agent:main:<mainKey>` 为键。
- 工作区默认为 `~/.openclaw/workspace`（或 `~/.openclaw/workspace-<agentId>`）。
- 代理目录默认为 `~/.openclaw/agents/<agentId>/agent`。

## 代理绑定到 WhatsApp 群组

将一个专用的家庭代理绑定到一个 WhatsApp 群组，设置提及门控和更严格的工具策略：

```json
{
  "agents": {
    "list": [
      {
        "id": "family",
        "name": "Family",
        "workspace": "~/.openclaw/workspace-family",
        "identity": { "name": "Family Bot" },
        "groupChat": {
          "mentionPatterns": ["@family", "@familybot", "@Family Bot"],
        },
        "sandbox": {
          "mode": "all",
          "scope": "agent",
        },
        "tools": {
          "allow": [
            "exec",
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          "deny": ["write", "edit", "apply_patch", "browser", "canvas", "nodes", "cron"],
        },
      },
    ],
  },
  "bindings": [
    {
      "agentId": "family",
      "match": {
        "channel": "whatsapp",
        "peer": { "kind": "group", "id": "120363999999999999@g.us" },
      },
    },
  ],
}
```

**说明**：

- 工具允许/拒绝列表是**工具**，不是技能。如果一个技能需要运行一个二进制文件，请确保 `exec` 被允许且二进制文件存在于沙箱中。
- 对于更严格的门控，请设置 `agents.list[].groupChat.mentionPatterns` 并保持通道的群允许列表启用。

## 每个代理的沙箱和工具配置

从 v2026.1.6 开始，每个代理可以有自己的沙箱和工具限制：

```js
{
  "agents": {
    "list": [
      {
        "id": "personal",
        "workspace": "~/.openclaw/workspace-personal",
        "sandbox": {
          "mode": "off",  // 个人代理无沙箱
        },
        // 无工具限制 - 所有工具可用
      },
      {
        "id": "family",
        "workspace": "~/.openclaw/workspace-family",
        "sandbox": {
          "mode": "all",     // 始终沙箱化
          "scope": "agent",  // 每个代理一个容器
          "docker": {
            // 容器创建后的一次性设置命令
            "setupCommand": "apt-get update && apt-get install -y git curl",
          },
        },
        "tools": {
          "allow": ["read"],                    // 仅允许读取工具
          "deny": ["exec", "write", "edit", "apply_patch"],    // 拒绝其他工具
        },
      },
    ],
  },
}
```

**注意**：`setupCommand` 位于 `sandbox.docker` 下，并在容器创建时运行一次。当解析的范围是 `"shared"` 时，忽略每个代理的 `sandbox.docker.*` 覆盖。

**优势**：

- **安全隔离**：限制不受信任代理的工具
- **资源控制**：沙箱特定代理，而其他代理保持在主机上
- **灵活策略**：每个代理不同的权限

**注意**：`tools.elevated` 是**全局**的，并基于发送者；它不能按代理配置。如果你需要按代理边界，使用 `agents.list[].tools` 来拒绝 `exec`。对于群组目标，请使用 `agents.list[].groupChat.mentionPatterns` 以便 @提及清晰映射到目标代理。

详见 [多代理沙箱 & 工具](/multi-agent-sandbox-tools) 获取详细示例。