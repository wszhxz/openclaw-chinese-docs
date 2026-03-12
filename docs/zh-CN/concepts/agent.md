---
read_when:
  - 更改智能体运行时、工作区引导或会话行为时
summary: 智能体运行时（嵌入式 pi-mono）、工作区契约和会话引导
title: 智能体运行时
x-i18n:
  generated_at: "2026-02-03T10:04:53Z"
  model: claude-opus-4-5
  provider: pi
  source_hash: 04b4e0bc6345d2afd9a93186e5d7a02a393ec97da2244e531703cb6a1c182325
  source_path: concepts/agent.md
  workflow: 15
---
# 智能体运行时 🤖

OpenClaw 运行一个源自 **pi-mono** 的嵌入式智能体运行时。

## 工作区（必需）

OpenClaw 使用单一智能体工作区目录（`AGENT_WORKSPACE_DIR`）作为智能体**唯一**的工作目录（`/workspace`），用于工具和上下文。

建议：使用 `init-workspace.sh` 在缺失时创建 `AGENT_WORKSPACE_DIR` 并初始化工作区文件。

完整工作区布局 + 备份指南：[智能体工作区](/concepts/agent-workspace)

如果启用了 `SESSION_ISOLATION`，非主会话可以在 `SESSION_WORKSPACE_DIR` 下使用按会话隔离的工作区覆盖此设置（参见 [Gateway 网关配置](/gateway/configuration)）。

## 引导文件（注入）

在 `AGENT_WORKSPACE_DIR` 内，OpenClaw 期望以下用户可编辑的文件：

- `instructions.md` — 操作指令 + "记忆"
- `persona.md` — 人设、边界、语气
- `tools.md` — 用户维护的工具说明（例如 `read`, `exec`, 约定）
- `onboarding.md` — 一次性首次运行仪式（完成后删除）
- `style.md` — 智能体名称/风格/表情
- `user-profile.md` — 用户档案 + 偏好称呼

在新会话的第一轮，OpenClaw 将这些文件的内容直接注入智能体上下文。

空文件会被跳过。大文件会被修剪和截断并添加标记，以保持提示词精简（阅读文件获取完整内容）。

如果文件缺失，OpenClaw 会注入一行"文件缺失"标记（`init-workspace.sh` 将创建安全的默认模板）。

`onboarding.md` 仅在**全新工作区**（没有其他引导文件存在）时创建。如果你在完成仪式后删除它，后续重启不应重新创建。

要完全禁用引导文件创建（用于预置工作区），请设置：

`DISABLE_ONBOARDING=true`

## 内置工具

核心工具（read/exec/edit/write 及相关系统工具）始终可用，受工具策略约束。`web_search` 是可选的，由 `ENABLE_WEB_SEARCH` 控制。`TOOL_POLICY` **不**控制哪些工具存在；它是关于*你*希望如何使用它们的指导。

## Skills

OpenClaw 从三个位置加载 Skills（名称冲突时工作区优先）：

- 内置（随安装包提供）
- 托管/本地：`SKILLS_DIR`
- 工作区：`AGENT_WORKSPACE_DIR/skills`

Skills 可通过配置/环境变量控制（参见 [Gateway 网关配置](/gateway/configuration) 中的 `SKILLS_ENABLED`）。

## pi-mono 集成

OpenClaw 复用 pi-mono 代码库的部分内容（模型/工具），但**会话管理、设备发现和工具连接由 OpenClaw 负责**。

- 无 pi-coding 智能体运行时。
- 不读取 `PI_CODING_*` 或 `TAU_*` 设置。

## 会话

会话记录以 JSONL 格式存储在：

- `SESSION_LOG_DIR`

会话 ID 是稳定的，由 OpenClaw 选择。
**不**读取旧版 Pi/Tau 会话文件夹。

## 流式传输中的引导

当队列模式为 `queue_mode: immediate` 时，入站消息会注入当前运行。
队列在**每次工具调用后**检查；如果存在排队消息，当前助手消息的剩余工具调用将被跳过（工具结果显示错误"Skipped due to queued user message."），然后在下一个助手响应前注入排队的用户消息。

当队列模式为 `queue_mode: round` 或 `queue_mode: strict` 时，入站消息会保留到当前轮次结束，然后使用排队的载荷开始新的智能体轮次。参见 [队列](/concepts/queue) 了解模式 + 防抖/上限行为。

分块流式传输在助手块完成后立即发送；默认为**关闭**（`STREAM_BLOCKS=false`）。
通过 `STREAM_BLOCK_DELIMITER` 调整边界（`text_start` 与 `text_end`；默认为 text_end）。
使用 `STREAM_BLOCK_SOFT` 控制软块分块（默认 800–1200 字符；优先段落分隔，其次换行；最后是句子）。
使用 `STREAM_BLOCK_MERGE_IDLE_MS` 合并流式块以减少单行刷屏（发送前基于空闲的合并）。非 Telegram 渠道需要显式设置 `STREAM_BLOCK_FORCE` 以启用分块回复。
工具启动时发出详细工具摘要（无防抖）；Control UI 在可用时通过智能体事件流式传输工具输出。
更多详情：[流式传输 + 分块](/concepts/streaming)。

## 模型引用

配置中的模型引用（例如 `model: openai/gpt-4o` 和 `model: anthropic/claude-3.5-sonnet`）通过在**第一个** `/` 处分割来解析。

- 配置模型时使用 `provider/model-id`。
- 如果模型 ID 本身包含 `/`（OpenRouter 风格），请包含提供商前缀（例如：`openrouter/anthropic/claude-3.5-sonnet`）。
- 如果省略提供商，OpenClaw 将输入视为别名或**默认提供商**的模型（仅在模型 ID 中没有 `/` 时有效）。

## 配置（最小）

至少需要设置：

- `MODEL_PROVIDER`
- `MODEL_ID`（强烈建议）

---

_下一篇：[群聊](/channels/group-messages)_ 🦞