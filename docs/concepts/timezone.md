---
summary: "Timezone handling for agents, envelopes, and prompts"
read_when:
  - You need to understand how timestamps are normalized for the model
  - Configuring the user timezone for system prompts
title: "Timezones"
---
# 时区

OpenClaw 标准化时间戳，使模型看到一个 **单一的参考时间**。

## 消息信封（默认为本地时间）

入站消息被封装在一个信封中，如下所示：

```
[Provider ... 2026-01-05 16:26 PST] message text
```

信封中的时间戳默认是 **主机本地时间**，精度为分钟。

你可以通过以下方式覆盖：

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
- `envelopeTimezone: "user"` 使用 `agents.defaults.userTimezone`（回退到主机时区）。
- 使用显式的 IANA 时区（例如 `"Europe/Vienna"`）以固定偏移量。
- `envelopeTimestamp: "off"` 从信封头中移除绝对时间戳。
- `envelopeElapsed: "off"` 移除经过时间后缀（`+2m` 风格）。

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

## 工具负载（原始提供商数据 + 规范化字段）

工具调用 (`channels.discord.readMessages`, `channels.slack.readMessages` 等) 返回 **原始提供商时间戳**。
我们还附加规范化字段以保持一致性：

- `timestampMs` (UTC 时间戳毫秒数)
- `timestampUtc` (ISO 8601 UTC 字符串)

原始提供商字段被保留。

## 用户系统提示中的时区

设置 `agents.defaults.userTimezone` 以告知模型用户的本地时区。如果未设置，
OpenClaw 在运行时解析 **主机时区**（不写入配置）。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

系统提示包括：

- 包含本地时间和时区的 `Current Date & Time` 部分
- `Time format: 12-hour` 或 `24-hour`

你可以使用 `agents.defaults.timeFormat` 控制提示格式 (`auto` | `12` | `24`)。

有关完整行为和示例，请参阅 [日期和时间](/date-time)。