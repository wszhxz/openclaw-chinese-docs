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

在提示时不接受默认值（包括适用的重启/服务/沙盒修复步骤）。

```bash
openclaw doctor --repair
```

在提示时不接受推荐的修复（安全的情况下进行修复+重启）。

```bash
openclaw doctor --repair --force
```

应用激进的修复（覆盖自定义监督器配置）。

```bash
openclaw doctor --non-interactive
```

在没有提示的情况下运行，并仅应用安全的迁移（配置规范化+磁盘上的状态移动）。跳过需要人工确认的重启/服务/沙盒操作。
检测到旧版状态迁移时会自动运行。

```bash
openclaw doctor --deep
```

扫描系统服务以查找额外的网关安装（launchd/systemd/schtasks）。

如果您想在写入之前查看更改，请先打开配置文件：

```bash
cat ~/.openclaw/openclaw.json
```

## 它的作用（摘要）

- 可选的预检更新（仅限 git 安装）。
- UI 协议新鲜度检查（当协议架构较新时重建控制 UI）。
- 健康检查 + 重启提示。
- 技能状态摘要（符合条件/缺失/被阻止）。
- 旧版值的配置规范化。
- OpenCode Zen 提供者覆盖警告 (`models.providers.opencode`)。
- 旧版磁盘上状态迁移（会话/代理目录/WhatsApp 认证）。
- 状态完整性和权限检查（会话、记录、状态目录）。
- 运行本地时检查配置文件权限（chmod 600）。
- 模型认证健康：检查 OAuth 过期时间，可以刷新即将过期的令牌，并报告认证配置文件冷却/禁用状态。
- 额外工作区目录检测 (`~/openclaw`)。
- 启用沙盒时修复沙盒镜像。
- 旧版服务迁移和额外网关检测。
- 网关运行时检查（已安装但未运行的服务；缓存的 launchd 标签）。
- 通道状态警告（从正在运行的网关探测）。
- 监督器配置审核（launchd/systemd/schtasks），可选修复。
- 网关运行时最佳实践检查（Node vs Bun，版本管理器路径）。
- 网关端口冲突诊断（默认 `18789`）。
- 对于开放 DM 策略的安全警告。
- 当没有设置 `gateway.auth.token` 时发出网关认证警告（本地模式；提供令牌生成）。
- 在 Linux 上进行 systemd linger 检查。
- 源安装检查（pnpm 工作区不匹配，缺少 UI 资产，缺少 tsx 二进制文件）。
- 写入更新后的配置 + 向导元数据。

## 详细行为和理由

### 0) 可选更新（git 安装）

如果这是一个 git 检出并且 doctor 正在交互式运行，它会在运行 doctor 之前提供更新（获取/合并/构建）的选择。

### 1) 配置规范化

如果配置包含旧版值形状（例如 `messages.ackReaction` 没有特定通道的重写），doctor 将其规范化为当前架构。

### 2) 旧版配置键迁移

当配置包含已弃用的键时，其他命令会拒绝运行并要求您运行 `openclaw doctor`。

Doctor 将：

- 解释找到的旧版键。
- 显示应用的迁移。
- 使用更新后的架构重写 `~/.openclaw/openclaw.json`。

网关也会在启动时自动运行 doctor 迁移，当检测到旧版配置格式时，无需手动干预即可修复过时的配置。

当前迁移：

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → 顶级 `bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`

### 2b) OpenCode Zen 提供者覆盖

如果您手动添加了 `models.providers.opencode`（或 `opencode-zen`），它会覆盖来自 `@mariozechner/pi-ai` 的内置 OpenCode Zen 目录。这可能会将每个模型强制到单个 API 或清零成本。Doctor 会发出警告，以便您可以删除覆盖并恢复按模型的 API 路由 + 成本。

### 3) 旧版状态迁移（磁盘布局）

Doctor 可以将较旧的磁盘布局迁移到当前结构：

- 会话存储 + 记录：
  - 从 `~/.openclaw/sessions/` 到 `~/.openclaw/agents/<agentId>/sessions/`
- 代理目录：
  - 从 `~/.openclaw/agent/` 到 `~/.openclaw/agents/<agentId>/agent/`
- WhatsApp 认证状态（Baileys）：
  - 从旧版 `~/.openclaw/credentials/*.json`（除了 `oauth.json`）
  - 到 `~/.openclaw/credentials/whatsapp/<accountId>/...`（默认账户 ID: `default`）

这些迁移是尽力而为且幂等的；当 doctor 留下任何旧版文件夹作为备份时会发出警告。网关/CLI 也会在启动时自动迁移旧版会话 + 代理目录，因此历史记录/认证/模型会进入每个代理的路径，而无需手动运行 doctor。WhatsApp 认证故意仅通过 `openclaw doctor` 进行迁移。

### 4) 状态完整性检查（会话持久性、路由和安全性）

状态目录是操作的核心。如果它消失，您将丢失会话、凭据、日志和配置（除非您在其他地方有备份）。

Doctor 检查：

- **状态目录缺失**：警告灾难性状态丢失，提示重新创建目录，并提醒您无法恢复丢失的数据。
- **状态目录权限**：验证可写性；提供修复权限的选项（当检测到所有者/组不匹配时发出 `chown` 提示）。
- **会话目录缺失**：`sessions/` 和会话存储目录是必需的，以持久化历史记录并避免 `ENOENT` 崩溃。
- **记录不匹配**：当最近的会话条目缺少记录文件时发出警告。
- **主会话“1 行 JSONL”**：标记当主记录只有 1 行时（历史记录未累积）。
- **多个状态目录**：当多个 `~/.openclaw` 文件夹存在于主目录之间或 `OPENCLAW_STATE_DIR` 指向其他位置时发出警告（历史记录可以在安装之间拆分）。
- **远程模式提醒**：如果 `gateway.mode=remote`，doctor 提醒您在远程主机上运行它（状态存储在那里）。
- **配置文件权限**：如果 `~/.openclaw/openclaw.json` 是组/世界可读的，则发出警告并提供收紧到 `600` 的选项。

### 5) 模型认证健康（OAuth 过期）

Doctor 检查认证存储中的 OAuth 配置文件，当令牌即将过期/过期时发出警告，并在安全的情况下刷新它们。如果 Anthropic Claude Code 配置文件过时，建议运行 `claude setup-token`（或粘贴一个设置令牌）。刷新提示仅在交互式运行（TTY）时出现；`--non-interactive` 跳过刷新尝试。

Doctor 还报告由于以下原因暂时无法使用的认证配置文件：

- 短暂冷却（速率限制/超时/认证失败）
- 较长禁用（计费/信用失败）

### 6) Hooks 模型验证

如果设置了 `hooks.gmail.model`，doctor 验证模型引用是否与目录和允许列表匹配，并在无法解析或被禁止时发出警告。

### 7) 沙盒镜像修复

当启用沙盒时，doctor 检查 Docker 镜像，并在当前镜像缺失时提供构建或切换到旧版名称的选项。

### 8) 网关服务迁移和清理提示

Doctor 检测旧版网关服务（launchd/systemd/schtasks），并提供删除它们并使用当前网关端口安装 OpenClaw 服务的选项。它还可以扫描类似网关的服务并打印清理提示。以配置文件命名的 OpenClaw 网关服务被视为第一类服务，不会被标记为“额外”。

### 9) 安全警告

当提供者对 DM 开放且没有允许列表，或者策略以危险方式配置时，Doctor 发出警告。

### 10) systemd linger (Linux)

如果作为 systemd 用户服务运行，doctor 确保启用了 lingering，以便网关在注销后保持运行。

### 11) 技能状态

Doctor 打印当前工作区符合条件/缺失/被阻止的技能的快速摘要。

### 12) 网关认证检查（本地令牌）

当本地网关上缺少 `gateway.auth` 时，Doctor 发出警告并提供生成令牌的选项。使用 `openclaw doctor --generate-gateway-token` 在自动化中强制创建令牌。

### 13) 网关健康检查 + 重启

Doctor 运行健康检查并在网关看起来不健康时提供重启选项。

### 14) 通道状态警告

如果网关健康，Doctor 运行通道状态探测并报告带有建议修复的警告。

### 15) 监督器配置审核 + 修复

Doctor 检查已安装的监督器配置（launchd/systemd/schtasks）中是否存在缺失或过时的默认设置（例如，systemd network-online 依赖项和重启延迟）。当发现不匹配时，它建议更新并可以将服务文件/任务重写为当前默认设置。

注意：

- `openclaw doctor` 在重写监督器配置之前提示。
- `openclaw doctor --yes` 接受默认修复提示。
- `openclaw doctor --repair` 在没有提示的情况下应用推荐的修复。
- `openclaw doctor --repair --force` 覆盖自定义监督器配置。
- 您可以通过 `openclaw gateway install --force` 强制完全重写。

### 16) 网关运行时 + 端口诊断

Doctor 检查服务运行时（PID，最后退出状态），并在服务已安装但未实际运行时发出警告。它还会检查网关端口（默认 `18789`）上的端口冲突，并报告可能的原因（网关已经在运行，SSH 隧道）。

### 17) 网关运行时最佳实践

Doctor 在网关服务使用 Bun 或版本管理的 Node 路径（`nvm`，`fnm`，`volta`，`asdf` 等）时发出警告。WhatsApp + Telegram 通道需要 Node，并且版本管理路径在升级后可能会中断，因为服务不会加载您的 shell 初始化。当可用时，Doctor 提供迁移到系统 Node 安装的选项（Homebrew/apt/choco）。

### 18) 配置写入 + 向导元数据

Doctor 持久化任何配置更改，并记录 doctor 运行的向导元数据。

### 19) 工作区提示（备份 + 记忆系统）

当缺少时，Doctor 建议一个工作区记忆系统，并在工作区尚未在 git 下时打印备份提示。

有关工作区结构和 git 备份（推荐私有 GitHub 或 GitLab）的完整指南，请参阅 [/concepts/agent-workspace](/concepts/agent-workspace)。