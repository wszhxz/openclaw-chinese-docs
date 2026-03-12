---
title: "Prompt Caching"
summary: "Prompt caching knobs, merge order, provider behavior, and tuning patterns"
read_when:
  - You want to reduce prompt token costs with cache retention
  - You need per-agent cache behavior in multi-agent setups
  - You are tuning heartbeat and cache-ttl pruning together
---
# 提示缓存

提示缓存意味着模型提供商可在多轮对话中复用未发生变化的提示前缀（通常是系统/开发者指令及其他稳定上下文），而无需每次重新处理。首个匹配请求将写入缓存令牌（``cacheWrite``），后续匹配请求则可读取这些缓存令牌（``cacheRead``）。

为何这很重要：降低令牌成本、加快响应速度，并为长时间运行的会话提供更可预测的性能。若无缓存，即使大部分输入内容未变，每轮重复提示仍需支付完整的提示成本。

本页涵盖所有影响提示复用与令牌成本的缓存相关配置项。

有关 Anthropic 的定价详情，请参阅：  
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

## 主要配置项

### ``cacheRetention``（模型级与每代理级）

在模型参数中设置缓存保留时长：

````yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "short" # none | short | long
````

每代理级覆盖配置：

````yaml
agents:
  list:
    - id: "alerts"
      params:
        cacheRetention: "none"
````

配置合并顺序：

1. ``agents.defaults.models["provider/model"].params``
2. ``agents.list[].params``（匹配的代理 ID；按键覆盖）

### 已弃用的 ``cacheControlTtl``

旧版值仍被接受并自动映射：

- ``5m`` → ``short``
- ``1h`` → ``long``

新配置请优先使用 ``cacheRetention``。

### ``contextPruning.mode: "cache-ttl"``

在缓存 TTL 窗口期后裁剪过期的工具结果上下文，避免空闲后再次请求时因历史过大而重复缓存。

````yaml
agents:
  defaults:
    contextPruning:
      mode: "cache-ttl"
      ttl: "1h"
````

完整行为详见 [会话裁剪](/concepts/session-pruning)。

### 心跳保活（Heartbeat keep-warm）

心跳机制可维持缓存窗口活跃状态，减少空闲间隔后的重复缓存写入。

````yaml
agents:
  defaults:
    heartbeat:
      every: "55m"
````

每代理级心跳支持位于 ``agents.list[].heartbeat``。

## 供应商行为

### Anthropic（直连 API）

- 支持 ``cacheRetention``。
- 使用 Anthropic API 密钥认证配置时，若未显式设置，OpenClaw 将为 Anthropic 模型引用自动注入 ``cacheRetention: "short"``。

### Amazon Bedrock

- Anthropic Claude 模型引用（``amazon-bedrock/*anthropic.claude*``）支持显式 ``cacheRetention`` 透传。
- 非 Anthropic 的 Bedrock 模型将在运行时强制设为 ``cacheRetention: "none"``。

### OpenRouter 上的 Anthropic 模型

对于 ``openrouter/anthropic/*`` 模型引用，OpenClaw 会在系统/开发者提示块中注入 Anthropic 的 ``cache_control``，以提升提示缓存复用率。

### 其他供应商

若供应商不支持该缓存模式，则 ``cacheRetention`` 不产生任何效果。

## 调优模式

### 混合流量（推荐默认配置）

为主代理保持长期有效的基线缓存，同时对突发性通知类代理禁用缓存：

````yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long"
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m"
    - id: "alerts"
      params:
        cacheRetention: "none"
````

### 成本优先基线

- 设置基线 ``cacheRetention: "short"``。
- 启用 ``contextPruning.mode: "cache-ttl"``。
- 仅对能从热缓存中获益的代理，将心跳间隔设置为低于其 TTL。

## 缓存诊断

OpenClaw 为嵌入式代理运行提供了专用的缓存追踪诊断功能。

### ``diagnostics.cacheTrace`` 配置

````yaml
diagnostics:
  cacheTrace:
    enabled: true
    filePath: "~/.openclaw/logs/cache-trace.jsonl" # optional
    includeMessages: false # default true
    includePrompt: false # default true
    includeSystem: false # default true
````

默认值：

- ``filePath``: ``$OPENCLAW_STATE_DIR/logs/cache-trace.jsonl``
- ``includeMessages``: ``true``
- ``includePrompt``: ``true``
- ``includeSystem``: ``true``

### 环境变量开关（一次性调试）

- ``OPENCLAW_CACHE_TRACE=1`` 启用缓存追踪。
- ``OPENCLAW_CACHE_TRACE_FILE=/path/to/cache-trace.jsonl`` 覆盖输出路径。
- ``OPENCLAW_CACHE_TRACE_MESSAGES=0|1`` 切换是否捕获完整消息载荷。
- ``OPENCLAW_CACHE_TRACE_PROMPT=0|1`` 切换是否捕获提示文本。
- ``OPENCLAW_CACHE_TRACE_SYSTEM=0|1`` 切换是否捕获系统提示。

### 应检查内容

- 缓存追踪事件采用 JSONL 格式，包含如 ``session:loaded``、``prompt:before``、``stream:context`` 和 ``session:after`` 等分阶段快照。
- 每轮缓存令牌影响可在常规使用界面中通过 ``cacheRead`` 和 ``cacheWrite`` 查看（例如 ``/usage full`` 及会话用量汇总）。

## 快速排障

- 多数轮次中 ``cacheWrite`` 值偏高：检查系统提示输入是否不稳定，并确认所用模型/供应商是否支持当前缓存设置。
- ``cacheRetention`` 无效果：确认模型密钥是否匹配 ``agents.defaults.models["provider/model"]``。
- 在 Bedrock Nova/Mistral 请求中使用缓存设置：预期将在运行时强制设为 ``none``。

相关文档：

- [Anthropic](/providers/anthropic)
- [令牌使用与成本](/reference/token-use)
- [会话裁剪](/concepts/session-pruning)
- [网关配置参考](/gateway/configuration-reference)