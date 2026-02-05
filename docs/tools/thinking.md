---
summary: "Directive syntax for /think + /verbose and how they affect model reasoning"
read_when:
  - Adjusting thinking or verbose directive parsing or defaults
title: "Thinking Levels"
---
# 思考层次 (/think 指令)

## 它的作用

- 在任何传入消息体中的内联指令：`/t <level>`，`/think:<level>`，或 `/thinking <level>`。
- 层次（别名）：`off | minimal | low | medium | high | xhigh`（仅限 GPT-5.2 + Codex 模型）
  - minimal → “think”
  - low → “think hard”
  - medium → “think harder”
  - high → “ultrathink”（最大预算）
  - xhigh → “ultrathink+”（仅限 GPT-5.2 + Codex 模型）
  - `highest`，`max` 映射到 `high`。
- 提供商说明：
  - Z.AI (`zai/*`) 仅支持二元思考 (`on`/`off`)。任何非 `off` 层次被视为 `on`（映射到 `low`）。

## 解析顺序

1. 消息上的内联指令（仅适用于该消息）。
2. 会话覆盖（通过发送仅包含指令的消息设置）。
3. 全局默认值（配置中的 `agents.defaults.thinkingDefault`）。
4. 回退：对于具备推理能力的模型为 low；否则为关闭。

## 设置会话默认值

- 发送一条**仅**包含指令的消息（允许空白），例如 `/think:medium` 或 `/t high`。
- 这适用于当前会话（默认按发件人区分）；通过 `/think:off` 或会话空闲重置清除。
- 发送确认回复 (`Thinking level set to high.` / `Thinking disabled.`)。如果层次无效（例如 `/thinking big`)，命令将被拒绝并提供提示，会话状态保持不变。
- 发送 `/think`（或 `/think:`）不带参数以查看当前思考层次。

## 代理应用

- **嵌入式 Pi**：解析后的层次传递给进程中的 Pi 代理运行时。

## 详细指令 (/verbose 或 /v)

- 层次：`on`（最小）| `full` | `off`（默认）。
- 仅指令消息切换会话详细模式并回复 `Verbose logging enabled.` / `Verbose logging disabled.`；无效层次返回提示而不更改状态。
- `/verbose off` 存储显式会话覆盖；通过会话 UI 选择 `inherit` 清除。
- 内联指令仅影响该消息；否则应用会话/全局默认值。
- 发送 `/verbose`（或 `/verbose:`）不带参数以查看当前详细层次。
- 当详细模式开启时，发出结构化工具结果（Pi，其他 JSON 代理）的代理将每个工具调用作为其自身的元数据消息发送回，前缀为 `<emoji> <tool-name>: <arg>`（当可用时）（路径/命令）。这些工具摘要在每个工具启动时发送（单独气泡），而不是作为流式增量。
- 当详细模式为 `full` 时，工具输出在完成后也会转发（单独气泡，截断为安全长度）。如果您在运行过程中切换 `/verbose on|full|off`，后续工具气泡将遵循新设置。

## 推理可见性 (/reasoning)

- 层次：`on|off|stream`。
- 仅指令消息切换回复中是否显示思考块。
- 启用时，推理作为**单独消息**发送，前缀为 `Reasoning:`。
- `stream`（仅限 Telegram）：在回复生成时将推理流式传输到 Telegram 草稿气泡中，然后发送最终答案而不包含推理。
- 别名：`/reason`。
- 发送 `/reasoning`（或 `/reasoning:`）不带参数以查看当前推理层次。

## 相关

- 升级模式文档位于 [升级模式](/tools/elevated)。

## 心跳

- 心跳探测消息体是配置的心跳提示（默认：`Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`)。心跳消息中的内联指令按常规应用（但避免从心跳中更改会话默认值）。
- 心跳交付默认为最终有效负载。要同时发送单独的 `Reasoning:` 消息（当可用时），设置 `agents.defaults.heartbeat.includeReasoning: true` 或每个代理的 `agents.list[].heartbeat.includeReasoning: true`。

## 网页聊天界面

- 网页聊天思考选择器在页面加载时反映传入会话存储/配置中存储的层次。
- 选择另一个层次仅适用于下一条消息 (`thinkingOnce`)；发送后，选择器恢复到存储的会话层次。
- 要更改会话默认值，发送 `/think:<level>` 指令（如前所述）；选择器将在下次重新加载后反映更改。