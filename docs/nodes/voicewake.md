---
summary: "Global voice wake words (Gateway-owned) and how they sync across nodes"
read_when:
  - Changing voice wake words behavior or defaults
  - Adding new node platforms that need wake word sync
title: "Voice Wake"
---
# 语音唤醒（全局唤醒词）

OpenClaw 将**唤醒词视为由网关（Gateway）统一管理的单一全局列表**。

- **不支持为各节点配置自定义唤醒词**。
- **任意节点或应用界面均可编辑该列表**；修改由网关持久化并广播至所有客户端。
- macOS 和 iOS 系统在本地保留**语音唤醒启用/禁用开关**（本地用户体验与权限机制存在差异）。
- Android 当前默认关闭语音唤醒功能，并在“语音”标签页中采用手动麦克风采集流程。

## 存储（网关主机）

唤醒词存储于网关机器上的以下路径：

- `~/.openclaw/settings/voicewake.json`

数据结构如下：

```json
{ "triggers": ["openclaw", "claude", "computer"], "updatedAtMs": 1730000000000 }
```

## 协议

### 方法

- `voicewake.get` → `{ triggers: string[] }`
- `voicewake.set` 带参数 `{ triggers: string[] }` → `{ triggers: string[] }`

注意事项：

- 触发词会进行标准化处理（去除首尾空格，丢弃空项）。若列表为空，则回退至默认值。
- 为保障安全性，对数量和长度施加了限制（设有计数上限与长度上限）。

### 事件

- `voicewake.changed` 负载内容为 `{ triggers: string[] }`

接收方包括：

- 所有 WebSocket 客户端（如 macOS 应用、WebChat 等）
- 所有已连接节点（iOS / Android），且在节点初次连接时亦会推送一次初始“当前状态”。

## 客户端行为

### macOS 应用

- 使用全局唤醒词列表来控制 `VoiceWakeRuntime` 触发行为。
- 在“语音唤醒”设置中编辑“触发词”将调用 `voicewake.set`，随后依赖广播机制确保其他客户端同步更新。

### iOS 节点

- 使用全局唤醒词列表进行 `VoiceWakeManager` 触发检测。
- 在设置中编辑唤醒词将调用 `voicewake.set`（通过网关 WebSocket），同时保持本地唤醒词检测响应及时。

### Android 节点

- Android 运行时及设置中当前禁用语音唤醒功能。
- Android 的语音功能在“语音”标签页中采用手动麦克风采集方式，而非基于唤醒词的自动触发。