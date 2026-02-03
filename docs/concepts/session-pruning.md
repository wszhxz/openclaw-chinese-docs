---
summary: "Session pruning: tool-result trimming to reduce context bloat"
read_when:
  - You want to reduce LLM context growth from tool outputs
  - You are tuning agents.defaults.contextPruning
---
工具<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context and key terms. The main topic is session pruning in an LLM system, specifically related to Anthropic API and OpenRouter models. 

First, I'll identify technical terms and ensure they are accurately translated. For example, "session pruning" should be "会话修剪" to maintain the technical meaning. Terms like "cache-ttl" might stay as is since they are specific modes or settings. 

I need to be careful with the structure, like headings and bullet points. The user mentioned only returning the translated text, so I must avoid any extra explanations. Also, code blocks and JSON examples should remain unchanged except for the language. 

Some phrases like "toolResult" might be translated as "工具结果" to keep the context. I'll check for consistency in terms like "context window" which should be "上下文窗口" and "cacheWrite" as "缓存写入". 

I should also pay attention to the specific examples provided, ensuring that the JSON syntax is preserved and that the comments are correctly translated. For instance, "OAuth or setup-token profiles" becomes "OAuth 或 setup-token 配置文件". 

There are sections about modes, soft vs hard pruning, and tool selection. These need precise translation to maintain the technical accuracy. Terms like "soft-trim" and "hard-clear" should be translated to "软修剪" and "硬清除" respectively. 

I'll go through each section step by step, translating each part while keeping the structure intact. I'll make sure that the explanations about how pruning affects cache behavior and costs are clearly conveyed in Chinese. 

Finally, I'll review the entire translation to ensure there are no errors and that the flow matches the original document. This way, the translated text will be accurate, clear, and suitable for the target audience.
</think>

# 会话修剪

会话修剪会在每次调用大语言模型（LLM）之前，从内存上下文中移除**旧的工具结果**。它**不会**重写磁盘上的会话历史记录（`*.jsonl`）。

## 何时运行

- 当启用 `mode: "cache-ttl"` 且会话的最后一次 Anthropic 调用时间早于 `ttl` 时。
- 仅影响该请求发送给模型的消息。
- 仅对 Anthropic API 调用（以及 OpenRouter 的 Anthropic 模型）生效。
- 为了最佳效果，请将 `ttl` 与模型的 `cacheControlTtl` 匹配。
- 修剪后，TTL 窗口会重置，后续请求会保持缓存直到 `ttl` 再次过期。

## 智能默认值（Anthropic）

- **OAuth 或 setup-token 配置文件**：启用 `cache-ttl` 修剪，并将心跳间隔设置为 `1h`。
- **API 密钥** 配置文件：启用 `cache-ttl` 修剪，将心跳间隔设置为 `30m`，并在 Anthropic 模型上将 `cacheControlTtl` 默认设置为 `1h`。
- 如果您显式设置了这些值，OpenClaw **不会** 覆盖它们。

## 优化效果（成本 + 缓存行为）

- **为何修剪**：Anthropic 的提示缓存仅在 TTL 内有效。如果会话在 TTL 之后空闲，下一次请求会重新缓存完整提示，除非您先进行修剪。
- **什么变得更便宜**：修剪会减少该 TTL 过期后第一个请求的 **缓存写入** 大小。
- **为何 TTL 重置重要**：一旦修剪运行，缓存窗口会重置，因此后续请求可以复用最新缓存的提示，而不是再次缓存完整历史。
- **它不做什么**：修剪不会增加令牌或“双重”成本；它仅改变第一个 TTL 后请求中缓存的内容。

## 可修剪的内容

- 仅 `toolResult` 消息。
- 用户 + 助理消息 **永远不会** 被修改。
- 最后 `keepLastAssistants` 条助理消息受保护；该截止点之后的工具结果不会被修剪。
- 如果没有足够的助理消息来确定截止点，修剪将被跳过。
- 包含 **图像块** 的工具结果将被跳过（永不修剪/清除）。

## 上下文窗口估计

修剪使用估计的上下文窗口（字符 ≈ 令牌 × 4）。基础窗口的解析顺序如下：

1. `models.providers.*.models[].contextWindow` 覆盖。
2. 模型定义 `contextWindow`（来自模型注册表）。
3. 默认 `200000` 令牌。

如果设置了 `agents.defaults.contextTokens`，它被视为解析窗口的上限（最小值）。

## 模式

### cache-ttl

- 仅当最后一次 Anthropic 调用时间早于 `ttl`（默认 `5m`）时运行修剪。
- 运行时：与之前相同，采用软修剪 + 硬清除行为。

## 软修剪 vs 硬清除

- **软修剪**：仅用于过大工具结果。
  - 保留头部 + 尾部，插入 `...`，并附加原始大小的说明。
  - 跳过包含图像块的结果。
- **硬清除**：将整个工具结果替换为 `hardClear.placeholder`。

## 工具选择

- `tools.allow` / `tools.deny` 支持 `*` 通配符。
- 拒绝优先。
- 匹配不区分大小写。
- 空白允许列表 => 允许所有工具。

## 与其他限制的交互

- 内置工具已自行截断输出；会话修剪是额外的一层，防止长时间对话在模型上下文中累积过多工具输出。
- 压缩是独立的：压缩会总结并持久化，修剪是每次请求的临时操作。请参见 [/concepts/compaction](/concepts/compaction)。

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
  agent: {
    contextPruning: { mode: "off" },
  },
}
```

启用 TTL 意识修剪：

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

查看配置参考：[网关配置](/gateway/configuration)