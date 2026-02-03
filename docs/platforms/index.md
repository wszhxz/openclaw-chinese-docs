---
summary: "Platform support overview (Gateway + companion apps)"
read_when:
  - Looking for OS support or install paths
  - Deciding where to run the Gateway
title: "Platforms"
---
# 平台

OpenClaw 核心使用 TypeScript 编写。**Node 是推荐的运行时**。
Bun 不推荐用于网关（WhatsApp/Telegram 存在错误）。

macOS（菜单栏应用）和移动节点（iOS/Android）存在配套应用。Windows 和
Linux 的配套应用计划开发，但网关目前完全支持。
Windows 的原生配套应用也计划开发；建议通过 WSL2 使用网关。

## 选择您的操作系统

- macOS: [macOS](/platforms/macos)
- iOS: [iOS](/platforms/ios)
- Android: [Android](/platforms/android)
- Windows: [Windows](/platforms/windows)
- Linux: [Linux](/platforms/linux)

## VPS 与托管

- VPS 中心: [VPS 托管](/vps)
- Fly.io: [Fly.io](/platforms/fly)
- Hetzner (Docker): [Hetzner](/platforms/hetzner)
- GCP (Compute Engine): [GCP](/platforms/gcp)
- exe.dev (VM + HTTPS 代理): [exe.dev](/platforms/exe-dev)

## 常用链接

- 安装指南: [入门指南](/start/getting-started)
- 网关操作手册: [网关](/gateway)
- 网关配置: [配置](/gateway/configuration)
- 服务状态: `openclaw gateway status`

## 网关服务安装（CLI）

使用以下任一方式（均受支持）:

- 向导（推荐）: `openclaw onboard --install-daemon`
- 直接安装: `openclaw gateway install`
- 配置流程: `openclaw configure` → 选择 **网关服务**
- 修复/迁移: `openclaw doctor`（提供安装或修复服务的选项）

服务目标取决于操作系统:

- macOS: 启动代理（`bot.molt.gateway` 或 `bot.molt.<profile>`；旧版 `com.openclaw.*`）
- Linux/WSL2: systemd 用户服务（`openclaw-gateway[-<profile>].service`）