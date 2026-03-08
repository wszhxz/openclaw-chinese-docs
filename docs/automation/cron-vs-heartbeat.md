---
summary: "Guidance for choosing between heartbeat and cron jobs for automation"
read_when:
  - Deciding how to schedule recurring tasks
  - Setting up background monitoring or notifications
  - Optimizing token usage for periodic checks
title: "Cron vs Heartbeat"
---
# Cron vs Heartbeat：何时使用哪一个

心跳（Heartbeat）和 Cron 任务都允许你按计划运行任务。本指南帮助你为用例选择正确的机制。

## 快速决策指南

| 用例                             | 推荐方案                  | 原因                                      |
| -------------------------------- | ------------------- | ---------------------------------------- |
| 每 30 分钟检查收件箱             | Heartbeat           | 与其他检查批量处理，感知上下文 |
| 每天上午 9 点准时发送日报       | Cron (isolated)     | 需要精确时间                      |
| 监控日历以获取即将发生的事件 | Heartbeat           | 周期性感知的自然契合       |
| 运行每周深度分析             | Cron (isolated)     | 独立任务，可使用不同模型 |
| 20 分钟后提醒我              | Cron (main, `--at`) | 带精确时间的一次性任务             |
| 后台项目健康检查      | Heartbeat           | 依附于现有周期             |

## Heartbeat：周期性感知

Heartbeat 在 **主会话** 中以固定间隔运行（默认：30 分钟）。它们旨在让 Agent 检查各项事务并呈现任何重要内容。

### 何时使用 Heartbeat

- **多个周期性检查**：与其使用 5 个独立的 Cron 任务分别检查收件箱、日历、天气、通知和项目状态，单个 Heartbeat 可以批量处理所有这些任务。
- **感知上下文的决策**：Agent 拥有完整的主会话上下文，因此它可以就什么是紧急的、什么可以等待做出明智的决策。
- **对话连续性**：Heartbeat 运行共享同一个会话，因此 Agent 会记住最近的对话并能自然地跟进。
- **低开销监控**：一个 Heartbeat 取代了许多小型轮询任务。

### Heartbeat 优势

- **批量多个检查**：一次 Agent 操作可以一起审查收件箱、日历和通知。
- **减少 API 调用**：单个 Heartbeat 比 5 个独立的 Cron 任务更便宜。
- **感知上下文**：Agent 知道你正在做什么，并据此进行优先级排序。
- **智能抑制**：如果没有任何需要注意的事项，Agent 回复 `HEARTBEAT_OK` 且不发送消息。
- **自然时机**：根据队列负载略有漂移，这对大多数监控来说是可以接受的。

### Heartbeat 示例：HEARTBEAT.md 清单

```md
# Heartbeat checklist

- Check email for urgent messages
- Review calendar for events in next 2 hours
- If a background task finished, summarize results
- If idle for 8+ hours, send a brief check-in
```

Agent 在每个 Heartbeat 上读取此内容并在一次操作中处理所有项目。

### 配置 Heartbeat

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // interval
        target: "last", // explicit alert delivery target (default is "none")
        activeHours: { start: "08:00", end: "22:00" }, // optional
      },
    },
  },
}
```

有关完整配置，请参阅 [Heartbeat](/gateway/heartbeat)。

## Cron：精确调度

Cron 任务在精确时间运行，并且可以在隔离会话中运行而不影响主上下文。
重复的整点计划会自动通过确定性
每个任务的偏移量在 0-5 分钟的窗口内分散。

### 何时使用 Cron

- **需要精确时间**：“每周一上午 9:00 发送此内容”（而不是“9 点左右”）。
- **独立任务**：不需要对话上下文的任务。
- **不同的模型/思维**：值得使用更强大模型的繁重分析。
- **一次性提醒**：“20 分钟后提醒我”，配合 `--at`。
- **嘈杂/频繁任务**：会弄乱主会话历史的任务。
- **外部触发器**：无论 Agent 是否处于活动状态都应独立运行的任务。

### Cron 优势

- **精确时间**：支持时区的 5 字段或 6 字段（秒）Cron 表达式。
- **内置负载分散**：默认的重复整点计划最多交错 5 分钟。
- **按任务控制**：使用 `--stagger <duration>` 覆盖交错，或使用 `--exact` 强制精确时间。
- **会话隔离**：在 `cron:<jobId>` 中运行，不会污染主历史。
- **模型覆盖**：为每个任务使用更便宜或更强大的模型。
- **交付控制**：隔离任务默认为 `announce`（摘要）；根据需要选择 `none`。
- **即时交付**：广播模式直接发布，无需等待 Heartbeat。
- **不需要 Agent 上下文**：即使主会话空闲或压缩也会运行。
- **一次性支持**：用于精确未来时间戳的 `--at`。

### Cron 示例：每日早晨简报

```bash
openclaw cron add \
  --name "Morning briefing" \
  --cron "0 7 * * *" \
  --tz "America/New_York" \
  --session isolated \
  --message "Generate today's briefing: weather, calendar, top emails, news summary." \
  --model opus \
  --announce \
  --channel whatsapp \
  --to "+15551234567"
```

这将在纽约时间上午 7:00 精确运行，使用 Opus 保证质量，并直接将摘要广播到 WhatsApp。

### Cron 示例：一次性提醒

```bash
openclaw cron add \
  --name "Meeting reminder" \
  --at "20m" \
  --session main \
  --system-event "Reminder: standup meeting starts in 10 minutes." \
  --wake now \
  --delete-after-run
```

有关完整的 CLI 参考，请参阅 [Cron jobs](/automation/cron-jobs)。

## 决策流程图

```
Does the task need to run at an EXACT time?
  YES -> Use cron
  NO  -> Continue...

Does the task need isolation from main session?
  YES -> Use cron (isolated)
  NO  -> Continue...

Can this task be batched with other periodic checks?
  YES -> Use heartbeat (add to HEARTBEAT.md)
  NO  -> Use cron

Is this a one-shot reminder?
  YES -> Use cron with --at
  NO  -> Continue...

Does it need a different model or thinking level?
  YES -> Use cron (isolated) with --model/--thinking
  NO  -> Use heartbeat
```

## 结合两者

最高效的设置使用 **两者**：

1. **Heartbeat** 处理常规监控（收件箱、日历、通知），每 30 分钟在一个批量操作中完成。
2. **Cron** 处理精确计划（日报、周回顾）和一次性提醒。

### 示例：高效自动化设置

**HEARTBEAT.md**（每 30 分钟检查）：

```md
# Heartbeat checklist

- Scan inbox for urgent emails
- Check calendar for events in next 2h
- Review any pending tasks
- Light check-in if quiet for 8+ hours
```

**Cron 任务**（精确时间）：

```bash
# Daily morning briefing at 7am
openclaw cron add --name "Morning brief" --cron "0 7 * * *" --session isolated --message "..." --announce

# Weekly project review on Mondays at 9am
openclaw cron add --name "Weekly review" --cron "0 9 * * 1" --session isolated --message "..." --model opus

# One-shot reminder
openclaw cron add --name "Call back" --at "2h" --session main --system-event "Call back the client" --wake now
```

## Lobster：具有审批的确定性工作流

Lobster 是 **多步骤工具管道** 的工作流运行时，需要确定性执行和显式审批。
当任务超过单次 Agent 操作，且您希望有一个带有人工检查点的可恢复工作流时使用它。

### 何时适合使用 Lobster

- **多步骤自动化**：您需要固定的工具调用管道，而不是临时提示。
- **审批关卡**：副作用应暂停直到您批准，然后恢复。
- **可恢复运行**：继续暂停的工作流而无需重新运行早期步骤。

### 它与 Heartbeat 和 Cron 的配合方式

- **Heartbeat/Cron** 决定 _何时_ 运行。
- **Lobster** 定义 _哪些步骤_ 在运行开始后发生。

对于计划工作流，使用 Cron 或 Heartbeat 触发调用 Lobster 的 Agent 操作。
对于临时工作流，直接调用 Lobster。

### 操作说明（来自代码）

- Lobster 作为 **本地子进程** (`lobster` CLI) 以工具模式运行并返回 **JSON 信封**。
- 如果工具返回 `needs_approval`，您使用 `resumeToken` 和 `approve` 标志恢复。
- 该工具是 **可选插件**；通过 `tools.alsoAllow: ["lobster"]` 以添加方式启用（推荐）。
- Lobster 期望 `lobster` CLI 在 `PATH` 上可用。

有关完整用法和示例，请参阅 [Lobster](/tools/lobster)。

## 主会话与隔离会话

Heartbeat 和 Cron 都可以与主会话交互，但方式不同：

|         | Heartbeat                       | Cron (main)              | Cron (isolated)            |
| ------- | ------------------------------- | ------------------------ | -------------------------- |
| 会话 | 主                              | 主（通过系统事件）  | `cron:<jobId>`             |
| 历史 | 共享                          | 共享                   | 每次运行新建             |
| 上下文 | 完整                            | 完整                     | 无（从头开始）        |
| 模型   | 主会话模型              | 主会话模型       | 可以覆盖               |
| 输出  | 如果不为 `HEARTBEAT_OK` 则发送 | Heartbeat 提示 + 事件 | 广播摘要（默认） |

### 何时使用主会话 Cron

当您想要以下情况时使用 `--session main` 配合 `--system-event`：

- 提醒/事件出现在主会话上下文中
- Agent 在下一个 Heartbeat 期间使用完整上下文处理它
- 没有单独的隔离运行

```bash
openclaw cron add \
  --name "Check project" \
  --every "4h" \
  --session main \
  --system-event "Time for a project health check" \
  --wake now
```

### 何时使用隔离 Cron

当您想要以下情况时使用 `--session isolated`：

- 干净的起点，没有先前的上下文
- 不同的模型或思维设置
- 直接将广播摘要发送到频道
- 不弄乱主会话的历史

```bash
openclaw cron add \
  --name "Deep analysis" \
  --cron "0 6 * * 0" \
  --session isolated \
  --message "Weekly codebase analysis..." \
  --model opus \
  --thinking high \
  --announce
```

## 成本考量

| 机制             | 成本概况                                              |
| --------------- | ------------------------------------------------------- |
| Heartbeat       | 每 N 分钟执行一次 Agent 回合；随 HEARTBEAT.md 大小扩展 |
| Cron (主)       | 将事件添加到下一个 Heartbeat（无独立 Agent 回合）      |
| Cron (独立)     | 每个作业执行完整的 Agent 回合；可使用更便宜的 Model    |

**提示**：

- 保持 `HEARTBEAT.md` 较小以最小化 Token 开销。
- 将类似检查批量合并到 Heartbeat 中，而不是使用多个 Cron 作业。
- 如果仅需内部处理，请在 Heartbeat 上使用 `target: "none"`。
- 对于常规任务，请使用带有更便宜 Model 的独立 Cron。

## 相关

- [Heartbeat](/gateway/heartbeat) - 完整 Heartbeat 配置
- [Cron 作业](/automation/cron-jobs) - 完整 Cron CLI 和 API 参考
- [System](/cli/system) - 系统事件 + Heartbeat 控制