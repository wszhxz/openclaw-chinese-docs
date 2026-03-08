---
summary: "Doctor command: health checks, config migrations, and repair steps"
read_when:
  - Adding or modifying doctor migrations
  - Introducing breaking config changes
title: "Doctor"
---
# Doctor

`openclaw doctor` 是 OpenClaw 的修复和迁移工具。它修复过时的配置/状态，检查健康状况，并提供可操作的修复步骤。

## 快速开始

```bash
openclaw doctor
```

### 无头模式 / 自动化

```bash
openclaw doctor --yes
```

无需提示即接受默认值（包括适用的重启/服务/沙箱修复步骤）。

```bash
openclaw doctor --repair
```

无需提示即应用推荐的修复（在安全的情况下进行修复 + 重启）。

```bash
openclaw doctor --repair --force
```

同时应用激进修复（覆盖自定义的管理器配置）。

```bash
openclaw doctor --non-interactive
```

在无提示模式下运行，仅应用安全的迁移（配置规范化 + 磁盘状态移动）。跳过需要人工确认的重启/服务/沙箱操作。
检测到过时状态迁移时会自动运行。

```bash
openclaw doctor --deep
```

扫描系统服务以查找额外的网关安装（launchd/systemd/schtasks）。

如果您想在写入前查看更改，请先打开配置文件：

```bash
cat ~/.openclaw/openclaw.json
```

## 功能概述

- 可选的 git 安装预检更新（仅限交互式）。
- UI 协议新鲜度检查（当协议架构更新时重建控制 UI）。
- 健康检查 + 重启提示。
- 技能状态摘要（符合条件/缺失/被阻止）。
- 过时值的配置规范化。
- OpenCode Zen 提供者覆盖警告 (`models.providers.opencode`)。
- 过时磁盘状态迁移（会话/代理目录/WhatsApp 认证）。
- 状态完整性和权限检查（会话、转录、状态目录）。
- 本地运行时配置文件权限检查（chmod 600）。
- 模型认证健康：检查 OAuth 过期情况，可刷新即将过期的令牌，并报告认证配置文件冷却/禁用状态。
- 额外工作区目录检测 (`~/openclaw`)。
- 启用沙箱时修复沙箱镜像。
- 过时服务迁移和额外网关检测。
- 网关运行时检查（已安装但未运行的服务；缓存的 launchd 标签）。
- 通道状态警告（从运行的网关探测）。
- 管理器配置审计（launchd/systemd/schtasks），支持可选修复。
- 网关运行时最佳实践检查（Node 与 Bun，版本管理器路径）。
- 网关端口冲突诊断（默认 `18789`）。
- 开放 DM 策略的安全警告。
- 本地令牌模式的网关认证检查（当不存在令牌源时提供令牌生成；不覆盖令牌 SecretRef 配置）。
- Linux 上的 systemd linger 检查。
- 源码安装检查（pnpm 工作区不匹配、缺少 UI 资源、缺少 tsx 二进制文件）。
- 写入更新的配置 + 向导元数据。

## 详细行为与原理

### 0) 可选更新（git 安装）

如果是 git 检出且 doctor 正在交互式运行，它会在运行 doctor 之前提供更新（获取/变基/构建）选项。

### 1) 配置规范化

如果配置包含过时值形状（例如 `messages.ackReaction` 没有特定于通道的覆盖），doctor 会将它们规范化为当前架构。

### 2) 过时配置键迁移

当配置包含已弃用的键时，其他命令将拒绝运行并要求您运行 `openclaw doctor`。

Doctor 将：

- 解释发现了哪些过时键。
- 显示其应用的迁移。
- 使用更新的架构重写 `~/.openclaw/openclaw.json`。

网关在启动时检测到过时配置格式时也会自动运行 doctor 迁移，因此无需手动干预即可修复过时配置。

当前迁移：

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → 顶层 `bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- 对于具有命名 `accounts` 但缺少 `accounts.default` 的通道，当存在时将账户范围顶层单账户通道值移动到 `channels.<channel>.accounts.default`
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*`（tools/elevated/exec/sandbox/subagents）
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`

Doctor 警告还包括多账户通道的账户默认指导：

- 如果配置了两个或更多 `channels.<channel>.accounts` 条目而没有 `channels.<channel>.defaultAccount` 或 `accounts.default`，doctor 会警告回退路由可能会选择意外的账户。
- 如果 `channels.<channel>.defaultAccount` 设置为未知账户 ID，doctor 会发出警告并列出配置的账户 ID。

### 2b) OpenCode Zen 提供者覆盖

如果您手动添加了 `models.providers.opencode`（或 `opencode-zen`），它将覆盖来自 `@mariozechner/pi-ai` 的内置 OpenCode Zen 目录。这可能会强制所有模型使用单个 API 或将成本归零。Doctor 会发出警告，以便您可以移除覆盖并恢复按模型的 API 路由 + 成本。

### 3) 过时状态迁移（磁盘布局）

Doctor 可以将较旧的磁盘布局迁移到当前结构：

- 会话存储 + 转录：
  - 从 `~/.openclaw/sessions/` 到 `~/.openclaw/agents/<agentId>/sessions/`
- 代理目录：
  - 从 `~/.openclaw/agent/` 到 `~/.openclaw/agents/<agentId>/agent/`
- WhatsApp 认证状态（Baileys）：
  - 从过时 `~/.openclaw/credentials/*.json`（除 `oauth.json` 外）
  - 到 `~/.openclaw/credentials/whatsapp/<accountId>/...`（默认账户 ID：`default`）

这些迁移尽最大努力且幂等；doctor 在遗留文件夹作为备份留下时会发出警告。网关/CLI 也会在启动时自动迁移过时会话 + 代理目录，这样历史/认证/模型就会进入每个代理路径，而无需手动运行 doctor。WhatsApp 认证有意仅通过 `openclaw doctor` 迁移。

### 4) 状态完整性检查（会话持久性、路由和安全）

状态目录是操作中枢。如果它消失，您将丢失会话、凭据、日志和配置（除非您在别处有备份）。

Doctor 检查：

- **状态目录缺失**：警告灾难性状态丢失，提示重新创建目录，并提醒您无法恢复丢失的数据。
- **状态目录权限**：验证可写性；提供修复权限选项（当检测到所有者/组不匹配时发出 `chown` 提示）。
- **macOS 云同步状态目录**：当状态解析到 iCloud Drive (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) 或 `~/Library/CloudStorage/...` 下时发出警告，因为基于同步的路径可能导致较慢的 I/O 和锁/同步竞争。
- **Linux SD 或 eMMC 状态目录**：当状态解析到 `mmcblk*` 挂载源时发出警告，因为基于 SD 或 eMMC 的随机 I/O 在会话和凭据写入下可能更慢且磨损更快。
- **会话目录缺失**：`sessions/` 和会话存储目录是持久化历史所必需的，以避免 `ENOENT` 崩溃。
- **转录不匹配**：当最近的会话条目缺少转录文件时发出警告。
- **主会话"1 行 JSONL"**：当主转录只有一行时标记（历史未累积）。
- **多个状态目录**：当跨主目录存在多个 `~/.openclaw` 文件夹或 `OPENCLAW_STATE_DIR` 指向其他地方时发出警告（历史可能在安装之间分裂）。
- **远程模式提醒**：如果 `gateway.mode=remote`，doctor 提醒您要在远程主机上运行它（状态位于那里）。
- **配置文件权限**：如果 `~/.openclaw/openclaw.json` 对组/世界可读则发出警告，并提供收紧到 `600` 的选项。

### 5) 模型认证健康（OAuth 过期）

Doctor 检查认证存储中的 OAuth 配置文件，当令牌即将过期/已过期时发出警告，并在安全时刷新它们。如果 Anthropic Claude Code 配置文件过时，建议运行 `claude setup-token`（或粘贴 setup-token）。刷新提示仅在交互式运行时出现（TTY）；`--non-interactive` 跳过刷新尝试。

Doctor 还报告因以下原因暂时不可用的认证配置文件：

- 短冷却期（速率限制/超时/认证失败）
- 较长禁用（计费/信用失败）

### 6) Hooks 模型验证

如果设置了 `hooks.gmail.model`，doctor 会根据目录和允许列表验证模型引用，并在无法解析或被禁止时发出警告。

### 7) 沙箱镜像修复

启用沙箱时，doctor 检查 Docker 镜像，如果当前镜像缺失，则提供构建或切换到旧名称的选项。

### 8) 网关服务迁移和清理提示

Doctor 检测过时网关服务（launchd/systemd/schtasks），并提供移除它们并使用当前网关端口安装 OpenClaw 服务的选项。它还可以扫描额外的类网关服务并打印清理提示。以配置文件命名的 OpenClaw 网关服务被视为一等公民，不会被标记为“额外”。

### 9) 安全警告

当提供者对 DM 开放而没有允许列表，或者策略以危险方式配置时，Doctor 发出警告。

### 10) systemd linger（Linux）

如果作为 systemd 用户服务运行，doctor 确保启用 linger，以便注销后网关保持存活。

### 11) 技能状态

Doctor 打印当前工作区的符合条件/缺失/被阻止技能的快速摘要。

### 12) 网关认证检查（本地令牌）

Doctor 检查本地网关令牌认证就绪状态。

- 如果 token mode 需要 token 且不存在 token source，doctor 提供生成一个的选项。
- 如果 `gateway.auth.token` 是由 SecretRef 管理但 unavailable，doctor 会警告且不会用 plaintext 覆盖它。
- `openclaw doctor --generate-gateway-token` 仅在没有配置 token SecretRef 时强制 generation。

### 12b) Read-only SecretRef-aware repairs

某些 repair flows 需要检查配置的 credentials 而不削弱 runtime fail-fast behavior。

- `openclaw doctor --fix` 现在使用与 status-family commands 相同的 read-only SecretRef summary model 来进行 targeted config repairs。
- 示例：Telegram `allowFrom` / `groupAllowFrom` `@username` repair 尝试在 available 时使用配置的 bot credentials。
- 如果 Telegram bot token 是通过 SecretRef 配置的但在当前 command path 中 unavailable，doctor 报告该 credential 是 configured-but-unavailable 并跳过 auto-resolution，而不是 crashing 或将 token 误报为 missing。

### 13) Gateway health check + restart

Doctor 运行 health check 并在 gateway 看起来 unhealthy 时提供 restart 选项。

### 14) Channel status warnings

如果 gateway 是 healthy 的，doctor 运行 channel status probe 并报告 warnings 及 suggested fixes。

### 15) Supervisor config audit + repair

Doctor 检查已安装的 supervisor config (launchd/systemd/schtasks) 是否存在 missing 或 outdated defaults (例如，systemd network-online dependencies 和 restart delay)。当发现 mismatch 时，它推荐 update 并可以 rewrite the service file/task 为 current defaults。

Notes:

- `openclaw doctor` 在 rewriting supervisor config 之前 prompts。
- `openclaw doctor --yes` 接受 default repair prompts。
- `openclaw doctor --repair` 应用 recommended fixes 而不 prompts。
- `openclaw doctor --repair --force` 覆盖 custom supervisor configs。
- 如果 token auth 需要 token 且 `gateway.auth.token` 是由 SecretRef 管理，doctor service install/repair 验证 SecretRef 但不会 persist resolved plaintext token values 到 supervisor service environment metadata 中。
- 如果 token auth 需要 token 且配置的 token SecretRef 是 unresolved，doctor 阻止 the install/repair path 并提供 actionable guidance。
- 如果 `gateway.auth.token` 和 `gateway.auth.password` 都 configured 且 `gateway.auth.mode` 是 unset，doctor 阻止 install/repair 直到 mode 被 explicitly set。
- 对于 Linux user-systemd units，doctor token drift checks 现在在 comparing service auth metadata 时包括 both `Environment=` 和 `EnvironmentFile=` sources。
- 你总是可以通过 `openclaw gateway install --force` 强制 full rewrite。

### 16) Gateway runtime + port diagnostics

Doctor 检查 the service runtime (PID, last exit status) 并在 service 是 installed 但 not actually running 时警告。它还检查 gateway port (默认 `18789`) 上的 port collisions 并报告 likely causes (gateway already running, SSH tunnel)。

### 17) Gateway runtime best practices

当 gateway service 运行在 Bun 或 version-managed Node path (`nvm`, `fnm`, `volta`, `asdf`, 等) 上时，Doctor 会警告。WhatsApp + Telegram channels 需要 Node，且 version-manager paths 可能在 upgrades 后 break，因为 service 不加载你的 shell init。Doctor 提供迁移到 system Node install 的选项 (如果可用 (Homebrew/apt/choco))。

### 18) Config write + wizard metadata

Doctor 持久化任何 config changes 并标记 wizard metadata 以记录 the doctor run。

### 19) Workspace tips (backup + memory system)

当 missing 时 Doctor 建议一个 workspace memory system，如果 workspace 尚未纳入 git 则打印 backup tip。

参见 [/concepts/agent-workspace](/concepts/agent-workspace) 获取 workspace structure 和 git backup 的完整指南 (推荐 private GitHub 或 GitLab)。