---
summary: "Heartbeat polling messages and notification rules"
read_when:
  - Adjusting heartbeat cadence or messaging
  - Deciding between heartbeat and cron for scheduled tasks
title: "Heartbeat"
---
# 心跳 (网关)

> **心跳 vs 定时任务?** 请参阅 [定时任务 vs 心跳](/automation/cron-vs-heartbeat) 以获取关于何时使用每个功能的指导。

心跳在主会话中运行 **定期代理轮询**，以便模型可以
突出显示任何需要关注的内容而不会打扰您。

## 快速入门 (初学者)

1. 保持心跳启用（默认是 `30m`，或 `1h` 对于 Anthropic OAuth/设置令牌）或设置您自己的频率。
2. 在代理工作区创建一个小型 `HEARTBEAT.md` 待办事项列表（可选但推荐）。
3. 决定心跳消息应发送到哪里（默认是 `target: "last"`）。
4. 可选：启用心跳推理传递以提高透明度。
5. 可选：将心跳限制在活动时间（本地时间）。

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

- 间隔：`30m`（或当检测到 Anthropic OAuth/设置令牌身份验证模式时为 `1h`）。设置 `agents.defaults.heartbeat.every` 或每个代理的 `agents.list[].heartbeat.every`；使用 `0m` 禁用。
- 提示正文（可通过 `agents.defaults.heartbeat.prompt` 配置）：
  `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`
- 心跳提示作为用户消息 **逐字** 发送。系统
  提示包括“心跳”部分，并且运行内部标记为心跳。
- 活动时间 (`heartbeat.activeHours`) 在配置时区中检查。
  在窗口之外，心跳将被跳过，直到窗口内的下一个周期。

## 心跳提示的作用

默认提示故意设计得很广泛：

- **后台任务**：“考虑未完成的任务”提示代理审查
  跟进事项（收件箱、日历、提醒、排队的工作）并突出显示任何紧急事项。
- **人类检查**：“白天偶尔检查您的人类”提示偶尔发送一条轻量级的“您需要什么？”消息，但通过使用您的配置的本地时区避免夜间打扰（请参阅 [/concepts/timezone](/concepts/timezone)）。

如果您希望心跳执行非常具体的操作（例如“检查 Gmail PubSub 统计信息”或“验证网关健康状况”），请将 `agents.defaults.heartbeat.prompt`（或
`agents.list[].heartbeat.prompt`）设置为自定义正文（逐字发送）。

## 响应契约

- 如果没有需要关注的内容，请回复 **`HEARTBEAT_OK`**。
- 在心跳运行期间，OpenClaw 将 `HEARTBEAT_OK` 视为确认，当它出现在回复的 **开头或结尾** 时。如果剩余内容 **≤ `ackMaxChars`**（默认：300），则会删除该令牌和回复。
- 如果 `HEARTBEAT_OK` 出现在回复的 **中间**，则不会特别处理。
- 对于警报，**不要** 包含 `HEARTBEAT_OK`；仅返回警报文本。

外部心跳检测中，在消息的开头或结尾出现的孤立 `HEARTBEAT_OK` 会被移除并记录；仅包含 `HEARTBEAT_OK` 的消息将被丢弃。

## 配置

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // default: 30m (0m disables)
        model: "anthropic/claude-opus-4-5",
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
- `agents.list[].heartbeat` 覆盖在上层；如果任何代理具有 `heartbeat` 块，则**只有这些代理**运行心跳。
- `channels.defaults.heartbeat` 为所有频道设置可见性默认值。
- `channels.<channel>.heartbeat` 覆盖频道默认值。
- `channels.<channel>.accounts.<id>.heartbeat`（多账户频道）覆盖每个频道的设置。

### 每个代理的心跳

如果任何 `agents.list[]` 条目包含 `heartbeat` 块，则**只有这些代理**
运行心跳。每个代理的块会覆盖 `agents.defaults.heartbeat`
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

### 多账户示例

使用 `accountId` 针对多账户频道（如Telegram）中的特定账户：

```json5
{
  agents: {
    list: [
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "telegram",
          to: "12345678",
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

- `every`: 心跳间隔（持续时间字符串；默认单位=分钟）。
- `model`: 心跳运行时的可选模型覆盖 (`provider/model`)。
- `includeReasoning`: 启用时，如果有可用的单独的 `Reasoning:` 消息时也一并发送（与 `/reasoning on` 形状相同）。
- `session`: 心跳运行时的可选会话密钥。
  - `main`（默认）：代理主会话。
  - 显式会话密钥（从 `openclaw sessions --json` 或 [sessions CLI](/cli/sessions) 复制）。
  - 会话密钥格式：参见 [Sessions](/concepts/session) 和 [Groups](/concepts/groups)。
- `target`:
  - `last`（默认）：发送到最后使用的外部通道。
  - 显式通道：`whatsapp` / `telegram` / `discord` / `googlechat` / `slack` / `msteams` / `signal` / `imessage`。
  - `none`：运行心跳但**不**外部发送。
- `to`: 可选收件人覆盖（通道特定的id，例如 WhatsApp 的 E.164 或 Telegram 聊天 id）。
- `accountId`: 多账户通道的可选账户 id。当 `target: "last"` 时，账户 id 适用于解析后的最后一个通道（如果支持账户）；否则忽略。如果账户 id 不匹配解析通道的配置账户，则跳过发送。
- `prompt`: 覆盖默认提示正文（不合并）。
- `ackMaxChars`: 在发送前允许的最大字符数 `HEARTBEAT_OK`。

## 发送行为

- 心跳默认在代理的主会话中运行 (`agent:<id>:<mainKey>`)，
  或 `global` 当 `session.scope = "global"`。设置 `session` 以覆盖到
  特定通道会话（Discord/WhatsApp 等）。
- `session` 仅影响运行上下文；发送由 `target` 和 `to` 控制。
- 要发送到特定通道/收件人，设置 `target` + `to`。使用
  `target: "last"`，发送使用该会话的最后一个外部通道。
- 如果主队列繁忙，心跳将被跳过并稍后重试。
- 如果 `target` 解析为没有外部目标，则运行仍然发生但不
  发送外发消息。
- 仅心跳回复**不会**保持会话活跃；最后的 `updatedAt`
  将被恢复，以便空闲过期行为正常。

## 可见性控制

默认情况下，在发送警报内容时抑制 `HEARTBEAT_OK` 确认。您可以根据通道或账户进行调整：

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

- `showOk`: 在模型返回仅OK回复时发送`HEARTBEAT_OK`确认。
- `showAlerts`: 在模型返回非OK回复时发送警报内容。
- `useIndicator`: 为UI状态表面发出指示事件。

如果**全部三个**都为假，OpenClaw将完全跳过心跳运行（不调用模型）。

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
| 默认行为（静默OK，警报开启） | _(无需配置)_                                                                     |
| 完全静默（无消息，无指示） | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: false }` |
| 仅指示（无消息）             | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: true }`  |
| 仅在一个通道中发送OK                  | `channels.telegram.heartbeat: { showOk: true }`                                          |

## HEARTBEAT.md（可选）

如果工作区中存在`HEARTBEAT.md`文件，默认提示会让代理读取它。可以将其视为您的“心跳检查清单”：小巧、稳定且每30分钟包含一次是安全的。

如果`HEARTBEAT.md`存在但实际上是空的（只有空白行和Markdown标题如`# Heading`），OpenClaw将跳过心跳运行以节省API调用。如果文件缺失，心跳仍然会运行，模型会决定如何操作。

保持其简洁（简短的清单或提醒）以避免提示膨胀。

示例`HEARTBEAT.md`：

```md
# Heartbeat checklist

- Quick scan: anything urgent in inboxes?
- If it’s daytime, do a lightweight check-in if nothing else is pending.
- If a task is blocked, write down _what is missing_ and ask Peter next time.
```

### 代理可以更新HEARTBEAT.md吗？

可以——如果您要求它这样做。

`HEARTBEAT.md`只是代理工作区中的一个普通文件，因此您可以告诉代理（在正常聊天中）如下内容：

- “更新`HEARTBEAT.md`以添加每日日历检查。”
- “重写`HEARTBEAT.md`使其更短并专注于收件箱跟进。”

如果您希望主动进行此操作，也可以在心跳提示中包含显式行，例如：“如果检查清单过时，请使用更好的清单更新HEARTBEAT.md。”

安全注意事项：不要将机密信息（API密钥、电话号码、私有令牌）放入`HEARTBEAT.md`——它将成为提示上下文的一部分。

## 手动唤醒（按需）

你可以通过以下方式入队一个系统事件并触发立即的心跳：

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
```

如果有多个代理配置了 `heartbeat`，则会立即运行每个代理的心跳。

使用 `--mode next-heartbeat` 等待下一个计划的时间点。

## 原因传递（可选）

默认情况下，心跳仅传递最终的“答案”负载。

如果你需要透明度，请启用：

- `agents.defaults.heartbeat.includeReasoning: true`

启用后，心跳还将传递一个以 `Reasoning:` 为前缀的单独消息（与 `/reasoning on` 形状相同）。当代理管理多个会话/代码库时，这在你想要了解它为何决定向你发送心跳时非常有用——但它也可能泄露比你想要的更多内部细节。建议在群聊中保持关闭状态。

## 成本意识

心跳运行完整的代理轮次。较短的时间间隔会消耗更多的令牌。保持 `HEARTBEAT.md` 较小，并考虑使用更便宜的 `model` 或 `target: "none"`，如果你只需要内部状态更新。