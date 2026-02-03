---
summary: "Zalo Personal plugin: QR login + messaging via zca-cli (plugin install + channel config + CLI + tool)"
read_when:
  - You want Zalo Personal (unofficial) support in OpenClaw
  - You are configuring or developing the zalouser plugin
title: "Zalo Personal Plugin"
---
# Zalo 个人版（插件）

通过插件支持 Zalo 个人版的 OpenClaw，使用 `zca-cli` 自动化操作普通 Zalo 用户账户。

> **警告：** 非官方自动化可能导致账户被暂停或封禁。请自行承担风险使用。

## 命名

频道 ID 为 `zalouser`，以明确表示这是自动化操作的 **Zalo 个人用户账户**（非官方）。我们保留 `zalo` 用于未来可能的官方 Zalo API 集成。

## 运行环境

此插件在 **网关进程内部** 运行。

如果你使用远程网关，请在 **运行网关的机器** 上安装/配置，然后重启网关。

## 安装

### 选项 A：从 npm 安装

```bash
openclaw plugins install @openclaw/zalouser
```

安装完成后重启网关。

### 选项 B：从本地文件夹安装（开发用途）

```bash
openclaw plugins install ./extensions/zalouser
cd ./extensions/zalouser && pnpm install
```

安装完成后重启网关。

## 前提条件：zca-cli

网关机器必须将 `zca` 添加到 `PATH` 中：

```bash
zca --version
```

## 配置

频道配置位于 `channels.zalouser`（而非 `plugins.entries.*`）：

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

## 命令行界面（CLI）

```bash
openclaw channels login --channel zalouser
openclaw channels logout --channel zalouser
openclaw channels status --probe
openclaw message send --channel zalouser --target <threadId> --message "Hello from OpenClaw"
openclaw directory peers list --channel zalouser --query "name"
```

## 代理工具

工具名称：`zalouser`

操作：`发送`, `图片`, `链接`, `好友`, `群组`, `我`, `状态`