---
summary: "macOS IPC architecture for OpenClaw app, gateway node transport, and PeekabooBridge"
read_when:
  - Editing IPC contracts or menu bar app IPC
title: "macOS IPC"
---
# OpenClaw macOS IPC架构

**当前模型：** 一个本地Unix套接字将**节点主机服务**与**macOS应用**连接起来，用于执行审批 + `system.run`。存在一个`openclaw-mac`调试CLI用于发现/连接检查；代理操作仍然通过网关WebSocket和`node.invoke`进行。UI自动化使用PeekabooBridge。

## 目标

- 单个GUI应用程序实例拥有所有面向TCC的工作（通知、屏幕录制、麦克风、语音、AppleScript）。
- 自动化的小界面：网关+节点命令，加上用于UI自动化的PeekabooBridge。
- 可预测的权限：始终是相同的签名包ID，由launchd启动，因此TCC授权保持不变。

## 工作原理

### 网关+节点传输

- 应用程序运行网关（本地模式）并作为节点连接到它。
- 通过`node.invoke`执行代理操作（例如`system.run`、`system.notify`、`canvas.*`）。

### 节点服务+应用IPC

- 无头节点主机服务连接到网关WebSocket。
- `system.run`请求通过本地Unix套接字转发到macOS应用。
- 应用在UI上下文中执行操作，如果需要则提示，并返回输出。

图示（SCI）：

```
Agent -> Gateway -> Node Service (WS)
                      |  IPC (UDS + token + HMAC + TTL)
                      v
                  Mac App (UI + TCC + system.run)
```

### PeekabooBridge（UI自动化）

- UI自动化使用名为`bridge.sock`的单独UNIX套接字和PeekabooBridge JSON协议。
- 主机优先级顺序（客户端侧）：Peekaboo.app → Claude.app → OpenClaw.app → 本地执行。
- 安全性：桥接主机需要允许的TeamID；仅DEBUG模式下的相同UID逃生舱口由`PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`保护（Peekaboo惯例）。
- 详情参见：[PeekabooBridge使用](/platforms/mac/peekaboo)。

## 操作流程

- 重启/重建：`SIGN_IDENTITY="Apple Development: <Developer Name> (<TEAMID>)" scripts/restart-mac.sh`
  - 终止现有实例
  - Swift构建+打包
  - 写入/引导/启动LaunchAgent
- 单实例：如果另一个具有相同包ID的实例正在运行，则应用程序提前退出。

## 强化注意事项

- 优先要求所有特权表面匹配TeamID。
- PeekabooBridge: `PEEKABOO_ALLOW_UNSIGNED_SOCKET_CLIENTS=1`（仅DEBUG模式）可能允许同一UID调用者进行本地开发。
- 所有通信保持本地化；不暴露网络套接字。
- TCC提示仅从GUI应用程序包发起；在重新构建时保持签名包ID稳定。
- IPC强化：套接字模式`0600`、令牌、对等UID检查、HMAC挑战/响应、短TTL。