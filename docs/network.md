---
summary: "Network hub: gateway surfaces, pairing, discovery, and security"
read_when:
  - You need the network architecture + security overview
  - You are debugging local vs tailnet access or pairing
  - You want the canonical list of networking docs
title: "Network"
---
# 网络中心

此中心链接了关于 OpenClaw 如何在 localhost、LAN 和 tailnet 上连接、配对和保护设备的核心文档。

## 核心模型

大多数操作都通过 Gateway (`openclaw gateway`) 进行，这是一个拥有通道连接和 WebSocket 控制平面的单进程长期运行服务。

- **优先使用 Loopback**：Gateway WS 默认为 `ws://127.0.0.1:18789`。
  非 Loopback 绑定需要有效的网关认证路径：shared-secret token/密码认证，或正确配置的非 Loopback
  `trusted-proxy` 部署。
- **每个主机一个 Gateway** 是推荐的。为了实现隔离，请运行具有隔离配置文件和端口的多个 Gateway（[多个 Gateway](/gateway/multiple-gateways)）。
- **Canvas host** 与 Gateway 在同一端口上提供服务（`/__openclaw__/canvas/`, `/__openclaw__/a2ui/`），当绑定超出 Loopback 时受 Gateway 认证保护。
- **远程访问** 通常是 SSH 隧道或 Tailscale VPN（[远程访问](/gateway/remote)）。

关键参考：

- [Gateway 架构](/concepts/architecture)
- [Gateway 协议](/gateway/protocol)
- [Gateway 运行手册](/gateway)
- [Web 界面 + 绑定模式](/web)

## 配对 + 身份

- [配对概览 (DM + nodes)](/channels/pairing)
- [Gateway 拥有的节点配对](/gateway/pairing)
- [设备 CLI (配对 + token 轮换)](/cli/devices)
- [配对 CLI (DM 审批)](/cli/pairing)

本地信任：

- 直接本地 Loopback 连接可以自动批准配对，以保持同主机 UX 流畅。
- OpenClaw 还有一个狭窄的后端/容器本地自连接路径，用于可信的 shared-secret 辅助流程。
- Tailnet 和 LAN 客户端，包括同主机 Tailnet 绑定，仍然需要明确的配对批准。

## 发现 + 传输

- [发现与传输](/gateway/discovery)
- [Bonjour / mDNS](/gateway/bonjour)
- [远程访问 (SSH)](/gateway/remote)
- [Tailscale](/gateway/tailscale)

## 节点 + 传输

- [节点概览](/nodes)
- [桥接协议 (旧版节点，历史)](/gateway/bridge-protocol)
- [节点运行手册：iOS](/platforms/ios)
- [节点运行手册：Android](/platforms/android)

## 安全

- [安全概览](/gateway/security)
- [Gateway 配置参考](/gateway/configuration)
- [故障排除](/gateway/troubleshooting)
- [Doctor](/gateway/doctor)