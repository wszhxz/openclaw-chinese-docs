---
summary: "Agent runtime (embedded pi-mono), workspace contract, and session bootstrap"
read_when:
  - Changing agent runtime, workspace bootstrap, or session behavior
title: "Agent Runtime"
---
# 代理运行时 🤖

OpenClaw 运行一个基于 **pi-mono** 的嵌入式代理运行时。

## 工作区（必需）

OpenClaw 使用单个代理工作区目录 (`agents.defaults.workspace`) 作为代理的 **唯一** 工作目录 (`cwd`) 用于工具和上下文。

推荐：如果缺少 `openclaw setup`，使用 `~/.openclaw/openclaw.json` 创建并初始化工作区文件。

完整的工作区布局 + 备份指南：[代理工作区](/concepts/agent-workspace)

如果 `agents.defaults.sandbox` 启用，非主会话可以使用每个会话的工作区覆盖此设置，位于 `agents.defaults.sandbox.workspaceRoot` 下（参见 [网关配置](/gateway/configuration)）。

## 引导文件（注入）

在 `agents.defaults.workspace` 内，OpenClaw 期望这些用户可编辑的文件：

- `AGENTS.md` — 操作说明 + “记忆”
- `SOUL.md` — 角色设定、边界、语气
- `TOOLS.md` — 用户维护的工具笔记（例如 `imsg`，`sag`，约定）
- `BOOTSTRAP.md` — 一次性首次运行仪式（完成后删除）
- `IDENTITY.md` — 代理名称/氛围/表情符号
- `USER.md` — 用户资料 + 偏好地址

在新会话的第一轮中，OpenClaw 直接将这些文件的内容注入代理上下文中。

空白文件会被跳过。大文件会被截断并在末尾标记，以保持提示简洁（阅读文件获取完整内容）。

如果文件缺失，OpenClaw 注入一个“缺失文件”标记行（并且 `openclaw setup` 将创建一个安全的默认模板）。

`BOOTSTRAP.md` 仅在 **全新工作区**（没有其他引导文件存在）时创建。如果您在完成仪式后删除它，在后续重启中不应重新创建。

要完全禁用引导文件的创建（适用于预填充的工作区），设置：

```json5
{ agent: { skipBootstrap: true } }
```

## 内置工具

核心工具（读/执行/编辑/写入及相关系统工具）始终可用，受工具策略限制。`apply_patch` 是可选的，并由 `tools.exec.applyPatch` 控制。`TOOLS.md` 不控制哪些工具存在；它是您希望如何使用它们的指导。

## 技能

OpenClaw 从三个位置加载技能（工作区中的同名技能优先）：

- 内置（随安装提供）
- 管理/本地：`~/.openclaw/skills`
- 工作区：`<workspace>/skills`

技能可以通过配置/环境进行限制（参见 [网关配置](/gateway/configuration) 中的 `skills`）。

## pi-mono 集成

OpenClaw 重用了 pi-mono 代码库的部分（模型/工具），但 **会话管理、发现和工具连接由 OpenClaw 所有**。

- 没有 pi-coding 代理运行时。
- 不会查询 `~/.pi/agent` 或 `<workspace>/.pi` 设置。

## 会话

会话记录存储为 JSONL 格式于：

- `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`

会话 ID 是稳定的，由 OpenClaw 选择。
旧版 Pi/Tau 会话文件夹 **不会** 被读取。

## 流式传输时的控制

当队列模式为 `steer` 时，传入的消息被注入到当前运行中。
队列在每次工具调用 **之后** 检查；如果有排队消息存在，
则跳过当前助手消息中的剩余工具调用（错误工具结果显示为“由于排队用户消息而跳过。”），然后在下一个助手响应之前注入排队的用户消息。

当队列模式为 `followup` 或 `collect` 时，传入的消息会被保留直到当前回合结束，然后使用排队的有效负载启动新的代理回合。参见 [队列](/concepts/queue) 获取模式 + 去抖/容量行为。

块流式传输会在完成助手块后立即发送；默认情况下是关闭的 (`agents.defaults.blockStreamingDefault: "off"`)。
通过 `agents.defaults.blockStreamingBreak` 调整边界 (`text_end` 对比 `message_end`；默认为 text_end)。
使用 `agents.defaults.blockStreamingChunk` 控制软块分块（默认为 800–1200 字符；偏好段落换行，然后换行符；句子最后）。
使用 `agents.defaults.blockStreamingCoalesce` 合并流式传输的块以减少单行垃圾信息（基于空闲状态合并前发送）。非 Telegram 渠道需要显式启用 `*.blockStreaming: true` 以启用块回复。
工具开始时发出详细的工具摘要（无去抖）；当可用时，UI 通过代理事件流式传输工具输出。
更多详情：[流式传输 + 分块](/concepts/streaming)。

## 模型引用

配置中的模型引用（例如 `agents.defaults.model` 和 `agents.defaults.models`）通过在 **第一个** `/` 处拆分来解析。

- 在配置模型时使用 `provider/model`。
- 如果模型 ID 本身包含 `/`（OpenRouter 风格），包括提供商前缀（示例：`openrouter/moonshotai/kimi-k2`）。
- 如果省略提供商，OpenClaw 将输入视为别名或默认提供商的模型（仅在模型 ID 中没有 `/` 时有效）。

## 配置（最小）

至少设置：

- `agents.defaults.workspace`
- `channels.whatsapp.allowFrom`（强烈建议）

---

_接下来：[群聊](/concepts/group-messages)_ 🦞