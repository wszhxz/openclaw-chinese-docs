---
summary: "Camera capture (iOS/Android nodes + macOS app) for agent use: photos (jpg) and short video clips (mp4)"
read_when:
  - Adding or modifying camera capture on iOS/Android nodes or macOS
  - Extending agent-accessible MEDIA temp-file workflows
title: "Camera Capture"
---
# 相机捕获（agent）

OpenClaw 支持用于 agent 工作流的 **相机捕获**：

- **iOS 节点**（通过 Gateway 配对）：通过 `node.invoke` 捕获 **照片** (`jpg`) 或 **短视频片段** (`mp4`，可选音频)。
- **Android 节点**（通过 Gateway 配对）：通过 `node.invoke` 捕获 **照片** (`jpg`) 或 **短视频片段** (`mp4`，可选音频)。
- **macOS 应用**（通过 Gateway 的节点）：通过 `node.invoke` 捕获 **照片** (`jpg`) 或 **短视频片段** (`mp4`，可选音频)。

所有相机访问均受 **用户控制的设置** 限制。

## iOS 节点

### 用户设置（默认开启）

- iOS 设置标签页 → **相机** → **允许相机** (`camera.enabled`)
  - 默认：**开启**（缺少键视为启用）。
  - 当关闭时：`camera.*` 命令返回 `CAMERA_DISABLED`。

### 命令（通过 Gateway `node.invoke`）

- `camera.list`
  - 响应负载：
    - `devices`: `{ id, name, position, deviceType }` 数组

- `camera.snap`
  - 参数：
    - `facing`: `front|back`（默认：`front`）
    - `maxWidth`: 数字（可选；iOS 节点上默认 `1600`）
    - `quality`: `0..1`（可选；默认 `0.9`）
    - `format`: 当前为 `jpg`
    - `delayMs`: 数字（可选；默认 `0`）
    - `deviceId`: 字符串（可选；来自 `camera.list`）
  - 响应负载：
    - `format: "jpg"`
    - `base64: "<...>"`
    - `width`, `height`
  - 负载保护：照片会被重新压缩以保持 base64 负载在 5 MB 以下。

- `camera.clip`
  - 参数：
    - `facing`: `front|back`（默认：`front`）
    - `durationMs`: 数字（默认 `3000`，限制最大值为 `60000`）
    - `includeAudio`: 布尔值（默认 `true`）
    - `format`: 当前为 `mp4`
    - `deviceId`: 字符串（可选；来自 `camera.list`）
  - 响应负载：
    - `format: "mp4"`
    - `base64: "<...>"`
    - `durationMs`
    - `hasAudio`

### 前台要求

像 `canvas.*` 一样，iOS 节点仅允许在 **前台** 执行 `camera.*` 命令。后台调用返回 `NODE_BACKGROUND_UNAVAILABLE`。

### CLI 辅助工具（临时文件 + MEDIA）

获取附件的最简单方法是通过 CLI 辅助工具，它将解码后的媒体写入临时文件并打印 `MEDIA:<path>`。

示例：

```bash
openclaw nodes camera snap --node <id>               # default: both front + back (2 MEDIA lines)
openclaw nodes camera snap --node <id> --facing front
openclaw nodes camera clip --node <id> --duration 3000
openclaw nodes camera clip --node <id> --no-audio
```

注意：

- `nodes camera snap` 默认为 **双向**，以便 agent 获得两个视角。
- 输出文件是临时的（位于 OS 临时目录中），除非你构建自己的包装器。

## Android 节点

### Android 用户设置（默认开启）

- Android 设置表 → **相机** → **允许相机** (`camera.enabled`)
  - 默认：**开启**（缺少键视为启用）。
  - 当关闭时：`camera.*` 命令返回 `CAMERA_DISABLED`。

### 权限

- Android 需要运行时权限：
  - `CAMERA` 适用于 `camera.snap` 和 `camera.clip` 两者。
  - 当 `includeAudio=true` 时，`camera.clip` 需要 `RECORD_AUDIO`。

如果缺少权限，应用将在可能时提示；如果被拒绝，`camera.*` 请求将失败并返回
`*_PERMISSION_REQUIRED` 错误。

### Android 前台要求

像 `canvas.*` 一样，Android 节点仅允许在 **前台** 执行 `camera.*` 命令。后台调用返回 `NODE_BACKGROUND_UNAVAILABLE`。

### Android 命令（通过 Gateway `node.invoke`）

- `camera.list`
  - 响应负载：
    - `devices`: `{ id, name, position, deviceType }` 数组

### 负载保护

照片会被重新压缩以保持 base64 负载在 5 MB 以下。

## macOS 应用

### 用户设置（默认关闭）

macOS 配套应用暴露了一个复选框：

- **设置 → 通用 → 允许相机** (`openclaw.cameraEnabled`)
  - 默认：**关闭**
  - 当关闭时：相机请求返回 "Camera disabled by user"。

### CLI 辅助工具（node invoke）

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

- `openclaw nodes camera snap` 默认为 `maxWidth=1600`，除非被覆盖。
- 在 macOS 上，`camera.snap` 在预热/曝光稳定后等待 `delayMs`（默认 2000ms）再进行捕获。
- 照片负载会被重新压缩以保持 base64 在 5 MB 以下。

## 安全 + 实际限制

- 相机和麦克风访问会触发常规的 OS 权限提示（并且需要在 Info.plist 中使用字符串）。
- 视频片段被限制（当前为 `<= 60s`），以避免节点负载过大（base64 开销 + 消息限制）。

## macOS 屏幕视频（OS 级别）

对于 _屏幕_ 视频（非相机），使用 macOS 配套应用：

```bash
openclaw nodes screen record --node <id> --duration 10s --fps 15   # prints MEDIA:<path>
```

注意：

- 需要 macOS **屏幕录制** 权限 (TCC)。