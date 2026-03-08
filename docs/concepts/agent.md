---
summary: "Agent runtime (embedded pi-mono), workspace contract, and session bootstrap"
read_when:
  - Changing agent runtime, workspace bootstrap, or session behavior
title: "Agent Runtime"
---
# 代理运行时 🤖

OpenClaw 运行一个源自 **pi-mono** 的单一嵌入式代理运行时。

## 工作区（必需）

OpenClaw 使用单个代理工作区目录 (`agents.defaults.workspace`) 作为代理用于工具和上下文的 **唯一** 工作目录 (`cwd`)。

建议：如果缺失，使用 `openclaw setup` 创建 `~/.openclaw/openclaw.json` 并初始化工作区文件。

完整的工作区布局 + 备份指南：[代理工作区](/concepts/agent-workspace)

如果启用了 `agents.defaults.sandbox`，非主会话可以使用 `agents.defaults.sandbox.workspaceRoot` 下的每会话工作区来覆盖此设置（参见 [网关配置](/gateway/configuration)）。

## 引导文件（注入）

在 `agents.defaults.workspace` 内，OpenClaw 期望存在这些用户可编辑的文件：

- `AGENTS.md` — 操作指令 + “记忆”
- `SOUL.md` — 人设、边界、语气
- `TOOLS.md` — 用户维护的工具笔记（例如 `imsg`、`sag`、约定）
- `BOOTSTRAP.md` — 一次性首次运行仪式（完成后删除）
- `IDENTITY.md` — 代理名称/氛围/表情符号
- `USER.md` — 用户个人资料 + 首选地址

在新会话的第一轮，OpenClaw 将这些文件的内容直接注入到代理上下文中。

空白文件会被跳过。大文件会被修剪和截断并标记，以保持提示词精简（读取文件获取完整内容）。

如果文件缺失，OpenClaw 会注入单行“文件缺失”标记（并且 `openclaw setup` 将创建一个安全的默认模板）。

`BOOTSTRAP.md` 仅针对 **全新工作区** 创建（不存在其他引导文件）。如果在完成仪式后删除它，它在后续重启时不应被重新创建。

要完全禁用引导文件创建（针对预种子工作区），请设置：

```json5
{ agent: { skipBootstrap: true } }
```

## 内置工具

核心工具（read/exec/edit/write 及相关系统工具）始终可用，受工具策略约束。`apply_patch` 是可选的，并由 `tools.exec.applyPatch` 控制。`TOOLS.md` **不** 控制存在哪些工具；它是关于 _你_ 希望如何使用它们的指导。

## 技能

OpenClaw 从三个位置加载技能（名称冲突时工作区优先）：

- 捆绑（随安装附带）
- 托管/本地：`~/.openclaw/skills`
- 工作区：`<workspace>/skills`

技能可以通过配置/环境变量控制（参见 [网关配置](/gateway/configuration) 中的 `skills`）。

## pi-mono 集成

OpenClaw 复用了 pi-mono 代码库的部分内容（模型/工具），但 **会话管理、发现和工具连接归 OpenClaw 所有**。

- 无 pi-coding 代理运行时。
- 不会咨询 `~/.pi/agent` 或 `<workspace>/.pi` 设置。

## 会话

会话记录以 JSONL 格式存储在：

- `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`

会话 ID 是稳定的，由 OpenClaw 选择。
遗留的 Pi/Tau 会话文件夹 **不** 被读取。

## 流式传输时的控制

当队列模式为 `steer` 时，传入消息会被注入到当前运行中。
队列在 **每次工具调用后** 检查；如果存在 queued 消息，当前助手消息的剩余工具调用将被跳过（错误工具结果为 "Skipped due to queued user message."），然后 queued 用户消息在下一个助手响应之前注入。

当队列模式为 `followup` 或 `collect` 时，传入消息会被保留直到当前轮次结束，然后新的代理轮次将使用 queued 负载开始。参见 [队列](/concepts/queue) 了解模式 + 防抖/上限行为。

块流式传输在完成后立即发送完成的助手块；默认情况下 **关闭** (`agents.defaults.blockStreamingDefault: "off"`)。
通过 `agents.defaults.blockStreamingBreak` 调整边界（`text_end` 对比 `message_end`；默认为 text_end）。
使用 `agents.defaults.blockStreamingChunk` 控制软块分块（默认为 800–1200 字符；首选段落断点，然后是换行符；最后是句子）。
使用 `agents.defaults.blockStreamingCoalesce` 合并流式块以减少单行垃圾信息（发送前基于空闲的合并）。非 Telegram 渠道需要显式 `*.blockStreaming: true` 才能启用块回复。
详细的工具摘要在工具启动时发出（无防抖）；控制 UI 在可用时通过代理事件流式传输工具输出。
更多详情：[流式传输 + 分块](/concepts/streaming)。

## 模型引用

配置中的模型引用（例如 `agents.defaults.model` 和 `agents.defaults.models`）通过在 **第一个** `/` 处分割进行解析。

- 配置模型时使用 `provider/model`。
- 如果模型 ID 本身包含 `/`（OpenRouter 风格），请包含提供者前缀（例如：`openrouter/moonshotai/kimi-k2`）。
- 如果省略提供者，OpenClaw 将输入视为别名或 **默认提供者** 的模型（仅当模型 ID 中没有 `/` 时有效）。

## 配置（最小化）

至少设置：

- `agents.defaults.workspace`
- `channels.whatsapp.allowFrom`（强烈建议）

---

_下一步：[群聊](/channels/group-messages)_ 🦞