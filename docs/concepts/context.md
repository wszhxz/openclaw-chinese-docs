---
summary: "Context: what the model sees, how it is built, and how to inspect it"
read_when:
  - You want to understand what “context” means in OpenClaw
  - You are debugging why the model “knows” something (or forgot it)
  - You want to reduce context overhead (/context, /status, /compact)
title: "Context"
---
# 上下文（Context）

“上下文”是 **OpenClaw 每次运行时发送给模型的全部内容**。它受限于模型的 **上下文窗口**（即 token 数量限制）。

初学者心智模型：

- **系统提示（System prompt）**（由 OpenClaw 构建）：包含规则、工具列表、技能列表、时间/运行时信息，以及注入的工作区文件。
- **对话历史**：您与助手在本次会话中的全部消息。
- **工具调用/结果 + 附件**：命令输出、文件读取内容、图像/音频等。

上下文 **不等于** “记忆”：记忆可存储在磁盘上并后续重新加载；而上下文仅指模型当前窗口中所包含的内容。

## 快速入门（检查上下文）

- `/status` → 快速查看“我的窗口已使用多少？”及会话设置。
- `/context list` → 查看已注入内容及其粗略大小（按文件分别统计 + 总计）。
- `/context detail` → 更深入的细分：按文件、按工具 schema、按技能条目、以及系统提示本身的大小。
- `/usage tokens` → 在常规回复末尾附加每次回复的用量统计脚注。
- `/compact` → 将较早的历史压缩为紧凑条目，以释放窗口空间。

另请参阅：[斜杠命令（Slash commands）](/tools/slash-commands)、[Token 使用与费用](/reference/token-use)、[压缩（Compaction）](/concepts/compaction)。

## 示例输出

具体数值因模型、提供商、工具策略及您工作区中的内容而异。

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

模型接收到的所有内容均计入上下文窗口，包括：

- 系统提示（所有部分）。
- 对话历史。
- 工具调用 + 工具执行结果。
- 附件/转录文本（图像/音频/文件）。
- 压缩摘要与剪枝产物（pruning artifacts）。
- 提供商的“包装器”或隐藏头部（不可见，但仍会计入）。

## OpenClaw 如何构建系统提示

系统提示由 **OpenClaw 全权管理**，且每次运行时都会重建。其内容包括：

- 工具列表 + 简短描述。
- 技能列表（仅含元数据；详见下文）。
- 工作区位置。
- 时间（UTC 时间 + 若已配置则转换为用户本地时间）。
- 运行时元数据（主机/操作系统/模型/推理模式等）。
- 在 **项目上下文（Project Context）** 下注入的工作区引导文件。

完整拆解详见：[系统提示（System Prompt）](/concepts/system-prompt)。

## 注入的工作区文件（项目上下文）

默认情况下，OpenClaw 会注入一组固定的工作区文件（若存在）：

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（仅首次运行时注入）

大文件将按单个文件进行截断，截断策略为 `agents.defaults.bootstrapMaxChars`（默认为 `20000` 个字符）。此外，OpenClaw 还对所有引导文件的总注入量设定了上限，即 `agents.defaults.bootstrapTotalMaxChars`（默认为 `150000` 个字符）。`/context` 显示了各文件的 **原始大小 vs 实际注入大小**，并标明是否发生了截断。

当发生截断时，运行时可在“项目上下文”下注入一个内嵌警告块。可通过 `agents.defaults.bootstrapPromptTruncationWarning` 配置该行为（支持选项：`off`、`once`、`always`；默认为 `once`）。

## 技能：哪些被注入，哪些按需加载

系统提示中包含一份精简的 **技能列表**（含名称、描述和位置）。该列表本身具有真实开销。

技能的具体指令 **默认不包含在内**。模型仅在 **实际需要时** 才应通过 `read` 加载对应技能的 `SKILL.md`。

## 工具：存在两种开销

工具对上下文的影响体现在两个方面：

1. 系统提示中的 **工具列表文本**（即您所见的“Tooling”部分）。
2. **工具 Schema（JSON 格式）**：这些 Schema 会被发送给模型，以便其调用工具。尽管您无法在纯文本中直接看到它们，但它们仍计入上下文。

`/context detail` 将列出体积最大的工具 Schema，助您识别主要开销来源。

## 命令、指令与“内联快捷方式”

斜杠命令由网关（Gateway）处理，其行为分为以下几类：

- **独立命令（Standalone commands）**：仅含 `/...` 的消息将作为命令执行。
- **指令（Directives）**：`/think`、`/verbose`、`/reasoning`、`/elevated`、`/model`、`/queue` 会在模型接收消息前被移除。
  - 仅含指令的消息会持久化会话设置。
  - 在普通消息中内联使用的指令，则作为该条消息的临时提示。
- **内联快捷方式（Inline shortcuts）**（仅限白名单发送者）：某些 `/...` 令牌若出现在普通消息中，可立即触发执行（例如：“hey /status”），并在模型接收剩余文本前被移除。

详情请参阅：[斜杠命令（Slash commands）](/tools/slash-commands)。

## 会话、压缩与剪枝（哪些内容会持续保留）

不同机制下，跨消息持续保留的内容也不同：

- **常规历史记录** 保留在会话转录中，直至按策略被压缩或剪枝。
- **压缩（Compaction）** 将摘要写入转录，并保持最近的消息不变。
- **剪枝（Pruning）** 从当前运行的 **内存中上下文** 中移除旧的工具结果，但 **不会重写转录内容**。

相关文档：[会话（Session）](/concepts/session)、[压缩（Compaction）](/concepts/compaction)、[会话剪枝（Session pruning）](/concepts/session-pruning)。

默认情况下，OpenClaw 使用内置的 `legacy` 上下文引擎来完成上下文组装与压缩。若您安装了一个提供 `kind: "context-engine"` 的插件，并通过 `plugins.slots.contextEngine` 选择启用它，则 OpenClaw 将把上下文组装、`/compact` 及相关子代理上下文生命周期钩子交由该引擎处理。

## `/context` 实际报告的内容

`/context` 在可用时优先采用最新的 **运行时生成（run-built）** 系统提示报告：

- `System prompt (run)` = 从上一次嵌入式（具备工具能力）运行中捕获，并持久化保存在会话存储中。
- `System prompt (estimate)` = 当不存在运行报告（或通过不生成该报告的 CLI 后端运行）时，实时动态计算得出。

无论哪种方式，它都仅报告大小及主要贡献项；**不会** 输出完整的系统提示或工具 Schema。