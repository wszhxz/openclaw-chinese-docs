---
summary: "Setup guide for developers working on the OpenClaw macOS app"
read_when:
  - Setting up the macOS development environment
title: "macOS Dev Setup"
---
# macOS 开发者设置

本指南涵盖了从源代码构建和运行 OpenClaw macOS 应用程序所需的步骤。

## 先决条件

在构建应用程序之前，请确保已安装以下软件：

1. **Xcode 26.2+**：Swift 开发所需。
2. **Node.js 22+ & pnpm**：网关、CLI 和打包脚本所需。

## 1. 安装依赖项

安装项目范围的依赖项：

```bash
pnpm install
```

## 2. 构建和打包应用程序

要构建 macOS 应用程序并将其打包为 `dist/OpenClaw.app`，请运行：

```bash
./scripts/package-mac-app.sh
```

如果您没有 Apple Developer ID 证书，脚本将自动使用 **临时签名** (`-`)。

有关开发运行模式、签名标志和 Team ID 故障排除的信息，请参阅 macOS 应用程序 README：
[https://github.com/openclaw/openclaw/blob/main/apps/macos/README.md](https://github.com/openclaw/openclaw/blob/main/apps/macos/README.md)

> **注意**：临时签名的应用程序可能会触发安全提示。如果应用程序立即崩溃并显示“Abort trap 6”，请参阅 [故障排除](#troubleshooting) 部分。

## 3. 安装 CLI

macOS 应用程序需要全局安装 `openclaw` CLI 来管理后台任务。

**安装方法（推荐）：**

1. 打开 OpenClaw 应用程序。
2. 转到 **General** 设置选项卡。
3. 点击 **"Install CLI"**。

或者，手动安装：

```bash
npm install -g openclaw@<version>
```

## 故障排除

### 构建失败：工具链或 SDK 不匹配

macOS 应用程序构建需要最新的 macOS SDK 和 Swift 6.2 工具链。

**系统依赖项（必需）：**

- **通过软件更新提供的最新 macOS 版本**（Xcode 26.2 SDK 所需）
- **Xcode 26.2**（Swift 6.2 工具链）

**检查：**

```bash
xcodebuild -version
xcrun swift --version
```

如果版本不匹配，请更新 macOS/Xcode 并重新运行构建。

### 授权时应用程序崩溃

如果您在尝试允许 **Speech Recognition** 或 **Microphone** 访问时应用程序崩溃，可能是由于 TCC 缓存损坏或签名不匹配。

**解决方法：**

1. 重置 TCC 权限：

   ```bash
   tccutil reset All ai.openclaw.mac.debug
   ```

2. 如果上述方法无效，请在 [`scripts/package-mac-app.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-app.sh) 中暂时更改 `BUNDLE_ID` 以强制 macOS 从“干净状态”开始。

### 网关“Starting...”无限期

如果网关状态一直显示为“Starting...”，请检查是否有僵尸进程占用了端口：

```bash
openclaw gateway status
openclaw gateway stop

# If you’re not using a LaunchAgent (dev mode / manual runs), find the listener:
lsof -nP -iTCP:18789 -sTCP:LISTEN
```

如果手动运行占用了端口，请停止该进程（Ctrl+C）。作为最后的手段，杀死上面找到的 PID。