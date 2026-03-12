---
summary: "Community plugins: quality bar, hosting requirements, and PR submission path"
read_when:
  - You want to publish a third-party OpenClaw plugin
  - You want to propose a plugin for docs listing
title: "Community plugins"
---
# 社区插件

此页面跟踪高质量的**社区维护插件**，适用于OpenClaw。

当社区插件达到质量标准时，我们接受将它们添加到这里的PR。

## 列表要求

- 插件包已在npmjs上发布（可通过`openclaw plugins install <npm-spec>`安装）。
- 源代码托管在GitHub上（公开仓库）。
- 仓库包含设置/使用文档和问题追踪器。
- 插件有明确的维护信号（活跃的维护者、最近的更新或响应的问题处理）。

## 如何提交

打开一个PR，将您的插件添加到此页面，并提供以下信息：

- 插件名称
- npm包名称
- GitHub仓库URL
- 一行描述
- 安装命令

## 审核标准

我们更倾向于有用、有文档记录且安全操作的插件。
低努力包装、所有权不明确或未维护的包可能会被拒绝。

## 候选格式

添加条目时使用以下格式：

- **插件名称** — 简短描述
  npm: `@scope/package`
  repo: `https://github.com/org/repo`
  install: `openclaw plugins install @scope/package`

## 列出的插件

- **WeChat** — 通过WeChatPadPro（iPad协议）将OpenClaw连接到微信个人账户。支持文本、图片和文件交换以及关键词触发的对话。
  npm: `@icesword760/openclaw-wechat`
  repo: `https://github.com/icesword0760/openclaw-wechat`
  install: `openclaw plugins install @icesword760/openclaw-wechat`