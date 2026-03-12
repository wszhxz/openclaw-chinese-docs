---
summary: "Platform support overview (Gateway + companion apps)"
read_when:
  - Looking for OS support or install paths
  - Deciding where to run the Gateway
title: "Platforms"
---
# 平台

OpenClaw 核心是用 TypeScript 编写的。**建议使用 Node 作为运行时**。
不建议在网关（WhatsApp/Telegram 错误）中使用 Bun。

macOS（菜单栏应用）和移动节点（iOS/Android）有配套应用程序。Windows 和 Linux 配套应用程序正在计划中，但目前网关已完全支持。
也计划为 Windows 开发原生配套应用程序；建议通过 WSL2 使用网关。

## 选择您的操作系统

- macOS: [macOS](/platforms/macos)
- iOS: [iOS](/platforms/ios)
- Android: [Android](/platforms/android)
- Windows: [Windows](/platforms/windows)
- Linux: [Linux](/platforms/linux)

## VPS & 托管

- VPS 中心: [VPS 托管](/vps)
- Fly.io: [Fly.io](/install/fly)
- Hetzner (Docker): [Hetzner](/install/hetzner)
- GCP (Compute Engine): [GCP](/install/gcp)
- exe.dev (VM + HTTPS 代理): [exe.dev](/install/exe-dev)

## 常见链接

- 安装指南: [入门](/start/getting-started)
- 网关运行手册: [网关](/gateway)
- 网关配置: [配置](/gateway/configuration)
- 服务状态: `openclaw gateway status`

## 网关服务安装 (CLI)

请使用以下方法之一（均受支持）：

- 向导（推荐）: `openclaw onboard --install-daemon`
- 直接: `openclaw gateway install`
- 配置流程: `openclaw configure` → 选择 **网关服务**
- 修复/迁移: `openclaw doctor`（提供安装或修复服务的选项）

服务目标取决于操作系统：

- macOS: LaunchAgent (`ai.openclaw.gateway` 或 `ai.openclaw.<profile>`; 旧版 `com.openclaw.*`)
- Linux/WSL2: systemd 用户服务 (`openclaw-gateway[-<profile>].service`)