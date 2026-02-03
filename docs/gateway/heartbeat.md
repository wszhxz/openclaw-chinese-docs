---
summary: "Heartbeat polling messages and notification rules"
read_when:
  - Adjusting heartbeat cadence or messaging
  - Deciding between heartbeat and cron for scheduled tasks
title: "Heartbeat"
---
# 心跳（网关）

> **心跳与Cron的区别？** 请参阅 [Cron 与 心跳](/自动化/cron-vs-heartbeat) 以了解何时使用每种方式的指导。

心跳在主会话中运行**周期性代理轮询**，以便模型可以
在不打扰您的情况下突出显示任何需要关注的内容。

## 快速入门（初学者）

1. 保持心跳启用（默认是 `30m`，或 `1h` 用于 Anthropic OAuth/设置令牌）或设置您自己的频率。
2. 在代理工作区中创建一个小型的 `HEARTBEAT.md` 检查清单（可选但推荐）。
3. 决定心跳消息应发送到何处（`target: "last"` 是默认值）。
4. 可选：启用心跳推理交付以提高透明度。
5. 可选：限制心跳到活跃时段（本地时间）。

示例配置：

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last",
        // activeHours: { start: "08:00", end: "24:00" },
        // includeReasoning: true, // 可选：发送单独的 `Reasoning:` 消息
      },
    },
  },
}
```

## 默认值

- 间隔：`30m`（或 `1h` 当检测到 Anthropic OAuth/设置令牌的认证模式时）。设置 `agents.defaults.heartbeat.every` 或每个代理的 `agents.list[].heartbeat.every`；使用 `0m` 禁用。
- 提示正文（可通过 `agents.defaults.heartbeat.prompt` 配置）：
  `如果存在 HEARTBEAT.md（工作区上下文），请阅读它。严格遵循。不要推断或重复之前聊天中的旧任务。如果无需关注，请回复 HEARTBEAT_OK。`
- 心跳提示以**原样**作为用户消息发送。系统
  提示包含一个“心跳”部分，并在内部标记运行。
- 活跃时段（`heartbeat.activeHours`）在配置的时区中检查。
  在窗口外，心跳将跳过，直到下一个窗口内的滴答。

## 心跳提示的用途

默认提示有意广泛：

- **后台任务**：“考虑未完成的任务”会促使代理审查
  后续操作（收件箱、日历、提醒、排队的工作）并突出显示任何紧急事项。
- **人类检查**：“白天偶尔检查您的人类”会促使一个
  偶尔的轻量级“您需要什么？”消息，但通过您的配置本地时区（参见 [/概念/时区](/概念/时区)）避免夜间垃圾邮件。

如果您希望心跳执行非常具体的操作（例如“检查 Gmail PubSub
统计信息”或“验证网关健康状况”），请设置 `agents.defaults.heartbeat.prompt`（或
`agents.list[].heartbeat.prompt`）为自定义正文（原样发送）。

## 响应契约

- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请回复 **`HEARTBEAT_OK`**。
- 如果无需关注，请