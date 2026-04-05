---
summary: "Broadcast a WhatsApp message to multiple agents"
read_when:
  - Configuring broadcast groups
  - Debugging multi-agent replies in WhatsApp
status: experimental
title: "Broadcast Groups"
---
# 广播组

**状态：** 实验性  
**版本：** 添加于 2026.1.9

## 概述

广播组允许多个智能体同时处理并响应同一条消息。这使您能够创建专门的智能体团队，在单个 WhatsApp 群组或私信中协同工作——所有都使用一个电话号码。

当前范围：**仅限 WhatsApp**（网页渠道）。

广播组在通道白名单和群组激活规则之后进行评估。在 WhatsApp 群组中，这意味着当 OpenClaw 通常会回复时（例如：被提及时，取决于您的群组设置），就会发生广播。

## 用例

### 1. 专用智能体团队

部署具有原子化、专注职责的多个智能体：

```
Group: "Development Team"
Agents:
  - CodeReviewer (reviews code snippets)
  - DocumentationBot (generates docs)
  - SecurityAuditor (checks for vulnerabilities)
  - TestGenerator (suggests test cases)
```

每个智能体处理相同的消息并提供其专业视角。

### 2. 多语言支持

```
Group: "International Support"
Agents:
  - Agent_EN (responds in English)
  - Agent_DE (responds in German)
  - Agent_ES (responds in Spanish)
```

### 3. 质量保证工作流

```
Group: "Customer Support"
Agents:
  - SupportAgent (provides answer)
  - QAAgent (reviews quality, only responds if issues found)
```

### 4. 任务自动化

```
Group: "Project Management"
Agents:
  - TaskTracker (updates task database)
  - TimeLogger (logs time spent)
  - ReportGenerator (creates summaries)
```

## 配置

### 基本设置

添加顶层 `broadcast` 部分（位于 `bindings` 旁边）。键是 WhatsApp 对等 ID：

- 群聊：群组 JID（例如 `120363403215116621@g.us`）
- 私信：E.164 电话号码（例如 `+15551234567`）

```json
{
  "broadcast": {
    "120363403215116621@g.us": ["alfred", "baerbel", "assistant3"]
  }
}
```

**结果：** 当 OpenClaw 在此聊天中回复时，它将运行所有三个智能体。

### 处理策略

控制智能体如何处理消息：

#### 并行（默认）

所有智能体同时处理：

```json
{
  "broadcast": {
    "strategy": "parallel",
    "120363403215116621@g.us": ["alfred", "baerbel"]
  }
}
```

#### 顺序

智能体按顺序处理（一个等待前一个完成）：

```json
{
  "broadcast": {
    "strategy": "sequential",
    "120363403215116621@g.us": ["alfred", "baerbel"]
  }
}
```

### 完整示例

```json
{
  "agents": {
    "list": [
      {
        "id": "code-reviewer",
        "name": "Code Reviewer",
        "workspace": "/path/to/code-reviewer",
        "sandbox": { "mode": "all" }
      },
      {
        "id": "security-auditor",
        "name": "Security Auditor",
        "workspace": "/path/to/security-auditor",
        "sandbox": { "mode": "all" }
      },
      {
        "id": "docs-generator",
        "name": "Documentation Generator",
        "workspace": "/path/to/docs-generator",
        "sandbox": { "mode": "all" }
      }
    ]
  },
  "broadcast": {
    "strategy": "parallel",
    "120363403215116621@g.us": ["code-reviewer", "security-auditor", "docs-generator"],
    "120363424282127706@g.us": ["support-en", "support-de"],
    "+15555550123": ["assistant", "logger"]
  }
}
```

## 工作原理

### 消息流程

1. **传入消息** 到达 WhatsApp 群组
2. **广播检查**：系统检查对等 ID 是否在 `broadcast` 中
3. **如果在广播列表中**：
   - 所有列出的智能体处理该消息
   - 每个智能体拥有自己的会话密钥和隔离上下文
   - 智能体并行（默认）或顺序处理
4. **如果不在广播列表中**：
   - 应用正常路由（第一个匹配绑定）

注意：广播组不会绕过通道白名单或群组激活规则（提及/命令等）。它们仅改变当消息符合处理条件时 _哪些智能体运行_。

### 会话隔离

广播组中的每个智能体保持完全独立的：

- **会话密钥** (`agent:alfred:whatsapp:group:120363...` 与 `agent:baerbel:whatsapp:group:120363...`)
- **对话历史**（智能体看不到其他智能体的消息）
- **工作区**（如果配置了则独立沙盒）
- **工具访问**（不同的允许/拒绝列表）
- **记忆/上下文**（独立的 IDENTITY.md, SOUL.md 等）
- **群组上下文缓冲区**（用于上下文的最近群组消息）是按对等体共享的，因此所有广播智能体在触发时看到相同的上下文

这使得每个智能体可以拥有：

- 不同的人格
- 不同的工具访问权限（例如，只读与读写）
- 不同的模型（例如，opus 与 sonnet）
- 安装了不同的技能

### 示例：隔离会话

在群组 `120363403215116621@g.us` 中，带有智能体 `["alfred", "baerbel"]`：

**Alfred 的上下文：**

```
Session: agent:alfred:whatsapp:group:120363403215116621@g.us
History: [user message, alfred's previous responses]
Workspace: /Users/user/openclaw-alfred/
Tools: read, write, exec
```

**Bärbel 的上下文：**

```
Session: agent:baerbel:whatsapp:group:120363403215116621@g.us
History: [user message, baerbel's previous responses]
Workspace: /Users/user/openclaw-baerbel/
Tools: read only
```

## 最佳实践

### 1. 保持智能体专注

为每个智能体设计单一、清晰的职责：

```json
{
  "broadcast": {
    "DEV_GROUP": ["formatter", "linter", "tester"]
  }
}
```

✅ **好：** 每个智能体有一个任务  
❌ **坏：** 一个通用的“开发助手”智能体

### 2. 使用描述性名称

明确每个智能体的功能：

```json
{
  "agents": {
    "security-scanner": { "name": "Security Scanner" },
    "code-formatter": { "name": "Code Formatter" },
    "test-generator": { "name": "Test Generator" }
  }
}
```

### 3. 配置不同的工具访问权限

只给智能体他们需要的工具：

```json
{
  "agents": {
    "reviewer": {
      "tools": { "allow": ["read", "exec"] } // Read-only
    },
    "fixer": {
      "tools": { "allow": ["read", "write", "edit", "exec"] } // Read-write
    }
  }
}
```

### 4. 监控性能

对于大量智能体，请考虑：

- 使用 `"strategy": "parallel"`（默认）以获得速度
- 将广播组限制为 5-10 个智能体
- 为更简单的智能体使用更快的模型

### 5. 优雅地处理失败

智能体独立失败。一个智能体的错误不会阻塞其他智能体：

```
Message → [Agent A ✓, Agent B ✗ error, Agent C ✓]
Result: Agent A and C respond, Agent B logs error
```

## 兼容性

### 提供商

广播组目前适用于：

- ✅ WhatsApp（已实现）
- 🚧 Telegram（计划中）
- 🚧 Discord（计划中）
- 🚧 Slack（计划中）

### 路由

广播组与现有路由协同工作：

```json
{
  "bindings": [
    {
      "match": { "channel": "whatsapp", "peer": { "kind": "group", "id": "GROUP_A" } },
      "agentId": "alfred"
    }
  ],
  "broadcast": {
    "GROUP_B": ["agent1", "agent2"]
  }
}
```

- `GROUP_A`: 只有 alfred 回复（正常路由）
- `GROUP_B`: agent1 和 agent2 回复（广播）

**优先级：** `broadcast` 优先于 `bindings`。

## 故障排除

### 智能体未响应

**检查：**

1. 智能体 ID 存在于 `agents.list` 中
2. 对等 ID 格式正确（例如，`120363403215116621@g.us`）
3. 智能体不在拒绝列表中

**调试：**

```bash
tail -f ~/.openclaw/logs/gateway.log | grep broadcast
```

### 只有一个智能体响应

**原因：** 对等 ID 可能在 `bindings` 中但不在 `broadcast` 中。

**修复：** 添加到广播配置或从绑定中移除。

### 性能问题

**如果智能体多时速度慢：**

- 减少每组的智能体数量
- 使用更轻量的模型（用 sonnet 代替 opus）
- 检查沙盒启动时间

## 示例

### 示例 1：代码审查团队

```json
{
  "broadcast": {
    "strategy": "parallel",
    "120363403215116621@g.us": [
      "code-formatter",
      "security-scanner",
      "test-coverage",
      "docs-checker"
    ]
  },
  "agents": {
    "list": [
      {
        "id": "code-formatter",
        "workspace": "~/agents/formatter",
        "tools": { "allow": ["read", "write"] }
      },
      {
        "id": "security-scanner",
        "workspace": "~/agents/security",
        "tools": { "allow": ["read", "exec"] }
      },
      {
        "id": "test-coverage",
        "workspace": "~/agents/testing",
        "tools": { "allow": ["read", "exec"] }
      },
      { "id": "docs-checker", "workspace": "~/agents/docs", "tools": { "allow": ["read"] } }
    ]
  }
}
```

**用户发送：** 代码片段  
**回复：**

- code-formatter: “修复了缩进并添加了类型提示”
- security-scanner: "⚠️ 第 12 行存在 SQL 注入漏洞”
- test-coverage: “覆盖率为 45%，缺少错误情况的测试”
- docs-checker: “函数 `process_data` 缺少文档字符串”

### 示例 2：多语言支持

```json
{
  "broadcast": {
    "strategy": "sequential",
    "+15555550123": ["detect-language", "translator-en", "translator-de"]
  },
  "agents": {
    "list": [
      { "id": "detect-language", "workspace": "~/agents/lang-detect" },
      { "id": "translator-en", "workspace": "~/agents/translate-en" },
      { "id": "translator-de", "workspace": "~/agents/translate-de" }
    ]
  }
}
```

## API 参考

### 配置模式

```typescript
interface OpenClawConfig {
  broadcast?: {
    strategy?: "parallel" | "sequential";
    [peerId: string]: string[];
  };
}
```

### 字段

- `strategy`（可选）：如何处理智能体
  - `"parallel"`（默认）：所有智能体同时处理
  - `"sequential"`：智能体按数组顺序处理
- `[peerId]`：WhatsApp 群组 JID、E.164 号码或其他对等 ID
  - 值：应处理消息的智能体 ID 数组

## 限制

1. **最大智能体数：** 没有硬性限制，但 10+ 个智能体可能会慢
2. **共享上下文：** 智能体看不到彼此的回复（设计如此）
3. **消息排序：** 并行回复可能以任何顺序到达
4. **速率限制：** 所有智能体都计入 WhatsApp 速率限制

## 未来增强

计划功能：

- [ ] 共享上下文模式（智能体可看到彼此的回复）
- [ ] 智能体协同（智能体之间可以互相发送信号）
- [ ] 动态智能体选择（根据消息内容选择智能体）
- [ ] 智能体优先级（某些智能体在其他智能体之前响应）

## 另请参阅

- [多智能体配置](/tools/multi-agent-sandbox-tools)
- [路由配置](/channels/channel-routing)
- [会话管理](/concepts/session)