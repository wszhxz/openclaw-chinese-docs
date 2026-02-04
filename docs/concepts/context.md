---
summary: "Context: what the model sees, how it is built, and how to inspect it"
read_when:
  - You want to understand what “context” means in OpenClaw
  - You are debugging why the model “knows” something (or forgot it)
  - You want to reduce context overhead (/context, /status, /compact)
title: "Context"
---
# 上下文

“上下文”是 **OpenClaw 在一次运行中发送给模型的所有内容**。它受到模型的 **上下文窗口**（令牌限制）的约束。

初学者思维模型：

- **系统提示**（由 OpenClaw 构建）：规则、工具、技能列表、时间和运行时，以及注入的工作区文件。
- **对话历史**：本会话中的您的消息 + 助手的消息。
- **工具调用/结果 + 附件**：命令输出、文件读取、图像/音频等。

上下文 _不是_ “记忆”：记忆可以存储在磁盘上并在稍后重新加载；上下文是模型当前窗口内的内容。

## 快速入门（检查上下文）

- `/status` → 快速查看“我的窗口有多满？”+ 会话设置。
- `/context list` → 注入的内容 + 大致大小（按文件 + 总计）。
- `/context detail` → 更深入的细分：按文件、按工具模式大小、按技能条目大小和系统提示大小。
- `/usage tokens` → 将每回复使用情况附加到正常回复的底部。
- `/compact` → 将较旧的历史总结为一个紧凑的条目以释放窗口空间。

另见：[斜杠命令](/tools/slash-commands)，[令牌使用及费用](/token-use)，[压缩](/concepts/compaction)。

## 示例输出

值因模型、提供商、工具策略以及工作区中的内容而异。

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

## 计入上下文窗口的内容

模型接收到的所有内容都计入，包括：

- 系统提示（所有部分）。
- 对话历史。
- 工具调用 + 工具结果。
- 附件/记录（图像/音频/文件）。
- 压缩摘要和修剪工件。
- 提供商“包装器”或隐藏标头（不可见，但仍计入）。

## OpenClaw 如何构建系统提示

系统提示是 **OpenClaw 所有** 并在每次运行时重建。它包括：

- 工具列表 + 简短描述。
- 技能列表（仅元数据；见下文）。
- 工作区位置。
- 时间（UTC + 配置的用户时间）。
- 运行时元数据（主机/操作系统/模型/思考）。
- 在 **项目上下文** 下注入的工作区引导文件。

详细信息：[系统提示](/concepts/system-prompt)。

## 注入的工作区文件（项目上下文）

默认情况下，OpenClaw 注入一组固定的工作区文件（如果存在）：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（仅首次运行）

大文件按文件截断使用 `agents.defaults.bootstrapMaxChars`（默认 `20000` 字符）。`/context` 显示 **原始 vs 注入** 大小以及是否发生截断。

## 技能：注入的内容 vs 按需加载

系统提示包含一个紧凑的 **技能列表**（名称 + 描述 + 位置）。此列表具有实际开销。

技能指令 _不_ 默认包含。模型预期仅在需要时 `read` 技能的 `SKILL.md` **说明**。

## 工具：有两个成本

工具以两种方式影响上下文：

1. **系统提示中的工具列表文本**（您看到的“工具”）。
2. **工具模式**（JSON）。这些发送给模型以便它可以调用工具。即使您没有看到它们作为纯文本，它们也计入上下文。

`/context detail` 细分最大的工具模式，以便您可以看到哪些占主导地位。

## 命令、指令和“内联快捷方式”

斜杠命令由网关处理。有几种不同的行为：

- **独立命令**：仅包含 `/...` 的消息作为命令运行。
- **指令**：`/think`，`/verbose`，`/reasoning`，`/elevated`，`/model`，`/queue` 在模型看到消息之前被剥离。
  - 仅指令的消息保留会话设置。
  - 正常消息中的内联指令作为每消息提示。
- **内联快捷方式**（仅限白名单发送者）：正常消息中的某些 `/...` 标记可以立即运行（示例：“嘿 /status”），并在模型看到剩余文本之前被剥离。

详情：[斜杠命令](/tools/slash-commands)。

## 会话、压缩和修剪（持久化的内容）

消息之间持久化的内容取决于机制：

- **正常历史** 在会话记录中持久化，直到根据策略压缩/修剪。
- **压缩** 在记录中持久化一个摘要并保留最近的消息。
- **修剪** 从运行的 _内存中_ 提示中移除旧的工具结果，但不会重写记录。

文档：[会话](/concepts/session)，[压缩](/concepts/compaction)，[会话修剪](/concepts/session-pruning)。

## `/context` 实际报告的内容

`/context` 优先使用可用的最新 **运行生成** 的系统提示报告：

- `System prompt (run)` = 从最后一个嵌入（工具功能）运行捕获并保留在会话存储中。
- `System prompt (estimate)` = 当没有运行报告存在时（或通过不生成报告的 CLI 后端运行时）实时计算。

无论哪种方式，它都会报告大小和主要贡献者；它 **不** 转储完整的系统提示或工具模式。