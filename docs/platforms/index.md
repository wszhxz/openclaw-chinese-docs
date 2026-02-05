---
summary: "Platform support overview (Gateway + companion apps)"
read_when:
  - Looking for OS support or install paths
  - Deciding where to run the Gateway
title: "Platforms"
---
# 平台

OpenClaw 核心是用 TypeScript 编写的。**Node 是推荐的运行时**。
不建议在网关（WhatsApp/Telegram 错误）中使用 Bun。

存在适用于 macOS（菜单栏应用）和移动节点（iOS/Android）的配套应用。Windows 和
Linux 配套应用正在计划中，但网关今天已得到完全支持。
Windows 的原生配套应用也在计划中；通过 WSL2 推荐使用网关。

## 选择您的操作系统

- macOS: [macOS](/platforms/macos)
- iOS: [iOS](/platforms/ios)
- Android: [Android](/platforms/android)
- Windows: [Windows](/platforms/windows)
- Linux: [Linux](/platforms/linux)

## VPS & 托管

- VPS 中心: [VPS 托管](/vps)
- Fly.io: [Fly.io](/platforms/fly)
- Hetzner (Docker): [Hetzner](/platforms/hetzner)
- GCP (Compute Engine): [GCP](/platforms/gcp)
- exe.dev (VM + HTTPS 代理): [exe.dev](/platforms/exe-dev)

## 常用链接

- 安装指南: [入门指南](/start/getting-started)
- 网关运行手册: [网关](/gateway)
- 网关配置: [配置](/gateway/configuration)
- 服务状态: `openclaw gateway status`

## 网关服务安装（CLI）

使用以下任一方法（全部支持）：

- 向导（推荐）: `openclaw onboard --install-daemon`
- 直接: `openclaw gateway install`
- 配置流程: `openclaw configure` → 选择 **网关服务**
- 修复/迁移: `openclaw doctor`（提供安装或修复服务选项）

服务目标取决于操作系统：

- macOS: LaunchAgent (`bot.molt.gateway` 或 `bot.molt.<profile>`; 旧版 `com.openclaw.*`)
- Linux/WSL2: systemd 用户服务 (`openclaw-gateway[-<profile>].service`)