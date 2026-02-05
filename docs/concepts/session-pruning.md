---
summary: "Session pruning: tool-result trimming to reduce context bloat"
read_when:
  - You want to reduce LLM context growth from tool outputs
  - You are tuning agents.defaults.contextPruning
---
# 会话修剪

会话修剪在每次LLM调用之前从内存上下文中裁剪**旧工具结果**。它**不会**重写磁盘上的会话历史（`*.jsonl`）。

## 运行时机

- 当`mode: "cache-ttl"`启用且会话的最后一次Anthropic调用早于`ttl`时。
- 仅影响发送给该请求模型的消息。
- 仅对Anthropic API调用（和OpenRouter Anthropic模型）生效。
- 为了获得最佳效果，请将`ttl`与您的模型`cacheControlTtl`匹配。
- 修剪后，TTL窗口重置，因此后续请求会保持缓存直到`ttl`再次过期。

## 智能默认值（Anthropic）

- **OAuth或setup-token**配置文件：启用`cache-ttl`修剪并将心跳设置为`1h`。
- **API密钥**配置文件：启用`cache-ttl`修剪，将心跳设置为`30m`，并在Anthropic模型上将默认`cacheControlTtl`设置为`1h`。
- 如果您明确设置了这些值中的任何一个，OpenClaw**不会**覆盖它们。

## 改进内容（成本+缓存行为）

- **为什么要修剪：** Anthropic提示缓存仅在TTL内适用。如果会话在TTL过去后处于空闲状态，下次请求会重新缓存完整提示，除非您先进行修剪。
- **什么变得更便宜：** 修剪减少了TTL过期后第一次请求的**cacheWrite**大小。
- **为什么TTL重置很重要：** 一旦修剪运行，缓存窗口重置，因此后续请求可以重用新缓存的提示，而不是再次重新缓存完整历史记录。
- **它不做什么：** 修剪不会添加令牌或"双重"成本；它只改变TTL后第一次请求的缓存内容。

## 可修剪的内容

- 仅限`toolResult`消息。
- 用户+助手消息**永远不会**被修改。
- 最后的`keepLastAssistants`个助手消息受到保护；该截止时间之后的工具结果不会被修剪。
- 如果没有足够的助手消息来建立截止点，则跳过修剪。
- 包含**图像块**的工具结果会被跳过（永远不会被修剪/清除）。

## 上下文窗口估算

修剪使用估算的上下文窗口（字符≈令牌×4）。基础窗口按此顺序解析：

1. `models.providers.*.models[].contextWindow`覆盖。
2. 模型定义`contextWindow`（来自模型注册表）。
3. 默认`200000`令牌。

如果设置了`agents.defaults.contextTokens`，则将其视为解析窗口的上限（最小值）。

## 模式

### cache-ttl

- 仅当上次Anthropic调用早于`ttl`（默认`5m`）时才运行修剪。
- 运行时：与之前相同的软修剪+硬清除行为。

## 软修剪vs硬修剪

- **软修剪**：仅针对超大工具结果。
  - 保留头部+尾部，插入`...`，并附加原始大小的注释。
  - 跳过包含图像块的结果。
- **硬清除**：用`hardClear.placeholder`替换整个工具结果。

## 工具选择

- `tools.allow`/`tools.deny`支持`*`通配符。
- 拒绝优先。
- 匹配不区分大小写。
- 空允许列表=>允许所有工具。

## 与其他限制的交互

- 内置工具已经截断自己的输出；会话修剪是防止长时间运行的聊天在模型上下文中累积过多工具输出的额外层。
- 压缩是独立的：压缩总结并持久化，修剪是每个请求的临时操作。参见[/concepts/compaction](/concepts/compaction)。

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

启用TTL感知修剪：

```json5
{
  agent: {
    contextPruning: { mode: "cache-ttl", ttl: "5m" },
  },
}
```

将修剪限制为特定工具：

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