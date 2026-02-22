---
summary: "Elevated exec mode and /elevated directives"
read_when:
  - Adjusting elevated mode defaults, allowlists, or slash command behavior
title: "Elevated Mode"
---
# 提升模式 (/elevated 指令)

## 它的作用

- `/elevated on` 在网关主机上运行并保留执行审批（与 `/elevated ask` 相同）。
- `/elevated full` 在网关主机上运行 **并** 自动批准执行（跳过执行审批）。
- `/elevated ask` 在网关主机上运行但保留执行审批（与 `/elevated on` 相同）。
- `on`/`ask` 不会强制 `exec.security=full`；配置的安全/询问策略仍然适用。
- 仅在代理被 **沙盒化** 时更改行为（否则执行已经在主机上运行）。
- 指令形式：`/elevated on|off|ask|full`，`/elev on|off|ask|full`。
- 仅接受 `on|off|ask|full`；其他任何内容都会返回提示且不改变状态。

## 它控制的内容（以及它不控制的内容）

- **可用性门控**：`tools.elevated` 是全局基线。`agents.list[].tools.elevated` 可以进一步限制每个代理的提升（两者都必须允许）。
- **会话状态**：`/elevated on|off|ask|full` 设置当前会话密钥的提升级别。
- **内联指令**：消息中的 `/elevated on|ask|full` 仅适用于该消息。
- **组**：在群聊中，提升指令仅在代理被提及时才被认可。绕过提及要求的命令消息被视为已提及。
- **主机执行**：提升强制将 `exec` 放置在网关主机上；`full` 也设置 `security=full`。
- **审批**：`full` 跳过执行审批；`on`/`ask` 在白名单/询问规则要求时遵守它们。
- **非沙盒化代理**：对位置无操作；仅影响门控、日志记录和状态。
- **工具策略仍然适用**：如果 `exec` 被工具策略拒绝，则无法使用提升。
- **独立于 `/exec`**：`/exec` 调整授权发送者的会话默认值，并且不需要提升。

## 解析顺序

1. 消息中的内联指令（仅适用于该消息）。
2. 会话覆盖（通过发送仅包含指令的消息设置）。
3. 全局默认值（配置中的 `agents.defaults.elevatedDefault`）。

## 设置会话默认值

- 发送一条 **仅** 包含指令的消息（允许空格），例如 `/elevated full`。
- 发送确认回复（`Elevated mode set to full...` / `Elevated mode disabled.`）。
- 如果提升访问被禁用或发送者不在批准的白名单中，指令会回复一个可操作的错误并且不会更改会话状态。
- 发送 `/elevated`（或 `/elevated:`）不带参数以查看当前的提升级别。

## 可用性 + 白名单

- 功能门控：`tools.elevated.enabled`（即使代码支持，默认也可以通过配置关闭）。
- 发送者白名单：`tools.elevated.allowFrom` 带有每个提供商的白名单（例如 `discord`，`whatsapp`）。
- 每个代理的门控：`agents.list[].tools.elevated.enabled`（可选；只能进一步限制）。
- 每个代理的白名单：`agents.list[].tools.elevated.allowFrom`（可选；设置后，发送者必须匹配 **全局** + **每个代理** 的白名单）。
- Discord 备用：如果省略 `tools.elevated.allowFrom.discord`，则使用 `channels.discord.allowFrom` 列表作为备用（旧版：`channels.discord.dm.allowFrom`）。设置 `tools.elevated.allowFrom.discord`（甚至 `[]`）以覆盖。每个代理的白名单 **不** 使用备用。
- 所有门控必须通过；否则提升被视为不可用。

## 日志记录 + 状态

- 提升执行调用以信息级别记录。
- 会话状态包括提升模式（例如 `elevated=ask`，`elevated=full`）。