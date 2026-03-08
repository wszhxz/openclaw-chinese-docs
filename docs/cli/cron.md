---
summary: "CLI reference for `openclaw cron` (schedule and run background jobs)"
read_when:
  - You want scheduled jobs and wakeups
  - You’re debugging cron execution and logs
title: "cron"
---
# `openclaw cron`

管理 Gateway scheduler 的 cron 任务。

相关：

- Cron 任务：[Cron 任务](/automation/cron-jobs)

提示：运行 `openclaw cron --help` 以获取完整的命令集。

注意：隔离的 `cron add` 任务默认使用 `--announce` 交付。使用 `--no-deliver` 保持输出内部化。`--deliver` 仍作为 `--announce` 的已弃用别名保留。

注意：一次性（`--at`）任务默认在成功后删除。使用 `--keep-after-run` 保留它们。

注意：重复任务现在在连续错误后使用指数退避重试（30s → 1m → 5m → 15m → 60m），然后在下次成功运行后恢复正常计划。

注意：保留/清理在配置中控制：

- `cron.sessionRetention`（默认 `24h`）清理已完成的隔离运行会话。
- `cron.runLog.maxBytes` + `cron.runLog.keepLines` 清理 `~/.openclaw/cron/runs/<jobId>.jsonl`。

## 常见编辑

更新交付设置而不更改消息：

```bash
openclaw cron edit <job-id> --announce --channel telegram --to "123456789"
```

禁用隔离任务的交付：

```bash
openclaw cron edit <job-id> --no-deliver
```

为隔离任务启用轻量级引导上下文：

```bash
openclaw cron edit <job-id> --light-context
```

向特定频道广播：

```bash
openclaw cron edit <job-id> --announce --channel slack --to "channel:C1234567890"
```

创建带有轻量级引导上下文的隔离任务：

```bash
openclaw cron add \
  --name "Lightweight morning brief" \
  --cron "0 7 * * *" \
  --session isolated \
  --message "Summarize overnight updates." \
  --light-context \
  --no-deliver
```

`--light-context` 仅适用于隔离的 agent-turn 任务。对于 cron 运行，轻量模式保持引导上下文为空，而不是注入完整的工作区引导集合。