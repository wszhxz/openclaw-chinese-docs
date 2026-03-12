---
summary: "CLI reference for `openclaw system` (system events, heartbeat, presence)"
read_when:
  - You want to enqueue a system event without creating a cron job
  - You need to enable or disable heartbeats
  - You want to inspect system presence entries
title: "system"
---
# `openclaw system`

网关的系统级辅助工具：入队系统事件、控制心跳信号，以及查看在线状态。

## 常用命令

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
openclaw system heartbeat enable
openclaw system heartbeat last
openclaw system presence
```

## `system event`

在 **main** 会话中入队一个系统事件。下一次心跳将在提示符中将其注入为一行 `System:`。使用 `--mode now` 可立即触发心跳；而 `next-heartbeat` 则等待下一次计划的时间点。

标志项：

- `--text <text>`：必需的系统事件文本。
- `--mode <mode>`：`now` 或 `next-heartbeat`（默认值）。
- `--json`：机器可读输出。

## `system heartbeat last|enable|disable`

心跳控制：

- `last`：显示最近一次心跳事件。
- `enable`：重新启用心跳（若此前已被禁用，请使用此选项）。
- `disable`：暂停心跳。

标志项：

- `--json`：机器可读输出。

## `system presence`

列出网关当前已知的系统在线状态条目（节点、实例及类似的状态行）。

标志项：

- `--json`：机器可读输出。

## 注意事项

- 需要当前配置可访问（本地或远程）且正在运行的网关。
- 系统事件是临时性的，不会在重启后保留。