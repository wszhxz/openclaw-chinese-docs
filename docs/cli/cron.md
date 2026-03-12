---
summary: "CLI reference for `openclaw cron` (schedule and run background jobs)"
read_when:
  - You want scheduled jobs and wakeups
  - You’re debugging cron execution and logs
title: "cron"
---
# `openclaw cron`

管理网关调度器的 Cron 任务。

相关文档：

- Cron 任务：[Cron 任务](/automation/cron-jobs)

提示：运行 `openclaw cron --help` 可查看完整命令集。

注意：隔离式（isolated）`cron add` 任务默认采用 `--announce` 投递方式。使用 `--no-deliver` 可将输出保留在内部。`--deliver` 仍作为 `--announce` 的已弃用别名保留。

注意：一次性（one-shot）`--at` 任务在成功执行后默认自动删除。使用 `--keep-after-run` 可保留它们。

注意：重复性任务在连续出错后现采用指数退避重试策略（30 秒 → 1 分钟 → 5 分钟 → 15 分钟 → 60 分钟），并在下一次成功运行后恢复常规调度。

注意：保留期 / 清理行为由配置控制：

- `cron.sessionRetention`（默认为 `24h`）用于清理已完成的隔离式运行会话。
- `cron.runLog.maxBytes` + `cron.runLog.keepLines` 用于清理 `~/.openclaw/cron/runs/<jobId>.jsonl`。

## 常见编辑操作

在不更改消息内容的前提下更新投递设置：

```bash
openclaw cron edit <job-id> --announce --channel telegram --to "123456789"
```

禁用隔离式任务的投递功能：

```bash
openclaw cron edit <job-id> --no-deliver
```

为隔离式任务启用轻量级引导上下文（lightweight bootstrap context）：

```bash
openclaw cron edit <job-id> --light-context
```

向指定频道发送通知：

```bash
openclaw cron edit <job-id> --announce --channel slack --to "channel:C1234567890"
```

创建一个带轻量级引导上下文的隔离式任务：

```bash
openclaw cron add \
  --name "Lightweight morning brief" \
  --cron "0 7 * * *" \
  --session isolated \
  --message "Summarize overnight updates." \
  --light-context \
  --no-deliver
```

`--light-context` 仅适用于隔离式 agent-turn 任务。对于 Cron 运行，轻量模式会保持引导上下文为空，而非注入完整的 workspace 引导集合。