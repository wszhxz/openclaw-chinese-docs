---
summary: "Global voice wake words (Gateway-owned) and how they sync across nodes"
read_when:
  - Changing voice wake words behavior or defaults
  - Adding new node platforms that need wake word sync
title: "Voice Wake"
---
# 语音唤醒（全局唤醒词）

OpenClaw 将 **唤醒词视为一个全局列表**，由 **网关** 所有。

- 没有 **针对每个节点的自定义唤醒词**。
- **任何节点/应用 UI 都可以编辑** 该列表；更改由网关持久化并广播给所有人。
- 每个设备仍保留自己的 **语音唤醒启用/禁用** 开关（本地用户体验 + 权限不同）。

## 存储（网关主机）

唤醒词存储在网关机器上的以下路径：

- `~/.openclaw/settings/voicewake.json`

结构：

```json
{ "triggers": ["openclaw", "claude", "computer"], "updatedAtMs": 1730000000000 }
```

## 协议

### 方法

- `voicewake.get` → `{ triggers: string[] }`
- `voicewake.set` 带参数 `{ triggers: string[] }` → `{ triggers: string[] }`

说明：

- 触发词会被规范化（去除空格，空列表会被丢弃）。空列表将回退到默认值。
- 为了安全起见，会强制执行限制（计数/长度上限）。

### 事件

- `voicewake.changed` 负载 `{ triggers: string[] }`

接收者：

- 所有 WebSocket 客户端（macOS 应用、WebChat 等）
- 所有已连接的节点（iOS/Android），并在节点连接时作为初始“当前状态”推送。

## 客户端行为

### macOS 应用

- 使用全局列表来控制 `VoiceWakeRuntime` 的触发词。
- 在语音唤醒设置中编辑“触发词”会调用 `voicewake.set`，然后依赖广播来保持其他客户端同步。

### iOS 节点

- 使用全局列表进行 `VoiceWakeManager` 的触发词检测。
- 在设置中编辑唤醒词会调用