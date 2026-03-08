---
summary: "Context: what the model sees, how it is built, and how to inspect it"
read_when:
  - You want to understand what “context” means in OpenClaw
  - You are debugging why the model “knows” something (or forgot it)
  - You want to reduce context overhead (/context, /status, /compact)
title: "Context"
---
# 上下文

"Context"（上下文）是 **OpenClaw 在一次运行中发送给模型的所有内容**。它受模型的 **上下文窗口**（Token 限制）限制。

初学者思维模型：

- **系统提示词**（OpenClaw 构建）：规则、工具、技能列表、时间/运行时，以及注入的工作区文件。
- **对话历史**：你的消息 + 此会话中 assistant 的消息。
- **工具调用/结果 + 附件**：命令输出、文件读取、图像/音频等。

上下文 _与_ "memory"（记忆）_不同_：记忆可以存储在磁盘上并在以后重新加载；上下文是模型当前窗口内的内容。

## 快速开始（检查上下文）

- `/status` → 快速查看“我的窗口有多满？” + 会话设置。
- `/context list` → 注入了什么 + 大致大小（每文件 + 总计）。
- `/context detail` → 更深入的分解：每文件、每工具 schema 大小、每技能条目大小，以及系统提示词大小。
- `/usage tokens` → 将每次回复的使用情况 footer 附加到正常回复中。
- `/compact` → 将较旧的历史记录总结为紧凑条目以释放窗口空间。

另见：[斜杠命令](/tools/slash-commands)，[Token 使用与成本](/reference/token-use)，[压缩](/concepts/compaction)。

## 示例输出

值因模型、提供商、工具策略和工作区内容而异。

### `/context list`

```
🧠 Context breakdown
Workspace: <workspaceDir>
Bootstrap max/file: 20,000 chars
Sandbox: mode=non-main sandboxed=false
System prompt (run): 38,412 chars (~9,603 tok) (Project Context 23,901 chars (~5,976 tok))

Injected workspace files:
- AGENTS.md: OK | raw 1,742 chars (~436 tok) | injected 1,742 chars (~436 tok)
- SOUL.md: OK | raw 912 chars (~228 tok) | injected 912 chars (~228 tok)
- TOOLS.md: TRUNCATED | raw 54,210 chars (~13,553 tok) | injected 20,962 chars (~5,241 tok)
- IDENTITY.md: OK | raw 211 chars (~53 tok) | injected 211 chars (~53 tok)
- USER.md: OK | raw 388 chars (~97 tok) | injected 388 chars (~97 tok)
- HEARTBEAT.md: MISSING | raw 0 | injected 0
- BOOTSTRAP.md: OK | raw 0 chars (~0 tok) | injected 0 chars (~0 tok)

Skills list (system prompt text): 2,184 chars (~546 tok) (12 skills)
Tools: read, edit, write, exec, process, browser, message, sessions_send, …
Tool list (system prompt text): 1,032 chars (~258 tok)
Tool schemas (JSON): 31,988 chars (~7,997 tok) (counts toward context; not shown as text)
Tools: (same as above)

Session tokens (cached): 14,250 total / ctx=32,000
```

### `/context detail`

```
🧠 Context breakdown (detailed)
…
Top skills (prompt entry size):
- frontend-design: 412 chars (~103 tok)
- oracle: 401 chars (~101 tok)
… (+10 more skills)

Top tools (schema size):
- browser: 9,812 chars (~2,453 tok)
- exec: 6,240 chars (~1,560 tok)
… (+N more tools)
```

## 什么计入上下文窗口

模型接收的所有内容都计入，包括：

- 系统提示词（所有部分）。
- 对话历史。
- 工具调用 + 工具结果。
- 附件/转录（图像/音频/文件）。
- 压缩总结和修剪产物。
- 提供商"wrappers"或隐藏 headers（不可见，但仍计入）。

## OpenClaw 如何构建系统提示词

系统提示词由 **OpenClaw 拥有** 并在每次运行时重建。它包括：

- 工具列表 + 简短描述。
- 技能列表（仅元数据；见下文）。
- 工作区位置。
- 时间（UTC + 转换后的用户时间，如果已配置）。
- 运行时元数据（host/OS/model/thinking）。
- **项目上下文** 下注入的工作区 bootstrap 文件。

完整分解：[系统提示词](/concepts/system-prompt)。

## 注入的工作区文件（项目上下文）

默认情况下，OpenClaw 注入一组固定的工作区文件（如果存在）：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（仅首次运行）

大文件使用 `agents.defaults.bootstrapMaxChars` 按文件截断（默认 `20000` 字符）。OpenClaw 还通过 `agents.defaults.bootstrapTotalMaxChars` 对所有文件执行总的 bootstrap 注入上限（默认 `150000` 字符）。`/context` 显示 **原始 vs 注入** 大小以及是否发生了截断。

当发生截断时，运行时可以在项目上下文下注入一个 prompt 内警告块。使用 `agents.defaults.bootstrapPromptTruncationWarning` 配置此项（`off`, `once`, `always`; 默认 `once`）。

## 技能：注入的内容 vs 按需加载的内容

系统提示词包含一个紧凑的 **技能列表**（名称 + 描述 + 位置）。此列表有实际的开销。

技能说明默认 _不_ 包含在内。模型被期望 **仅在需要时** `read` 技能的 `SKILL.md`。

## 工具：有两种成本

工具通过两种方式影响上下文：

1. 系统提示词中的 **工具列表文本**（你看到的"Tooling"）。
2. **工具 schemas**（JSON）。这些发送给模型以便它可以调用工具。即使你没有将它们视为纯文本，它们也计入上下文。

`/context detail` 分解最大的工具 schemas，以便你可以看到什么占主导地位。

## 命令、指令和“内联快捷方式”

斜杠命令由 Gateway 处理。有几种不同的行为：

- **独立命令**：仅是 `/...` 的消息作为命令运行。
- **指令**：`/think`, `/verbose`, `/reasoning`, `/elevated`, `/model`, `/queue` 在模型看到消息之前被剥离。
  - 仅指令的消息持久化会话设置。
  - 正常消息中的内联指令充当每条消息的提示。
- **内联快捷方式**（仅限允许列表中的发送者）：正常消息中的某些 `/...` tokens 可以立即运行（例如："hey /status"），并在模型看到剩余文本之前被剥离。

详情：[斜杠命令](/tools/slash-commands)。

## 会话、压缩和修剪（什么持久化）

跨消息持久化的内容取决于机制：

- **正常历史** 持久化在会话转录中，直到被策略压缩/修剪。
- **压缩** 将总结持久化到转录中，并保持最近消息完整。
- **修剪** 从运行的 _内存中_ 提示词中移除旧工具结果，但不重写转录。

文档：[会话](/concepts/session)，[压缩](/concepts/compaction)，[会话修剪](/concepts/session-pruning)。

默认情况下，OpenClaw 使用内置的 `legacy` 上下文引擎进行组装和压缩。如果你安装了一个提供 `kind: "context-engine"` 的插件并使用 `plugins.slots.contextEngine` 选择它，OpenClaw 会将上下文组装、`/compact` 和相关子代理上下文生命周期钩子委托给该引擎。

## `/context` 实际报告的内容

`/context` 优先使用最新的 **运行构建** 系统提示词报告（如果可用）：

- `System prompt (run)` = 从上次嵌入式（工具能力）运行中捕获并持久化在会话存储中。
- `System prompt (estimate)` = 当不存在运行报告时（或通过不生成报告的 CLI 后端运行时）即时计算。

无论哪种方式，它都报告大小和主要贡献者；它 **不** 转储完整的系统提示词或工具 schemas。