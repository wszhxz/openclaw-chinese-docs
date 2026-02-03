---
summary: "CLI reference for `openclaw nodes` (list/status/approve/invoke, camera/canvas/screen)"
read_when:
  - You’re managing paired nodes (cameras, screen, canvas)
  - You need to approve requests or invoke node commands
title: "nodes"
---
# `openclaw 节点`

管理配对的节点（设备）并调用节点功能。

相关：

- 节点概览：[节点](/nodes)
- 相机：[相机节点](/nodes/camera)
- 图像：[图像节点](/nodes/images)

常用选项：

- `--url`, `--token`, `--timeout`, `--json`

## 常用命令

```bash
openclaw 节点列表
openclaw 节点列表 --connected
openclaw 节点列表 --last-connected 24h
openclaw 节点待处理
openclaw 节点批准 <requestId>
openclaw 节点状态
openclaw 节点状态 --connected
openclaw 节点状态 --last-connected 24h
```

`节点列表` 会打印待处理/配对的表格。配对的行包含最近连接时间（Last Connect）。
使用 `--connected` 仅显示当前连接的节点。使用 `--last-connected <持续时间>` 来
过滤在指定持续时间内连接的节点（例如 `24h`、`7d`）。

## 调用 / 运行

```bash
openclaw 节点调用 --node <id|name|ip> --command <command> --params <json>
openclaw 节点运行 --node <id|name|ip> <command...>
openclaw 节点运行 --raw "git status"
openclaw 节点运行 --agent main --node <id|name|ip> --raw "git status"
```

调用标志：

- `--params <json>`：JSON对象字符串（默认为 `{}`）。
- `--invoke-timeout <ms>`：节点调用超时时间（默认为 `15000`）。
- `--idempotency-key <key>`：可选的幂等性键。

### Exec 风格默认值

`节点运行` 模拟模型的 exec 行为（默认值 + 审批）：

- 读取 `tools.exec.*`（加上 `agents.list[].tools.exec.*` 覆盖）。
- 在调用 `system.run` 之前使用 exec 审批（`exec.approval.request`）。
- 当 `tools.exec.node` 设置时，可以省略 `--node`。
- 需要一个声明支持 `system.run` 的节点（macOS 伴侣应用或无头节点主机）。

标志：

- `--cwd <路径>`：工作目录。
- `--env <键=值>`：环境变量覆盖（可重复）。
- `--command-timeout <ms>`：命令超时时间。
- `--invoke-timeout <ms>`：节点调用超时时间（默认为 `30000`）。
- `--needs-screen-recording`：要求屏幕录制权限。
- `--raw <命令>`：运行 shell 字符串（`/bin/sh -lc` 或 `cmd.exe /c`）。
- `--agent <id>`：代理作用域的审批/白名单（默认为配置的代理）。
- `--ask <off|on-miss|always>`，`--security <deny|allowlist|full>`：覆盖设置。