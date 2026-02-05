---
summary: "OpenProse: .prose workflows, slash commands, and state in OpenClaw"
read_when:
  - You want to run or write .prose workflows
  - You want to enable the OpenProse plugin
  - You need to understand state storage
title: "OpenProse"
---
# OpenProse

OpenProse 是一种便携式的、以 markdown 为优先的 AI 会话编排工作流格式。在 OpenClaw 中它作为插件提供，安装 OpenProse 技能包以及一个 `/prose` 斜杠命令。程序存在于 `.prose` 文件中，可以生成多个具有显式控制流的子代理。

官方网站：https://www.prose.md

## 功能特性

- 具有显式并行性的多代理研究 + 综合。
- 可重复的审批安全工作流（代码审查、事件分类、内容管道）。
- 可重用的 `.prose` 程序，可在支持的代理运行时中运行。

## 安装 + 启用

捆绑插件默认处于禁用状态。启用 OpenProse：

```bash
openclaw plugins enable open-prose
```

启用插件后重启网关。

开发/本地检出：`openclaw plugins install ./extensions/open-prose`

相关文档：[插件](/plugin)，[插件清单](/plugins/manifest)，[技能](/tools/skills)。

## 斜杠命令

OpenProse 注册了 `/prose` 作为用户可调用的技能命令。它路由到 OpenProse VM 指令并在底层使用 OpenClaw 工具。

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

## 示例：简单的 `.prose` 文件

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

OpenProse 在工作区中的 `.prose/` 下保存状态：

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
- **in-context**：临时的，用于小型程序
- **sqlite**（实验性）：需要 `sqlite3` 二进制文件
- **postgres**（实验性）：需要 `psql` 和连接字符串

注意事项：

- sqlite/postgres 为可选功能且处于实验阶段。
- postgres 凭据会流入子代理日志；使用专用的最低权限数据库。

## 远程程序

`/prose run <handle/slug>` 解析为 `https://p.prose.md/<handle>/<slug>`。
直接 URL 按原样获取。这使用 `web_fetch` 工具（或 `exec` 用于 POST）。

## OpenClaw 运行时映射

OpenProse 程序映射到 OpenClaw 原语：

| OpenProse 概念            | OpenClaw 工具    |
| ------------------------- | ---------------- |
| Spawn session / Task 工具 | `sessions_spawn` |
| 文件读写                  | `read` / `write` |
| 网络获取                  | `web_fetch`      |

如果您的工具白名单阻止了这些工具，OpenProse 程序将失败。参见 [技能配置](/tools/skills-config)。

## 安全 + 审批

将 `.prose` 文件视为代码。运行前进行审查。使用 OpenClaw 工具白名单和审批门控来控制副作用。

对于确定性的、审批门控的工作流，请与 [Lobster](/tools/lobster) 进行比较。