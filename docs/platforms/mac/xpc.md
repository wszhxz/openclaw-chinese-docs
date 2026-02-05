---
summary: "macOS IPC architecture for OpenClaw app, gateway node transport, and PeekabooBridge"
read_when:
  - Editing IPC contracts or menu bar app IPC
title: "macOS IPC"
---
# OpenClaw macOS IPC 架构

**当前模型：** 一个本地 Unix 套接字连接 **node 主机服务** 到 **macOS 应用程序** 用于 exec 批准 + `system.run`。存在一个 `openclaw-mac` 调试 CLI 用于发现/连接检查；代理操作仍通过网关 WebSocket 和 `node.invoke` 流转。UI 自动化使用 PeekabooBridge。

## 目标

- 单个 GUI 应用程序实例拥有所有面向 TCC 的工作（通知、屏幕录制、麦克风、语音、AppleScript）。
- 小型自动化表面：网关 + node 命令，加上 PeekabooBridge 用于 UI 自动化。
- 可预测的权限：始终是相同的签名包 ID，由 launchd 启动，因此 TCC 授权会保持。

## 工作原理

### 网关 + node 传输

- 应用程序运行网关（本地模式）并作为 node 连接到它。
- 代理操作通过 `node.invoke` 执行（例如 `system.run`、`system.notify`、`canvas.*`）。

### Node 服务 + 应用程序 IPC

- 无头 node 主机服务连接到网关 WebSocket。
- `system.run` 请求通过本地 Unix 套接字转发到 macOS 应用程序。
- 应用程序在 UI 上下文中执行 exec，根据需要提示，并返回输出。

图表（SCI）：

```
Agent -> Gateway -> Node Service (WS)
                      |  IPC (UDS + token + HMAC + TTL)
                      v
                  Mac App (UI + TCC + system.run)
```

### PeekabooBridge（UI 自动化）

- UI 自动化使用名为 `bridge.sock` 的单独 UNIX 套接字和 PeekabooBridge JSON 协议。
- 主机首选顺序（客户端）：Peekaboo.app → Claude.app → OpenClaw.app → 本地执行。
- 安全性：桥接主机需要允许的 TeamID；仅 DEBUG 的相同 UID 逃生通道由 `PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1` 保护（Peekaboo 约定）。
- 参见：[PeekabooBridge 使用方法](/platforms/mac/peekaboo) 了解详情。

## 操作流程

- 重启/重建：`SIGN_IDENTITY="Apple Development: <Developer Name> (<TEAMID>)" scripts/restart-mac.sh`
  - 终止现有实例
  - Swift 构建 + 打包
  - 写入/引导/启动 LaunchAgent
- 单个实例：如果具有相同包 ID 的另一个实例正在运行，应用程序会提前退出。

## 强化注意事项

- 优先考虑对所有特权表面要求 TeamID 匹配。
- PeekabooBridge：`PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`（仅 DEBUG）可能允许相同 UID 调用者进行本地开发。
- 所有通信仅限本地；不暴露网络套接字。
- TCC 提示仅来自 GUI 应用程序包；在重建过程中保持签名包 ID 稳定。
- IPC 强化：套接字模式 `0600`、令牌、对等 UID 检查、HMAC 挑战/响应、短 TTL。