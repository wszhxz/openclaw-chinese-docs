---
summary: "Heartbeat polling messages and notification rules"
read_when:
  - Adjusting heartbeat cadence or messaging
  - Deciding between heartbeat and cron for scheduled tasks
title: "Heartbeat"
---
# 心跳 (网关)

> **心跳与 Cron？** 参见 [Cron vs Heartbeat](/automation/cron-vs-heartbeat) 以获取何时使用两者的指导。

心跳在主会话中运行**周期性的代理轮次**，以便模型可以显示任何需要注意的内容，而不会向您发送垃圾信息。

故障排除：[/automation/troubleshooting](/automation/troubleshooting)

## 快速入门（初学者）

1. 保持心跳启用（默认值为 `30m`，或 Anthropic OAuth/setup-token 为 `1h`），或者设置您自己的频率。
2. 在代理工作区创建一个微小的 `HEARTBEAT.md` 检查清单（可选但推荐）。
3. 决定心跳消息应发送至何处（`target: "none"` 是默认值；设置 `target: "last"` 以路由到最后的联系人）。
4. 可选：启用心跳推理传递以提高透明度。
5. 可选：如果心跳运行仅需 `HEARTBEAT.md`，则使用轻量级引导上下文。
6. 可选：将心跳限制在活动时间内（本地时间）。

示例配置：

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // explicit delivery to last contact (default is "none")
        directPolicy: "allow", // default: allow direct/DM targets; set "block" to suppress
        lightContext: true, // optional: only inject HEARTBEAT.md from bootstrap files
        // activeHours: { start: "08:00", end: "24:00" },
        // includeReasoning: true, // optional: send separate `Reasoning:` message too
      },
    },
  },
}
```

## 默认值

- 间隔：`30m`（当检测到 Anthropic OAuth/setup-token 为认证模式时，则为 `1h`）。设置 `agents.defaults.heartbeat.every` 或每个代理的 `agents.list[].heartbeat.every`；使用 `0m` 禁用。
- 提示词正文（可通过 `agents.defaults.heartbeat.prompt` 配置）：
  `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`
- 心跳提示词作为用户消息**逐字**发送。系统提示词包含一个“心跳”部分，且运行会被内部标记。
- 活动时间（`heartbeat.activeHours`）在配置的时区中进行检查。
  窗口之外，心跳将被跳过，直到下一个在窗口内的计时点。

## 心跳提示词的用途

默认提示词故意较为宽泛：

- **后台任务**：“考虑待处理任务”促使代理审查跟进事项（收件箱、日历、提醒、排队工作）并显示任何紧急内容。
- **用户签到**：“白天偶尔检查一下你的用户”促使偶尔发送一条轻量级的“有什么需要吗？”消息，但通过使用配置的本地时区避免夜间垃圾信息（参见 [/concepts/timezone](/concepts/timezone)）。

如果您希望心跳执行非常具体的操作（例如“检查 Gmail PubSub 统计信息”或“验证网关健康状态”），请将 `agents.defaults.heartbeat.prompt`（或 `agents.list[].heartbeat.prompt`）设置为自定义正文（逐字发送）。

## 响应契约

- 如果没有需要注意的事项，请回复 **`HEARTBEAT_OK`**。
- 在心跳运行期间，OpenClaw 将 `HEARTBEAT_OK` 视为 ack，当它出现在回复的**开头或结尾**时。该令牌被剥离，如果剩余内容 **≤ `ackMaxChars`**（默认值：300），则丢弃回复。
- 如果 `HEARTBEAT_OK` 出现在回复的**中间**，则不特殊对待。
- 对于警报，**不要**包含 `HEARTBEAT_OK`；仅返回警报文本。

心跳之外，消息开头/结尾的孤立 `HEARTBEAT_OK` 会被剥离和记录；仅包含 `HEARTBEAT_OK` 的消息会被丢弃。

## 配置

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // default: 30m (0m disables)
        model: "anthropic/claude-opus-4-6",
        includeReasoning: false, // default: false (deliver separate Reasoning: message when available)
        lightContext: false, // default: false; true keeps only HEARTBEAT.md from workspace bootstrap files
        target: "last", // default: none | options: last | none | <channel id> (core or plugin, e.g. "bluebubbles")
        to: "+15551234567", // optional channel-specific override
        accountId: "ops-bot", // optional multi-account channel id
        prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        ackMaxChars: 300, // max chars allowed after HEARTBEAT_OK
      },
    },
  },
}
```

### 范围和优先级

- `agents.defaults.heartbeat` 设置全局心跳行为。
- `agents.list[].heartbeat` 合并在上面；如果任何代理拥有 `heartbeat` 块，则**只有那些代理**运行心跳。
- `channels.defaults.heartbeat` 设置所有通道的可见性默认值。
- `channels.<channel>.heartbeat` 覆盖通道默认值。
- `channels.<channel>.accounts.<id>.heartbeat`（多账户通道）覆盖每通道设置。

### 每代理心跳

如果任何 `agents.list[]` 条目包含 `heartbeat` 块，则**只有那些代理**运行心跳。每代理块合并于 `agents.defaults.heartbeat` 之上（因此您可以一次设置共享默认值并按代理进行覆盖）。

示例：两个代理，仅第二个代理运行心跳。

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // explicit delivery to last contact (default is "none")
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

### 活动时间示例

将心跳限制在特定时区的营业时间内：

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // explicit delivery to last contact (default is "none")
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

在此窗口之外（东部时间上午 9 点之前或晚上 10 点之后），心跳将被跳过。窗口内下一个计划的计时点将正常运行。

### 全天候设置

如果您希望心跳全天运行，请使用以下模式之一：

- 完全省略 `activeHours`（无时间窗口限制；这是默认行为）。
- 设置全天窗口：`activeHours: { start: "00:00", end: "24:00" }`。

不要设置相同的 `start` 和 `end` 时间（例如 `08:00` 至 `08:00`）。
这被视为零宽度窗口，因此心跳总是被跳过。

### 多账户示例

使用 `accountId` 针对多账户通道（如 Telegram）上的特定账户：

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

- `every`：心跳间隔（持续时间字符串；默认单位 = 分钟）。
- `model`：心跳运行的可选模型覆盖（`provider/model`）。
- `includeReasoning`：启用时，如果可用，还传递单独的 `Reasoning:` 消息（形状与 `/reasoning on` 相同）。
- `lightContext`：当为 true 时，心跳运行使用轻量级引导上下文，并仅保留工作区引导文件中的 `HEARTBEAT.md`。
- `session`：心跳运行的可选会话密钥。
  - `main`（默认）：代理主会话。
  - 显式会话密钥（从 `openclaw sessions --json` 或 [sessions CLI](/cli/sessions) 复制）。
  - 会话密钥格式：参见 [Sessions](/concepts/session) 和 [Groups](/channels/groups)。
- `target`：
  - `last`：传递到上次使用的外部通道。
  - 显式通道：`whatsapp` / `telegram` / `discord` / `googlechat` / `slack` / `msteams` / `signal` / `imessage`。
  - `none`（默认）：运行心跳但**不外部传递**。
- `directPolicy`：控制直接/DM 传递行为：
  - `allow`（默认）：允许直接/DM 心跳传递。
  - `block`：抑制直接/DM 传递（`reason=dm-blocked`）。
- `to`：可选接收者覆盖（通道特定 ID，例如 WhatsApp 的 E.164 或 Telegram 聊天 ID）。对于 Telegram 主题/线程，使用 `<chatId>:topic:<messageThreadId>`。
- `accountId`：多账户通道的可选账户 ID。当 `target: "last"` 时，账户 ID 适用于解析后的最后通道（如果支持账户）；否则忽略它。如果账户 ID 与解析通道的配置账户不匹配，则跳过传递。
- `prompt`：覆盖默认提示词正文（不合并）。
- `ackMaxChars`：传递前 `HEARTBEAT_OK` 后允许的最大字符数。
- `suppressToolErrorWarnings`：当为 true 时，抑制心跳运行期间的工具错误警告负载。
- `activeHours`：将心跳运行限制在时间窗口内。对象包含 `start`（HH:MM，包含；开始日使用 `00:00`），`end`（HH:MM 不包含；结束日允许 `24:00`），以及可选的 `timezone`。
  - 省略或 `"user"`：如果设置了您的 `agents.defaults.userTimezone`，则使用它，否则回退到主机系统时区。
  - `"local"`：始终使用主机系统时区。
  - 任何 IANA 标识符（例如 `America/New_York`）：直接使用；如果无效，则回退到上述 `"user"` 行为。
  - 对于活动窗口，`start` 和 `end` 不得相等；相等的值被视为零宽度（始终在窗口之外）。
  - 在活动窗口之外，心跳将被跳过，直到下一个在窗口内的计时点。

## 投递行为

- 心跳默认在代理的主会话中运行（`agent:<id>:<mainKey>`），或在 `session.scope = "global"` 时为 `global`。设置 `session` 可覆盖为特定的渠道会话（Discord/WhatsApp 等）。
- `session` 仅影响运行上下文；投递由 `target` 和 `to` 控制。
- 要投递到特定渠道/收件人，设置 `target` + `to`。使用 `target: "last"` 时，投递使用该会话的最后外部渠道。
- 心跳投递默认允许直接/DM 目标。设置 `directPolicy: "block"` 可抑制直接目标发送，同时仍运行心跳回合。
- 如果主队列繁忙，心跳将被跳过并在稍后重试。
- 如果 `target` 解析为无外部目的地，运行仍会发生，但不会发送出站消息。
- 仅心跳回复 **不** 保持会话活跃；最后的 `updatedAt` 会被恢复，以便空闲过期行为正常。

## 可见性控制

默认情况下，在投递警报内容时会抑制 `HEARTBEAT_OK` 确认。您可以按渠道或按账户调整此设置：

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

优先级：每账户 → 每渠道 → 渠道默认值 → 内置默认值。

### 每个标志的作用

- `showOk`：当模型返回仅 OK 回复时，发送 `HEARTBEAT_OK` 确认。
- `showAlerts`：当模型返回非 OK 回复时，发送警报内容。
- `useIndicator`：为 UI 状态界面发出指示器事件。

如果 **全部三个** 均为 false，OpenClaw 将完全跳过心跳运行（无模型调用）。

### 每渠道与每账户示例

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
| 默认行为（静默 OK，警报开启） | _(无需配置)_                                                                     |
| 完全静默（无消息，无指示器） | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: false }` |
| 仅指示器（无消息）             | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: true }`  |
| 仅在一个渠道中发送 OK                  | `channels.telegram.heartbeat: { showOk: true }`                                          |

## HEARTBEAT.md（可选）

如果工作区中存在 `HEARTBEAT.md` 文件，默认提示词会告诉代理读取它。将其视为您的“心跳检查清单”：小巧、稳定，且适合每 30 分钟包含一次。

如果 `HEARTBEAT.md` 存在但实际为空（仅包含空行和 Markdown 标题，如 `# Heading`），OpenClaw 将跳过心跳运行以节省 API 调用。
如果文件缺失，心跳仍会运行，由模型决定做什么。

保持其小巧（简短的检查清单或提醒），以避免提示词膨胀。

示例 `HEARTBEAT.md`：

```md
# Heartbeat checklist

- Quick scan: anything urgent in inboxes?
- If it’s daytime, do a lightweight check-in if nothing else is pending.
- If a task is blocked, write down _what is missing_ and ask Peter next time.
```

### 代理可以更新 HEARTBEAT.md 吗？

可以 — 如果您要求它这样做。

`HEARTBEAT.md` 只是代理工作区中的普通文件，因此您可以告诉代理（在普通聊天中）如下内容：

- “更新 `HEARTBEAT.md` 以添加每日日历检查。”
- “重写 `HEARTBEAT.md` 使其更短并专注于收件箱跟进。”

如果您希望主动发生这种情况，您还可以在心跳提示词中包含一行明确的内容，例如：“如果检查清单变得过时，请用更好的清单更新 HEARTBEAT.md。”

安全提示：不要将机密信息（API 密钥、电话号码、私人令牌）放入 `HEARTBEAT.md` — 它将成为提示词上下文的一部分。

## 手动唤醒（按需）

您可以入队一个系统事件并使用以下命令触发立即心跳：

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
```

如果多个代理配置了 `heartbeat`，手动唤醒将立即运行每个代理的心跳。

使用 `--mode next-heartbeat` 等待下一个计划 tick。

## 推理投递（可选）

默认情况下，心跳仅投递最终“答案”负载。

如果您想要透明度，启用：

- `agents.defaults.heartbeat.includeReasoning: true`

启用后，心跳还将投递一条前缀为 `Reasoning:` 的单独消息（形状与 `/reasoning on` 相同）。当代理管理多个会话/codexes 且您想查看为何决定 ping 您时，这可能很有用 — 但它也可能泄露比您想要的更多内部细节。建议在群聊中保持关闭。

## 成本意识

心跳运行完整的代理回合。较短的间隔会消耗更多 tokens。保持 `HEARTBEAT.md` 较小，如果您只想要内部状态更新，请考虑更便宜的 `model` 或 `target: "none"`。