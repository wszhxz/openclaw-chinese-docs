---
summary: "ClawHub guide: public skills registry + CLI workflows"
read_when:
  - Introducing ClawHub to new users
  - Installing, searching, or publishing skills
  - Explaining ClawHub CLI flags and sync behavior
title: "ClawHub"
---
# ClawHub

ClawHub 是 **OpenClaw 的公共技能注册中心**。它是一个免费服务：所有技能都是公开的、开放的，并且对所有人可见，便于分享和复用。一个技能只是一个包含 `SKILL.md` 文件（加上支持性文本文件）的文件夹。您可以通过网页应用浏览技能，或使用 CLI 来搜索、安装、更新和发布技能。

网站：[clawhub.ai](https://clawhub.ai)

## ClawHub 是什么

- OpenClaw 技能的公共注册中心。
- 技能包和元数据的版本化存储库。
- 用于搜索、标签和使用信号的发现界面。

## 工作原理

1. 用户发布一个技能包（文件 + 元数据）。
2. ClawHub 存储该包，解析元数据，并分配版本。
3. 注册中心对技能进行索引，以便搜索和发现。
4. 用户在 OpenClaw 中浏览、下载并安装技能。

## 您可以做什么

- 发布新技能以及现有技能的新版本。
- 通过名称、标签或搜索发现技能。
- 下载技能包并检查其文件。
- 报告具有攻击性或不安全的技能。
- 如果您是管理员，可以隐藏、取消隐藏、删除或封禁。

## 适用对象（适合初学者）

如果您想为 OpenClaw 代理添加新功能，ClawHub 是查找和安装技能的最简单方式。您无需了解后端如何工作。您可以：

- 通过自然语言搜索技能。
- 将技能安装到您的工作区。
- 通过一条命令以后续更新技能。
- 通过发布自己的技能进行备份。

## 快速入门（非技术）

1. 安装 CLI（请参阅下一部分）。
2. 搜索您需要的内容：
   - `clawhub search "calendar"`
3. 安装一个技能：
   - `clawhub install <skill-slug>`
4. 启动一个新的 OpenClaw 会话，以便它能够使用新技能。

## 安装 CLI

选择一个：

```bash
npm i -g clawhub
```

```bash
pnpm add -g clawhub
```

## ClawHub 在 OpenClaw 中的作用

默认情况下，CLI 会将技能安装到当前工作目录下的 `./skills` 中。如果配置了 OpenClaw 工作区，`clawhub` 将回退到该工作区，除非您覆盖 `--workdir`（或 `CLAWHUB_WORKDIR`）。OpenClaw 会从 `<workspace>/skills` 加载工作区技能，并在 **下一次** 会话中使用它们。如果您已经使用 `~/.openclaw/skills` 或捆绑技能，工作区技能将优先。

有关技能如何加载、共享和受保护的更多详细信息，请参阅
[Skills](/tools/skills)。

## 技能系统概述

一个技能是一个版本化的文件包，它教会 OpenClaw 如何执行特定任务。每次发布都会创建一个新版本，注册中心会保留版本历史记录，以便用户审核更改。

一个典型的技能包括：

- 一个 `SKILL.md` 文件，包含主要描述和用法。
- 可选的配置文件、脚本或支持文件。
- 元数据，如标签、摘要和安装要求。

ClawHub 使用元数据来驱动发现并安全地暴露技能功能。注册中心还跟踪使用信号（如星标和下载量），以改进排名和可见性。

## 服务提供的功能（特性）

- **公开浏览**技能及其 `SKILL.md` 内容。
- **基于嵌入的搜索**（向量搜索），而不仅仅是关键词。
- **版本控制**，使用语义版本、变更日志和标签（包括 `latest`）。
- **按版本下载**为 zip 文件。
- **星标和评论**以获取社区反馈。
- **审核**钩子用于审批和审计。
- **CLI 友好的 API**用于自动化和脚本。

## 安全性和审核

ClawHub 默认是开放的。任何人都可以上传技能，但必须拥有至少一周历史的 GitHub 账户才能发布。这有助于减缓滥用，而不会阻止合法贡献者。

报告和审核：

- 任何登录用户都可以报告一个技能。
- 报告原因必须提供并记录。
- 每个用户每次最多可以有 20 个活跃报告。
- 有超过 3 个唯一报告的技能默认会自动隐藏。
- 管理员可以查看隐藏的技能，取消隐藏、删除它们或封禁用户。
- 滥用报告功能可能导致账户被封禁。

有兴趣成为管理员吗？在 OpenClaw Discord 中提问并联系管理员或维护者。

## CLI 命令和参数

全局选项（适用于所有命令）：

- `--workdir <dir>`：工作目录（默认：当前目录；回退到 OpenClaw 工作区）。
- `--dir <dir>`：技能目录，相对于工作目录（默认：`skills`）。
- `--site <url>`：网站基础 URL（浏览器登录）。
- `--registry <url>`：注册中心 API 基础 URL。
- `--no-input`：禁用提示（非交互式）。
- `-V, --cli-version`：打印 CLI 版本。

认证：

- `clawhub login`（浏览器流程）或 `clawhub login --token <token>`
- `clawhub logout`
- `clawhub whoami`

选项：

- `--token <token>`：粘贴 API 令牌。
- `--label <label>`：用于浏览器登录令牌的标签（默认：`CLI token`）。
- `--no-browser`：不打开浏览器（需要 `--token`）。

搜索：

- `clawhub search "query"`
- `--limit <n>`：最大结果数。

安装：

- `clawhub install <slug>`
- `--version <version>`：安装特定版本。
- `--force`：如果文件夹已存在则覆盖。

更新：

- `clawhub update <slug>`
- `clawhub update --all`
- `--version <version>`：更新到特定版本（仅单个 slug）。
- `--force`：如果本地文件与任何已发布版本不匹配时覆盖。

列出：

- `clawhub list`（读取 `SKILL.md` 文件）

## 什么是技能

- 一个技能是一个版本化的文件包，它教会 OpenClaw 如何执行特定任务。每次发布都会创建一个新版本，注册中心