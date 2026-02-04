---
summary: "Gateway-owned node pairing (Option B) for iOS and other remote nodes"
read_when:
  - Implementing node pairing approvals without macOS UI
  - Adding CLI flows for approving remote nodes
  - Extending gateway protocol with node management
title: "Gateway-Owned Pairing"
---
# 网关拥有配对（选项B）

在网关拥有配对中，**网关**是决定哪些节点可以加入的真相来源。UI（macOS应用、未来客户端）只是前端，用于批准或拒绝待处理请求。

**重要：** WS节点在`connect`期间使用**设备配对**（角色 `node`）。
`node.pair.*`是一个独立的配对存储，并且**不**限制WS握手。
只有显式调用`node.pair.*`的客户端使用此流程。

## 概念

- **待处理请求**：请求加入的节点；需要批准。
- **已配对节点**：已批准并颁发了认证令牌的节点。
- **传输**：网关WS端点转发请求但不决定成员资格。（遗留的TCP桥接支持已弃用/移除。）

## 配对如何工作

1. 节点连接到网关WS并请求配对。
2. 网关存储一个**待处理请求**并发出`node.pair.requested`。
3. 您批准或拒绝请求（CLI或UI）。
4. 批准后，网关颁发一个新的**令牌**（重新配对时会轮换令牌）。
5. 节点使用令牌重新连接，现在“已配对”。

待处理请求会在**5分钟**后自动过期。

## CLI工作流（适合无头模式）

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes reject <requestId>
openclaw nodes status
openclaw nodes rename --node <id|name|ip> --name "Living Room iPad"
```

`nodes status`显示已配对/已连接的节点及其功能。

## API接口（网关协议）

事件：

- `node.pair.requested` — 当创建新的待处理请求时发出。
- `node.pair.resolved` — 当请求被批准/拒绝/过期时发出。

方法：

- `node.pair.request` — 创建或重用待处理请求。
- `node.pair.list` — 列出待处理+已配对的节点。
- `node.pair.approve` — 批准待处理请求（颁发令牌）。
- `node.pair.reject` — 拒绝待处理请求。
- `node.pair.verify` — 验证`{ nodeId, token }`。

注意事项：

- `node.pair.request`每个节点都是幂等的：重复调用返回相同的待处理请求。
- 批准**总是**生成一个新的令牌；`node.pair.request`从未返回令牌。
- 请求可能包含`silent: true`作为自动批准流程的提示。

## 自动批准（macOS应用）

macOS应用可以在以下情况下尝试**静默批准**：

- 请求被标记为`silent`，并且
- 应用可以使用同一用户验证与网关主机的SSH连接。

如果静默批准失败，则回退到正常的“批准/拒绝”提示。

## 存储（本地、私有）

配对状态存储在网关状态目录下（默认`~/.openclaw`）：

- `~/.openclaw/nodes/paired.json`
- `~/.openclaw/nodes/pending.json`

如果您覆盖`OPENCLAW_STATE_DIR`，则`nodes/`文件夹也会随之移动。

安全注意事项：

- 令牌是机密信息；将`paired.json`视为敏感信息。
- 轮换令牌需要重新批准（或删除节点条目）。

## 传输行为

- 传输是**无状态**的；它不存储成员资格。
- 如果网关离线或禁用配对，节点无法配对。
- 如果网关处于远程模式，配对仍然针对远程网关的存储进行。