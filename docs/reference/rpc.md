---
summary: "RPC adapters for external CLIs (signal-cli, legacy imsg) and gateway patterns"
read_when:
  - Adding or changing external CLI integrations
  - Debugging RPC adapters (signal-cli, imsg)
title: "RPC Adapters"
---
# RPC adapters

OpenClaw通过JSON-RPC集成外部CLI。今天使用两种模式。

## 模式A：HTTP守护进程 (signal-cli)

- `signal-cli` 作为守护进程通过HTTP运行JSON-RPC。
- 事件流是SSE (`/api/v1/events`)。
- 健康检查：`/api/v1/check`。
- 当`channels.signal.autoStart=true`时，OpenClaw拥有生命周期。

请参阅[Signal](/channels/signal)以获取设置和端点信息。

## 模式B：stdio子进程 (旧版：imsg)

> **注意：** 对于新的iMessage设置，请改用[BlueBubbles](/channels/bluebubbles)。

- OpenClaw以子进程形式启动`imsg rpc`（旧版iMessage集成）。
- JSON-RPC通过stdin/stdout进行行分隔（每行一个JSON对象）。
- 不需要TCP端口，也不需要守护进程。

使用的核方法：

- `watch.subscribe` → 通知 (`method: "message"`)
- `watch.unsubscribe`
- `send`
- `chats.list`（探测/诊断）

请参阅[iMessage](/channels/imessage)以获取旧版设置和寻址信息 (`chat_id`优先）。

## 适配器指南

- 网关拥有进程（启动/停止与提供商生命周期绑定）。
- 保持RPC客户端的弹性：超时、退出时重启。
- 优先使用稳定ID（例如，`chat_id`）而不是显示字符串。