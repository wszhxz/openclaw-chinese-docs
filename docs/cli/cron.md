---
summary: "CLI reference for `openclaw cron` (schedule and run background jobs)"
read_when:
  - You want scheduled jobs and wakeups
  - You’re debugging cron execution and logs
title: "cron"
---
# `openclaw cron`

管理网关调度器的定时任务。

相关：

- 定时任务：[定时任务](/automation/cron-jobs)

提示：运行 `openclaw cron --help` 查看完整命令列表。

## 常见编辑

更新投递设置而不更改消息：

```bash
openclaw cron edit <job-id> --deliver --channel telegram --to "123456789"
```

禁用孤立任务的投递：

```bash
openclaw cron edit <job-id> --no-deliver
```