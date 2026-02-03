---
summary: "macOS IPC architecture for OpenClaw app, gateway node transport, and PeekabooBridge"
read_when:
  - Editing IPC contracts or menu bar app IPC
title: "macOS IPC"
---
# OpenClaw macOS IPC 架构

**当前模型：** 一个本地 Unix 套接字将 **节点主机服务** 与 **macOS 应用** 连接起来，用于执行批准 + `system.run`。存在一个 `openclaw-mac` 调试 CLI 用于发现/连接检查；代理操作仍通过网关 WebSocket 和 `node.invoke` 流动。UI 自动化使用 PeekabooBridge。

## 目标

- 一个单一的 GUI 应用实例，负责所有面向 TCC 的工作（通知、屏幕录制、麦克风、语音、AppleScript）。
- 一个小型的自动化接口：网关 + 节点命令，加上 Peekab00Bridge 用于 UI 自动化。
- 可预测的权限：始终使用相同的签名捆绑 ID，由 launchd 启动，因此 TCC 权限会保持授予。

## 工作原理

### 网关 + 节点传输

- 应用运行网关（本地模式）并将其作为节点连接到网关。
- 代理操作通过 `node.invoke` 执行（例如 `system.run`、`system.notify`、`canvas.*`）。

### 节点服务 + 应用 IPC

- 一个无头的节点主机服务连接到网关 WebSocket。
- `system.run` 请求通过本地 Unix 套接字转发到 macOS 应用。
- 应用在 UI 上下文中执行 exec，如需提示则进行提示，并返回输出。

图示（SCI）：

```
代理 -> 网关 -> 节点服务（WebSocket）
                      |  IPC（UDS + token + HMAC + TTL）
                      v
                  Mac 应用（UI + TCC + system.run）
```

### PeekabooBridge（UI 自动化）

- UI 自动化使用一个名为 `bridge.sock` 的独立 UNIX 套接字和 PeekabooBridge JSON 协议。
- 主机偏好顺序（客户端侧）：Peekaboo.app → Claude.app → OpenClaw.app → 本地执行。
- 安全性：桥接主机需要允许的 TeamID；仅限调试的相同 UID 逃生通道由 `PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`（Peekaboo 习惯）保护。
- 详情请参阅：[PeekabooBridge 使用方法](/platforms/mac/peekaboo)

## 操作流程

- 重启/重建：`SIGN_IDENTITY="Apple Development: <开发者名称> (<TEAMID>)" scripts/restart-mac.sh`
  - 终止现有实例
  - Swift 构建 + 包装
  - 写入/引导/启动 LaunchAgent
- 单实例：如果另一个具有相同捆绑 ID 的实例正在运行，则应用会提前退出。

## 安全加固说明

- 优先要求所有特权接口匹配 TeamID。
- PeekabooBridge：`PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`（仅限调试）可能允许本地开发的相同 UID 调用者。
- 所有通信保持本地仅用；不暴露任何网络套接字。
- TCC 提示仅来自 GUI 应用捆绑包；在重建过程中保持签名捆绑 ID 稳定。
- IPC 安全加固：套接字模式 `0600`，token，对等 UID 检查，HMAC 挑战/响应，短 TTL。