---
summary: "Troubleshoot node pairing, foreground requirements, permissions, and tool failures"
read_when:
  - Node is connected but camera/canvas/screen/exec tools fail
  - You need the node pairing versus approvals mental model
title: "Node Troubleshooting"
---
# 节点故障排除

当节点在状态中可见但节点工具失败时，请使用此页面。

## 命令检查流程

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

然后运行特定于节点的检查：

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
```

健康信号：

- 节点已连接并针对角色 `node` 完成配对。
- `nodes describe` 包含您正在调用的功能。
- 执行审批显示预期的模式/白名单。

## 前台要求

`canvas.*`、`camera.*` 和 `screen.*` 仅在 iOS/Android 节点上需要前台运行。

快速检查和修复：

```bash
openclaw nodes describe --node <idOrNameOrIp>
openclaw nodes canvas snapshot --node <idOrNameOrIp>
openclaw logs --follow
```

如果您看到 `NODE_BACKGROUND_UNAVAILABLE`，请将节点应用置于前台并重试。

## 权限矩阵

| Capability                   | iOS                                     | Android                                      | macOS node app                | Typical failure code           |
| ---------------------------- | --------------------------------------- | -------------------------------------------- | ----------------------------- | ------------------------------ |
| `camera.snap`, `camera.clip` | 摄像头（剪辑音频需麦克风）           | 摄像头（剪辑音频需麦克风）                | 摄像头（剪辑音频需麦克风） | `*_PERMISSION_REQUIRED`        |
| `screen.record`              | 屏幕录制（麦克风可选）       | 屏幕捕获提示（麦克风可选）       | 屏幕录制              | `*_PERMISSION_REQUIRED`        |
| `location.get`               | 使用期间或始终（取决于模式） | 基于模式的后台/前台定位 | 位置权限           | `LOCATION_PERMISSION_REQUIRED` |
| `system.run`                 | 不适用（节点主机路径）                    | 不适用（节点主机路径）                         | 需要执行审批       | `SYSTEM_RUN_DENIED`            |

## 配对与审批

这些是不同的检查点：

1. **设备配对**：此节点能否连接到网关？
2. **网关节点命令策略**：RPC 命令 ID 是否被 `gateway.nodes.allowCommands` / `denyCommands` 及平台默认值允许？
3. **执行审批**：此节点能否在本地运行特定的 shell 命令？

快速检查：

```bash
openclaw devices list
openclaw nodes status
openclaw approvals get --node <idOrNameOrIp>
openclaw approvals allowlist add --node <idOrNameOrIp> "/usr/bin/uname"
```

如果缺少配对，请先批准节点设备。
如果 `nodes describe` 缺少命令，请检查网关节点命令策略以及节点在连接时是否实际声明了该命令。
如果配对正常但 `system.run` 失败，请修复该节点上的执行审批/白名单。

节点配对是身份/信任检查点，而非针对每条命令的审批界面。对于 `system.run`，每节点策略位于该节点的执行审批文件 (`openclaw approvals get --node ...`) 中，而非网关配对记录中。

对于由审批支持的 `host=node` 运行，网关还将执行绑定到准备好的规范 `systemRunPlan`。如果在批准的运行转发之前，后续调用者修改了命令/cwd 或会话元数据，网关将拒绝该运行作为审批不匹配，而不是信任编辑后的负载。

## 常见节点错误代码

- `NODE_BACKGROUND_UNAVAILABLE` → 应用处于后台；将其置于前台。
- `CAMERA_DISABLED` → 节点设置中禁用了相机切换。
- `*_PERMISSION_REQUIRED` → 操作系统权限缺失/被拒绝。
- `LOCATION_DISABLED` → 定位模式已关闭。
- `LOCATION_PERMISSION_REQUIRED` → 请求的定位模式未获授权。
- `LOCATION_BACKGROUND_UNAVAILABLE` → 应用处于后台，但仅存在“使用期间”权限。
- `SYSTEM_RUN_DENIED: approval required` → 执行请求需要明确审批。
- `SYSTEM_RUN_DENIED: allowlist miss` → 命令被白名单模式阻止。
  在 Windows 节点主机上，像 `cmd.exe /c ...` 这样的 shell 包装器形式在白名单模式下被视为白名单未命中，除非通过询问流程获得批准。

## 快速恢复循环

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
```

如果仍然卡住：

- 重新批准设备配对。
- 重新打开节点应用（前台）。
- 重新授予操作系统权限。
- 重新创建/调整执行审批策略。

相关：

- [/nodes/index](/nodes/index)
- [/nodes/camera](/nodes/camera)
- [/nodes/location-command](/nodes/location-command)
- [/tools/exec-approvals](/tools/exec-approvals)
- [/gateway/pairing](/gateway/pairing)