---
summary: "Date and time handling across envelopes, prompts, tools, and connectors"
read_when:
  - You are changing how timestamps are shown to the model or users
  - You are debugging time formatting in messages or system prompt output
title: "Date and Time"
---
# 日期与时间

OpenClaw 默认使用 **主机本地时间作为传输时间戳** 和 **仅在系统提示中使用用户时区**。
提供者的时间戳会被保留，以便工具保持其原生语义（当前时间可通过 `session_status` 获取）。

## 消息信封（默认为本地）

传入的消息会附带一个时间戳（精确到分钟）：

```
[Provider ... 2026-01-05 16:26 PST] message text
```

此信封时间戳默认为 **主机本地时间**，无论提供者时区如何。

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
- 使用显式 IANA 时区（例如 `"America/Chicago"`）以固定时区。
- `envelopeTimestamp: "off"` 从信封头中移除绝对时间戳。
- `envelopeElapsed: "off"` 移除经过时间后缀（`+2m` 样式）。

### 示例

**本地（默认）：**

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

如果已知用户时区，系统提示将包含一个专用的
**当前日期与时间** 部分，仅显示 **时区**（不显示时钟/时间格式）
以保持提示缓存稳定：

```
Time zone: America/Chicago
```

当代理需要当前时间时，使用 `session_status` 工具；状态
卡片中包含一个时间戳行。

## 系统事件行（默认为本地）

插入代理上下文的排队系统事件前缀带有时间戳，使用
与消息信封相同的时区选择（默认：主机本地）。

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

- `userTimezone` 设置提示上下文中的 **用户本地时区**。
- `timeFormat` 控制提示中的 **12小时/24小时显示**。`auto` 遵循操作系统偏好设置。

## 时间格式检测（自动）

当 `timeFormat: "auto"`，OpenClaw 检查操作系统偏好设置（macOS/Windows）
并回退到区域设置格式。检测到的值按 **进程缓存**
以避免重复的系统调用。

## 工具负载 + 连接器（原始提供者时间 + 规范化字段）

通道工具返回 **提供者原生时间戳** 并添加规范化字段以保持一致性：

- `timestampMs`：自纪元以来的毫秒数（UTC）
- `timestampUtc`：ISO 8601 UTC 字符串

原始提供者字段被保留，以防止丢失信息。

- Slack：API 中的类似自纪元字符串
- Discord：UTC ISO 时间戳
- Telegram/WhatsApp：提供者特定的数字/ISO 时间戳

如果您需要本地时间，请使用已知时区进行下游转换。

## 相关文档

- [系统提示](/concepts/system-prompt)
- [时区](/concepts/timezone)
- [消息](/concepts/messages)