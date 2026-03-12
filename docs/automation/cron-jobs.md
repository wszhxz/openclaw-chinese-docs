---
summary: "Cron jobs + wakeups for the Gateway scheduler"
read_when:
  - Scheduling background jobs or wakeups
  - Wiring automation that should run with or alongside heartbeats
  - Deciding between heartbeat and cron for scheduled tasks
title: "Cron Jobs"
---
# Cron 任务（网关调度器）

> **Cron 与 Heartbeat 的区别？** 请参阅 [Cron 与 Heartbeat](/automation/cron-vs-heartbeat)，了解何时应使用哪一种机制。

Cron 是网关内置的调度器。它会持久化任务、在正确的时间唤醒代理，并可选择将输出结果回传至聊天中。

如果你需要 _“每天早上运行此操作”_ 或 _“20 分钟后提醒代理”_，那么 Cron 就是实现该需求的机制。

故障排查：[/automation/troubleshooting](/automation/troubleshooting)

## 快速概览（TL;DR）

- Cron 在 **网关内部** 运行（而非在模型内部）。
- 任务持久化存储于 `~/.openclaw/cron/` 下，因此重启不会丢失已设定的调度计划。
- 两种执行方式：
  - **主会话模式**：入队一个系统事件，然后在下一次心跳时运行。
  - **隔离模式**：在 `cron:<jobId>` 中运行一次专用的代理回合，并支持交付（默认为公告模式，也可设为不交付）。
- 唤醒机制为一级特性：任务可明确请求“立即唤醒”或“等待下次心跳”。
- Webhook 发送按任务配置，通过 `delivery.mode = "webhook"` + `delivery.to = "<url>"` 实现。
- 对于已存储但仍使用 `notify: true` 的旧版任务（当 `cron.webhook` 被设置时），系统保留兼容性回退逻辑；建议将这些任务迁移至 Webhook 交付模式。

## 快速上手（可操作示例）

创建一个一次性提醒任务，验证其存在，并立即执行：

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

安排一个带交付功能的周期性隔离任务：

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

## 工具调用等效形式（网关 Cron 工具）

关于标准 JSON 结构及示例，请参阅 [工具调用的 JSON Schema](/automation/cron-jobs#json-schema-for-tool-calls)。

## Cron 任务的存储位置

默认情况下，Cron 任务持久化保存在网关主机上的 `~/.openclaw/cron/jobs.json`。
网关会将该文件加载进内存，并在发生变更时写回磁盘，因此仅当网关已停止运行时，手动编辑才安全。建议优先使用 `openclaw cron add/edit` 或 Cron 工具调用 API 来修改任务。

## 面向初学者的概述

可将 Cron 任务理解为：**何时运行** + **执行什么操作**。

1. **选择调度方式**
   - 一次性提醒 → `schedule.kind = "at"`（CLI：`--at`）
   - 周期性任务 → `schedule.kind = "every"` 或 `schedule.kind = "cron"`
   - 若 ISO 时间戳未指定时区，则默认视为 **UTC**。

2. **选择运行位置**
   - `sessionTarget: "main"` → 在下次心跳期间、使用主上下文运行。
   - `sessionTarget: "isolated"` → 在 `cron:<jobId>` 中运行一次专用的代理回合。

3. **选择有效载荷（payload）**
   - 主会话模式 → `payload.kind = "systemEvent"`
   - 隔离会话模式 → `payload.kind = "agentTurn"`

可选：一次性任务（`schedule.kind = "at"`）默认在成功执行后自动删除。若需保留，请设置 `deleteAfterRun: false`（任务将在成功后被禁用）。

## 核心概念

### 任务（Jobs）

一个 Cron 任务是一条持久化记录，包含以下字段：

- **调度时间**（应何时运行），
- **有效载荷**（应执行什么操作），
- 可选的 **交付模式**（`announce`、`webhook` 或 `none`），
- 可选的 **代理绑定**（`agentId`）：指定任务在特定代理下运行；若未指定或代理未知，网关将回退至默认代理。

任务通过稳定的 `jobId` 进行标识（供 CLI / 网关 API 使用）。  
在代理工具调用中，`jobId` 为标准字段；为兼容性，也接受旧版 `id`。  
一次性任务默认在成功后自动删除；如需保留，请设置 `deleteAfterRun: false`。

### 调度方式（Schedules）

Cron 支持三种调度类型：

- `at`：通过 `schedule.at`（ISO 8601）指定的一次性时间戳。
- `every`：固定时间间隔（毫秒）。
- `cron`：五字段 Cron 表达式（或六字段，含秒），支持可选 IANA 时区。

Cron 表达式采用 `croner`。若未指定时区，则使用网关主机的本地时区。

为减少大量网关在整点时刻集中触发导致的负载尖峰，OpenClaw 对重复性的整点表达式（例如 `0 * * * *`、`0 */2 * * *`）应用了确定性的每任务错峰窗口（最多 5 分钟）。而像 `0 7 * * *` 这类固定小时表达式则保持精确执行。

对于任意 Cron 调度，均可通过 `schedule.staggerMs` 显式设置错峰窗口（`0` 表示禁用错峰，保持精确时间）。CLI 快捷方式如下：

- `--stagger 30s`（或 `1m`、`5m`）用于显式设置错峰窗口。
- `--exact` 强制启用 `staggerMs = 0`。

### 主会话 vs 隔离执行

#### 主会话任务（系统事件）

主会话任务将一个系统事件加入队列，并可选地唤醒心跳执行器。必须使用 `payload.kind = "systemEvent"`。

- `wakeMode: "now"`（默认）：事件触发一次即时心跳运行。
- `wakeMode: "next-heartbeat"`：事件等待下一次预定的心跳。

当你希望使用常规心跳提示词 + 主会话上下文时，这是最合适的模式。详见 [Heartbeat](/gateway/heartbeat)。

#### 隔离任务（专用 Cron 会话）

隔离任务在会话 `cron:<jobId>` 中运行一次专用的代理回合。

关键行为包括：

- 提示词前缀为 `[cron:<jobId> <job name>]`，便于追踪。
- 每次运行均生成一个**全新的会话 ID**（不继承先前对话历史）。
- 默认行为：若未指定 `delivery`，隔离任务将公告摘要（`delivery.mode = "announce"`）。
- `delivery.mode` 控制交付行为：
  - `announce`：向目标频道交付摘要，并在主会话中发布简要摘要。
  - `webhook`：当完成事件包含摘要时，将完成事件的有效载荷 POST 至 `delivery.to`。
  - `none`：仅限内部使用（无交付，也不在主会话中发布摘要）。
- `wakeMode` 控制主会话摘要的发布时间：
  - `now`：立即触发心跳。
  - `next-heartbeat`：等待下一次预定的心跳。

请对那些嘈杂、高频或属于“后台杂务”的任务使用隔离模式，以避免污染主聊天历史。

### 有效载荷格式（实际运行内容）

支持两类有效载荷：

- `systemEvent`：仅适用于主会话，经由心跳提示词路由。
- `agentTurn`：仅适用于隔离会话，运行一次专用的代理回合。

常见 `agentTurn` 字段：

- `message`：必需的文本提示词。
- `model` / `thinking`：可选覆盖项（见下文）。
- `timeoutSeconds`：可选超时覆盖。
- `lightContext`：可选轻量级引导模式，适用于无需注入工作区引导文件的任务。

交付配置：

- `delivery.mode`：`none` | `announce` | `webhook`。
- `delivery.channel`：`last` 或具体频道。
- `delivery.to`：频道特定的目标（公告）或 Webhook URL（Webhook 模式）。
- `delivery.bestEffort`：若公告交付失败，避免导致整个任务失败。

公告交付会抑制本次运行中的消息工具发送；如需定向发送至聊天，请使用 `delivery.channel`/`delivery.to`。当 `delivery.mode = "none"` 时，主会话中不发布摘要。

若隔离任务未指定 `delivery`，OpenClaw 默认使用 `announce`。

#### 公告交付流程

当 `delivery.mode = "announce"` 时，Cron 直接通过出站频道适配器交付。主代理不会被启动来构造或转发该消息。

行为细节如下：

- 内容：交付使用隔离运行的出站有效载荷（文本/媒体），并遵循常规分块和频道格式化规则。
- 仅含心跳响应（`HEARTBEAT_OK`）且无实质内容的响应，不予交付。
- 若隔离运行已通过消息工具向同一目标发送过消息，则跳过交付，避免重复。
- 若交付目标缺失或无效，且未设置 `delivery.bestEffort = true`，则任务失败。
- 仅当 `delivery.mode = "announce"` 时，才在主会话中发布简短摘要。
- 主会话摘要遵循 `wakeMode`：`now` 触发即时心跳，`next-heartbeat` 则等待下一次预定心跳。

#### Webhook 交付流程

当 `delivery.mode = "webhook"` 时，Cron 在完成事件包含摘要时，将完成事件的有效载荷 POST 至 `delivery.to`。

行为细节如下：

- 终端地址必须是有效的 HTTP(S) URL。
- Webhook 模式下不尝试任何频道交付。
- Webhook 模式下不在主会话中发布摘要。
- 若设置了 `cron.webhookToken`，认证头为 `Authorization: Bearer <cron.webhookToken>`。
- 已弃用的回退机制：仍使用 `notify: true` 的旧版已存任务，仍将 POST 至 `cron.webhook`（若已配置），同时发出警告，提示你迁移到 `delivery.mode = "webhook"`。

### 模型与推理级别覆盖

隔离任务（`agentTurn`）可覆盖模型与推理级别：

- `model`：提供方/模型字符串（例如 `anthropic/claude-sonnet-4-20250514`）或别名（例如 `opus`）
- `thinking`：推理级别（`off`、`minimal`、`low`、`medium`、`high`、`xhigh`；仅 GPT-5.2 和 Codex 模型支持）

注意：你也可以为主会话任务设置 `model`，但这会更改共享的主会话模型。我们建议仅对隔离任务使用模型覆盖，以避免意外的上下文切换。

解析优先级如下：

1. 任务有效载荷覆盖（最高优先级）
2. 钩子特定默认值（例如 `hooks.gmail.model`）
3. 代理配置默认值

### 轻量级引导上下文

隔离任务（`agentTurn`）可通过设置 `lightContext: true` 启用轻量级引导上下文。

- 适用于无需注入工作区引导文件的定时杂务。
- 实际运行中，嵌入式运行时使用 `bootstrapContextMode: "lightweight"`，从而有意保持 Cron 引导上下文为空。
- CLI 等效命令：`openclaw cron add --light-context ...` 和 `openclaw cron edit --light-context`。

### 交付（频道 + 目标）

隔离任务可通过顶层 `delivery` 配置向频道交付输出：

- `delivery.mode`：`announce`（频道交付）、`webhook`（HTTP POST）或 `none`。
- `delivery.channel`：`whatsapp` / `telegram` / `discord` / `slack` / `mattermost`（插件）/ `signal` / `imessage` / `last`。
- `delivery.to`：频道特定的接收者目标。

``announce`` 交付仅对隔离型任务（``sessionTarget: "isolated"``）有效。  
``webhook`` 交付对主任务和隔离型任务均有效。

如果省略 ``delivery.channel`` 或 ``delivery.to``，cron 可回退至主会话的“最后路由”（即 agent 最后一次响应的位置）。

目标格式提醒：

- Slack/Discord/Mattermost（插件）目标应使用显式前缀（例如 ``channel:<id>``、``user:<id>``），以避免歧义。  
- Telegram 主题应采用 ``:topic:`` 格式（见下文）。

#### Telegram 交付目标（主题 / 论坛帖子）

Telegram 通过 ``message_thread_id`` 支持论坛主题。对于 cron 交付，您可将主题/帖子编码进 ``to`` 字段：

- ``-1001234567890``（仅聊天 ID）  
- ``-1001234567890:topic:123``（推荐：显式主题标识符）  
- ``-1001234567890:123``（简写：数字后缀）

也支持带前缀的目标，例如 ``telegram:...`` / ``telegram:group:...``：

- ``telegram:group:-1001234567890:topic:123``

## 工具调用的 JSON Schema

在直接调用 Gateway ``cron.*`` 工具时（agent 工具调用或 RPC），请使用以下结构。  
CLI 标志接受人类可读的持续时间格式（如 ``20m``），但工具调用中，``schedule.at`` 应使用 ISO 8601 字符串，``schedule.everyMs`` 应使用毫秒数。

### `cron.add` 参数

一次性、主会话任务（系统事件）：

````json
{
  "name": "Reminder",
  "schedule": { "kind": "at", "at": "2026-02-01T16:00:00Z" },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": { "kind": "systemEvent", "text": "Reminder text" },
  "deleteAfterRun": true
}
````

周期性、带交付功能的隔离型任务：

````json
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
````

说明：

- ``schedule.kind``：``at``（``at``）、``every``（``everyMs``）或 ``cron``（``expr``，可选 ``tz``）。  
- ``schedule.at`` 接受 ISO 8601 格式（时区为可选；若省略，则视为 UTC）。  
- ``everyMs`` 单位为毫秒。  
- ``sessionTarget`` 必须为 ``"main"`` 或 ``"isolated"``，且必须与 ``payload.kind`` 匹配。  
- 可选字段：``agentId``、``description``、``enabled``、``deleteAfterRun``（对 ``at`` 默认为 `true`）、``delivery``。  
- ``wakeMode`` 在省略时默认为 ``"now"``。

### `cron.update` 参数

````json
{
  "jobId": "job-123",
  "patch": {
    "enabled": false,
    "schedule": { "kind": "every", "everyMs": 3600000 }
  }
}
````

说明：

- ``jobId`` 是规范形式；``id`` 为兼容性而保留。  
- 在 patch 中使用 ``agentId: null`` 可清除 agent 绑定。

### `cron.run` 和 `cron.remove` 参数

````json
{ "jobId": "job-123", "mode": "force" }
````

````json
{ "jobId": "job-123" }
````

## 存储与历史记录

- 任务存储：``~/.openclaw/cron/jobs.json``（Gateway 托管的 JSON）。  
- 运行历史：``~/.openclaw/cron/runs/<jobId>.jsonl``（JSONL 格式，按文件大小和行数自动裁剪）。  
- ``sessions.json`` 中的隔离型 cron 运行会话按 ``cron.sessionRetention`` 裁剪（默认为 ``24h``；设置 ``false`` 可禁用）。  
- 覆盖存储路径：在配置中设置 ``cron.store``。

## 重试策略

当任务失败时，OpenClaw 将错误分类为 **临时性**（可重试）或 **永久性**（立即禁用）。

### 临时性错误（将重试）

- 速率限制（429、请求过多、资源耗尽）  
- 提供商过载（例如 Anthropic ``529 overloaded_error``、过载回退摘要）  
- 网络错误（超时、ECONNRESET、fetch 失败、socket）  
- 服务器错误（5xx）  
- Cloudflare 相关错误  

### 永久性错误（不重试）

- 认证失败（API 密钥无效、未授权）  
- 配置或验证错误  
- 其他非临时性错误  

### 默认行为（无显式配置）

**一次性任务（``schedule.kind: "at"``）：**

- 遇临时性错误：最多重试 3 次，采用指数退避（30 秒 → 1 分钟 → 5 分钟）。  
- 遇永久性错误：立即禁用。  
- 成功或跳过时：禁用（若启用 ``deleteAfterRun: true``，则删除）。

**周期性任务（``cron`` / ``every``）：**

- 遇任何错误：在下次预定运行前应用指数退避（30 秒 → 1 分钟 → 5 分钟 → 15 分钟 → 60 分钟）。  
- 任务保持启用状态；下次成功运行后，退避计时器重置。

可通过配置 ``cron.retry`` 覆盖上述默认行为（参见 [配置](/automation/cron-jobs#configuration)）。

## 配置

````json5
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
````

运行日志裁剪行为：

- ``cron.runLog.maxBytes``：裁剪前运行日志文件的最大大小。  
- ``cron.runLog.keepLines``：裁剪时仅保留最新的 N 行。  
- 以上两项均适用于 ``cron/runs/<jobId>.jsonl`` 文件。

Webhook 行为：

- 推荐方式：为每个任务单独设置 ``delivery.mode: "webhook"`` 并指定 ``delivery.to: "https://..."``。  
- Webhook URL 必须为有效的 ``http://`` 或 ``https://`` URL。  
- 发送时，负载为 cron 完成事件的 JSON。  
- 若设置了 ``cron.webhookToken``，认证头为 ``Authorization: Bearer <cron.webhookToken>``。  
- 若未设置 ``cron.webhookToken``，则不发送 ``Authorization`` 头。  
- 已弃用的回退方式：已存档的旧版任务若含 ``notify: true``，仍将使用 ``cron.webhook``（若存在）。

完全禁用 cron：

- ``cron.enabled: false``（配置项）  
- ``OPENCLAW_SKIP_CRON=1``（环境变量）

## 维护

Cron 内置两条维护路径：隔离型运行会话保留策略与运行日志裁剪。

### 默认值

- ``cron.sessionRetention``：``24h``（设置 ``false`` 可禁用运行会话裁剪）  
- ``cron.runLog.maxBytes``：``2_000_000`` 字节  
- ``cron.runLog.keepLines``：``2000``

### 工作原理

- 隔离型运行会创建会话条目（``...:cron:<jobId>:run:<uuid>``）及转录文件。  
- 清理器（reaper）将移除早于 ``cron.sessionRetention`` 的过期运行会话条目。  
- 对于会话存储中不再引用的已删除运行会话，OpenClaw 将归档其转录文件，并在同一保留窗口内清理旧的已归档文件。  
- 每次追加运行日志后，都会对 ``cron/runs/<jobId>.jsonl`` 进行大小检查：  
  - 若文件大小超过 ``runLog.maxBytes``，则裁剪为最新的 ``runLog.keepLines`` 行。

### 高频调度器的性能注意事项

高频 cron 设置可能产生庞大的运行会话与运行日志数据量。虽然内置了维护机制，但宽松的限制仍可能导致不必要的 I/O 开销与清理工作。

需关注事项：

- 较长的 ``cron.sessionRetention`` 窗口内存在大量隔离型运行  
- 较高的 ``cron.runLog.keepLines`` 与较大的 ``runLog.maxBytes`` 同时出现  
- 大量嘈杂的周期性任务向同一 ``cron/runs/<jobId>.jsonl`` 写入日志  

建议操作：

- 将 ``cron.sessionRetention`` 缩短至满足调试/审计需求的最小值  
- 通过合理的 ``runLog.maxBytes`` 和 ``runLog.keepLines`` 控制运行日志大小  
- 将嘈杂的后台任务迁移至隔离模式，并配置交付规则以避免不必要的消息干扰  
- 定期使用 ``openclaw cron runs`` 检查增长趋势，并在日志变大前调整保留策略  

### 自定义示例

保留运行会话一周，并允许更大的运行日志：

````json5
{
  cron: {
    sessionRetention: "7d",
    runLog: {
      maxBytes: "10mb",
      keepLines: 5000,
    },
  },
}
````

禁用隔离型运行会话裁剪，但保留运行日志裁剪：

````json5
{
  cron: {
    sessionRetention: false,
    runLog: {
      maxBytes: "5mb",
      keepLines: 3000,
    },
  },
}
````

针对高频 cron 使用场景进行调优（示例）：

````json5
{
  cron: {
    sessionRetention: "12h",
    runLog: {
      maxBytes: "3mb",
      keepLines: 1500,
    },
  },
}
````

## CLI 快速入门

一次性提醒（UTC ISO 格式，成功后自动删除）：

````bash
openclaw cron add \
  --name "Send reminder" \
  --at "2026-01-12T18:00:00Z" \
  --session main \
  --system-event "Reminder: submit expense report." \
  --wake now \
  --delete-after-run
````

一次性提醒（主会话，立即唤醒）：

````bash
openclaw cron add \
  --name "Calendar check" \
  --at "20m" \
  --session main \
  --system-event "Next heartbeat: check calendar." \
  --wake now
````

周期性隔离型任务（向 WhatsApp 发送通知）：

````bash
openclaw cron add \
  --name "Morning status" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize inbox + calendar for today." \
  --announce \
  --channel whatsapp \
  --to "+15551234567"
````

带显式 30 秒错峰的周期性 cron 任务：

````bash
openclaw cron add \
  --name "Minute watcher" \
  --cron "0 * * * * *" \
  --tz "UTC" \
  --stagger 30s \
  --session isolated \
  --message "Run minute watcher checks." \
  --announce
````

周期性隔离型任务（交付至 Telegram 主题）：

````bash
openclaw cron add \
  --name "Nightly summary (topic)" \
  --cron "0 22 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize today; send to the nightly topic." \
  --announce \
  --channel telegram \
  --to "-1001234567890:topic:123"
````

带模型与推理覆盖的隔离型任务：

````bash
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
````

Agent 选择（多 Agent 场景）：

手动运行（强制运行是默认行为，仅在到期时运行请使用 `--due`）：

```bash
openclaw cron run <jobId>
openclaw cron run <jobId> --due
```

编辑现有任务（补丁字段）：

```bash
openclaw cron edit <jobId> \
  --message "Updated prompt" \
  --model "opus" \
  --thinking low
```

强制现有定时任务严格按照计划时间运行（无延迟）：

```bash
openclaw cron edit <jobId> --exact
```

运行历史：

```bash
openclaw cron runs --id <jobId> --limit 50
```

不创建任务的即时系统事件：

```bash
openclaw system event --mode now --text "Next heartbeat: check battery."
```

## 网关 API 接口

- `cron.list`、`cron.status`、`cron.add`、`cron.update`、`cron.remove`
- `cron.run`（强制或到期触发）、`cron.runs`  
  对于不创建任务的即时系统事件，请使用 [`openclaw system event`](/cli/system)。

## 故障排除

### “没有任何任务运行”

- 检查 cron 是否已启用：`cron.enabled` 和 `OPENCLAW_SKIP_CRON`。
- 检查网关是否持续运行（cron 在网关进程内运行）。
- 对于 `cron` 类型的调度：确认时区设置（`--tz`）与宿主机时区是否一致。

### 周期性任务在失败后持续延迟

- OpenClaw 对连续出错的周期性任务应用指数退避重试策略：  
  重试间隔依次为 30 秒、1 分钟、5 分钟、15 分钟，之后固定为 60 分钟。
- 下一次成功运行后，退避计时将自动重置。
- 单次执行（`at`）任务会对临时性错误（如速率限制、过载、网络问题、server_error）最多重试 3 次（含退避）；而对永久性错误则立即禁用任务。参见 [重试策略](/automation/cron-jobs#retry-policy)。

### Telegram 消息投递到错误位置

- 对于论坛主题，请显式使用 `-100…:topic:<id>`，以确保无歧义。
- 若在日志或已存储的“最后路由”目标中看到 `telegram:...` 前缀，属正常现象；  
  定时任务投递机制支持该格式，并仍能正确解析主题 ID。

### 子代理通告投递重试

- 当子代理运行完成时，网关会向请求方会话通告执行结果。
- 若通告流程返回 `false`（例如请求方会话正忙），网关将通过 `announceRetryCount` 进行跟踪，并最多重试 3 次。
- 超过 `endedAt` 后 5 分钟的通告将被强制过期，以防陈旧条目无限循环。
- 若在日志中观察到重复的通告投递，请检查子代理注册表中是否存在 `announceRetryCount` 值较高的条目。