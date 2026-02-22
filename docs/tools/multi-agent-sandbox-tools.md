---
summary: "Per-agent sandbox + tool restrictions, precedence, and examples"
title: Multi-Agent Sandbox & Tools
read_when: "You want per-agent sandboxing or per-agent tool allow/deny policies in a multi-agent gateway."
status: active
---
# 多智能体沙箱及工具配置

## 概述

多智能体设置中的每个智能体现在可以有自己的：

- **沙箱配置** (`agents.list[].sandbox` 覆盖 `agents.defaults.sandbox`)
- **工具限制** (`tools.allow` / `tools.deny`，加上 `agents.list[].tools`)

这允许你运行具有不同安全配置文件的多个智能体：

- 具有完全访问权限的个人助理
- 工具受限的家庭/工作智能体
- 运行在沙箱中的面向公众的智能体

`setupCommand` 属于 `sandbox.docker`（全局或每个智能体），并在创建容器时运行一次。

身份验证是每个智能体独立的：每个智能体从自己的 `agentDir` 身份验证存储中读取：

```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

智能体之间不共享凭证。不要在智能体之间重用 `agentDir`。
如果你想共享凭证，请将 `auth-profiles.json` 复制到其他智能体的 `agentDir` 中。

有关沙箱在运行时的行为，请参阅 [Sandboxing](/gateway/sandboxing)。
有关调试“为什么被阻止了？”，请参阅 [Sandbox vs Tool Policy vs Elevated](/gateway/sandbox-vs-tool-policy-vs-elevated) 和 `openclaw sandbox explain`。

---

## 配置示例

### 示例 1：个人 + 受限家庭智能体

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "name": "Personal Assistant",
        "workspace": "~/.openclaw/workspace",
        "sandbox": { "mode": "off" }
      },
      {
        "id": "family",
        "name": "Family Bot",
        "workspace": "~/.openclaw/workspace-family",
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        },
        "tools": {
          "allow": ["read"],
          "deny": ["exec", "write", "edit", "apply_patch", "process", "browser"]
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "family",
      "match": {
        "provider": "whatsapp",
        "accountId": "*",
        "peer": {
          "kind": "group",
          "id": "120363424282127706@g.us"
        }
      }
    }
  ]
}
```

**结果：**

- `main` 智能体：在主机上运行，具有完整工具访问权限
- `family` 智能体：在 Docker 中运行（每个智能体一个容器），仅使用 `read` 工具

---

### 示例 2：具有共享沙箱的工作智能体

```json
{
  "agents": {
    "list": [
      {
        "id": "personal",
        "workspace": "~/.openclaw/workspace-personal",
        "sandbox": { "mode": "off" }
      },
      {
        "id": "work",
        "workspace": "~/.openclaw/workspace-work",
        "sandbox": {
          "mode": "all",
          "scope": "shared",
          "workspaceRoot": "/tmp/work-sandboxes"
        },
        "tools": {
          "allow": ["read", "write", "apply_patch", "exec"],
          "deny": ["browser", "gateway", "discord"]
        }
      }
    ]
  }
}
```

---

### 示例 2b：全局编码配置文件 + 仅消息传递智能体

```json
{
  "tools": { "profile": "coding" },
  "agents": {
    "list": [
      {
        "id": "support",
        "tools": { "profile": "messaging", "allow": ["slack"] }
      }
    ]
  }
}
```

**结果:**

- default agents get coding tools
- `support` agent is messaging-only (+ Slack tool)

---

### 示例 3: 每个代理不同的沙盒模式

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main", // Global default
        "scope": "session"
      }
    },
    "list": [
      {
        "id": "main",
        "workspace": "~/.openclaw/workspace",
        "sandbox": {
          "mode": "off" // Override: main never sandboxed
        }
      },
      {
        "id": "public",
        "workspace": "~/.openclaw/workspace-public",
        "sandbox": {
          "mode": "all", // Override: public always sandboxed
          "scope": "agent"
        },
        "tools": {
          "allow": ["read"],
          "deny": ["exec", "write", "edit", "apply_patch"]
        }
      }
    ]
  }
}
```

---

## 配置优先级

当同时存在全局 (`agents.defaults.*`) 和代理特定 (`agents.list[].*`) 配置时：

### 沙盒配置

代理特定设置覆盖全局：

```
agents.list[].sandbox.mode > agents.defaults.sandbox.mode
agents.list[].sandbox.scope > agents.defaults.sandbox.scope
agents.list[].sandbox.workspaceRoot > agents.defaults.sandbox.workspaceRoot
agents.list[].sandbox.workspaceAccess > agents.defaults.sandbox.workspaceAccess
agents.list[].sandbox.docker.* > agents.defaults.sandbox.docker.*
agents.list[].sandbox.browser.* > agents.defaults.sandbox.browser.*
agents.list[].sandbox.prune.* > agents.defaults.sandbox.prune.*
```

**注意:**

- `agents.list[].sandbox.{docker,browser,prune}.*` 覆盖该代理的 `agents.defaults.sandbox.{docker,browser,prune}.*`（当沙盒范围解析为 `"shared"` 时忽略）。

### 工具限制

过滤顺序为：

1. **工具配置文件** (`tools.profile` 或 `agents.list[].tools.profile`)
2. **提供商工具配置文件** (`tools.byProvider[provider].profile` 或 `agents.list[].tools.byProvider[provider].profile`)
3. **全局工具策略** (`tools.allow` / `tools.deny`)
4. **提供商工具策略** (`tools.byProvider[provider].allow/deny`)
5. **代理特定工具策略** (`agents.list[].tools.allow/deny`)
6. **代理提供商策略** (`agents.list[].tools.byProvider[provider].allow/deny`)
7. **沙盒工具策略** (`tools.sandbox.tools` 或 `agents.list[].tools.sandbox.tools`)
8. **子代理工具策略** (`tools.subagents.tools`，如果适用）

每个级别可以进一步限制工具，但不能恢复之前级别拒绝的工具。
如果设置了 `agents.list[].tools.sandbox.tools`，它将替换该代理的 `tools.sandbox.tools`。
如果设置了 `agents.list[].tools.profile`，它将覆盖该代理的 `tools.profile`。
提供商工具密钥接受 `provider`（例如 `google-antigravity`）或 `provider/model`（例如 `openai/gpt-5.2`）。

### 工具组（简写）

工具策略（全局、代理、沙盒）支持 `group:*` 条目，这些条目会扩展为多个具体的工具：

- `group:runtime`: `exec`, `bash`, `process`
- `group:fs`: `read`, `write`, `edit`, `apply_patch`
- `group:sessions`: `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status`
- `group:memory`: `memory_search`, `memory_get`
- `group:ui`: `browser`, `canvas`
- `group:automation`: `cron`, `gateway`
- `group:messaging`: `message`
- `group:nodes`: `nodes`
- `group:openclaw`: 所有内置的OpenClaw工具（不包括提供商插件）

### 提升模式

`tools.elevated` 是全局基线（基于发送者的允许列表）。`agents.list[].tools.elevated` 可以进一步限制特定代理的提升权限（两者都必须允许）。

缓解模式：

- 拒绝不受信任代理的 `exec` (`agents.list[].tools.deny: ["exec"]`)
- 避免将路由到受限代理的发送者加入允许列表
- 如果只想进行沙箱执行，请全局禁用提升 (`tools.elevated.enabled: false`)
- 对敏感配置文件禁用每个代理的提升 (`agents.list[].tools.elevated.enabled: false`)

---

## 从单代理迁移

**之前（单代理）：**

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.openclaw/workspace",
      "sandbox": {
        "mode": "non-main"
      }
    }
  },
  "tools": {
    "sandbox": {
      "tools": {
        "allow": ["read", "write", "apply_patch", "exec"],
        "deny": []
      }
    }
  }
}
```

**之后（多代理，不同配置文件）：**

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "workspace": "~/.openclaw/workspace",
        "sandbox": { "mode": "off" }
      }
    ]
  }
}
```

旧的 `agent.*` 配置通过 `openclaw doctor` 迁移；建议以后使用 `agents.defaults` + `agents.list`。

---

## 工具限制示例

### 只读代理

```json
{
  "tools": {
    "allow": ["read"],
    "deny": ["exec", "write", "edit", "apply_patch", "process"]
  }
}
```

### 安全执行代理（无文件修改）

```json
{
  "tools": {
    "allow": ["read", "exec", "process"],
    "deny": ["write", "edit", "apply_patch", "browser", "gateway"]
  }
}
```

### 仅通信代理

```json
{
  "tools": {
    "sessions": { "visibility": "tree" },
    "allow": ["sessions_list", "sessions_send", "sessions_history", "session_status"],
    "deny": ["exec", "write", "edit", "apply_patch", "read", "browser"]
  }
}
```

---

## 常见陷阱：“非主代理”

`agents.defaults.sandbox.mode: "non-main"` 基于 `session.mainKey`（默认 `"main"`），
而不是代理ID。组/频道会话总是有自己的密钥，因此被视为非主代理并会被沙箱化。如果您希望某个代理永不被沙箱化，请设置 `agents.list[].sandbox.mode: "off"`。

---

## 测试

在配置多代理沙箱和工具后：

1. **检查代理解析：**

   ```exec
   openclaw agents list --bindings
   ```

2. **验证沙箱容器:**

   ```exec
   docker ps --filter "name=openclaw-sbx-"
   ```

3. **测试工具限制:**
   - 发送一条需要受限工具的消息
   - 验证代理无法使用被拒绝的工具

4. **监控日志:**

   ```exec
   tail -f "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/logs/gateway.log" | grep -E "routing|sandbox|tools"
   ```

---

## 故障排除

### 尽管有`mode: "all"`，代理未被沙箱化

- 检查是否有全局`agents.defaults.sandbox.mode`覆盖了它
- 代理特定配置优先级更高，因此设置`agents.list[].sandbox.mode: "all"`

### 尽管有拒绝列表，工具仍然可用

- 检查工具过滤顺序：全局 → 代理 → 沙箱 → 子代理
- 每个级别只能进一步限制，不能重新授权
- 使用日志验证：`[tools] filtering tools for agent:${agentId}`

### 容器未按代理隔离

- 在代理特定的沙箱配置中设置`scope: "agent"`
- 默认是`"session"`，每个会话创建一个容器

---

## 参见

- [多代理路由](/concepts/multi-agent)
- [沙箱配置](/gateway/configuration#agentsdefaults-sandbox)
- [会话管理](/concepts/session)