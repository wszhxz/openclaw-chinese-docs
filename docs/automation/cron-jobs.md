---
summary: "Cron jobs + wakeups for the Gateway scheduler"
read_when:
  - Scheduling background jobs or wakeups
  - Wiring automation that should run with or alongside heartbeats
  - Deciding between heartbeat and cron for scheduled tasks
title: "Cron Jobs"
---
# Cron 任务（Gateway 调度器）

> **Cron 与 Heartbeat？** 参见 [Cron vs Heartbeat](/automation/cron-vs-heartbeat) 以获取何时使用两者的指导。

Cron 是 Gateway 内置的调度器。它持久化任务，在正确时间唤醒 Agent，并可选择将输出回传至聊天。

如果您想要 _“run this every morning”_ 或 _“poke the agent in 20 minutes”_，cron 就是该机制。

故障排查：[/automation/troubleshooting](/automation/troubleshooting)

## 简而言之

- Cron 在 **Gateway 内部** 运行（不在模型内部）。
- 任务在 `~/.openclaw/cron/` 下持久化，因此重启不会丢失计划。
- 两种执行样式：
  - **主会话**：入队系统事件，然后在下一个 heartbeat 运行。
  - **隔离**：在 `cron:<jobId>` 中运行专用的 agent 回合，带有交付（默认 announce 或无）。
- 唤醒是一等公民：任务可以请求“立即唤醒”vs“下一个 heartbeat”。
- Webhook 发布针对每个任务，通过 `delivery.mode = "webhook"` + `delivery.to = "<url>"`。
- 对于设置了 `cron.webhook` 且存储了 `notify: true` 的任务，保留遗留回退方案，将这些任务迁移到 webhook 交付模式。

## 快速开始（可操作）

创建一次性提醒，验证其存在，并立即运行：

```bash
openclaw cron add \
  --name "Reminder" \
  --at "2026-02-01T16:00:00Z" \
  --session main \
  --system-event "Reminder: check the cron docs draft" \
  --wake now \
  --delete-after-run

openclaw cron list
openclaw cron run <job-id>
openclaw cron runs --id <job-id>
```

安排一个带交付的重复隔离任务：

```bash
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize overnight updates." \
  --announce \
  --channel slack \
  --to "channel:C1234567890"
```

## 工具调用等效项（Gateway cron 工具）

有关标准的 JSON 形状和示例，请参见 [JSON schema for tool calls](/automation/cron-jobs#json-schema-for-tool-calls)。

## Cron 任务存储位置

Cron 任务默认持久化在 Gateway 主机上的 `~/.openclaw/cron/jobs.json`。Gateway 将文件加载到内存中，并在更改时写回，因此仅在 Gateway 停止时手动编辑才是安全的。优先使用 `openclaw cron add/edit` 或 cron 工具调用 API 进行更改。

## 初学者友好概述

将 cron 任务视为：**何时**运行 + **做什么**。

1. **选择计划**
   - 一次性提醒 → `schedule.kind = "at"`（CLI: `--at`）
   - 重复任务 → `schedule.kind = "every"` 或 `schedule.kind = "cron"`
   - 如果您的 ISO 时间戳省略了时区，则将其视为 **UTC**。

2. **选择运行位置**
   - `sessionTarget: "main"` → 在下一个 heartbeat 期间运行，使用主上下文。
   - `sessionTarget: "isolated"` → 在 `cron:<jobId>` 中运行专用的 agent 回合。

3. **选择载荷**
   - 主会话 → `payload.kind = "systemEvent"`
   - 隔离会话 → `payload.kind = "agentTurn"`

可选：一次性任务（`schedule.kind = "at"`）默认在成功后删除。设置 `deleteAfterRun: false` 以保留它们（它们在成功后将禁用）。

## 概念

### 任务

Cron 任务是一个存储的记录，包含：

- **计划**（何时运行），
- **载荷**（应做什么），
- 可选的 **交付模式**（`announce`、`webhook` 或 `none`）。
- 可选的 **Agent 绑定**（`agentId`）：在特定 Agent 下运行任务；如果缺失或未知，Gateway 回退到默认 Agent。

任务由稳定的 `jobId` 标识（CLI/Gateway APIs 使用）。在 Agent 工具调用中，`jobId` 是标准格式；为了兼容性接受遗留的 `id`。一次性任务默认在成功后自动删除；设置 `deleteAfterRun: false` 以保留它们。

### 计划

Cron 支持三种计划类型：

- `at`：通过 `schedule.at`（ISO 8601）的一次性时间戳。
- `every`：固定间隔（毫秒）。
- `cron`：5 字段 cron 表达式（或带秒的 6 字段），可选 IANA 时区。

Cron 表达式使用 `croner`。如果省略时区，则使用 Gateway 主机的本地时区。

为了减少跨多个 Gateway 的小时整点负载峰值，OpenClaw 对重复的小时整点表达式应用最多 5 分钟的确定性每任务交错窗口（例如 `0 * * * *`、`0 */2 * * *`）。像 `0 7 * * *` 这样的固定小时表达式保持精确。

对于任何 cron 计划，您可以使用 `schedule.staggerMs` 设置显式交错窗口（`0` 保持精确计时）。CLI 快捷方式：

- `--stagger 30s`（或 `1m`、`5m`）以设置显式交错窗口。
- `--exact` 强制 `staggerMs = 0`。

### 主会话与隔离执行

#### 主会话任务（系统事件）

主任务入队系统事件，并可选择唤醒 heartbeat 运行器。它们必须使用 `payload.kind = "systemEvent"`。

- `wakeMode: "now"`（默认）：事件触发立即 heartbeat 运行。
- `wakeMode: "next-heartbeat"`：事件等待下一个计划的 heartbeat。

当您想要正常的 heartbeat 提示 + 主会话上下文时，这是最佳选择。参见 [Heartbeat](/gateway/heartbeat)。

#### 隔离任务（专用 cron 会话）

隔离任务在会话 `cron:<jobId>` 中运行专用的 agent 回合。

关键行为：

- 提示符前缀为 `[cron:<jobId> <job name>]` 以便追溯。
- 每次运行启动一个新的 **session id**（无之前的对话延续）。
- 默认行为：如果省略 `delivery`，隔离任务会发布公告摘要（`delivery.mode = "announce"`）。
- `delivery.mode` 选择发生什么：
  - `announce`：向目标频道交付摘要并向主会话发布简短摘要。
  - `webhook`：当完成的事件包含摘要时，将完成的事件负载 POST 到 `delivery.to`。
  - `none`：仅限内部（无交付，无主会话摘要）。
- `wakeMode` 控制主会话摘要何时发布：
  - `now`：立即 heartbeat。
  - `next-heartbeat`：等待下一个计划的 heartbeat。

使用隔离任务处理嘈杂、频繁或不应干扰您主聊天历史的“后台杂务”。

### 载荷形状（运行内容）

支持两种载荷类型：

- `systemEvent`：仅主会话，通过 heartbeat 提示路由。
- `agentTurn`：仅隔离会话，运行专用的 agent 回合。

常见 `agentTurn` 字段：

- `message`：必需的文本提示。
- `model` / `thinking`：可选覆盖（见下文）。
- `timeoutSeconds`：可选超时覆盖。
- `lightContext`：轻量级引导模式，适用于不需要工作区引导文件注入的任务。

交付配置：

- `delivery.mode`：`none` | `announce` | `webhook`。
- `delivery.channel`：`last` 或特定频道。
- `delivery.to`：特定频道目标（announce）或 webhook URL（webhook 模式）。
- `delivery.bestEffort`：如果 announce 交付失败，避免任务失败。

Announce 交付抑制运行的消息工具发送；改用 `delivery.channel`/`delivery.to`  targeting 聊天。当 `delivery.mode = "none"` 时，不向主会话发布摘要。

如果为隔离任务省略 `delivery`，OpenClaw 默认为 `announce`。

#### Announce 交付流程

当 `delivery.mode = "announce"` 时，cron 直接通过出站频道适配器交付。不启动主 agent 来构建或转发消息。

行为详情：

- 内容：交付使用隔离运行的出站载荷（文本/媒体），具有正常的分块和频道格式化。
- 仅 heartbeat 响应（`HEARTBEAT_OK` 无实际内容）不会被交付。
- 如果隔离运行已通过消息工具向同一目标发送了消息，则跳过交付以避免重复。
- 除非 `delivery.bestEffort = true`，否则缺失或无效的交付目标会导致任务失败。
- 仅当 `delivery.mode = "announce"` 时，才会向主会话发布简短摘要。
- 主会话摘要遵循 `wakeMode`：`now` 触发立即 heartbeat，`next-heartbeat` 等待下一个计划的 heartbeat。

#### Webhook 交付流程

当 `delivery.mode = "webhook"` 时，如果完成的事件包含摘要，cron 将完成的事件负载 POST 到 `delivery.to`。

行为详情：

- 端点必须是有效的 HTTP(S) URL。
- Webhook 模式下不尝试频道交付。
- Webhook 模式下不发布主会话摘要。
- 如果设置了 `cron.webhookToken`，auth header 为 `Authorization: Bearer <cron.webhookToken>`。
- 已弃用的回退方案：存储的遗留任务带有 `notify: true` 仍会 POST 到 `cron.webhook`（如果配置），并发出警告以便您迁移到 `delivery.mode = "webhook"`。

### 模型和思考覆盖

隔离任务（`agentTurn`）可以覆盖模型和思考级别：

- `model`：Provider/model 字符串（例如 `anthropic/claude-sonnet-4-20250514`）或别名（例如 `opus`）
- `thinking`：思考级别（`off`、`minimal`、`low`、`medium`、`high`、`xhigh`；仅限 GPT-5.2 + Codex 模型）

注意：您也可以在主会话任务上设置 `model`，但这会更改共享的主会话模型。我们建议仅对隔离任务进行模型覆盖，以避免意外的上下文切换。

解析优先级：

1. 任务载荷覆盖（最高）
2. Hook 特定默认值（例如 `hooks.gmail.model`）
3. Agent 配置默认值

### 轻量级引导上下文

隔离任务（`agentTurn`）可以设置 `lightContext: true` 以使用轻量级引导上下文运行。

- 用于不需要工作区引导文件注入的计划杂务。
- 实际上，嵌入式运行时使用 `bootstrapContextMode: "lightweight"` 运行，这故意使 cron 引导上下文为空。
- CLI 等效项：`openclaw cron add --light-context ...` 和 `openclaw cron edit --light-context`。

### 交付（频道 + 目标）

隔离任务可以通过顶级 `delivery` 配置将输出交付到频道：

- `delivery.mode`：`announce`（频道交付）、`webhook`（HTTP POST）或 `none`。
- `delivery.channel`：`whatsapp` / `telegram` / `discord` / `slack` / `mattermost`（插件）/ `signal` / `imessage` / `last`。
- `delivery.to`：特定频道接收者目标。

`announce` 投递仅适用于孤立任务（`sessionTarget: "isolated"`）。
`webhook` 投递同时适用于主任务和孤立任务。

如果省略了 `delivery.channel` 或 `delivery.to`，cron 可以回退到主会话的
“最后路由”（代理回复的最后位置）。

目标格式提醒：

- Slack/Discord/Mattermost (插件) 目标应使用明确的前缀（例如 `channel:<id>`, `user:<id>`）以避免歧义。
- Telegram 主题应使用 `:topic:` 形式（见下文）。

#### Telegram 投递目标（主题 / 论坛线程）

Telegram 通过 `message_thread_id` 支持论坛主题。对于 cron 投递，您可以将
主题/线程编码到 `to` 字段中：

- `-1001234567890`（仅聊天 ID）
- `-1001234567890:topic:123`（推荐：显式主题标记）
- `-1001234567890:123`（简写：数字后缀）

带有前缀的目标如 `telegram:...` / `telegram:group:...` 也被接受：

- `telegram:group:-1001234567890:topic:123`

## 工具调用的 JSON 架构

直接调用 Gateway `cron.*` 工具时使用这些形状（代理工具调用或 RPC）。
CLI 标志接受人类可读的持续时间，如 `20m`，但工具调用应使用 ISO 8601 字符串
用于 `schedule.at`，毫秒用于 `schedule.everyMs`。

### cron.add 参数

一次性、主会话任务（系统事件）：

```json
{
  "name": "Reminder",
  "schedule": { "kind": "at", "at": "2026-02-01T16:00:00Z" },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": { "kind": "systemEvent", "text": "Reminder text" },
  "deleteAfterRun": true
}
```

周期性、带投递的孤立任务：

```json
{
  "name": "Morning brief",
  "schedule": { "kind": "cron", "expr": "0 7 * * *", "tz": "America/Los_Angeles" },
  "sessionTarget": "isolated",
  "wakeMode": "next-heartbeat",
  "payload": {
    "kind": "agentTurn",
    "message": "Summarize overnight updates.",
    "lightContext": true
  },
  "delivery": {
    "mode": "announce",
    "channel": "slack",
    "to": "channel:C1234567890",
    "bestEffort": true
  }
}
```

注意：

- `schedule.kind`: `at` (`at`), `every` (`everyMs`), 或 `cron` (`expr`, 可选 `tz`)。
- `schedule.at` 接受 ISO 8601（时区可选；省略时视为 UTC）。
- `everyMs` 是毫秒。
- `sessionTarget` 必须是 `"main"` 或 `"isolated"`，且必须匹配 `payload.kind`。
- 可选字段：`agentId`, `description`, `enabled`, `deleteAfterRun`（`at` 默认为 true），
  `delivery`。
- `wakeMode` 省略时默认为 `"now"`。

### cron.update 参数

```json
{
  "jobId": "job-123",
  "patch": {
    "enabled": false,
    "schedule": { "kind": "every", "everyMs": 3600000 }
  }
}
```

注意：

- `jobId` 是标准形式；`id` 为兼容性而被接受。
- 在补丁中使用 `agentId: null` 清除代理绑定。

### cron.run 和 cron.remove 参数

```json
{ "jobId": "job-123", "mode": "force" }
```

```json
{ "jobId": "job-123" }
```

## 存储与历史

- 任务存储：`~/.openclaw/cron/jobs.json`（Gateway 管理的 JSON）。
- 运行历史：`~/.openclaw/cron/runs/<jobId>.jsonl`（JSONL，按大小和行数自动修剪）。
- `sessions.json` 中的孤立 cron 运行会话由 `cron.sessionRetention` 修剪（默认 `24h`；设置 `false` 以禁用）。
- 覆盖存储路径：配置中的 `cron.store`。

## 重试策略

当任务失败时，OpenClaw 将错误分类为 **瞬态**（可重试）或 **永久**（立即禁用）。

### 瞬态错误（会重试）

- 速率限制（429，请求过多，资源耗尽）
- 提供商过载（例如 Anthropic `529 overloaded_error`，过载回退摘要）
- 网络错误（超时，ECONNRESET，fetch 失败，socket）
- 服务器错误（5xx）
- Cloudflare 相关错误

### 永久错误（不重试）

- 认证失败（无效 API 密钥，未授权）
- 配置或验证错误
- 其他非瞬态错误

### 默认行为（无配置）

**一次性任务（`schedule.kind: "at"`）：**

- 遇到瞬态错误：最多重试 3 次，采用指数退避（30 秒 → 1 分钟 → 5 分钟）。
- 遇到永久错误：立即禁用。
- 成功或跳过时：禁用（如果 `deleteAfterRun: true` 则删除）。

**周期性任务（`cron` / `every`）：**

- 遇到任何错误：在下一次计划运行之前应用指数退避（30 秒 → 1 分钟 → 5 分钟 → 15 分钟 → 60 分钟）。
- 任务保持启用状态；下一次成功运行后重置退避。

配置 `cron.retry` 以覆盖这些默认值（参见 [配置](/automation/cron-jobs#configuration)）。

## 配置

```json5
{
  cron: {
    enabled: true, // default true
    store: "~/.openclaw/cron/jobs.json",
    maxConcurrentRuns: 1, // default 1
    // Optional: override retry policy for one-shot jobs
    retry: {
      maxAttempts: 3,
      backoffMs: [60000, 120000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "server_error"],
    },
    webhook: "https://example.invalid/legacy", // deprecated fallback for stored notify:true jobs
    webhookToken: "replace-with-dedicated-webhook-token", // optional bearer token for webhook mode
    sessionRetention: "24h", // duration string or false
    runLog: {
      maxBytes: "2mb", // default 2_000_000 bytes
      keepLines: 2000, // default 2000
    },
  },
}
```

运行日志修剪行为：

- `cron.runLog.maxBytes`：修剪前的最大运行日志文件大小。
- `cron.runLog.keepLines`：修剪时，仅保留最新的 N 行。
- 两者均适用于 `cron/runs/<jobId>.jsonl` 文件。

Webhook 行为：

- 推荐：为每个任务设置 `delivery.mode: "webhook"` 和 `delivery.to: "https://..."`。
- Webhook URL 必须是有效的 `http://` 或 `https://` URL。
- 发布时，负载是 cron 完成事件的 JSON。
- 如果设置了 `cron.webhookToken`，auth 头为 `Authorization: Bearer <cron.webhookToken>`。
- 如果未设置 `cron.webhookToken`，则不发送 `Authorization` 头。
- 已弃用的回退：存储的旧任务若包含 `notify: true`，仍会使用 `cron.webhook`（如果存在）。

完全禁用 cron：

- `cron.enabled: false`（配置）
- `OPENCLAW_SKIP_CRON=1`（环境变量）

## 维护

Cron 有两个内置维护路径：孤立运行会话保留和运行日志修剪。

### 默认值

- `cron.sessionRetention`: `24h`（设置 `false` 以禁用运行会话修剪）
- `cron.runLog.maxBytes`: `2_000_000` 字节
- `cron.runLog.keepLines`: `2000`

### 工作原理

- 孤立运行创建会话条目（`...:cron:<jobId>:run:<uuid>`）和转录文件。
- 回收器移除超过 `cron.sessionRetention` 的过期运行会话条目。
- 对于不再被会话存储引用的已删除运行会话，OpenClaw 归档转录文件，并在相同的保留窗口内清理旧的已删除归档。
- 每次追加运行后，检查 `cron/runs/<jobId>.jsonl` 的大小：
  - 如果文件大小超过 `runLog.maxBytes`，则修剪至最新的 `runLog.keepLines` 行。

### 高频率调度器的性能注意事项

高频 cron 设置可能会产生庞大的运行会话和运行日志占用空间。虽然内置了维护功能，但宽松的限制仍可能导致可避免的 IO 和清理工作。

需要关注：

- 具有许多孤立运行的长 `cron.sessionRetention` 窗口
- 高 `cron.runLog.keepLines` 结合大 `runLog.maxBytes`
- 许多嘈杂的周期性任务写入同一个 `cron/runs/<jobId>.jsonl`

该怎么做：

- 尽可能短地保持 `cron.sessionRetention`，以满足您的调试/审计需求
- 使用适度的 `runLog.maxBytes` 和 `runLog.keepLines` 保持运行日志有界
- 将嘈杂的后台任务移至孤立模式，并使用避免不必要噪音的投递规则
- 定期使用 `openclaw cron runs` 审查增长情况，并在日志变大之前调整保留期

### 自定义示例

保留一周的运行会话并允许更大的运行日志：

```json5
{
  cron: {
    sessionRetention: "7d",
    runLog: {
      maxBytes: "10mb",
      keepLines: 5000,
    },
  },
}
```

禁用孤立运行会话修剪但保留运行日志修剪：

```json5
{
  cron: {
    sessionRetention: false,
    runLog: {
      maxBytes: "5mb",
      keepLines: 3000,
    },
  },
}
```

针对高流量 cron 使用进行微调（示例）：

```json5
{
  cron: {
    sessionRetention: "12h",
    runLog: {
      maxBytes: "3mb",
      keepLines: 1500,
    },
  },
}
```

## CLI 快速入门

一次性提醒（UTC ISO，成功后自动删除）：

```bash
openclaw cron add \
  --name "Send reminder" \
  --at "2026-01-12T18:00:00Z" \
  --session main \
  --system-event "Reminder: submit expense report." \
  --wake now \
  --delete-after-run
```

一次性提醒（主会话，立即唤醒）：

```bash
openclaw cron add \
  --name "Calendar check" \
  --at "20m" \
  --session main \
  --system-event "Next heartbeat: check calendar." \
  --wake now
```

周期性孤立任务（向 WhatsApp 宣布）：

```bash
openclaw cron add \
  --name "Morning status" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize inbox + calendar for today." \
  --announce \
  --channel whatsapp \
  --to "+15551234567"
```

带有明确 30 秒错开的周期性 cron 任务：

```bash
openclaw cron add \
  --name "Minute watcher" \
  --cron "0 * * * * *" \
  --tz "UTC" \
  --stagger 30s \
  --session isolated \
  --message "Run minute watcher checks." \
  --announce
```

周期性孤立任务（投递到 Telegram 主题）：

```bash
openclaw cron add \
  --name "Nightly summary (topic)" \
  --cron "0 22 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize today; send to the nightly topic." \
  --announce \
  --channel telegram \
  --to "-1001234567890:topic:123"
```

带有模型和思考覆盖的孤立任务：

```bash
openclaw cron add \
  --name "Deep analysis" \
  --cron "0 6 * * 1" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Weekly deep analysis of project progress." \
  --model "opus" \
  --thinking high \
  --announce \
  --channel whatsapp \
  --to "+15551234567"
```

代理选择（多代理设置）：

手动运行（默认强制，使用 `--due` 仅在到期时运行）：

```bash
openclaw cron run <jobId>
openclaw cron run <jobId> --due
```

编辑现有任务（更新字段）：

```bash
openclaw cron edit <jobId> \
  --message "Updated prompt" \
  --model "opus" \
  --thinking low
```

强制现有 cron 任务严格按照计划运行（无交错）：

```bash
openclaw cron edit <jobId> --exact
```

运行历史：

```bash
openclaw cron runs --id <jobId> --limit 50
```

无需创建任务的即时系统事件：

```bash
openclaw system event --mode now --text "Next heartbeat: check battery."
```

## Gateway API 接口

- `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`
- `cron.run` (force or due), `cron.runs`
  对于无需创建任务的即时系统事件，请使用 [`openclaw system event`](/cli/system)。

## 故障排除

### “没有任何内容运行”

- 检查 cron 是否已启用：`cron.enabled` 和 `OPENCLAW_SKIP_CRON`。
- 检查网关是否持续运行（cron 在网关进程中运行）。
- 对于 `cron` 计划：确认时区（`--tz`）与主机时区。

### 重复任务在失败后持续延迟

- OpenClaw 对重复任务在连续错误后应用指数重试退避：
  30s, 1m, 5m, 15m，然后重试间隔为 60m。
- 退避在下次成功运行后自动重置。
- 一次性 (`at`) 任务会重试临时错误（rate limit, overloaded, network, server_error），最多 3 次并带有退避；永久错误则立即禁用。请参阅 [重试策略](/automation/cron-jobs#retry-policy)。

### Telegram 发送到了错误的位置

- 对于论坛主题，请使用 `-100…:topic:<id>`，使其明确且无歧义。
- 如果在日志或存储的“最后路由”目标中看到 `telegram:...` 前缀，这是正常的；
  cron 投递接受它们并能正确解析主题 ID。

### 子代理公告投递重试

- 当子代理运行完成时，网关向请求者会话公告结果。
- 如果公告流程返回 `false`（例如请求者会话繁忙），网关将重试最多 3 次并通过 `announceRetryCount` 进行跟踪。
- 超过 `endedAt` 5 分钟的公告将被强制过期，以防止陈旧条目无限循环。
- 如果在日志中看到重复的公告投递，请检查子代理注册表中具有高 `announceRetryCount` 值的条目。