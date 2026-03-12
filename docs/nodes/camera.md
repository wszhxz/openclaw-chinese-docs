---
summary: "Camera capture (iOS/Android nodes + macOS app) for agent use: photos (jpg) and short video clips (mp4)"
read_when:
  - Adding or modifying camera capture on iOS/Android nodes or macOS
  - Extending agent-accessible MEDIA temp-file workflows
title: "Camera Capture"
---
# 摄像头采集（代理）

OpenClaw 支持在代理工作流中进行**摄像头采集**：

- **iOS 节点**（通过网关配对）：通过 `jpg` 拍摄一张**照片**，或通过 `mp4`（可选音频）录制一段**短视频片段**，使用 `node.invoke`。
- **Android 节点**（通过网关配对）：通过 `jpg` 拍摄一张**照片**，或通过 `mp4`（可选音频）录制一段**短视频片段**，使用 `node.invoke`。
- **macOS 应用**（通过网关作为节点）：通过 `jpg` 拍摄一张**照片**，或通过 `mp4`（可选音频）录制一段**短视频片段**，使用 `node.invoke`。

所有摄像头访问均受**用户可控设置**限制。

## iOS 节点

### 用户设置（默认开启）

- iOS 设置页 → **摄像头** → **允许摄像头访问** (`camera.enabled`)
  - 默认值：**开启**（缺失该键值视为已启用）。
  - 关闭时：`camera.*` 命令返回 `CAMERA_DISABLED`。

### 命令（通过网关 `node.invoke`）

- `camera.list`
  - 响应载荷：
    - `devices`：包含 `{ id, name, position, deviceType }` 的数组

- `camera.snap`
  - 参数：
    - `facing`：`front|back`（默认：`front`）
    - `maxWidth`：数字（可选；iOS 节点上默认为 `1600`）
    - `quality`：`0..1`（可选；默认为 `0.9`）
    - `format`：当前为 `jpg`
    - `delayMs`：数字（可选；默认为 `0`）
    - `deviceId`：字符串（可选；来自 `camera.list`）
  - 响应载荷：
    - `format: "jpg"`
    - `base64: "<...>"`
    - `width`、`height`
  - 载荷保护机制：照片将被重新压缩，以确保 base64 编码后的载荷小于 5 MB。

- `camera.clip`
  - 参数：
    - `facing`：`front|back`（默认：`front`）
    - `durationMs`：数字（默认为 `3000`，上限限制为 `60000`）
    - `includeAudio`：布尔值（默认为 `true`）
    - `format`：当前为 `mp4`
    - `deviceId`：字符串（可选；来自 `camera.list`）
  - 响应载荷：
    - `format: "mp4"`
    - `base64: "<...>"`
    - `durationMs`
    - `hasAudio`

### 前台运行要求

与 `canvas.*` 类似，iOS 节点仅允许在**前台**执行 `camera.*` 命令。后台调用将返回 `NODE_BACKGROUND_UNAVAILABLE`。

### CLI 辅助工具（临时文件 + MEDIA）

获取附件最简便的方式是使用 CLI 辅助工具，它会将解码后的媒体写入临时文件，并打印 `MEDIA:<path>`。

示例：

```bash
openclaw nodes camera snap --node <id>               # default: both front + back (2 MEDIA lines)
openclaw nodes camera snap --node <id> --facing front
openclaw nodes camera clip --node <id> --duration 3000
openclaw nodes camera clip --node <id> --no-audio
```

注意事项：

- `nodes camera snap` 默认为**前后双摄**，以便代理同时获取两个视角。
- 输出文件为临时文件（位于操作系统临时目录中），除非您自行构建封装器。

## Android 节点

### Android 用户设置（默认开启）

- Android 设置面板 → **摄像头** → **允许摄像头访问** (`camera.enabled`)
  - 默认值：**开启**（缺失该键值视为已启用）。
  - 关闭时：`camera.*` 命令返回 `CAMERA_DISABLED`。

### 权限要求

- Android 需要运行时权限：
  - `CAMERA` 同时用于 `camera.snap` 和 `camera.clip`。
  - 当 `includeAudio=true` 时，`RECORD_AUDIO` 用于 `camera.clip`。

若缺少相应权限，应用将在可能时提示用户授权；若被拒绝，则 `camera.*` 请求将失败并返回 `*_PERMISSION_REQUIRED` 错误。

### Android 前台运行要求

与 `canvas.*` 类似，Android 节点仅允许在**前台**执行 `camera.*` 命令。后台调用将返回 `NODE_BACKGROUND_UNAVAILABLE`。

### Android 命令（通过网关 `node.invoke`）

- `camera.list`
  - 响应载荷：
    - `devices`：包含 `{ id, name, position, deviceType }` 的数组

### 载荷保护机制

照片将被重新压缩，以确保 base64 编码后的载荷小于 5 MB。

## macOS 应用

### 用户设置（默认关闭）

macOS 辅助应用提供一个复选框：

- **设置 → 通用 → 允许摄像头访问** (`openclaw.cameraEnabled`)
  - 默认值：**关闭**
  - 关闭时：摄像头请求将返回“用户已禁用摄像头”。

### CLI 辅助工具（节点调用）

使用主 `openclaw` CLI 在 macOS 节点上调用摄像头命令。

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

注意事项：

- `openclaw nodes camera snap` 默认为 `maxWidth=1600`，除非显式覆盖。
- 在 macOS 上，`camera.snap` 将在预热/曝光稳定后等待 `delayMs`（默认 2000ms）再执行拍摄。
- 照片载荷将被重新压缩，以确保 base64 编码后的数据小于 5 MB。

## 安全性与实际限制

- 摄像头和麦克风访问会触发常规的操作系统权限提示（并在 Info.plist 中要求提供用途说明字符串）。
- 视频片段长度受到限制（当前为 `<= 60s`），以避免节点载荷过大（base64 开销 + 消息长度限制）。

## macOS 屏幕视频（系统级）

如需录制**屏幕视频**（而非摄像头视频），请使用 macOS 辅助应用：

```bash
openclaw nodes screen record --node <id> --duration 10s --fps 15   # prints MEDIA:<path>
```

注意事项：

- 需要 macOS 的**屏幕录制**权限（TCC）。