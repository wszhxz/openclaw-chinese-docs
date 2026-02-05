---
summary: "Gateway singleton guard using the WebSocket listener bind"
read_when:
  - Running or debugging the gateway process
  - Investigating single-instance enforcement
title: "Gateway Lock"
---
# 网关锁

最后更新时间: 2025-12-11

## 为什么

- 确保同一主机上的每个基本端口只运行一个网关实例；额外的网关必须使用隔离的配置文件和唯一的端口。
- 在崩溃或SIGKILL的情况下不会留下过时的锁文件。
- 当控制端口已被占用时快速失败并给出清晰的错误。

## 机制

- 网关在启动时立即使用独占的TCP监听器绑定WebSocket监听器（默认 `ws://127.0.0.1:18789`）。
- 如果绑定失败并抛出 `EADDRINUSE`，则启动时抛出 `GatewayLockError("another gateway instance is already listening on ws://127.0.0.1:<port>")`。
- 操作系统会在任何进程退出时自动释放监听器，包括崩溃和SIGKILL——不需要单独的锁文件或清理步骤。
- 关闭时，网关会关闭WebSocket服务器和底层HTTP服务器以尽快释放端口。

## 错误范围

- 如果另一个进程持有该端口，启动时抛出 `GatewayLockError("another gateway instance is already listening on ws://127.0.0.1:<port>")`。
- 其他绑定失败表现为 `GatewayLockError("failed to bind gateway socket on ws://127.0.0.1:<port>: …")`。

## 运营注意事项

- 如果端口被 _另一个_ 进程占用，错误相同；释放端口或使用 `openclaw gateway --port <port>` 选择另一个。
- macOS应用程序仍然在其生成网关之前维护自己的轻量级PID保护；运行时锁由WebSocket绑定强制执行。