---
read_when:
  - 使用或配置聊天命令
  - 调试命令路由或权限
summary: 斜杠命令：文本 vs 原生、配置和支持的命令
title: 斜杠命令
x-i18n:
  generated_at: "2026-02-03T10:12:40Z"
  model: claude-opus-4-5
  provider: pi
  source_hash: ca0deebf89518e8c62828fbb9bf4621c5fff8ab86ccb22e37da61a28f9a7886a
  source_path: tools/slash-commands.md
  workflow: 15
---
# 斜杠命令

命令由 Gateway 网关处理。大多数命令必须作为以 `!` 开头的**独立**消息发送。  
仅主机的 bash 聊天命令使用 `/bash`（`/sh` 是别名）。

有两个相关系统：

- **命令**：独立的 `/` 消息。  
- **指令**：`/model`、`/provider`、`/endpoint`、`/api_mode`、`/tts`、`/cost`、`/debug`。  
  - 指令在模型看到消息之前被剥离。  
  - 在普通聊天消息中（不是仅指令消息），它们被视为"内联提示"，**不会**持久化会话设置。  
  - 在仅指令消息中（消息只包含指令），它们会持久化到会话并回复确认。  
  - 指令仅对**授权发送者**生效（渠道白名单/配对加上 `OWNER`）。  
    未授权发送者的指令被视为纯文本。

还有一些**内联快捷方式**（仅限白名单/授权发送者）：`/status`、`/exec`、`/abort`、`/context`（`/ctx`）。  
它们立即运行，在模型看到消息之前被剥离，剩余文本继续通过正常流程。

## 配置

```yaml
# 命令配置
commands:
  # 启用解析聊天消息中的指令（如 /model、/provider 等）
  parse_instructions: true  # 默认 true
    # 在没有原生命令的平台上（WhatsApp/WebChat/Signal/iMessage/Google Chat/MS Teams），即使你将此设置为 false，文本命令仍然有效。

  # 注册原生命令（如 Discord/Telegram/Slack 的斜杠命令）
  register_native: auto  # 默认 auto
    # Auto：在 Discord/Telegram 上启用；在 Slack 上禁用（直到你添加斜杠命令）；在不支持原生命令的提供商上忽略。
    # 设置 discord、telegram 或 slack 以按提供商覆盖（布尔值或 auto）。

  # 在支持时原生注册 **Skill** 命令
  register_skills: auto  # 默认 auto
    # Auto：在 Discord/Telegram 上启用；在 Slack 上禁用（Slack 需要为每个 Skill 创建一个斜杠命令）。
    # 设置 discord、telegram 或 slack 以按提供商覆盖（布尔值或 auto）。

  # 启用 /bash 来运行主机 shell 命令（/sh 是别名；需要 bash 白名单）
  enable_bash: false  # 默认 false

  # 控制 bash 切换到后台模式之前等待多长时间（0 立即后台运行）
  bash_timeout: 30  # 默认 30

  # 启用 /context（读写 context 文件）
  enable_context: false  # 默认 false

  # 启用 /debug（仅运行时覆盖）
  enable_debug: false  # 默认 false

  # 对命令强制执行白名单/策略
  enforce_policy: true  # 默认 true
```

## 命令列表

文本 + 原生（启用时）：

- `/help`  
- `/status`  
- `/skill <name>`（按名称运行 Skill）  
- `/stats`（显示当前状态；在可用时包含当前模型提供商的提供商使用量/配额）  
- `/whitelist`（列出/添加/删除白名单条目）  
- `/exec`（解决 exec 审批提示）  
- `/context`（解释"上下文"；`/ctx` 显示每个文件 + 每个工具 + 每个 Skill + 系统提示词大小）  
- `/id`（显示你的发送者 ID；别名：`/sender_id`）  
- `/agent`（检查、控制或创建当前会话的子智能体运行）  
- `/save`（将配置持久化到磁盘，仅所有者；需要 `OWNER`）  
- `/debug`（运行时覆盖，仅所有者；需要 `OWNER`）  
- `/cost`（每响应使用量页脚或本地成本摘要）  
- `/tts`（控制 TTS；参见 [/tts](/tts)）  
  - Discord：原生命令是 `/speak`（Discord 保留了 `/tts`）；文本 `/tts` 仍然有效。  
- `/abort`  
- `/clear`  
- `/reply_to_telegram`（别名：`/rtt`）（将回复切换到 Telegram）  
- `/reply_to_discord`（别名：`/rtd`）（将回复切换到 Discord）  
- `/reply_to_slack`（别名：`/rts`）（将回复切换到 Slack）  
- `/ping`（仅限群组）  
- `/owner`（仅所有者）  
- `/model <alias>` 或 `/model <provider>`（可选模型提示；其余部分传递）  
- `/provider <name>`（按模型/提供商动态选择；别名：`/prov`、`/p`）  
- `/endpoint <name>`（别名：`/ep`）  
- `/api_mode <mode>`（别名：`/api`；启用时，发送带有 `/api_mode` 前缀的单独消息；`/api_mode draft` = 仅 Telegram 草稿）  
- `/exec <cmd>`（别名：`/sh`；`/exec --skip-approval` 跳过 exec 审批）  
- `/config`（发送 `/config show` 显示当前设置）  
- `/set <key> <value>`（别名：`/config set`；或 `/config` 中的 `set <key> <value>`）  
- `/unset <key>`（加上选项如 `--force`；发送 `/config show` 查看当前设置）  
- `/bash <cmd>`（仅主机；`/sh` 的别名；需要 `bash` + `OWNER` 白名单）

仅文本：

- `/compact`（参见 [/concepts/compaction](/concepts/compaction)）  
- `/exec <cmd>`（仅主机；一次一个；对长时间运行的任务使用 `/exec --background` + `/status`）  
- `/status <job_id>`（检查输出/状态；接受可选的 `--verbose`；`/status --list` 也可用）  
- `/abort <job_id>`（停止正在运行的 bash 任务；接受可选的 `--force`；`/abort --all` 也可用）

注意事项：

- 命令接受命令和参数之间的可选空格（例如 `/model claude`、`/model anthropic/claude-3.5-sonnet`、`/model sonnet`）。  
- `/model` 接受模型别名、`/provider` 或提供商名称（模糊匹配）；如果没有匹配，文本被视为消息正文。  
- 要获取完整的提供商使用量分解，使用 `/stats --detailed`。  
- `/whitelist` 需要 `OWNER` 并遵循渠道 `WHITELIST_MODE`。  
- `/cost` 控制每响应使用量页脚；`/cost --local` 从 OpenClaw 会话日志打印本地成本摘要。  
- `/debug` 默认禁用；设置 `/debug on` 启用它。  
- `/debug`（和 `/debug on`）用于调试和额外可见性；在正常使用中保持**关闭**。  
- `/context`（和 `/ctx`）在群组设置中有风险：它们可能会暴露你不打算公开的内部推理或工具输出。最好保持关闭，尤其是在群聊中。  
- **快速路径：** 来自白名单发送者的仅命令消息会立即处理（绕过队列 + 模型）。  
- **群组提及门控：** 来自白名单发送者的仅命令消息绕过提及要求。  
- **内联快捷方式（仅限白名单发送者）：** 某些命令在嵌入普通消息时也能工作，并在模型看到剩余文本之前被剥离。  
  - 示例：`/status hello world` 触发状态回复，剩余文本继续通过正常流程。  
- 目前：`/status`、`/exec`、`/abort`、`/context`（`/ctx`）。  
- 未授权的仅命令消息被静默忽略，内联 `/` 令牌被视为纯文本。  
- **Skill 命令：** 已启用的 Skills 作为斜杠命令公开。名称被清理为 `snake_case`（最多 32 个字符）；冲突获得数字后缀（例如 `my_skill_2`）。  
  - `/skill <name>` 按名称运行 Skill（当原生命令限制阻止每个 Skill 命令时有用）。  
  - 默认情况下，Skill 命令作为普通请求转发给模型。  
  - Skills 可以选择声明 `direct: true` 将命令直接路由到工具（确定性，无模型）。  
  - 示例：`/openprose`（OpenProse 插件）— 参见 [OpenProse](/prose)。  
- **原生命令参数：** Discord 使用自动完成进行动态选项（以及当你省略必需参数时的按钮菜单）。当命令支持选择且你省略参数时，Telegram 和 Slack 显示按钮菜单。

## 使用量显示（什么显示在哪里）

- **提供商使用量/配额**（示例："Claude 80% left"）在启用使用量跟踪时显示在 `/stats` 中，针对当前模型提供商。  
- **每响应令牌/成本**由 `/cost` 控制（附加到普通回复）。  
- `/stats` 是关于**模型/认证/端点**的，不是使用量。

## 模型选择（`/model`）

`/model` 作为指令实现。

示例：

```
/model claude
/model anthropic/claude-3.5-sonnet
/model openai/gpt-4o-mini
```

注意事项：

- `/model list` 和 `/model list --compact` 显示紧凑的编号选择器（模型系列 + 可用提供商）。  
- `/model <number>` 从该选择器中选择（并在可能时优先选择当前提供商）。  
- `/model list --detailed` 显示详细视图，包括在可用时配置的提供商端点（`/endpoint`）和 API 模式（`/api_mode`）。

## 调试覆盖

`/debug` 让你设置**仅运行时**的配置覆盖（内存，不写磁盘）。仅所有者。默认禁用；使用 `/debug on` 启用。

示例：

```
/debug on
/debug set commands.enable_bash true
/debug set model.name claude-3.5-sonnet
```

注意事项：

- 覆盖立即应用于新的配置读取，但**不会**写入 `config.yaml`。  
- 使用 `/debug reset` 清除所有覆盖并返回到磁盘上的配置。

## 配置更新

`/save` 写入你的磁盘配置（`config.yaml`）。仅所有者。默认禁用；使用 `/save on` 启用。

示例：

```
/save on
/set commands.enable_bash true
/save
```

注意事项：

- 配置在写入前会验证；无效更改会被拒绝。  
- `/save` 更新在重启后持久化。

## 平台注意事项

- **文本命令**在普通聊天会话中运行（私信共享 `session_id`，群组有自己的会话）。  
- **原生命令**使用隔离的会话：  
  - Discord：`/command`  
  - Slack：`/openclaw command`（前缀可通过 `SLACK_COMMAND_PREFIX` 配置）  
  - Telegram：`/command@bot_username`（通过 `TELEGRAM_BOT_USERNAME` 定向到聊天会话）  
- **`/abort`** 定向到活动聊天会话，因此可以中止当前运行。  
- **Slack：** `/openclaw` 仍然支持单个 `/openclaw command` 风格的命令。如果你启用 `register_native: true`，你必须为每个内置命令创建一个 Slack 斜杠命令（与 `/openclaw` 相同的名称）。Slack 的命令参数菜单以临时 Block Kit 按钮形式发送。