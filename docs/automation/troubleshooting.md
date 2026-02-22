---
summary: "Troubleshoot cron and heartbeat scheduling and delivery"
read_when:
  - Cron did not run
  - Cron ran but no message was delivered
  - Heartbeat seems silent or skipped
title: "Automation Troubleshooting"
---
# 自动化故障排除

使用此页面解决调度器和交付问题 (`cron` + `heartbeat`)。

## 命令梯级

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

良好的输出如下：

- `cron status` 报告启用并有一个未来的 `nextWakeAtMs`。
- 作业已启用并且有一个有效的计划/时区。
- `cron runs` 显示 `ok` 或明确的跳过原因。

常见签名：

- `cron: scheduler disabled; jobs will not run automatically` → 配置/env 中禁用了 cron。
- `cron: timer tick failed` → 调度器滴答崩溃；检查周围的堆栈/日志上下文。
- 运行输出中的 `reason: not-due` → 手动运行未调用 `--force` 且作业尚未到期。

## Cron 触发但无交付

```bash
openclaw cron runs --id <jobId> --limit 20
openclaw cron list
openclaw channels status --probe
openclaw logs --follow
```

良好的输出如下：

- 运行状态为 `ok`。
- 对于隔离作业，交付模式/目标已设置。
- 通道探测报告目标通道已连接。

常见签名：

- 运行成功但交付模式为 `none` → 不期望外部消息。
- 交付目标缺失/无效 (`channel`/`to`) → 内部运行可能成功但跳过外发。
- 通道认证错误 (`unauthorized`, `missing_scope`, `Forbidden`) → 交付被通道凭据/权限阻止。

## 心跳被抑制或跳过

```bash
openclaw system heartbeat last
openclaw logs --follow
openclaw config get agents.defaults.heartbeat
openclaw channels status --probe
```

良好的输出如下：

- 心跳以非零间隔启用。
- 最后一次心跳结果为 `ran`（或跳过原因是可理解的）。

常见签名：

- `heartbeat skipped` 带有 `reason=quiet-hours` → 在 `activeHours` 外部。
- `requests-in-flight` → 主通道繁忙；心跳延迟。
- `empty-heartbeat-file` → 由于 `HEARTBEAT.md` 没有可操作的内容且没有排队的标记 cron 事件而跳过间隔心跳。
- `alerts-disabled` → 可见性设置抑制了外发心跳消息。

## 时区和 activeHours 注意事项

```bash
openclaw config get agents.defaults.heartbeat.activeHours
openclaw config get agents.defaults.heartbeat.activeHours.timezone
openclaw config get agents.defaults.userTimezone || echo "agents.defaults.userTimezone not set"
openclaw cron list
openclaw logs --follow
```

快速规则：

- `Config path not found: agents.defaults.userTimezone` 表示该键未设置；心跳回退到主机时区（如果设置了则为 `activeHours.timezone`）。
- 没有 `--tz` 的 Cron 使用网关主机时区。
- 心跳 `activeHours` 使用配置的时间区解析 (`user`, `local`，或显式的 IANA tz)。
- 没有时区的 ISO 时间戳被视为 UTC 用于 Cron `at` 计划。

常见签名：

- 在主机时区更改后，作业在错误的墙钟时间运行。
- 因为 `activeHours.timezone` 错误，心跳始终在您的白天被跳过。

相关：

- [/automation/cron-jobs](/automation/cron-jobs)
- [/gateway/heartbeat](/gateway/heartbeat)
- [/automation/cron-vs-heartbeat](/automation/cron-vs-heartbeat)
- [/concepts/timezone](/concepts/timezone)