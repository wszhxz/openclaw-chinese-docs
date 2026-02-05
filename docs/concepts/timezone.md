---
summary: "Timezone handling for agents, envelopes, and prompts"
read_when:
  - You need to understand how timestamps are normalized for the model
  - Configuring the user timezone for system prompts
title: "Timezones"
---
# 时区

OpenClaw 标准化时间戳，使模型看到一个**单一参考时间**。

## 消息信封（默认为本地时间）

传入消息被包装在一个信封中，如下所示：

```
[Provider ... 2026-01-05 16:26 PST] message text
```

信封中的时间戳**默认为主机本地时间**，精度为分钟。

您可以使用以下方式覆盖此设置：

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
- 使用明确的 IANA 时区（例如 `"Europe/Vienna"`）来设置固定偏移量。
- `envelopeTimestamp: "off"` 从信封头中移除绝对时间戳。
- `envelopeElapsed: "off"` 移除经过时间后缀（即 `+2m` 样式）。

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

## 工具负载（原始提供者数据 + 标准化字段）

工具调用（`channels.discord.readMessages`、`channels.slack.readMessages` 等）返回**原始提供者时间戳**。
我们还附加标准化字段以确保一致性：

- `timestampMs`（UTC 纪元毫秒）
- `timestampUtc`（ISO 8601 UTC 字符串）

原始提供者字段得以保留。

## 系统提示中的用户时区

设置 `agents.defaults.userTimezone` 来告诉模型用户的本地时区。如果未设置，
OpenClaw 在运行时解析**主机时区**（无需写入配置）。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

系统提示包含：

- 带有本地时间和时区的 `Current Date & Time` 部分
- `Time format: 12-hour` 或 `24-hour`

您可以使用 `agents.defaults.timeFormat`（`auto` | `12` | `24`）控制提示格式。

有关完整行为和示例，请参见 [日期和时间](/date-time)。