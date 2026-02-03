---
summary: "How OpenClaw builds prompt context and reports token usage + costs"
read_when:
  - Explaining token usage, costs, or context windows
  - Debugging context growth or compaction behavior
title: "Token Use and Costs"
---
# Token 使用与成本

OpenClaw 跟踪 **tokens**，而不是字符。Tokens 是特定于模型的，但大多数 OpenAI 风格的模型在英文文本中每个 token 平均约为 4 个字符。

## 系统提示的构建方式

OpenClaw 在每次运行时都会组装自己的系统提示。它包括：

- 工具列表 + 简短描述
- 技能列表（仅元数据；指令按需加载，使用 `read`）
- 自更新指令
- 工作区 + 引导文件 (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md` 当为新文件）。大文件会被 `agents.defaults.bootstrapMaxChars` 截断（默认：20000）。
- 时间（UTC + 用户时区）
- 回复标签 + 心跳行为
- 运行时元数据（主机/操作系统/模型/思考过程）

详见 [系统提示](/concepts/system-prompt) 的完整拆分。

## 上下文窗口中的内容统计

模型接收到的所有内容都计入上下文限制：

- 系统提示（上述所有部分）
- 对话历史记录（用户 + 助手消息）
- 工具调用和工具结果
- 附件/转录（图像、音频、文件）
- 压缩摘要和修剪产物
- 提供者包装器或安全头（不可见，但仍计入）

对于实际拆分（按注入文件、工具、技能和系统提示大小），使用 `/context list` 或 `/context detail`。详见 [上下文](/concepts/context)。

## 如何查看当前 token 使用情况

在聊天中使用这些命令：

- `/status` → 显示包含会话模型、上下文使用情况、上次响应输入/输出 token 和 **估算成本**（仅限 API 密钥）的 **表情丰富的状态卡片**。
- `/usage off|tokens|full` → 每个回复附加一个 **每响应使用情况页脚**。
  - 按会话持久化（存储为 `responseUsage`）。
  - OAuth 认证 **隐藏成本**（仅显示 token）。
- `/usage cost` → 显示来自 OpenClaw 会话日志的本地成本摘要。

其他界面：

- **TUI/Web TUI:** 支持 `/status` + `/usage`。
- **CLI:** `openclaw status --usage` 和 `openclaw channels list` 显示
  提供者配额窗口（非每响应成本）。

## 成本估算（当显示时）

成本根据您的模型定价配置估算：

```
models.providers.<provider>.models[].cost
```

这些是 `input`, `output`, `cacheRead`, 和 `cacheWrite` 的 **每百万 token 美元**。如果缺少定价，OpenClaw 仅显示 token。OAuth token 从不显示美元成本。

## 缓存 TTL 和修剪影响

提供者提示缓存仅在缓存 TTL 窗口内应用。OpenClaw 可以选择运行 **cache-ttl 修剪**：在缓存 TTL 到期后修剪会话，然后重置缓存窗口，以便后续请求可以重用新缓存的上下文，而不是重新缓存完整历史记录。这可以降低会话在 TTL 后闲置时的缓存写入成本。

在 [网关配置](/gateway/configuration) 中进行配置，并在 [会话修剪](/concepts/session-pruning) 中查看行为详情。

心跳可以在空闲间隔内保持缓存 **暖**。如果您的模型缓存 TTL 为 `1h`，将心跳间隔设置为略低于该值（例如，`55m`）可以避免重新缓存完整提示，从而降低缓存写入成本。

对于 Anthropic API 定价，缓存读取比输入 token 显著便宜，而缓存写入按更高倍数计费。参阅 Anthropic 的提示缓存定价获取最新费率和 TTL 倍数：
https://docs.anthropic.com/docs/build-with-claude/prompt-caching

### 示例：使用心跳保持 1 小时缓存暖

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-5"
    models:
      "anthropic/claude-opus-4-5":
        params:
          cacheRetention: "long"
    heartbeat:
      every: "55m"
```

## 减少 token 压力的技巧

- 使用 `/compact` 汇总长会话。
- 在工作流中修剪大型工具输出。
- 保持技能描述简短（技能列表被注入到提示中）。
- 优先使用较小的模型进行冗长的探索性工作。

详见 [技能](/tools/skills) 获取确切的技能列表开销公式。