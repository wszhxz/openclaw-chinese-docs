---
summary: "Deep dive: session store + transcripts, lifecycle, and (auto)compaction internals"
read_when:
  - You need to debug session ids, transcript JSONL, or sessions.json fields
  - You are changing auto-compaction behavior or adding “pre-compaction” housekeeping
  - You want to implement memory flushes or silent system turns
title: "Session Management Deep Dive"
---
# 会话管理与压缩（深入解析）

本文详细说明 OpenClaw 如何端到端地管理会话：

- **会话路由**（入站消息如何映射到一个 `sessionKey`）
- **会话存储**（`sessions.json`）及其所追踪的内容
- **对话记录持久化**（`*.jsonl`）及其结构
- **对话记录卫生机制**（在运行前针对不同提供方所做的特定修复）
- **上下文限制**（上下文窗口 vs 已追踪的 token 数量）
- **压缩机制**（手动压缩 + 自动压缩），以及可在压缩前插入自定义逻辑的位置
- **静默式后台维护**（例如：不应向用户呈现输出的内存写入操作）

如需先了解更高层次的概览，请从以下文档开始：

- [/concepts/session](/concepts/session)
- [/concepts/compaction](/concepts/compaction)
- [/concepts/session-pruning](/concepts/session-pruning)
- [/reference/transcript-hygiene](/reference/transcript-hygiene)

---

## 真实性来源：网关（Gateway）

OpenClaw 的设计围绕一个单一的 **网关进程（Gateway process）**，该进程拥有全部会话状态。

- 各类 UI（macOS 应用、Web 控制界面、TUI）应向网关查询会话列表和 token 计数。
- 在远程模式下，会话文件位于远程主机上；“检查本地 Mac 文件”无法反映网关当前实际使用的数据。

---

## 两层持久化机制

OpenClaw 采用两层机制来持久化会话：

1. **会话存储（`sessions.json`）**
   - 键值映射：`sessionKey -> SessionEntry`
   - 数据量小、可变、安全（可编辑或删除条目）
   - 追踪会话元数据（当前会话 ID、最后活跃时间、开关设置、token 计数器等）

2. **对话记录（`<sessionId>.jsonl`）**
   - 仅追加（append-only）的树状结构对话记录（每条记录包含 `id` + `parentId`）
   - 存储实际对话内容 + 工具调用 + 压缩摘要
   - 用于为后续轮次重建模型上下文

---

## 磁盘上的存储路径

每个代理（agent）在网关主机上的路径如下：

- 存储目录：`~/.openclaw/agents/<agentId>/sessions/sessions.json`
- 对话记录目录：`~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Telegram 主题会话：`.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw 通过 `src/config/sessions.ts` 解析这些路径。

---

## 存储维护与磁盘控制

会话持久化具备自动维护控制机制（`session.maintenance`），适用于 `sessions.json` 和对话记录相关产物：

- `mode`：`warn`（默认）或 `enforce`
- `pruneAfter`：陈旧条目的年龄阈值（默认 `30d`）
- `maxEntries`：对 `sessions.json` 中条目数量的上限（默认 `500`）
- `rotateBytes`：当 `sessions.json` 超出大小限制时执行轮转（默认 `10mb`）
- `resetArchiveRetention`：`*.reset.<timestamp>` 对话记录归档的保留期限（默认与 `pruneAfter` 相同；`false` 将禁用清理）
- `maxDiskBytes`：可选的会话目录配额
- `highWaterBytes`：清理后的目标占用量（默认为 `80%` × `maxDiskBytes`）

磁盘配额清理的执行顺序（`mode: "enforce"`）如下：

1. 首先移除最旧的已归档或孤立的对话记录产物。
2. 若仍超出目标，则逐个驱逐最旧的会话条目及其对应的对话记录文件。
3. 持续执行，直至磁盘使用量降至 `highWaterBytes` 或更低。

在 `mode: "warn"` 模式下，OpenClaw 仅报告潜在的驱逐项，但不会修改存储或文件。

按需运行维护任务：

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## 定时任务会话与运行日志

独立的定时任务（cron）运行也会创建会话条目/对话记录，并配有专用的保留控制策略：

- `cron.sessionRetention`（默认 `24h`）将从会话存储（`false` 将禁用该功能）中清理过期的独立定时任务会话。
- `cron.runLog.maxBytes` + `cron.runLog.keepLines` 将清理 `~/.openclaw/cron/runs/<jobId>.jsonl` 文件（默认限制：`2_000_000` 字节和 `2000` 行）。

---

## 会话键（`sessionKey`）

一个 `sessionKey` 用于标识你当前所处的 _对话分桶_（用于路由与隔离）。

常见模式包括：

- 主会话/直接聊天（每个代理）：`agent:<agentId>:<mainKey>`（默认 `main`）
- 群组：`agent:<agentId>:<channel>:group:<id>`
- 房间/频道（Discord/Slack）：`agent:<agentId>:<channel>:channel:<id>` 或 `...:room:<id>`
- 定时任务：`cron:<job.id>`
- Webhook：`hook:<uuid>`（除非被显式覆盖）

权威的规范规则详见 [/concepts/session](/concepts/session)。

---

## 会话 ID（`sessionId`）

每个 `sessionKey` 指向一个当前有效的 `sessionId`（即延续该对话的对话记录文件）。

经验法则如下：

- **重置操作**（`/new`、`/reset`）将为该 `sessionKey` 创建一个新的 `sessionId`。
- **每日重置**（默认为网关主机本地时间凌晨 4:00）将在重置时间点之后收到的第一条消息触发创建一个新的 `sessionId`。
- **空闲超时**（`session.reset.idleMinutes` 或传统 `session.idleMinutes`）将在一条消息于空闲窗口期后到达时，创建一个新的 `sessionId`。若同时配置了每日重置与空闲超时，则以先到期者为准。
- **线程父会话分叉防护**（`session.parentForkMaxTokens`，默认 `100000`）：当父会话已过大时，跳过对其对话记录的分叉；新线程将从头开始。设为 `0` 可禁用此防护。

实现细节：该决策发生在 `initSessionState()` 中的 `src/auto-reply/reply/session.ts`。

---

## 会话存储结构（`sessions.json`）

存储中的值类型为 `SessionEntry`，定义于 `src/config/sessions.ts`。

关键字段（非完整列表）：

- `sessionId`：当前对话记录 ID（文件名由此派生，除非设置了 `sessionFile`）
- `updatedAt`：最后活跃时间戳
- `sessionFile`：可选的显式对话记录路径覆盖
- `chatType`：`direct | group | room`（辅助 UI 和发送策略）
- `provider`、`subject`、`room`、`space`、`displayName`：群组/频道标签相关的元数据
- 开关设置：
  - `thinkingLevel`、`verboseLevel`、`reasoningLevel`、`elevatedLevel`
  - `sendPolicy`（每会话级覆盖）
- 模型选择：
  - `providerOverride`、`modelOverride`、`authProfileOverride`
- Token 计数器（尽力而为 / 依赖提供方）：
  - `inputTokens`、`outputTokens`、`totalTokens`、`contextTokens`
- `compactionCount`：该会话键已完成自动压缩的次数
- `memoryFlushAt`：上次压缩前内存刷新的时间戳
- `memoryFlushCompactionCount`：上次刷新运行时的压缩计数

该存储允许安全编辑，但网关具有最终权威性：它可能在会话运行过程中重写或重新填充条目。

---

## 对话记录结构（`*.jsonl`）

对话记录由 `@mariozechner/pi-coding-agent` 的 `SessionManager` 进行管理。

文件格式为 JSONL：

- 第一行：会话头部（`type: "session"`，含 `id`、`cwd`、`timestamp`、可选的 `parentSession`）
- 其后：带 `id` + `parentId`（树状结构）的会话条目

值得注意的条目类型包括：

- `message`：用户 / 助理 / toolResult 消息
- `custom_message`：扩展程序注入的消息，_会_ 进入模型上下文（可在 UI 中隐藏）
- `custom`：扩展程序状态，_不_ 进入模型上下文
- `compaction`：已持久化的压缩摘要，含 `firstKeptEntryId` 和 `tokensBefore`
- `branch_summary`：在导航树分支时持久化的摘要

OpenClaw **有意不** “修正” 对话记录；网关使用 `SessionManager` 来读写它们。

---

## 上下文窗口 vs 已追踪 token 数量

两个不同概念至关重要：

1. **模型上下文窗口**：各模型的硬性上限（模型可见的 token 数量）
2. **会话存储计数器**：写入 `sessions.json` 的滚动统计信息（供 `/status` 和仪表板使用）

如需调整限制：

- 上下文窗口来自模型目录（可通过配置覆盖）。
- 存储中的 `contextTokens` 是运行时估算/上报值；请勿将其视为严格保证。

更多详情参见 [/token-use](/reference/token-use)。

---

## 压缩：其本质

压缩将较早的对话内容汇总为一条持久化的 `compaction` 条目存入对话记录，同时保持近期消息不变。

压缩完成后，后续轮次将看到：

- 压缩摘要
- `firstKeptEntryId` 之后的消息

压缩是 **持久性的**（不同于会话裁剪）。详见 [/concepts/session-pruning](/concepts/session-pruning)。

---

## 自动压缩触发时机（Pi 运行时）

在嵌入式 Pi 代理中，自动压缩在以下两种情形下触发：

1. **溢出恢复**：模型返回上下文溢出错误 → 执行压缩 → 重试。
2. **阈值维护**：一次成功轮次结束后，当满足以下条件时：

`contextTokens > contextWindow - reserveTokens`

其中：

- `contextWindow` 是模型的上下文窗口
- `reserveTokens` 是为提示词 + 下一轮模型输出预留的余量

这是 Pi 运行时语义（OpenClaw 消费这些事件，但由 Pi 决定何时压缩）。

---

## 压缩设置（`reserveTokens`、`keepRecentTokens`）

Pi 的压缩设置位于 Pi 设置中：

```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,
    keepRecentTokens: 20000,
  },
}
```

OpenClaw 还为嵌入式运行强制设定一个安全下限：

- 若 `compaction.reserveTokens < reserveTokensFloor`，OpenClaw 将提升该值。
- 默认下限为 `20000` 个 token。
- 设置 `agents.defaults.compaction.reserveTokensFloor: 0` 可禁用该下限。
- 若当前值已高于下限，OpenClaw 将保持原值不变。

原因：为多轮次“后台维护”（如内存写入）预留足够余量，避免压缩成为不可避免的操作。

实现位置：`ensurePiCompactionReserveTokens()`（位于 `src/agents/pi-settings.ts` 中）  
（由 `src/agents/pi-embedded-runner.ts` 调用）

---

## 用户可见界面

您可通过以下方式观察压缩及会话状态：

- `/status`（任意聊天会话中）
- `openclaw status`（CLI）
- `openclaw sessions` / `sessions --json`
- 详细模式：`🧹 Auto-compaction complete` + 压缩计数

---

## 静默式后台维护（`NO_REPLY`）

OpenClaw 支持“静默”轮次，用于执行用户不应看到中间输出的后台任务。

约定如下：

- 助理在其输出开头添加 `NO_REPLY`，表示“不向用户交付回复”。
- OpenClaw 在交付层中会剥离/抑制该标记。

截至 `2026.1.10`，OpenClaw 还会在部分数据块以 `NO_REPLY` 开头时，抑制 **草稿/输入流式传输（draft/typing streaming）**，从而避免静默操作在回合中途泄露部分输出。

---

## 预压缩“内存刷新”（已实现）

目标：在自动压缩发生前，执行一次静默的智能体回合，将持久化状态写入磁盘（例如，写入智能体工作区中的 `memory/YYYY-MM-DD.md`），确保压缩过程不会抹除关键上下文。

OpenClaw 采用 **阈值前刷新（pre-threshold flush）** 方式：

1. 监控会话上下文使用量。
2. 当其超过“软阈值”（低于 Pi 的压缩阈值）时，向智能体发出一条静默的“立即写入内存”指令。
3. 使用 `NO_REPLY`，确保用户无感知。

配置项（`agents.defaults.compaction.memoryFlush`）：

- `enabled`（默认值：`true`）
- `softThresholdTokens`（默认值：`4000`）
- `prompt`（用于刷新回合的用户消息）
- `systemPrompt`（附加于刷新回合的额外系统提示）

注意事项：

- 默认提示/系统提示中包含一个 `NO_REPLY` 提示，用于抑制内容投递。
- 每次压缩周期内仅执行一次刷新（由 `sessions.json` 跟踪）。
- 刷新仅针对嵌入式 Pi 会话运行（CLI 后端会跳过）。
- 若会话工作区为只读（`workspaceAccess: "ro"` 或 `"none"`），则跳过刷新。
- 有关工作区文件布局与写入模式，请参阅 [Memory](/concepts/memory)。

Pi 还在扩展 API 中暴露了一个 `session_before_compact` 钩子，但 OpenClaw 当前的刷新逻辑实现在网关侧。

---

## 故障排查清单

- 会话密钥错误？请从 [/concepts/session](/concepts/session) 入手，并确认 `sessionKey` 是否与 `/status` 中的一致。
- 存储与对话记录不匹配？请核对网关主机地址，以及来自 `openclaw status` 的存储路径。
- 压缩过于频繁？请检查：
  - 模型上下文窗口（过小）
  - 压缩设置（`reserveTokens` 设置过高，相对于模型窗口可能导致更早触发压缩）
  - 工具结果膨胀：启用或调整会话剪枝（session pruning）
- 静默回合出现泄露？请确认回复严格以 `NO_REPLY`（精确匹配该 token）开头，并确认所用构建版本已包含流式传输抑制修复。