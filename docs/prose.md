---
summary: "OpenProse: .prose workflows, slash commands, and state in OpenClaw"
read_when:
  - You want to run or write .prose workflows
  - You want to enable the OpenProse plugin
  - You need to understand state storage
title: "OpenProse"
---
# OpenProse

OpenProse 是一种便携的、以 Markdown 为中心的工作流格式，用于编排 AI 会话。在 OpenClaw 中，它作为插件提供，安装一个 OpenProse 技能包以及一个 `/prose` 斜杠命令。程序存储在 `.prose` 文件中，并可以生成多个子代理，具有明确的控制流。

官方网站: https://www.prose.md

## 它能做什么

- 显式并行的多代理研究与综合。
- 可重复的安全审批工作流（代码审查、事件分类、内容管道）。
- 可重用的 `.prose` 程序，可以在支持的代理运行时中运行。

## 安装 + 启用

捆绑的插件默认处于禁用状态。启用 OpenProse：

```bash
openclaw plugins enable open-prose
```

启用插件后重启网关。

开发/本地检出：`openclaw plugins install ./extensions/open-prose`

相关文档：[Plugins](/plugin)，[Plugin manifest](/plugins/manifest)，[Skills](/tools/skills)。

## 斜杠命令

OpenProse 注册 `/prose` 为用户可调用的技能命令。它路由到 OpenProse VM 指令，并在内部使用 OpenClaw 工具。

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
# Research + synthesis with two agents running in parallel.

input topic: "What should we research?"

agent researcher:
  model: sonnet
  prompt: "You research thoroughly and cite sources."

agent writer:
  model: opus
  prompt: "You write a concise summary."

parallel:
  findings = session: researcher
    prompt: "Research {topic}."
  draft = session: writer
    prompt: "Summarize {topic}."

session "Merge the findings + draft into a final answer."
context: { findings, draft }
```

## 文件位置

OpenProse 在您的工作区下的 `.prose/` 中保持状态：

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

用户级持久代理位于：

```
~/.prose/agents/
```

## 状态模式

OpenProse 支持多种状态后端：

- **filesystem**（默认）：`.prose/runs/...`
- **in-context**：临时的，适用于小型程序
- **sqlite**（实验性）：需要 `sqlite3` 二进制文件
- **postgres**（实验性）：需要 `psql` 和连接字符串

注意事项：

- sqlite/postgres 是可选且实验性的。
- postgres 凭据会流入子代理日志；使用专用的最低权限数据库。

## 远程程序

`/prose run <handle/slug>` 解析为 `https://p.prose.md/<handle>/<slug>`。
直接 URL 将按原样获取。这使用了 `web_fetch` 工具（或 `exec` 用于 POST）。

## OpenClaw 运行时映射

OpenProse 程序映射到 OpenClaw 原语：

| OpenProse 概念         | OpenClaw 工具    |
| ------------------------- | ---------------- |
| 生成会话 / 任务工具 | `sessions_spawn` |
| 文件读写           | `read` / `write` |
| 网络获取                 | `web_fetch`      |

如果您的工具白名单阻止了这些工具，OpenProse 程序将失败。参见 [Skills 配置](/tools/skills-config)。

## 安全性 + 批准

像对待代码一样处理 `.prose` 文件。运行前进行审查。使用 OpenClaw 工具白名单和批准门来控制副作用。

对于确定性和批准门控制的工作流，请参考 [Lobster](/tools/lobster)。