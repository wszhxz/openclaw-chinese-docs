---
summary: "Date and time handling across envelopes, prompts, tools, and connectors"
read_when:
  - You are changing how timestamps are shown to the model or users
  - You are debugging time formatting in messages or system prompt output
title: "Date and Time"
---
# 日期与时间

OpenClaw 默认使用**主机本地时间作为传输时间戳**，以及**仅在系统提示中使用用户时区**。
提供者时间戳会被保留，以便工具保持其原生语义（当前时间可通过 `session_status` 获取）。

## 消息信封（默认为本地时间）

入站消息会用时间戳（分钟精度）进行包装：

```
[Provider ... 2026-01-05 16:26 PST] message text
```

此信封时间戳**默认为主机本地时间**，无论提供者的时区如何。

您可以覆盖此行为：

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
- `envelopeTimezone: "local"` 使用主机时区。
- `envelopeTimezone: "user"` 使用 `agents.defaults.userTimezone`（回退到主机时区）。
- 使用明确的 IANA 时区（例如 `"America/Chicago"`）来固定时区。
- `envelopeTimestamp: "off"` 从信封头中移除绝对时间戳。
- `envelopeElapsed: "off"` 移除经过时间后缀（即 `+2m` 样式）。

### 示例

**本地时间（默认）：**

```
[WhatsApp +1555 2026-01-18 00:19 PST] hello
```

**用户时区：**

```
[WhatsApp +1555 2026-01-18 00:19 CST] hello
```

**启用经过时间：**

```
[WhatsApp +1555 +30s 2026-01-18T05:19Z] follow-up
```

## 系统提示：当前日期与时间

如果已知用户时区，系统提示会包含一个专门的
**当前日期与时间** 部分，其中仅包含**时区**（无时钟/时间格式）
以保持提示缓存稳定：

```
Time zone: America/Chicago
```

当代理需要当前时间时，请使用 `session_status` 工具；状态卡片包含时间戳行。

## 系统事件行（默认为本地时间）

插入到代理上下文中的排队系统事件会以前缀时间戳开头，
使用与消息信封相同的时区选择（默认：主机本地时间）。

```
System: [2026-01-12 12:19:17 PST] Model switched.
```

### 配置用户时区 + 格式

```json5
{
  agents: {
    defaults: {
      userTimezone: "America/Chicago",
      timeFormat: "auto", // auto | 12 | 24
    },
  },
}
```

- `userTimezone` 设置提示上下文的**用户本地时区**。
- `timeFormat` 控制提示中的**12小时/24小时显示**。`auto` 遵循操作系统偏好。

## 时间格式检测（自动）

当 `timeFormat: "auto"` 时，OpenClaw 会检查操作系统偏好（macOS/Windows）
并回退到区域设置格式。检测值会**按进程缓存**
以避免重复的系统调用。

## 工具载荷 + 连接器（原始提供者时间 + 标准化字段）

通道工具返回**提供者原生时间戳**并添加标准化字段以确保一致性：

- `timestampMs`：纪元毫秒（UTC）
- `timestampUtc`：ISO 8601 UTC 字符串

原始提供者字段会被保留，因此不会丢失任何信息。

- Slack：来自 API 的类似纪元的字符串
- Discord：UTC ISO 时间戳
- Telegram/WhatsApp：提供者特定的数字/ISO 时间戳

如果您需要本地时间，请使用已知时区在下游进行转换。

## 相关文档

- [系统提示](/concepts/system-prompt)
- [时区](/concepts/timezone)
- [消息](/concepts/messages)