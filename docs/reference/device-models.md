---
summary: "How OpenClaw vendors Apple device model identifiers for friendly names in the macOS app."
read_when:
  - Updating device model identifier mappings or NOTICE/license files
  - Changing how Instances UI displays device names
title: "Device Model Database"
---
# 设备型号数据库（友好名称）

macOS 伴侣应用通过将 Apple 设备型号标识符（例如 `iPad16,6`、`Mac16,6`）映射为人类可读的名称，在 **实例** 界面中显示友好的 Apple 设备型号名称。

该映射关系以 JSON 格式包含在以下路径中：

- `apps/macos/Sources/OpenClaw/Resources/DeviceModels/`

## 数据来源

我们目前从以下 MIT 许可证仓库中获取映射关系：

- `kyle-seongwoo-jun/apple-device-identifiers`

为确保构建过程的可确定性，JSON 文件被固定到特定的上游提交记录（记录在 `apps/macos/Sources/OpenClaw/Resources/DeviceModels/NOTICE.md` 中）。

## 更新数据库

1. 选择要固定的上游提交记录（iOS 和 macOS 各一个）。
2. 更新 `apps/macos/Sources/OpenClaw/Resources/DeviceModels/NOTICE.md` 中的提交哈希值。
3. 重新下载固定到这些提交记录的 JSON 文件：

```bash
IOS_COMMIT="<commit sha for ios-device-identifiers.json>"
MAC_COMMIT="<commit sha for mac-device-identifiers.json>"

curl -fsSL "https://raw.githubusercontent.com/kyle-seongwoo-jun/apple-device-identifiers/${IOS_COMMIT}/ios-device-identifiers.json" \
  -o apps/macos/Sources/OpenClaw/Resources/DeviceModels/ios-device-identifiers.json

curl -fsSL "https://raw.githubusercontent.com/kyle-seongwoo-jun/apple-device-identifiers/${MAC_COMMIT}/mac-device-identifiers.json" \
  -o apps/macos/Sources/OpenClaw/Resources/DeviceModels/mac-device-identifiers.json
```

4. 确保 `apps/macos/Sources/OpenClaw/Resources/DeviceModels/LICENSE.apple-device-identifiers.txt` 仍与上游一致（如果上游许可证发生变化，请替换该文件）。
5. 验证 macOS 应用程序能否干净地构建（无警告）：

```bash
swift build --package-path apps/macos
```