---
summary: "Doctor command: health checks, config migrations, and repair steps"
read_when:
  - Adding or modifying doctor migrations
  - Introducing breaking config changes
title: "Doctor"
---
# 医生（Doctor）

`openclaw doctor` 是 OpenClaw 的修复与迁移工具。它可修复陈旧的配置/状态、检查系统健康状况，并提供可操作的修复步骤。

## 快速开始

```bash
openclaw doctor
```

### 无头模式 / 自动化

```bash
openclaw doctor --yes
```

不提示即接受所有默认选项（包括在适用时自动执行重启/服务/沙箱修复步骤）。

```bash
openclaw doctor --repair
```

不提示即应用推荐的修复操作（仅在安全前提下执行修复 + 重启）。

```bash
openclaw doctor --repair --force
```

同时应用激进式修复（将覆盖自定义的 supervisor 配置）。

```bash
openclaw doctor --non-interactive
```

无提示运行，且仅执行安全的迁移操作（配置规范化 + 磁盘上状态路径迁移）。跳过需人工确认的重启/服务/沙箱操作。  
当检测到遗留状态时，会自动运行遗留状态迁移。

```bash
openclaw doctor --deep
```

扫描系统服务以查找额外的网关安装（launchd/systemd/schtasks）。

如您希望在写入前先审阅变更，请先打开配置文件：

```bash
cat ~/.openclaw/openclaw.json
```

## 功能概览（What it does）

- （仅交互式）可选的 Git 安装预检更新。
- UI 协议新鲜度检查（当协议 schema 更新时，重建 Control UI）。
- 健康检查 + 重启提示。
- 技能状态摘要（可用/缺失/被阻止）。
- 针对旧版值的配置规范化。
- OpenCode Zen 提供方覆盖警告（`models.providers.opencode`）。
- 遗留磁盘状态迁移（会话/agent 目录/WhatsApp 认证）。
- 状态完整性与权限检查（会话、转录记录、状态目录）。
- 本地运行时的配置文件权限检查（`chmod 600`）。
- 模型认证健康检查：检查 OAuth 过期时间，可刷新即将过期的令牌，并报告认证配置文件处于冷却/禁用状态。
- 额外工作区目录检测（`~/openclaw`）。
- 启用沙箱时的沙箱镜像修复。
- 遗留服务迁移与额外网关检测。
- 网关运行时检查（服务已安装但未运行；缓存的 launchd 标签）。
- 渠道状态警告（从正在运行的网关探测得出）。
- Supervisor 配置审计（launchd/systemd/schtasks），支持可选修复。
- 网关运行时最佳实践检查（Node vs Bun、版本管理器路径）。
- 网关端口冲突诊断（默认为 `18789`）。
- 对开放 DM 策略的安全警告。
- 网关本地令牌模式下的认证检查（当不存在令牌源时，提供令牌生成选项；但不会覆盖令牌 `SecretRef` 配置）。
- Linux 上的 systemd linger 检查。
- 源码安装检查（pnpm 工作区不匹配、缺少 UI 资源、缺少 tsx 二进制文件）。
- 写入更新后的配置 + 向导元数据。

## 详细行为与设计原理

### 0）可选更新（Git 安装）

若当前为 Git 克隆仓库，且 doctor 正在以交互方式运行，则会在执行 doctor 主流程前提示是否更新（fetch/rebase/build）。

### 1）配置规范化

若配置中包含旧版值结构（例如：未设置渠道专属覆盖项的 `messages.ackReaction`），doctor 将其规范化为当前 schema。

### 2）旧版配置键迁移

当配置中包含已弃用的键时，其他命令将拒绝运行，并提示您运行 `openclaw doctor`。

Doctor 将执行以下操作：

- 解释检测到哪些旧版键；
- 展示所应用的迁移操作；
- 使用更新后的 schema 重写 `~/.openclaw/openclaw.json`。

此外，网关在启动时若检测到旧版配置格式，也会自动运行 doctor 迁移，因此陈旧配置可在无需人工干预的情况下完成修复。

当前支持的迁移包括：

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
- 对于具有命名 `accounts` 但缺少 `accounts.default` 的渠道，当存在 `channels.<channel>.accounts.default` 时，将账户作用域的顶层单账户渠道值迁移至其中；
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*`（tools/elevated/exec/sandbox/subagents）
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`  
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`

Doctor 的警告还包含针对多账户渠道的账户默认行为指引：

- 若配置了两个或以上 `channels.<channel>.accounts` 条目，但未设置 `channels.<channel>.defaultAccount` 或 `accounts.default`，doctor 将警告：回退路由可能选择意外的账户；
- 若 `channels.<channel>.defaultAccount` 设置为未知账户 ID，doctor 将发出警告并列出已配置的账户 ID。

### 2b）OpenCode Zen 提供方覆盖

若您手动添加了 `models.providers.opencode`（或 `opencode-zen`），则会覆盖内置的 OpenCode Zen 目录（`@mariozechner/pi-ai`）。这可能导致所有模型强制使用单一 API，或使成本归零。Doctor 将发出警告，以便您移除该覆盖，恢复按模型划分的 API 路由及成本计算。

### 3）旧版状态迁移（磁盘布局）

Doctor 可将旧版磁盘布局迁移至当前结构：

- 会话存储 + 转录记录：
  - 从 `~/.openclaw/sessions/` 迁移至 `~/.openclaw/agents/<agentId>/sessions/`
- Agent 目录：
  - 从 `~/.openclaw/agent/` 迁移至 `~/.openclaw/agents/<agentId>/agent/`
- WhatsApp 认证状态（Baileys）：
  - 从旧版 `~/.openclaw/credentials/*.json`（`oauth.json` 除外）
  - 迁移至 `~/.openclaw/credentials/whatsapp/<accountId>/...`（默认账户 ID：`default`）

这些迁移为尽力而为且幂等；doctor 在保留任何旧版文件夹作为备份时将发出警告。网关/CLI 在启动时也会自动迁移旧版会话 + agent 目录，因此历史记录/认证/模型将自动落入每个 agent 的路径下，无需手动运行 doctor。WhatsApp 认证仅通过 `openclaw doctor` 进行迁移。

### 4）状态完整性检查（会话持久性、路由与安全性）

状态目录是系统的运行中枢。一旦丢失，您将失去会话、凭证、日志和配置（除非另有备份）。

Doctor 检查以下内容：

- **状态目录缺失**：警告灾难性状态丢失风险，提示重新创建目录，并提醒您无法恢复已丢失的数据；
- **状态目录权限**：验证是否可写；提供权限修复选项（并在检测到属主/组不匹配时给出 `chown` 提示）；
- **macOS 云同步状态目录**：当状态路径解析至 iCloud Drive（`~/Library/Mobile Documents/com~apple~CloudDocs/...`）或  
  `~/Library/CloudStorage/...` 时发出警告，因为基于同步的路径可能导致 I/O 更慢，以及锁/同步竞争；
- **Linux SD 或 eMMC 状态目录**：当状态路径解析至 `mmcblk*` 挂载源时发出警告，因为基于 SD 或 eMMC 的随机 I/O 在会话与凭证写入场景下可能更慢，且磨损更快；
- **会话目录缺失**：`sessions/` 和会话存储目录是持久化历史记录、避免 `ENOENT` 崩溃所必需的；
- **转录记录不匹配**：当近期会话条目缺少对应转录文件时发出警告；
- **主会话“单行 JSONL”**：当主转录文件仅含一行时标记（表明历史记录未持续累积）；
- **多个状态目录**：当在多个主目录中存在多个 `~/.openclaw` 文件夹，或 `OPENCLAW_STATE_DIR` 指向其他位置时发出警告（历史记录可能分散在不同安装中）；
- **远程模式提醒**：若 `gateway.mode=remote`，doctor 提醒您应在远程主机上运行（状态实际位于该处）；
- **配置文件权限**：若 `~/.openclaw/openclaw.json` 对组/其他用户可读，doctor 将发出警告，并提供收紧至 `600` 的选项。

### 5）模型认证健康检查（OAuth 过期）

Doctor 检查认证存储中的 OAuth 配置文件，对即将过期/已过期的令牌发出警告，并在安全前提下刷新它们。若 Anthropic Claude Code 配置文件已过时，doctor 将建议运行 `claude setup-token`（或粘贴 setup-token）。刷新提示仅在交互式（TTY）运行时出现；`--non-interactive` 将跳过刷新尝试。

Doctor 还会报告因以下原因暂时不可用的认证配置文件：

- 短期冷却（速率限制/超时/认证失败）；
- 较长禁用（账单/信用失败）。

### 6）钩子模型验证

若设置了 `hooks.gmail.model`，doctor 将依据目录与白名单验证模型引用，并在模型无法解析或被禁止时发出警告。

### 7）沙箱镜像修复

启用沙箱时，doctor 检查 Docker 镜像，并在当前镜像缺失时提供构建或切换至旧版名称的选项。

### 8）网关服务迁移与清理提示

Doctor 检测旧版网关服务（launchd/systemd/schtasks），并提供移除旧服务、使用当前网关端口安装 OpenClaw 服务的选项。它还可扫描额外的类网关服务并输出清理提示。以配置文件命名的 OpenClaw 网关服务被视为一等公民，不会被标记为“额外”。

### 9）安全警告

当某提供方对 DM 开放且未配置允许列表，或策略以危险方式配置时，doctor 将发出警告。

### 10）systemd linger（Linux）

若以 systemd 用户服务运行，doctor 确保已启用 linger，以便网关在用户登出后仍保持运行。

### 11）技能状态

Doctor 打印当前工作区中可用/缺失/被阻止技能的简要摘要。

### 12）网关认证检查（本地令牌）

Doctor 检查本地网关令牌认证就绪状态。

- 如果令牌模式需要一个令牌但不存在令牌源，doctor 会提供生成令牌的选项。  
- 如果 ``gateway.auth.token`` 由 SecretRef 管理但不可用，doctor 将发出警告，且不会将其覆盖为明文。  
- ``openclaw doctor --generate-gateway-token`` 仅在未配置令牌 SecretRef 时强制执行生成操作。

### 12b) 只读、SecretRef 感知的修复

某些修复流程需要检查已配置的凭据，同时不削弱运行时快速失败（fail-fast）行为。

- ``openclaw doctor --fix`` 现在对目标化配置修复使用与 status 类命令相同的只读 SecretRef 摘要模型。  
- 示例：Telegram ``allowFrom`` / ``groupAllowFrom`` ``@username`` 修复会在可用时尝试使用已配置的机器人凭据。  
- 如果 Telegram 机器人令牌通过 SecretRef 配置，但在当前命令路径中不可用，doctor 将报告该凭据“已配置但不可用”，并跳过自动解析，而非崩溃或错误地将令牌报告为缺失。

### 13) 网关健康检查 + 重启

Doctor 执行健康检查，并在网关看起来不健康时提供重启选项。

### 14) 通道状态警告

如果网关健康，doctor 将运行通道状态探测，并报告警告及建议的修复方法。

### 15) Supervisor 配置审计 + 修复

Doctor 检查已安装的 Supervisor 配置（launchd/systemd/schtasks），查找缺失或过时的默认项（例如 systemd 的 network-online 依赖项和重启延迟）。当发现不匹配时，它会建议更新，并可将服务文件/任务重写为当前默认配置。

说明：

- ``openclaw doctor`` 在重写 Supervisor 配置前提示用户确认。  
- ``openclaw doctor --yes`` 接受默认的修复提示。  
- ``openclaw doctor --repair`` 在无提示情况下直接应用推荐的修复。  
- ``openclaw doctor --repair --force`` 覆盖自定义的 Supervisor 配置。  
- 如果令牌认证需要令牌，且 ``gateway.auth.token`` 由 SecretRef 管理，doctor 的服务安装/修复过程将验证该 SecretRef，但不会将解析出的明文令牌值持久化到 Supervisor 服务环境元数据中。  
- 如果令牌认证需要令牌，而所配置的令牌 SecretRef 无法解析，doctor 将阻断安装/修复流程，并提供可操作的指导。  
- 如果同时配置了 ``gateway.auth.token`` 和 ``gateway.auth.password``，但 ``gateway.auth.mode`` 未设置，doctor 将阻断安装/修复流程，直至显式设置模式。  
- 对于 Linux 用户级 systemd 单元，doctor 的令牌漂移检查现在在比对服务认证元数据时，同时包含 ``Environment=`` 和 ``EnvironmentFile=`` 来源。  
- 您始终可通过 ``openclaw gateway install --force`` 强制执行完整重写。

### 16) 网关运行时 + 端口诊断

Doctor 检查服务运行时信息（PID、上次退出状态），并在服务已安装但实际未运行时发出警告。它还会检查网关端口（默认为 ``18789``）是否存在端口冲突，并报告可能的原因（例如网关已在运行、SSH 隧道占用）。

### 17) 网关运行时最佳实践

当网关服务运行在 Bun 或版本管理的 Node 路径（如 ``nvm``、``fnm``、``volta``、``asdf`` 等）上时，doctor 将发出警告。WhatsApp 和 Telegram 通道需要 Node，而版本管理器路径在升级后可能失效，因为服务不会加载您的 shell 初始化脚本。当系统中存在可用的系统级 Node 安装（如 Homebrew/apt/choco）时，doctor 会提供迁移到该安装的选项。

### 18) 配置写入 + 向导元数据

Doctor 持久化所有配置更改，并添加向导元数据以记录本次 doctor 运行。

### 19) 工作区提示（备份 + 内存系统）

当工作区缺少内存系统时，doctor 会建议一种工作区内存系统；若工作区尚未纳入 git 管理，则打印一条备份提示。

详见 [/concepts/agent-workspace](/concepts/agent-workspace)，了解完整的工作区结构指南及 git 备份说明（推荐使用私有 GitHub 或 GitLab）。