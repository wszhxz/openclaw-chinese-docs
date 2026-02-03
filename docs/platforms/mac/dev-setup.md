---
summary: "Setup guide for developers working on the OpenClaw macOS app"
read_when:
  - Setting up the macOS development environment
title: "macOS Dev Setup"
---
# macOS 开发者设置

本指南介绍了从源代码构建和运行 OpenClaw macOS 应用程序所需的必要步骤。

## 前提条件

在构建应用程序之前，请确保已安装以下内容：

1. **Xcode 26.2+**：用于 Swift 开发。
2. **Node.js 22+ & pnpm**：用于网关、CLI 和打包脚本。

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

如果您没有 Apple Developer ID 证书，脚本将自动使用 **ad-hoc 签名** (`-`)。

有关开发运行模式、签名标志和团队 ID 故障排除，请参阅 macOS 应用程序的 README：
https://github.com/openclaw/openclaw/blob/main/apps/macos/README.md

> **注意**：使用 ad-hoc 签名的应用程序可能会触发安全提示。如果应用程序立即崩溃并显示 "Abort trap 6"，请参阅 [故障排除](#troubleshooting) 部分。

## 3. 安装 CLI

macOS 应用程序期望全局安装 `openclaw` CLI 以管理后台任务。

**安装方法（推荐）：**

1. 打开 OpenClaw 应用程序。
2. 转到 **"常规"** 设置标签页。
3. 点击 **"安装 CLI"**。

或者，手动安装：

```bash
npm install -g openclaw@<version>
```

## 故障排除

### 构建失败：工具链或 SDK 不匹配

macOS 应用程序构建需要最新的 macOS SDK 和 Swift 6.2 工具链。

**系统依赖项（必需）：**

- **Software Update 中可用的最新 macOS 版本**（由 Xcode 26.2 SDKs 所需）
- **Xcode 26.2**（Swift 6.2 工具链）

**检查：**

```bash
xcodebuild -version
xcrun swift --version
```

如果版本不匹配，请更新 macOS/Xcode 并重新运行构建。

### 应用程序在授予权限时崩溃

如果在尝试允许 **语音识别** 或 **麦克风** 访问时应用程序崩溃，可能是由于 TCC 缓存损坏或签名不匹配。

**解决方法：**

1. 重置 TCC 权限：
   ```bash
   tccutil reset All bot.molt.mac.debug
   ```
2. 如果上述方法失败，请暂时更改 [`scripts/package-mac-app.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-app.sh) 中的 `BUNDLE_ID` 以强制 macOS 从头开始。

### 网关 "Starting..." 无限期持续

如果网关状态停留在 "Starting..."，请检查是否有僵尸进程占用了端口：

```bash
openclaw gateway status
openclaw gateway stop

# 如果您未使用 LaunchAgent（开发模式 / 手动运行），查找监听进程：
lsof -nP -iTCP:18789 -sTCP:LISTEN
```

如果手动运行的进程占用了端口，请停止该进程（Ctrl+C）。作为最后的手段，终止您找到的 PID。