---
summary: "Slash commands: text vs native, config, and supported commands"
read_when:
  - Using or configuring chat commands
  - Debugging command routing or permissions
title: "Slash Commands"
---
# 斜杠命令

命令由网关处理。大多数命令必须作为以 `/` 开头的**独立消息**发送。
主机专用的bash聊天命令使用 `! <cmd>`（`/bash <cmd>` 为别名）。

存在两个相关系统：

- **命令**：独立的 `/...` 消息。
- **指令**：`/think`、`/verbose`、`/reasoning`、`/elevated`、`/exec`、`/model`、`/queue`。
  - 指令在模型看到消息前会被移除。
  - 在普通聊天消息（非仅指令）中，它们被视为“内联提示”，**不会**持久化会话设置。
  - 在仅指令消息（消息仅包含指令）中，它们会持久化到会话并回复确认。
  - 指令仅对**授权发送者**（频道白名单/配对加上 `commands.useAccessGroups`）生效。
    未授权发送者会将指令视为普通文本。

还有一些**内联快捷方式**（仅限白名单/授权发送者）：`/help`、`/commands`、`/status`、`/whoami`（`/id`）。
它们会立即执行，消息在模型看到前会被移除，剩余文本会继续通过正常流程。

## 配置

```json5
{
  commands: {
    native: "auto",
    nativeSkills: "auto",
    text: true,
    bash: false,
    bashForegroundMs: 2000,
    config: false,
    debug: false,
    restart: false,
    useAccessGroups: true,
  },
}
```

- `commands.text`（默认 `true`）启用聊天消息中 `/...` 的解析。
  - 在无原生命令的平台（WhatsApp/WebChat/Signal/iMessage/Google Chat/MS Teams）中，即使设置为 `false`，文本命令仍有效。
- `commands.native`（默认 `"auto"`）注册原生命令。
  - 自动：Discord/Telegram 开启；Slack 关闭（直到你添加斜杠命令）；无原生支持的提供者被忽略。
  - 设置 `channels.discord.commands.native`、`channels.telegram.commands.native` 或 `channels.slack.commands.native` 可覆盖每个提供者（布尔值或 `"auto"`）。
  - `false` 会在启动时清除 Discord/Telegram 上已注册的命令。Slack 命令在 Slack 应用中管理，不会自动移除。
- `commands.nativeSkills`（默认 `"auto"`）在支持时注册**技能**命令。
  - 自动：Discord/Telegram 开启；Slack 关闭（Slack 需为每个技能创建斜杠命令）。
  - 设置 `channels.discord.commands.nativeSkills`、`channels.telegram.commands.nativeSkills` 或 `channels.slack.commands.nativeSkills` 可覆盖每个提供者（布尔值或 `"auto"`）。
- `commands.bash`（默认 `false`）启用 `! <cmd>`。
- `commands.bashForegroundMs`（默认 2000）设置 bash 前台等待时间。
- `commands.config`（默认 `false`）启用配置。
- `commands.debug`（默认 `false`）启用调试。
- `commands.restart`（默认 `false`）启用重启。
- `commands.useAccessGroups`（默认 `true`）启用访问组。

## 命令列表

- `/help`：帮助。
- `/commands`：命令列表。
- `/status`：状态。
- `/whoami`：我是谁。
- `/id`：ID。
- `/model`：模型。
- `/debug`：调试。
- `/config`：配置。
- `/stop`：停止。
- `/exec`：执行。
- `/verbose`：详细。
- `/reasoning`：推理。
- `/elevated`：提升权限。
- `/queue`：队列。
- `/think`：思考。
- `/bash`：bash。
- `/model list`：模型列表。
- `/model status`：模型状态。
- `/model openai/gpt-5.2`：模型 openai/gpt-5.2。
- `/model opus@anthropic:default`：模型 opus@anthropic:default。
- `/model 3`：模型 3。
- `/model list`：模型列表。
- `/model status`：模型状态。
- `/debug show`：显示调试。
- `/debug set messages.responsePrefix="[openclaw]"`：设置调试。
- `/debug unset messages.responsePrefix`：取消设置调试。
- `/debug reset`：重置调试。
- `/config show`：显示配置。
- `/config show messages.responsePrefix`：显示配置。
- `/config get messages.responsePrefix`：获取配置。
- `/config set messages.responsePrefix="[openclaw]"`：设置配置。
- `/config unset messages.responsePrefix`：取消设置配置。

## 表面说明（在哪里显示什么）

- **提供者使用/配额**（示例：“Claude 剩余 80%”）在启用使用跟踪时显示在 `/status` 中。
- **每条回复的标记/成本**由 `/usage off|tokens|full` 控制（附加在正常回复后）。
- `/model status` 关于**模型/认证/端点**，而非使用。

## 模型选择 (`/model`)

`/model` 作为指令实现。

示例：

```
/model
/model list
/model 3
/model openai/gpt-5.2
/model opus@anthropic:default
/model status
```

说明：

- `/model` 和 `/model list` 显示紧凑的编号选择器（模型家族 + 可用提供者）。
- `/model <#>` 从该选择器中选择（尽可能优先当前提供者）。
- `/model status` 显示详细视图，包括配置的提供者端点 (`baseUrl`) 和 API 模式 (`api`)（如有）。

##