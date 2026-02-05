---
summary: "Zalo Personal plugin: QR login + messaging via zca-cli (plugin install + channel config + CLI + tool)"
read_when:
  - You want Zalo Personal (unofficial) support in OpenClaw
  - You are configuring or developing the zalouser plugin
title: "Zalo Personal Plugin"
---
# Zalo Personal (插件)

通过插件，Zalo Personal 支持 OpenClaw，使用 `zca-cli` 自动化一个正常的 Zalo 用户账户。

> **警告:** 非官方自动化可能导致账户被暂停/封禁。请自行承担风险。

## 命名

通道 ID 是 `zalouser` 以明确这是自动化一个 **个人 Zalo 用户账户**（非官方）。我们保留 `zalo` 用于潜在的未来官方 Zalo API 集成。

## 运行位置

此插件运行在 **网关进程内部**。

如果您使用的是远程网关，请在 **运行网关的机器** 上安装/配置它，然后重启网关。

## 安装

### 选项 A: 从 npm 安装

```bash
openclaw plugins install @openclaw/zalouser
```

之后重启网关。

### 选项 B: 从本地文件夹安装（开发）

```bash
openclaw plugins install ./extensions/zalouser
cd ./extensions/zalouser && pnpm install
```

之后重启网关。

## 先决条件: zca-cli

网关机器上必须在 `PATH` 上安装 `zca`:

```bash
zca --version
```

## 配置

通道配置位于 `channels.zalouser`（不是 `plugins.entries.*`）:

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

操作: `send`, `image`, `link`, `friends`, `groups`, `me`, `status`