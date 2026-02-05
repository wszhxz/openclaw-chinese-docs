---
summary: "How OpenClaw presence entries are produced, merged, and displayed"
read_when:
  - Debugging the Instances tab
  - Investigating duplicate or stale instance rows
  - Changing gateway WS connect or system-event beacons
title: "Presence"
---
# 在线状态

OpenClaw "在线状态" 是对以下内容的轻量级、尽力而为的视图：

- **网关**本身，以及
- **连接到网关的客户端**（mac 应用、WebChat、CLI 等）

在线状态主要用于渲染 macOS 应用的**实例**标签页并提供快速的操作员可见性。

## 在线状态字段（显示的内容）

在线状态条目是具有如下字段的结构化对象：

- `id`（可选但强烈推荐）：稳定的客户端标识（通常为 `machineId`）
- `hostname`：人性化的主机名
- `ip`：尽力而为的 IP 地址
- `version`：客户端版本字符串
- `platform` / `arch`：硬件提示
- `status`：`online`, `idle`, `busy`, `away`, `do-not-disturb`, `offline`, `stale`, ...
- `idleTimeSecs`："自上次用户输入以来的秒数"（如果已知）
- `tags`：`admin`, `dev`, `prod`, `backup`, `testing`, ...
- `lastUpdateMs`：最后更新时间戳（自纪元以来的毫秒数）

## 生产者（在线状态来源）

在线状态条目由多个源产生并**合并**。

### 1) 网关自条目

网关总是在启动时播种一个"自"条目，以便在任何客户端连接之前 UI 就能显示网关主机。

### 2) WebSocket 连接

每个 WS 客户端都以 `handshake` 请求开始。握手成功后，网关为该连接插入/更新一个在线状态条目。

#### 为什么一次性 CLI 命令不显示

CLI 经常为短时间的一次性命令进行连接。为了避免刷屏实例列表，`handshake` **不会**转换为在线状态条目。

### 3) `beacon` 信标

客户端可以通过 `beacon` 方法发送更丰富的周期性信标。mac 应用使用此功能报告主机名、IP 和 `status`。

### 4) 节点连接（角色：node）

当节点通过网关 WebSocket 以 `role: node` 连接时，网关为该节点插入/更新一个在线状态条目（与其他 WS 客户端相同的流程）。

## 合并 + 去重规则（为什么 `id` 很重要）

在线状态条目存储在单个内存映射中：

- 条目按键值为**在线状态键**。
- 最佳键是稳定的 `machineId`（来自 `handshake`）能够经受重启。
- 键值不区分大小写。

如果客户端重新连接时没有稳定的 `id`，它可能会显示为**重复**行。

## TTL 和有限大小

在线状态是有意短暂的：

- **TTL：**超过 5 分钟的条目会被修剪
- **最大条目数：**200（最旧的优先删除）

这使列表保持最新并避免无限制的内存增长。

## 远程/隧道注意事项（回环 IP）

当客户端通过 SSH 隧道/本地端口转发连接时，网关可能将远程地址视为 `127.0.0.1`。为避免覆盖良好的客户端报告的 IP，回环远程地址被忽略。

## 消费者

### macOS 实例标签页

macOS 应用渲染 `getPresence` 的输出，并根据最后更新的时间应用小的状态指示器（活动/空闲/陈旧）。

## 调试技巧

- 要查看原始列表，请对网关调用 `getPresence`。
- 如果看到重复：
  - 确认客户端在握手时发送稳定的 `id`
  - 确认周期性信标使用相同的 `id`
  - 检查连接派生的条目是否缺少 `id`（重复是预期的）