---
summary: "Slash commands: text vs native, config, and supported commands"
read_when:
  - Using or configuring chat commands
  - Debugging command routing or permissions
title: "Slash Commands"
---
# 斜杠命令

命令由网关处理。大多数命令必须作为以 `/` 开头的**独立**消息发送。
仅主机的bash聊天命令使用 `! <cmd>`（其中 `/bash <cmd>` 是别名）。

有两个相关的系统：

- **Commands**: 独立的 `/...` 消息。
- **Directives**: `/think`, `/verbose`, `/reasoning`, `/elevated`, `/exec`, `/model`, `/queue`。
  - 在模型看到消息之前，指令会被移除。
  - 在正常的聊天消息中（不是仅包含指令的消息），它们被视为“内联提示”，并且**不**会持久化会话设置。
  - 在仅包含指令的消息中（消息仅包含指令），它们会持久化到会话，并回复确认信息。
  - 指令仅适用于**授权的发送者**。如果设置了 `commands.allowFrom`，它就是唯一的
    允许列表；否则授权来自频道允许列表/配对加上 `commands.useAccessGroups`。
    未经授权的发送者会看到指令被视为纯文本。

还有一些**内联快捷方式**（仅允许列表/授权的发送者可用）：`/help`, `/commands`, `/status`, `/whoami` (`/id`)。
它们会立即运行，在模型看到消息之前被移除，剩余的文本继续通过正常流程。

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
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- `commands.text` (默认 `true`) 启用在聊天消息中解析 `/...`。
  - 在不支持原生命令的平台上（WhatsApp/WebChat/Signal/iMessage/Google Chat/MS Teams），即使将此设置为 `false`，文本命令仍然有效。
- `commands.native` (默认 `"auto"`) 注册原生命令。
  - 自动：Discord/Telegram 开启；Slack 关闭（直到你添加斜杠命令）；不支持原生功能的提供商忽略此设置。
  - 设置 `channels.discord.commands.native`，`channels.telegram.commands.native` 或 `channels.slack.commands.native` 以按提供商覆盖（布尔值或 `"auto"`）。
  - `false` 在启动时清除 Discord/Telegram 上先前注册的命令。Slack 命令在 Slack 应用中管理，并不会自动删除。
- `commands.nativeSkills` (默认 `"auto"`) 当支持时原生注册 **skill** 命令。
  - 自动：Discord/Telegram 开启；Slack 关闭（Slack 需要为每个 skill 创建一个斜杠命令）。
  - 设置 `channels.discord.commands.nativeSkills`，`channels.telegram.commands.nativeSkills` 或 `channels.slack.commands.nativeSkills` 以按提供商覆盖（布尔值或 `"auto"`）。
- `commands.bash` (默认 `false`) 启用 `! <cmd>` 运行主机 shell 命令 (`/bash <cmd>` 是别名；需要 `tools.elevated` 允许列表)。
- `commands.bashForegroundMs` (默认 `2000`) 控制 bash 在切换到后台模式之前的等待时间 (`0` 立即后台)。
- `commands.config` (默认 `false`) 启用 `/config` (读取/写入 `openclaw.json`)。
- `commands.debug` (默认 `false`) 启用 `/debug` (仅运行时覆盖)。
- `commands.allowFrom` (可选) 为每个提供商设置命令授权允许列表。配置后，它是命令和指令的唯一授权源（频道允许列表/配对和 `commands.useAccessGroups` 被忽略）。使用 `"*"` 作为全局默认值；特定于提供商的密钥会覆盖它。
- `commands.useAccessGroups` (默认 `true`) 当未设置 `commands.allowFrom` 时强制执行命令的允许列表/策略。

## 命令列表

文本 + 原生（当启用时）：

- `/help`
- `/commands`
- `/skill <name> [input]` (按名称运行技能)
- `/status` (显示当前状态；包括当前模型提供商的使用情况/配额（如果可用））
- `/allowlist` (列出/添加/删除白名单条目)
- `/approve <id> allow-once|allow-always|deny` (解决执行批准提示)
- `/context [list|detail|json]` (解释“上下文”；`detail` 显示每个文件 + 每个工具 + 每个技能 + 系统提示大小)
- `/whoami` (显示您的发送者ID；别名：`/id`)
- `/subagents list|stop|log|info|send` (检查、停止、记录或向当前会话的子代理运行发送消息)
- `/config show|get|set|unset` (将配置持久化到磁盘，仅限所有者；需要 `commands.config: true`)
- `/debug show|set|unset|reset` (运行时覆盖，仅限所有者；需要 `commands.debug: true`)
- `/usage off|tokens|full|cost` (每响应使用情况页脚或本地成本摘要)
- `/tts off|always|inbound|tagged|status|provider|limit|summary|audio` (控制TTS；参见 [/tts](/tts))
  - Discord: 原生命令是 `/voice` (Discord 保留 `/tts`)；文本 `/tts` 仍然有效。
- `/stop`
- `/restart`
- `/dock-telegram` (别名：`/dock_telegram`) (切换回复到Telegram)
- `/dock-discord` (别名：`/dock_discord`) (切换回复到Discord)
- `/dock-slack` (别名：`/dock_slack`) (切换回复到Slack)
- `/activation mention|always` (仅限群组)
- `/send on|off|inherit` (仅限所有者)
- `/reset` 或 `/new [model]` (可选模型提示；其余部分将传递)
- `/think <off|minimal|low|medium|high|xhigh>` (按模型/提供商动态选择；别名：`/thinking`, `/t`)
- `/verbose on|full|off` (别名：`/v`)
- `/reasoning on|off|stream` (别名：`/reason`；启用时，发送一个带有前缀 `Reasoning:` 的单独消息；`stream` = 仅Telegram草稿)
- `/elevated on|off|ask|full` (别名：`/elev`；`full` 跳过执行批准)
- `/exec host=<sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>` (发送 `/exec` 显示当前)
- `/model <name>` (别名：`/models`；或从 `agents.defaults.models.*.alias` 发送 `/<alias>`)
- `/queue <mode>` (加上选项如 `debounce:2s cap:25 drop:summarize`；发送 `/queue` 查看当前设置)
- `/bash <command>` (仅限主机；`! <command>` 的别名；需要 `commands.bash: true` + `tools.elevated` 白名单)

纯文本：

- `/compact [instructions]` (参见 [/concepts/compaction](/concepts/compaction))
- `! <command>` (仅限主机；一次一个；对长时间运行的任务使用 `!poll` + `!stop`)
- `!poll` (检查输出/状态；接受可选的 `sessionId`；`/bash poll` 也有效)
- `!stop` (停止正在运行的bash任务；接受可选的 `sessionId`；`/bash stop` 也有效)

注释：

- 命令在命令和参数之间可选接受一个 `:`（例如 `/think: high`, `/send: on`, `/help:`）。
- `/new <model>` 接受一个模型别名 `provider/model`，或提供者名称（模糊匹配）；如果没有匹配项，则文本被视为消息正文。
- 有关完整提供者使用情况的细分，请使用 `openclaw status --usage`。
- `/allowlist add|remove` 需要 `commands.config=true` 并尊重频道 `configWrites`。
- `/usage` 控制每个响应的使用情况页脚；`/usage cost` 从 OpenClaw 会话日志打印本地成本摘要。
- `/restart` 默认处于禁用状态；设置 `commands.restart: true` 以启用它。
- `/verbose` 用于调试和额外的可见性；正常使用时请保持 **关闭** 状态。
- `/reasoning`（和 `/verbose`）在群组设置中存在风险：它们可能会泄露您不打算公开的内部推理或工具输出。建议在群聊中尽量避免使用它们。
- **快速路径：** 允许列表中的发件人发送的仅包含命令的消息会立即处理（绕过队列 + 模型）。
- **群组提及门控：** 允许列表中的发件人发送的仅包含命令的消息会绕过提及要求。
- **内联快捷方式（仅限允许列表中的发件人）：** 某些命令也可以嵌入到正常消息中，并且在模型看到剩余文本之前会被剥离。
  - 示例：`hey /status` 触发状态回复，而剩余文本将继续通过正常流程。
- 目前：`/help`, `/commands`, `/status`, `/whoami` (`/id`)。
- 未经授权的仅包含命令的消息会被静默忽略，内联 `/...` 标记被视为纯文本。
- **技能命令：** `user-invocable` 技能作为斜杠命令暴露。名称被清理为 `a-z0-9_`（最多 32 个字符）；冲突项会附加数字后缀（例如 `_2`）。
  - `/skill <name> [input]` 按名称运行技能（当原生命令限制阻止按技能命令时很有用）。
  - 默认情况下，技能命令会被转发到模型作为正常请求。
  - 技能可以选择声明 `command-dispatch: tool` 以直接将命令路由到工具（确定性，无模型）。
  - 示例：`/prose`（OpenProse 插件）— 请参阅 [OpenProse](/prose)。
- **原生命令参数：** Discord 使用自动完成功能动态选项（以及省略必需参数时的按钮菜单）。Telegram 和 Slack 在命令支持选择且省略参数时显示按钮菜单。

## 使用场景（什么显示在哪里）

- **提供者使用情况/配额**（示例：“Claude 剩余 80%”）在启用使用情况跟踪时显示在当前模型提供者的 `/status` 中。
- **每个响应的令牌/成本** 由 `/usage off|tokens|full` 控制（附加到正常回复）。
- `/model status` 关于 **模型/身份验证/端点**，而不是使用情况。

## 模型选择 (`/model`)

`/model` 实现为指令。

示例：

```
/model
/model list
/model 3
/model openai/gpt-5.2
/model opus@anthropic:default
/model status
```

注释：

- `/model` 和 `/model list` 显示一个紧凑的编号选择器（型号系列 + 可用提供商）。
- `/model <#>` 从该选择器中进行选择（并在可能的情况下优先选择当前提供商）。
- `/model status` 显示详细视图，包括配置的提供商端点 (`baseUrl`) 和 API 模式 (`api`)（如果可用）。

## 调试覆盖

`/debug` 允许您设置 **仅运行时** 的配置覆盖（内存中，不是磁盘）。仅限所有者；默认情况下禁用；使用 `commands.debug: true` 启用。

示例：

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

注意：

- 覆盖会立即应用于新的配置读取，但不会写入 `openclaw.json`。
- 使用 `/debug reset` 清除所有覆盖并恢复到磁盘上的配置。

## 配置更新

`/config` 写入您的磁盘配置 (`openclaw.json`)。仅限所有者；默认情况下禁用；使用 `commands.config: true` 启用。

示例：

```
/config show
/config show messages.responsePrefix
/config get messages.responsePrefix
/config set messages.responsePrefix="[openclaw]"
/config unset messages.responsePrefix
```

注意：

- 在写入之前验证配置；无效的更改将被拒绝。
- `/config` 更新在重启之间持久化。

## 表面说明

- **文本命令** 在正常的聊天会话中运行（DM 共享 `main`，群组有自己的会话）。
- **原生命令** 使用隔离的会话：
  - Discord: `agent:<agentId>:discord:slash:<userId>`
  - Slack: `agent:<agentId>:slack:slash:<userId>`（前缀可通过 `channels.slack.slashCommand.sessionPrefix` 配置）
  - Telegram: `telegram:slash:<userId>`（通过 `CommandTargetSessionKey` 目标聊天会话）
- **`/stop`** 目标活动聊天会话以便可以中止当前运行。
- **Slack:** 仍然支持单个 `/openclaw` 样式的命令的 `channels.slack.slashCommand`。如果您启用 `commands.native`，必须为每个内置命令创建一个 Slack 斜杠命令（与 `/help` 中的名称相同）。Slack 的命令参数菜单以临时 Block Kit 按钮的形式提供。