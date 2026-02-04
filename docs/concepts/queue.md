---
summary: "Command queue design that serializes inbound auto-reply runs"
read_when:
  - Changing auto-reply execution or concurrency
title: "Command Queue"
---
# 命令队列 (2026-01-16)

我们将所有渠道的入站自动回复运行通过一个小型的进程内队列进行序列化，以防止多个代理运行发生冲突，同时仍然允许跨会话的安全并行性。

## 为什么

- 自动回复运行可能代价高昂（LLM调用），当多个入站消息几乎同时到达时可能会发生冲突。
- 序列化可以避免竞争共享资源（会话文件、日志、CLI标准输入），并减少上游速率限制的可能性。

## 工作原理

- 一个具有车道感知的FIFO队列根据可配置的并发上限（未配置的车道默认为1；主车道默认为4，子代理默认为8）排空每个车道。
- `runEmbeddedPiAgent` 按 **会话键**（车道 `session:<key>`）入队，以确保每个会话只有一个活动运行。
- 然后，每个会话运行被放入一个 **全局车道**（默认为 `main`），因此整体并行性由 `agents.defaults.maxConcurrent` 限制。
- 当启用详细日志记录时，如果排队运行在开始前等待超过约2秒，则会发出简短通知。
- 在支持的渠道中，入队时立即触发打字指示符，因此在等待轮到我们时用户体验不会改变。

## 队列模式（按渠道）

入站消息可以引导当前运行、等待后续回合，或者两者都做：

- `steer`：立即注入当前运行（在下一个工具边界后取消待处理的工具调用）。如果不流式传输，则回退到后续回合。
- `followup`：在当前运行结束后，将入队到下一个代理回合。
- `collect`：将所有排队的消息合并为一个 **单一** 后续回合（默认）。如果消息针对不同的渠道/线程，则单独排出以保留路由。
- `steer-backlog`（即 `steer+backlog`）：现在引导 **并** 保留消息以供后续回合使用。
- `interrupt`（旧版）：中止该会话的活动运行，然后运行最新的消息。
- `queue`（旧版别名）：与 `steer` 相同。

引导回溯意味着您可以在引导运行之后获得后续响应，因此
流式表面可能会看起来像重复项。如果您希望每个入站消息只得到一个响应，
请使用 `collect`/`steer`。
发送 `/queue collect` 作为独立命令（每会话）或设置 `messages.queue.byChannel.discord: "collect"`。

默认值（当配置中未设置时）：

- 所有表面 → `collect`

通过 `messages.queue` 全局或按渠道配置：

```json5
{
  messages: {
    queue: {
      mode: "collect",
      debounceMs: 1000,
      cap: 20,
      drop: "summarize",
      byChannel: { discord: "collect" },
    },
  },
}
```

## 队列选项

选项适用于 `followup`、`collect` 和 `steer-backlog`（以及当它回退到后续回合时的 `steer`）：

- `debounceMs`：等待安静后再开始后续回合（防止“继续，继续”）。
- `cap`：每个会话的最大排队消息数。
- `drop`：溢出策略（`old`、`new`、`summarize`）。

摘要保留一个简短的被丢弃消息列表，并将其作为合成后续提示注入。
默认值：`debounceMs: 1000`、`cap: 20`、`drop: summarize`。

## 每会话覆盖

- 发送 `/queue <mode>` 作为独立命令以存储当前会话的模式。
- 选项可以组合：`/queue collect debounce:2s cap:25 drop:summarize`
- `/queue default` 或 `/queue reset` 清除会话覆盖。

## 范围和保证

- 适用于使用网关回复管道的所有入站渠道的自动回复代理运行（WhatsApp Web、Telegram、Slack、Discord、Signal、iMessage、Web聊天等）。
- 默认车道（`main`）是进程范围内的入站+主心跳；设置 `agents.defaults.maxConcurrent` 以允许并行会话。
- 可能存在其他车道（例如 `cron`、`subagent`），以便后台作业可以并行运行而不阻塞入站回复。
- 每会话车道保证一次只有一个代理运行接触给定的会话。
- 无外部依赖或后台工作线程；纯TypeScript + Promise。

## 故障排除

- 如果命令似乎卡住，请启用详细日志并查找“queued for …ms”行以确认队列正在排出。
- 如果需要队列深度，请启用详细日志并监视队列计时行。