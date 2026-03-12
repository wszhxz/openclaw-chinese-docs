---
summary: "Troubleshoot node pairing, foreground requirements, permissions, and tool failures"
read_when:
  - Node is connected but camera/canvas/screen/exec tools fail
  - You need the node pairing versus approvals mental model
title: "Node Troubleshooting"
---
# 节点故障排查

当节点在状态页中可见，但节点工具无法正常工作时，请使用本页面。

## 命令执行阶梯

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

然后运行节点特定检查：

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
```

健康信号包括：

- 节点已连接，并已为角色 `node` 完成配对。
- `nodes describe` 包含您所调用的功能。
- 执行审批显示了预期的模式/白名单。

## 前台运行要求

`canvas.*`、`camera.*` 和 `screen.*` 在 iOS/Android 节点上仅支持前台运行。

快速检查与修复：

```bash
openclaw nodes describe --node <idOrNameOrIp>
openclaw nodes canvas snapshot --node <idOrNameOrIp>
openclaw logs --follow
```

若看到 `NODE_BACKGROUND_UNAVAILABLE`，请将节点应用切换至前台并重试。

## 权限对照表

| 功能                         | iOS                                     | Android                                      | macOS 节点应用                | 典型错误代码                   |
| ---------------------------- | --------------------------------------- | -------------------------------------------- | ----------------------------- | ------------------------------ |
| `camera.snap`、`camera.clip` | 相机（录制视频片段音频时还需麦克风）     | 相机（录制视频片段音频时还需麦克风）         | 相机（录制视频片段音频时还需麦克风） | `*_PERMISSION_REQUIRED`        |
| `screen.record`              | 屏幕录制（麦克风可选）                   | 屏幕捕获提示（麦克风可选）                   | 屏幕录制                      | `*_PERMISSION_REQUIRED`        |
| `location.get`               | 使用期间或始终允许（取决于模式）         | 根据模式决定前台/后台位置权限                | 位置权限                      | `LOCATION_PERMISSION_REQUIRED` |
| `system.run`                 | 不适用（节点主机路径）                   | 不适用（节点主机路径）                       | 需要执行审批                  | `SYSTEM_RUN_DENIED`            |

## 配对 vs. 审批

这是两个不同的访问控制关卡：

1. **设备配对**：该节点能否连接到网关？
2. **执行审批**：该节点能否运行特定的 shell 命令？

快速检查：

```bash
openclaw devices list
openclaw nodes status
openclaw approvals get --node <idOrNameOrIp>
openclaw approvals allowlist add --node <idOrNameOrIp> "/usr/bin/uname"
```

若缺少配对，请先批准该节点设备。  
若配对正常但 `system.run` 失败，请修正执行审批/白名单设置。

## 常见节点错误代码

- `NODE_BACKGROUND_UNAVAILABLE` → 应用处于后台；请将其切换至前台。
- `CAMERA_DISABLED` → 节点设置中已禁用相机开关。
- `*_PERMISSION_REQUIRED` → 操作系统权限缺失或已被拒绝。
- `LOCATION_DISABLED` → 位置功能已关闭。
- `LOCATION_PERMISSION_REQUIRED` → 请求的位置模式未被授予。
- `LOCATION_BACKGROUND_UNAVAILABLE` → 应用处于后台，但仅拥有“使用期间”权限。
- `SYSTEM_RUN_DENIED: approval required` → 执行请求需要显式审批。
- `SYSTEM_RUN_DENIED: allowlist miss` → 命令被白名单模式阻止。  
  在 Windows 节点主机上，类似 `cmd.exe /c ...` 的 shell-wrapper 形式命令，在白名单模式下会被视为白名单未命中，除非通过询问流程（ask flow）获得明确批准。

## 快速恢复循环

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
```

若问题仍未解决：

- 重新批准设备配对；
- 重新打开节点应用（确保处于前台）；
- 重新授予操作系统权限；
- 重建或调整执行审批策略。

相关链接：

- [/nodes/index](/nodes/index)
- [/nodes/camera](/nodes/camera)
- [/nodes/location-command](/nodes/location-command)
- [/tools/exec-approvals](/tools/exec-approvals)
- [/gateway/pairing](/gateway/pairing)