---
title: "Session Pruning"
summary: "Session pruning: tool-result trimming to reduce context bloat"
read_when:
  - You want to reduce LLM context growth from tool outputs
  - You are tuning agents.defaults.contextPruning
---
# 会话修剪

会话修剪在每次 LLM 调用之前，从内存上下文中修剪**旧工具结果**。它**不会**重写磁盘上的会话历史（`*.jsonl`）。

## 运行时机

- 当 `mode: "cache-ttl"` 启用且会话的最后一次 Anthropic 调用早于 `ttl` 时。
- 仅影响该请求发送给模型的消息。
- 仅对 Anthropic API 调用（以及 OpenRouter Anthropic 模型）生效。
- 为获得最佳效果，请将 `ttl` 与您的模型 `cacheRetention` 策略相匹配（`short` = 5m，`long` = 1h）。
- 修剪后，TTL 窗口重置，因此后续请求会保持缓存，直到 `ttl` 再次过期。

## 智能默认值（Anthropic）

- **OAuth 或 setup-token** 配置文件：启用 `cache-ttl` 修剪并将心跳设置为 `1h`。
- **API key** 配置文件：启用 `cache-ttl` 修剪，将心跳设置为 `30m`，并在 Anthropic 模型上默认 `cacheRetention: "short"`。
- 如果您显式设置了任何这些值，OpenClaw **不会**覆盖它们。

## 改进内容（成本 + 缓存行为）

- **为何修剪：** Anthropic 提示词缓存仅在 TTL 内适用。如果会话空闲超过 TTL，除非您先修剪它，否则下一个请求将重新缓存完整提示词。
- **什么变得更便宜：** 修剪减少了 TTL 过期后第一个请求的 **cacheWrite** 大小。
- **为何 TTL 重置很重要：** 一旦运行修剪，缓存窗口重置，因此后续请求可以重用新缓存的提示词，而不是再次重新缓存完整历史。
- **它不做什么：** 修剪不会增加 token 或“加倍”成本；它只改变 TTL 后第一个请求上缓存的内容。

## 可修剪内容

- 仅 `toolResult` 消息。
- User + assistant 消息**永远不会**被修改。
- 最后 `keepLastAssistants` 条 assistant 消息受保护；该截止点之后的工具结果不会被修剪。
- 如果没有足够的 assistant 消息来建立截止点，则跳过修剪。
- 包含 **image blocks** 的工具结果会被跳过（永远不会被修剪/清除）。

## 上下文窗口估算

修剪使用估算的上下文窗口（chars ≈ tokens × 4）。基础窗口按以下顺序解析：

1. `models.providers.*.models[].contextWindow` 覆盖。
2. 模型定义 `contextWindow`（来自模型注册表）。
3. 默认 `200000` tokens。

如果设置了 `agents.defaults.contextTokens`，它被视为解析窗口的上限（最小值）。

## 模式

### cache-ttl

- 仅当最后一次 Anthropic 调用早于 `ttl` 时运行修剪（默认 `5m`）。
- 运行时：与之前相同的 soft-trim + hard-clear 行为。

## 软修剪与硬修剪

- **Soft-trim**：仅针对过大的工具结果。
  - 保留 head + tail，插入 `...`，并附加带有原始大小的注释。
  - 跳过包含 image blocks 的结果。
- **Hard-clear**：用 `hardClear.placeholder` 替换整个工具结果。

## 工具选择

- `tools.allow` / `tools.deny` 支持 `*` 通配符。
- Deny 优先。
- 匹配不区分大小写。
- 空 allow list => 允许所有工具。

## 与其他限制的交互

- 内置工具已经截断了自己的输出；会话修剪是额外的一层，防止长时间运行的聊天在模型上下文中积累过多的工具输出。
- Compaction 是独立的：compaction 进行总结并持久化，修剪是每个请求瞬态的。参见 [/concepts/compaction](/concepts/compaction)。

## 默认值（启用时）

- `ttl`: `"5m"`
- `keepLastAssistants`: `3`
- `softTrimRatio`: `0.3`
- `hardClearRatio`: `0.5`
- `minPrunableToolChars`: `50000`
- `softTrim`: `{ maxChars: 4000, headChars: 1500, tailChars: 1500 }`
- `hardClear`: `{ enabled: true, placeholder: "[Old tool result content cleared]" }`

## 示例

默认（关闭）：

```json5
{
  agents: { defaults: { contextPruning: { mode: "off" } } },
}
```

启用 TTL 感知修剪：

```json5
{
  agents: { defaults: { contextPruning: { mode: "cache-ttl", ttl: "5m" } } },
}
```

将修剪限制为特定工具：

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl",
        tools: { allow: ["exec", "read"], deny: ["*image*"] },
      },
    },
  },
}
```

参见配置参考：[网关配置](/gateway/configuration)