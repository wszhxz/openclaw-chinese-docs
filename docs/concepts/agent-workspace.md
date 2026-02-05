---
summary: "Agent workspace: location, layout, and backup strategy"
read_when:
  - You need to explain the agent workspace or its file layout
  - You want to back up or migrate an agent workspace
title: "Agent Workspace"
---
# Agent 工作区

工作区是代理的家。它是用于文件工具和工作区上下文的唯一工作目录。请保持其私密性，并将其视为内存。

这与 `~/.openclaw/` 是分开的，后者存储配置、凭据和会话。

**重要：** 工作区是 **默认的当前工作目录**，而不是硬沙盒。工具会根据工作区解析相对路径，但绝对路径仍然可以访问主机上的其他位置，除非启用了沙盒。如果需要隔离，请使用[`agents.defaults.sandbox`](/gateway/sandboxing)（和/或每个代理的沙盒配置）。当启用沙盒且 `workspaceAccess` 不是 `"rw"` 时，工具将在 `~/.openclaw/sandboxes` 下的沙盒工作区中运行，而不是您的主机工作区。

## 默认位置

- 默认: `~/.openclaw/workspace`
- 如果设置了 `OPENCLAW_PROFILE` 且不是 `"default"`，默认变为
  `~/.openclaw/workspace-<profile>`。
- 在 `~/.openclaw/openclaw.json` 中覆盖：

```json5
{
  agent: {
    workspace: "~/.openclaw/workspace",
  },
}
```

`openclaw onboard`，`openclaw configure`，或 `openclaw setup` 将在缺少时创建工作区并填充引导文件。

如果您已经自行管理工作区文件，可以禁用引导文件的创建：

```json5
{ agent: { skipBootstrap: true } }
```

## 额外的工作区文件夹

旧版本安装可能会创建 `~/openclaw`。保留多个工作区目录可能会导致混淆的身份验证或状态漂移，因为一次只有一个工作区处于活动状态。

**建议：** 保持一个活动的工作区。如果您不再使用额外的文件夹，请将其归档或移动到废纸篓（例如 `trash ~/openclaw`）。如果您有意保留多个工作区，请确保
`agents.defaults.workspace` 指向活动的一个。

`openclaw doctor` 在检测到额外的工作区目录时会发出警告。

## 工作区文件映射（每个文件的含义）

这些是 OpenClaw 期望在工作区中的标准文件：

- `AGENTS.md`
  - 代理的操作说明及其如何使用内存。
  - 在每个会话开始时加载。
  - 规则、优先级和“如何表现”的详细信息的好地方。

- `SOUL.md`
  - 人格、语气和界限。
  - 每个会话加载。

- `USER.md`
  - 用户是谁以及如何称呼他们。
  - 每个会话加载。

- `IDENTITY.md`
  - 代理的名称、氛围和表情符号。
  - 在引导仪式期间创建/更新。

- `TOOLS.md`
  - 关于本地工具和约定的笔记。
  - 不控制工具可用性；仅作为指导。

- `HEARTBEAT.md`
  - 可选的小型心跳运行检查清单。
  - 保持简短以避免令牌消耗。

- `BOOT.md`
  - 可选的启动检查清单，在内部钩子启用时网关重启时执行。
  - 保持简短；使用消息工具进行外部发送。

- `BOOTSTRAP.md`
  - 一次性首次运行仪式。
  - 仅针对全新的工作区创建。
  - 完成仪式后删除它。

- `memory/YYYY-MM-DD.md`
  - 每日记忆日志（每天一个文件）。
  - 建议在会话开始时阅读今天和昨天的日志。

- `MEMORY.md`（可选）
  - 筛选后的长期记忆。
  - 仅在主、私有会话中加载（不包括共享/组上下文）。

参见 [Memory](/concepts/memory) 了解工作流程和自动记忆刷新。

- `skills/`（可选）
  - 工作区特定技能。
  - 当名称冲突时覆盖托管/捆绑的技能。

- `canvas/`（可选）
  - 节点显示的画布 UI 文件（例如 `canvas/index.html`）。

如果缺少任何引导文件，OpenClaw 会在会话中注入“缺失文件”标记并继续。注入时大型引导文件会被截断；通过 `agents.defaults.bootstrapMaxChars` 调整限制（默认：20000）。
`openclaw setup` 可以重新创建缺失的默认值而不覆盖现有文件。

## 工作区中不包含的内容

这些位于 `~/.openclaw/` 下，不应提交到工作区仓库：

- `~/.openclaw/openclaw.json`（配置）
- `~/.openclaw/credentials/`（OAuth 令牌、API 密钥）
- `~/.openclaw/agents/<agentId>/sessions/`（会话记录 + 元数据）
- `~/.openclaw/skills/`（托管技能）

如果您需要迁移会话或配置，请单独复制它们并保持不在版本控制中。

## Git 备份（推荐，私有）

将工作区视为私有内存。将其放入一个 **私有** 的 git 仓库中以便备份和恢复。

在网关运行的机器上运行这些步骤（即工作区所在的位置）。

### 1) 初始化仓库

如果已安装 git，全新工作区会自动初始化。如果此工作区还不是仓库，请运行：

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md SOUL.md TOOLS.md IDENTITY.md USER.md HEARTBEAT.md memory/
git commit -m "Add agent workspace"
```

### 2) 添加私有远程（适合初学者的选项）

选项 A: GitHub 网页界面

1. 在 GitHub 上创建一个新的 **私有** 仓库。
2. 不要使用 README 初始化（避免合并冲突）。
3. 复制 HTTPS 远程 URL。
4. 添加远程并推送：

```bash
git branch -M main
git remote add origin <https-url>
git push -u origin main
```

选项 B: GitHub CLI (`gh`)

```bash
gh auth login
gh repo create openclaw-workspace --private --source . --remote origin --push
```

选项 C: GitLab 网页界面

1. 在 GitLab 上创建一个新的 **私有** 仓库。
2. 不要使用 README 初始化（避免合并冲突）。
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

## 不要提交机密信息

即使在私有仓库中，也避免在工作区中存储机密信息：

- API 密钥、OAuth 令牌、密码或其他私人凭证。
- `~/.openclaw/` 下的所有内容。
- 聊天的原始转储或敏感附件。

如果必须存储敏感引用，请使用占位符并将实际机密信息保存在其他位置（密码管理器、环境变量或 `~/.openclaw/`）。

建议的 `.gitignore` 启动器：

```gitignore
.DS_Store
.env
**/*.key
**/*.pem
**/secrets*
```

## 将工作区迁移到新机器

1. 将仓库克隆到所需路径（默认 `~/.openclaw/workspace`）。
2. 在 `~/.openclaw/openclaw.json` 中将 `agents.defaults.workspace` 设置为该路径。
3. 运行 `openclaw setup --workspace <path>` 以填充任何缺失的文件。
4. 如果需要会话，请从旧机器单独复制 `~/.openclaw/agents/<agentId>/sessions/`。

## 高级说明

- 多代理路由可以为每个代理使用不同的工作区。参见
  [Channel routing](/concepts/channel-routing) 了解路由配置。
- 如果 `agents.defaults.sandbox` 已启用，非主会话可以使用 `agents.defaults.sandbox.workspaceRoot` 下的每个会话沙盒工作区。