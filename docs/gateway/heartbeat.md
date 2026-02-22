---
summary: "Heartbeat polling messages and notification rules"
read_when:
  - Adjusting heartbeat cadence or messaging
  - Deciding between heartbeat and cron for scheduled tasks
title: "Heartbeat"
---
# 心跳 (网关)

> **心跳 vs Cron?** 有关何时使用每个工具的指导，请参阅 [Cron vs 心跳](/automation/cron-vs-heartbeat)。

心跳在主会话中运行 **周期性代理轮次**，以便模型可以
突出显示任何需要关注的内容而不会骚扰您。

故障排除: [/automation/troubleshooting](/automation/troubleshooting)

## 快速入门 (初学者)

1. 保持心跳启用（默认是 `30m`，或 `1h` 用于 Anthropic OAuth/setup-token）或设置您自己的节奏。
2. 在代理工作区创建一个小型 `HEARTBEAT.md` 检查清单（可选但推荐）。
3. 决定心跳消息应发送到哪里（默认是 `target: "last"`）。
4. 可选：启用心跳推理传递以提高透明度。
5. 可选：将心跳限制在活跃时间（本地时间）。

示例配置：

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last",
        // activeHours: { start: "08:00", end: "24:00" },
        // includeReasoning: true, // optional: send separate `Reasoning:` message too
      },
    },
  },
}
```

## 默认设置

- 间隔: `30m`（或当检测到 Anthropic OAuth/setup-token 身份验证模式时为 `1h`）。设置 `agents.defaults.heartbeat.every` 或每个代理的 `agents.list[].heartbeat.every`；使用 `0m` 禁用。
- 提示正文（可通过 `agents.defaults.heartbeat.prompt` 配置）：
  `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`
- 心跳提示作为用户消息 **逐字** 发送。系统
  提示包括“心跳”部分，并且运行内部标记为心跳。
- 活跃时间 (`heartbeat.activeHours`) 根据配置的时区进行检查。
  在窗口之外，心跳会被跳过，直到窗口内的下一个刻度。

## 心跳提示的作用

默认提示故意设计得很广泛：

- **后台任务**：提示“考虑未完成的任务”会促使代理审查
  待办事项（收件箱、日历、提醒、排队的工作）并突出显示任何紧急事项。
- **人工检查**：提示“白天偶尔检查您的人类”会促使偶尔发送一条轻量级的“您需要什么？”消息，但通过使用您配置的本地时区避免夜间骚扰（请参阅 [/concepts/timezone](/concepts/timezone)）。

如果您希望心跳执行非常具体的操作（例如“检查 Gmail PubSub 统计信息”或“验证网关健康状况”），请将 `agents.defaults.heartbeat.prompt`（或
`agents.list[].heartbeat.prompt`）设置为自定义正文（逐字发送）。

## 响应契约

- 如果没有需要注意的地方，回复 **`HEARTBEAT_OK`**。
- 在心跳运行期间，OpenClaw 将 `HEARTBEAT_OK` 视为确认信息，当它出现在回复的 **开头或结尾** 时。如果剩余内容 **≤ `ackMaxChars`**（默认：300），则会移除该标记并丢弃回复。
- 如果 `HEARTBEAT_OK` 出现在回复的 **中间**，则不会被特殊处理。
- 对于警报，**不要** 包含 `HEARTBEAT_OK`；仅返回警报文本。

在非心跳期间，消息开头或结尾的孤立 `HEARTBEAT_OK` 会被移除并记录日志；仅包含 `HEARTBEAT_OK` 的消息会被丢弃。

## 配置

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // default: 30m (0m disables)
        model: "anthropic/claude-opus-4-6",
        includeReasoning: false, // default: false (deliver separate Reasoning: message when available)
        target: "last", // last | none | <channel id> (core or plugin, e.g. "bluebubbles")
        to: "+15551234567", // optional channel-specific override
        accountId: "ops-bot", // optional multi-account channel id
        prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        ackMaxChars: 300, // max chars allowed after HEARTBEAT_OK
      },
    },
  },
}
```

### 作用域和优先级

- `agents.defaults.heartbeat` 设置全局心跳行为。
- `agents.list[].heartbeat` 覆盖其上；如果有任何代理具有 `heartbeat` 块，则 **只有这些代理** 运行心跳。
- `channels.defaults.heartbeat` 为所有频道设置可见性默认值。
- `channels.<channel>.heartbeat` 覆盖频道默认值。
- `channels.<channel>.accounts.<id>.heartbeat`（多账户频道）覆盖每个频道的设置。

### 每个代理的心跳

如果任何 `agents.list[]` 条目包含 `heartbeat` 块，则 **只有这些代理** 运行心跳。每个代理的块会覆盖 `agents.defaults.heartbeat`
（因此您可以一次性设置共享默认值，并按代理进行覆盖）。

示例：两个代理，只有第二个代理运行心跳。

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last",
      },
    },
    list: [
      { id: "main", default: true },
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "whatsapp",
          to: "+15551234567",
          prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        },
      },
    ],
  },
}
```

### 工作时间示例

将心跳限制在特定时区的工作时间内：

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last",
        activeHours: {
          start: "09:00",
          end: "22:00",
          timezone: "America/New_York", // optional; uses your userTimezone if set, otherwise host tz
        },
      },
    },
  },
}
```

在此窗口之外（东部时间早上9点之前或晚上10点之后），心跳检测会被跳过。窗口内的下一个预定滴答将正常运行。

### 24/7 设置

如果您希望心跳检测全天运行，请使用以下模式之一：

- 完全省略 `activeHours`（无时间窗口限制；这是默认行为）。
- 设置全天窗口：`activeHours: { start: "00:00", end: "24:00" }`。

不要将相同的 `start` 和 `end` 时间设置为相同（例如 `08:00` 到 `08:00`）。
这被视为零宽度窗口，因此心跳检测将始终被跳过。

### 多账户示例

在Telegram等多账户频道中，使用 `accountId` 针对特定账户：

```json5
{
  agents: {
    list: [
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "telegram",
          to: "12345678:topic:42", // optional: route to a specific topic/thread
          accountId: "ops-bot",
        },
      },
    ],
  },
  channels: {
    telegram: {
      accounts: {
        "ops-bot": { botToken: "YOUR_TELEGRAM_BOT_TOKEN" },
      },
    },
  },
}
```

### 字段说明

- `every`: 心跳间隔（持续时间字符串；默认单位 = 分钟）。
- `model`: 可选的心跳运行模型覆盖 (`provider/model`)。
- `includeReasoning`: 启用时，当可用时也发送单独的 `Reasoning:` 消息（与 `/reasoning on` 形状相同）。
- `session`: 可选的心跳运行会话密钥。
  - `main`（默认）：代理主会话。
  - 显式会话密钥（从 `openclaw sessions --json` 或 [sessions CLI](/cli/sessions) 复制）。
  - 会话密钥格式：参见 [Sessions](/concepts/session) 和 [Groups](/channels/groups)。
- `target`:
  - `last`（默认）：发送到最后使用的外部通道。
  - 显式通道：`whatsapp` / `telegram` / `discord` / `googlechat` / `slack` / `msteams` / `signal` / `imessage`。
  - `none`：运行心跳但**不进行外部发送**。
- `to`: 可选的收件人覆盖（通道特定的ID，例如WhatsApp的E.164或Telegram聊天ID）。对于Telegram主题/线程，使用 `<chatId>:topic:<messageThreadId>`。
- `accountId`: 多账户通道的可选账户ID。当 `target: "last"` 时，账户ID适用于解析后的最后一个通道（如果支持账户）；否则忽略。如果账户ID与解析通道的配置账户不匹配，则跳过发送。
- `prompt`: 覆盖默认提示正文（不合并）。
- `ackMaxChars`: 在发送之前允许的最大字符数 `HEARTBEAT_OK` 之后。
- `suppressToolErrorWarnings`: 当为true时，在心跳运行期间抑制工具错误警告负载。
- `activeHours`: 将心跳运行限制在时间窗口内。具有 `start`（HH:MM，包含；使用 `00:00` 表示一天开始），`end`（HH:MM，不包含；`24:00` 允许表示一天结束），以及可选的 `timezone` 的对象。
  - 省略或 `"user"`：如果设置了 `agents.defaults.userTimezone`，则使用该值，否则回退到主机系统时区。
  - `"local"`：始终使用主机系统时区。
  - 任何IANA标识符（例如 `America/New_York`）：直接使用；如果无效，则回退到上述 `"user"` 行为。
  - `start` 和 `end` 对于活动窗口必须不相等；相等的值被视为零宽度（始终在窗口之外）。
  - 在活动窗口之外，心跳将被跳过，直到下一个窗口内的刻度。

## 发送行为

- 心跳默认在代理的主会话中运行 (`agent:<id>:<mainKey>`)，或在 `global` 当 `session.scope = "global"`。设置 `session` 以覆盖到特定的通道会话（Discord/WhatsApp等）。
- `session` 仅影响运行上下文；传递由 `target` 和 `to` 控制。
- 要传递到特定的通道/接收者，设置 `target` + `to`。使用 `target: "last"`，传递使用该会话的最后一个外部通道。
- 如果主队列繁忙，心跳会被跳过并稍后重试。
- 如果 `target` 解析为没有外部目标，则运行仍然会发生但不会发送出站消息。
- 仅心跳回复**不**保持会话活跃；最后的 `updatedAt` 被恢复，以便空闲过期行为正常。

## 可见性控制

默认情况下，在传递警报内容时抑制 `HEARTBEAT_OK` 确认。您可以根据通道或账户进行调整：

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false # Hide HEARTBEAT_OK (default)
      showAlerts: true # Show alert messages (default)
      useIndicator: true # Emit indicator events (default)
  telegram:
    heartbeat:
      showOk: true # Show OK acknowledgments on Telegram
  whatsapp:
    accounts:
      work:
        heartbeat:
          showAlerts: false # Suppress alert delivery for this account
```

优先级：按账户 → 按通道 → 通道默认值 → 内置默认值。

### 每个标志的作用

- `showOk`：当模型返回仅 OK 的回复时发送 `HEARTBEAT_OK` 确认。
- `showAlerts`：当模型返回非 OK 的回复时发送警报内容。
- `useIndicator`：为 UI 状态表面发出指示事件。

如果**全部三个**都为假，OpenClaw 完全跳过心跳运行（无模型调用）。

### 按通道与按账户示例

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false
      showAlerts: true
      useIndicator: true
  slack:
    heartbeat:
      showOk: true # all Slack accounts
    accounts:
      ops:
        heartbeat:
          showAlerts: false # suppress alerts for the ops account only
  telegram:
    heartbeat:
      showOk: true
```

### 常见模式

| 目标                                     | 配置                                                                                   |
| ---------------------------------------- | ---------------------------------------------------------------------------------------- |
| 默认行为（静默 OK，警报开启）            | _(无需配置)_                                                                           |
| 完全静默（无消息，无指示）               | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: false }` |
| 仅指示（无消息）                         | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: true }`  |
| 仅在一个通道中显示 OK                    | `channels.telegram.heartbeat: { showOk: true }`                                          |

## HEARTBEAT.md (可选)

如果工作区中存在一个 `HEARTBEAT.md` 文件，默认提示会让代理读取它。可以将其视为你的“心跳检查清单”：简短、稳定且每30分钟安全包含一次。

如果 `HEARTBEAT.md` 存在但实际上是空的（只有空白行和markdown标题如 `# Heading`)，OpenClaw会跳过心跳运行以节省API调用。如果文件缺失，心跳仍然会运行，模型会决定接下来的操作。

保持其简洁（简短的清单或提醒）以避免提示膨胀。

示例 `HEARTBEAT.md`:

```md
# Heartbeat checklist

- Quick scan: anything urgent in inboxes?
- If it’s daytime, do a lightweight check-in if nothing else is pending.
- If a task is blocked, write down _what is missing_ and ask Peter next time.
```

### 代理可以更新 HEARTBEAT.md 吗？

可以 — 如果你要求它这样做。

`HEARTBEAT.md` 只是代理工作区中的一个普通文件，因此你可以告诉代理（在正常对话中）如下内容：

- “更新 `HEARTBEAT.md` 以添加每日日历检查。”
- “重写 `HEARTBEAT.md` 使其更短并专注于收件箱跟进。”

如果你想主动进行此操作，也可以在心跳提示中包含如下明确的一行：“如果清单过时，请使用更好的清单更新 HEARTBEAT.md。”

安全注意事项：不要将机密信息（API密钥、电话号码、私人令牌）放入 `HEARTBEAT.md` 中 — 它将成为提示上下文的一部分。

## 手动唤醒（按需）

你可以排队一个系统事件并触发立即心跳：

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
```

如果有多个代理配置了 `heartbeat`，手动唤醒会立即运行每个代理的心跳。

使用 `--mode next-heartbeat` 等待下一个预定的时间点。

## 推理交付（可选）

默认情况下，心跳仅传递最终的“答案”负载。

如果你需要透明度，启用：

- `agents.defaults.heartbeat.includeReasoning: true`

启用后，心跳还会传递一个带有前缀 `Reasoning:` 的单独消息（与 `/reasoning on` 形状相同）。当代理管理多个会话/代码库并且你想了解它为何要通知你时这很有用 — 但它也可能泄露比你想要的更多内部细节。建议在群聊中保持关闭状态。

## 成本意识

心跳运行完整的代理轮次。较短的间隔会消耗更多的token。保持 `HEARTBEAT.md` 简洁，并考虑使用更便宜的 `model` 或 `target: "none"` 如果你只需要内部状态更新。