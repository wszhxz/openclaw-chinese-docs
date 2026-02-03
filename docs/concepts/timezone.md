---
summary: "Timezone handling for agents, envelopes, and prompts"
read_when:
  - You need to understand how timestamps are normalized for the model
  - Configuring the user timezone for system prompts
title: "Timezones"
---
# 时区

OpenClaw 对时间戳进行标准化，使模型看到一个 **单一参考时间**。

## 消息信封（默认为本地时区）

入站消息会被封装成如下格式：

```
[Provider ... 2026-01-05 16:26 PST] 消息内容
```

信封中的时间戳默认为 **主机本地时区**，精度为分钟。

您可以通过以下配置覆盖该设置：

```json5
{
  agents: {
    defaults: {
      envelopeTimezone: "local", // "utc" | "local" | "user" | IANA 时区
      envelopeTimestamp: "on", // "on" | "off"
      envelopeElapsed: "on", // "on" | "off"
    },
  },
}
```

- `envelopeTimezone: "utc"` 使用 UTC 时区。
- `envelopeTimezone: "user"` 使用 `agents.defaults.userTimezone`（若未设置则回退到主机时区）。
- 使用显式的 IANA 时区（例如 `"Europe/Vienna"`）以固定偏移量。
- `envelopeTimestamp: "off"` 会从信封头中移除绝对时间戳。
- `envelopeElapsed: "off"` 会移除时间流逝后缀（如 `+2m` 样式）。

### 示例

**本地（默认）：**

```
[Signal Alice +1555 2026-01-18 00:19 PST] 你好
```

**固定时区：**

```
[Signal Alice +1555 2026-01-18 06:19 GMT+1] 你好
```

**时间流逝：**

```
[Signal Alice +1555 +2m 2026-01-18T05:19Z] 后续跟进
```

## 工具负载（原始提供者数据 + 标准化字段）

工具调用（如 `channels.discord.readMessages`、`channels.slack.readMessages` 等）返回 **原始提供者时间戳**。
我们还会附加标准化字段以确保一致性：

- `timestampMs`（UTC 时间戳毫秒）
- `timestampUtc`（ISO 8601 UTC 字符串）

原始提供者字段将被保留。

## 系统提示中的用户时区

设置 `agents.defaults.userTimezone` 以告知模型用户的本地时区。若未设置，OpenClaw 会在运行时解析 **主机时区**（无需配置写入）。

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

系统提示包含以下内容：

- 包含本地时间和时区的 `当前日期和时间` 部分
- `时间格式：12小时制` 或 `24小时制`

您可以通过 `agents.defaults.timeFormat` 控制提示格式（`auto` | `12` | `24`）。

有关完整行为和示例，请参阅 [日期和时间](/date-time)。