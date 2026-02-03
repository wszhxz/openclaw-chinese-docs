---
summary: "Inbound channel location parsing (Telegram + WhatsApp) and context fields"
read_when:
  - Adding or modifying channel location parsing
  - Using location context fields in agent prompts or tools
title: "Channel Location Parsing"
---
# 频道位置解析

OpenClaw 将聊天频道中的共享位置标准化为：

- 添加到入站正文中的可读文本，以及
- 自动回复上下文负载中的结构化字段。

目前支持：

- **Telegram**（位置标记 + 场地 + 实时位置）
- **WhatsApp**（locationMessage + liveLocationMessage）
- **Matrix**（`m.location` 中的 `geo_uri`）

## 文本格式

位置以无括号的友好行形式呈现：

- 标记：
  - `📍 48.858844, 2.294351 ±12m`
- 命名地点：
  - `📍 埃菲尔铁塔 —— 马尔斯广场, 巴黎 (48.858844, 2.294351 ±12m)`
- 实时共享：
  - `🛰 实时位置：48.858844, 2.294351 ±12m`

如果频道包含说明/评论，则会附加在下一行：

```
📍 48.858844, 2.294351 ±12m
在此集合
``
```

## 上下文字段

当存在位置时，这些字段会添加到 `ctx` 中：

- `LocationLat`（数字）
- `LocationLon`（数字）
- `LocationAccuracy`（数字，单位为米；可选）
- `LocationName`（字符串；可选）
- `LocationAddress`（字符串；可选）
- `LocationSource`（`标记 | 地点 | 实时`）
- `LocationIsLive`（布尔值）

## 频道说明

- **Telegram**：场地映射到 `LocationName/LocationAddress`；实时位置使用 `live_period`。
- **WhatsApp**：`locationMessage.comment` 和 `liveLocationMessage.caption` 会作为说明行附加。
- **Matrix**：`geo_uri` 会被解析为标记位置；海拔被忽略且 `LocationIsLive` 始终为 false。