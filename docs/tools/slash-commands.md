---
summary: "Slash commands: text vs native, config, and supported commands"
read_when:
  - Using or configuring chat commands
  - Debugging command routing or permissions
title: "Slash Commands"
---
# 斜杠命令

命令由网关处理。大多数命令必须作为以`/`开头的**独立**消息发送。
仅主机的bash聊天命令使用`! <cmd>`（`/bash <cmd>`作为别名）。

有两个相关的系统：

- **命令**：独立的`/...`消息。
- **指令**：`/think`, `/verbose`, `/reasoning`, `/elevated`, `/exec`, `/model`, `/queue`。
  - 在模型看到消息之前，指令会被从消息中移除。
  - 在正常的聊天消息（非仅指令）中，它们被视为“内联提示”，并且**不会**持久化会话设置。
  - 在仅指令的消息（消息只包含指令）中，它们会持久化到会话，并回复确认信息。
  - 指令仅对**授权发送者**生效。如果设置了`commands.allowFrom`，则它是唯一使用的允许列表；否则授权来自频道允许列表/配对加上`commands.useAccessGroups`。
    未授权的发送者将把指令视为纯文本处理。

还有一些**内联快捷方式**（仅限列入白名单/授权的发送者）：`/help`, `/commands`, `/status`, `/whoami` (`/id`)。
它们立即运行，在模型看到消息前被移除，剩余文本继续通过正常流程处理。

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

- `commands.text` (默认`true`) 启用解析聊天消息中的`/...`。
  - 对于没有原生命令支持的平台（WhatsApp/WebChat/Signal/iMessage/Google Chat/MS Teams），即使你将其设置为`false`，文本命令仍然有效。
- `commands.native` (默认`"auto"`) 注册原生命令。
  - 自动：对于Discord/Telegram启用；对于Slack禁用（直到你添加斜杠命令）；对于不支持原生命令的服务提供商忽略此设置。
  - 设置`channels.discord.commands.native`, `channels.telegram.commands.native` 或 `channels.slack.commands.native` 来覆盖每个服务提供商的设置（布尔值或`"auto"`）。
  - `false` 在启动时清除Discord/Telegram上先前注册的命令。Slack命令在Slack应用中管理，不会自动删除。
- `commands.nativeSkills` (默认`"auto"`) 当支持时，注册**技能**命令。
  - 自动：对于Discord/Telegram启用；对于Slack禁用（Slack需要为每个技能创建一个斜杠命令）。
  - 设置`channels.discord.commands.nativeSkills`, `channels.telegram.commands.nativeSkills` 或 `channels.slack.commands.nativeSkills` 来覆盖每个服务提供商的设置（布尔值或`"auto"`）。
- `commands.bash` (默认`false`) 启用`! <cmd>` 运行主机shell命令（`/bash <cmd>` 是别名；需要`tools.elevated` 允许列表）。
- `commands.bashForegroundMs` (默认`2000`) 控制bash等待多久后切换到后台模式（`0` 立即切换到后台）。
- `commands.config` (默认`false`) 启用`/config` (读写`openclaw.json`)。
- `commands.debug` (默认`false`) 启用`/debug` (仅运行时覆盖)。
- `commands.allowFrom` (可选) 为每个服务提供商设置命令授权的允许列表。配置后，这是
  命令和指令的唯一授权来源（频道允许列表/配对和`commands.useAccessGroups`
  被忽略）。使用`"*"` 作为全局默认值；特定于提供者的键会覆盖它。
- `commands.useAccessGroups` (默认`true`) 当未设置`commands.allowFrom` 时，强制执行命令的允许列表/策略。

## 命令列表

文本 + 原生（当启用时）：

- `/help`
- `/commands`
- `/skill <name> [input]` (按名称运行技能)
- `/status` (显示当前状态；包括可用/配额信息，当当前模型提供商支持时)
- `/allowlist` (列出/添加/移除允许列表条目)
- `/approve <id> allow-once|allow-always|deny` (解决执行批准提示)
- `/context [list|detail|json]` (解释“上下文”；`detail` 显示每文件+每工具+每技能+系统提示大小)
- `/export-session [path]` (别名: `/export`) (导出当前会话至HTML，含完整系统提示)
- `/whoami` (显示你的发送者ID；别名: `/id`)
- `/session idle <duration|off>` (管理聚焦线程绑定的非活动自动取消聚焦)
- `/session max-age <duration|off>` (管理聚焦线程绑定的硬最大年龄自动取消聚焦)
- `/subagents list|kill|log|info|send|steer|spawn` (检查、控制或生成当前会话的子代理运行)
- `/acp spawn|cancel|steer|close|status|set-mode|set|cwd|permissions|timeout|model|reset-options|doctor|install|sessions` (检查和控制ACP运行时会话)
- `/agents` (列出此会话的线程绑定代理)
- `/focus <target>` (Discord: 绑定此线程或新线程到会话/子代理目标)
- `/unfocus` (Discord: 移除当前线程绑定)
- `/kill <id|#|all>` (立即中止此会话的一个或所有正在运行的子代理；无确认消息)
- `/steer <id|#> <message>` (立即转向正在运行的子代理：可能时在运行中转向，否则中止当前工作并在转向消息上重新开始)
- `/tell <id|#> <message>` (别名为 `/steer`)
- `/config show|get|set|unset` (将配置持久化到磁盘，仅所有者；需要`commands.config: true`)
- `/debug show|set|unset|reset` (运行时覆盖，仅所有者；需要`commands.debug: true`)
- `/usage off|tokens|full|cost` (每次响应后的使用情况页脚或本地成本摘要)
- `/tts off|always|inbound|tagged|status|provider|limit|summary|audio` (控制TTS；参见 [/tts](/tts))
  - Discord: 原生命令是`/voice` (Discord保留了`/tts`); 文本`/tts` 仍然有效。
- `/stop`
- `/restart`
- `/dock-telegram` (别名: `/dock_telegram`) (切换回复到Telegram)
- `/dock-discord` (别名: `/dock_discord`) (切换回复到Discord)
- `/dock-slack` (别名: `/dock_slack`) (切换回复到Slack)
- `/activation mention|always` (仅群组)
- `/send on|off|inherit` (仅所有者)
- `/reset` 或 `/new [model]` (可选模型提示；其余部分传递)
- `/think <off|minimal|low|medium|high|xhigh>` (动态选择模型/提供商；别名: `/thinking`, `/t`)
- `/verbose on|full|off` (别名: `/v`)
- `/reasoning on|off|stream` (别名: `/reason`; 开启时，发送一条单独的消息并以前缀`Reasoning:`; `stream` = 仅Telegram草稿)
- `/elevated on|off|ask|full` (别名: `/elev`; `full` 跳过执行批准)
- `/exec host=<sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>` (发送`/exec` 显示当前)
- `/model <name>` (别名: `/models`; 或从`agents.defaults.models.*.alias` 发送`/<alias>`)
- `/queue <mode>` (加上选项如`debounce:2s cap:25 drop:summarize`; 发送`/queue` 查看当前设置)
- `/bash <command>` (仅主机; 别名: `! <command>`; 需要`commands.bash: true` + `tools.elevated` 允许列表)

仅文本：

- `/compact [instructions]` (参见 [/concepts/compaction](/concepts/compaction))
- `! <command>` (仅主机; 一次一个; 使用`!poll` + `!stop` 处理长时间运行的任务)
- `!poll` (检查输出/状态; 接受可选的`sessionId`; `/bash poll` 也有效)
- `!stop` (停止正在运行的bash作业; 接受可选的`sessionId`; `/bash stop` 也有效)

注释：

- 命令接受命令和参数之间的一个可选的`:`（例如 `/think: high`, `/send: on`, `/help:`）。
- `/new <model>` 接受模型别名、`provider/model` 或提供者名称（模糊匹配）；如果没有匹配项，文本将被视为消息正文。
- 要获取完整的提供者使用情况细分，请使用 `openclaw status --usage`。
- `/allowlist add|remove` 需要 `commands.config=true` 并尊重频道 `configWrites`。
- `/usage` 控制每个响应的使用情况页脚；`/usage cost` 从 OpenClaw 会话日志中打印本地成本摘要。
- 默认启用 `/restart`；设置 `commands.restart: false` 以禁用它。
- 仅限 Discord 的原生命令：`/vc join|leave|status` 控制语音频道（需要 `channels.discord.voice` 和原生命令；不可作为文本使用）。
- Discord 线程绑定命令（`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`）需要启用有效的线程绑定（`session.threadBindings.enabled` 和/或 `channels.discord.threadBindings.enabled`）。
- ACP 命令参考和运行时行为：[ACP Agents](/tools/acp-agents)。
- `/verbose` 用于调试和额外可见性；在正常使用中保持关闭状态。
- 当相关时，工具失败摘要仍然显示，但详细的失败文本仅在 `/verbose` 是 `on` 或 `full` 时包含。
- 在群组设置中，`/reasoning`（和 `/verbose`）是有风险的：它们可能会揭示您不打算公开的内部推理或工具输出。最好关闭它们，尤其是在群聊中。
- **快速路径**：来自允许列表发送者的仅命令消息立即处理（绕过队列 + 模型）。
- **群组提及门控**：来自允许列表发送者的仅命令消息绕过提及要求。
- **内联快捷方式（仅限允许列表发送者）**：某些命令也可以嵌入到普通消息中，并在模型看到剩余文本之前被剥离。
  - 示例：`hey /status` 触发状态回复，剩余文本继续通过正常流程。
- 目前：`/help`, `/commands`, `/status`, `/whoami` (`/id`)。
- 未经授权的仅命令消息将被静默忽略，内联 `/...` 令牌被视为纯文本。
- **技能命令**：`user-invocable` 技能作为斜杠命令暴露。名称被清理为 `a-z0-9_`（最多 32 个字符）；冲突时添加数字后缀（例如 `_2`）。
  - `/skill <name> [input]` 通过名称运行技能（当原生命令限制阻止每个技能命令时有用）。
  - 默认情况下，技能命令作为正常请求转发给模型。
  - 技能可以选择声明 `command-dispatch: tool` 以直接将命令路由到工具（确定性，无模型）。
  - 示例：`/prose`（OpenProse 插件）— 请参阅 [OpenProse](/prose)。
- **原生命令参数**：Discord 使用自动完成功能进行动态选项（并在省略必需参数时使用按钮菜单）。Telegram 和 Slack 在命令支持选择且省略参数时显示按钮菜单。

## 使用界面（什么在哪里显示）

- **提供者使用/配额**（例如：“Claude 80% left”）在启用使用跟踪时显示当前模型提供者的 `/status` 中。
- **每个响应的令牌/成本** 由 `/usage off|tokens|full` 控制（附加到正常回复中）。
- `/model status` 关于 **模型/认证/端点**，而不是使用情况。

## 模型选择（`/model`）

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

注意事项：

- `/model` 和 `/model list` 显示一个紧凑的编号选择器（模型系列 + 可用提供者）。
- 在 Discord 上，`/model` 和 `/models` 打开一个带有提供者和模型下拉菜单以及提交步骤的交互式选择器。
- `/model <#>` 从该选择器中选择（并尽可能优先选择当前提供者）。
- `/model status` 显示详细视图，包括配置的提供者端点（`baseUrl`）和 API 模式（`api`），如果可用的话。

## 调试覆盖

`/debug` 允许您设置 **仅运行时** 的配置覆盖（内存，非磁盘）。仅所有者可以使用。默认禁用；启用 `commands.debug: true`。

示例：

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

注意事项：

- 覆盖立即应用于新的配置读取，但 **不会** 写入 `openclaw.json`。
- 使用 `/debug reset` 清除所有覆盖并返回到磁盘上的配置。

## 配置更新

`/config` 写入您的磁盘上的配置（`openclaw.json`）。仅所有者可以使用。默认禁用；启用 `commands.config: true`。

示例：

```
/config show
/config show messages.responsePrefix
/config get messages.responsePrefix
/config set messages.responsePrefix="[openclaw]"
/config unset messages.responsePrefix
```

注意事项：

- 在写入之前验证配置；无效的更改将被拒绝。
- `/config` 更新在重启后仍然有效。

## 界面说明

- **文本命令** 在正常的聊天会话中运行（私信共享 `main`，群组有自己的会话）。
- **原生命令** 使用隔离会话：
  - Discord: `agent:<agentId>:discord:slash:<userId>`
  - Slack: `agent:<agentId>:slack:slash:<userId>`（通过 `channels.slack.slashCommand.sessionPrefix` 可配置前缀）
  - Telegram: `telegram:slash:<userId>`（通过 `CommandTargetSessionKey` 面向聊天会话）
- **`/stop`** 面向活动的聊天会话，因此它可以中止当前运行。
- **Slack**：`channels.slack.slashCommand` 仍然支持单个 `/openclaw` 样式的命令。如果您启用了 `commands.native`，则必须为每个内置命令创建一个 Slack 斜杠命令（与 `/help` 同名）。Slack 命令参数菜单以临时 Block Kit 按钮形式传递。
  - Slack 原生例外：注册 `/agentstatus`（不是 `/status`），因为 Slack 预留了 `/status`。文本 `/status` 仍然可以在 Slack 消息中工作。