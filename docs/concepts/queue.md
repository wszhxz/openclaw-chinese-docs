---
summary: "Command queue design that serializes inbound auto-reply runs"
read_when:
  - Changing auto-reply execution or concurrency
title: "Command Queue"
---
时<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context and key terms. The document is about a command queue system for handling auto-reply runs across different channels, with various modes and configurations.

First, I'll identify the main sections: the title, the "Why" section, "How it works," "Queue modes (per channel)," "Queue options," "Per-session overrides," "Scope and guarantees," and "Troubleshooting." Each of these sections has specific terminology related to queues, concurrency, sessions, and modes like 'collect' or 'steer-backlog.'

I need to make sure that technical terms are accurately translated. For example, "Command Queue" becomes "命令队列," and "auto-reply runs" might be "自动回复运行." Terms like "concurrency cap" could be "并发限制." It's important to maintain the structure and formatting, such as code blocks and bullet points, so the translation remains clear and organized.

I should also pay attention to the specific modes mentioned, like 'steer,' 'followup,' 'collect,' and 'steer-backlog.' These should be translated consistently throughout the document. For instance, 'steer-backlog' might be "引导回溯" or "引导并保留消息," but I need to check if there's a standard translation for such terms in technical contexts.

Another part is the JSON configuration example. I need to ensure that the syntax remains correct in Chinese, using proper quotation marks and structure. Terms like "debounceMs" and "drop" should be translated appropriately, maybe as "防抖时间" and "丢弃策略."

I'll also check for any idiomatic expressions or phrases that might not translate directly. For example, "streaming surfaces can look like duplicates" should be translated in a way that conveys the same meaning without being literal. Maybe "流式界面可能会显示为重复内容."

Throughout the translation, I'll maintain the technical accuracy while ensuring the language is clear and natural in Chinese. I'll review each section to confirm that the translated terms are consistent and that the overall message remains intact. Finally, I'll verify that the formatting, such as code blocks and bullet points, is preserved to match the original document's structure.
</think>

# 命令队列（2026-01-16）

我们通过一个微型的进程内队列对所有渠道的入站自动回复运行进行序列化，以防止多个代理运行发生冲突，同时仍允许会话间的安全并行处理。

## 为什么

- 自动回复运行可能成本较高（LLM调用），当多个入站消息接近时可能会发生冲突。
- 序列化可避免争夺共享资源（会话文件、日志、CLI标准输入），并降低上游速率限制的可能性。

## 工作原理

- 一个车道感知的FIFO队列会按可配置的并发限制（未配置车道默认为1；主车道默认为4，子代理默认为8）依次处理每个车道。
- `runEmbeddedPiAgent` 通过 **会话密钥**（车道 `session:<key>`）入队，以确保每个会话仅有一个活跃运行。
- 每个会话运行随后会被排队到一个 **全局车道**（默认为 `main`），因此整体并行度受 `agents.defaults.maxConcurrent` 限制。
- 当启用详细日志时，排队运行若等待超过约2秒才开始，会发出简短提示。
- 输入指示器在入队时仍会立即触发（如渠道支持），因此在等待轮到我们时用户体验保持不变。

## 队列模式（按渠道）

入站消息可以引导当前运行、等待后续回合，或两者兼有：

- `steer`：立即注入当前运行（在下一个工具边界后取消待处理的工具调用）。若非流式处理，则退回到后续回合。
- `followup`：在当前运行结束后排队等待下一个代理回合。
- `collect`：将所有排队消息合并为 **单个** 后续回合（默认）。若消息目标不同渠道/线程，则会单独处理以保留路由。
- `steer-backlog`（即 `steer+backlog`）：现在引导 **并** 保留消息供后续回合使用。
- `interrupt`（旧版）：中止该会话的当前运行，然后运行最新消息。
- `queue`（旧版别名）：与 `steer` 相同。

`steer-backlog` 表示您可以在引导运行后获得后续响应，因此流式界面可能会显示为重复内容。如果您希望每条入站消息对应一个响应，请优先使用 `collect`/`steer`。发送 `/queue collect` 作为独立命令（每会话一次）或设置 `messages.queue.byChannel.discord: "collect"`。

默认值（未在配置中设置时）：

- 所有界面 → `collect`

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

选项适用于 `followup`、`collect` 和 `steer-backlog`（以及 `steer` 在退回到 `followup` 时）：

- `debounceMs`：在开始后续回合前等待安静期（防止“继续，继续”重复）。
- `cap`：每会话最大排队消息数。
- `drop`：溢出策略（`old`、`new`、`summarize`）。

`summarize` 会保留被丢弃消息的简短项目列表，并将其作为合成的后续提示注入。
默认值：`debounceMs: 1000`，`cap: 20`，`drop: summarize`。

## 每会话覆盖

- 发送 `/queue <mode>` 作为独立命令以存储当前会话的模式。
- 选项可以组合使用：`/queue collect debounce:2s cap:25 drop:summarize`
- `/queue default` 或 `/queue reset` 会清除会话覆盖。

## 范围和保证

- 适用于所有使用网关回复管道的入站渠道的自动回复代理运行（如 WhatsApp Web、Telegram、Slack、Discord、Signal、iMessage、网页聊天等）。
- 默认车道（`main`）是进程范围的，适用于入站 + 主心跳；设置 `agents.defaults.maxConcurrent` 以允许并行处理多个会话。
- 可能存在其他车道（如 `cron`、`subagent`），以便后台任务可并行运行而不阻塞入站回复。
- 每会话车道保证同一时间仅有一个代理运行处理特定会话。
- 无外部依赖或后台工作线程；纯 TypeScript + Promises。

## 故障排除

- 如果命令似乎卡住，请启用详细日志并查找“排队中 …ms”行以确认队列正在处理。
- 如果需要队列深度，请启用详细日志并观察队列时间线。