---
summary: "VPS hosting hub for OpenClaw (Oracle/Fly/Hetzner/GCP/exe.dev)"
read_when:
  - You want to run the Gateway in the cloud
  - You need a quick map of VPS/hosting guides
title: "VPS Hosting"
---
# VPS托管

此中心链接到支持的VPS/托管指南，并解释云部署的高层次工作原理。

## 选择提供商

- **Railway**（一键+浏览器设置）：[Railway](/railway)
- **Northflank**（一键+浏览器设置）：[Northflank](/northflank)
- **Oracle Cloud（始终免费）**：[Oracle](/platforms/oracle) — 每月$0（始终免费，ARM；容量/注册可能存在问题）
- **Fly.io**：[Fly.io](/platforms/fly)
- **Hetzner（Docker）**：[Hetzner](/platforms/hetzner)
- **GCP（计算引擎）**：[GCP](/platforms/gcp)
- **exe.dev**（VM + HTTPS代理）：[exe.dev](/platforms/exe-dev)
- **AWS（EC2/Lightsail/免费层级）**：同样运行良好。视频指南：
  https://x.com/techfrenAJ/status/2014934471095812547

## 云设置的工作原理

- **网关在VPS上运行，并拥有状态 + 工作区**。
- 您可通过 **控制界面** 或 **Tailscale/SSH** 从笔记本电脑/手机连接。
- 将VPS视为真实来源，并 **备份** 状态 + 工作区。
- 安全默认：保持网关在环回接口上，并通过SSH隧道或Tailscale Serve访问。
  如果绑定到 `lan`/`tailnet`，则需要 `gateway.auth.token` 或 `gateway.auth.password`。

远程访问：[网关远程](/gateway/remote)  
平台中心：[平台](/platforms)

## 使用VPS配合节点

您可以将网关保留在云中，并在本地设备（Mac/iOS/Android/无头设备）上配对 **节点**。节点提供本地屏幕/摄像头/画布和 `system.run` 功能，而网关则保留在云中。

文档：[节点](/nodes)，[节点CLI](/cli/nodes)