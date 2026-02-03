---
summary: "OpenProse: .prose workflows, slash commands, and state in OpenClaw"
read_when:
  - You want to run or write .prose workflows
  - You want to enable the OpenProse plugin
  - You need to understand state storage
title: "OpenProse"
---
# OpenProse

OpenProse 是一种便携式、以 Markdown 为核心的 AI 会话工作流格式。在 OpenClaw 中，它作为插件提供，安装一个 OpenProse 技能包以及一个 `/prose` 命令。程序存储在 `.prose` 文件中，并且可以显式控制流程生成多个子代理。

官方网站：https://www.prose.md

## 它能做什么

- 支持显式并行的多代理研究 + 综合。
- 可重复的审批安全工作流（代码审查、事件分类、内容管道）。
- 可复用的 `.prose` 程序，可在支持的代理运行时中运行。

## 安装 + 启用

捆绑的插件默认禁用。启用 OpenProse：

```bash
openclaw plugins enable open-prose
```

启用插件后重启网关。

开发/本地检查：`openclaw plugins install ./extensions/open-prose`

相关文档：[插件](/plugin)，[插件清单](/plugins/manifest)，[技能](/tools/skills)。

## 命令

OpenProse 注册 `/prose` 作为用户可调用的技能命令。它会路由到 OpenProse 虚拟机指令，并在内部使用 OpenClaw 工具。

常用命令：

```
/prose help
/prose run <file.prose>
/prose run <handle/slug>
/prose run <https://example.com/file.prose>
/prose compile <file.prose>
/prose examples
/prose update
```

## 示例：一个简单的 `.prose` 文件

```prose
# 使用两个并行运行的代理进行研究 + 综合。

输入主题: "我们应该研究什么？"

代理研究员:
  模型: sonnet
  提示: "你彻底研究并引用来源。"

代理撰写者:
  模型: opus
  提示: "你撰写简洁的摘要。"

并行:
  发现 = 会话: 研究员
    提示: "研究 {topic}。"
  草稿 = 会话: 撰写者
    提示: "总结 {topic}。"

会话 "将发现 + 草稿合并为最终答案。"
上下文: { 发现, 草稿 }
```

## 文件位置

OpenProse 在你的工作区中将状态存储在 `.prose/` 目录下：

```
.prose/
├── .env
├── runs/
│   └── {YYYYMMDD}-{HHMMSS}-{random}/
│       ├── program.prose
│       ├── state.md
│       ├── bindings/
│       └── agents/
└── agents/
```

用户级别的持久化代理位于：

```
~/.prose/agents/
```

## 状态模式

OpenProse 支持多种状态后端：

- **文件系统**（默认）：`.prose/runs/...`
- **上下文内**：临时，适用于小型程序
- **SQLite**（实验性）：需要 `sqlite3` 二进制文件
- **PostgreSQL**（实验性）：需要 `psql` 和连接字符串

注意事项：

- SQLite/PostgreSQL 是可选且实验性的。
- PostgreSQL 凭据会流入子代理日志；请使用专用的、权限最小的数据库。

## 远程程序

`/prose run <handle/slug>` 解析为 `https://p.prose.md/<handle>/<slug>`。
直接 URL 会按原样获取。此操作使用 `web_fetch` 工具（或 `exec` 用于 POST）。

## OpenClaw 运行时映射

OpenProse 程序映射到 OpenClaw 原语：

| OpenProse 概念         | OpenClaw 工具    |
| ------------------------- | ---------------- |
| 生成会话 / 任务工具 | `sessions_spawn` |
| 文件读写           | `read` / `write` |
| 网络获取                 | `web_fetch`      |

如果您的工具白名单阻止了这些工具，OpenProse 程序将失败。请参阅 [技能配置](/tools/skills-config)。

## 安全性 + 审批

将 `.prose` 文件视为代码。运行前进行审查。使用 OpenClaw 工具白名单和审批门控来控制副作用。

对于确定性、审批门控的工作流，请与 [Lobster](/tools/lobster) 进行比较。