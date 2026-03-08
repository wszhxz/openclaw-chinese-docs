---
summary: "Agent workspace: location, layout, and backup strategy"
read_when:
  - You need to explain the agent workspace or its file layout
  - You want to back up or migrate an agent workspace
title: "Agent Workspace"
---
# Agent 工作区

工作区是 Agent 的家。它是文件工具和工作区上下文使用的唯一工作目录。请保持其私密性并将其视为记忆。

这与 `~/.openclaw/` 分开，后者存储配置、凭据和会话。

**重要：** 工作区是 **默认 cwd**，而不是硬沙箱。工具针对工作区解析相对路径，但除非启用沙箱，否则绝对路径仍然可以到达主机上的其他位置。如果需要隔离，请使用 [`agents.defaults.sandbox`](/gateway/sandboxing)（和/或每 Agent 沙箱配置）。当启用沙箱且 `workspaceAccess` 不是 `"rw"` 时，工具在 `~/.openclaw/sandboxes` 下的沙箱工作区内操作，而不是你的主机工作区。

## 默认位置

- 默认：`~/.openclaw/workspace`
- 如果设置了 `OPENCLAW_PROFILE` 且不是 `"default"`，默认变为 `~/.openclaw/workspace-<profile>`。
- 在 `~/.openclaw/openclaw.json` 中覆盖：

```json5
{
  agent: {
    workspace: "~/.openclaw/workspace",
  },
}
```

`openclaw onboard`、`openclaw configure` 或 `openclaw setup` 将创建工作区，并在缺少引导文件时初始化它们。
沙箱种子复制仅接受工作区内的常规文件；解析到源工作区之外的符号链接/硬链接别名将被忽略。

如果你已经自己管理工作区文件，可以禁用引导文件创建：

```json5
{ agent: { skipBootstrap: true } }
```

## 额外工作区文件夹

较旧的安装可能创建了 `~/openclaw`。保留多个工作区目录可能会导致令人困惑的认证或状态漂移，因为一次只有一个工作区是活动的。

**建议：** 保持单个活动工作区。如果你不再使用额外文件夹，将其归档或移动到回收站（例如 `trash ~/openclaw`）。如果你有意保留多个工作区，请确保 `agents.defaults.workspace` 指向活动的那个。

`openclaw doctor` 在检测到额外工作区目录时会发出警告。

## 工作区文件映射（每个文件的含义）

这些是 OpenClaw 期望在工作区内的标准文件：

- `AGENTS.md`
  - Agent 的操作指令以及它应该如何使用记忆。
  - 在每个会话开始时加载。
  - 适合放置规则、优先级和“如何行为”的详细信息。

- `SOUL.md`
  - 人设、语气和边界。
  - 每个会话加载。

- `USER.md`
  - 用户是谁以及如何称呼他们。
  - 每个会话加载。

- `IDENTITY.md`
  - Agent 的名称、氛围和表情符号。
  - 在引导仪式期间创建/更新。

- `TOOLS.md`
  - 关于本地工具和约定的注释。
  - 不控制工具可用性；它仅是指导。

- `HEARTBEAT.md`
  - 用于心跳运行的可选小型检查列表。
  - 保持简短以避免令牌消耗。

- `BOOT.md`
  - 当启用内部钩子时，在 Gateway 重启时执行的可选启动检查列表。
  - 保持简短；使用消息工具进行外发发送。

- `BOOTSTRAP.md`
  - 一次性首次运行仪式。
  - 仅在全新工作区时创建。
  - 仪式完成后删除它。

- `memory/YYYY-MM-DD.md`
  - 每日记忆日志（每天一个文件）。
  - 建议在会话开始时读取今天 + 昨天的内容。

- `MEMORY.md`（可选）
  - 策划的长期记忆。
  - 仅在主私密会话中加载（不在共享/群组上下文中）。

参见 [记忆](/concepts/memory) 了解工作流和自动记忆刷新。

- `skills/`（可选）
  - 工作区特定的技能。
  - 当名称冲突时覆盖托管/捆绑技能。

- `canvas/`（可选）
  - 用于节点显示的 Canvas UI 文件（例如 `canvas/index.html`）。

如果任何引导文件缺失，OpenClaw 会将“缺失文件”标记注入会话并继续。大型引导文件在注入时会被截断；使用 `agents.defaults.bootstrapMaxChars`（默认：20000）和 `agents.defaults.bootstrapTotalMaxChars`（默认：150000）调整限制。
`openclaw setup` 可以重新创建缺失的默认值而不覆盖现有文件。

## 工作区中不包含的内容

这些位于 `~/.openclaw/` 下，不应提交到工作区仓库：

- `~/.openclaw/openclaw.json`（配置）
- `~/.openclaw/credentials/`（OAuth 令牌、API 密钥）
- `~/.openclaw/agents/<agentId>/sessions/`（会话转录 + 元数据）
- `~/.openclaw/skills/`（托管技能）

如果你需要迁移会话或配置，请单独复制它们并将其保持在版本控制之外。

## Git 备份（建议，私密）

将工作区视为私密记忆。将其放入 **私密** git 仓库中，以便备份和恢复。

在运行 Gateway 的机器上运行这些步骤（即工作区所在之处）。

### 1) 初始化仓库

如果安装了 git，全新工作区会自动初始化。如果此工作区还不是仓库，运行：

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md SOUL.md TOOLS.md IDENTITY.md USER.md HEARTBEAT.md memory/
git commit -m "Add agent workspace"
```

### 2) 添加私密远程（初学者友好选项）

选项 A：GitHub Web UI

1. 在 GitHub 上创建一个新的 **私密** 仓库。
2. 不要用 README 初始化（避免合并冲突）。
3. 复制 HTTPS 远程 URL。
4. 添加远程并推送：

```bash
git branch -M main
git remote add origin <https-url>
git push -u origin main
```

选项 B：GitHub CLI (`gh`)

```bash
gh auth login
gh repo create openclaw-workspace --private --source . --remote origin --push
```

选项 C：GitLab Web UI

1. 在 GitLab 上创建一个新的 **私密** 仓库。
2. 不要用 README 初始化（避免合并冲突）。
3. 复制 HTTPS 远程 URL。
4. 添加远程并推送：

```bash
git branch -M main
git remote add origin <https-url>
git push -u origin main
```

### 3) 持续更新

```bash
git status
git add .
git commit -m "Update memory"
git push
```

## 不要提交秘密

即使在私密仓库中，也要避免在工作区中存储秘密：

- API 密钥、OAuth 令牌、密码或私密凭据。
- `~/.openclaw/` 下的任何内容。
- 聊天原始转储或敏感附件。

如果你必须存储敏感引用，请使用占位符并将真实秘密保存在其他地方（密码管理器、环境变量或 `~/.openclaw/`）。

建议的 `.gitignore` 起始文件：

```gitignore
.DS_Store
.env
**/*.key
**/*.pem
**/secrets*
```

## 将工作区移动到新机器

1. 将仓库克隆到所需路径（默认 `~/.openclaw/workspace`）。
2. 在 `~/.openclaw/openclaw.json` 中将 `agents.defaults.workspace` 设置为该路径。
3. 运行 `openclaw setup --workspace <path>` 以初始化任何缺失的文件。
4. 如果你需要会话，请单独从旧机器复制 `~/.openclaw/agents/<agentId>/sessions/`。

## 高级说明

- 多 Agent 路由可以为每个 Agent 使用不同的工作区。参见 [Channel 路由](/channels/channel-routing) 了解路由配置。
- 如果启用了 `agents.defaults.sandbox`，非主会话可以使用 `agents.defaults.sandbox.workspaceRoot` 下的每会话沙箱工作区。