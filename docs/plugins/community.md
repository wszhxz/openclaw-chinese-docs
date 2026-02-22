---
summary: "Community plugins: quality bar, hosting requirements, and PR submission path"
read_when:
  - You want to publish a third-party OpenClaw plugin
  - You want to propose a plugin for docs listing
title: "Community plugins"
---
# 社区插件

此页面跟踪由社区维护的高质量**OpenClaw插件**。

当插件符合质量标准时，我们接受添加社区插件的PR。

## 列表要求

- 插件包已发布到npmjs（可通过`openclaw plugins install <npm-spec>`安装）。
- 源代码托管在GitHub上（公共仓库）。
- 仓库包含设置/使用文档和问题跟踪器。
- 插件有明确的维护信号（活跃的维护者、最近的更新或响应的问题处理）。

## 如何提交

通过以下内容打开一个PR，将您的插件添加到此页面：

- 插件名称
- npm包名称
- GitHub仓库URL
- 简短描述
- 安装命令

## 审查标准

我们更倾向于有用、有文档支持且安全可操作的插件。
低投入的包装器、所有权不明确或未维护的包可能会被拒绝。

## 候选格式

在添加条目时使用此格式：

- **插件名称** — 简短描述
  npm: `@scope/package`
  repo: `https://github.com/org/repo`
  install: `openclaw plugins install @scope/package`