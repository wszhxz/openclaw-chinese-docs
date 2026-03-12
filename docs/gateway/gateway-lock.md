---
summary: "Gateway singleton guard using the WebSocket listener bind"
read_when:
  - Running or debugging the gateway process
  - Investigating single-instance enforcement
title: "Gateway Lock"
---
# 网关锁

最后更新时间：2025-12-11

## 原因

- 确保在同一主机上，每个基础端口仅运行一个网关实例；额外的网关必须使用隔离的配置文件和唯一的端口。
- 在崩溃或收到 `SIGKILL` 信号后仍能正常恢复，不会遗留过期的锁文件。
- 当控制端口已被占用时，快速失败并给出明确的错误提示。

## 机制

- 网关在启动时立即绑定 WebSocket 监听器（默认为 `ws://127.0.0.1:18789`），使用独占式 TCP 监听器。
- 如果绑定失败且错误为 `EADDRINUSE`，则启动过程抛出 `GatewayLockError("another gateway instance is already listening on ws://127.0.0.1:<port>")`。
- 操作系统会在进程退出（包括崩溃和 `SIGKILL`）时自动释放该监听器——无需单独的锁文件或清理步骤。
- 关闭过程中，网关会关闭 WebSocket 服务器及底层 HTTP 服务器，从而及时释放端口。

## 错误表现

- 若端口被其他进程占用，启动时将抛出 `GatewayLockError("another gateway instance is already listening on ws://127.0.0.1:<port>")`。
- 其他绑定失败情况则表现为 `GatewayLockError("failed to bind gateway socket on ws://127.0.0.1:<port>: …")`。

## 运维说明

- 如果端口被 _其他_ 进程占用，报错信息相同；请释放该端口，或通过 `openclaw gateway --port <port>` 指定另一个端口。
- macOS 应用在启动网关前仍保留其自身的轻量级 PID 守护机制；而运行时锁则由 WebSocket 绑定强制实施。