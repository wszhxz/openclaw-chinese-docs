---
summary: "Guidance for choosing between heartbeat and cron jobs for automation"
read_when:
  - Deciding how to schedule recurring tasks
  - Setting up background monitoring or notifications
  - Optimizing token usage for periodic checks
title: "Cron vs Heartbeat"
---
# Cron vs Heartbeat: 使用场景选择

心跳和cron作业都允许你按计划运行任务。本指南帮助你根据使用情况选择合适的机制。

## 快速决策指南

| 使用场景                             | 推荐                | 原因                                      |
| ------------------------------------ | ------------------- | ---------------------------------------- |
| 每30分钟检查一次收件箱             | Heartbeat           | 与其他检查批量处理，上下文感知 |
| 每天上午9点发送报告                | Cron (独立)         | 需要精确的时间                         |
| 监控日历上的即将发生的事件         | Heartbeat           | 定期意识的自然选择                     |
| 每周运行深度分析                   | Cron (独立)         | 独立任务，可以使用不同的模型           |
| 20分钟后提醒我                       | Cron (主, `--at`) | 单次执行，需要精确时间                 |
| 后台项目健康检查                   | Heartbeat           | 利用现有的周期                         |

## Heartbeat: 定期意识

心跳在**主会话**中以固定间隔（默认：30分钟）运行。它们旨在让代理检查事物并突出显示任何重要的内容。

### 何时使用心跳

- **多个定期检查**：与其使用5个单独的cron作业分别检查收件箱、日历、天气、通知和项目状态，一个心跳可以批量处理所有这些。
- **上下文感知决策**：代理具有完整的主会话上下文，因此可以根据紧急程度与等待事项做出明智的决策。
- **对话连续性**：心跳运行共享相同的会话，因此代理会记住最近的对话并可以自然地跟进。
- **低开销监控**：一个心跳可以替代许多小型轮询任务。

### 心跳优势

- **批量多个检查**：一个代理轮次可以一起审查收件箱、日历和通知。
- **减少API调用**：单个心跳比5个独立的cron作业更便宜。
- **上下文感知**：代理知道你在做什么，并可以相应地优先处理。
- **智能抑制**：如果没有需要关注的内容，代理回复`HEARTBEAT_OK`且不会发送消息。
- **自然时间**：根据队列负载略有偏移，这对于大多数监控来说是可以接受的。

### 心跳示例：HEARTBEAT.md 检查清单

```md
# Heartbeat checklist

- Check email for urgent messages
- Review calendar for events in next 2 hours
- If a background task finished, summarize results
- If idle for 8+ hours, send a brief check-in
```

代理在每次心跳时读取此内容并在一个轮次中处理所有项目。

### 配置心跳

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // interval
        target: "last", // where to deliver alerts
        activeHours: { start: "08:00", end: "22:00" }, // optional
      },
    },
  },
}
```

请参阅[Heartbeat](/gateway/heartbeat)获取完整配置。

## Cron: 精确调度

Cron 作业在精确时间运行，并且可以在隔离的会话中运行而不影响主上下文。
重复的每小时开始的任务会通过一个确定性的
每个作业偏移量在0-5分钟窗口内自动分散。

### 使用 cron 的情况

- **需要精确时间**：“每周一上午9:00发送”（而不是“大约9点左右”）。
- **独立任务**：不需要对话上下文的任务。
- **不同的模型/思维方式**：需要更强大模型的重型分析。
- **一次性提醒**：使用 `--at` 的“20分钟后提醒我”。
- **嘈杂/频繁的任务**：会 clutter 主会话历史的任务。
- **外部触发器**：应独立于代理是否处于活动状态而运行的任务。

### Cron 优点

- **精确时间**：支持时区的5字段或6字段（秒）cron 表达式。
- **内置负载分散**：默认情况下，重复的每小时开始的任务会在最多5分钟内分散。
- **每个作业控制**：使用 `--stagger <duration>` 覆盖分散，或使用 `--exact` 强制精确时间。
- **会话隔离**：在 `cron:<jobId>` 中运行，不会污染主历史记录。
- **模型覆盖**：每个作业可以使用更便宜或更强大的模型。
- **交付控制**：隔离的作业默认为 `announce`（摘要）；根据需要选择 `none`。
- **立即交付**：公告模式直接发布，不等待心跳。
- **不需要代理上下文**：即使主会话空闲或压缩，也会运行。
- **一次性支持**：使用 `--at` 进行精确的未来时间戳。

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

这将在纽约时间上午7:00精确运行，使用 Opus 以保证质量，并直接通过 WhatsApp 发布摘要。

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

参见 [Cron 作业](/automation/cron-jobs) 获取完整的 CLI 参考。

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

## 结合使用

最有效的设置是同时使用 **两者**：

1. **Heartbeat** 每 30 分钟处理一次批量监控（收件箱、日历、通知）。
2. **Cron** 处理精确调度（每日报告、每周审查）和一次性提醒。

### 示例：高效的自动化设置

**HEARTBEAT.md**（每 30 分钟检查一次）：

```md
# Heartbeat checklist

- Scan inbox for urgent emails
- Check calendar for events in next 2h
- Review any pending tasks
- Light check-in if quiet for 8+ hours
```

**Cron 任务**（精确计时）：

```bash
# Daily morning briefing at 7am
openclaw cron add --name "Morning brief" --cron "0 7 * * *" --session isolated --message "..." --announce

# Weekly project review on Mondays at 9am
openclaw cron add --name "Weekly review" --cron "0 9 * * 1" --session isolated --message "..." --model opus

# One-shot reminder
openclaw cron add --name "Call back" --at "2h" --session main --system-event "Call back the client" --wake now
```

## Lobster：带有审批的确定性工作流

Lobster 是用于需要确定性执行和显式审批的**多步骤工具管道**的工作流运行时。
当任务不仅仅是单个代理操作，并且您希望有一个可恢复的工作流并有人类检查点时使用它。

### Lobster 的适用场景

- **多步骤自动化**：您需要一个固定的工具调用管道，而不是一次性提示。
- **审批关卡**：副作用应在您批准之前暂停，然后继续。
- **可恢复的运行**：在不重新运行早期步骤的情况下继续暂停的工作流。

### 它如何与 heartbeat 和 cron 配对

- **Heartbeat/cron** 决定运行发生的时间。
- **Lobster** 定义运行开始后发生的**步骤**。

对于计划的工作流，使用 cron 或 heartbeat 触发一个调用 Lobster 的代理操作。
对于临时工作流，直接调用 Lobster。

### 运营说明（来自代码）

- Lobster 作为**本地子进程**（`lobster` CLI）在工具模式下运行，并返回一个**JSON 包装**。
- 如果工具返回 `needs_approval`，您可以通过 `resumeToken` 和 `approve` 标志恢复。
- 工具是一个**可选插件**；通过 `tools.alsoAllow: ["lobster"]` 启用（推荐）。
- Lobster 期望 `lobster` CLI 在 `PATH` 上可用。

参见 [Lobster](/tools/lobster) 获取完整用法和示例。

## 主会话与隔离会话

Heartbeat 和 cron 都可以与主会话交互，但方式不同：

|         | Heartbeat                       | Cron (main)              | Cron (isolated)            |
| ------- | ------------------------------- | ------------------------ | -------------------------- |
| Session | Main                            | Main (via system event)  | `cron:<jobId>`             |
| History | Shared                          | Shared                   | Fresh each run             |
| Context | Full                            | Full                     | None (starts clean)        |
| Model   | Main session model              | Main session model       | Can override               |
| Output  | Delivered if not `HEARTBEAT_OK` | Heartbeat prompt + event | Announce summary (default) |

### 何时使用主会话cron

在以下情况下使用 `--session main` 和 `--system-event` ：

- 希望提醒/事件出现在主会话上下文中
- 希望代理在下一次心跳时使用完整上下文处理它
- 不需要单独的隔离运行

```bash
openclaw cron add \
  --name "Check project" \
  --every "4h" \
  --session main \
  --system-event "Time for a project health check" \
  --wake now
```

### 何时使用隔离cron

在以下情况下使用 `--session isolated` ：

- 希望有一个没有先前上下文的干净环境
- 使用不同的模型或思考设置
- 直接向频道宣布摘要
- 不会干扰主会话的历史记录

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

## 成本考虑

| 机制        | 成本概况                                            |
| --------------- | ------------------------------------------------------- |
| Heartbeat       | 每N分钟一个回合；随HEARTBEAT.md大小缩放 |
| Cron (main)     | 将事件添加到下一个心跳（无隔离回合）         |
| Cron (isolated) | 每个作业一个完整的代理回合；可以使用更便宜的模型          |

**提示**:

- 保持 `HEARTBEAT.md` 小以减少令牌开销。
- 将类似的检查批量到心跳中而不是多个cron作业。
- 如果只需要内部处理，请在心跳中使用 `target: "none"` 。
- 对于常规任务，使用隔离cron和更便宜的模型。

## 相关

- [Heartbeat](/gateway/heartbeat) - 完整的心跳配置
- [Cron jobs](/automation/cron-jobs) - 完整的cron CLI和API参考
- [System](/cli/system) - 系统事件 + 心跳控制