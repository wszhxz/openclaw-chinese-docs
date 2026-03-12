---
summary: "Elevated exec mode and /elevated directives"
read_when:
  - Adjusting elevated mode defaults, allowlists, or slash command behavior
title: "Elevated Mode"
---
# 提升模式（/elevated 指令）

## 功能

- `/elevated on` 在网关主机上运行并保持执行批准（与 `/elevated ask` 相同）。
- `/elevated full` 在网关主机上运行**并**自动批准执行（跳过执行批准）。
- `/elevated ask` 在网关主机上运行但保持执行批准（与 `/elevated on` 相同）。
- `on`/`ask` **不**强制 `exec.security=full`；配置的安全/询问策略仍然适用。
- 仅当代理被**沙箱化**时才改变行为（否则执行已经在主机上运行）。
- 指令形式：`/elevated on|off|ask|full`, `/elev on|off|ask|full`。
- 仅接受 `on|off|ask|full`；其他任何内容都会返回提示且不会改变状态。

## 控制的内容（以及不控制的内容）

- **可用性门控**：`tools.elevated` 是全局基线。`agents.list[].tools.elevated` 可以进一步限制每个代理的提升（两者都必须允许）。
- **会话状态**：`/elevated on|off|ask|full` 设置当前会话密钥的提升级别。
- **内联指令**：消息中的 `/elevated on|ask|full` 仅适用于该消息。
- **组**：在群聊中，只有当提到代理时才会尊重提升指令。绕过提及要求的仅命令消息被视为已提及。
- **主机执行**：提升强制将 `exec` 放到网关主机上；`full` 也设置 `security=full`。
- **批准**：`full` 跳过执行批准；`on`/`ask` 在允许列表/询问规则需要时遵守它们。
- **非沙箱化代理**：对位置无操作；仅影响门控、日志记录和状态。
- **工具策略仍然适用**：如果 `exec` 被工具策略拒绝，则不能使用提升。
- **与 `/exec` 分开**：`/exec` 调整授权发送者的每会话默认值，并且不需要提升。

## 解析顺序

1. 消息上的内联指令（仅适用于该消息）。
2. 会话覆盖（通过发送仅包含指令的消息来设置）。
3. 全局默认值（配置中的 `agents.defaults.elevatedDefault`）。

## 设置会话默认值

- 发送一条**仅**包含指令的消息（允许空白），例如 `/elevated full`。
- 发送确认回复（`Elevated mode set to full...` / `Elevated mode disabled.`）。
- 如果提升访问被禁用或发送者不在批准的允许列表中，指令会回复一个可操作的错误并且不会改变会话状态。
- 发送 `/elevated`（或 `/elevated:`）且不带参数以查看当前的提升级别。

## 可用性 + 允许列表

- 功能门控：`tools.elevated.enabled`（即使代码支持，默认情况下也可以通过配置关闭）。
- 发送者允许列表：`tools.elevated.allowFrom` 带有每个提供者的允许列表（例如 `discord`, `whatsapp`）。
- 未加前缀的允许列表条目仅匹配发送者范围的身份值（`SenderId`, `SenderE164`, `From`）；接收者路由字段永远不会用于提升授权。
- 可变的发送者元数据需要显式前缀：
  - `name:<value>` 匹配 `SenderName`
  - `username:<value>` 匹配 `SenderUsername`
  - `tag:<value>` 匹配 `SenderTag`
  - `id:<value>`, `from:<value>`, `e164:<value>` 可用于显式身份定位
- 每个代理的门控：`agents.list[].tools.elevated.enabled`（可选；只能进一步限制）。
- 每个代理的允许列表：`agents.list[].tools.elevated.allowFrom`（可选；设置后，发送者必须同时匹配全局和每个代理的允许列表）。
- Discord 回退：如果省略了 `tools.elevated.allowFrom.discord`，则使用 `channels.discord.allowFrom` 列表作为回退（遗留：`channels.discord.dm.allowFrom`）。设置 `tools.elevated.allowFrom.discord`（甚至是 `[]`）以覆盖。每个代理的允许列表**不**使用回退。
- 所有门控都必须通过；否则提升被视为不可用。

## 日志记录 + 状态

- 提升执行调用在信息级别记录。
- 会话状态包括提升模式（例如 `elevated=ask`, `elevated=full`）。