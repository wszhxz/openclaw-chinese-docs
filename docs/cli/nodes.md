---
summary: "CLI reference for `openclaw nodes` (list/status/approve/invoke, camera/canvas/screen)"
read_when:
  - You’re managing paired nodes (cameras, screen, canvas)
  - You need to approve requests or invoke node commands
title: "nodes"
---
# `openclaw nodes`

管理配对节点（设备）并调用节点功能。

相关：

- 节点概览：[Nodes](/nodes)
- 相机：[Camera nodes](/nodes/camera)
- 图像：[Image nodes](/nodes/images)

通用选项：

- `--url`, `--token`, `--timeout`, `--json`

## 通用命令

```bash
openclaw nodes list
openclaw nodes list --connected
openclaw nodes list --last-connected 24h
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes status
openclaw nodes status --connected
openclaw nodes status --last-connected 24h
```

`nodes list` 打印待处理/配对表。配对行包含最近连接时间（Last Connect）。
使用 `--connected` 仅显示当前连接的节点。使用 `--last-connected <duration>` 过滤在指定时间内连接的节点（例如 `24h`, `7d`）。

## 调用 / 运行

```bash
openclaw nodes invoke --node <id|name|ip> --command <command> --params <json>
openclaw nodes run --node <id|name|ip> <command...>
openclaw nodes run --raw "git status"
openclaw nodes run --agent main --node <id|name|ip> --raw "git status"
```

调用标志：

- `--params <json>`: JSON 对象字符串（默认 `{}`）。
- `--invoke-timeout <ms>`: 节点调用超时（默认 `15000`）。
- `--idempotency-key <key>`: 可选的幂等键。

### 执行风格默认值

`nodes run` 镜像模型的执行行为（默认值 + 批准）：

- 读取 `tools.exec.*`（加上 `agents.list[].tools.exec.*` 覆盖）。
- 在调用 `system.run` 之前使用执行批准（`exec.approval.request`）。
- 当设置 `tools.exec.node` 时，可省略 `--node`。
- 需要通告 `system.run` 的节点（macOS 配套应用或无头节点主机）。

标志：

- `--cwd <path>`: 工作目录。
- `--env <key=val>`: 环境变量覆盖（可重复）。注意：节点主机忽略 `PATH` 覆盖（且 `tools.exec.pathPrepend` 不适用于节点主机）。
- `--command-timeout <ms>`: 命令超时。
- `--invoke-timeout <ms>`: 节点调用超时（默认 `30000`）。
- `--needs-screen-recording`: 需要屏幕录制权限。
- `--raw <command>`: 运行 shell 字符串（`/bin/sh -lc` 或 `cmd.exe /c`）。
  在 Windows 节点主机的白名单模式下，`cmd.exe /c` shell 包装器运行需要批准
  （仅白名单条目不会自动允许包装器形式）。
- `--agent <id>`: 代理范围的批准/白名单（默认为配置的代理）。
- `--ask <off|on-miss|always>`, `--security <deny|allowlist|full>`: 覆盖。