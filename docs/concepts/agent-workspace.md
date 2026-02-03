---
summary: "Agent workspace: location, layout, and backup strategy"
read_when:
  - You need to explain the agent workspace or its file layout
  - You want to back up or migrate an agent workspace
title: "Agent Workspace"
---
# 代理工作区

工作区是代理的家。它是用于文件工具和工作区上下文的唯一工作目录。请保持其私密性，并将其视为内存。

这与 `~/.openclaw/` 是分开的，后者存储配置、凭证和会话信息。

**重要：** 工作区是 **默认当前工作目录 (cwd)**，而不是严格的沙箱环境。工具会将相对路径解析为工作区，但绝对路径仍可访问主机上的其他位置，除非启用了沙箱功能。如果需要隔离，使用 [`agents.defaults.sandbox`](/gateway/sandboxing)（以及/或每个代理的沙箱配置）。当启用了沙箱且 `workspaceAccess` 不是 `"rw"` 时，工具会在 `~/.openclaw/sandboxes` 下的沙箱工作区中运行，而不是您的主机工作区。

## 默认位置

- 默认位置：`~/.openclaw/workspace`
- 如果设置了 `OPENCLAW_PROFILE` 且不等于 `"default"`，默认位置变为 `~/.openclaw/workspace-<profile>`。
- 在 `~/.openclaw/openclaw.json` 中覆盖：

```json5
{
  agent: {
    workspace: "~/.openclaw/workspace",
  },
}
```

`openclaw onboard`、`openclaw configure` 或 `openclaw setup` 会创建工作区并生成引导文件（如果缺失）。

如果您自行管理工作区文件，可以禁用引导文件的创建：

```json5
{ agent: { skipBootstrap: true } }
```

## 额外的工作区文件夹

旧版本安装可能创建了 `~/openclaw`。保留多个工作区目录可能导致身份验证或状态漂移的混淆，因为一次只能有一个工作区处于活动状态。

**建议：** 保持单一的活动工作区。如果您不再使用额外的文件夹，请归档或移动到废纸篓（例如 `trash ~/openclaw`）。如果您有意保留多个工作区，请确保 `agents.defaults.workspace` 指向当前活动的工作区。

`openclaw doctor` 会在检测到额外的工作区目录时发出警告。

## 工作区文件映射（每个文件的含义）

这些是 OpenClaw 预期在工作区中的标准文件：

- `AGENTS.md`
  - 代理的操作指南以及如何使用内存。
  - 每个会话开始时加载。
  - 规则、优先级和“如何行为”的好地方。

- `SOUL.md`
  - 个性、语气和边界。
  - 每个会话加载。

- `USER.md`
  - 用户是谁以及如何称呼他们。
  - 每个会话加载。

- `IDENTITY.md`
  - 代理的名称、氛围和表情符号。
  - 在引导仪式中创建/更新。

- `TOOLS.md`
  - 关于本地工具和惯例的说明。
  - 不控制工具可用性；仅作为指导。

- `HEARTBEAT.md`
  - 可选的小型心跳运行检查清单。
  - 保持简短以避免消耗令牌。

- `BOOT.md`
  - 可选的启动检查清单，在网关重启且内部钩子启用时执行。
  - 保持简短；使用消息工具进行出站发送。

- `BOOTSTRAP.md`
  - 一次性首次运行仪式。
  - 仅在全新的工作区中创建。
  - 仪式完成后删除该文件。

- `memory/YYYY-MM-DD.md`
  - 每日记忆日志（每天一个文件）。
  - 建议在会话开始时阅读今天和昨天的内容。

- `MEMORY.md`（可选）
  - 精选的长期记忆。
  - 仅在主、私有会话中加载（不包括共享/组上下文）。

有关工作流程和自动内存刷新，请参见 [Memory](/concepts/memory)。

- `skills/`（可选）
  - 工作区特定的技能。
  - 当名称冲突时，覆盖管理/捆绑的技能。

- `canvas/`（可选）
  - 节点显示的画布 UI 文件（例如 `canvas/index.html`）。

如果缺少任何引导文件，OpenClaw 会在会话中注入“缺失文件”标记并继续。注入时大型引导文件会被截断；通过 `agents.defaults.bootstrapMaxChars` 调整限制（默认值：20000）。`openclaw setup` 可以在不覆盖现有文件的情况下重新创建缺失的默认值。

## 工作区中不包含的内容

这些文件位于 `~/.openclaw/` 下，不应提交到工作区仓库：

- `~/.openclaw/openclaw.json`（配置）
- `~/.openclaw/credentials/`（OAuth 令牌、API 密钥）
- `~/.openclaw/agents/<agentId>/sessions/`（会话记录 + 元数据）
- `~/.openclaw/skills/`（管理的技能）

如果您需要迁移会话或配置，请分别复制它们并确保它们不在版本控制中。

## Git 备份（推荐，私有）

将工作区视为私有内存。将其放入一个 **私有** 的 Git 仓库中，以便备份和恢复。

在网关运行的机器上运行以下步骤（即工作区所在的位置）。

### 1) 初始化仓库

如果安装了 Git，新工作区会自动初始化。如果此工作区尚未是仓库，请运行：

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md SOUL.md TOOLS.md IDENTITY.md USER.md HEARTBEAT.md memory/
git commit -m "添加代理工作区"
```

### 2) 添加私有远程仓库（适合初学者的选项）

选项 A：GitHub 网站界面

1. 在 GitHub 上创建一个新的 **私有** 仓库。
2. 不使用 README 初始化（避免合并冲突）。
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

选项 C：GitLab 网站界面

1. 在 GitLab 上创建一个新的 **私有** 仓库。
2. 不使用 README 初始化（避免合并冲突）。
3. 复制 HTTPS 远程 URL。
4