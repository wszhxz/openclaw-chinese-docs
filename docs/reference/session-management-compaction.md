---
summary: "Deep dive: session store + transcripts, lifecycle, and (auto)compaction internals"
read_when:
  - You need to debug session ids, transcript JSONL, or sessions.json fields
  - You are changing auto-compaction behavior or adding “pre-compaction” housekeeping
  - You want to implement memory flushes or silent system turns
title: "Session Management Deep Dive"
---
# 会话管理与压缩（深度解析）

本文档解释了 OpenClaw 如何端到端管理会话：

- **会话路由**（入站消息如何映射到 `sessionKey`）
- **会话存储**（`sessions.json`）及其跟踪内容
- **对话记录持久化**（`*.jsonl`）及其结构
- **对话记录整理**（运行前的提供者特定修复）
- **上下文限制**（上下文窗口与跟踪的令牌）
- **压缩**（手动 + 自动压缩）以及在哪里挂钩压缩前工作
- **静默维护**（例如不应产生用户可见输出的内存写入）

如果您想先了解更高级别的概述，请从以下开始：

- [/concepts/session](/concepts/session)
- [/concepts/compaction](/concepts/compaction)
- [/concepts/session-pruning](/concepts/session-pruning)
- [/reference/transcript-hygiene](/reference/transcript-hygiene)

---

## 真实来源：网关

OpenClaw 围绕一个拥有会话状态的单一 **Gateway 进程** 设计。

- UI（macOS 应用、Web 控制 UI、TUI）应查询网关以获取会话列表和令牌计数。
- 在远程模式下，会话文件位于远程主机上；"检查您的本地 Mac 文件"不会反映网关正在使用的内容。

---

## 两个持久化层

OpenClaw 在两个层中持久化会话：

1. **会话存储（`sessions.json`）**
   - 键/值映射：`sessionKey -> SessionEntry`
   - 小巧、可变、编辑安全（或删除条目）
   - 跟踪会话元数据（当前会话 ID、最后活动时间、切换、令牌计数器等）

2. **对话记录（`<sessionId>.jsonl`）**
   - 具有树结构的仅追加对话记录（条目具有 `id` + `parentId`）
   - 存储实际对话 + 工具调用 + 压缩摘要
   - 用于重建模型上下文以供后续回合使用

---

## 磁盘位置

每个代理，在网关主机上：

- 存储：`~/.openclaw/agents/<agentId>/sessions/sessions.json`
- 对话记录：`~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Telegram 主题会话：`.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw 通过 `src/config/sessions.ts` 解析这些。

---

## 会话键（`sessionKey`）

`sessionKey` 标识您所在的 _哪个对话桶_（路由 + 隔离）。

常见模式：

- 主/直接聊天（每个代理）：`agent:<agentId>:<mainKey>`（默认 `main`）
- 群组：`agent:<agentId>:<channel>:group:<id>`
- 房间/频道（Discord/Slack）：`agent:<agentId>:<channel>:channel:<id>` 或 `...:room:<id>`
- 定时任务：`cron:<job.id>`
- Webhook：`hook:<uuid>`（除非被覆盖）

规范规则记录在 [/concepts/session](/concepts/session)。

---

## 会话 ID（`sessionId`）

每个 `sessionKey` 指向当前的 `sessionId`（继续对话的对话记录文件）。

经验法则：

- **重置**（`/new`，`/reset`）为该`sessionKey`创建一个新的`sessionId`。
- **每日重置**（默认在网关主机上的本地时间凌晨4:00）在重置边界后的下一条消息上创建一个新的`sessionId`。
- **空闲过期**（`session.reset.idleMinutes`或旧版`session.idleMinutes`）在消息在空闲窗口后到达时创建一个新的`sessionId`。当每日重置+空闲过期都配置时，先过期的生效。

实现细节：决策发生在`src/auto-reply/reply/session.ts`中的`initSessionState()`。

---

## 会话存储模式（`sessions.json`）

存储的值类型是`src/config/sessions.ts`中的`SessionEntry`。

键字段（非详尽）：

- `sessionId`：当前转录ID（文件名由此派生，除非设置了`sessionFile`）
- `updatedAt`：最后活动时间戳
- `sessionFile`：可选的显式转录路径覆盖
- `chatType`：`direct | group | room`（帮助UI和发送策略）
- `provider`、`subject`、`room`、`space`、`displayName`：用于群组/频道标签的元数据
- 开关：
  - `thinkingLevel`、`verboseLevel`、`reasoningLevel`、`elevatedLevel`
  - `sendPolicy`（每会话覆盖）
- 模型选择：
  - `providerOverride`、`modelOverride`、`authProfileOverride`
- 令牌计数器（尽力而为/提供者相关）：
  - `inputTokens`、`outputTokens`、`totalTokens`、`contextTokens`
- `compactionCount`：此会话键的自动压缩完成频率
- `memoryFlushAt`：上次预压缩内存刷新的时间戳
- `memoryFlushCompactionCount`：上次刷新运行时的压缩计数

存储可以安全编辑，但网关是权威：它可能会在会话运行时重写或重新填充条目。

---

## 转录结构（`*.jsonl`）

转录由`@mariozechner/pi-coding-agent`的`SessionManager`管理。

文件是JSONL：

- 第一行：会话头（`type: "session"`，包含`id`、`cwd`、`timestamp`，可选的`parentSession`）
- 然后：带有`id` + `parentId`（树）的会话条目

值得注意的条目类型：

- `message`：用户/助手/工具结果消息
- `custom_message`：扩展注入的消息，_会_进入模型上下文（可以从UI隐藏）
- `custom`：扩展状态，_不会_进入模型上下文
- `compaction`：持久化的压缩摘要，带有`firstKeptEntryId`和`tokensBefore`
- `branch_summary`：导航树分支时的持久化摘要

OpenClaw故意**不**"修复"转录；网关使用`SessionManager`来读写它们。

---

## 上下文窗口与跟踪令牌

两个不同的概念很重要：

1. **模型上下文窗口**：每个模型的硬限制（模型可见的令牌）
2. **会话存储计数器**：滚动统计信息写入到`sessions.json`（用于/status和仪表板）

如果您正在调整限制：

- 上下文窗口来自模型目录（可通过配置覆盖）。
- 存储中的 `context_window` 是运行时估计/报告值；不要将其视为严格的保证。

更多信息，请参见 [/token-use](/token-use)。

---

## 压缩：它的含义

压缩将较旧的对话总结为 transcript 中持久化的 `compacted_summary` 条目，并保持最近的消息完整。

压缩后，未来的对话回合会看到：

- 压缩摘要
- `compaction_point` 之后的消息

压缩是**持久性**的（与会话修剪不同）。参见 [/concepts/session-pruning](/concepts/session-pruning)。

---

## 自动压缩发生时机（Pi 运行时）

在嵌入式 Pi 代理中，自动压缩在两种情况下触发：

1. **溢出恢复**：模型返回上下文溢出错误 → 压缩 → 重试。
2. **阈值维护**：成功回合后，当：

```
(context_window - headroom) * threshold_fraction <= occupied_tokens
```

其中：

- `context_window` 是模型的上下文窗口
- `headroom` 是为提示 + 下一个模型输出预留的空间

这些是 Pi 运行时语义（OpenClaw 消费事件，但由 Pi 决定何时压缩）。

---

## 压缩设置 (`compaction_threshold`, `compaction_headroom`)

Pi 的压缩设置位于 Pi 设置中：

```
compaction:
  threshold_fraction: 0.75
  headroom: 1024
```

OpenClaw 还为嵌入式运行强制执行安全下限：

- 如果 `headroom < MIN_HEADROOM`，OpenClaw 会提升它。
- 默认下限为 `512` 个 token。
- 设置 `disable_headroom_floor = true` 以禁用下限。
- 如果它已经更高，OpenClaw 不会更改它。

原因：在压缩变得不可避免之前，为多轮"管理任务"（如内存写入）留出足够的空间。

实现：`compact()` 在 `pi_runtime.py` 中
（从 `handle_overflow()` 调用）。

---

## 用户可见界面

您可以通过以下方式观察压缩和会话状态：

- `/session` （在任何聊天会话中）
- `--verbose` （CLI）
- `session_state` / `compaction_count`
- 详细模式：`occupied_tokens` + 压缩计数

---

## 静默管理任务 (`SILENT_TURN`)

OpenClaw 支持"静默"回合，用于后台任务，用户不应看到中间输出。

约定：

- 助手在其输出开头使用 `SILENT_TURN` 来表示"不要向用户发送回复"。
- OpenClaw 在交付层剥离/抑制此标记。

自 `v0.3.0` 起，当部分块以 `SILENT_TURN` 开头时，OpenClaw 还会抑制**草稿/输入流**，因此静默操作不会在回合中途泄露部分输出。

---

## 压缩前"内存刷新"（已实现）

目标：在自动压缩发生之前，运行一个静默的代理回合，将持久状态写入磁盘（例如代理工作区中的 `memory.json`），这样压缩就不会擦除关键上下文。

OpenClaw 使用**预阈值刷新**方法：

1. 监控会话上下文使用情况。
2. 当超过"软阈值"（低于 Pi 的压缩阈值）时，向代理运行静默的
   "立即写入内存"指令。
3. 使用 `NO_REPLY` 因此用户看不到任何内容。

配置 (`agents.defaults.compaction.memoryFlush`):

- `enabled` （默认值：`true`）
- `softThresholdTokens` （默认值：`4000`）
- `prompt` （刷新回合的用户消息）
- `systemPrompt` （刷新回合附加的额外系统提示）

注意事项：

- 默认提示/系统提示包含一个 `NO_REPLY` 提示来抑制传递。
- 刷新在每个压缩周期运行一次（在 `sessions.json` 中跟踪）。
- 刷新仅针对嵌入式 Pi 会话运行（CLI 后端跳过它）。
- 当会话工作区为只读时跳过刷新（`workspaceAccess: "ro"` 或 `"none"`）。
- 关于工作区文件布局和写入模式，请参见 [Memory](/concepts/memory)。

Pi 还在扩展 API 中公开了一个 `session_before_compact` 钩子，但 OpenClaw 的
刷新逻辑目前位于网关端。

---

## 故障排除检查清单

- 会话密钥错误？从 [/concepts/session](/concepts/session) 开始，确认 `/status` 中的 `sessionKey`。
- 存储与转录不匹配？确认来自 `openclaw status` 的网关主机和存储路径。
- 压缩垃圾信息？检查：
  - 模型上下文窗口（太小）
  - 压缩设置（对于模型窗口来说 `reserveTokens` 太高可能导致更早的压缩）
  - 工具结果膨胀：启用/调整会话修剪
- 静默回合泄漏？确认回复以 `NO_REPLY` 开头（确切的令牌），并且您使用的构建包含流抑制修复。