---
summary: "RPC adapters for external CLIs (signal-cli, legacy imsg) and gateway patterns"
read_when:
  - Adding or changing external CLI integrations
  - Debugging RPC adapters (signal-cli, imsg)
title: "RPC Adapters"
---
# RPC 适配器

OpenClaw 通过 JSON-RPC 集成外部命令行工具（CLI）。目前采用两种模式。

## 模式 A：HTTP 守护进程（signal-cli）

- `signal-cli` 作为守护进程运行，通过 HTTP 提供 JSON-RPC 接口。
- 事件流采用服务器发送事件（SSE）机制（`/api/v1/events`）。
- 健康检查端点：`/api/v1/check`。
- 当 `channels.signal.autoStart=true` 时，OpenClaw 负责该进程的生命周期管理。

有关配置与端点详情，请参阅 [Signal](/channels/signal)。

## 模式 B：标准输入/输出子进程（旧版：imsg）

> **注意**：对于新的 iMessage 配置，请改用 [BlueBubbles](/channels/bluebubbles)。

- OpenClaw 将 `imsg rpc` 作为子进程启动（旧版 iMessage 集成）。
- JSON-RPC 通过 stdin/stdout 以行分隔方式传输（每行一个 JSON 对象）。
- 无需 TCP 端口，也无需单独的守护进程。

所使用的核心方法包括：

- `watch.subscribe` → 通知（`method: "message"`）
- `watch.unsubscribe`
- `send`
- `chats.list`（用于健康探测/诊断）

有关旧版配置与寻址方式，请参阅 [iMessage](/channels/imessage)（推荐使用 `chat_id`）。

## 适配器指南

- 网关负责进程管理（启动/停止与提供方生命周期绑定）。
- 确保 RPC 客户端具备弹性：设置超时、进程退出后自动重启。
- 优先使用稳定 ID（例如 `chat_id`），而非显示字符串。