---
summary: "Network hub: gateway surfaces, pairing, discovery, and security"
read_when:
  - You need the network architecture + security overview
  - You are debugging local vs tailnet access or pairing
  - You want the canonical list of networking docs
title: "Network"
---
# 网络枢纽

此枢纽链接了OpenClaw如何在本地主机、局域网和尾网中连接、配对和安全设备的核心文档。

## 核心模型

- [网关架构](/concepts/architecture)
- [网关协议](/gateway/protocol)
- [网关操作指南](/gateway)
- [Web界面 + 绑定模式](/web)

## 配对 + 身份

- [配对概述（DM + 节点）](/start/pairing)
- [网关拥有节点的配对](/gateway/pairing)
- [设备CLI（配对 + 令牌轮换）](/cli/devices)
- [配对CLI（DM审批）](/cli/pairing)

本地信任：

- 本地连接（回环或网关主机自身的尾网地址）可自动批准配对，以保持同主机用户体验流畅。
- 非本地尾网/局域网客户端仍需显式配对批准。

## 发现 + 传输

- [发现与传输](/gateway/discovery)
- [Bonjour / mDNS](/gateway/bonjour)
- [远程访问（SSH）](/gateway/remote)
- [Tailscale](/gateway/tailscale)

## 节点 + 传输

- [节点概述](/nodes)
- [桥接协议（旧版节点）](/gateway/bridge-protocol)
- [节点操作指南：iOS](/platforms/ios)
- [节点操作指南：Android](/platforms/android)

## 安全

- [安全概述](/gateway/security)
- [网关配置参考](/gateway/configuration)
- [故障排除](/gateway/troubleshooting)
- [诊断工具](/gateway/doctor)