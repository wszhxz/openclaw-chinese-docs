---
summary: "Broadcast a WhatsApp message to multiple agents"
read_when:
  - Configuring broadcast groups
  - Debugging multi-agent replies in WhatsApp
status: experimental
title: "Broadcast Groups"
---
# 广播组

**状态：** 实验性功能  
**版本：** 2026.1.9 中新增

## 概述

广播组允许多个代理同时处理和响应同一条消息。这使您能够创建专门的代理团队，在单个 WhatsApp 群组或私信中协同工作——全部使用一个电话号码。

当前范围：**仅 WhatsApp**（网页渠道）。

广播组在渠道白名单和群组激活规则之后进行评估。在 WhatsApp 群组中，这意味着当 OpenClaw 正常回复时（例如：提及，取决于您的群组设置），广播就会发生。

## 使用场景

### 1. 专业化代理团队

部署具有原子化、专注职责的多个代理：

```yaml
broadcast_groups:
  "group-id@chat.whatsapp.com":
    - name: "sales-agent"
      strategy: parallel
    - name: "support-agent" 
      strategy: parallel
    - name: "moderation-agent"
      strategy: parallel
```

每个代理处理相同的消息并提供其专业视角。

### 2. 多语言支持

```yaml
broadcast_groups:
  "group-id@chat.whatsapp.com":
    - name: "english-agent"
    - name: "spanish-agent"
    - name: "french-agent"
```

### 3. 质量保证工作流程

```yaml
broadcast_groups:
  "group-id@chat.whatsapp.com":
    - name: "primary-agent"
    - name: "qa-monitoring-agent"  # 监控和记录
    - name: "compliance-agent"     # 合规检查
```

### 4. 任务自动化

```yaml
broadcast_groups:
  "group-id@chat.whatsapp.com":
    - name: "main-agent"
    - name: "ticket-creator-agent"   # 创建工单
    - name: "analytics-agent"        # 分析跟踪
```

## 配置

### 基础设置

添加顶级 `broadcast_groups` 部分（与 `agents` 并列）。键是 WhatsApp 对等方 ID：

- 群聊：群组 JID（例如 `group-id@chat.whatsapp.com`）
- 私信：E.164 电话号码（例如 `+1234567890@s.whatsapp.net`）

```yaml
agents:
  - name: "sales-agent"
    # ... agent config
  - name: "support-agent" 
    # ... agent config
  - name: "moderation-agent"
    # ... agent config

broadcast_groups:
  "group-id@chat.whatsapp.com":
    - name: "sales-agent"
    - name: "support-agent"
    - name: "moderation-agent"
```

**结果：** 当 OpenClaw 在此聊天中回复时，它将运行所有三个代理。

### 处理策略

控制代理如何处理消息：

#### 并行（默认）

所有代理同时处理：

```yaml
broadcast_groups:
  "group-id@chat.whatsapp.com":
    strategy: parallel  # default
    agents:
      - name: "agent1"
      - name: "agent2"
```

#### 顺序

代理按顺序处理（一个等待前一个完成）：

```yaml
broadcast_groups:
  "group-id@chat.whatsapp.com":
    strategy: sequential
    agents:
      - name: "validation-agent"
      - name: "processing-agent"
      - name: "confirmation-agent"
```

### 完整示例

```yaml
BROADCAST_GROUPS:
  "whatsapp:group:123456789": 
    - alfred
    - bärbel
```

## 工作原理

### 消息流程

1. **传入消息** 在 WhatsApp 群组中到达
2. **广播检查**：系统检查对等 ID 是否在 `broadcast` 中
3. **如果在广播列表中**：
   - 所有列出的代理处理消息
   - 每个代理都有自己的会话密钥和隔离上下文
   - 代理并行（默认）或顺序处理
4. **如果不在广播列表中**：
   - 应用正常路由（第一个匹配的绑定）

注意：广播群组不会绕过频道白名单或群组激活规则（提及/命令等）。它们只改变消息符合处理条件时运行的代理。

### 会话隔离

广播群组中的每个代理维护完全独立的：

- **会话密钥**（`agent:alfred:whatsapp:group:120363...` vs `agent:baerbel:whatsapp:group:120363...`）
- **对话历史**（代理看不到其他代理的消息）
- **工作区**（如果配置了单独的沙箱）
- **工具访问权限**（不同的允许/拒绝列表）
- **内存/上下文**（单独的 IDENTITY.md、SOUL.md 等）
- **群组上下文缓冲区**（用于上下文的最近群组消息）按对等方共享，因此所有广播代理在触发时看到相同的上下文

这允许每个代理具有：

- 不同的个性
- 不同的工具访问权限（例如，只读与读写）
- 不同的模型（例如，opus 与 sonnet）
- 不同的已安装技能

### 示例：隔离会话

在群组 `120363403215116621@g.us` 中使用代理 `["alfred", "baerbel"]`：

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

### 1. 保持代理专注

为每个代理设计单一、明确的职责：

```json
{
  "broadcast": {
    "DEV_GROUP": ["formatter", "linter", "tester"]
  }
}
```

✅ **良好：** 每个代理有一个任务  
❌ **不良：** 一个通用的"开发助手"代理

### 2. 使用描述性名称

明确每个代理的作用：

```
agents:
  code_reviewer:
    name: "Code Review Assistant"
    model: claude-3-haiku
    prompt: "Review code for best practices..."
  
  bug_finder:
    name: "Bug Detection Specialist" 
    model: claude-3-sonnet
    prompt: "Find potential bugs and issues..."
```

### 3. 配置不同的工具访问权限

只为代理提供它们需要的工具：

```
agents:
  researcher:
    tools: [web_search, calculator]
    # No code execution needed
    
  developer:
    tools: [code_interpreter, file_manager]
    # No web access needed
```

### 4. 监控性能

对于多个代理，请考虑：

- 使用 `round_robin`（默认）以提高速度
- 将广播组限制为 5-10 个代理
- 为简单代理使用更快的模型

### 5. 优雅处理故障

代理独立失败。一个代理的错误不会阻止其他代理：

```
# 如果 agent1 失败，agent2 仍会响应
broadcast_groups:
  support_team:
    - agent1  # 可能失败
    - agent2  # 仍然工作
    - agent3  # 仍然工作
```

## 兼容性

### 提供商

广播组目前支持：

- ✅ WhatsApp（已实现）
- 🚧 Telegram（计划中）
- 🚧 Discord（计划中）
- 🚧 Slack（计划中）

### 路由

广播组与现有路由一起工作：

```
routing:
  bindings:
    - peer_id: "alfred"
      agent_id: "main_assistant"
  
  broadcast_groups:
    - peer_id: "team_123"
      agent_ids: ["agent1", "agent2"]
```

- `@alfred`: 只有 alfred 响应（正常路由）
- `@team_123`: agent1 和 agent2 都响应（广播）

**优先级：** `broadcast_groups` 优先于 `bindings`。

## 故障排除

### 代理不响应

**检查：**

1. 代理 ID 在 `agents` 中存在
2. 对等 ID 格式正确（例如，`whatsapp:1234567890`）
3. 代理不在拒绝列表中

**调试：**

```
# 启用详细日志
LOG_LEVEL=DEBUG
smb sandbox run
```

### 只有一个代理响应

**原因：** 对等 ID 可能在 `bindings` 中但不在 `broadcast_groups` 中。

**修复：** 添加到广播配置或从绑定中移除。

### 性能问题

**如果代理数量多导致缓慢：**

- 减少每组中的代理数量
- 使用更轻量的模型（sonnet 而不是 opus）
- 检查沙箱启动时间

## 示例

### 示例 1：代码审查团队

```
broadcast_groups:
  code_review:
    - senior_developer
    - security_specialist
    - testing_expert

agents:
  senior_developer:
    name: "Senior Dev Reviewer"
    model: claude-3-sonnet
    prompt: "Review code quality, architecture, and best practices..."
    
  security_specialist:
    name: "Security Auditor"
    model: claude-3-sonnet  
    prompt: "Audit for security vulnerabilities and compliance..."
    
  testing_expert:
    name: "Testing Advisor"
    model: claude-3-haiku
    prompt: "Suggest test cases and review test coverage..."
```

**用户发送：** 代码片段  
**响应：**

- code-formatter: "修复了缩进并添加了类型提示"
- security-scanner: "⚠️ 第12行存在SQL注入漏洞"
- test-coverage: "覆盖率是45%，缺少错误情况的测试"
- docs-checker: "函数 `process_data` 缺少文档字符串"

### 示例2：多语言支持

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

## API参考

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

- `strategy` (可选): 如何处理代理
  - `"parallel"` (默认): 所有代理同时处理
  - `"sequential"`: 代理按数组顺序处理
- `[peerId]`: WhatsApp群组JID、E.164号码或其他对等ID
  - 值: 应该处理消息的代理ID数组

## 限制

1. **最大代理数：** 没有硬性限制，但10个以上代理可能会很慢
2. **共享上下文：** 代理看不到彼此的响应（按设计）
3. **消息排序：** 并行响应可能以任意顺序到达
4. **速率限制：** 所有代理都计入WhatsApp速率限制

## 未来增强功能

计划功能：

- [ ] 共享上下文模式（代理可以看到彼此的响应）
- [ ] 代理协调（代理可以相互发送信号）
- [ ] 动态代理选择（根据消息内容选择代理）
- [ ] 代理优先级（某些代理在其他代理之前响应）

## 参见

- [多代理配置](/multi-agent-sandbox-tools)
- [路由配置](/concepts/channel-routing)
- [会话管理](/concepts/sessions)