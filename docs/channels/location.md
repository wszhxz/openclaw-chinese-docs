---
summary: "Inbound channel location parsing (Telegram + WhatsApp) and context fields"
read_when:
  - Adding or modifying channel location parsing
  - Using location context fields in agent prompts or tools
title: "Channel Location Parsing"
---
# 频道位置解析

OpenClaw 将聊天频道中共享的位置信息标准化为：

- 附加在入站消息正文末尾的、便于人类阅读的文本，以及
- 自动回复上下文载荷（context payload）中的结构化字段。

当前支持的渠道：

- **Telegram**（位置标记 + 地点 + 实时位置）
- **WhatsApp**（`locationMessage` + `liveLocationMessage`）
- **Matrix**（``m.location`` 与 ``geo_uri``）

## 文本格式

位置信息以友好、无括号的行形式呈现：

- 位置标记（Pin）：
  - ``📍 48.858844, 2.294351 ±12m``
- 命名地点（Named place）：
  - ``📍 Eiffel Tower — Champ de Mars, Paris (48.858844, 2.294351 ±12m)``
- 实时共享（Live share）：
  - ``🛰 Live location: 48.858844, 2.294351 ±12m``

若频道消息包含标题/评论（caption/comment），则将其追加在下一行：

````
📍 48.858844, 2.294351 ±12m
Meet here
````

## 上下文字段

当存在位置信息时，以下字段将被添加到 ``ctx`` 中：

- ``LocationLat``（数字）
- ``LocationLon``（数字）
- ``LocationAccuracy``（数字，单位：米；可选）
- ``LocationName``（字符串；可选）
- ``LocationAddress``（字符串；可选）
- ``LocationSource``（``pin | place | live``）
- ``LocationIsLive``（布尔值）

## 各渠道说明

- **Telegram**：地点（venues）映射为 ``LocationName/LocationAddress``；实时位置使用 ``live_period``。
- **WhatsApp**：``locationMessage.comment`` 和 ``liveLocationMessage.caption`` 将作为标题行（caption line）追加。
- **Matrix**：``geo_uri`` 被解析为位置标记（pin location）；海拔（altitude）被忽略，且 ``LocationIsLive`` 恒为 `false`。