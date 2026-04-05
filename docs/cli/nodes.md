---
summary: "CLI reference for `openclaw nodes` (status, pairing, invoke, camera/canvas/screen)"
read_when:
  - You’re managing paired nodes (cameras, screen, canvas)
  - You need to approve requests or invoke node commands
title: "nodes"
---
# `openclaw nodes`

管理配对的节点（设备）并调用节点功能。

相关：

- 节点概览：[节点](/nodes)
- 相机：[相机节点](/nodes/camera)
- 图像：[图像节点](/nodes/images)

通用选项：

- `--url`, `--token`, `--timeout`, `--json`

## 通用命令

```bash
openclaw nodes list
openclaw nodes list --connected
openclaw nodes list --last-connected 24h
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes reject <requestId>
openclaw nodes rename --node <id|name|ip> --name <displayName>
openclaw nodes status
openclaw nodes status --connected
openclaw nodes status --last-connected 24h
```

`nodes list` 打印待处理/已配对的表格。已配对行包含最近连接时间（Last Connect）。
使用 `--connected` 仅显示当前连接的节点。使用 `--last-connected <duration>` 来
过滤在特定时间段内连接的节点（例如 `24h`, `7d`）。

审批说明：

- `openclaw nodes pending` 仅需配对范围。
- `openclaw nodes approve <requestId>` 继承待处理请求的额外范围要求：
  - 无命令请求：仅配对
  - 非执行节点命令：配对 + 写入
  - `system.run` / `system.run.prepare` / `system.which`: 配对 + 管理员

## 调用

```bash
openclaw nodes invoke --node <id|name|ip> --command <command> --params <json>
```

调用标志：

- `--params <json>`: JSON 对象字符串（默认 `{}`）。
- `--invoke-timeout <ms>`: 节点调用超时（默认 `15000`）。
- `--idempotency-key <key>`: 可选幂等键。
- `system.run` 和 `system.run.prepare` 在此处被阻止；请使用 `exec` 工具配合 `host=node` 进行 Shell 执行。

对于节点上的 Shell 执行，请使用 `exec` 工具配合 `host=node` 代替 `openclaw nodes run`。
`nodes` CLI 现在专注于功能：通过 `nodes invoke` 直接 RPC，以及配对、相机、屏幕、位置、画布和通知。