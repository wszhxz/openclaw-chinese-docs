---
summary: "Timezone handling for agents, envelopes, and prompts"
read_when:
  - You need to understand how timestamps are normalized for the model
  - Configuring the user timezone for system prompts
title: "Timezones"
---
# 时区

OpenClaw 对时间戳进行标准化，使模型始终看到 **单一参考时间**。

## 消息信封（默认为本地时间）

入站消息被封装在如下格式的信封中：

```
[Provider ... 2026-01-05 16:26 PST] message text
```

信封中的时间戳 **默认为宿主机本地时间**，精度为分钟。

您可通过以下方式覆盖该默认行为：

```json5
{
  agents: {
    defaults: {
      envelopeTimezone: "local", // "utc" | "local" | "user" | IANA timezone
      envelopeTimestamp: "on", // "on" | "off"
      envelopeElapsed: "on", // "on" | "off"
    },
  },
}
```

- `envelopeTimezone: "utc"` 使用 UTC。
- `envelopeTimezone: "user"` 使用 `agents.defaults.userTimezone`（若未配置，则回退至宿主机时区）。
- 使用显式的 IANA 时区（例如 `"Europe/Vienna"`）可指定固定偏移量。
- `envelopeTimestamp: "off"` 将从信封头部移除绝对时间戳。
- `envelopeElapsed: "off"` 将移除经过时间后缀（即 `+2m` 格式）。

### 示例

**本地时间（默认）：**

```
[Signal Alice +1555 2026-01-18 00:19 PST] hello
```

**固定时区：**

```
[Signal Alice +1555 2026-01-18 06:19 GMT+1] hello
```

**经过时间：**

```
[Signal Alice +1555 +2m 2026-01-18T05:19Z] follow-up
```

## 工具载荷（原始提供方数据 + 标准化字段）

工具调用（如 `channels.discord.readMessages`、`channels.slack.readMessages` 等）返回 **原始提供方的时间戳**。  
我们还附加了标准化字段以确保一致性：

- `timestampMs`（UTC 纪元毫秒数）
- `timestampUtc`（ISO 8601 格式的 UTC 字符串）

原始提供方字段将被保留。

## 系统提示中的用户时区

设置 `agents.defaults.userTimezone` 可告知模型用户的本地时区。若未设置，OpenClaw 将在运行时解析 **宿主机时区**（无需写入配置）。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

系统提示中包含：

- `Current Date & Time` 部分，含本地时间和时区信息
- `Time format: 12-hour` 或 `24-hour`

您可通过 `agents.defaults.timeFormat`（`auto` | `12` | `24`）控制提示格式。

完整行为与示例请参阅 [日期与时间](/date-time)。