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
**版本：** 2026.1.9 版本中新增

## 概述

广播组支持多个智能体（agent）同时处理并响应同一条消息。这使您能够创建专业化协作的智能体团队，共同在同一个 WhatsApp 群组或私聊（DM）中工作——全部共用一个手机号。

当前适用范围：**仅限 WhatsApp**（网页渠道）。

广播组的评估发生在渠道白名单和群组激活规则之后。在 WhatsApp 群组中，这意味着广播行为会在 OpenClaw 原本会回复时触发（例如：被提及，具体取决于您的群组设置）。

## 使用场景

### 1. 专业化智能体团队

部署多个职责单一、高度聚焦的智能体：

```
Group: "Development Team"
Agents:
  - CodeReviewer (reviews code snippets)
  - DocumentationBot (generates docs)
  - SecurityAuditor (checks for vulnerabilities)
  - TestGenerator (suggests test cases)
```

每个智能体处理同一条消息，并提供其专业视角的响应。

### 2. 多语言支持

```
Group: "International Support"
Agents:
  - Agent_EN (responds in English)
  - Agent_DE (responds in German)
  - Agent_ES (responds in Spanish)
```

### 3. 质量保障工作流

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

### 基础设置

在配置顶层添加一个 `broadcast` 区块（与 `bindings` 并列）。键（keys）为 WhatsApp 对等端 ID（peer IDs）：

- 群聊：群组 JID（例如 `120363403215116621@g.us`）  
- 私聊（DM）：E.164 格式电话号码（例如 `+15551234567`）

```json
{
  "broadcast": {
    "120363403215116621@g.us": ["alfred", "baerbel", "assistant3"]
  }
}
```

**效果：** 当 OpenClaw 在该聊天中本应回复时，将同时运行全部三个智能体。

### 处理策略

控制智能体处理消息的方式：

#### 并行处理（默认）

所有智能体同时处理：

```json
{
  "broadcast": {
    "strategy": "parallel",
    "120363403215116621@g.us": ["alfred", "baerbel"]
  }
}
```

#### 串行处理

智能体按顺序依次处理（后一个等待前一个完成）：

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

### 消息流向

1. **入站消息** 进入 WhatsApp 群组  
2. **广播检查：** 系统检查对等端 ID 是否存在于 `broadcast` 中  
3. **若在广播列表中：**  
   - 所有列出的智能体均处理该消息  
   - 每个智能体拥有独立的会话密钥（session key）和隔离的上下文（isolated context）  
   - 智能体以并行（默认）或串行方式处理  
4. **若不在广播列表中：**  
   - 启用常规路由逻辑（匹配首个符合条件的绑定）

注意：广播组**不会绕过**渠道白名单或群组激活规则（如提及、指令等），它仅在消息已满足处理条件的前提下，改变**实际参与处理的智能体集合**。

### 会话隔离

广播组中的每个智能体完全独立维护以下各项：

- **会话密钥**（`agent:alfred:whatsapp:group:120363...` 与 `agent:baerbel:whatsapp:group:120363...` 相互隔离）  
- **对话历史**（各智能体无法看到其他智能体发出的消息）  
- **工作区**（若已配置沙箱，则彼此隔离）  
- **工具访问权限**（允许/禁止列表各不相同）  
- **记忆/上下文**（各自独立的 `IDENTITY.md`、`SOUL.md` 等文件）  
- **群组上下文缓冲区**（用于构建上下文的近期群消息）按对等端（peer）共享，因此所有广播智能体在被触发时看到的是**相同的上下文**

这使得每个智能体可具备：

- 不同的人格设定  
- 不同的工具访问权限（例如：只读 vs. 读写）  
- 不同的大模型（例如：opus vs. sonnet）  
- 不同的已安装技能  

### 示例：隔离的会话

在群组 `120363403215116621@g.us` 中，配置了智能体 `["alfred", "baerbel"]`：

**Alfred 的上下文：**

```
Session: agent:alfred:whatsapp:group:120363403215116621@g.us
History: [user message, alfred's previous responses]
Workspace: /Users/pascal/openclaw-alfred/
Tools: read, write, exec
```

**Bärbel 的上下文：**

```
Session: agent:baerbel:whatsapp:group:120363403215116621@g.us
History: [user message, baerbel's previous responses]
Workspace: /Users/pascal/openclaw-baerbel/
Tools: read only
```

## 最佳实践

### 1. 保持智能体职责聚焦

为每个智能体设计单一、明确的职责：

```json
{
  "broadcast": {
    "DEV_GROUP": ["formatter", "linter", "tester"]
  }
}
```

✅ **良好实践：** 每个智能体只承担一项任务  
❌ **不良实践：** 单一泛化的“开发助手”智能体

### 2. 使用描述性名称

清晰表明每个智能体的功能：

```json
{
  "agents": {
    "security-scanner": { "name": "Security Scanner" },
    "code-formatter": { "name": "Code Formatter" },
    "test-generator": { "name": "Test Generator" }
  }
}
```

### 3. 配置差异化的工具访问权限

仅授予智能体所需的工具权限：

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

### 4. 监控性能表现

当启用大量智能体时，请考虑：

- 使用 `"strategy": "parallel"`（默认）以提升速度  
- 将单个广播组中的智能体数量限制在 5–10 个以内  
- 为较简单的智能体选用响应更快的模型  

### 5. 妥善处理失败情形

各智能体失败相互独立；任一智能体出错**不会阻塞**其余智能体：

```
Message → [Agent A ✓, Agent B ✗ error, Agent C ✓]
Result: Agent A and C respond, Agent B logs error
```

## 兼容性

### 支持的渠道提供商

广播组当前支持：

- ✅ WhatsApp（已实现）  
- 🚧 Telegram（规划中）  
- 🚧 Discord（规划中）  
- 🚧 Slack（规划中）

### 路由机制

广播组与现有路由机制协同工作：

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

- `GROUP_A`：仅 alfred 响应（常规路由）  
- `GROUP_B`：agent1 和 agent2 同时响应（广播）

**优先级规则：** `broadcast` 优先于 `bindings`。

## 故障排查

### 智能体未响应

**请检查：**

1. 智能体 ID 是否存在于 `agents.list` 中  
2. 对等端 ID 格式是否正确（例如：`120363403215116621@g.us`）  
3. 智能体是否位于拒绝列表（deny lists）中  

**调试方法：**

```bash
tail -f ~/.openclaw/logs/gateway.log | grep broadcast
```

### 仅有一个智能体响应

**原因：** 对等端 ID 可能存在于 `bindings` 中，但未列入 `broadcast`。

**解决方法：** 将其添加至广播配置，或从绑定（bindings）中移除。

### 性能问题

**若因智能体数量过多导致响应缓慢：**

- 减少每组中的智能体数量  
- 使用更轻量级的模型（例如：sonnet 替代 opus）  
- 检查沙箱启动耗时  

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

**用户发送：** 一段代码片段  
**响应内容：**

- code-formatter：“已修正缩进，并添加类型提示”  
- security-scanner：“⚠️ 第 12 行存在 SQL 注入漏洞”  
- test-coverage：“测试覆盖率仅为 45%，缺少针对错误情况的测试”  
- docs-checker：“函数 `process_data` 缺少文档字符串（docstring）”

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

### 配置模式（Schema）

```typescript
interface OpenClawConfig {
  broadcast?: {
    strategy?: "parallel" | "sequential";
    [peerId: string]: string[];
  };
}
```

### 字段说明

- `strategy`（可选）：指定智能体处理方式  
  - `"parallel"`（默认）：所有智能体并行处理  
  - `"sequential"`：智能体按数组顺序串行处理  
- `[peerId]`：WhatsApp 群组 JID、E.164 电话号码或其他对等端 ID  
  - 值：需处理消息的智能体 ID 数组  

## 局限性

1. **智能体数量上限：** 无硬性限制，但超过 10 个智能体可能导致响应变慢  
2. **上下文共享限制：** 智能体之间**无法看到彼此的响应**（此为设计使然）  
3. **消息响应顺序：** 并行响应可能以任意顺序抵达  
4. **速率限制：** 所有智能体的调用均计入 WhatsApp 的速率限制配额  

## 后续增强计划

已规划的功能：

- [ ] 共享上下文模式（代理可以看到彼此的响应）  
- [ ] 代理协调（代理可以相互发送信号）  
- [ ] 动态代理选择（根据消息内容选择代理）  
- [ ] 代理优先级（某些代理优先于其他代理进行响应）  

## 另请参阅  

- [多代理配置](/tools/multi-agent-sandbox-tools)  
- [路由配置](/channels/channel-routing)  
- [会话管理](/concepts/session)