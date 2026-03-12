---
summary: "Agent runtime (embedded pi-mono), workspace contract, and session bootstrap"
read_when:
  - Changing agent runtime, workspace bootstrap, or session behavior
title: "Agent Runtime"
---
# 代理运行时 🤖

OpenClaw 运行一个源自 **pi-mono** 的嵌入式代理运行时（单实例）。

## 工作区（必需）

OpenClaw 使用单一代理工作区目录（`agents.defaults.workspace`）作为代理的**唯一**工作目录（`cwd`），供工具和上下文使用。

建议：若该目录缺失，使用 `openclaw setup` 创建 `~/.openclaw/openclaw.json` 并初始化工作区文件。

完整工作区结构 + 备份指南：[代理工作区](/concepts/agent-workspace)

若启用了 `agents.defaults.sandbox`，非主会话可通过位于 `agents.defaults.sandbox.workspaceRoot` 下的每会话工作区覆盖此设置（参见  
[网关配置](/gateway/configuration)）。

## 引导文件（自动注入）

在 `agents.defaults.workspace` 内，OpenClaw 期望以下用户可编辑文件：

- `AGENTS.md` — 运行指令 + “记忆”
- `SOUL.md` — 人格设定、行为边界、语气风格
- `TOOLS.md` — 用户维护的工具说明（例如 `imsg`、`sag`、约定规范）
- `BOOTSTRAP.md` — 一次性首次运行仪式脚本（执行完毕后即被删除）
- `IDENTITY.md` — 代理名称 / 氛围 / 表情符号
- `USER.md` — 用户档案 + 偏好称呼方式

在新会话的首轮交互中，OpenClaw 将这些文件的内容直接注入代理上下文。

空文件将被跳过。大文件会被裁剪并截断，同时添加标记以确保提示词保持精简（如需查看完整内容，请直接读取对应文件）。

若某文件缺失，OpenClaw 将注入一行“缺失文件”标记（且 `openclaw setup` 将生成一个安全的默认模板）。

`BOOTSTRAP.md` 仅在**全新工作区**（无其他引导文件存在时）创建。若您在完成仪式后将其删除，则后续重启时不应再次生成。

如需完全禁用引导文件的自动创建（适用于预填充工作区），请设置：

```json5
{ agent: { skipBootstrap: true } }
```

## 内置工具

核心工具（读取 / 执行 / 编辑 / 写入及相关系统工具）始终可用，前提是符合工具策略。  
`apply_patch` 为可选功能，受 `tools.exec.applyPatch` 控制。  
`TOOLS.md` **不**控制哪些工具实际存在；它仅用于指导**您**希望如何使用这些工具。

## 技能（Skills）

OpenClaw 从三个位置加载技能（同名冲突时，工作区优先）：

- 内置技能（随安装包一同分发）
- 受管 / 本地技能：`~/.openclaw/skills`
- 工作区技能：`<workspace>/skills`

技能可通过配置 / 环境变量进行启用或禁用（参见 [网关配置](/gateway/configuration) 中的 `skills`）。

## pi-mono 集成

OpenClaw 复用部分 pi-mono 代码库（模型 / 工具），但**会话管理、能力发现及工具连接均由 OpenClaw 自主实现**。

- 不使用 pi-coding 代理运行时。
- 不读取 `~/.pi/agent` 或 `<workspace>/.pi` 配置项。

## 会话

会话记录以 JSONL 格式存储于：

- `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`

会话 ID 具有稳定性，由 OpenClaw 统一分配。  
旧版 Pi/Tau 会话文件夹**不会被读取**。

## 流式响应中的动态干预（Steering while streaming）

当队列模式为 `steer` 时，传入消息将被注入当前运行流程。  
队列会在**每次工具调用之后**检查；若发现待处理消息，则跳过当前助手消息中剩余的所有工具调用（相关工具结果返回错误：“Skipped due to queued user message.”），随后将排队的用户消息注入，并在下一轮助手响应前生效。

当队列模式为 `followup` 或 `collect` 时，传入消息将被暂存，直至当前轮次结束，然后以排队的有效载荷启动新一轮代理交互。详见 [队列机制](/concepts/queue) 中关于模式及防抖 / 限流行为的说明。

块式流式响应（Block streaming）会在助手响应块完成时立即发送；该功能**默认关闭**（`agents.defaults.blockStreamingDefault: "off"`）。  
可通过 `agents.defaults.blockStreamingBreak` 调整分块边界（支持 `text_end` 与 `message_end`；默认为 `text_end`）。  
通过 `agents.defaults.blockStreamingChunk` 控制软块切分（默认为 800–1200 字符；优先按段落切分，其次换行符，最后句子结尾）。  
使用 `agents.defaults.blockStreamingCoalesce` 合并流式响应块，以减少单行刷屏（基于空闲时间合并后再发送）。  
非 Telegram 渠道需显式启用 `*.blockStreaming: true` 才能支持块式回复。  
工具摘要信息在工具启动时即刻输出（无防抖）；控制界面在可用时通过代理事件流式传输工具输出。  
更多细节请参阅：[流式响应与分块](/concepts/streaming)。

## 模型引用（Model refs）

配置中的模型引用（例如 `agents.defaults.model` 和 `agents.defaults.models`）将依据**首个** `/` 进行解析。

- 配置模型时请使用 `provider/model`。
- 若模型 ID 本身已含 `/`（OpenRouter 风格），则必须包含提供方前缀（示例：`openrouter/moonshotai/kimi-k2`）。
- 若省略提供方前缀，OpenClaw 将把输入视为别名，或视为**默认提供方**下的模型（仅当模型 ID 中不含 `/` 时有效）。

## 配置（最小化要求）

至少需设置以下两项：

- `agents.defaults.workspace`
- `channels.whatsapp.allowFrom`（强烈推荐）

---

_下一步：[群组聊天](/channels/group-messages)_ 🦞