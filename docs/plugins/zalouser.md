---
summary: "Zalo Personal plugin: QR login + messaging via native zca-js (plugin install + channel config + tool)"
read_when:
  - You want Zalo Personal (unofficial) support in OpenClaw
  - You are configuring or developing the zalouser plugin
title: "Zalo Personal Plugin"
---
# Zalo Personal (插件)

通过插件支持OpenClaw使用Zalo Personal，利用本地`zca-js`来自动化一个普通的Zalo用户账号。

> **警告：** 非官方的自动化可能导致账号被暂停或封禁。请自行承担风险使用。

## 命名

频道ID是`zalouser`，明确表示这是自动化一个**个人Zalo用户账号**（非官方）。我们保留`zalo`用于未来可能的官方Zalo API集成。

## 运行位置

此插件在**网关进程中**运行。

如果您使用的是远程网关，请在**运行网关的机器上**安装/配置它，然后重启网关。

不需要外部的`zca`/`openzca` CLI二进制文件。

## 安装

### 选项A: 从npm安装

```bash
openclaw plugins install @openclaw/zalouser
```

之后重启网关。

### 选项B: 从本地文件夹安装（开发）

```bash
openclaw plugins install ./extensions/zalouser
cd ./extensions/zalouser && pnpm install
```

之后重启网关。

## 配置

频道配置位于`channels.zalouser`（不是`plugins.entries.*`）：

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      dmPolicy: "pairing",
    },
  },
}
```

## CLI

```bash
openclaw channels login --channel zalouser
openclaw channels logout --channel zalouser
openclaw channels status --probe
openclaw message send --channel zalouser --target <threadId> --message "Hello from OpenClaw"
openclaw directory peers list --channel zalouser --query "name"
```

## 代理工具

工具名称: `zalouser`

动作: `send`, `image`, `link`, `friends`, `groups`, `me`, `status`

频道消息动作也支持`react`用于消息反应。