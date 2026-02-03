---
summary: "Agent runtime (embedded pi-mono), workspace contract, and session bootstrap"
read_when:
  - Changing agent runtime, workspace bootstrap, or session behavior
title: "Agent Runtime"
---
# 代理运行时 🤖

OpenClaw 运行一个基于 **pi-mono** 的单个嵌入式代理运行时。

## 工作区（必需）

OpenClaw 使用一个代理工作目录（`agents.defaults.workspace`）作为代理的 **唯一** 工作目录（`cwd`）用于工具和上下文。

推荐：如果缺失则使用 `openclaw setup` 创建 `~/.openclaw/openclaw.json` 并初始化工作区文件。

完整工作区布局 + 备份指南：[代理工作区](/concepts/agent-workspace)

如果启用了 `agents.defaults.sandbox`，非主会话可通过 `agents.defaults.sandbox.workspaceRoot` 下的会话专属工作区覆盖此设置（参见 [网关配置](/gateway/configuration)）。

## 启动文件（注入）

在 `agents.defaults.workspace` 中，OpenClaw 预期这些用户可编辑的文件：

- `AGENTS.md` — 操作说明 + “记忆”
- `SOUL.md` — 人格、边界、语气
- `TOOLS.md` — 用户维护的工具说明（例如 `imsg`、`sag`、规范）
- `BOOTSTRAP.md` — 一次性首次运行仪式（完成删除）
- `IDENTITY.md` — 代理名称/风格/表情符号
- `USER.md` — 用户资料 + 预选地址

在新会话的首次轮询中，OpenCl,aw 会将这些文件内容直接注入代理上下文。

空白文件会被跳过。大文件会被截断并标记，以保持提示简洁（阅读文件获取完整内容）。

如果文件缺失，OpenClaw 会注入一条“缺失文件”标记行（`openclaw setup` 将创建安全默认模板）。

`BOOTSTRAP.md` 仅在 **全新工作区** 中创建（无其他启动文件）。若在完成仪式后删除它，后续重启不会重新创建。

要完全禁用启动文件创建（用于预填充的工作区），设置：

```json5
{ agent: { skipBootstrap: true } }
```

## 内置工具

核心工具（读/执行/编辑/写及相关系统工具）始终可用，受工具策略限制。`apply_patch` 是可选的，受 `tools.exec.applyPatch` 控制。`TOOLS.md` 并不控制哪些工具存在；它是你希望如何使用它们的指导。

## 技能

OpenClaw 从三个位置加载技能（工作区在名称冲突时优先）：

- 内置（随安装提供）
- 管理/本地：`~/.openclaw/skills`
- 工作区：`<workspace>/skills`

技能可通过配置/环境变量控制（参见 [网关配置](/gateway/configuration) 中的 `skills`）。

## pi-mono 集成

OpenClaw 重用了 pi-mono 代码库的部分（模型/工具），但 **会话管理、发现和工具绑定由 OpenClaw 独占**。

- 不使用 pi-coding 代理运行时。
- 不会参考 `~/.pi/agent` 或 `<workspace>/.pi` 设置。

## 会话

会话转录存储为 JSONL 于：

- `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`

会话 ID 稳定且由 OpenClaw 选择。
旧版 Pi/Tau 会话文件夹 **不会** 被读取。

## 流式传输时的控制

当队列模式为 `steer` 时，入站消息会注入当前运行。
每次工具调用后会检查队列；如果存在排队消息，则跳过当前助手消息的剩余工具调用（错误工具结果为“因排队用户消息跳过”），然后在下一个助手响应前注入排队用户消息。

当队列模式为 `followup` 或 `collect` 时，入站消息会保留至当前轮次结束，然后以排队负载启动新代理轮次。参见 [队列](/concepts/queue) 了解模式 + 去抖/上限行为。

块流式传输在完成助手块时立即发送；默认为 **关闭**（`agents.defaults.blockStreamingDefault: "off"`）。
通过 `agents.defaults.blockStreamingBreak` 调整边界（`text_end` vs `message_end`；默认为 `text_end`）。
通过 `agents.defaults.blockStreamingChunk` 控制软块分块（默认为 800–1200 字符；优先段落换行，再换行；最后句子）。
通过 `agents.defaults.blockStreamingCoalesce` 合并流式传输块以减少单行垃圾信息（发送前基于空闲合并）。非 Telegram 渠道需显式设置 `*.blockStreaming: true` 启用块回复。
工具开始时会输出详细工具摘要（无去抖）；当可用时，通过代理事件控制 UI 流式传输工具输出。
更多详情：[流式传输 + 分块](/concepts/streaming)。

## 模型引用

配置中的模型引用（例如 `agents.defaults.model` 和 `agents.defaults.models`）通过按 **第一个** `/` 分割解析。

- 配置模型时使用 `provider/model`。
- 如果模型 ID 本身包含 `/`（OpenRouter 风格），包含提供者前缀（示例：`openrouter/moonshotai/kimi-k2`）。
- 如果省略提供者，OpenClaw 将输入视为默认提供者的别名或模型（仅在模型 ID 中无 `/` 时有效）。

## 配置（最小）

至少设置：

- `agents.defaults.workspace`
- `channels.whatsapp.allowFrom`（强烈推荐）

---

_下一页：[群聊](/concepts/group-messages)_ 🦜