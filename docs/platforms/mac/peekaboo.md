---
summary: "PeekabooBridge integration for macOS UI automation"
read_when:
  - Hosting PeekabooBridge in OpenClaw.app
  - Integrating Peekaboo via Swift Package Manager
  - Changing PeekabooBridge protocol/paths
title: "Peekaboo Bridge"
---
# Peekaboo Bridge（macOS UI 自动化）

OpenClaw 可以托管 **PeekabooBridge** 作为本地的、具有权限感知的 UI 自动化代理。这使得 `peekaboo` CLI 能够驱动 UI 自动化，同时重用 macOS 应用的 TCC 权限。

## 这是什么（以及不是什么）

- **主机**：OpenClaw.app 可以充当 PeekabooBridge 主机。
- **客户端**：使用 `peekaboo` CLI（没有单独的 `openclaw ui ...` 界面）。
- **UI**：视觉覆盖层保留在 Peekaboo.app 中；OpenClaw 是一个轻量级代理主机。

## 启用桥接

在 macOS 应用中：

- 设置 → **启用 Peekaboo 桥接**

启用后，OpenClaw 会启动一个本地 UNIX 套接字服务器。如果禁用，主机会停止，`peekaboo` 将回退到其他可用主机。

## 客户端发现顺序

Peekaboo 客户端通常按此顺序尝试主机：

1. Peekaboo.app（完整用户体验）
2. Claude.app（如果已安装）
3. OpenClaw.app（轻量级代理）

使用 `peekaboo bridge status --verbose` 查看哪个主机处于活动状态以及正在使用哪个套接字路径。您可以使用以下方式覆盖：

```bash
export PEEKABOO_BRIDGE_SOCKET=/path/to/bridge.sock
```

## 安全性与权限

- 桥接验证 **调用者代码签名**；强制执行 TeamID 白名单（Peekaboo 主机 TeamID + OpenClaw 应用 TeamID）。
- 请求在约 10 秒后超时。
- 如果缺少必要权限，桥接会返回清晰的错误消息，而不是启动系统设置。

## 快照行为（自动化）

快照存储在内存中，并在短时间窗口后自动过期。如果您需要更长的保留时间，请从客户端重新捕获。

## 故障排除

- 如果 `peekaboo` 报告"桥接客户端未授权"，请确保客户端正确签名，或仅在 **调试** 模式下使用 `PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1` 运行主机。
- 如果找不到主机，请打开其中一个主机应用（Peekaboo.app 或 OpenClaw.app）并确认已授予权限。