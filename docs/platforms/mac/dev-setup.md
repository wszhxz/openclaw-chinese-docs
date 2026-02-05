---
summary: "Setup guide for developers working on the OpenClaw macOS app"
read_when:
  - Setting up the macOS development environment
title: "macOS Dev Setup"
---
# macOS 开发者设置

本指南涵盖了从源代码构建和运行 OpenClaw macOS 应用程序的必要步骤。

## 先决条件

在构建应用程序之前，请确保已安装以下内容：

1.  **Xcode 26.2+**: Swift 开发所必需。
2.  **Node.js 22+ & pnpm**: 网关、CLI 和打包脚本所必需。

## 1. 安装依赖项

安装项目范围的依赖项：

```bash
pnpm install
```

## 2. 构建和打包应用程序

要构建 macOS 应用程序并将其打包到 `OpenClaw.app` 中，请运行：

```bash
pnpm -F macos run package
```

如果您没有 Apple Developer ID 证书，脚本将自动使用 **ad-hoc signing** (`--adhoc`)。

有关开发运行模式、签名标志和 Team ID 故障排除，请参阅 macOS 应用程序 README：
https://github.com/openclaw/openclaw/blob/main/apps/macos/README.md

> **注意**: Ad-hoc 签名的应用程序可能会触发安全提示。如果应用程序立即崩溃并显示 "Abort trap 6"，请参阅 [故障排除](#troubleshooting) 部分。

## 3. 安装 CLI

macOS 应用程序期望全局 `openclaw` CLI 安装来管理后台任务。

**要安装它（推荐）：**

1.  打开 OpenClaw 应用程序。
2.  转到 **常规** 设置选项卡。
3.  点击 **"安装 CLI"**。

或者，手动安装：

```bash
pnpm -F cli exec openclaw install-cli
```

## 故障排除

### 构建失败：工具链或 SDK 不匹配

macOS 应用程序构建需要最新的 macOS SDK 和 Swift 6.2 工具链。

**系统依赖项（必需）：**

- **软件更新中可用的最新 macOS 版本**（Xcode 26.2 SDK 所需）
- **Xcode 26.2** （Swift 6.2 工具链）

**检查：**

```bash
xcodebuild -version
swift --version
```

如果版本不匹配，请更新 macOS/Xcode 并重新运行构建。

### 在权限授予时应用程序崩溃

如果在尝试允许 **语音识别** 或 **麦克风** 访问时应用程序崩溃，可能是由于损坏的 TCC 缓存或签名不匹配。

**修复：**

1. 重置 TCC 权限：
   ```bash
   tccutil reset All com.openclaw.macos
   ```
2. 如果失败，在 [`scripts/package-mac-app.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-app.sh) 中临时更改 `APP_BUNDLE_ID` 以强制 macOS 使用"干净状态"。

### 网关无限期显示"正在启动..."

如果网关状态保持在"正在启动..."，请检查是否有僵尸进程占用端口：

```bash
lsof -i :3000
```

如果手动运行占用了端口，请停止该进程（Ctrl+C）。作为最后手段，终止您上面找到的 PID。