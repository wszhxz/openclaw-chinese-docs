---
summary: "ClawHub guide: public skills registry + CLI workflows"
read_when:
  - Introducing ClawHub to new users
  - Installing, searching, or publishing skills
  - Explaining ClawHub CLI flags and sync behavior
title: "ClawHub"
---
# ClawHub

ClawHub 是 **OpenClaw 的公共技能注册表**。它是一个免费服务：所有技能都是公开、开放的，并且对所有人可见，以便共享和重用。一个技能只是一个包含 `SKILL.md` 文件（加上支持文本文件）的文件夹。您可以在网页应用中浏览技能，或使用 CLI 搜索、安装、更新和发布技能。

网站: [clawhub.ai](https://clawhub.ai)

## ClawHub 是什么

- OpenClaw 技能的公共注册表。
- 版本化的技能包和元数据存储。
- 用于搜索、标签和使用信号的发现界面。

## 工作原理

1. 用户发布一个技能包（文件 + 元数据）。
2. ClawHub 存储该包，解析元数据并分配版本。
3. 注册表为搜索和发现索引该技能。
4. 用户浏览、下载并在 OpenClaw 中安装技能。

## 您可以做什么

- 发布新技能和现有技能的新版本。
- 通过名称、标签或搜索发现技能。
- 下载技能包并检查其文件。
- 报告滥用或不安全的技能。
- 如果您是管理员，可以隐藏、取消隐藏、删除或封禁技能。

## 适用对象（适合初学者）

如果您想为您的 OpenClaw 代理添加新功能，ClawHub 是查找和安装技能的最简单方法。您不需要了解后端的工作原理。您可以：

- 用自然语言搜索技能。
- 将技能安装到您的工作区。
- 使用一条命令稍后更新技能。
- 通过发布它们来备份您自己的技能。

## 快速开始（非技术）

1. 安装 CLI（请参阅下一节）。
2. 搜索您需要的内容：
   - `clawhub search "calendar"`
3. 安装一个技能：
   - `clawhub install <skill-slug>`
4. 启动一个新的 OpenClaw 会话，以便它加载新的技能。

## 安装 CLI

选择一个：

```bash
npm i -g clawhub
```

```bash
pnpm add -g clawhub
```

## 如何与 OpenClaw 集成

默认情况下，CLI 会将技能安装到当前工作目录下的 `./skills`。如果配置了 OpenClaw 工作区，除非您覆盖 `--workdir`（或 `CLAWHUB_WORKDIR`），否则 `clawhub` 会回退到该工作区。OpenClaw 从 `<workspace>/skills` 加载工作区技能，并将在 **下一个** 会话中拾取这些技能。如果您已经使用 `~/.openclaw/skills` 或捆绑技能，工作区技能将优先。

有关技能如何加载、共享和控制的更多详细信息，请参阅
[Skills](/tools/skills)。

## 技能系统概述

技能是一组版本化的文件，教 OpenClaw 如何执行特定任务。每次发布都会创建一个新版本，注册表会保留版本历史记录，以便用户可以审核更改。

典型的技能包括：

- 一个带有主要描述和用法的 `SKILL.md` 文件。
- 技能使用的可选配置、脚本或支持文件。
- 元数据，如标签、摘要和安装要求。

ClawHub 使用元数据来支持发现并安全地暴露技能能力。注册表还跟踪使用信号（如星标和下载量）以改进排名和可见性。

## 服务提供的内容（功能）

- 技能及其 `SKILL.md` 内容的 **公共浏览**。
- 由嵌入（向量搜索）驱动的 **搜索**，而不仅仅是关键词。
- 带有 semver、变更日志和标签（包括 `latest`）的 **版本控制**。
- 按版本下载为 zip 文件。
- 用于社区反馈的 **星标和评论**。
- 用于审批和审核的 **管理** 钩子。
- 用于自动化和脚本的 **CLI 友好 API**。

## 安全性和管理

ClawHub 默认是开放的。任何人都可以上传技能，但发布时 GitHub 账户必须至少有一周的历史。这有助于减缓滥用行为，而不阻止合法贡献者。

报告和管理：

- 任何登录用户都可以报告一个技能。
- 报告原因必须提供并记录。
- 每个用户一次最多可以有 20 个活跃报告。
- 超过 3 个唯一报告的技能默认自动隐藏。
- 管理员可以查看隐藏的技能，取消隐藏、删除或封禁用户。
- 滥用报告功能可能导致账户被封禁。

有兴趣成为管理员？请在 OpenClaw Discord 中询问并与管理员或维护者联系。

## CLI 命令和参数

全局选项（适用于所有命令）：

- `--workdir <dir>`: 工作目录（默认：当前目录；回退到 OpenClaw 工作区）。
- `--dir <dir>`: 技能目录，相对于工作目录（默认：`skills`）。
- `--site <url>`: 站点基础 URL（浏览器登录）。
- `--registry <url>`: 注册表 API 基础 URL。
- `--no-input`: 禁用提示（非交互式）。
- `-V, --cli-version`: 打印 CLI 版本。

认证：

- `clawhub login`（浏览器流程）或 `clawhub login --token <token>`
- `clawhub logout`
- `clawhub whoami`

选项：

- `--token <token>`: 粘贴 API 令牌。
- `--label <label>`: 用于浏览器登录令牌的存储标签（默认：`CLI token`）。
- `--no-browser`: 不打开浏览器（需要 `--token`）。

搜索：

- `clawhub search "query"`
- `--limit <n>`: 最大结果数。

安装：

- `clawhub install <slug>`
- `--version <version>`: 安装特定版本。
- `--force`: 如果文件夹已存在则覆盖。

更新：

- `clawhub update <slug>`
- `clawhub update --all`
- `--version <version>`: 更新到特定版本（仅单个 slug）。
- `--force`: 当本地文件与任何已发布的版本不匹配时覆盖。

列表：

- `clawhub list`（读取 `.clawhub/lock.json`）

发布：

- `clawhub publish <path>`
- `--slug <slug>`: 技能 slug。
- `--name <name>`: 显示名称。
- `--version <version>`: Semver 版本。
- `--changelog <text>`: 变更日志文本（可以为空）。
- `--tags <tags>`: 逗号分隔的标签（默认：`latest`）。

删除/恢复（仅限所有者/管理员）：

- `clawhub delete <slug> --yes`
- `clawhub undelete <slug> --yes`

同步（扫描本地技能 + 发布新/更新的）：

- `clawhub sync`
- `--root <dir...>`: 额外的扫描根目录。
- `--all`: 无需提示上传所有内容。
- `--dry-run`: 显示将要上传的内容。
- `--bump <type>`: `patch|minor|major` 用于更新（默认：`patch`）。
- `--changelog <text>`: 非交互式更新的变更日志。
- `--tags <tags>`: 逗号分隔的标签（默认：`latest`）。
- `--concurrency <n>`: 注册表检查（默认：4）。

## 代理的常见工作流程

### 搜索技能

```bash
clawhub search "postgres backups"
```

### 下载新技能

```bash
clawhub install my-skill-pack
```

### 更新已安装的技能

```bash
clawhub update --all
```

### 备份您的技能（发布或同步）

对于单个技能文件夹：

```bash
clawhub publish ./my-skill --slug my-skill --name "My Skill" --version 1.0.0 --tags latest
```

一次性扫描并备份多个技能：

```bash
clawhub sync --all
```

## 高级细节（技术）

### 版本控制和标签

- 每次发布都会创建一个新的 **semver** `SkillVersion`。
- 标签（如 `latest`）指向一个版本；移动标签可以让您回滚。
- 变更日志附加在每个版本上，在同步或发布更新时可以为空。

### 本地更改与注册表版本

更新时，CLI 会比较本地技能内容与注册表版本的内容哈希。如果本地文件与任何已发布的版本不匹配，CLI 会在覆盖前询问（或在非交互运行中需要 `--force`）。

### 同步扫描和回退根目录

`clawhub sync` 首先扫描您的当前工作目录。如果没有找到技能，它会回退到已知的旧位置（例如 `~/openclaw/skills` 和 `~/.openclaw/skills`）。这是为了在没有额外标志的情况下找到旧的技能安装。

### 存储和锁文件

- 安装的技能记录在工作目录下的 `.clawhub/lock.json` 中。
- 认证令牌存储在 ClawHub CLI 配置文件中（可以通过 `CLAWHUB_CONFIG_PATH` 覆盖）。

### 遥测（安装计数）

当您在登录状态下运行 `clawhub sync` 时，CLI 会发送一个最小快照以计算安装计数。您可以完全禁用此功能：

```bash
export CLAWHUB_DISABLE_TELEMETRY=1
```

## 环境变量

- `CLAWHUB_SITE`: 覆盖站点 URL。
- `CLAWHUB_REGISTRY`: 覆盖注册表 API URL。
- `CLAWHUB_CONFIG_PATH`: 覆盖 CLI 存储令牌/配置的位置。
- `CLAWHUB_WORKDIR`: 覆盖默认工作目录。
- `CLAWHUB_DISABLE_TELEMETRY=1`: 在 `sync` 上禁用遥测。