---
summary: "How OpenClaw builds prompt context and reports token usage + costs"
read_when:
  - Explaining token usage, costs, or context windows
  - Debugging context growth or compaction behavior
title: "Token Use and Costs"
---
# 令牌使用与费用

OpenClaw 跟踪的是**令牌**，而不是字符。令牌是模型特定的，但对于英文文本，
大多数 OpenAI 风格的模型平均每令牌约 4 个字符。

## 系统提示的构建方式

OpenClaw 在每次运行时都会组装自己的系统提示。它包括：

- 工具列表 + 简短描述
- 技能列表（仅元数据；指令通过 `read` 按需加载）
- 自更新指令
- 工作区 + 引导文件（新文件时：`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、`BOOTSTRAP.md`）。大文件会被 `agents.defaults.bootstrapMaxChars` 截断（默认值：20000）。
- 时间（UTC + 用户时区）
- 回复标签 + 心跳行为
- 运行时元数据（主机/操作系统/模型/思考）

在 [系统提示](/concepts/system-prompt) 中查看完整分解。

## 上下文窗口中计算的内容

模型接收到的所有内容都计入上下文限制：

- 系统提示（上述所有部分）
- 对话历史（用户 + 助手消息）
- 工具调用和工具结果
- 附件/转录（图像、音频、文件）
- 压缩摘要和修剪工件
- 提供商包装器或安全头（不可见，但仍被计算）

要了解实际分解（按注入文件、工具、技能和系统提示大小），请使用 `/context list` 或 `/context detail`。参见 [上下文](/concepts/context)。

## 如何查看当前令牌使用情况

在聊天中使用这些命令：

- `/status` → 带有会话模型、上下文使用情况、最后响应输入/输出令牌的**表情丰富的状态卡片**，以及**预估费用**（仅 API 密钥）。
- `/usage off|tokens|full` → 在每个回复中附加**每响应使用情况页脚**。
  - 每会话持久化（存储为 `responseUsage`）。
  - OAuth 认证**隐藏费用**（仅显示令牌）。
- `/usage cost` → 显示来自 OpenClaw 会话日志的本地费用摘要。

其他界面：

- **TUI/Web TUI：** 支持 `/status` + `/usage`。
- **CLI：** `openclaw status --usage` 和 `openclaw channels list` 显示
  提供商配额窗口（非每响应费用）。

## 费用估算（显示时）

费用根据您的模型定价配置进行估算：

```
models.providers.<provider>.models[].cost
```

这些是 `input`、`output`、`cacheRead` 和
`cacheWrite` 的**每 100 万令牌美元**。如果缺少定价，OpenClaw 仅显示令牌。OAuth 令牌
从不显示美元费用。

## 缓存 TTL 和修剪影响

提供商提示缓存仅在缓存 TTL 窗口内适用。OpenClaw 可以选择性地运行**缓存 TTL 修剪**：缓存 TTL
过期后修剪会话，然后重置缓存窗口，以便后续请求可以重用
刚缓存的上下文，而不是重新缓存完整历史记录。这在会话超过 TTL 后空闲时降低缓存
写入成本。

在 [网关配置](/gateway/configuration) 中配置它，并在 [会话修剪](/concepts/session-pruning) 中查看
行为详情。

心跳可以使缓存在空闲间隔期间保持**温暖**。如果您的模型缓存 TTL
是 `1h`，将心跳间隔设置得略低于该值（例如 `55m`）可以避免
重新缓存完整提示，降低缓存写入成本。

对于 Anthropic API 定价，缓存读取比输入令牌便宜得多，而缓存写入按更高的乘数计费。请参阅 Anthropic 的
提示缓存定价以获取最新费率和 TTL 乘数：
https://docs.anthropic.com/docs/build-with-claude/prompt-caching

### 示例：使用心跳保持 1 小时缓存温暖

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

## 减少令牌压力的技巧

- 使用 `/compact` 来总结长会话。
- 在工作流程中修剪大型工具输出。
- 保持技能描述简短（技能列表被注入到提示中）。
- 在冗长、探索性工作中优先使用较小的模型。

参见 [技能](/tools/skills) 了解确切的技能列表开销公式。