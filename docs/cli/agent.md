---
summary: "CLI reference for `openclaw agent` (send one agent turn via the Gateway)"
read_when:
  - You want to run one agent turn from scripts (optionally deliver reply)
title: "agent"
---
# `openclaw agent`

通过网关运行一个智能体（Agent）回合（嵌入式场景请使用 `--local`）。
使用 `--agent <id>` 可直接调用已配置的智能体。

相关：

- 智能体发送工具：[Agent send](/tools/agent-send)

## 示例

```bash
openclaw agent --to +15555550123 --message "status update" --deliver
openclaw agent --agent ops --message "Summarize logs"
openclaw agent --session-id 1234 --message "Summarize inbox" --thinking medium
openclaw agent --agent ops --message "Generate report" --deliver --reply-channel slack --reply-to "#reports"
```

## 注意事项

- 当该命令触发 `models.json` 重新生成时，由 SecretRef 管理的提供方凭据将被持久化为非密文标记（例如环境变量名或 `secretref-managed`），而非解析后的密文明文。