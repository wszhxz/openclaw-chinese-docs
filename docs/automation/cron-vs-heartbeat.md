---
summary: "Guidance for choosing between heartbeat and cron jobs for automation"
read_when:
  - Deciding how to schedule recurring tasks
  - Setting up background monitoring or notifications
  - Optimizing token usage for periodic checks
title: "Cron vs Heartbeat"
---
# Cron 与 Heartbeat：何时使用哪一种

Heartbeat 和 Cron 任务均可按计划运行任务。本指南将帮助您为具体用例选择合适的机制。

## 快速决策指南

| 使用场景                             | 推荐方式         | 原因                                      |
| ------------------------------------ | ------------------- | ---------------------------------------- |
| 每 30 分钟检查收件箱                 | Heartbeat           | 可与其他检查批量处理，具备上下文感知能力 |
| 每天上午 9 点整准时发送日报           | Cron（隔离式）      | 需要精确时间控制                          |
| 监控日历中即将发生的事件             | Heartbeat           | 天然适配周期性状态感知                     |
| 执行每周深度分析                     | Cron（隔离式）      | 独立任务，可使用不同模型                   |
| 提醒我 20 分钟后                      | Cron（主会话，`--at`） | 单次触发，需精确计时                       |
| 后台项目健康检查                     | Heartbeat           | 可复用现有执行周期                         |

## Heartbeat：周期性状态感知

Heartbeat 在 **主会话** 中以固定间隔运行（默认：30 分钟）。其设计目标是让智能体定期检查各项状态，并主动呈现重要信息。

### 何时使用 Heartbeat

- **多项周期性检查**：无需分别设置 5 个 Cron 任务来检查收件箱、日历、天气、通知和项目状态，单个 Heartbeat 即可批量完成全部检查。
- **上下文感知型决策**：智能体拥有完整的主会话上下文，因此能智能判断哪些事项紧急、哪些可延后处理。
- **对话连续性**：所有 Heartbeat 运行共享同一会话，因此智能体能记住最近的对话内容，并自然地进行后续跟进。
- **低开销监控**：一个 Heartbeat 即可替代多个轻量级轮询任务。

### Heartbeat 的优势

- **批量执行多项检查**：一次智能体交互即可同时审阅收件箱、日历和通知。
- **减少 API 调用次数**：单次 Heartbeat 比 5 个独立 Cron 任务成本更低。
- **上下文感知**：智能体了解您当前的工作内容，从而相应调整优先级。
- **智能抑制机制**：若无须关注事项，智能体将回复 `HEARTBEAT_OK`，且不发送任何消息。
- **自然的时间弹性**：执行时间会根据队列负载略有浮动，这对大多数监控场景完全可接受。

### Heartbeat 示例：HEARTBEAT.md 检查清单

```md
# Heartbeat checklist

- Check email for urgent messages
- Review calendar for events in next 2 hours
- If a background task finished, summarize results
- If idle for 8+ hours, send a brief check-in
```

智能体每次 Heartbeat 时读取该文件，并在单次交互中处理全部条目。

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

完整配置说明请参阅 [Heartbeat](/gateway/heartbeat)。

## Cron：精确调度

Cron 任务在精确时刻运行，且可在隔离会话中执行，不影响主会话上下文。  
每小时整点重复执行的任务会通过确定性的每任务偏移量，在 0–5 分钟窗口内自动错峰。

### 何时使用 Cron

- **需要精确时间控制**：“每周一上午 9:00 发送此内容”（而非“大约上午 9 点”）。
- **独立任务**：无需对话上下文的任务。
- **差异化模型/推理方式**：需更强大模型支持的重型分析任务。
- **单次提醒**：如“20 分钟后提醒我”，配合 `--at`。
- **高频率/干扰性强的任务**：可能污染主会话历史记录的任务。
- **外部触发器**：应独立于智能体是否处于活跃状态而运行的任务。

### Cron 的优势

- **精确时间控制**：支持 5 字段或 6 字段（含秒）Cron 表达式，并支持时区。
- **内置负载分散机制**：每小时整点重复任务默认最多错峰 5 分钟。
- **每任务独立控制**：可通过 `--stagger <duration>` 覆盖错峰设置，或通过 `--exact` 强制精确执行。
- **会话隔离**：在 `cron:<jobId>` 中运行，不污染主会话历史。
- **模型覆盖能力**：可为每个任务单独指定更经济或更强大的模型。
- **交付控制**：隔离任务默认采用 `announce`（摘要模式）；可根据需要选择 `none`。
- **即时交付**：Announce 模式直接发布，无需等待 Heartbeat。
- **无需智能体上下文**：即使主会话处于空闲或已压缩状态，仍可正常运行。
- **单次触发支持**：通过 `--at` 支持精确的未来时间戳。

### Cron 示例：每日晨间简报

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

该任务将在纽约时间每天上午 7:00 精确执行，使用 Opus 模型保障质量，并直接向 WhatsApp 发送摘要公告。

### Cron 示例：单次提醒

```bash
openclaw cron add \
  --name "Meeting reminder" \
  --at "20m" \
  --session main \
  --system-event "Reminder: standup meeting starts in 10 minutes." \
  --wake now \
  --delete-after-run
```

完整 CLI 参考请参阅 [Cron jobs](/automation/cron-jobs)。

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

## 同时结合两者使用

最高效的方案是 **同时使用两者**：

1. **Heartbeat** 每 30 分钟批量处理常规监控任务（收件箱、日历、通知）；
2. **Cron** 处理精确时间要求的任务（日报、周度回顾）及单次提醒。

### 示例：高效自动化配置

**HEARTBEAT.md**（每 30 分钟检查一次）：

```md
# Heartbeat checklist

- Scan inbox for urgent emails
- Check calendar for events in next 2h
- Review any pending tasks
- Light check-in if quiet for 8+ hours
```

**Cron 任务**（精确时间控制）：

```bash
# Daily morning briefing at 7am
openclaw cron add --name "Morning brief" --cron "0 7 * * *" --session isolated --message "..." --announce

# Weekly project review on Mondays at 9am
openclaw cron add --name "Weekly review" --cron "0 9 * * 1" --session isolated --message "..." --model opus

# One-shot reminder
openclaw cron add --name "Call back" --at "2h" --session main --system-event "Call back the client" --wake now
```

## Lobster：带审批的确定性工作流

Lobster 是面向 **多步骤工具流水线** 的工作流运行时，专为需要确定性执行与显式人工审批的场景而设计。当任务超出单次智能体交互范畴，且您需要支持人工检查点的可恢复工作流时，请选用 Lobster。

### Lobster 的适用场景

- **多步骤自动化**：您需要固定的工具调用流水线，而非一次性提示词。
- **审批关卡**：副作用操作应在获得您批准后暂停，再继续执行。
- **可恢复运行**：可从中断处继续工作流，无需重跑先前步骤。

### 与 Heartbeat 和 Cron 的协同方式

- **Heartbeat/Cron** 决定运行的 **时机**；
- **Lobster** 定义运行启动后的 **具体步骤**。

对于定时工作流，可使用 Cron 或 Heartbeat 触发一次智能体交互，再由该交互调用 Lobster；  
对于临时性工作流，则可直接调用 Lobster。

### 运行说明（来自代码）

- Lobster 以 **本地子进程**（`lobster` CLI）方式在工具模式下运行，并返回一个 **JSON 封套**。
- 若工具返回 `needs_approval`，您需使用 `resumeToken` 并带上 `approve` 标志来恢复执行。
- 该工具为 **可选插件**；建议通过 `tools.alsoAllow: ["lobster"]` 增量启用。
- Lobster 要求系统路径 `PATH` 中存在 `lobster` CLI。

完整用法与示例请参阅 [Lobster](/tools/lobster)。

## 主会话 vs 隔离会话

Heartbeat 和 Cron 均可与主会话交互，但方式不同：

|         | Heartbeat                       | Cron（主会话）              | Cron（隔离式）            |
| ------- | ------------------------------- | ------------------------ | -------------------------- |
| 会话     | 主会话                           | 主会话（通过系统事件）      | `cron:<jobId>`             |
| 历史记录 | 共享                             | 共享                      | 每次运行均为全新历史          |
| 上下文     | 完整                             | 完整                      | 无（从干净状态开始）         |
| 模型       | 主会话所用模型                    | 主会话所用模型             | 可覆盖                      |
| 输出       | 若非 `HEARTBEAT_OK` 则交付     | Heartbeat 提示 + 事件       | Announce 摘要（默认）        |

### 何时使用主会话 Cron

当您希望满足以下条件时，请使用 `--session main` 并搭配 `--system-event`：

- 提醒/事件显示在主会话上下文中；
- 智能体在下次 Heartbeat 期间、利用完整上下文处理该事件；
- 不启动额外的隔离式运行。

```bash
openclaw cron add \
  --name "Check project" \
  --every "4h" \
  --session main \
  --system-event "Time for a project health check" \
  --wake now
```

### 何时使用隔离式 Cron

当您希望满足以下条件时，请使用 `--session isolated`：

- 从干净状态开始，不继承先前上下文；
- 使用不同模型或推理配置；
- 直接向某个频道推送 Announce 摘要；
- 历史记录不混入主会话。

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

| 机制            | 开销特征                                                |
| --------------- | ------------------------------------------------------- |
| 心跳（Heartbeat） | 每 N 分钟执行一次轮询；开销随 HEARTBEAT.md 文件大小而变化 |
| Cron（主）      | 将事件添加至下一次心跳中（不触发独立轮询）               |
| Cron（隔离）    | 每个任务均触发一次完整的 Agent 轮询；可使用成本更低的模型 |

**提示**：

- 将 `HEARTBEAT.md` 保持较小，以最小化 token 开销。
- 将相似的检查批量合并至 heartbeat 中，而非拆分为多个 cron 任务。
- 若仅需内部处理，请在 heartbeat 中使用 `target: "none"`。
- 对于常规任务，可使用隔离型 cron 并搭配成本更低的模型。

## 相关文档

- [心跳（Heartbeat）](/gateway/heartbeat) — 完整的心跳配置说明
- [Cron 任务](/automation/cron-jobs) — 完整的 cron CLI 与 API 参考
- [系统（System）](/cli/system) — 系统事件 + 心跳控制