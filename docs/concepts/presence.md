---
summary: "How OpenClaw presence entries are produced, merged, and displayed"
read_when:
  - Debugging the Instances tab
  - Investigating duplicate or stale instance rows
  - Changing gateway WS connect or system-event beacons
title: "Presence"
---
# 在线状态（Presence）

OpenClaw 的“在线状态（presence）”是一种轻量级、尽力而为的视图，用于反映：

- **网关（Gateway）本身**，以及  
- **连接到网关的客户端**（macOS 应用、WebChat、CLI 等）

在线状态主要用于渲染 macOS 应用中的 **“实例（Instances）”标签页**，并为运维人员提供快速的状态可见性。

## 在线状态字段（显示内容）

在线状态条目是结构化对象，包含如下字段：

- `instanceId`（可选但强烈推荐）：稳定的客户端标识（通常为 `connect.client.instanceId`）  
- `host`：便于人类识别的主机名  
- `ip`：尽力而为获取的 IP 地址  
- `version`：客户端版本字符串  
- `deviceFamily` / `modelIdentifier`：硬件提示信息  
- `mode`：`ui`、`webchat`、`cli`、`backend`、`probe`、`test`、`node`……  
- `lastInputSeconds`：“距上次用户输入经过的秒数”（如已知）  
- `reason`：`self`、`connect`、`node-connected`、`periodic`……  
- `ts`：最后更新时间戳（自 Unix 纪元起的毫秒数）

## 生成方（在线状态的来源）

在线状态条目由多个来源生成，并被**合并（merged）**。

### 1) 网关自身条目

网关在启动时总会预先注入一条“自身（self）”条目，确保 UI 在任何客户端连接之前就能显示网关主机信息。

### 2) WebSocket 连接

每个 WebSocket 客户端均以一个 `connect` 请求开始。握手成功后，网关将为该连接插入或更新（upsert）一条在线状态条目。

#### 为何一次性 CLI 命令不会显示

CLI 常用于执行短暂的一次性命令。为避免频繁刷屏干扰“实例”列表，`client.mode === "cli"` **不会**生成在线状态条目。

### 3) `system-event` 心跳信标（beacons）

客户端可通过 `system-event` 方法发送更丰富的周期性心跳信标。macOS 应用即使用此机制上报主机名、IP 地址及 `lastInputSeconds`。

### 4) 节点连接（角色：node）

当节点通过网关 WebSocket 连接并声明 `role: node` 角色时，网关将为其插入或更新（upsert）一条在线状态条目（流程与其他 WebSocket 客户端一致）。

## 合并与去重规则（为何 `instanceId` 至关重要）

在线状态条目存储于单个内存映射表中：

- 条目以 **在线状态键（presence key）** 为索引。  
- 最佳键值是一个稳定的 `instanceId`（来自 `connect.client.instanceId`），该值可在重启后保持不变。  
- 键值不区分大小写。

若客户端在未提供稳定 `instanceId` 的情况下重新连接，则可能作为**重复条目**出现。

## 生存时间（TTL）与容量限制

在线状态被有意设计为临时性数据：

- **生存时间（TTL）：** 超过 5 分钟的条目将被自动清理；  
- **最大条目数：** 200 条（最旧条目优先丢弃）。

此举确保列表始终新鲜，并防止内存无界增长。

## 远程/隧道注意事项（回环 IP 地址）

当客户端通过 SSH 隧道或本地端口转发连接时，网关所见的远端地址可能为 `127.0.0.1`。为避免覆盖客户端主动上报的有效 IP 地址，所有回环地址形式的远端地址均被忽略。

## 消费方（Consumers）

### macOS 实例标签页

macOS 应用渲染 `system-presence` 的输出结果，并依据最后更新时间的相对新旧程度，附加一个小型状态指示器（活跃 / 空闲 / 过期）。

## 调试技巧

- 要查看原始列表，请对网关调用 `system-presence`。  
- 若发现重复条目：  
  - 请确认客户端在握手阶段是否发送了稳定的 `client.instanceId`；  
  - 请确认周期性心跳信标是否使用了相同的 `instanceId`；  
  - 请检查连接派生的条目是否缺失 `instanceId`（若缺失，则重复属于预期行为）。