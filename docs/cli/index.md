---
summary: "OpenClaw CLI reference for `openclaw` commands, subcommands, and options"
read_when:
  - Adding or modifying CLI commands or options
  - Documenting new command surfaces
title: "CLI Reference"
---
# CLI 参考

本页描述了当前的CLI行为。如果命令发生变化，请更新此文档。

## 命令页面

- [`setup`](/cli/setup)
- [`onboard`](/cli/onboard)
- [`configure`](/cli/configure)
- [`config`](/cli/config)
- [`doctor`](/cli/doctor)
- [`dashboard`](/cli/dashboard)
- [`reset`](/cli/reset)
- [`uninstall`](/cli/uninstall)
- [`update`](/cli/update)
- [`message`](/cli/message)
- [`agent`](/cli/agent)
- [`agents`](/cli/agents)
- [`acp`](/cli/acp)
- [`status`](/cli/status)
- [`health`](/cli/health)
- [`sessions`](/cli/sessions)
- [`gateway`](/cli/gateway)
- [`logs`](/cli/logs)
- [`system`](/cli/system)
- [`models`](/cli/models)
- [`memory`](/cli/memory)
- [`nodes`](/cli/nodes)
- [`devices`](/cli/devices)
- [`node`](/cli/node)
- [`approvals`](/cli/approvals)
- [`sandbox`](/cli/sandbox)
- [`tui`](/cli/tui)
- [`browser`](/cli/browser)
- [`cron`](/cli/cron)
- [`dns`](/cli/dns)
- [`docs`](/cli/docs)
- [`hooks`](/cli/hooks)
- [`webhooks`](/cli/webhooks)
- [`pairing`](/cli/pairing)
- [`plugins`](/cli/plugins) (插件命令)
- [`channels`](/cli/channels)
- [`security`](/cli/security)
- [`skills`](/cli/skills)
- [`voicecall`](/cli/voicecall) (插件；如已安装)

## 全局标志

- `--dev`: 在 `~/.openclaw-dev` 下隔离状态并移默认端口。
- `--profile <name>`: 在 `~/.openclaw-<name>` 下隔离状态。
- `--no-color`: 禁用 ANSI 颜色。
- `--update`: `openclaw update` 的简写形式（仅适用于源码安装）。
- `-V`, `--version`, `-v`: 打印版本并退出。

## 输出样式

- ANSI 颜色和进度指示器仅在 TTY 会话中渲染。
- 支持的终端中，OSC-8 超链接会渲染为可点击链接；否则我们回退到纯 URL。
- `--json`（以及支持的 `--plain`）禁用样式以获得干净的输出。
- `--no-color` 禁用 ANSI 样式；也尊重 `NO_COLOR=1`。
- 长时间运行的命令会显示进度指示器（当支持时使用 OSC 9;4）。

## 颜色调色板

OpenClaw 使用龙虾调色板用于 CLI 输出。

- `accent` (#FF5A2D): 标题、标签、主要高亮。
- `accentBright` (#FF7A3D): 命令名称、强调。
- `accentDim` (#D14A22): 次要高亮文本。
- `info` (#FF8A5B): 信息值。
- `success` (#2FBF71): 成功状态。
- `warn` (#FFB020): 警告、回退、注意。
- `error` (#E23D2D): 错误、失败。
- `muted` (#8B7F77): 减弱强调、元数据。

调色板真实来源: `src/terminal/palette.ts`（即“lobster seam”）。

## 命令树

```
openclaw [--dev] [--profile <name>] <command>
  setup
  onboard
  configure
  config
    get
    set
    unset
  doctor
  security
    audit
  reset
  uninstall
  update
  channels
    list
    status
    logs
    add
    remove
    login
    logout
  skills
    list
    info
    check
  plugins
    list
    info
    install
    enable
    disable
    doctor
  memory
    status
    index
    search
  message
  agent
  agents
    list
    add
    delete
  acp
  status
  health
  sessions
  gateway
    call
    health
    status
    probe
    discover
    install
    uninstall
    start
    stop
    restart
    run
  logs
  system
    event
    heartbeat last|enable|disable
    presence
  models
    list
    status
    set
    set-image
    aliases list|add|remove
    fallbacks list|add|remove|clear
    image-fallbacks list|add|remove|clear
    scan
    auth add|setup-token|paste-token
    auth order get|set|clear
  sandbox
    list
    recreate
    explain
  cron
    status
    list
    add
    edit
    rm
    enable
    disable
    runs
    run
  nodes
  devices
  node
    run
    status
    install
    uninstall
    start
    stop
    restart
  approvals
    get
    set
    allowlist add|remove
  browser
    status
    start
    stop
    reset-profile
    tabs
    open
    focus
    close
    profiles
    create-profile
    delete-profile
    screenshot
    snapshot
    navigate
    resize
    click
    type
    press
    hover
    drag
    select
    upload
    fill
    dialog
    wait
    evaluate
    console
    pdf
  hooks
    list
    info
    check
    enable
    disable
    install
    update
  webhooks
    gmail setup|run
  pairing
    list
    approve
  docs
  dns
    setup
  tui
```

注意：插件可以添加额外的顶级命令（例如 `openclaw voicecall`）。

## 安全性

- `openclaw security audit` — 审计配置 + 本地状态以查找常见的安全陷阱。
- `openclaw security audit --deep` — 最佳努力实时网关探测。
- `openclaw security audit --fix` — 加紧安全默认设置并更改状态/配置权限。

## 插件

管理扩展及其配置：

- `openclaw plugins list` — 发现插件（使用 `--json` 获取机器输出）。
- `openclaw plugins info <id>` — 显示插件详细信息。
- `openclaw plugins install <path|.tgz|npm-spec>` — 安装插件（或向 `plugins.load.paths` 添加插件路径）。
- `openclaw plugins enable <id>` / `disable <id>` — 切换 `plugins.entries.<id>.enabled`。
- `openclaw plugins doctor` — 报告插件加载错误。

大多数插件更改需要网关重启。参见 [/plugin](/plugin)。

## 内存

对 `MEMORY.md` + `memory/*.md` 进行向量搜索：

- `openclaw memory status` — 显示索引统计信息。
- `openclaw memory index` — 重新索引内存文件。
- `openclaw memory search "<query>"` — 对内存进行语义搜索。

## 聊天斜杠命令

聊天消息支持 `/...` 命令（文本和原生）。参见 [/tools/slash-commands](/tools/slash-commands)。

亮点：

- `/status` 用于快速诊断。
- `/config` 用于持久化配置更改。
- `/debug` 用于仅运行时配置覆盖（内存，非磁盘；需要 `commands.debug: true`）。

## 设置 + 入门

### `setup`

初始化配置 + 工作区。

选项：

- `--workspace <dir>`: 代理工作区路径（默认 `~/.openclaw/workspace`）。
- `--wizard`: 运行入门向导。
- `--non-interactive`: 无提示运行向导。
- `--mode <local|remote>`: 向导模式。
- `--remote-url <url>`: 远程网关 URL。
- `--remote-token <token>`: 远程网关令牌。

当存在任何向导标志时，向导会自动运行（`--non-interactive`, `--mode`, `--remote-url`, `--remote-token`）。

### `onboard`

交互式向导以设置网关、工作区和技能。

选项：

- `--workspace <dir>`
- `--reset`（重置配置 + 凭证 + 会话 + 工作区前运行向导）
- `--non-interactive`
- `--mode <local|remote>`
- `--flow <quickstart|advanced|manual>`（手动是高级的别名）
- `--auth-choice <setup-token|token|chutes|openai-codex|openai-api-key|openrouter-api-key|ai-gateway-api-key|moonshot-api-key|kimi-code-api-key|synthetic-api-key|venice-api-key|gemini-api-key|zai-api-key|apiKey|minimax-api|minimax-api-lightning|opencode-zen|skip>`
- `--token-provider <id>`（非交互式；与 `--auth-choice token` 结合使用）
- `--token <token>`（非交互式；与 `--auth-choice token` 结合使用）
- `--token-profile-id <id>`（非交互式；默认：`<provider>:manual`）
- `--token-expires-in <duration>`（非交互式；例如 `365d`, `12h`）
- `--anthropic-api-key <key>`
- `--openai-api-key <key>`
- `--openrouter-api-key <key>`
- `--ai-gateway-api-key <key>`
- `--moonshot-api-key <key>`
- `--kimi-code-api-key <key>`
- `--gemini-api-key <key>`
- `--zai-api-key <key>`
- `--minimax-api-key <key>`
- `--opencode-zen-api-key <key>`
- `--gateway-port <port>`
- `--gateway-bind <loopback|lan|tailnet|auto|custom>`
- `--gateway-auth <token|password>`
- `--gateway-token <token>`
- `--gateway-password <password>`
- `--remote-url <url>`
- `--remote-token <token>`
- `--tailscale <off|serve|funnel>`
- `--tailscale-reset-on-exit`
- `--install-daemon`
- `--no-install-daemon`（别名：`--skip-daemon`）
- `--daemon-runtime <node|bun>`
- `--skip-channels`
- `--skip-skills`
- `--skip-health`
- `--skip-ui`
- `--node-manager <npm|pnpm|bun>`（推荐使用 pnpm；不建议在网关运行时使用 bun）
- `--json`

### `configure`

交互式配置向导（模型、通道、技能、网关）。

### `config`

非交互式配置助手（获取/设置/取消设置）。运行 `openclaw config` 且没有子命令时启动向导。

子命令：

- `config get <path>`: 打印配置值（点/括号路径）。
- `config set <path> <value>`: 设置值（JSON5 或原始字符串）。
- `config unset <path>`: 移除值。

### `doctor`

健康检查 + 快速修复（配置 + 网关 + 旧版服务）。

选项：

- `--no-workspace-suggestions`: 禁用工作区内存提示。
- `--yes`: 接受默认值而不提示（无头模式）。
- `--non-interactive`: 跳过提示；仅应用安全迁移。
- `--deep`: 扫描系统服务以查找额外的网关安装。

## 通道助手

### `channels`

管理聊天通道账户（WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (插件)/Signal/iMessage/MS Teams）。

子命令：

- `channels list`: 显示配置的通道和认证配置文件。
- `channels status`: 检查网关可达性和通道健康状况（`--probe` 运行额外检查；使用 `openclaw health` 或 `openclaw status --deep` 进行网关健康探测）。
- 提示：`channels status` 在检测到常见错误配置时打印警告并提供修复建议（然后指向 `openclaw doctor`）。
- `channels logs`: 显示来自网关日志文件的最近通道日志。
- `channels add`: 无标志传递时采用向导风格设置；标志切换到非交互模式。
- `channels remove`: 默认禁用；传递 `--delete` 以无提示删除配置条目。
- `channels login`: 交互式通道登录（仅限 WhatsApp Web）。
- `channels logout`: 登出通道会话（如果支持）。

常用选项：

- `--channel <name>`: `whatsapp|telegram|discord|googlechat|slack|mattermost|signal|imessage|msteams`
- `--account <id>`: 通道账户 ID（默认 `default`）
- `--name <label>`: 账户的显示名称

`channels login` 选项：

- `--channel <channel>`（默认 `whatsapp`；支持 `whatsapp`/`web`）
- `--account <id>`
- `--verbose`

`channels logout` 选项：

- `--channel <channel>`（默认 `whatsapp`）
- `--account <id>`

`channels list` 选项：

- `--no-usage`: 跳过模型提供商使用/配额快照（仅限 OAuth/API 支持）。
- `--json`: 输出 JSON（除非设置了 `--no-usage`，否则包括使用情况）。

`channels logs` 选项：

- `--channel <name|all>`（默认 `all`）
- `--lines <n>`（默认 `200`）
- `--json`

更多详情：[/concepts/oauth](/concepts/oauth)

示例：

```bash
openclaw channels add --channel telegram --account alerts --name "Alerts Bot" --token $TELEGRAM_BOT_TOKEN
openclaw channels add --channel discord --account work --name "Work Bot" --token $DISCORD_BOT_TOKEN
openclaw channels remove --channel discord --account work --delete
openclaw channels status --probe
openclaw status --deep
```

### `skills`

列出并检查可用技能及其就绪信息。

子命令：

- `skills list`: 列出技能（无子命令时默认）。
- `skills info <name>`: 显示单个技能的详细信息。
- `skills check`: 就绪与缺失要求的摘要。

选项：

- `--eligible`: 仅显示就绪的技能。
- `--json`: 输出 JSON（无样式）。
- `-v`, `--verbose`: 包含缺失要求的详细信息。

提示：使用 `npx clawhub` 来搜索、安装和同步技能。

### `pairing`

跨通道批准 DM 配对请求。

子命令：

- `pairing list <channel> [--json]`
- `pairing approve <channel> <code> [--notify]`

### `webhooks gmail`

Gmail Pub/Sub 钩子设置 + 运行器。参见 [/automation/gmail-pubsub](/automation/gmail-pubsub)。

子命令：

- `webhooks gmail setup`（需要 `--account <email>`；支持 `--project`, `--topic`, `--subscription`, `--label`, `--hook-url`, `--hook-token`, `--push-token`, `--bind`, `--port`, `--path`, `--include-body`, `--max-bytes`, `--renew-minutes`, `--tailscale`, `--tailscale-path`, `--tailscale-target`, `--push-endpoint`, `--json`）
- `webhooks gmail run`（相同标志的运行时覆盖）

### `dns setup`

广域发现 DNS 辅助工具（CoreDNS + Tailscale）。参见 [/gateway/discovery](/gateway/discovery)。

选项：

- `--apply`: 安装/更新 CoreDNS 配置（需要 sudo；仅限 macOS）。

## 消息 + 代理

### `message`

统一的外发消息 + 通道操作。

参见：[/cli/message](/cli/message)

子命令：

- `message send|poll|react|reactions|read|edit|delete|pin|unpin|pins|permissions|search|timeout|kick|ban`
- `message thread <create|list|reply>`
- `message emoji <list|upload>`
- `message sticker <send|upload>`
- `message role <info|add|remove>`
- `message channel <info|list>`
- `message member info`
- `message voice status`
- `message event <list|create>`

示例：

- `openclaw message send --target +15555550123 --message "Hi"`
- `openclaw message poll --channel discord --target channel:123 --poll-question "Snack?" --poll-option Pizza --poll-option Sushi`

### `agent`

通过网关（或嵌入式 `--local`）运行一个代理回合。

必需：

- `--message <text>`

选项：

- `--to <dest>`（用于会话密钥和可选交付）
- `--session-id <id>`
- `--thinking <off|minimal|low|medium|high|xhigh>`（仅限 GPT-5.2 + Codex 模型）
- `--verbose <on|full|off>`
- `--channel <whatsapp|telegram|discord|slack|mattermost|signal|imessage|msteams>`
- `--local`
- `--deliver`
- `--json`
- `--timeout <seconds>`

### `agents`

管理隔离代理（工作区 + 认证 + 路由）。

#### `agents list`

列出配置的代理。

选项：

- `--json`
- `--bindings`

#### `agents add [name]`

添加新的隔离代理。除非传递标志（或 `--non-interactive`），否则运行引导向导；在非交互模式下需要 `--workspace`。

选项：

- `--workspace <dir>`
- `--model <id>`
- `--agent-dir <dir>`
- `--bind <channel[:accountId]>`（可重复）
- `--non-interactive`
- `--json`

绑定规范使用 __CODE