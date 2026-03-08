---
summary: "CLI reference for `openclaw agent` (send one agent turn via the Gateway)"
read_when:
  - You want to run one agent turn from scripts (optionally deliver reply)
title: "agent"
---
# `openclaw agent`

通过 Gateway 运行 agent turn（嵌入式使用 `--local`）。
使用 `--agent <id>` 直接定位已配置的 agent。

相关：

- Agent 发送工具：[Agent send](/tools/agent-send)

## 示例

```bash
openclaw agent --to +15555550123 --message "status update" --deliver
openclaw agent --agent ops --message "Summarize logs"
openclaw agent --session-id 1234 --message "Summarize inbox" --thinking medium
openclaw agent --agent ops --message "Generate report" --deliver --reply-channel slack --reply-to "#reports"
```

## 注意事项

- 当此命令触发 `models.json` 再生时，SecretRef 管理的 provider 凭证会被持久化为非秘密标记（例如 env var 名称或 `secretref-managed`），而不是解析后的秘密明文。