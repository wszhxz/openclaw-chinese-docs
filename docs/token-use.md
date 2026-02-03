---
summary: "How OpenClaw builds prompt context and reports token usage + costs"
read_when:
  - Explaining token usage, costs, or context windows
  - Debugging context growth or compaction behavior
title: "Token Use and Costs"
---
# 标记使用与成本

OpenClaw 跟踪的是 **标记**，而非字符。标记是模型特定的，但大多数 OpenAI 风格的模型在英文文本中平均每个标记约 4 个字符。

## 系统提示的构建方式

每次运行时，OpenClaw 都会自行构建系统提示。它包括以下内容：

- 工具列表 + 简要描述
- 技能列表（仅元数据；指令通过 `read` 按需加载）
- 自更新指令
- 工作区 + 启动文件（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、`BOOTSTRAP.md` 新增时）。大文件通过 `agents.defaults.bootstrapMaxChars` 截断（默认：20000）。
- 时间（UTC + 用户时区）
- 回复标签 + 心跳行为
- 运行时元数据（主机/操作系统/模型/思考状态）

完整拆分请参见 [系统提示](/concepts/system-prompt)。

## 上下文窗口中计入的内容

模型接收到的所有内容都会计入上下文限制：

- 系统提示（上述所有部分）
- 对话历史（用户 + 助理消息）
- 工具调用和工具结果
- 附件/转录内容（图片、音频、文件）
- 压缩摘要和修剪产物
- 提供商包装器或安全头信息（不可见，但仍计入）

如需实际拆分（按注入文件、工具、技能和系统提示大小），使用 `/context list` 或 `/context detail`。详情请参见 [上下文](/concepts/context)。

## 查看当前标记使用情况

在聊天中使用以下命令：

- `/status` → 显示包含会话模型、上下文使用情况、最后响应输入/输出标记及 **预估成本**（仅 API 密钥）的 **表情丰富的状态卡片**。
- `/usage off|tokens|full` → 在每条回复末尾附加 **每条响应的使用情况页脚**。
  - 持续会话期间（存储为 `responseUsage`）。
  - OAuth 认证 **隐藏成本**（仅标记）。
- `/usage cost` → 显示本地成本摘要，来自 OpenClaw 会话日志。

其他界面：

- **TUI/Web TUI**：支持 `/status` + `/usage`。
- **CLI**：`openclaw status --usage` 和 `openclaw channels list` 显示提供商配额窗口（非每条响应成本）。

## 成本估算（当显示时）

成本从您的模型定价配置估算：

```
models.providers.<provider>.models[].cost
```

这些是 **每 100 万标记的美元成本**，适用于 `input`、`output`、`cacheRead` 和 `cacheWrite`。如果定价缺失，OpenClaw 仅显示标记。OAuth 标记 **永不显示美元成本**。

## 缓存 TTL 和修剪影响

提供商提示缓存仅在缓存 TTL 窗口内生效。OpenClaw 可选择运行 **缓存 TTL 修剪**：当缓存 TTL 过期后，修剪会话，然后重置缓存窗口，使后续请求可复用新鲜缓存的上下文，而非重新缓存完整历史。这在会话空闲超过 TTL 后能降低缓存写入成本。

在 [网关配置](/gateway/configuration) 中配置，详情请参见 [会话修剪](/concepts/session-pruning)。

心跳可在空闲间隙保持缓存 **温暖**。如果您的模型缓存 TTL 是 `1h`，将心跳间隔设为略低于该值（例如 `55m`），可避免重新缓存完整提示，降低缓存写入成本。

关于 Anthropic API 定价，缓存读取显著低于输入标记成本，而缓存写入则按更高倍数计费。请参见 Anthropic 的提示缓存定价以获取最新费率和 TTL 倍数：
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

## 降低标记压力的技巧

- 使用 `/compact` 总结长会话。
- 在工作流中修剪大型工具输出。
- 保持技能描述简短（技能列表会注入到提示中）。
- 对冗长、探索性工作优先使用较小模型。

技能列表的精确开销公式请参见 [技能](/tools/skills)。