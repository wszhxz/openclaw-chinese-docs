---
summary: "CLI reference for `openclaw system` (system events, heartbeat, presence)"
read_when:
  - You want to enqueue a system event without creating a cron job
  - You need to enable or disable heartbeats
  - You want to inspect system presence entries
title: "system"
---
# `openclaw system`

网关的系统级辅助工具：排队系统事件、控制心跳，并查看在线状态。

## 常用命令

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
openclaw system heartbeat enable
openclaw system heartbeat last
openclaw system presence
```

## `system event`

在**主**会话上排队一个系统事件。下一个心跳会在提示中注入它作为一个`System:`行。使用`--mode now`立即触发心跳；`next-heartbeat`等待下一个预定的时间点。

标志：

- `--text <text>`: 必需的系统事件文本。
- `--mode <mode>`: `now` 或 `next-heartbeat`（默认）。
- `--json`: 机器可读输出。

## `system heartbeat last|enable|disable`

心跳控制：

- `last`: 显示最后一个心跳事件。
- `enable`: 重新启用心跳（如果之前被禁用）。
- `disable`: 暂停心跳。

标志：

- `--json`: 机器可读输出。

## `system presence`

列出网关当前已知的系统在线状态条目（节点、实例等状态行）。

标志：

- `--json`: 机器可读输出。

## 注意事项

- 需要一个可以通过当前配置访问的正在运行的网关（本地或远程）。
- 系统事件是临时的，不会在重启之间持久化。