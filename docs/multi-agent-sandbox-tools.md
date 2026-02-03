---
summary: "Per-agent sandbox + tool restrictions, precedence, and examples"
title: Multi-Agent Sandbox & Tools
read_when: "You want per-agent sandboxing or per-agent tool allow/deny policies in a multi-agent gateway."
status: active
---
# 多代理沙箱 & 工具配置

## 概述

在多代理设置中，每个代理现在可以拥有自己的：

- **沙箱配置**（`agents.list[].sandbox` 覆盖 `agents.defaults.sandbox`）
- **工具限制**（`tools.allow` / `tools.deny`，加上 `agents.list[].tools`）

这允许您运行具有不同安全配置的多个代理：

- 拥有完全访问权限的个人助理
- 限制工具的家庭/工作代理
- 在沙箱中运行的面向公众的代理

`setupCommand` 应属于 `sandbox.docker`（全局或每个代理）并在容器创建时运行一次。

认证是每个代理独立的：每个代理从其自己的 `agentDir` 认证存储中读取，路径为：

```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

凭证在代理之间**不共享**。不要在不同代理之间重复使用 `agentDir`。如果您想共享凭证，请将 `auth-profiles.json` 复制到其他代理的 `agentDir` 中。

有关运行时沙箱行为的详细信息，请参阅 [沙箱](/gateway/sandboxing)。有关“为什么被阻止？”的调试信息，请参阅 [沙箱 vs 工具策略 vs 提升权限](/gateway/sandbox-vs-tool-policy-vs-elevated) 和 `openclaw sandbox explain`。

---

## 配置示例

### 示例 1：个人 + 受限家庭代理

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "name": "个人助理",
        "workspace": "~/.openclaw/workspace",
        "sandbox": { "mode": "off" }
      },
      {
        "id": "family",
        "name": "家庭机器人",
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

- `main` 代理：在主机上运行，拥有完整工具访问权限
- `family` 代理：在 Docker 中运行（每个代理一个容器），仅允许 `read` 工具

---

### 示例 2：共享沙箱的工作代理

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

### 示例 2b：全局编码配置 + 仅消息代理

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

**结果：**

- 默认代理获得编码工具
- `support` 代理仅限消息（+ Slack 工具）

---

### 示例 3：每个代理不同的沙箱模式

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main", // 全局默认
        "scope": "session"
      }
    },
    "list": [
      {
        "id": "main",
        "workspace": "~/.openclaw/workspace",
        "sandbox": {
          "mode": "off" // 覆盖：main 代理永不沙箱化
        }
      },
      {
        "id": "public",
        "workspace": "~/.openclaw/workspace-public",
        "sandbox": {
          "mode": "all", // 覆盖：public 代理始终沙箱化
          "scope": "agent"
        },
        "tools": {
          "allow": ["read"],
          "deny": ["exec", "write", "edit", "apply_patch", "process", "browser"]
        }
      }
    ]
  }
}
```

---

## 常见陷阱："non-main"

`agents.defaults.sandbox.mode: "non-main"` 基于 `session.mainKey`（默认为 `"main"`），而不是代理 ID。群组/频道会话始终拥有自己的密钥，因此被视为非主模式并被沙箱化。如果您希望某个代理永不沙箱化，请设置 `agents.list[].sandbox.mode: "off"`。

---

## 测试

在配置多代理沙箱和工具后：

1. **检查代理解析：**

   ```exec
   openclaw agents list --bindings
   ```

2. **验证沙箱容器：**

   ```exec
   docker ps --filter "name=openclaw-sbx-"
   ```

3. **测试工具限制：**
   - 发送需要受限工具的消息
   - 验证代理无法使用被拒绝的工具

4. **监控日志：**
   ```exec
   tail -f "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/logs/gateway.log" | grep -E "路由|沙箱|工具"
   ```

---

## 故障排除

### 代理未被沙箱化，尽管 `mode: "all"`

- 检查是否存在全局 `agents.defaults.sandbox.mode` 覆盖了它
- 代理特定配置优先，因此设置 `agents.list[].sandbox.mode: "all"`

### 尽管有拒绝列表，工具仍可用

- 检查工具过滤顺序：全局 → 代理 → 沙箱 → 子代理
- 每个层级只能进一步限制，不能重新授予
- 通过日志验证：`[tools] 为代理:${agentId} 过滤工具`

### 容器未按代理隔离

- 在代理特定沙箱配置中设置 `scope: "agent"`
- 默认是 `"session"`，每个会话创建一个容器

---

## 参见

- [多代理路由](/concepts/multi-agent)
- [沙箱配置](/gateway/configuration#agentsdefaults-sandbox)
- [会话管理](/concepts/session)