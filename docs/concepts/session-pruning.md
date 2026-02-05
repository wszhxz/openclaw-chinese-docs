---
summary: "Session pruning: tool-result trimming to reduce context bloat"
read_when:
  - You want to reduce LLM context growth from tool outputs
  - You are tuning agents.defaults.contextPruning
---
# 会话修剪

会话修剪在每次调用LLM之前从内存上下文中移除**旧工具结果**。它**不会**重写磁盘上的会话历史记录(`*.jsonl`)。

## 运行时机

- 当`mode: "cache-ttl"`启用且该会话的最后一次Anthropic调用时间超过`ttl`。
- 仅影响该请求发送给模型的消息。
- 仅对Anthropic API调用（以及OpenRouter Anthropic模型）有效。
- 为了最佳效果，请将`ttl`与您的模型`cacheControlTtl`匹配。
- 修剪后，TTL窗口重置，因此后续请求会在`ttl`过期前继续使用缓存。

## 智能默认设置（Anthropic）

- **OAuth或setup-token**配置文件：启用`cache-ttl`修剪并将心跳设置为`1h`。
- **API密钥**配置文件：启用`cache-ttl`修剪，将心跳设置为`30m`，并将Anthropic模型的默认`cacheControlTtl`设置为`1h`。
- 如果您显式设置了这些值，OpenClaw**不会**覆盖它们。

## 改进之处（成本+缓存行为）

- **为什么修剪：** Anthropic提示缓存仅在TTL内有效。如果会话在TTL之后空闲，下一个请求会重新缓存完整提示，除非您先进行修剪。
- **什么变得更便宜：** 修剪可以减少TTL过期后的第一个请求的**cacheWrite**大小。
- **为什么TTL重置很重要：** 一旦运行修剪，缓存窗口会重置，因此后续请求可以重用新缓存的提示，而不是重新缓存完整历史记录。
- **它不做什么：** 修剪不会增加令牌或“双倍”成本；它仅更改TTL后第一个请求的缓存内容。

## 可以修剪的内容

- 仅`toolResult`消息。
- 用户和助手的消息**永远不会**被修改。
- 最近的`keepLastAssistants`助手消息受到保护；该截止点之后的工具结果不会被修剪。
- 如果助手消息不足以建立截止点，则跳过修剪。
- 包含**图像块**的工具结果会被跳过（从不修剪/清除）。

## 上下文窗口估算

修剪使用估算的上下文窗口（字符 ≈ 令牌 × 4）。基本窗口按以下顺序解析：

1. `models.providers.*.models[].contextWindow`覆盖。
2. 模型定义`contextWindow`（来自模型注册表）。
3. 默认`200000`令牌。

如果设置了`agents.defaults.contextTokens`，则将其视为解析窗口的上限（最小值）。

## 模式

### cache-ttl

- 仅当最后一次Anthropic调用时间超过`ttl`（默认`5m`）时才运行修剪。
- 运行时：与之前的软修剪+硬清除行为相同。

## 软修剪与硬修剪

- **软修剪**：仅用于超大工具结果。
  - 保留头部和尾部，插入`...`，并附加一个包含原始大小的注释。
  - 跳过包含图像块的结果。
- **硬清除**：将整个工具结果替换为`hardClear.placeholder`。

## 工具选择

- `tools.allow` / `tools.deny`支持`*`通配符。
- 拒绝优先。
- 匹配不区分大小写。
- 空允许列表 => 允许所有工具。

## 与其他限制的交互

- 内置工具已经截断了自己的输出；会话修剪是额外的一层，防止长时间聊天在模型上下文中累积过多的工具输出。
- 压缩是独立的：压缩会总结并持久化，而修剪是每个请求的临时操作。参见[/concepts/compaction](/concepts/compaction)。

## 默认设置（启用时）

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
  agent: {
    contextPruning: { mode: "off" },
  },
}
```

启用TTL感知修剪：

```json5
{
  agent: {
    contextPruning: { mode: "cache-ttl", ttl: "5m" },
  },
}
```

限制修剪到特定工具：

```json5
{
  agent: {
    contextPruning: {
      mode: "cache-ttl",
      tools: { allow: ["exec", "read"], deny: ["*image*"] },
    },
  },
}
```

参见配置参考：[网关配置](/gateway/configuration)