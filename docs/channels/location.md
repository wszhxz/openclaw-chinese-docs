---
summary: "Inbound channel location parsing (Telegram + WhatsApp) and context fields"
read_when:
  - Adding or modifying channel location parsing
  - Using location context fields in agent prompts or tools
title: "Channel Location Parsing"
---
# 通道位置解析

OpenClaw 将聊天通道中的共享位置规范化为：

- 附加到传入正文的人类可读文本，以及
- 自动回复上下文负载中的结构化字段。

当前支持：

- **Telegram** (位置标记 + 场所 + 实时位置)
- **WhatsApp** (locationMessage + liveLocationMessage)
- **Matrix** (`m.location` with `geo_uri`)

## 文本格式

位置以不带括号的友好行呈现：

- 标记：
  - `📍 48.858844, 2.294351 ±12m`
- 命名地点：
  - `📍 Eiffel Tower — Champ de Mars, Paris (48.858844, 2.294351 ±12m)`
- 实时共享：
  - `🛰 Live location: 48.858844, 2.294351 ±12m`

如果通道包含标题/评论，则附加在下一行：

```
📍 48.858844, 2.294351 ±12m
Meet here
```

## 上下文字段

当存在位置时，这些字段会被添加到 `ctx`：

- `LocationLat` (数字)
- `LocationLon` (数字)
- `LocationAccuracy` (数字，米；可选)
- `LocationName` (字符串；可选)
- `LocationAddress` (字符串；可选)
- `LocationSource` (`pin | place | live`)
- `LocationIsLive` (布尔值)

## 通道说明

- **Telegram**: 场所映射到 `LocationName/LocationAddress`；实时位置使用 `live_period`。
- **WhatsApp**: `locationMessage.comment` 和 `liveLocationMessage.caption` 作为标题行附加。
- **Matrix**: `geo_uri` 被解析为标记位置；海拔被忽略且 `LocationIsLive` 始终为假。