---
summary: "Guidance for choosing between heartbeat and cron jobs for automation"
read_when:
  - Deciding how to schedule recurring tasks
  - Setting up background monitoring or notifications
  - Optimizing token usage for periodic checks
title: "Cron vs Heartbeat"
---
# Cron 与 Heartbeat：何时使用每个工具

Cron 任务和 Heartbeat 都允许你按计划运行任务。本指南将帮助你为特定使用场景选择合适的机制。

## 快速决策指南

| 使用场景                             | 推荐使用         | 原因                                      |
| ------------------------------------ | ----------------- | ---------------------------------------- |
| 每 30 分钟检查收件箱             | Heartbeat           | 与其他检查合并处理，上下文感知 |
| 早上 9 点准时发送日报       | Cron (隔离模式)     | 需要精确时间                      |
| 监控日历以获取即将发生的事件 | Heartbeat           | 适合周期性感知的自然选择       |
| 每周运行深度分析             | Cron (隔离模式)     | 独立任务，可使用不同模型 |
| 20 分钟后提醒我              | Cron (主模式, `--at`) | 单次执行，需要精确时间             |
| 背景项目健康检查      | Heartbeat           | 依附于现有周期进行监控             |

## Heartbeat：周期性感知

Heartbeat 在 **主会话** 中以固定间隔运行（默认：30 分钟）。它专为代理检查事物并呈现重要信息而设计。

### 何时使用 Heartbeat

- **多个周期性检查**：而不是 5 个独立的 Cron 任务检查收件箱、日历、天气、通知和项目状态，一个 Heartbeat 可以合并处理所有这些任务。
- **上下文感知决策**：代理拥有完整的主会话上下文，因此可以智能判断哪些任务紧急，哪些可以稍后处理。
- **对话连续性**：Heartbeat 任务共享同一个会话，因此代理可以记住最近的对话并自然地跟进。
- **低开销监控**：一个 Heartbeat 替代多个小型轮询任务。

### Heartbeat 优势

- **合并多个检查**：一个代理回合可以同时检查收件箱、日历和通知。
- **减少 API 调用**：一个 Heartbeat 比 5 个独立 Cron 任务更便宜。
- **上下文感知**：代理知道你最近在做什么，可以据此优先处理任务。
- **智能抑制**：如果无需关注，代理会回复 `HEARTBEAT_OK` 并不发送消息。
- **自然时间安排**：根据队列负载略有偏移，对大多数监控来说是可以接受的。

### Heartbeat 示例：HEARTBEAT.md 检查清单

```md
# Heartbeat 检查清单

- 检查邮箱中的紧急消息
- 查看接下来 2 小时的日历事件
- 如果背景任务完成，总结结果
- 如果空闲 8 小时以上，发送简要检查
```

代理在每次 Heartbeat 时读取此清单并在一个回合内处理所有项目。

### 配置 Heartbeat

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 间隔
        target: "last", // 通知的发送位置
        activeHours: { start: "08:00", end: "22:00" }, // 可选
      },
    },
  },
}
```

详见 [Heartbeat](/gateway/heartbeat) 获取完整配置。

## Cron：精确调度

Cron 任务在 **精确时间** 运行，并且可以在隔离会话中运行，不会影响主上下文。

### 何时使用 Cron

- **需要精确时间**：如“每周一早上 9 点发送此消息”（而不是“大约 9 点”）。
- **独立任务**：不需要对话上下文的任务。
- **不同模型/思考方式**：需要更强大模型的复杂分析。
- **单次提醒**：使用 `--at` 的“20 分钟后提醒我”。
- **嘈杂/频繁任务**：不会干扰主会话历史的任务。
- **外部触发**：无论代理是否处于活动状态，任务都应独立运行。

### Cron 优势

- **精确时间**：支持 5 字段的 Cron 表达式和时区。
- **会话隔离**：在 `cron:<jobId>` 中运行，不会污染主会话历史。
- **不同模型或思考设置**：可使用更便宜的模型。
- **输出直接发送到频道**：（摘要仍默认发布到主会话）。
- **不会干扰主会话的历史记录**。

### Cron 示例

```bash
openclaw cron add \
  --name "检查项目" \
  --every "4h" \
  --session main \
  --system-event "项目健康检查时间到了" \
  --wake now
```

### 何时使用隔离模式的 Cron

使用 `--session isolated` 时：

- **干净的初始状态**：没有先前上下文。
- **不同的模型或思考设置**。
- **输出直接发送到频道**（摘要仍默认发布到主会话）。
- **不会干扰主会话的历史记录**。

```bash
openclaw cron add \
  --name "深度分析" \
  --cron "0 6 * * 0" \
  --session isolated \
  --message "每周代码库分析..." \
  --model opus \
  --thinking high \
  --deliver
```

## 成本考虑

| 机制       | 成本特性                                            |
| ----------- | ------------------------------------------------------- |
| Heartbeat       | 每 N 分钟一次操作；与 HEARTBEAT.md 大小成正比 |
| Cron (主)     | 将事件添加到下一个 Heartbeat（无隔离操作）         |
| Cron (隔离) | 每个任务一次完整代理操作；可使用更便宜的模型          |

**提示**：

- 保持 `HEARTBEAT.md` 小以减少 token 开销。
- 将相似检查合并到 Heartbeat 而不是多个 Cron 任务。
- 如果仅需内部处理，使用 `target: "none"`。
- 对常规任务使用隔离模式的 Cron 并使用更便宜的模型。

## 相关链接

- [Heartbeat](