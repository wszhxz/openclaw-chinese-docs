---
summary: "Camera capture (iOS node + macOS app) for agent use: photos (jpg) and short video clips (mp4)"
read_when:
  - Adding or modifying camera capture on iOS nodes or macOS
  - Extending agent-accessible MEDIA temp-file workflows
title: "Camera Capture"
---
# 相机捕获 (代理)

OpenClaw 支持 **相机捕获** 用于代理工作流：

- **iOS 节点** (通过网关配对)：通过 `node.invoke` 捕获 **照片** (`jpg`) 或 **短视频片段** (`mp4`，可选音频)。
- **Android 节点** (通过网关配对)：通过 `node.invoke` 捕获 **照片** (`jpg`) 或 **短视频片段** (`mp4`，可选音频)。
- **macOS 应用** (通过网关的节点)：通过 `node.invoke` 捕获 **照片** (`jpg`) 或 **短视频片段** (`mp4`，可选音频)。

所有相机访问都受 **用户控制设置** 的限制。

## iOS 节点

### 用户设置 (默认开启)

- iOS 设置标签 → **相机** → **允许相机** (`camera.enabled`)
  - 默认：**开启** (缺失键视为已启用)。
  - 当关闭时：`camera.*` 命令返回 `CAMERA_DISABLED`。

### 命令 (通过网关 `node.invoke`)

- `camera.list`
  - 响应负载：
    - `devices`: `{ id, name, position, deviceType }` 数组

- `camera.snap`
  - 参数：
    - `facing`: `front|back` (默认: `front`)
    - `maxWidth`: 数字 (可选；默认 iOS 节点上的 `1600`)
    - `quality`: `0..1` (可选；默认 `0.9`)
    - `format`: 目前 `jpg`
    - `delayMs`: 数字 (可选；默认 `0`)
    - `deviceId`: 字符串 (可选；来自 `camera.list`)
  - 响应负载：
    - `format: "jpg"`
    - `base64: "<...>"`
    - `width`, `height`
  - 负载保护：照片会重新压缩以保持 base64 负载在 5 MB 以下。

- `camera.clip`
  - 参数：
    - `facing`: `front|back` (默认: `front`)
    - `durationMs`: 数字 (默认 `3000`，最大值为 `60000`)
    - `includeAudio`: 布尔值 (默认 `true`)
    - `format`: 目前 `mp4`
    - `deviceId`: 字符串 (可选；来自 `camera.list`)
  - 响应负载：
    - `format: "mp4"`
    - `base64: "<...>"`
    - `durationMs`
    - `hasAudio`

### 前台要求

像 `canvas.*` 一样，iOS 节点仅允许在 **前台** 执行 `camera.*` 命令。后台调用返回 `NODE_BACKGROUND_UNAVAILABLE`。

### CLI 辅助工具 (临时文件 + MEDIA)

获取附件的最简单方法是通过 CLI 辅助工具，它将解码后的媒体写入临时文件并打印 `MEDIA:<path>`。

示例：

```bash
openclaw nodes camera snap --node <id>               # default: both front + back (2 MEDIA lines)
openclaw nodes camera snap --node <id> --facing front
openclaw nodes camera clip --node <id> --duration 3000
openclaw nodes camera clip --node <id> --no-audio
```

注意：

- `nodes camera snap` 默认为 **前后** 方向，以便代理获得两个视角。
- 输出文件是临时的（在操作系统临时目录中），除非你构建自己的包装器。

## Android 节点

### 用户设置 (默认开启)

- Android 设置表 → **相机** → **允许相机** (`camera.enabled`)
  - 默认：**开启** (缺失键视为已启用)。
  - 当关闭时：`camera.*` 命令返回 `CAMERA_DISABLED`。

### 权限

- Android 需要运行时权限：
  - `CAMERA` 用于 `camera.snap` 和 `camera.clip`。
  - `RECORD_AUDIO` 用于 `camera.clip` 当 `includeAudio=true`。

如果缺少权限，应用会在可能的情况下提示；如果被拒绝，`camera.*` 请求将失败并返回 `*_PERMISSION_REQUIRED` 错误。

### 前台要求

像 `canvas.*` 一样，Android 节点仅允许在 **前台** 执行 `camera.*` 命令。后台调用返回 `NODE_BACKGROUND_UNAVAILABLE`。

### 负载保护

照片会重新压缩以保持 base64 负载在 5 MB 以下。

## macOS 应用

### 用户设置 (默认关闭)

macOS 伴侣应用提供一个复选框：

- **设置 → 常规 → 允许相机** (`openclaw.cameraEnabled`)
  - 默认：**关闭**
  - 当关闭时：相机请求返回“用户禁用了相机”。

### CLI 辅助工具 (节点调用)

使用主 `openclaw` CLI 在 macOS 节点上调用相机命令。

示例：

```bash
openclaw nodes camera list --node <id>            # list camera ids
openclaw nodes camera snap --node <id>            # prints MEDIA:<path>
openclaw nodes camera snap --node <id> --max-width 1280
openclaw nodes camera snap --node <id> --delay-ms 2000
openclaw nodes camera snap --node <id> --device-id <id>
openclaw nodes camera clip --node <id> --duration 10s          # prints MEDIA:<path>
openclaw nodes camera clip --node <id> --duration-ms 3000      # prints MEDIA:<path> (legacy flag)
openclaw nodes camera clip --node <id> --device-id <id>
openclaw nodes camera clip --node <id> --no-audio
```

注意：

- `openclaw nodes camera snap` 默认为 `maxWidth=1600` 除非被覆盖。
- 在 macOS 上，`camera.snap` 在暖机/曝光稳定后等待 `delayMs` (默认 2000ms) 再进行捕获。
- 照片负载会重新压缩以保持 base64 在 5 MB 以下。

## 安全性和实际限制

- 相机和麦克风访问会触发常规的 OS 权限提示（并需要在 Info.plist 中使用字符串）。
- 视频片段被限制 (目前 `<= 60s`) 以避免过大的节点负载 (base64 开销 + 消息限制)。

## macOS 屏幕视频 (OS 级别)

对于 _屏幕_ 视频（不是相机），使用 macOS 伴侣：

```bash
openclaw nodes screen record --node <id> --duration 10s --fps 15   # prints MEDIA:<path>
```

注意：

- 需要 macOS **屏幕录制** 权限 (TCC)。