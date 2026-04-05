---
summary: "CLI reference for `openclaw system` (system events, heartbeat, presence)"
read_when:
  - You want to enqueue a system event without creating a cron job
  - You need to enable or disable heartbeats
  - You want to inspect system presence entries
title: "system"
---
# `openclaw system`

Gateway 的系统级辅助工具：入队系统事件、控制心跳以及查看状态。

所有 `system` 子命令均使用 Gateway RPC 并接受共享客户端标志：

- `--url <url>`
- `--token <token>`
- `--timeout <ms>`
- `--expect-final`

## 常用命令

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
openclaw system event --text "Check for urgent follow-ups" --url ws://127.0.0.1:18789 --token "$OPENCLAW_GATEWAY_TOKEN"
openclaw system heartbeat enable
openclaw system heartbeat last
openclaw system presence
```

## `system event`

在 **主** 会话中入队一个系统事件。下一次心跳将把它作为 `System:` 行注入到提示符中。使用 `--mode now` 立即触发心跳；`next-heartbeat` 则等待下一个调度周期。

标志：

- `--text <text>`: 必需的系统事件文本。
- `--mode <mode>`: `now` 或 `next-heartbeat`（默认值）。
- `--json`: 机器可读输出。
- `--url`, `--token`, `--timeout`, `--expect-final`: 共享的 Gateway RPC 标志。

## `system heartbeat last|enable|disable`

心跳控制：

- `last`: 显示上次心跳事件。
- `enable`: 重新开启心跳（如果之前被禁用的话请使用此选项）。
- `disable`: 暂停心跳。

标志：

- `--json`: 机器可读输出。
- `--url`, `--token`, `--timeout`, `--expect-final`: 共享的 Gateway RPC 标志。

## `system presence`

列出 Gateway 当前知晓的系统状态条目（节点、实例及类似的状态行）。

标志：

- `--json`: 机器可读输出。
- `--url`, `--token`, `--timeout`, `--expect-final`: 共享的 Gateway RPC 标志。

## 注意

- 需要运行中的 Gateway，且可通过当前配置访问（本地或远程）。
- 系统事件是临时的，不会在重启后持久化。