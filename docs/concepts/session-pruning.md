---
title: "Session Pruning"
summary: "Session pruning: tool-result trimming to reduce context bloat"
read_when:
  - You want to reduce LLM context growth from tool outputs
  - You are tuning agents.defaults.contextPruning
---
# 会话剪枝（Session Pruning）

会话剪枝会在每次调用大语言模型（LLM）**之前**，从内存中的上下文里裁剪掉**过期的工具执行结果**。它**不会**重写磁盘上的会话历史记录（``*.jsonl``）。

## 触发时机

- 当启用 ``mode: "cache-ttl"`` 且当前会话中上一次 Anthropic 调用距今已超过 ``ttl`` 时。
- 仅影响发送给模型的本次请求消息。
- 仅对 Anthropic API 调用（以及 OpenRouter 上的 Anthropic 模型）生效。
- 为获得最佳效果，请将 ``ttl`` 与所用模型的 ``cacheRetention`` 策略保持一致（例如：``short` = 5m`，``long` = 1h`）。
- 剪枝完成后，TTL 时间窗口将重置，因此后续请求可继续利用缓存，直至 ``ttl`` 再次过期。

## 智能默认配置（Anthropic）

- **OAuth 或 setup-token 认证方式**的配置文件：启用 ``cache-ttl`` 剪枝，并将心跳间隔设为 ``1h``。
- **API key 认证方式**的配置文件：启用 ``cache-ttl`` 剪枝，将心跳间隔设为 ``30m``，并在 Anthropic 模型上默认启用 ``cacheRetention: "short"``。
- 若您显式设置了其中任一参数，OpenClaw **不会**覆盖这些值。

## 此功能带来的优化（成本 + 缓存行为）

- **为何需要剪枝**：Anthropic 的提示词缓存仅在 TTL 有效期内生效。若会话空闲时间超出 TTL，下次请求将重新缓存完整提示词——除非您提前进行剪枝。
- **降低成本的环节**：剪枝可减小 TTL 过期后首次请求的 `cacheWrite` 数据量。
- **TTL 重置的意义**：一旦执行剪枝，缓存窗口即重置，后续请求便可复用新缓存的提示词，而无需再次缓存全部历史。
- **它不做的事情**：剪枝既不会增加 token 数量，也不会造成“重复计费”；它仅改变 TTL 过期后首次请求中被缓存的内容。

## 可被剪枝的内容

- 仅限 ``toolResult`` 类型的消息。
- 用户（User）和助手（Assistant）消息**永远不会被修改**。
- 最近的 ``keepLastAssistants`` 条助手消息受保护；该截断点之后的工具结果**不会被剪枝**。
- 若助手消息数量不足以确立该截断点，则跳过剪枝。
- 包含**图像块（image blocks）** 的工具结果会被跳过（永不裁剪/清除）。

## 上下文窗口估算

剪枝使用估算的上下文窗口（字符数 ≈ token 数 × 4）。基础窗口按如下优先级确定：

1. ``models.providers.*.models[].contextWindow`` 覆盖设置。
2. 模型定义中的 ``contextWindow``（来自模型注册表）。
3. 默认值 ``200000`` tokens。

若设置了 ``agents.defaults.contextTokens``，则将其视为已解析窗口的上限（最小值）。

## 模式

### cache-ttl

- 仅当上一次 Anthropic 调用距今已超过 ``ttl``（默认为 ``5m``）时才执行剪枝。
- 执行时行为与此前一致：先软裁剪（soft-trim），再硬清除（hard-clear）。

## 软剪枝 vs 硬清除

- **软裁剪（Soft-trim）**：仅适用于过大尺寸的工具结果。
  - 保留头部（head）和尾部（tail），中间插入 ``...``，并在末尾附加一条注明原始大小的说明。
  - 含图像块的结果将被跳过。
- **硬清除（Hard-clear）**：将整个工具结果替换为 ``hardClear.placeholder``。

## 工具选择规则

- ``tools.allow`` / ``tools.deny`` 支持 ``*`` 通配符。
- 拒绝（deny）规则优先于允许（allow）规则。
- 匹配不区分大小写。
- 若允许列表为空，则所有工具均被允许。

## 与其他限制的交互关系

- 内置工具本身已对其输出进行截断；会话剪枝是额外一层防护机制，防止长时间对话在模型上下文中累积过多工具输出。
- 压缩（Compaction）是独立功能：压缩会对内容进行摘要并持久化存储，而剪枝则是每次请求时的临时操作。详见 [/concepts/compaction](/concepts/compaction)。

## 默认配置（启用时）

- ``ttl``: ``"5m"``
- ``keepLastAssistants``: ``3``
- ``softTrimRatio``: ``0.3``
- ``hardClearRatio``: ``0.5``
- ``minPrunableToolChars``: ``50000``
- ``softTrim``: ``{ maxChars: 4000, headChars: 1500, tailChars: 1500 }``
- ``hardClear``: ``{ enabled: true, placeholder: "[Old tool result content cleared]" }``

## 示例

默认（关闭）：

````json5
{
  agents: { defaults: { contextPruning: { mode: "off" } } },
}
````

启用基于 TTL 的剪枝：

````json5
{
  agents: { defaults: { contextPruning: { mode: "cache-ttl", ttl: "5m" } } },
}
````

限制剪枝仅作用于特定工具：

````json5
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
````

参阅配置参考文档：[网关配置（Gateway Configuration）](/gateway/configuration)