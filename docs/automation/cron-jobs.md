---
summary: "Cron jobs + wakeups for the Gateway scheduler"
read_when:
  - Scheduling background jobs or wakeups
  - Wiring automation that should run with or alongside heartbeats
  - Deciding between heartbeat and cron for scheduled tasks
title: "Cron Jobs"
---
# Cron jobs (Gateway scheduler)

> **Cron vs Heartbeat?** 请参阅 [Cron vs Heartbeat](/automation/cron-vs-heartbeat) 以获取何时使用每个工具的指导。

Cron 是 Gateway 的内置调度器。它会持久化任务，在正确的时间唤醒代理，并可以选择将输出发送回聊天。

如果您想要 _“每天早上运行一次”_ 或 _“20分钟后唤醒代理”_，cron 就是实现机制。

故障排除：[/automation/troubleshooting](/automation/troubleshooting)

## TL;DR

- Cron 在 **Gateway 内部** 运行（不在模型内部）。
- 任务在 `~/.openclaw/cron/` 中持久化，因此重启不会丢失计划。
- 两种执行方式：
  - **主会话**：排队一个系统事件，然后在下一个心跳时运行。
  - **隔离**：在 `cron:<jobId>` 中运行专用代理回合，可选择是否发送结果（默认公告或不发送）。
- 唤醒是第一类操作：任务可以请求“立即唤醒”而不是“下一个心跳”。
- Webhook 发送是通过每个任务的 `delivery.mode = "webhook"` + `delivery.to = "<url>"`。
- 对于存储的任务，当设置了 `cron.webhook` 时，保留了 `notify: true` 的旧版回退，建议将这些任务迁移到 webhook 发送模式。

## 快速开始（可操作）

创建一个一次性提醒，验证其存在并立即运行：

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

安排一个带有发送功能的重复隔离任务：

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

## 工具调用等效（Gateway cron 工具）

有关规范的 JSON 形式和示例，请参阅 [工具调用的 JSON 模式](/automation/cron-jobs#json-schema-for-tool-calls)。

## Cron 任务存储位置

Cron 任务默认存储在 Gateway 主机上的 `~/.openclaw/cron/jobs.json`。
Gateway 将文件加载到内存中并在更改时写回，因此只有在 Gateway 停止时手动编辑才是安全的。建议使用 `openclaw cron add/edit` 或 cron 工具调用 API 进行更改。

## 初学者友好概述

将 cron 任务视为：**何时** 运行 + **做什么**。

1. **选择一个计划**
   - 一次性提醒 → `schedule.kind = "at"` (CLI: `--at`)
   - 重复任务 → `schedule.kind = "every"` 或 `schedule.kind = "cron"`
   - 如果您的 ISO 时间戳省略了时区，则被视为 **UTC**。

2. **选择运行位置**
   - `sessionTarget: "main"` → 在下一个心跳时使用主上下文运行。
   - `sessionTarget: "isolated"` → 在 `cron:<jobId>` 中运行专用代理回合。

3. **选择负载**
   - 主会话 → `payload.kind = "systemEvent"`
   - 隔离会话 → `payload.kind = "agentTurn"`

可选：一次性任务 (`schedule.kind = "at"`) 成功后默认删除。设置
`deleteAfterRun: false` 以保留它们（它们将在成功后禁用）。

## 概念

### 任务

一个cron任务是一个存储记录，包含：

- 一个 **调度**（它应该何时运行），
- 一个 **负载**（它应该做什么），
- 可选的 **传递模式** (`announce`, `webhook`, 或 `none`)。
- 可选的 **代理绑定** (`agentId`)：在特定代理下运行任务；如果
  缺少或未知，网关将回退到默认代理。

任务通过一个稳定的 `jobId` 标识（由CLI/网关API使用）。
在代理工具调用中，`jobId` 是规范的；为了兼容性，接受旧的 `id`。
一次性任务默认在成功后自动删除；设置 `deleteAfterRun: false` 以保留它们。

### 调度

Cron 支持三种调度类型：

- `at`：通过 `schedule.at`（ISO 8601）指定的一次性时间戳。
- `every`：固定间隔（毫秒）。
- `cron`：5字段cron表达式（或带有秒的6字段）以及可选的IANA时区。

Cron 表达式使用 `croner`。如果省略时区，则使用网关主机的
本地时区。

为了减少多个网关在整点时的负载峰值，OpenClaw 对于重复的整点表达式（例如 `0 * * * *`, `0 */2 * * *`）
应用一个确定性的每个任务最多5分钟的随机延迟窗口。固定小时表达式如 `0 7 * * *` 保持精确。

对于任何cron调度，您可以使用 `schedule.staggerMs` 设置显式的随机延迟窗口（`0` 保持精确计时）。CLI快捷方式：

- `--stagger 30s`（或 `1m`, `5m`）设置显式的随机延迟窗口。
- `--exact` 强制 `staggerMs = 0`。

### 主执行与隔离执行

#### 主会话任务（系统事件）

主任务入队一个系统事件，并可选地唤醒心跳运行器。
它们必须使用 `payload.kind = "systemEvent"`。

- `wakeMode: "now"`（默认）：事件触发立即的心跳运行。
- `wakeMode: "next-heartbeat"`：事件等待下一个计划的心跳。

当您希望使用正常的心跳提示 + 主会话上下文时，这是最佳选择。
参见 [Heartbeat](/gateway/heartbeat)。

#### 隔离任务（专用cron会话）

隔离任务在一个专用的会话 `cron:<jobId>` 中运行代理轮询。

关键行为：

- 提示前缀为 `[cron:<jobId> <job name>]` 以便追踪。
- 每次运行开始一个新的 **会话ID**（没有之前的对话延续）。
- 默认行为：如果省略 `delivery`，隔离任务会宣布一个摘要 (`delivery.mode = "announce"`)。
- `delivery.mode` 选择发生什么：
  - `announce`：将摘要发送到目标频道并在主会话中发布简要摘要。
  - `webhook`：当完成事件包含摘要时，POST完成事件负载到 `delivery.to`。
  - `none`：仅内部使用（无交付，无主会话摘要）。
- `wakeMode` 控制主会话摘要何时发布：
  - `now`：立即心跳。
  - `next-heartbeat`：等待下一个计划的心跳。

使用独立任务来处理嘈杂的、频繁的或“后台任务”，这些任务不应该充斥你的主要聊天历史。

### 负载形状（运行的内容）

支持两种负载类型：

- `systemEvent`: 仅主会话，通过心跳提示路由。
- `agentTurn`: 仅独立会话，运行专用代理轮次。

常见的 `agentTurn` 字段：

- `message`: 必需的文本提示。
- `model` / `thinking`: 可选覆盖（见下文）。
- `timeoutSeconds`: 可选超时覆盖。

交付配置：

- `delivery.mode`: `none` | `announce` | `webhook`.
- `delivery.channel`: `last` 或特定频道。
- `delivery.to`: 频道特定目标（公告）或 webhook URL（webhook 模式）。
- `delivery.bestEffort`: 如果公告交付失败，避免使任务失败。

公告交付会抑制运行期间的消息工具发送；使用 `delivery.channel`/`delivery.to`
来针对聊天。当 `delivery.mode = "none"`，不会将摘要发布到主会话。

如果孤立任务中省略了 `delivery`，OpenClaw 默认为 `announce`。

#### 公告交付流程

当 `delivery.mode = "announce"`，cron 直接通过出站频道适配器交付。
主代理不会启动以构建或转发消息。

行为细节：

- 内容：交付使用孤立运行的出站负载（文本/媒体），具有正常的分块和
  频道格式化。
- 仅心跳响应 (`HEARTBEAT_OK` 无实际内容) 不会被交付。
- 如果孤立运行已经通过消息工具向同一目标发送了消息，交付将被跳过以避免重复。
- 缺少或无效的交付目标会使任务失败，除非 `delivery.bestEffort = true`。
- 仅当 `delivery.mode = "announce"` 时，才会在主会话中发布简短摘要。
- 主会话摘要尊重 `wakeMode`: `now` 触发立即心跳，
  `next-heartbeat` 等待下一个计划的心跳。

#### Webhook 交付流程

当 `delivery.mode = "webhook"`，cron 在完成事件包含摘要时，将完成事件负载发布到 `delivery.to`。

行为细节：

- 终端必须是有效的 HTTP(S) URL。
- 在 webhook 模式下不尝试频道交付。
- 在 webhook 模式下不发布主会话摘要。
- 如果设置了 `cron.webhookToken`，auth 头是 `Authorization: Bearer <cron.webhookToken>`。
- 已弃用的回退：存储的遗留任务带有 `notify: true` 仍然发布到 `cron.webhook`（如果已配置），并发出警告，以便你可以迁移到 `delivery.mode = "webhook"`。

### 模型和思考覆盖

孤立任务 (`agentTurn`) 可以覆盖模型和思考级别：

- `model`: 提供商/模型字符串（例如，`anthropic/claude-sonnet-4-20250514`）或别名（例如，`opus`）
- `thinking`: 思考级别 (`off`, `minimal`, `low`, `medium`, `high`, `xhigh`; 仅适用于 GPT-5.2 + Codex 模型）

注意：您也可以在 `main-session` 作业上设置 `model`，但这会更改共享的主会话模型。我们建议仅在隔离作业中使用模型覆盖，以避免意外的上下文切换。

解析优先级：

1. 作业负载覆盖（最高）
2. 钩子特定默认值（例如，`hooks.gmail.model`）
3. 代理配置默认值

### 交付（通道 + 目标）

隔离作业可以通过顶级 `delivery` 配置将输出传递到通道：

- `delivery.mode`: `announce`（通道交付），`webhook`（HTTP POST），或 `none`。
- `delivery.channel`: `whatsapp` / `telegram` / `discord` / `slack` / `mattermost`（插件）/ `signal` / `imessage` / `last`。
- `delivery.to`: 特定通道的接收者目标。

`announce` 交付仅对隔离作业有效 (`sessionTarget: "isolated"`)。
`webhook` 交付对主作业和隔离作业都有效。

如果省略 `delivery.channel` 或 `delivery.to`，cron 可以回退到主会话的“最后路由”（代理最后回复的位置）。

目标格式提醒：

- Slack/Discord/Mattermost（插件）目标应使用显式前缀（例如 `channel:<id>`，`user:<id>`）以避免歧义。
- Telegram 主题应使用 `:topic:` 形式（见下文）。

#### Telegram 交付目标（主题 / 论坛线程）

Telegram 通过 `message_thread_id` 支持论坛主题。对于 cron 交付，您可以将主题/线程编码到 `to` 字段中：

- `-1001234567890`（仅聊天ID）
- `-1001234567890:topic:123`（首选：显式主题标记）
- `-1001234567890:123`（简写：数字后缀）

也接受带有前缀的目标如 `telegram:...` / `telegram:group:...`：

- `telegram:group:-1001234567890:topic:123`

## 工具调用的 JSON 模式

直接调用网关 `cron.*` 工具时使用这些形状（代理工具调用或 RPC）。
CLI 标志接受人类可读的持续时间如 `20m`，但工具调用应使用 ISO 8601 字符串用于 `schedule.at` 和毫秒用于 `schedule.everyMs`。

### cron.add 参数

一次性，主会话作业（系统事件）：

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

循环，带有交付的隔离作业：

```json
{
  "name": "Morning brief",
  "schedule": { "kind": "cron", "expr": "0 7 * * *", "tz": "America/Los_Angeles" },
  "sessionTarget": "isolated",
  "wakeMode": "next-heartbeat",
  "payload": {
    "kind": "agentTurn",
    "message": "Summarize overnight updates."
  },
  "delivery": {
    "mode": "announce",
    "channel": "slack",
    "to": "channel:C1234567890",
    "bestEffort": true
  }
}
```

注意事项：

- `schedule.kind`: `at` (`at`), `every` (`everyMs`), 或 `cron` (`expr`, 可选 `tz`)。
- `schedule.at` 接受 ISO 8601（时区可选；省略时视为 UTC）。
- `everyMs` 是毫秒。
- `sessionTarget` 必须是 `"main"` 或 `"isolated"` 并且必须匹配 `payload.kind`。
- 可选字段：`agentId`, `description`, `enabled`, `deleteAfterRun`（`at` 默认为 true）,
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

注意事项：

- `jobId` 是规范形式；接受 `id` 以兼容性。
- 使用 `agentId: null` 在补丁中清除代理绑定。

### cron.run 和 cron.remove 参数

```json
{ "jobId": "job-123", "mode": "force" }
```

```json
{ "jobId": "job-123" }
```

## 存储与历史记录

- 作业存储：`~/.openclaw/cron/jobs.json`（网关管理的 JSON）。
- 运行历史：`~/.openclaw/cron/runs/<jobId>.jsonl`（JSONL，自动修剪）。
- 覆盖存储路径：配置中的 `cron.store`。

## 配置

```json5
{
  cron: {
    enabled: true, // default true
    store: "~/.openclaw/cron/jobs.json",
    maxConcurrentRuns: 1, // default 1
    webhook: "https://example.invalid/legacy", // deprecated fallback for stored notify:true jobs
    webhookToken: "replace-with-dedicated-webhook-token", // optional bearer token for webhook mode
  },
}
```

Webhook 行为：

- 建议：为每个作业设置 `delivery.mode: "webhook"` 与 `delivery.to: "https://..."`。
- Webhook URL 必须是有效的 `http://` 或 `https://` URL。
- 发送时，负载是 cron 完成事件的 JSON。
- 如果设置了 `cron.webhookToken`，认证头是 `Authorization: Bearer <cron.webhookToken>`。
- 如果未设置 `cron.webhookToken`，不发送 `Authorization` 头。
- 已弃用的回退：使用 `notify: true` 存储的旧作业在存在时仍然使用 `cron.webhook`。

完全禁用 cron：

- `cron.enabled: false`（配置）
- `OPENCLAW_SKIP_CRON=1`（环境变量）

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

定期独立作业（通告到 WhatsApp）：

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

带有显式 30 秒延迟的定期 cron 作业：

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

循环独立任务（发送到Telegram主题）：

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

带有模型和思考覆盖的独立任务：

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

```bash
# Pin a job to agent "ops" (falls back to default if that agent is missing)
openclaw cron add --name "Ops sweep" --cron "0 6 * * *" --session isolated --message "Check ops queue" --agent ops

# Switch or clear the agent on an existing job
openclaw cron edit <jobId> --agent ops
openclaw cron edit <jobId> --clear-agent
```

手动运行（默认强制执行，使用`--due`仅在应执行时运行）：

```bash
openclaw cron run <jobId>
openclaw cron run <jobId> --due
```

编辑现有任务（修补字段）：

```bash
openclaw cron edit <jobId> \
  --message "Updated prompt" \
  --model "opus" \
  --thinking low
```

强制现有cron任务按计划精确运行（无延迟）：

```bash
openclaw cron edit <jobId> --exact
```

运行历史记录：

```bash
openclaw cron runs --id <jobId> --limit 50
```

立即系统事件而不创建任务：

```bash
openclaw system event --mode now --text "Next heartbeat: check battery."
```

## 网关API接口

- `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`
- `cron.run` (force 或 due), `cron.runs`
  对于没有任务的立即系统事件，请使用[`openclaw system event`](/cli/system)。

## 故障排除

### “没有任何任务运行”

- 检查cron是否已启用：`cron.enabled` 和 `OPENCLAW_SKIP_CRON`。
- 检查网关是否持续运行（cron在网关进程中运行）。
- 对于`cron`计划：确认时区(`--tz`)与主机时区。

### 循环任务在失败后不断延迟

- OpenClaw对连续错误后的循环任务应用指数级重试回退：
  30秒，1分钟，5分钟，15分钟，然后每次重试间隔60分钟。
- 下一次成功运行后，回退会自动重置。
- 单次运行(`at`)任务在终端运行后禁用(`ok`, `error`, 或 `skipped`)且不重试。

### Telegram发送到错误的位置

- 对于论坛主题，请使用`-100…:topic:<id>`以使其明确且无歧义。
- 如果在日志或存储的“最后路由”目标中看到`telegram:...`前缀，这是正常的；
  cron交付接受它们并仍能正确解析主题ID。

### Subagent announce delivery retries

- 当一个subagent运行完成时，网关会将结果通告给请求者会话。
- 如果通告流程返回 `false`（例如请求者会话繁忙），网关会重试最多3次，并通过 `announceRetryCount` 进行跟踪。
- 超过 `endedAt` 5分钟以上的通告会被强制过期，以防止陈旧条目无限循环。
- 如果在日志中看到重复的通告交付，请检查subagent注册表中具有高 `announceRetryCount` 值的条目。