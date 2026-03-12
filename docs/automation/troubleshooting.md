---
summary: "Troubleshoot cron and heartbeat scheduling and delivery"
read_when:
  - Cron did not run
  - Cron ran but no message was delivered
  - Heartbeat seems silent or skipped
title: "Automation Troubleshooting"
---
# 自动化故障排除

使用本页面排查调度器和消息投递问题（`cron` + `heartbeat`）。

## 命令阶梯

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

然后运行自动化检查：

```bash
openclaw cron status
openclaw cron list
openclaw system heartbeat last
```

## Cron 未触发

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw logs --follow
```

正常输出如下所示：

- `cron status` 报告为已启用，且存在未来的 `nextWakeAtMs`。
- 任务已启用，并具有有效的计划/时区设置。
- `cron runs` 显示为 `ok` 或明确的跳过原因。

常见异常特征：

- `cron: scheduler disabled; jobs will not run automatically` → 配置/环境变量中禁用了 cron。
- `cron: timer tick failed` → 调度器心跳崩溃；请检查其周围的堆栈/日志上下文。
- `reason: not-due` 出现在运行输出中 → 手动执行时未指定 `--force`，且该任务尚未到达执行时间。

## Cron 已触发但无消息投递

```bash
openclaw cron runs --id <jobId> --limit 20
openclaw cron list
openclaw channels status --probe
openclaw logs --follow
```

正常输出如下所示：

- 运行状态为 `ok`。
- 对于独立任务，已设置投递模式/目标。
- 通道探测报告目标通道已连接。

常见异常特征：

- 运行成功但投递模式为 `none` → 不预期产生任何外部消息。
- 投递目标缺失或无效（`channel`/`to`）→ 内部运行可能成功，但会跳过对外投递。
- 通道认证错误（`unauthorized`、`missing_scope`、`Forbidden`）→ 因通道凭据/权限问题导致投递被阻止。

## 心跳被抑制或跳过

```bash
openclaw system heartbeat last
openclaw logs --follow
openclaw config get agents.defaults.heartbeat
openclaw channels status --probe
```

正常输出如下所示：

- 心跳已启用，且间隔非零。
- 最近一次心跳结果为 `ran`（或跳过原因可理解）。

常见异常特征：

- `heartbeat skipped` 伴随 `reason=quiet-hours` → 超出 `activeHours` 范围。
- `requests-in-flight` → 主通道繁忙；心跳被延迟。
- `empty-heartbeat-file` → 间隔心跳被跳过，因为 `HEARTBEAT.md` 无任何可操作内容，且未排队任何带标签的 cron 事件。
- `alerts-disabled` → 可见性设置抑制了对外发送的心跳消息。

## 时区与 activeHours 的注意事项

```bash
openclaw config get agents.defaults.heartbeat.activeHours
openclaw config get agents.defaults.heartbeat.activeHours.timezone
openclaw config get agents.defaults.userTimezone || echo "agents.defaults.userTimezone not set"
openclaw cron list
openclaw logs --follow
```

快速规则：

- `Config path not found: agents.defaults.userTimezone` 表示该键未设置；心跳将回退至主机时区（若设置了 `activeHours.timezone`，则使用该值）。
- 不含 `--tz` 的 Cron 使用网关主机时区。
- 心跳的 `activeHours` 使用配置的时区解析方式（`user`、`local` 或显式的 IANA 时区标识符）。
- 不含时区信息的 ISO 时间戳在 Cron `at` 计划中被视为 UTC。

常见异常特征：

- 主机时区变更后，任务在错误的本地时间运行。
- 您的白天时段心跳始终被跳过，因为 `activeHours.timezone` 设置错误。

相关文档：

- [/automation/cron-jobs](/automation/cron-jobs)
- [/gateway/heartbeat](/gateway/heartbeat)
- [/automation/cron-vs-heartbeat](/automation/cron-vs-heartbeat)
- [/concepts/timezone](/concepts/timezone)