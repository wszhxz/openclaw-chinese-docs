---
summary: "Date and time handling across envelopes, prompts, tools, and connectors"
read_when:
  - You are changing how timestamps are shown to the model or users
  - You are debugging time formatting in messages or system prompt output
title: "Date and Time"
---
# 日期与时间

OpenClaw 默认对传输时间戳使用**主机本地时间**，仅在系统提示词中使用**用户时区**。  
保留提供方的时间戳，以确保工具维持其原生语义（可通过 ``session_status`` 获取当前时间）。

## 消息信封（默认为本地时间）

入站消息将被包裹在一个时间戳中（精确到分钟）：

```
[Provider ... 2026-01-05 16:26 PST] message text
```

该信封时间戳**默认为主机本地时间**，与提供方所在时区无关。

您可覆盖此行为：

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
- `envelopeTimezone: "user"` 使用 `agents.defaults.userTimezone`（若不可用则回退至主机时区）。
- 使用显式的 IANA 时区（例如 `"America/Chicago"`）指定固定时区。
- `envelopeTimestamp: "off"` 从信封头中移除绝对时间戳。
- `envelopeElapsed: "off"` 移除经过时间后缀（即 `+2m` 格式）。

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

## 系统提示词：当前日期与时间

若已知用户时区，系统提示词中将包含一个专用的 **当前日期与时间** 区域，其中仅包含**时区信息**（不含钟表/时间格式），以保障提示词缓存的稳定性：

```
Time zone: America/Chicago
```

当智能体需要获取当前时间时，请使用 ``session_status`` 工具；状态卡片中包含一行时间戳。

## 系统事件行（默认为本地时间）

插入智能体上下文的排队系统事件，其前缀时间戳采用与消息信封相同的时区选择逻辑（默认：主机本地时间）。

```
System: [2026-01-12 12:19:17 PST] Model switched.
```

### 配置用户时区及格式

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

- `userTimezone` 设置提示词上下文所用的**用户本地时区**。
- `timeFormat` 控制提示词中**12 小时制 / 24 小时制**的显示方式。`auto` 遵循操作系统偏好设置。

## 时间格式检测（自动）

当启用 ``timeFormat: "auto"`` 时，OpenClaw 将检查操作系统偏好设置（macOS / Windows），并回退至区域设置格式。检测所得值**按进程缓存**，以避免重复调用系统接口。

## 工具载荷与连接器（原始提供方时间 + 标准化字段）

通道类工具返回**提供方原生时间戳**，并额外添加标准化字段以保证一致性：

- `timestampMs`：自 Unix 纪元起的毫秒数（UTC）
- `timestampUtc`：ISO 8601 格式的 UTC 字符串

原始提供方字段予以保留，确保无任何信息丢失。

- Slack：来自 API 的类 epoch 字符串  
- Discord：UTC ISO 时间戳  
- Telegram / WhatsApp：提供方特定的数值型 / ISO 时间戳  

如需本地时间，请基于已知时区在下游进行转换。

## 相关文档

- [系统提示词](/concepts/system-prompt)  
- [时区](/concepts/timezone)  
- [消息](/concepts/messages)