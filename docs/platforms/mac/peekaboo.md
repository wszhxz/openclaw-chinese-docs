---
summary: "PeekabooBridge integration for macOS UI automation"
read_when:
  - Hosting PeekabooBridge in OpenClaw.app
  - Integrating Peekaboo via Swift Package Manager
  - Changing PeekabooBridge protocol/paths
title: "Peekaboo Bridge"
---
# Peekaboo Bridge (macOS UI自动化)

OpenClaw可以托管**PeekabooBridge**作为一个本地、权限感知的UI自动化代理。这使得`peekaboo` CLI能够驱动UI自动化，同时重用macOS应用的TCC权限。

## 这是什么（以及不是什么）

- **主机**: OpenClaw.app可以作为PeekabooBridge主机。
- **客户端**: 使用`peekaboo` CLI（无需单独的`openclaw ui ...`界面）。
- **UI**: 视觉叠加保留在Peekaboo.app中；OpenClaw是一个瘦代理主机。

## 启用桥接

在macOS应用中：

- 设置 → **启用Peekaboo Bridge**

启用后，OpenClaw启动一个本地UNIX套接字服务器。如果禁用，主机将停止，并且`peekaboo`将回退到其他可用主机。

## 客户端发现顺序

Peekaboo客户端通常按以下顺序尝试主机：

1. Peekaboo.app（完整UX）
2. Claude.app（如果已安装）
3. OpenClaw.app（瘦代理）

使用`peekaboo bridge status --verbose`查看哪个主机处于活动状态以及正在使用的套接字路径。您可以使用以下命令覆盖：

```bash
export PEEKABOO_BRIDGE_SOCKET=/path/to/bridge.sock
```

## 安全与权限

- 桥接验证**调用方代码签名**；强制执行TeamID白名单（Peekaboo主机TeamID + OpenClaw应用TeamID）。
- 请求在大约10秒后超时。
- 如果缺少所需权限，桥接将返回清晰的错误消息，而不是启动系统设置。

## 快照行为（自动化）

快照存储在内存中，并在短时间内自动过期。如果您需要更长的保留时间，请从客户端重新捕获。

## 故障排除

- 如果`peekaboo`报告“桥接客户端未授权”，请确保客户端已正确签名，或者仅在**调试**模式下运行主机`PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`。
- 如果找不到任何主机，请打开其中一个主机应用（Peekaboo.app或OpenClaw.app），并确认权限已授予。