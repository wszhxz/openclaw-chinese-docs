---
summary: "Gateway-owned node pairing (Option B) for iOS and other remote nodes"
read_when:
  - Implementing node pairing approvals without macOS UI
  - Adding CLI flows for approving remote nodes
  - Extending gateway protocol with node management
title: "Gateway-Owned Pairing"
---
# 网关拥有配对（选项 B）

在网关拥有配对中，**网关**是哪些节点可以加入的权威来源。UI（macOS 应用、未来客户端）只是前端，用于批准或拒绝待批准请求。

**重要：** WS 节点在 `connect` 期间使用 **设备配对**（角色为 `node`）。`node.pair.*` 是一个独立的配对存储，它**不会**限制 WS 握手。只有明确调用 `node.pair.*` 的客户端才会使用此流程。

## 概念

- **待批准请求**：节点请求加入；需要批准。
- **已配对节点**：已批准的节点，拥有已颁发的授权令牌。
- **传输**：网关 WS 端点转发请求，但不决定成员资格。（旧版 TCP 桥接支持已弃用/移除。）

## 配对流程

1. 节点连接到网关 WS 并请求配对。
2. 网关存储一个 **待批准请求** 并发出 `node.pair.requested`。
3. 您批准或拒绝请求（CLI 或 UI）。
4. 批准后，网关颁发一个 **新令牌**（重新配对时令牌会轮换）。
5. 节点使用令牌重新连接，现在变为“已配对”。

待批准请求在 **5 分钟后** 自动过期。

## CLI 流程（适合无头环境）

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes reject <requestId>
openclaw nodes status
openclaw nodes rename --node <id|name|ip> --name "Living Room iPad"
```

`nodes status` 显示已配对/连接的节点及其功能。

## API 接口（网关协议）

事件：

- `node.pair.requested` — 当创建新的待批准请求时发出。
- `node.paired.resolved` — 当请求被批准/拒绝/过期时发出。

方法：

- `node.pair.request` — 创建或复用待批准请求。
- `node.pair.list` — 列出待批准 + 已配对节点。
- `node.pair.approve` — 批准待批准请求（颁发令牌）。
- `node.pair.reject` — 拒绝待批准请求。
- `node.pair.verify` — 验证 `{ nodeId, token }`。

说明：

- `node.pair.request` 按节点是幂等的：重复调用返回相同的待批准请求。
- 批准 **始终** 生成新的令牌；`node.pair.request` 从不返回令牌。
- 请求可能包含 `silent: true` 作为自动批准流程的提示。

## 自动批准（macOS 应用）

当满足以下条件时，macOS 应用可选择性地尝试 **静默批准**：

- 请求被标记为 `silent`，且
- 应用可以使用相同用户验证到网关主机的 SSH 连接。

如果静默批准失败，将回退到正常的“批准/拒绝”提示。

## 存储（本地、私有）

配对状态存储在网关状态目录下（默认 `~/.openclaw`）：

- `~/.openclaw/nodes/paired.json`
- `~/.openclaw/nodes/pending.json`

如果覆盖 `OPENCLAW_STATE_DIR`，`nodes/` 文件夹会随之移动。

安全说明：

- 令牌是机密信息；将 `paired.json` 视为敏感数据。
- 令牌轮换需要重新批准（或删除节点条目）。

## 传输行为

- 传输是 **无状态** 的；它不会存储成员资格。
- 如果网关离线或配对功能被禁用，节点无法配对。
- 如果网关处于远程模式，配对仍会针对远程网关的存储进行。