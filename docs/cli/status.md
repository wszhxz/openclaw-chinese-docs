---
summary: "CLI reference for `openclaw status` (diagnostics, probes, usage snapshots)"
read_when:
  - You want a quick diagnosis of channel health + recent session recipients
  - You want a pasteable “all” status for debugging
title: "status"
---
# `openclaw status`

通道与会话的诊断。

```bash
openclaw status
openclaw status --all
openclaw status --deep
openclaw status --usage
```

注意：

- `--deep` 运行实时探针（WhatsApp Web + Telegram + Discord + Slack + Signal）。
- `--usage` 将标准化的提供商使用窗口打印为 `X% left`。
- MiniMax 的原始 `usage_percent` / `usagePercent` 字段表示剩余配额，因此 OpenClaw 在显示前会对其进行反转；当存在时，基于计数的字段优先。`model_remains` 响应优先选择聊天模型条目，必要时从时间戳推导窗口标签，并在计划标签中包含模型名称。
- 当当前会话快照稀疏时，`/status` 可以从最近的转录使用日志中回填 token 和缓存计数器。
- 现有的非零实时值仍然优于转录回退值。
- 当实时会话条目缺少运行时模型标签时，转录回退也可以恢复它。
- 如果该转录模型与所选模型不同，status 将根据恢复的运行时模型解析上下文窗口，而不是根据所选模型。
- 对于提示大小统计，当会话元数据缺失或较小时，转录回退优先选择较大的提示导向总量，以便自定义提供商会话不会坍缩为 `0` token 显示。
- 输出包含每个代理的会话存储（当配置了多个代理时）。
- 概览包括 Gateway + 节点主机服务的安装/运行时状态（如可用）。
- 概览包括更新通道 + git SHA（用于源码检出）。
- 更新信息显示在概览中；如果有可用更新，status 会打印运行 `openclaw update` 的提示（参见 [Updating](/install/updating)）。
- 只读状态显示（`status`, `status --json`, `status --all`）尽可能为其目标配置路径解析支持的 SecretRefs。
- 如果配置了支持的通道 SecretRef 但在当前命令路径中不可用，status 保持只读并报告降级输出，而不是崩溃。
- 人类可读输出显示警告，例如“此命令路径中配置的令牌不可用”，并且 JSON 输出包含 `secretDiagnostics`。
- 当命令本地 SecretRef 解析成功时，status 优先使用解析后的快照，并从最终输出中清除瞬态"secret unavailable"通道标记。
- `status --all` 包含一个 Secrets 概览行和一个诊断部分，总结秘密诊断（为可读性截断），而不停止报告生成。