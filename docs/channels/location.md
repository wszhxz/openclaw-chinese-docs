---
summary: "Inbound channel location parsing (Telegram/WhatsApp/Matrix) and context fields"
read_when:
  - Adding or modifying channel location parsing
  - Using location context fields in agent prompts or tools
title: "Channel Location Parsing"
---
# 频道位置解析

OpenClaw 将聊天频道中共享的位置标准化为：

- 附加到入站正文的可读文本，以及
- 自动回复上下文负载中的结构化字段。

目前支持：

- **Telegram** (位置图钉 + 场所 + 实时位置)
- **WhatsApp** (locationMessage + liveLocationMessage)
- **Matrix** (`m.location` 与 `geo_uri`)

## 文本格式化

位置被渲染为不带括号的易读行：

- 图钉：
  - `📍 48.858844, 2.294351 ±12m`
- 命名地点：
  - `📍 Eiffel Tower — Champ de Mars, Paris (48.858844, 2.294351 ±12m)`
- 实时分享：
  - `🛰 Live location: 48.858844, 2.294351 ±12m`

如果频道包含标题/注释，它将附加在下一行：

```
📍 48.858844, 2.294351 ±12m
Meet here
```

## 上下文字段

当存在位置时，这些字段会被添加到 `ctx`：

- `LocationLat` (number)
- `LocationLon` (number)
- `LocationAccuracy` (number, meters; optional)
- `LocationName` (string; optional)
- `LocationAddress` (string; optional)
- `LocationSource` (`pin | place | live`)
- `LocationIsLive` (boolean)

## 频道备注

- **Telegram**: 场所映射到 `LocationName/LocationAddress`；实时位置使用 `live_period`。
- **WhatsApp**: `locationMessage.comment` 和 `liveLocationMessage.caption` 作为标题行附加。
- **Matrix**: `geo_uri` 被解析为图钉位置；海拔被忽略且 `LocationIsLive` 始终为 false。