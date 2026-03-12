---
summary: "How OpenClaw builds prompt context and reports token usage + costs"
read_when:
  - Explaining token usage, costs, or context windows
  - Debugging context growth or compaction behavior
title: "Token Use and Costs"
---
# Token 使用量与费用

OpenClaw 跟踪的是 **token**，而非字符。Token 是模型特定的，但大多数类 OpenAI 模型在处理英文文本时平均约为每 token 对应 4 个字符。

## 系统提示词（system prompt）的构建方式

OpenClaw 每次运行时都会动态组装自身的系统提示词。其内容包括：

- 工具列表 + 简短描述  
- 技能列表（仅含元数据；具体指令通过 `read` 按需加载）  
- 自更新指令  
- 工作区 + 引导文件（当新增时为 `AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、`BOOTSTRAP.md`；当存在时还包括 `MEMORY.md` 和/或 `memory.md`）。大文件由 `agents.defaults.bootstrapMaxChars`（默认值：20000）截断，总引导注入量则受 `agents.defaults.bootstrapTotalMaxChars`（默认值：150000）限制。`memory/*.md` 所指文件通过内存工具按需加载，不会自动注入。  
- 时间（UTC + 用户时区）  
- 回复标签 + 心跳行为  
- 运行时元数据（主机/操作系统/模型/推理模式）

详见 [系统提示词](/concepts/system-prompt) 中的完整拆解。

## 上下文窗口中计入的内容

模型接收到的所有内容均计入上下文长度限制：

- 系统提示词（上述所有部分）  
- 对话历史（用户与助手的消息）  
- 工具调用及工具返回结果  
- 附件/转录内容（图像、音频、文件）  
- 压缩摘要与剪枝产物  
- 提供方封装层或安全头信息（虽不可见，但仍被计数）

对于图像，OpenClaw 在向提供方发起调用前会对转录/工具图像载荷进行降采样。  
可通过 `agents.defaults.imageMaxDimensionPx`（默认值：`1200`）调节该行为：

- 较低值通常可减少视觉 token 使用量和载荷大小。  
- 较高值可在 OCR 或 UI 密集型截图中保留更多视觉细节。

如需查看实际用量分解（按注入文件、工具、技能及系统提示词大小分别统计），请使用 `/context list` 或 `/context detail`。参见 [上下文](/concepts/context)。

## 如何查看当前 token 使用量

在聊天中使用以下指令：

- `/status` → 显示一张**富含 emoji 的状态卡片**，包含当前会话所用模型、上下文使用率、上一条响应的输入/输出 token 数，以及**预估费用**（仅限 API 密钥认证用户）。  
- `/usage off|tokens|full` → 在每次回复末尾附加一个**逐条响应用量页脚**。  
  - 该设置在会话内持续生效（以 `responseUsage` 形式存储）。  
  - OAuth 认证会**隐藏费用信息**（仅显示 token 数）。  
- `/usage cost` → 显示 OpenClaw 会话日志中的本地费用汇总。

其他界面支持情况：

- **TUI / Web TUI：** 支持 `/status` 与 `/usage`。  
- **CLI：** `openclaw status --usage` 和 `openclaw channels list` 可显示提供方配额窗口（非逐条响应费用）。

## 费用估算（当启用时）

费用根据您的模型定价配置进行估算：

```
models.providers.<provider>.models[].cost
```

以上为每 100 万 token 的 **美元单价**，分别对应 `input`、`output`、`cacheRead` 和 `cacheWrite`。若缺少定价信息，OpenClaw 仅显示 token 数；OAuth token 永远不显示美元金额。

## 缓存 TTL 与剪枝影响

提供方的提示词缓存仅在缓存 TTL 时间窗口内有效。OpenClaw 可选择性启用 **缓存 TTL 剪枝**：当缓存 TTL 过期后，系统将对会话执行剪枝操作，并重置缓存窗口，使后续请求能够复用最新缓存的上下文，而非重新缓存全部历史。此举可在会话空闲超过 TTL 后降低缓存写入成本。

您可在 [网关配置](/gateway/configuration) 中配置该功能，并在 [会话剪枝](/concepts/session-pruning) 中了解详细行为说明。

心跳机制可在空闲间隔期间保持缓存 **“温热”**。若您的模型缓存 TTL 为 `1h`，将心跳间隔设为略低于该值（例如 `55m`），即可避免重复缓存完整提示词，从而降低缓存写入成本。

在多智能体场景中，您可以共用一个模型配置，并通过 `agents.list[].params.cacheRetention` 为各智能体单独调节缓存行为。

如需全面掌握各项参数，请参阅 [提示词缓存](/reference/prompt-caching)。

对于 Anthropic API 定价，缓存读取费用显著低于输入 token，而缓存写入则按更高倍率计费。最新费率与 TTL 倍率请查阅 Anthropic 官方文档：  
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### 示例：使用心跳机制维持 1 小时缓存热度

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long"
    heartbeat:
      every: "55m"
```

### 示例：混合流量下的按智能体缓存策略

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long" # default baseline for most agents
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # keep long cache warm for deep sessions
    - id: "alerts"
      params:
        cacheRetention: "none" # avoid cache writes for bursty notifications
```

`agents.list[].params` 将叠加于所选模型的 `params` 之上，因此您只需覆盖 `cacheRetention`，其余模型默认值将保持不变。

### 示例：启用 Anthropic 100 万上下文窗口 Beta 头部

Anthropic 的 100 万上下文窗口目前处于 Beta 阶段。当您在支持的 Opus 或 Sonnet 模型上启用 `context1m` 时，OpenClaw 可自动注入所需的 `anthropic-beta` 值。

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

该值映射至 Anthropic 的 `context-1m-2025-08-07` Beta 头部。

此功能仅在对应模型条目中设置了 `context1m: true` 时生效。

前提条件：凭证必须具备长上下文使用资格（API 密钥计费，或已启用“额外用量”的订阅）。否则 Anthropic 将返回 `HTTP 429: rate_limit_error: Extra usage is required for long context requests`。

若您使用 OAuth/订阅令牌（`sk-ant-oat-*`）认证 Anthropic，OpenClaw 将跳过注入 `context-1m-*` Beta 头部，因为 Anthropic 当前对该组合返回 HTTP 401 错误。

## 降低 token 压力的技巧

- 使用 `/compact` 对长时间会话进行摘要。  
- 在工作流中裁剪大型工具输出。  
- 对截图密集型会话调低 `agents.defaults.imageMaxDimensionPx`。  
- 缩短技能描述（技能列表会被注入提示词中）。  
- 在需要大量输出、探索性强的任务中优先选用更小的模型。

有关技能列表开销公式的精确说明，请参阅 [技能](/tools/skills)。