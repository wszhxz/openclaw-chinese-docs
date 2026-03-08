---
summary: "OpenClaw CLI reference for `openclaw` commands, subcommands, and options"
read_when:
  - Adding or modifying CLI commands or options
  - Documenting new command surfaces
title: "CLI Reference"
---
# CLI 参考

本页描述了当前的 CLI 行为。如果命令发生变化，请更新本文档。

## 命令页面

- [`setup`](/cli/setup)
- [`onboard`](/cli/onboard)
- [`configure`](/cli/configure)
- [`config`](/cli/config)
- [`completion`](/cli/completion)
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
- [`directory`](/cli/directory)
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
- [`qr`](/cli/qr)
- [`plugins`](/cli/plugins) (插件命令)
- [`channels`](/cli/channels)
- [`security`](/cli/security)
- [`secrets`](/cli/secrets)
- [`skills`](/cli/skills)
- [`daemon`](/cli/daemon) (网关服务命令的旧版别名)
- [`clawbot`](/cli/clawbot) (旧版别名命名空间)
- [`voicecall`](/cli/voicecall) (插件；如已安装)

## 全局标志

- `--dev`：在 `~/.openclaw-dev` 下隔离状态并更改默认端口。
- `--profile <name>`：在 `~/.openclaw-<name>` 下隔离状态。
- `--no-color`：禁用 ANSI 颜色。
- `--update`：`openclaw update` 的缩写（仅限源码安装）。
- `-V`、`--version`、`-v`：打印版本并退出。

## 输出样式

- ANSI 颜色和进度指示器仅在 TTY 会话中渲染。
- OSC-8 超链接在支持的终端中显示为可点击链接；否则回退为普通 URL。
- `--json`（以及在支持的情况下 `--plain`）禁用样式以获取干净的输出。
- `--no-color` 禁用 ANSI 样式；`NO_COLOR=1` 同样有效。
- 长时间运行的命令会显示进度指示器（支持时为 OSC 9;4）。

## 颜色调色板

OpenClaw 为 CLI 输出使用龙虾调色板。

- `accent` (#FF5A2D): 标题、标签、主要高亮。
- `accentBright` (#FF7A3D): 命令名称、强调。
- `accentDim` (#D14A22): 次要高亮文本。
- `info` (#FF8A5B): 信息值。
- `success` (#2FBF71): 成功状态。
- `warn` (#FFB020): 警告、回退、注意。
- `error` (#E23D2D): 错误、失败。
- `muted` (#8B7F77): 弱化、元数据。

调色板权威来源：`src/terminal/palette.ts`（又名“龙虾接缝”）。

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
  completion
  doctor
  dashboard
  security
    audit
  secrets
    reload
    migrate
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
  directory
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
  daemon
    status
    install
    uninstall
    start
    stop
    restart
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
  qr
  clawbot
    qr
  docs
  dns
    setup
  tui
```

注意：插件可以添加额外的顶级命令（例如 `openclaw voicecall`）。

## 安全

- `openclaw security audit` — 审计配置和本地状态以查找常见的安全陷阱。
- `openclaw security audit --deep` — 尽力而为的实时网关探测。
- `openclaw security audit --fix` — 收紧安全默认值并 chmod 状态/配置。

## 密钥

- `openclaw secrets reload` — 重新解析引用并原子交换运行时快照。
- `openclaw secrets audit` — 扫描明文残留、未解析引用和优先级漂移。
- `openclaw secrets configure` — 用于提供者设置 + SecretRef 映射 + 预检/应用的交互式助手。
- `openclaw secrets apply --from <plan.json>` — 应用先前生成的计划（支持 `--dry-run`）。

## 插件

管理扩展及其配置：

- `openclaw plugins list` — 发现插件（机器输出请使用 `--json`）。
- `openclaw plugins info <id>` — 显示插件详情。
- `openclaw plugins install <path|.tgz|npm-spec>` — 安装插件（或将插件路径添加到 `plugins.load.paths`）。
- `openclaw plugins enable <id>` / `disable <id>` — 切换 `plugins.entries.<id>.enabled`。
- `openclaw plugins doctor` — 报告插件加载错误。

大多数插件更改需要重启网关。参见 [/plugin](/tools/plugin)。

## 记忆

在 `MEMORY.md` + `memory/*.md` 上进行向量搜索：

- `openclaw memory status` — 显示索引统计信息。
- `openclaw memory index` — 重新索引记忆文件。
- `openclaw memory search "<query>"`（或 `--query "<query>"`）— 对记忆进行语义搜索。

## 聊天斜杠命令

聊天消息支持 `/...` 命令（文本和本地）。参见 [/tools/slash-commands](/tools/slash-commands)。

亮点：

- `/status` 用于快速诊断。
- `/config` 用于持久化配置更改。
- `/debug` 用于仅运行时配置覆盖（记忆，非磁盘；需要 `commands.debug: true`）。

## 设置 + 入门

### `setup`

初始化配置和工作区。

选项：

- `--workspace <dir>`：代理工作区路径（默认 `~/.openclaw/workspace`）。
- `--wizard`：运行入门向导。
- `--non-interactive`：无提示运行向导。
- `--mode <local|remote>`：向导模式。
- `--remote-url <url>`：远程 Gateway URL。
- `--remote-token <token>`：远程 Gateway 令牌。

当存在任何向导标志时，向导自动运行（`--non-interactive`、`--mode`、`--remote-url`、`--remote-token`）。

### `onboard`

交互式向导，用于设置网关、工作区和技能。

选项：

- `--workspace <dir>`
- `--reset`（在向导之前重置配置 + 凭据 + 会话）
- `--reset-scope <config|config+creds+sessions|full>`（默认 `config+creds+sessions`；使用 `full` 也可移除工作区）
- `--non-interactive`
- `--mode <local|remote>`
- `--flow <quickstart|advanced|manual>`（manual 是 advanced 的别名）
- `--auth-choice <setup-token|token|chutes|openai-codex|openai-api-key|openrouter-api-key|ai-gateway-api-key|moonshot-api-key|moonshot-api-key-cn|kimi-code-api-key|synthetic-api-key|venice-api-key|gemini-api-key|zai-api-key|mistral-api-key|apiKey|minimax-api|minimax-api-lightning|opencode-zen|custom-api-key|skip>`
- `--token-provider <id>`（非交互；与 `--auth-choice token` 配合使用）
- `--token <token>`（非交互；与 `--auth-choice token` 配合使用）
- `--token-profile-id <id>`（非交互；默认：`<provider>:manual`）
- `--token-expires-in <duration>`（非交互；例如 `365d`、`12h`）
- `--secret-input-mode <plaintext|ref>`（默认 `plaintext`；使用 `ref` 存储提供者默认环境引用而非明文密钥）
- `--anthropic-api-key <key>`
- `--openai-api-key <key>`
- `--mistral-api-key <key>`
- `--openrouter-api-key <key>`
- `--ai-gateway-api-key <key>`
- `--moonshot-api-key <key>`
- `--kimi-code-api-key <key>`
- `--gemini-api-key <key>`
- `--zai-api-key <key>`
- `--minimax-api-key <key>`
- `--opencode-zen-api-key <key>`
- `--custom-base-url <url>`（非交互；与 `--auth-choice custom-api-key` 配合使用）
- `--custom-model-id <id>`（非交互；与 `--auth-choice custom-api-key` 配合使用）
- `--custom-api-key <key>`（非交互；可选；与 `--auth-choice custom-api-key` 配合使用；省略时回退到 `CUSTOM_API_KEY`）
- `--custom-provider-id <id>`（非交互；可选自定义提供者 ID）
- `--custom-compatibility <openai|anthropic>`（非交互；可选；默认 `openai`）
- `--gateway-port <port>`
- `--gateway-bind <loopback|lan|tailnet|auto|custom>`
- `--gateway-auth <token|password>`
- `--gateway-token <token>`
- `--gateway-token-ref-env <name>`（非交互；将 `gateway.auth.token` 存储为环境变量 SecretRef；需要设置该环境变量；不能与 `--gateway-token` 组合）
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
- `--node-manager <npm|pnpm|bun>`（推荐 pnpm；Gateway 运行时不推荐 bun）
- `--json`

### `configure`

交互式配置向导（模型、频道、技能、网关）。

### `config`

非交互式配置助手（get/set/unset/file/validate）。不带子命令运行 `openclaw config` 将启动向导。

子命令：

- `config get <path>`: 打印配置值（点号/方括号路径）。
- `config set <path> <value>`: 设置值（JSON5 或原始字符串）。
- `config unset <path>`: 移除值。
- `config file`: 打印当前活动配置文件路径。
- `config validate`: 在不启动网关的情况下验证当前配置是否符合模式。
- `config validate --json`: 输出机器可读的 JSON。

### `doctor`

健康检查 + 快速修复（配置 + 网关 + 遗留服务）。

选项：

- `--no-workspace-suggestions`: 禁用工作区内存提示。
- `--yes`: 接受默认值而不提示（无头模式）。
- `--non-interactive`: 跳过提示；仅应用安全迁移。
- `--deep`: 扫描系统服务以查找额外的网关安装。

## 频道助手

### `channels`

管理聊天频道账户（WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (插件)/Signal/iMessage/MS Teams）。

子命令：

- `channels list`: 显示配置的频道和认证配置文件。
- `channels status`: 检查网关可达性和频道健康状态（`--probe` 运行额外检查；使用 `openclaw health` 或 `openclaw status --deep` 进行网关健康探测）。
- 提示：当 `channels status` 能检测到常见配置错误时，会打印带有建议修复方案的警告（然后指引您前往 `openclaw doctor`）。
- `channels logs`: 显示网关日志文件中的最近频道日志。
- `channels add`: 未传递标志时使用向导式设置；传递标志则切换为非交互模式。
  - 当向仍使用单账户顶层配置的频道添加非默认账户时，OpenClaw 在写入新账户前将账户范围的值移动到 `channels.<channel>.accounts.default`。
  - 非交互式 `channels add` 不会自动创建/升级绑定；仅频道的绑定继续匹配默认账户。
- `channels remove`: 默认禁用；传递 `--delete` 可在不提示的情况下移除配置项。
- `channels login`: 交互式频道登录（仅限 WhatsApp Web）。
- `channels logout`: 退出频道会话（如果支持）。

通用选项：

- `--channel <name>`: `whatsapp|telegram|discord|googlechat|slack|mattermost|signal|imessage|msteams`
- `--account <id>`: 频道账户 ID（默认 `default`）
- `--name <label>`: 账户显示名称

`channels login` 选项：

- `--channel <channel>`（默认 `whatsapp`；支持 `whatsapp`/`web`）
- `--account <id>`
- `--verbose`

`channels logout` 选项：

- `--channel <channel>`（默认 `whatsapp`）
- `--account <id>`

`channels list` 选项：

- `--no-usage`: 跳过模型提供商使用情况/配额快照（仅限 OAuth/API 支持）。
- `--json`: 输出 JSON（除非设置 `--no-usage`，否则包含使用情况）。

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

列出并检查可用技能及就绪信息。

子命令：

- `skills list`: 列出技能（无子命令时的默认操作）。
- `skills info <name>`: 显示单个技能的详细信息。
- `skills check`: 就绪与缺失要求的摘要。

选项：

- `--eligible`: 仅显示就绪的技能。
- `--json`: 输出 JSON（无样式）。
- `-v`, `--verbose`: 包含缺失要求的详细信息。

提示：使用 `npx clawhub` 搜索、安装和同步技能。

### `pairing`

批准跨频道的 DM 配对请求。

子命令：

- `pairing list [channel] [--channel <channel>] [--account <id>] [--json]`
- `pairing approve <channel> <code> [--account <id>] [--notify]`
- `pairing approve --channel <channel> [--account <id>] <code> [--notify]`

### `devices`

管理网关设备配对条目和按角色的设备令牌。

子命令：

- `devices list [--json]`
- `devices approve [requestId] [--latest]`
- `devices reject <requestId>`
- `devices remove <deviceId>`
- `devices clear --yes [--pending]`
- `devices rotate --device <id> --role <role> [--scope <scope...>]`
- `devices revoke --device <id> --role <role>`

### `webhooks gmail`

Gmail Pub/Sub 钩子设置 + 运行器。参见 [/automation/gmail-pubsub](/automation/gmail-pubsub)。

子命令：

- `webhooks gmail setup`（需要 `--account <email>`；支持 `--project`, `--topic`, `--subscription`, `--label`, `--hook-url`, `--hook-token`, `--push-token`, `--bind`, `--port`, `--path`, `--include-body`, `--max-bytes`, `--renew-minutes`, `--tailscale`, `--tailscale-path`, `--tailscale-target`, `--push-endpoint`, `--json`）
- `webhooks gmail run`（相同标志的运行时覆盖）

### `dns setup`

广域网发现 DNS 助手（CoreDNS + Tailscale）。参见 [/gateway/discovery](/gateway/discovery)。

选项：

- `--apply`: 安装/更新 CoreDNS 配置（需要 sudo；仅限 macOS）。

## 消息传递 + 代理

### `message`

统一的外发消息 + 频道操作。

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

通过网关运行一个代理回合（或嵌入的 `--local`）。

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

列出已配置的代理。

选项：

- `--json`
- `--bindings`

#### `agents add [name]`

添加新的隔离代理。除非传递了标志（或 `--non-interactive`），否则运行引导向导；非交互模式下需要 `--workspace`。

选项：

- `--workspace <dir>`
- `--model <id>`
- `--agent-dir <dir>`
- `--bind <channel[:accountId]>`（可重复）
- `--non-interactive`
- `--json`

绑定规范使用 `channel[:accountId]`。当省略 `accountId` 时，OpenClaw 可能通过频道默认值/插件钩子解析账户范围；否则它是没有明确账户范围的频道绑定。

#### `agents bindings`

列出路由绑定。

选项：

- `--agent <id>`
- `--json`

#### `agents bind`

为代理添加路由绑定。

选项：

- `--agent <id>`
- `--bind <channel[:accountId]>`（可重复）
- `--json`

#### `agents unbind`

移除代理的路由绑定。

选项：

- `--agent <id>`
- `--bind <channel[:accountId]>`（可重复）
- `--all`
- `--json`

#### `agents delete <id>`

删除代理并清理其工作区 + 状态。

选项：

- `--force`
- `--json`

### `acp`

运行连接 IDE 到网关的 ACP 桥接程序。

参见 [`acp`](/cli/acp) 获取完整选项和示例。

### `status`

显示链接会话的健康状态和最近的接收者。

选项：

- `--json`
- `--all`（完整诊断；只读，可粘贴）
- `--deep`（探测频道）
- `--usage`（显示模型提供商使用情况/配额）
- `--timeout <ms>`
- `--verbose`
- `--debug`（`--verbose` 的别名）

注意：

- 概览包括网关 + 节点主机服务状态（如有）。

### 使用情况跟踪

当有 OAuth/API 凭据时，OpenClaw 可以显示提供商使用情况/配额。

显示内容：

- `/status`（如有时添加简短的提供商使用情况行）
- `openclaw status --usage`（打印完整的提供商细分）
- macOS 菜单栏（“上下文”下的“使用情况”部分）

注意：

- 数据直接来自提供商使用情况端点（无估算）。
- 提供商：Anthropic, GitHub Copilot, OpenAI Codex OAuth，以及启用这些提供商插件时的 Gemini CLI/Antigravity。
- 如果没有匹配的凭据，使用情况将被隐藏。
- 详情：参见 [使用情况跟踪](/concepts/usage-tracking)。

### `health`

从运行的网关获取健康状态。

选项：

- `--json`
- `--timeout <ms>`
- `--verbose`

### `sessions`

列出存储的对话会话。

选项：

- `--json`
- `--verbose`
- `--store <path>`
- `--active <minutes>`

## 重置 / 卸载

### `reset`

重置本地配置/状态（保留 CLI 安装）。

选项：

- `--scope <config|config+creds+sessions|full>`
- `--yes`
- `--non-interactive`
- `--dry-run`

注意：

- `--non-interactive` 需要 `--scope` 和 `--yes`。

### `uninstall`

卸载网关服务 + 本地数据（CLI 保留）。

选项：

- `--service`
- `--state`
- `--workspace`
- `--app`
- `--all`
- `--yes`
- `--non-interactive`
- `--dry-run`

注意：

- `--non-interactive` 需要 `--yes` 和显式范围（或 `--all`）。

## 网关

### `gateway`

运行 WebSocket 网关。

选项：

- `--port <port>`
- `--bind <loopback|tailnet|lan|auto|custom>`
- `--token <token>`
- `--auth <token|password>`
- `--password <password>`
- `--password-file <path>`
- `--tailscale <off|serve|funnel>`
- `--tailscale-reset-on-exit`
- `--allow-unconfigured`
- `--dev`
- `--reset`（重置开发配置 + 凭据 + 会话 + 工作区）
- `--force`（终止端口上的现有监听器）
- `--verbose`
- `--claude-cli-logs`
- `--ws-log <auto|full|compact>`
- `--compact`（`--ws-log compact` 的别名）
- `--raw-stream`
- `--raw-stream-path <path>`

### `gateway service`

管理网关服务（launchd/systemd/schtasks）。

子命令：

- `gateway status`（默认探测 Gateway RPC）
- `gateway install`（Service 安装）
- `gateway uninstall`
- `gateway start`
- `gateway stop`
- `gateway restart`

注意：

- `gateway status` 默认使用服务的解析端口/配置探测 Gateway RPC（使用 `--url/--token/--password` 覆盖）。
- `gateway status` 支持 `--no-probe`、`--deep` 和 `--json` 用于脚本编写。
- `gateway status` 还能显示它能检测到的遗留或额外的 Gateway 服务（`--deep` 添加系统级扫描）。以 Profile 命名的 OpenClaw 服务被视为一等公民，不会被标记为“额外”。
- `gateway status` 打印 CLI 使用的配置路径与服务可能使用的配置（Service 环境），以及解析后的探测目标 URL。
- 在 Linux systemd 安装中，状态令牌漂移检查包括 `Environment=` 和 `EnvironmentFile=` 单元源。
- `gateway install|uninstall|start|stop|restart` 支持 `--json` 用于脚本编写（默认输出保持人类可读）。
- `gateway install` 默认为 Node 运行时；bun **不推荐**（WhatsApp/Telegram 错误）。
- `gateway install` 选项：`--port`、`--runtime`、`--token`、`--force`、`--json`。

### `logs`

通过 RPC 跟踪 Gateway 文件日志。

注意：

- TTY 会话呈现彩色结构化视图；非 TTY 回退到纯文本。
- `--json` 输出行分隔的 JSON（每行一个日志事件）。

示例：

```bash
openclaw logs --follow
openclaw logs --limit 200
openclaw logs --plain
openclaw logs --json
openclaw logs --no-color
```

### `gateway <subcommand>`

Gateway CLI 辅助工具（对 RPC 子命令使用 `--url`、`--token`、`--password`、`--timeout`、`--expect-final`）。
当您传递 `--url` 时，CLI 不会自动应用配置或环境凭据。
请显式包含 `--token` 或 `--password`。缺少显式凭据是错误。

子命令：

- `gateway call <method> [--params <json>]`
- `gateway health`
- `gateway status`
- `gateway probe`
- `gateway discover`
- `gateway install|uninstall|start|stop|restart`
- `gateway run`

常见 RPC：

- `config.apply`（验证 + 写入配置 + 重启 + 唤醒）
- `config.patch`（合并部分更新 + 重启 + 唤醒）
- `update.run`（运行更新 + 重启 + 唤醒）

提示：直接调用 `config.set`/`config.apply`/`config.patch` 时，如果已存在配置，请从
`config.get` 传递 `baseHash`。

## 模型

有关回退行为和扫描策略，请参见 [/concepts/models](/concepts/models)。

Anthropic setup-token（支持）：

```bash
claude setup-token
openclaw models auth setup-token --provider anthropic
openclaw models status
```

策略说明：这是技术兼容性。Anthropic 过去曾阻止过某些
在 Claude Code 之外的订阅使用；在生产环境中依赖 setup-token 之前，请核实当前 Anthropic
条款。

### `models`（根）

`openclaw models` 是 `models status` 的别名。

根选项：

- `--status-json`（`models status --json` 的别名）
- `--status-plain`（`models status --plain` 的别名）

### `models list`

选项：

- `--all`
- `--local`
- `--provider <name>`
- `--json`
- `--plain`

### `models status`

选项：

- `--json`
- `--plain`
- `--check`（退出码 1=过期/缺失，2=即将过期）
- `--probe`（对配置的认证配置文件进行实时探测）
- `--probe-provider <name>`
- `--probe-profile <id>`（重复或逗号分隔）
- `--probe-timeout <ms>`
- `--probe-concurrency <n>`
- `--probe-max-tokens <n>`

始终包含认证存储中配置文件的认证概览和 OAuth 过期状态。
`--probe` 运行实时请求（可能会消耗令牌并触发速率限制）。

### `models set <model>`

设置 `agents.defaults.model.primary`。

### `models set-image <model>`

设置 `agents.defaults.imageModel.primary`。

### `models aliases list|add|remove`

选项：

- `list`: `--json`、`--plain`
- `add <alias> <model>`
- `remove <alias>`

### `models fallbacks list|add|remove|clear`

选项：

- `list`: `--json`、`--plain`
- `add <model>`
- `remove <model>`
- `clear`

### `models image-fallbacks list|add|remove|clear`

选项：

- `list`: `--json`、`--plain`
- `add <model>`
- `remove <model>`
- `clear`

### `models scan`

选项：

- `--min-params <b>`
- `--max-age-days <days>`
- `--provider <name>`
- `--max-candidates <n>`
- `--timeout <ms>`
- `--concurrency <n>`
- `--no-probe`
- `--yes`
- `--no-input`
- `--set-default`
- `--set-image`
- `--json`

### `models auth add|setup-token|paste-token`

选项：

- `add`: 交互式认证助手
- `setup-token`: `--provider <name>`（默认 `anthropic`）、`--yes`
- `paste-token`: `--provider <name>`、`--profile-id <id>`、`--expires-in <duration>`

### `models auth order get|set|clear`

选项：

- `get`: `--provider <name>`、`--agent <id>`、`--json`
- `set`: `--provider <name>`、`--agent <id>`、`<profileIds...>`
- `clear`: `--provider <name>`、`--agent <id>`

## 系统

### `system event`

入队系统事件并可选地触发心跳（Gateway RPC）。

必需：

- `--text <text>`

选项：

- `--mode <now|next-heartbeat>`
- `--json`
- `--url`、`--token`、`--timeout`、`--expect-final`

### `system heartbeat last|enable|disable`

心跳控制（Gateway RPC）。

选项：

- `--json`
- `--url`、`--token`、`--timeout`、`--expect-final`

### `system presence`

列出系统存在条目（Gateway RPC）。

选项：

- `--json`
- `--url`、`--token`、`--timeout`、`--expect-final`

## Cron

管理计划任务（Gateway RPC）。参见 [/automation/cron-jobs](/automation/cron-jobs)。

子命令：

- `cron status [--json]`
- `cron list [--all] [--json]`（默认表格输出；使用 `--json` 获取原始输出）
- `cron add`（别名：`create`；需要 `--name` 且恰好一个 `--at` | `--every` | `--cron`，以及恰好一个 `--system-event` | `--message` 载荷）
- `cron edit <id>`（修补字段）
- `cron rm <id>`（别名：`remove`、`delete`）
- `cron enable <id>`
- `cron disable <id>`
- `cron runs --id <id> [--limit <n>]`
- `cron run <id> [--force]`

所有 `cron` 命令接受 `--url`、`--token`、`--timeout`、`--expect-final`。

## Node 主机

`node` 运行 **无头节点主机** 或将其作为后台服务管理。参见
[`openclaw node`](/cli/node)。

子命令：

- `node run --host <gateway-host> --port 18789`
- `node status`
- `node install [--host <gateway-host>] [--port <port>] [--tls] [--tls-fingerprint <sha256>] [--node-id <id>] [--display-name <name>] [--runtime <node|bun>] [--force]`
- `node uninstall`
- `node stop`
- `node restart`

认证说明：

- `node` 从 env/config 解析网关认证（无需 `--token`/`--password` 标志）：`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`，然后是 `gateway.auth.*`，通过 `gateway.remote.*` 支持远程模式。
- 遗留 `CLAWDBOT_GATEWAY_*` 环境变量有意忽略用于 Node 主机认证解析。

## 节点

`nodes` 与 Gateway 通信并针对配对的节点。参见 [/nodes](/nodes)。

通用选项：

- `--url`、`--token`、`--timeout`、`--json`

子命令：

- `nodes status [--connected] [--last-connected <duration>]`
- `nodes describe --node <id|name|ip>`
- `nodes list [--connected] [--last-connected <duration>]`
- `nodes pending`
- `nodes approve <requestId>`
- `nodes reject <requestId>`
- `nodes rename --node <id|name|ip> --name <displayName>`
- `nodes invoke --node <id|name|ip> --command <command> [--params <json>] [--invoke-timeout <ms>] [--idempotency-key <key>]`
- `nodes run --node <id|name|ip> [--cwd <path>] [--env KEY=VAL] [--command-timeout <ms>] [--needs-screen-recording] [--invoke-timeout <ms>] <command...>`（mac 节点或无头节点主机）
- `nodes notify --node <id|name|ip> [--title <text>] [--body <text>] [--sound <name>] [--priority <passive|active|timeSensitive>] [--delivery <system|overlay|auto>] [--invoke-timeout <ms>]`（仅限 mac）

相机：

- `nodes camera list --node <id|name|ip>`
- `nodes camera snap --node <id|name|ip> [--facing front|back|both] [--device-id <id>] [--max-width <px>] [--quality <0-1>] [--delay-ms <ms>] [--invoke-timeout <ms>]`
- `nodes camera clip --node <id|name|ip> [--facing front|back] [--device-id <id>] [--duration <ms|10s|1m>] [--no-audio] [--invoke-timeout <ms>]`

画布 + 屏幕：

- `nodes canvas snapshot --node <id|name|ip> [--format png|jpg|jpeg] [--max-width <px>] [--quality <0-1>] [--invoke-timeout <ms>]`
- `nodes canvas present --node <id|name|ip> [--target <urlOrPath>] [--x <px>] [--y <px>] [--width <px>] [--height <px>] [--invoke-timeout <ms>]`
- `nodes canvas hide --node <id|name|ip> [--invoke-timeout <ms>]`
- `nodes canvas navigate <url> --node <id|name|ip> [--invoke-timeout <ms>]`
- `nodes canvas eval [<js>] --node <id|name|ip> [--js <code>] [--invoke-timeout <ms>]`
- `nodes canvas a2ui push --node <id|name|ip> (--jsonl <path> | --text <text>) [--invoke-timeout <ms>]`
- `nodes canvas a2ui reset --node <id|name|ip> [--invoke-timeout <ms>]`
- `nodes screen record --node <id|name|ip> [--screen <index>] [--duration <ms|10s>] [--fps <n>] [--no-audio] [--out <path>] [--invoke-timeout <ms>]`

位置：

- `nodes location get --node <id|name|ip> [--max-age <ms>] [--accuracy <coarse|balanced|precise>] [--location-timeout <ms>] [--invoke-timeout <ms>]`

## 浏览器

浏览器控制 CLI（专用 Chrome/Brave/Edge/Chromium）。参见 [`openclaw browser`](/cli/browser) 和 [浏览器工具](/tools/browser)。

通用选项：

- `--url`、`--token`、`--timeout`、`--json`
- `--browser-profile <name>`

管理：

- `browser status`
- `browser start`
- `browser stop`
- `browser reset-profile`
- `browser tabs`
- `browser open <url>`
- `browser focus <targetId>`
- `browser close [targetId]`
- `browser profiles`
- `browser create-profile --name <name> [--color <hex>] [--cdp-url <url>]`
- `browser delete-profile --name <name>`

检查：

- `browser screenshot [targetId] [--full-page] [--ref <ref>] [--element <selector>] [--type png|jpeg]`
- `browser snapshot [--format aria|ai] [--target-id <id>] [--limit <n>] [--interactive] [--compact] [--depth <n>] [--selector <sel>] [--out <path>]`

操作：

- `browser navigate <url> [--target-id <id>]`
- `browser resize <width> <height> [--target-id <id>]`
- `browser click <ref> [--double] [--button <left|right|middle>] [--modifiers <csv>] [--target-id <id>]`
- `browser type <ref> <text> [--submit] [--slowly] [--target-id <id>]`
- `browser press <key> [--target-id <id>]`
- `browser hover <ref> [--target-id <id>]`
- `browser drag <startRef> <endRef> [--target-id <id>]`
- `browser select <ref> <values...> [--target-id <id>]`
- `browser upload <paths...> [--ref <ref>] [--input-ref <ref>] [--element <selector>] [--target-id <id>] [--timeout-ms <ms>]`
- `browser fill [--fields <json>] [--fields-file <path>] [--target-id <id>]`
- `browser dialog --accept|--dismiss [--prompt <text>] [--target-id <id>] [--timeout-ms <ms>]`
- `browser wait [--time <ms>] [--text <value>] [--text-gone <value>] [--target-id <id>]`
- `browser evaluate --fn <code> [--ref <ref>] [--target-id <id>]`
- `browser console [--level <error|warn|info>] [--target-id <id>]`
- `browser pdf [--target-id <id>]`

## 文档搜索

### `docs [query...]`

搜索实时文档索引。

## TUI

### `tui`

打开连接到网关的终端 UI。

选项：

- `--url <url>`
- `--token <token>`
- `--password <password>`
- `--session <key>`
- `--deliver`
- `--thinking <level>`
- `--message <text>`
- `--timeout-ms <ms>`（默认为 `agents.defaults.timeoutSeconds`）
- `--history-limit <n>`