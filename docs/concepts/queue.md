---
summary: "Command queue design that serializes inbound auto-reply runs"
read_when:
  - Changing auto-reply execution or concurrency
title: "Command Queue"
---
# 命令队列（2026-01-16）

我们通过一个轻量级的进程内队列对所有通道的入站自动回复运行进行序列化处理，以防止多个智能体运行相互冲突，同时仍允许跨会话的安全并行执行。

## 原因

- 自动回复运行可能开销较大（例如调用大语言模型），当多个入站消息在相近时间到达时，容易发生冲突。
- 序列化可避免争用共享资源（会话文件、日志、CLI 标准输入），并降低触发上游速率限制的可能性。

## 工作原理

- 一个按通道区分的先进先出（FIFO）队列，为每个通道以可配置的并发上限进行消费（未配置通道默认为 1；主通道默认为 4，子智能体通道默认为 8）。
- `runEmbeddedPiAgent` 按 **会话密钥**（通道为 `session:<key>`）入队，确保每个会话至多只有一个活跃运行。
- 随后，每个会话运行被加入一个 **全局通道**（默认为 `main`），因此整体并行度受 `agents.defaults.maxConcurrent` 限制。
- 当启用详细日志时，若某次排队运行等待启动时间超过约 2 秒，则会输出一条简短提示。
- 输入指示器（typing indicators）仍在入队时立即触发（若通道支持），因此用户感知体验不受影响，仅需等待轮到自身处理。

## 队列模式（按通道）

入站消息可选择：接管当前运行、等待下一轮智能体响应，或二者兼有：

- `steer`: 立即注入当前运行（在下一个工具边界之后取消待处理的工具调用）。若非流式响应，则回退至 followup 模式。
- `followup`: 在当前运行结束后，将消息排队至下一轮智能体响应。
- `collect`: 将所有排队消息聚合成 **单个** followup 响应（默认行为）。若消息目标为不同通道/线程，则各自独立消费，以保留路由逻辑。
- `steer-backlog`（又称 `steer+backlog`）：立即接管 **且** 保留该消息用于后续 followup 响应。
- `interrupt`（旧版）：中止该会话当前活跃运行，然后执行最新消息。
- `queue`（旧版别名）：等同于 `steer`。

“接管-积压”（steer-backlog）意味着你可在接管运行之后获得一次 followup 响应，因此流式界面中可能出现看似重复的响应。如需每条入站消息对应唯一响应，请优先选用 `collect`/`steer`。  
发送 `/queue collect` 作为独立命令（按会话）或设置 `messages.queue.byChannel.discord: "collect"`。

默认值（配置中未显式设定时）：

- 所有界面 → `collect`

可通过 `messages.queue` 全局或按通道配置：

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

以下选项适用于 `followup`、`collect` 和 `steer-backlog`（以及 `steer` 在回退至 followup 模式时）：

- `debounceMs`: 在启动 followup 响应前等待静默期（防止出现“继续、继续”类连续响应）。
- `cap`: 每个会话最多允许排队的消息数。
- `drop`: 溢出策略（`old`、`new`、`summarize`）。

“摘要”（Summarize）模式会维护一个被丢弃消息的简短要点列表，并将其作为合成的 followup 提示注入。  
默认值：`debounceMs: 1000`、`cap: 20`、`drop: summarize`。

## 按会话覆盖设置

- 发送 `/queue <mode>` 作为独立命令，可为当前会话存储队列模式。
- 多个选项可组合使用：`/queue collect debounce:2s cap:25 drop:summarize`
- `/queue default` 或 `/queue reset` 可清除会话级覆盖设置。

## 作用范围与保障

- 适用于所有使用网关回复流水线的入站通道的自动回复智能体运行（WhatsApp Web、Telegram、Slack、Discord、Signal、iMessage、网页聊天等）。
- 默认通道（`main`）在进程范围内共享，涵盖入站消息及主心跳；设置 `agents.defaults.maxConcurrent` 可允许多个会话并行执行。
- 可能存在额外通道（例如 `cron`、`subagent`），以便后台任务并行运行而不阻塞入站响应。
- 按会话通道确保任意时刻仅有一个智能体运行访问指定会话。
- 不依赖任何外部组件或后台工作线程；纯 TypeScript + Promise 实现。

## 故障排查

- 若命令看似卡住，请启用详细日志并查找形如 “queued for …ms” 的日志行，确认队列是否正在正常消费。
- 若需获取队列深度信息，请启用详细日志并关注队列计时相关日志行。