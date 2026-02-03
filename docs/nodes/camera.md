---
summary: "Camera capture (iOS node + macOS app) for agent use: photos (jpg) and short video clips (mp4)"
read_when:
  - Adding or modifying camera capture on iOS nodes or macOS
  - Extending agent-accessible MEDIA temp-file workflows
title: "Camera Capture"
---
# 摄像头捕获（代理）

OpenClaw 支持 **摄像头捕获** 用于代理工作流：

- **iOS 节点**（通过网关配对）：通过 `node.invoke` 捕获 **照片**（`jpg`）或 **短视频片段**（`mp4`，可选音频）。
- **Android 节点**（通过网关配对）：通过 `node.invoke` 捕获 **照片**（`jpg`）或 **短视频片段**（`mp4`，可选音频）。
- **macOS 应用**（通过网关节点）：通过 `node.invoke` 捕获 **照片**（`jpg`）或 **短视频片段**（`mp4`，可选音频）。

所有摄像头访问均受 **用户控制设置** 管理。

## iOS 节点

### 用户设置（默认开启）

- iOS 设置标签 → **摄像头** → **允许摄像头** (`camera.enabled`)
  - 默认：**开启**（缺失键视为已启用）。
  - 关闭时：`camera.*` 命令返回 `CAMERA_DISABLED`。

### 命令（通过网关 `node.invoke`）

- `camera.list`
  - 响应负载：
    - `devices`: `{ id, name, position, deviceType }` 的数组

- `camera.snap`
  - 参数：
    - `facing`: `front|back`（默认：`front`）
    - `maxWidth`: 数字（可选；默认在 iOS 节点上为 `1600`）
    - `quality`: `0..1`（可选；默认 `0.9`）
    - `format`: 当前为 `jpg`
    - `delayMs`: 数字（可选；默认 `0`）
    - `deviceId`: 字符串（可选；来自 `camera.list`）
  - 响应负载：
    - `format: "jpg"`
    - `base64: "<. ..>"`
    - `width`, `height`
  - 负载保护：照片会被重新压缩以确保 base64 负载小于 5 MB。

- `camera.clip`
  - 参数：
    - `facing`: `front|back`（默认：`front`）
    - `durationMs`: 数字（默认 `3000`，最大限制为 `60000`）
    - `includeAudio`: 布尔值（默认 `true`）
    - `format`: 当前为 `mp4`
    - `deviceId`: 字符串（可选；来自 `camera.list`）
  - 响应负载：
    - `format: "mp4"`
    - `base64: "<. ..>"`
    - `durationMs`
    - `hasAudio`

### 前台要求

与 `canvas.*` 一样，iOS 节点仅允许在 **前台** 执行 `camera.*` 命令。后台调用返回 `NODE_BACKGROUND_UNAVAILABLE`。

### CLI 辅助工具（临时文件 + MEDIA）

获取附件最简单的方式是通过 CLI 辅助工具，它会将解码后的媒体写入临时文件并打印 `MEDIA:<路径>`。

示例：

```bash
openclaw nodes camera snap --node <id>               # 默认：前后摄像头（2 个 MEDIA 行）
openclaw nodes camera snap --node <id> --facing front
openclaw nodes camera clip --node <id> --duration 3000
openclaw nodes camera clip --node <id> --no-audio
```

说明：

- `nodes camera snap` 默认使用 **前后摄像头** 以提供代理双视角。
- 输出文件为临时文件（位于操作系统临时目录），除非您自行构建包装器。

## Android 节点

### 用户设置（默认开启）

- Android 设置表单 → **摄像头** → **允许摄像头** (`camera.enabled`)
  - 默认：**开启**（缺失键视为已启用）。
  - 关闭时：`camera.*` 命令返回 `CAMERA_DISABLED`。

### 权限

- Android 需要运行时权限：
  - `CAMERA` 用于 `camera.snap` 和 `camera.clip`。
  - `RECORD_AUDIO` 用于 `camera.clip` 当 `includeAudio=true`。

如果权限缺失，应用会在可能时提示用户；如果被拒绝，`camera.*` 请求将返回 `*_PERMISSION_REQUIRED` 错误。

### 前台要求

与 `canvas.*` 一样，Android 节点仅允许在 **前台** 执行 `camera.*` 命令。后台调用返回 `NODE_BACKGROUND_UNAVAILABLE`。

### 负载保护

照片会被重新压缩以确保 base64 负载小于 5 MB。

## macOS 应用

### 用户设置（默认关闭）

macOS 伴侣应用暴露了一个复选框：

- **设置 → 通用 → 允许摄像头** (`openclaw.cameraEnabled`)
  - 默认：**关闭**
  - 关闭时：摄像头请求返回“摄像头被用户禁用”。

### CLI 辅助工具（节点调用）

使用主 `openclaw` CLI 在 macOS 节点上调用摄像头命令。

示例：

```bash
openclaw nodes camera list --node <id>            # 列出摄像头 ID
openclaw nodes camera snap --node <id>            # 打印 MEDIA:<路径>
openclaw nodes camera snap --node <id> --max-width 1280
openclaw nodes camera snap --node <id> --delay-ms 2000
openclaw nodes camera snap --node <id> --device-id <id>
openclaw nodes camera clip --node <id> --duration 10s          # 打印 MEDIA:<路径>
openclaw nodes camera clip --node <id> --duration-ms 3000      # 打印 MEDIA:<路径>（旧标志）
openclaw nodes camera clip --node <id> --device-id <id>
openclaw nodes camera clip --node <id> --no-audio
```

说明：

- `openclaw nodes camera snap` 默认为 `maxWidth=1600`，除非被覆盖。
- 在 macOS 上，`camera.snap` 在预热/曝光稳定后等待 `delayMs`（默认 2000ms）再进行捕获。
- 照片负载会被重新压缩以确保 base64 小于 5 MB。

## 安全性 + 实用限制

- 摄像头和麦克风访问会触发常规的操作系统权限提示（并需要 Info.plist 中的使用字符串）。
- 视频片段被限制（目前 `<= 60 秒`）以避免过大节点负载（base64 开销 + 消息限制）。

## macOS 屏幕视频（操作系统级别）

对于 _屏幕_ 视频（非摄像头），使用 macOS 伴侣应用：

```bash
openclaw nodes screen record --node