---
summary: "OpenProse: .prose workflows, slash commands, and state in OpenClaw"
read_when:
  - You want to run or write .prose workflows
  - You want to enable the OpenProse plugin
  - You need to understand state storage
title: "OpenProse"
---
# OpenProse

OpenProse 是一种便携式的、以 Markdown 优先的工作流格式，用于编排 AI 会话。在 OpenClaw 中，它作为插件提供，安装后会附带一个 OpenProse 技能包以及一个 `/prose` 斜杠命令。程序存储在 `.prose` 文件中，并可以生成多个具有显式控制流的子智能体。

官方网站：[https://www.prose.md](https://www.prose.md)

## 它能做什么

- 多智能体研究与综合，支持显式并行。
- 可重复的审批安全工作流（代码审查、事件分类、内容流水线）。
- 可复用的 `.prose` 程序，可在支持的智能体运行时环境中运行。

## 安装与启用

捆绑插件默认禁用。启用 OpenProse：

```bash
openclaw plugins enable open-prose
```

启用插件后重启网关。

开发/本地检出：`openclaw plugins install ./path/to/local/open-prose-plugin`

相关文档：[插件](/tools/plugin)、[插件清单](/plugins/manifest)、[技能](/tools/skills)。

## 斜杠命令

OpenProse 将 `/prose` 注册为用户可调用的技能命令。它将路由到 OpenProse VM 指令，并在底层使用 OpenClaw 工具。

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

OpenProse 在工作区下的 `.prose/` 中保存状态：

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

用户级持久化智能体位于：

```
~/.prose/agents/
```

## 状态模式

OpenProse 支持多种状态后端：

- **文件系统**（默认）：`.prose/runs/...`
- **上下文内**：临时性，适用于小型程序
- **sqlite**（实验性）：需要 `sqlite3` 二进制文件
- **postgres**（实验性）：需要 `psql` 和连接字符串

注意：

- sqlite/postgres 为可选且实验性功能。
- postgres 凭据会流入子智能体日志；请使用专用的、权限最小的数据库。

## 远程程序

`/prose run <handle/slug>` 解析为 `https://p.prose.md/<handle>/<slug>`。
直接 URL 按原样获取。这使用了 `web_fetch` 工具（POST 请求则使用 `exec`）。

## OpenClaw 运行时映射

OpenProse 程序映射到 OpenClaw 原语：

| OpenProse 概念         | OpenClaw 工具    |
| ------------------------- | ---------------- |
| 启动会话 / 任务工具 | `sessions_spawn` |
| 文件读写           | `read` / `write` |
| Web 获取                 | `web_fetch`      |

如果您的工具白名单阻止了这些工具，OpenProse 程序将会失败。请参阅 [技能配置](/tools/skills-config)。

## 安全与审批

将 `.prose` 文件视为代码。运行前请审查。使用 OpenClaw 工具白名单和审批门禁来控制副作用。

对于确定性、审批门禁的工作流，请参考 [Lobster](/tools/lobster)。