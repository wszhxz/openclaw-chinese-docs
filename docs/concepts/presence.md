---
summary: "How OpenClaw presence entries are produced, merged, and displayed"
read_when:
  - Debugging the Instances tab
  - Investigating duplicate or stale instance rows
  - Changing gateway WS connect or system-event beacons
title: "Presence"
---
# 存在性

OpenClaw 的“存在性”是一种轻量级、尽力而为的视图，用于表示：

- **网关**本身，以及
- **连接到网关的客户端**（mac 应用、WebChat、CLI 等）

存在性主要用于渲染 macOS 应用的**实例**标签，并提供快速的操作员可见性。

## 存在性字段（显示的内容）

存在性条目是结构化的对象，包含以下字段：

- `instanceId`（可选但强烈建议使用）：稳定的客户端标识（通常为 `connect.client.instanceId`）
- `host`：人性化主机名
- `ip`：尽力而为的 IP 地址
- `version`：客户端版本字符串
- `deviceFamily` / `modelIdentifier`：硬件提示
- `mode`：`ui`、`webchat`、`cli`、`backend`、`probe`、`test`、`node` 等
- `lastInputSeconds`：自上次用户输入以来的秒数（如果已知）
- `reason`：`self`、`connect`、`node-connected`、`periodic` 等
- `ts`：最后更新时间戳（自纪元以来的毫秒数）

## 生产者（存在性来源）

存在性条目由多个来源生成并**合并**。

### 1) 网关自身条目

网关在启动时始终会生成一个“自身”条目，以便 UI 在任何客户端连接之前即可显示网关主机。

### 2) WebSocket 连接

每个 WebSocket 客户端都会以 `connect` 请求开始。在成功握手后，网关会为该连接插入或更新一个存在性条目。

#### 为什么一次性 CLI 命令不会显示

CLI 通常用于短时、一次性命令。为了避免 Instances 列表被垃圾信息淹没，`client.mode === "cli"` **不会**生成存在性条目。

### 3) `system-event` 信标

客户端可以通过 `system-event` 方法发送更丰富的周期性信标。mac 应用使用此方法报告主机名、IP 和 `lastInputSeconds`。

### 4) 节点连接（角色：节点）

当节点通过网关 WebSocket 以 `role: node` 连接时，网关会为该节点插入或更新一个存在性条目（与其它 WebSocket 客户端的流程相同）。

## 合并 + 去重规则（为什么 `instanceId` 重要）

存在性条目存储在一个单个的内存映射中：

- 条目通过**存在性键**进行键值关联。
- 最佳键是稳定的 `instanceId`（来自 `connect.client.instanceId`），可跨重启保持不变。
- 键值不区分大小写。

如果客户端在没有稳定 `instanceId` 的情况下重新连接，可能会显示为**重复**行。

## TTL 和有限大小

存在性是故意设计为临时性的：

- **TTL**：超过 5 分钟的条目会被清理
- **最大条目数**：200（优先删除最旧的条目）

这保持列表的最新状态，并避免内存无限制增长。

## 远程/隧道注意事项（回环 IP 地址）

当客户端通过 SSH 隧道/本地端口转发连接时，网关可能会将远程地址识别为 `127.0.0.1`。为了避免覆盖良好的客户端报告的 IP，回环远程地址将被忽略。

## 消费者

### macOS 实例标签

macOS 应用会渲染 `system-presence` 的输出，并根据最后更新时间的年龄显示小型状态指示器（活跃/空闲/过期）。

## 调试提示

- 要查看原始列表，请对网关调用 `system-presence`。
- 如果看到重复项：
  - 确认客户端在握手中发送稳定的 `client.instanceId`
  - 确认周期性信标使用相同的 `instanceId`
  - 检查连接衍生的条目是否缺少 `instanceId`（预期会出现重复）