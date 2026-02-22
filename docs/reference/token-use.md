---
summary: "How OpenClaw builds prompt context and reports token usage + costs"
read_when:
  - Explaining token usage, costs, or context windows
  - Debugging context growth or compaction behavior
title: "Token Use and Costs"
---
# Token 使用及费用

OpenClaw 跟踪 **tokens**，而不是字符。Tokens 是特定于模型的，但大多数
OpenAI 风格的模型在英文文本中每个 token 平均约为 4 个字符。

## 系统提示词的构建方式

OpenClaw 在每次运行时都会组装自己的系统提示词。它包括：

- 工具列表 + 简短描述
- 技能列表（仅元数据；指令按需加载自 `read`）
- 自更新指令
- 工作区 + 引导文件 (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md` 当为新会话时，加上 `MEMORY.md` 和/或 `memory.md` 当存在时)。大文件会被 `agents.defaults.bootstrapMaxChars` 截断（默认：20000），并且总引导注入量被限制为 `agents.defaults.bootstrapTotalMaxChars`（默认：150000）。`memory/*.md` 文件通过内存工具按需获取，并且不会自动注入。
- 时间（UTC + 用户时区）
- 回复标签 + 心跳行为
- 运行时元数据（主机/操作系统/模型/思考）

详见 [系统提示词](/concepts/system-prompt) 的完整分解。

## 计算上下文窗口的内容

模型接收到的所有内容都计入上下文限制：

- 系统提示词（上述所有部分）
- 对话历史（用户 + 助手消息）
- 工具调用和工具结果
- 附件/记录（图片、音频、文件）
- 压缩摘要和修剪工件
- 提供者包装器或安全头（不可见，但仍计入）

对于图片，OpenClaw 在提供者调用之前对记录/工具图片负载进行下采样。
使用 `agents.defaults.imageMaxDimensionPx`（默认：`1200`）来调整此设置：

- 较低的值通常会减少视觉 token 的使用和负载大小。
- 较高的值会保留更多视觉细节，适用于 OCR/UI 密集型截图。

要获得实际分解（按注入文件、工具、技能和系统提示词大小），使用 `/context list` 或 `/context detail`。详见 [上下文](/concepts/context)。

## 如何查看当前 token 使用情况

在聊天中使用这些命令：

- `/status` → 显示包含会话模型、上下文使用情况、
  最后一次响应输入/输出 token 数量以及 **估算成本**（仅限 API 密钥）的 **带表情符号的状态卡片**。
- `/usage off|tokens|full` → 将 **每响应使用情况页脚** 追加到每个回复。
  - 按会话持久化（存储为 `responseUsage`）。
  - OAuth 认证 **隐藏成本**（仅显示 token 数量）。
- `/usage cost` → 显示来自 OpenClaw 会话日志的本地成本摘要。

其他界面：

- **TUI/Web TUI:** 支持 `/status` + `/usage`。
- **CLI:** `openclaw status --usage` 和 `openclaw channels list` 显示
  提供者配额窗口（不是每响应成本）。

## 成本估算（当显示时）

成本根据您的模型定价配置估算：

```
models.providers.<provider>.models[].cost
```

这些是 `input`, `output`, `cacheRead`, 和
`cacheWrite` 的 **每百万 token 美元**。如果缺少定价，OpenClaw 仅显示 token 数量。OAuth token 永不显示美元成本。

## 缓存 TTL 和修剪影响

提供者提示缓存仅在缓存 TTL 窗口内应用。OpenClaw 可以选择运行 **缓存 TTL 修剪**：它在缓存 TTL 到期后修剪会话，然后重置缓存窗口，以便后续请求可以重用新缓存的上下文而不是重新缓存完整历史记录。这在会话空闲超过 TTL 后降低了缓存写入成本。

在 [网关配置](/gateway/configuration) 中配置它，并在 [会话修剪](/concepts/session-pruning) 中查看行为详细信息。

心跳可以在空闲间隔内保持缓存 **暖**。如果您的模型缓存 TTL 是 `1h`，将心跳间隔设置为略低于该值（例如，`55m`）可以避免重新缓存完整提示，从而降低缓存写入成本。

对于 Anthropic API 定价，缓存读取比输入 token 显著便宜，而缓存写入按更高的倍数计费。查看 Anthropic 的最新费率和 TTL 倍数的提示缓存定价：
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### 示例：使用心跳保持 1 小时缓存暖

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

### 示例：启用 Anthropic 1M 上下文测试版头

Anthropic 的 1M 上下文窗口目前处于测试版。OpenClaw 可以在支持的 Opus 或 Sonnet 模型上启用 `context1m` 时注入所需的 `anthropic-beta` 值。

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

这映射到 Anthropic 的 `context-1m-2025-08-07` 测试版头。

## 减少 token 压力的技巧

- 使用 `/compact` 汇总长时间会话。
- 在工作流中修剪大型工具输出。
- 降低截图密集型会话的 `agents.defaults.imageMaxDimensionPx`。
- 保持技能描述简短（技能列表会被注入到提示词中）。
- 优先使用较小的模型进行冗长的探索性工作。

详见 [技能](/tools/skills) 获取确切的技能列表开销公式。