---
summary: "Directive syntax for /think + /verbose and how they affect model reasoning"
read_when:
  - Adjusting thinking or verbose directive parsing or defaults
title: "Thinking Levels"
---
# 思考层级（/think 指令）

## 功能说明

- 任意输入内容中的内联指令：`/t <层级>`、`/think:<层级>` 或 `/thinking <层级>`。
- 层级（别名）：`off | minimal | low | medium | high | xhigh`（仅适用于 GPT-5.2 + Codex 模型）
  - minimal → “think”
  - low → “think hard”
  - medium → “think harder”
  - high → “ultrathink”（最大预算）
  - xhigh → “ultrathink+”（仅适用于 GPT-5.2 + Codex 模型）
  - `highest`、`max` 映射为 `high`。
- 提供商说明：
  - Z.AI（`zai/*`）仅支持二进制思考（`on`/`off`）。任何非 `off` 的层级均视为 `on`（映射为 `low`）。

## 解决顺序

1. 消息中的内联指令（仅适用于该消息）。
2. 会话覆盖（通过发送仅指令的消息设置）。
3. 全局默认值（配置中的 `agents.defaults.thinkingDefault`）。
4. 默认回退：对具备推理能力的模型使用 `low`，否则使用 `off`。

## 设置会话默认值

- 发送仅包含指令的消息（允许空格），例如 `/think:medium` 或 `/t high`。
- 该设置将保留当前会话（默认按发送者区分）；通过 `/think:off` 或会话空闲重置清除。
- 会发送确认回复（`Thinking level set to high.` / `Thinking disabled.`）。若层级无效（例如 `/thinking big`），指令将被拒绝并提示，同时会话状态保持不变。
- 发送 `/think`（或 `/think:`）无参数以查看当前思考层级。

## 代理应用

- **嵌入式 Pi**：解析后的层级将传递给进程内的 Pi 代理运行时。

## 详细指令（/verbose 或 /v）

- 层级：`on`（最小）| `full` | `off`（默认）。
- 仅指令消息切换会话详细模式，并回复 `Verbose logging enabled.` / `Verbose logging disabled.`；无效层级返回提示但不更改状态。
- `/verbose off` 存储显式的会话覆盖；通过会话 UI 选择 `inherit` 清除。
- 内联指令仅影响该消息；否则使用会话/全局默认值。
- 发送 `/verbose`（或 `/verbose:`）无参数以查看当前详细层级。
- 当详细模式开启时，发出结构化工具结果的代理（Pi、其他 JSON 代理）会将每个工具调用作为独立的元数据消息发送，前缀为 `<emoji> <tool-name>: <arg>`（当路径/命令可用时）。这些工具摘要会在每个工具启动时立即发送（独立气泡），而非流式增量。
- 当详细模式为 `full` 时，工具输出在完成时也会转发（独立气泡，截断至安全长度）。若在运行中切换 `/verbose on|full|off`，后续工具气泡将遵循新设置。

## 推理可见性（/reasoning）

- 层级：`on|off|stream`。
- 仅指令消息切换是否在回复中显示思考块。
- 启用时，推理将作为 **独立消息** 发送，前缀为 `Reasoning:`。
- `stream`（仅限 Telegram）：在回复生成时将推理流式传输至 Telegram 草稿气泡，然后发送最终答案而不包含推理。
- 别名：`/reason`。
- 发送 `/reasoning`（或 `/reasoning:`）无参数以查看当前推理层级。

## 相关内容

- 高级模式文档位于 [Elevated mode](/tools/elevated)。

## 心跳机制

- 心跳探针内容为配置的心跳提示（默认：`Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`）。心跳消息中的内联指令按常规应用（但避免通过心跳更改会话默认值）。
- 心跳默认仅发送最终负载。若需同时发送独立的 `Reasoning:` 消息（当可用时），设置 `agents.defaults.heartbeat.includeReasoning: true` 或单个代理 `agents.list[].heartbeat.includeReasoning: true`。

## 网页聊天 UI

- 网页聊天的思考选择器在页面加载时会镜像从输入会话存储/配置中存储的会话层级。
- 选择其他层级仅适用于下一条消息（`thinkingOnce`）；发送后，选择器会恢复到存储的会话层级。
- 要更改会话默认值，发送 `/think:<层级>` 指令（如前所述）；下一次刷新后，选择器将反映该设置。