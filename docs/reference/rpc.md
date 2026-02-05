---
summary: "RPC adapters for external CLIs (signal-cli, legacy imsg) and gateway patterns"
read_when:
  - Adding or changing external CLI integrations
  - Debugging RPC adapters (signal-cli, imsg)
title: "RPC Adapters"
---
# RPC适配器

OpenClaw通过JSON-RPC集成外部CLI。目前使用两种模式。

## 模式A：HTTP守护进程（signal-cli）

- `signal-cli` 作为守护进程运行，通过HTTP提供JSON-RPC。
- 事件流是SSE（`/api/v1/events`）。
- 健康检查：`/api/v1/check`。
- 当`channels.signal.autoStart=true`时，OpenClaw拥有生命周期管理。

有关设置和端点，请参见[Signal](/channels/signal)。

## 模式B：stdio子进程（遗留：imsg）

> **注意：** 对于新的iMessage设置，请改用[BlueBubbles](/channels/bluebubbles)。

- OpenClaw将`imsg rpc`作为子进程启动（遗留iMessage集成）。
- JSON-RPC通过stdin/stdout以行分隔（每行一个JSON对象）。
- 不需要TCP端口，不需要守护进程。

使用的核心方法：

- `watch.subscribe` → 通知（`method: "message"`）
- `watch.unsubscribe`
- `send`
- `chats.list`（探针/诊断）

有关遗留设置和寻址，请参见[iMessage](/channels/imessage)（推荐使用`chat_id`）。

## 适配器指南

- 网关拥有进程（启动/停止与提供者生命周期绑定）。
- 保持RPC客户端具有弹性：超时处理，在退出时重启。
- 优先使用稳定ID（例如`chat_id`）而不是显示字符串。