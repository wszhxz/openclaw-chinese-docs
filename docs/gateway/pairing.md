---
summary: "Gateway-owned node pairing (Option B) for iOS and other remote nodes"
read_when:
  - Implementing node pairing approvals without macOS UI
  - Adding CLI flows for approving remote nodes
  - Extending gateway protocol with node management
title: "Gateway-Owned Pairing"
---
# 网关托管配对（选项 B）

在网关托管配对中，**网关**是决定哪些节点被允许加入的权威来源。用户界面（macOS 应用、未来客户端）仅作为前端，用于批准或拒绝待处理的请求。

**重要提示：** WS 节点在 `connect` 期间使用**设备配对**（角色为 `node`）。  
`node.pair.*` 是一个独立的配对存储，**不**控制 WS 握手流程。  
仅显式调用 `node.pair.*` 的客户端才使用此流程。

## 概念

- **待处理请求**：节点发起加入请求；需经批准。
- **已配对节点**：已获批准且已颁发认证令牌的节点。
- **传输层**：网关 WS 端点转发请求，但不决定成员资格。（旧版 TCP 桥接支持已被弃用/移除。）

## 配对工作原理

1. 节点连接至网关 WS 并发起配对请求。
2. 网关保存一条**待处理请求**，并触发 `node.pair.requested`。
3. 您通过命令行或 UI 批准或拒绝该请求。
4. 批准后，网关签发一个**新令牌**（令牌在重新配对时轮换）。
5. 节点使用该令牌重新连接，即完成“配对”。

待处理请求将在 **5 分钟** 后自动过期。

## CLI 工作流（支持无头模式）

```bash
openclaw nodes pending
openclaw nodes approve <requestId>
openclaw nodes reject <requestId>
openclaw nodes status
openclaw nodes rename --node <id|name|ip> --name "Living Room iPad"
```

`nodes status` 显示已配对/已连接节点及其能力。

## API 接口（网关协议）

事件：

- `node.pair.requested` —— 创建新的待处理请求时触发。
- `node.pair.resolved` —— 请求被批准、拒绝或过期时触发。

方法：

- `node.pair.request` —— 创建或复用一条待处理请求。
- `node.pair.list` —— 列出待处理及已配对节点。
- `node.pair.approve` —— 批准一条待处理请求（签发令牌）。
- `node.pair.reject` —— 拒绝一条待处理请求。
- `node.pair.verify` —— 验证 `{ nodeId, token }`。

备注：

- `node.pair.request` 对每个节点是幂等的：重复调用将返回相同的待处理请求。
- 批准操作**始终**生成一个全新令牌；`node.pair.request` **从不**返回任何令牌。
- 请求可包含 `silent: true`，作为自动批准流程的提示信息。

## 自动批准（macOS 应用）

macOS 应用可选择性地尝试执行**静默批准**，前提是满足以下条件：

- 该请求被标记为 `silent`，且  
- 应用可通过同一用户，成功验证到网关主机的 SSH 连接。

若静默批准失败，则回退至常规的“批准/拒绝”提示界面。

## 存储（本地、私有）

配对状态保存在网关状态目录下（默认为 `~/.openclaw`）：

- `~/.openclaw/nodes/paired.json`  
- `~/.openclaw/nodes/pending.json`

若您覆盖了 `OPENCLAW_STATE_DIR`，则 `nodes/` 文件夹将随之迁移。

安全说明：

- 令牌属于机密信息；请将 `paired.json` 视为敏感数据。
- 轮换令牌需重新批准（或删除对应节点条目）。

## 传输层行为

- 传输层是**无状态的**；它不保存成员资格信息。
- 若网关离线或配对功能被禁用，节点将无法完成配对。
- 若网关处于远程模式，配对操作仍针对远程网关的配对存储执行。