---
summary: "OpenProse: .prose workflows, slash commands, and state in OpenClaw"
read_when:
  - You want to run or write .prose workflows
  - You want to enable the OpenProse plugin
  - You need to understand state storage
title: "OpenProse"
---
# OpenProse

OpenProse 是一种可移植的、以 Markdown 为优先的流程格式，用于编排 AI 会话。在 OpenClaw 中，它以插件形式提供，安装一个 OpenProse 技能包以及一个 ``/prose`` 斜杠命令。程序存放在 ``.prose`` 文件中，并可生成多个子智能体，具备显式的控制流。

官方网站：[https://www.prose.md](https://www.prose.md)

## 它能做什么

- 具备显式并行能力的多智能体研究与综合。
- 可重复、审批安全的工作流（代码审查、事件初步分诊、内容流水线）。
- 可复用的 ``.prose`` 程序，可在所有受支持的智能体运行时中执行。

## 安装与启用

捆绑插件默认处于禁用状态。启用 OpenProse：

````bash
openclaw plugins enable open-prose
````

启用插件后，请重启 Gateway。

开发/本地检出路径：``openclaw plugins install ./extensions/open-prose``

相关文档：[插件](/tools/plugin)、[插件清单](/plugins/manifest)、[技能](/tools/skills)。

## 斜杠命令

OpenProse 将 ``/prose`` 注册为用户可调用的技能命令。该命令路由至 OpenProse 虚拟机指令，并在底层使用 OpenClaw 工具。

常用命令：

````
/prose help
/prose run <file.prose>
/prose run <handle/slug>
/prose run <https://example.com/file.prose>
/prose compile <file.prose>
/prose examples
/prose update
````

## 示例：一个简单的 ``.prose`` 文件

````prose
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
````

## 文件位置

OpenProse 在工作区中的 ``.prose/`` 下维护其状态：

````
.prose/
├── .env
├── runs/
│   └── {YYYYMMDD}-{HHMMSS}-{random}/
│       ├── program.prose
│       ├── state.md
│       ├── bindings/
│       └── agents/
└── agents/
````

用户级持久化智能体存放于：

````
~/.prose/agents/
````

## 状态模式

OpenProse 支持多种状态后端：

- **filesystem**（默认）：``.prose/runs/...``
- **in-context**：临时性，适用于小型程序
- **sqlite**（实验性）：需 ``sqlite3`` 二进制文件
- **postgres**（实验性）：需 ``psql`` 及连接字符串

注意事项：

- sqlite / postgres 为可选功能，且处于实验阶段。
- postgres 凭据将流入子智能体日志；请使用专用的、最小权限数据库。

## 远程程序

``/prose run <handle/slug>`` 解析为 ``https://p.prose.md/<handle>/<slug>``。  
直接 URL 将原样获取。此过程使用 ``web_fetch`` 工具（或对 POST 请求使用 ``exec``）。

## OpenClaw 运行时映射

OpenProse 程序映射到 OpenClaw 原语：

| OpenProse 概念         | OpenClaw 工具    |
| ------------------------- | ---------------- |
| 启动会话 / 任务工具 | ``sessions_spawn`` |
| 文件读写           | ``read`` / ``write`` |
| Web 获取                 | ``web_fetch``      |

若您的工具白名单屏蔽了上述工具，则 OpenProse 程序将失败。参见 [技能配置](/tools/skills-config)。

## 安全性与审批

请将 ``.prose`` 文件视同代码对待；运行前务必审阅。利用 OpenClaw 工具白名单和审批门控机制来管控副作用。

如需确定性、经审批门控的工作流，请对比 [Lobster](/tools/lobster)。