---
summary: "PeekabooBridge integration for macOS UI automation"
read_when:
  - Hosting PeekabooBridge in OpenClaw.app
  - Integrating Peekaboo via Swift Package Manager
  - Changing PeekabooBridge protocol/paths
title: "Peekaboo Bridge"
---
# Peekaboo 桥 (macOS UI 自动化)

OpenClaw 可以将 **PeekabooBridge** 作为本地、权限感知的 UI 自动化代理。这使得 `peekaboo` 命令行工具能够驱动 UI 自动化，同时复用 macOS 应用的 TCC 权限。

## 这是什么（以及不是什么）

- **主机**：OpenClaw.app 可以作为 PeekabooBridge 主机。
- **客户端**：使用 `peekaboo` 命令行工具（无需单独的 `openclaw ui ...` 接口）。
- **UI**：视觉覆盖层保留在 Peekaboo.app 中；OpenClaw 是一个轻量级的代理主机。

## 启用桥接

在 macOS 应用中：

- 设置 → **启用 Peekaboo 桥**

启用后，OpenClaw 会启动一个本地 UNIX 套接字服务器。若禁用，主机将停止运行，`peekaboo` 将回退到其他可用主机。

## 客户端发现顺序

Peekaboo 客户端通常按以下顺序尝试主机：

1. Peekaboo.app（完整用户体验）
2. Claude.app（如果已安装）
3. OpenClaw.app（轻量级代理）

使用 `peekaboo bridge status --verbose` 查看当前活动的主机以及使用的套接字路径。您可以通过以下命令覆盖：

```bash
export PEEKABOO_BRIDGE_SOCKET=/path/to/bridge.sock
```

## 安全性与权限

- 桥接会验证 **调用方代码签名**；强制执行一个 TeamID 白名单（Peekaboo 主机 TeamID + OpenClaw 应用 TeamID）。
- 请求在约 10 秒后超时。
- 如果缺少必要权限，桥接将返回明确的错误信息，而不是启动系统设置。

## 快照行为（自动化）

快照存储在内存中，并在短时间内自动过期。如果需要更长的保留时间，请从客户端重新捕获。

## 故障排除

- 如果 `peekaboo` 报告 “桥客户端未授权”，请确保客户端已正确签名，或仅在 **调试** 模式下运行主机并设置 `PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`。
- 如果未找到任何主机，请打开其中一个主机应用（Peekaboo.app 或 OpenClaw.app），并确认已授予权限。