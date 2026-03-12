---
summary: "Agent workspace: location, layout, and backup strategy"
read_when:
  - You need to explain the agent workspace or its file layout
  - You want to back up or migrate an agent workspace
title: "Agent Workspace"
---
# 代理工作区

工作区是代理的“家”。它是文件工具和工作区上下文所使用的唯一工作目录。请将其设为私有，并视其为记忆。

这与 `~/.openclaw/` 是分离的，后者用于存储配置、凭据和会话。

**重要提示：** 工作区是 **默认当前工作目录（cwd）**，而非强制沙箱。工具将相对路径解析为相对于工作区的路径，但绝对路径仍可能访问主机上的其他位置（除非启用了沙箱功能）。如需隔离，请使用[`agents.defaults.sandbox`](/gateway/sandboxing)（和/或按代理配置沙箱）。当启用沙箱且 `workspaceAccess` 不等于 `"rw"` 时，工具将在 `~/.openclaw/sandboxes` 下的沙箱工作区内运行，而非您的主机工作区。

## 默认位置

- 默认值：`~/.openclaw/workspace`  
- 若设置了 `OPENCLAW_PROFILE` 且其值不为 `"default"`，则默认值变为 `~/.openclaw/workspace-<profile>`。  
- 可在 `~/.openclaw/openclaw.json` 中覆盖：

```json5
{
  agent: {
    workspace: "~/.openclaw/workspace",
  },
}
```

`openclaw onboard`、`openclaw configure` 或 `openclaw setup` 将在缺失时自动创建工作区并填充引导文件。  
沙箱种子拷贝仅接受常规的工作区内文件；指向源工作区外部的符号链接/硬链接别名将被忽略。

若您已自行管理工作区文件，可禁用引导文件的自动创建：

```json5
{ agent: { skipBootstrap: true } }
```

## 额外的工作区文件夹

旧版本安装可能创建了 `~/openclaw`。保留多个工作区目录可能导致身份验证混乱或状态漂移，因为同一时间仅有一个工作区处于激活状态。

**建议：** 仅保留一个活跃工作区。若不再使用额外文件夹，请将其归档或移至回收站（例如 `trash ~/openclaw`）。若您有意保留多个工作区，请确保 `agents.defaults.workspace` 指向当前活跃的那个。

`openclaw doctor` 在检测到额外工作区目录时会发出警告。

## 工作区文件映射（各文件含义）

以下是 OpenClaw 在工作区内预期的标准文件：

- `AGENTS.md`  
  - 代理的操作指令及其内存使用方式说明。  
  - 每次会话启动时加载。  
  - 适合存放规则、优先级及“行为规范”等细节。

- `SOUL.md`  
  - 人格设定、语气风格与行为边界。  
  - 每次会话均加载。

- `USER.md`  
  - 用户身份信息及称呼方式。  
  - 每次会话均加载。

- `IDENTITY.md`  
  - 代理的名称、气质与表情符号。  
  - 在引导仪式期间创建/更新。

- `TOOLS.md`  
  - 关于本地工具与约定的备注。  
  - 不控制工具可用性；仅为指导性内容。

- `HEARTBEAT.md`（可选）  
  - 心跳运行所需的简短检查清单。  
  - 请保持简洁，避免消耗过多 token。

- `BOOT.md`（可选）  
  - 网关重启时执行的可选启动检查清单（需启用内部钩子）。  
  - 请保持简洁；对外发送消息请使用 message 工具。

- `BOOTSTRAP.md`  
  - 一次性首次运行仪式。  
  - 仅针对全新工作区创建。  
  - 完成仪式后即可删除。

- `memory/YYYY-MM-DD.md`  
  - 日度记忆日志（每日一个文件）。  
  - 建议在会话启动时读取当日及昨日的日志。

- `MEMORY.md`（可选）  
  - 精心整理的长期记忆。  
  - 仅应在主会话（非共享/群组上下文）中加载。

详见 [Memory](/concepts/memory) 了解工作流及自动记忆清理机制。

- `skills/`（可选）  
  - 工作区专属技能。  
  - 当名称冲突时，将覆盖托管/预置技能。

- `canvas/`（可选）  
  - Canvas UI 节点显示所用文件（例如 `canvas/index.html`）。

若任一引导文件缺失，OpenClaw 将在会话中注入“文件缺失”标记并继续运行。大体积引导文件在注入时会被截断；可通过 `agents.defaults.bootstrapMaxChars`（默认值：20000）和 `agents.defaults.bootstrapTotalMaxChars`（默认值：150000）调整限制。  
`openclaw setup` 可在不覆盖现有文件的前提下重建缺失的默认文件。

## 工作区中 *不包含* 的内容

以下内容位于 `~/.openclaw/` 下，**不应**提交至工作区代码仓库：

- `~/.openclaw/openclaw.json`（配置）  
- `~/.openclaw/credentials/`（OAuth tokens、API keys）  
- `~/.openclaw/agents/<agentId>/sessions/`（会话记录 + 元数据）  
- `~/.openclaw/skills/`（托管技能）

如需迁移会话或配置，请单独复制，并确保其不纳入版本控制。

## Git 备份（推荐，私有）

请将工作区视为私有记忆。将其放入一个 **私有** Git 仓库，以实现备份与恢复。

请在网关运行的机器上执行以下步骤（即工作区所在机器）。

### 1）初始化仓库

若已安装 git，全新工作区将自动初始化。若当前工作区尚未成为仓库，请运行：

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md SOUL.md TOOLS.md IDENTITY.md USER.md HEARTBEAT.md memory/
git commit -m "Add agent workspace"
```

### 2）添加私有远程仓库（新手友好选项）

选项 A：GitHub 网页界面  

1. 在 GitHub 上新建一个 **私有** 仓库。  
2. 不要使用 README 初始化（避免合并冲突）。  
3. 复制 HTTPS 远程 URL。  
4. 添加远程仓库并推送：

```bash
git branch -M main
git remote add origin <https-url>
git push -u origin main
```

选项 B：GitHub CLI（`gh`）

```bash
gh auth login
gh repo create openclaw-workspace --private --source . --remote origin --push
```

选项 C：GitLab 网页界面  

1. 在 GitLab 上新建一个 **私有** 仓库。  
2. 不要使用 README 初始化（避免合并冲突）。  
3. 复制 HTTPS 远程 URL。  
4. 添加远程仓库并推送：

```bash
git branch -M main
git remote add origin <https-url>
git push -u origin main
```

### 3）持续更新

```bash
git status
git add .
git commit -m "Update memory"
git push
```

## 切勿提交密钥

即使在私有仓库中，也请避免在工作区中存储密钥：

- API 密钥、OAuth tokens、密码或私有凭据。  
- 所有位于 `~/.openclaw/` 下的内容。  
- 聊天原始转录或敏感附件的完整副本。

若必须存储敏感引用项，请使用占位符，并将真实密钥保存在其他安全位置（密码管理器、环境变量或 `~/.openclaw/`）。

推荐的 `.gitignore` 初始模板：

```gitignore
.DS_Store
.env
**/*.key
**/*.pem
**/secrets*
```

## 将工作区迁移至新机器

1. 将仓库克隆至目标路径（默认为 `~/.openclaw/workspace`）。  
2. 在 `~/.openclaw/openclaw.json` 中将 `agents.defaults.workspace` 设置为该路径。  
3. 运行 `openclaw setup --workspace <path>` 以填充任何缺失的文件。  
4. 若需迁移会话，请单独从旧机器复制 `~/.openclaw/agents/<agentId>/sessions/`。

## 高级说明

- 多代理路由可为每个代理指定不同工作区。参阅 [Channel routing](/channels/channel-routing) 了解路由配置。  
- 若启用了 `agents.defaults.sandbox`，非主会话可使用位于 `agents.defaults.sandbox.workspaceRoot` 下的每会话沙箱工作区。