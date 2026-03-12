---
summary: "Directive syntax for /think + /verbose and how they affect model reasoning"
read_when:
  - Adjusting thinking or verbose directive parsing or defaults
title: "Thinking Levels"
---
# 思考级别 (/think 指令)

## 功能

- 任何入站正文中的内联指令：`/t <level>`, `/think:<level>`, 或 `/thinking <level>`。
- 级别（别名）: `off | minimal | low | medium | high | xhigh | adaptive`
  - minimal → “think”
  - low → “think hard”
  - medium → “think harder”
  - high → “ultrathink” (最大预算)
  - xhigh → “ultrathink+” (仅限 GPT-5.2 和 Codex 模型)
  - adaptive → 提供商管理的自适应推理预算（支持 Anthropic Claude 4.6 模型系列）
  - `x-high`, `x_high`, `extra-high`, `extra high`, 和 `extra_high` 映射到 `xhigh`。
  - `highest`, `max` 映射到 `high`。
- 提供商说明：
  - 当未设置明确的思考级别时，Anthropic Claude 4.6 模型默认为 `adaptive`。
  - Z.AI (`zai/*`) 仅支持二进制思考 (`on`/`off`)。任何非 `off` 级别都被视为 `on`（映射到 `low`）。
  - Moonshot (`moonshot/*`) 将 `/think off` 映射到 `thinking: { type: "disabled" }`，并将任何非 `off` 级别映射到 `thinking: { type: "enabled" }`。当启用思考时，Moonshot 仅接受 `tool_choice` `auto|none`；OpenClaw 将不兼容的值标准化为 `auto`。

## 解析顺序

1. 消息上的内联指令（仅适用于该消息）。
2. 会话覆盖（通过发送仅包含指令的消息设置）。
3. 全局默认值（配置中的 `agents.defaults.thinkingDefault`）。
4. 回退：Anthropic Claude 4.6 模型为 `adaptive`，其他具备推理能力的模型为 `low`，否则为 `off`。

## 设置会话默认值

- 发送一条**仅**包含指令的消息（允许空白），例如 `/think:medium` 或 `/t high`。
- 这将应用于当前会话（默认情况下按发件人划分）；通过 `/think:off` 或会话空闲重置清除。
- 发送确认回复 (`Thinking level set to high.` / `Thinking disabled.`)。如果级别无效（例如 `/thinking big`），则命令被拒绝并提示，会话状态保持不变。
- 发送 `/think`（或 `/think:`）且无参数以查看当前思考级别。

## 代理应用

- **嵌入式 Pi**：解析后的级别传递给进程内的 Pi 代理运行时。

## 详细指令 (/verbose 或 /v)

- 级别：`on` (minimal) | `full` | `off` (默认)。
- 仅包含指令的消息切换会话详细模式并回复 `Verbose logging enabled.` / `Verbose logging disabled.`；无效级别返回提示而不改变状态。
- `/verbose off` 存储显式的会话覆盖；通过选择 Sessions UI 中的 `inherit` 清除它。
- 内联指令仅影响该消息；否则应用会话/全局默认值。
- 发送 `/verbose`（或 `/verbose:`）且无参数以查看当前详细级别。
- 当详细模式开启时，发出结构化工具结果的代理（Pi、其他 JSON 代理）将每个工具调用作为单独的仅元数据消息发送，如果有可用的路径/命令，则以前缀 `<emoji> <tool-name>: <arg>` 开头。这些工具摘要在每个工具启动时立即发送（单独的气泡），而不是作为流式增量。
- 工具失败摘要在正常模式下仍然可见，但原始错误详情后缀在详细模式不是 `on` 或 `full` 时隐藏。
- 当详细模式为 `full` 时，工具输出也在完成后转发（单独的气泡，截断至安全长度）。如果您在运行过程中切换 `/verbose on|full|off`，后续的工具气泡将遵循新的设置。

## 推理可见性 (/reasoning)

- 级别：`on|off|stream`。
- 仅包含指令的消息切换回复中是否显示思考块。
- 启用时，推理作为**单独的消息**发送，前缀为 `Reasoning:`。
- `stream`（仅 Telegram）：在生成回复时将推理流式传输到 Telegram 草稿气泡，然后发送最终答案而没有推理。
- 别名：`/reason`。
- 发送 `/reasoning`（或 `/reasoning:`）且无参数以查看当前推理级别。

## 相关

- 升级模式文档位于 [升级模式](/tools/elevated)。

## 心跳

- 心跳探测正文是配置的心跳提示（默认：`Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`）。心跳消息中的内联指令按常规应用（但避免从心跳更改会话默认值）。
- 心跳传递默认仅为最终负载。要同时发送单独的 `Reasoning:` 消息（如果有），请设置 `agents.defaults.heartbeat.includeReasoning: true` 或每个代理的 `agents.list[].heartbeat.includeReasoning: true`。

## Web 聊天界面

- Web 聊天思考选择器在页面加载时反映入站会话存储/配置中存储的级别。
- 选择另一个级别仅适用于下一条消息 (`thinkingOnce`)；发送后，选择器恢复到存储的会话级别。
- 要更改会话默认值，请发送一个 `/think:<level>` 指令（如前所述）；选择器将在下次重新加载后反映它。