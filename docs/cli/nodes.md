---
summary: "CLI reference for `openclaw nodes` (list/status/approve/invoke, camera/canvas/screen)"
read_when:
  - You’re managing paired nodes (cameras, screen, canvas)
  - You need to approve requests or invoke node commands
title: "nodes"
---
# `openclaw nodes`

管理已配对的节点（设备）并调用节点功能。

相关文档：

- 节点概述：[节点](/nodes)  
- 摄像头：[摄像头节点](/nodes/camera)  
- 图像：[图像节点](/nodes/images)

常用选项：

- `--url`、`--token`、`--timeout`、`--json`

## 常用命令

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

`nodes list` 输出待配对/已配对节点表。已配对行中包含最近一次连接的时长（上次连接时间）。  
使用 `--connected` 仅显示当前已连接的节点。使用 `--last-connected <duration>` 可按连接持续时间筛选节点（例如 `24h`、`7d`）。

## 调用 / 运行

```bash
openclaw nodes invoke --node <id|name|ip> --command <command> --params <json>
openclaw nodes run --node <id|name|ip> <command...>
openclaw nodes run --raw "git status"
openclaw nodes run --agent main --node <id|name|ip> --raw "git status"
```

调用标志：

- `--params <json>`：JSON 对象字符串（默认为 `{}`）。  
- `--invoke-timeout <ms>`：节点调用超时时间（默认为 `15000`）。  
- `--idempotency-key <key>`：可选的幂等性密钥。

### 类 exec 方式默认行为

`nodes run` 模拟模型的 exec 行为（含默认值与审批机制）：

- 读取 `tools.exec.*`（以及 `agents.list[].tools.exec.*` 中的覆盖项）。  
- 在调用 `system.run` 前，使用 exec 审批机制（`exec.approval.request`）。  
- 当设置了 `tools.exec.node` 时，可省略 `--node`。  
- 需要一个声明了 `system.run` 功能的节点（macOS 辅助应用或无头节点主机）。

标志：

- `--cwd <path>`：工作目录。  
- `--env <key=val>`：环境变量覆盖项（可重复指定）。注意：节点主机忽略 `PATH` 覆盖项（且 `tools.exec.pathPrepend` 不应用于节点主机）。  
- `--command-timeout <ms>`：命令超时时间。  
- `--invoke-timeout <ms>`：节点调用超时时间（默认为 `30000`）。  
- `--needs-screen-recording`：要求屏幕录制权限。  
- `--raw <command>`：运行 shell 字符串（`/bin/sh -lc` 或 `cmd.exe /c`）。  
  在 Windows 节点主机的白名单模式下，`cmd.exe /c` shell 包装器运行需经审批  
  （仅存在白名单条目本身，并不会自动允许该包装器形式）。  
- `--agent <id>`：代理作用域内的审批/白名单（默认为已配置的代理）。  
- `--ask <off|on-miss|always>`、`--security <deny|allowlist|full>`：覆盖项。