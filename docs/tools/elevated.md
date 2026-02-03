---
summary: "Elevated exec mode and /elevated directives"
read_when:
  - Adjusting elevated mode defaults, allowlists, or slash command behavior
title: "Elevated Mode"
---
# 提升模式 (/elevated 指令)

## 它的作用

- `/elevated on` 在网关主机上运行并保持执行审批（与 `/elevated ask` 相同）。
- `/elevated full` 在网关主机上运行 **并** 自动批准执行（跳过执行审批）。
- `/elevated ask` 在网关主机上运行但保持执行审批（与 `/elevated on` 相同）。
- `on`/`ask` 不会强制 `exec.security=full`；配置的权限/询问策略仍适用。
- 仅在代理 **沙箱化** 时改变行为（否则执行已直接在主机上运行）。
- 指令形式：`/elevated on|off|ask|full`，`/elev on|off|ask|full`。
- 仅接受 `on|off|ask|full`；其他内容返回提示且不更改状态。

## 它控制的内容（以及它不控制的内容）

- **可用性控制**：`tools.elevated` 是全局基准。`agents.list[].tools.elev,ated` 可进一步限制每个代理的提升权限（两者都必须允许）。
- **会话状态**：`/elevated on|off|ask|full` 设置当前会话密钥的提升级别。
- **内联指令**：消息内的 `/elevated on|ask|full` 仅适用于该消息。
- **群组**：在群聊中，仅当代理被提及才遵守提升指令。跳过提及要求的纯命令消息被视为已提及。
- **主机执行**：提升强制将 `exec` 运行在网关主机上；`full` 同时设置 `security=full`。
- **审批**：`full` 跳过执行审批；`on`/`ask` 在允许列表/询问规则要求时遵守审批。
- **未沙箱化代理**：对位置无影响；仅影响控制、日志和状态。
- **工具策略仍适用**：如果工具策略拒绝 `exec`，提升无法使用。
- **与 `/exec` 分离**：`/exec` 调整授权发送者的会话默认值，且无需提升。

## 解析顺序

1. 消息内的内联指令（仅适用于该消息）。
2. 会话覆盖（通过发送仅指令的消息设置）。
3. 全局默认值（配置中的 `agents.defaults.elevatedDefault`）。

## 设置会话默认值

- 发送仅包含指令的消息（允许空格），例如 `/elevated full`。
- 会发送确认回复（“提升模式设置为 full...” / “提升模式已禁用。”）。
- 如果提升访问被禁用或发送者不在批准的允许列表中，指令将回复可操作的错误且不更改会话状态。
- 发送 `/elevated`（或 `/elevated:`）无参数以查看当前提升级别。

## 可用性 + 允许列表

- 功能控制：`tools.elevated.enabled`（可通过配置关闭，即使代码支持）。
- 发送者允许列表：`tools.elevated.allowFrom` 包含每个提供者的允许列表（例如 `discord`、`whatsapp`）。
- 每个代理控制：`agents.list[].tools.elevated.enabled`（可选；只能进一步限制）。
- 每个代理允许列表：`agents.list[].tools.elevated.allowFrom`（可选；设置时，发送者必须同时匹配全局 + 每个代理允许列表）。
- Discord 回退：如果 `tools.elevated.allowFrom.discord` 被省略，则使用 `channels.discord.dm.allowFrom` 列表作为回退。设置 `tools.elevated.allowFrom.discord`（即使为 `[]`）以覆盖。每个代理允许列表 **不** 使用回退。
- 所有控制必须通过；否则提升被视为不可用。

## 日志 + 状态

- 提升执行调用以信息级别记录。
- 会话状态包含提升模式（例如 `elevated=ask`，`elevated=full`）。