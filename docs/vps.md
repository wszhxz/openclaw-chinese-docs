---
summary: "VPS hosting hub for OpenClaw (Oracle/Fly/Hetzner/GCP/exe.dev)"
read_when:
  - You want to run the Gateway in the cloud
  - You need a quick map of VPS/hosting guides
title: "VPS Hosting"
---
# VPS托管

本中心链接到支持的VPS/托管指南，并以高级别解释云部署的工作原理。

## 选择提供商

- **Railway** (一键+浏览器设置): [Railway](/railway)
- **Northflank** (一键+浏览器设置): [Northflank](/northflank)
- **Oracle Cloud (Always Free)**: [Oracle](/platforms/oracle) — $0/月 (Always Free, ARM；容量/注册可能挑剔)
- **Fly.io**: [Fly.io](/platforms/fly)
- **Hetzner (Docker)**: [Hetzner](/platforms/hetzner)
- **GCP (Compute Engine)**: [GCP](/platforms/gcp)
- **exe.dev** (VM + HTTPS代理): [exe.dev](/platforms/exe-dev)
- **AWS (EC2/Lightsail/免费层)**: 也运行良好。视频指南:
  https://x.com/techfrenAJ/status/2014934471095812547

## 云设置的工作原理

- **网关运行在VPS上**并拥有状态+工作区。
- 您可以通过**控制UI**或**Tailscale/SSH**从笔记本电脑/手机连接。
- 将VPS视为真理来源并**备份**状态+工作区。
- 默认安全：将网关保留在回环中并通过SSH隧道或Tailscale Serve访问。
  如果绑定到`lan`/`tailnet`，则需要`gateway.auth.token`或`gateway.auth.password`。

远程访问: [网关远程](/gateway/remote)  
平台中心: [平台](/platforms)

## 使用节点与VPS

您可以将网关保留在云端，并在本地设备（Mac/iOS/Android/无头）上配对**节点**。
节点提供本地屏幕/摄像头/画布和`system.run`功能，而网关保留在云端。

文档: [节点](/nodes), [节点CLI](/cli/nodes)