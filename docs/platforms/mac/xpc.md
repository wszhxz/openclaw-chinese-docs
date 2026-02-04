---
summary: "macOS IPC architecture for OpenClaw app, gateway node transport, and PeekabooBridge"
read_when:
  - Editing IPC contracts or menu bar app IPC
title: "macOS IPC"
---
# OpenClaw macOS IPC 架构

**当前模型：** 一个本地 Unix 套接字连接 **节点主机服务** 到 **macOS 应用程序** 用于执行审批 + `system.run`。一个 `openclaw-mac` 调试 CLI 存在用于发现/连接检查；代理操作仍然通过网关 WebSocket 和 `node.invoke` 进行。UI 自动化使用 PeekabooBridge。

## 目标

- 单个 GUI 应用程序实例拥有所有 TCC 面向的工作（通知、屏幕录制、麦克风、语音、AppleScript）。
- 自动化的最小接口：网关 + 节点命令，加上 PeekabooBridge 用于 UI 自动化。
- 可预测的权限：始终是相同的签名捆绑包 ID，由 launchd 启动，因此 TCC 授权会生效。

## 工作原理

### 网关 + 节点传输

- 应用程序运行网关（本地模式）并作为节点连接到它。
- 代理操作通过 `node.invoke` 执行（例如 `system.run`，`system.notify`，`canvas.*`）。

### 节点服务 + 应用程序 IPC

- 一个无头节点主机服务连接到网关 WebSocket。
- `system.run` 请求通过本地 Unix 套接字转发到 macOS 应用程序。
- 应用程序在 UI 上下文中执行 exec，如果需要则提示，并返回输出。

图示（SCI）：

```
Agent -> Gateway -> Node Service (WS)
                      |  IPC (UDS + token + HMAC + TTL)
                      v
                  Mac App (UI + TCC + system.run)
```

### PeekabooBridge（UI 自动化）

- UI 自动化使用一个名为 `bridge.sock` 的单独 UNIX 套接字和 PeekabooBridge JSON 协议。
- 主机首选顺序（客户端端）：Peekaboo.app → Claude.app → OpenClaw.app → 本地执行。
- 安全性：桥接主机需要允许的 TeamID；仅 DEBUG 模式下的相同 UID 逃逸通道受 `PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`（Peekaboo 规范）保护。
- 详情参见：[PeekabooBridge 使用说明](/platforms/mac/peekaboo)。

## 运营流程

- 重启/重建：`SIGN_IDENTITY="Apple Development: <Developer Name> (<TEAMID>)" scripts/restart-mac.sh`
  - 终止现有实例
  - Swift 构建 + 打包
  - 写入/引导/启动 LaunchAgent
- 单实例：如果存在相同捆绑包 ID 的另一个实例，应用程序将提前退出。

## 硬化注意事项

- 尽量要求所有特权表面匹配 TeamID。
- PeekabooBridge：`PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`（仅 DEBUG 模式）可能允许本地开发中的相同 UID 调用者。
- 所有通信保持本地；不暴露网络套接字。
- TCC 提示仅来自 GUI 应用程序捆绑包；保持签名捆绑包 ID 在重建之间稳定。
- IPC 硬化：套接字模式 `0600`，令牌，对等 UID 检查，HMAC 挑战/响应，短 TTL。