---
summary: "Deep dive: session store + transcripts, lifecycle, and (auto)compaction internals"
read_when:
  - You need to debug session ids, transcript JSONL, or sessions.json fields
  - You are changing auto-compaction behavior or adding “pre-compaction” housekeeping
  - You want to implement memory flushes or silent system turns
title: "Session Management Deep Dive"
---
# 会话管理与压缩（深入解析）

本文档解释了OpenClaw如何端到端管理会话：

- **会话路由**（入站消息如何映射到`sessionKey`）
- **会话存储**（`sessions.json`）及其跟踪内容
- **会话记录持久化**（`*.jsonl`）及其结构
- **会话卫生**（运行前的提供者特定修复）
- **上下文限制**（上下文窗口与跟踪令牌）
- **压缩**（手动 + 自动压缩）及预压缩工作挂钩位置
- **静默维护**（例如不应产生用户可见输出的内存写入）

如果您希望先获得更高层次的概述，请从以下内容开始：

- [/concepts/session](/concepts/session)
- [/concepts/compaction](/concepts/compaction)
- [/concepts/session-pruning](/concepts/session-pruning)
- [/reference/transcript-hygiene](/reference/transcript-hygiene)

---

## 真相来源：网关

OpenClaw围绕一个单一的**网关进程**设计，该进程拥有会话状态。

- UI（macOS应用、网页控制UI、TUI）应查询网关以获取会话列表和令牌计数。
- 在远程模式下，会话文件位于远程主机上；“检查您的本地Mac文件”不会反映网关正在使用的数据。

---

## 两层持久化

OpenClaw在两个层级持久化会话：

1. **会话存储**（`sessions.json`）
   - 键值映射：`sessionKey -> SessionEntry`
   - 小型、可变、可安全编辑（或删除条目）
   - 跟踪会话元数据（当前会话ID、最后活动时间、开关、令牌计数器等）

2. **会话记录**（`<sessionId>.jsonl`）
   - 仅追加的树结构记录（条目具有`id` + `parentId`）
   - 存储实际对话 + 工具调用 + 压缩摘要
   - 用于未来回合重建模型上下文

---

## 磁盘位置

每个代理，在网关主机上：

- 存储：`~/.openclaw/agents/<agentId>/sessions/sessions.json`
- 会话记录：`~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Telegram主题会话：`.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw通过`src/config/sessions.ts`解析这些路径。

---

## 会话键（`sessionKey`）

`sessionKey`标识您所在的_对话桶_（路由 + 隔离）。

常见模式：

- 主/直接聊天（每代理）：`agent:<agentId>:<mainKey>`（默认`main`）
- 群组：`agent:<agentId>:<channel>:group:<id>`
- 房间/频道（Discord/Slack）：`agent:<agentId>:<channel>:channel:<id>` 或 `...:room:<id>`
- 定时任务：`cron:<job.id>`
- Webhook：`hook:<uuid>`（除非被覆盖）

规范规则文档位于[/concepts/session](/concepts/session)。

---

## 会话ID（`sessionId`）

每个`sessionKey`指向当前的`sessionId`（继续对话的会话记录文件）。

经验法则：

- **重置**（`/new`, `/reset`）为该`sessionKey`创建新的`sessionId`。
- **每日重置**（默认网关主机本地时间凌晨4:00）在重置边界后的下一条消息创建新的`sessionId`。
- **空闲过期**（`session.reset.idleMinutes`或旧版`session.idleMinutes`）在空闲窗口后收到消息时创建新的`sessionId`。当每日和空闲都配置时，先过期的生效。

实现细节：决策发生在`src/auto-reply/reply/session.ts`中的`initSessionState()`。

---

## 会话存储架构（`sessions.json`）

存储的值类型是`SessionEntry`，定义于`src/config/sessions.ts`。

关键字段（不完全）：

- `sessionId`：当前会话记录ID（文件名由此推导，除非设置了`sessionFile`）
- `updatedAt`：最后活动时间戳
- `sessionFile`：可选的显式会话记录路径覆盖
- `chatType`：`direct | group | room`（帮助UI和发送策略）
- `provider`、`subject`、`room`、`space`、`displayName`：群组/频道标签的元数据
- 开关：
  - `thinkingLevel`、`verboseLevel`、`reasoningLevel`、`elevatedLevel`
- `prompt`：刷新回合的用户消息
- `systemPrompt`：附加到刷新回合的额外系统提示

注释：

- 默认提示/系统提示包含`NO_REPLY`提示以抑制发送。
- 刷新每轮压缩执行一次（记录在`sessions.json`）。
- 刷新仅适用于嵌入式Pi会话（CLI后端跳过）。
- 当会话工作区为只读时（`workspaceAccess: "ro"`或`"none"`）跳过刷新。
- 工作区文件布局和写入模式请参见[内存](/concepts/memory)。

Pi还通过扩展API暴露了`session_before_compact`钩子，但OpenClaw的刷新逻辑目前在网关端运行。

---

## 故障排查清单

- 会话键错误？从[/concepts/session](/concepts/session)开始并确认`/status`中的`sessionKey`。
- 存储与会话记录不匹配？确认网关主机和从`openclaw status`获取的存储路径。
- 压缩日志过多？检查：
  - 模型上下文窗口（太小）
  - 压缩设置（`reserveTokens`相对于模型窗口过高可能导致更早压缩）
  - 工具结果膨胀：启用/调整会话修剪
- 静默回合泄露？确认回复以`NO_REPLY`（精确令牌）开头且您使用包含流式传输抑制修复的构建。