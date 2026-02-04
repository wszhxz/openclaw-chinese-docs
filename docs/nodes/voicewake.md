---
summary: "Global voice wake words (Gateway-owned) and how they sync across nodes"
read_when:
  - Changing voice wake words behavior or defaults
  - Adding new node platforms that need wake word sync
title: "Voice Wake"
---
# 声音唤醒（全局唤醒词）

OpenClaw 将 **唤醒词视为由网关拥有的单个全局列表**。

- 没有 **每个节点的自定义唤醒词**。
- **任何节点/应用程序UI都可以编辑** 列表；更改由网关持久化并广播给所有人。
- 每个设备仍然保留自己的 **声音唤醒启用/禁用** 开关（本地用户体验和权限不同）。

## 存储（网关主机）

唤醒词存储在网关机器上：

- `~/.openclaw/settings/voicewake.json`

形状：

```json
{ "triggers": ["openclaw", "claude", "computer"], "updatedAtMs": 1730000000000 }
```

## 协议

### 方法

- `voicewake.get` → `{ triggers: string[] }`
- `voicewake.set` 带参数 `{ triggers: string[] }` → `{ triggers: string[] }`

注意：

- 触发器已标准化（已修剪，空项已删除）。空列表回退到默认值。
- 为了安全起见，强制执行限制（计数/长度上限）。

### 事件

- `voicewake.changed` 负载 `{ triggers: string[] }`

接收者：

- 所有 WebSocket 客户端（macOS 应用程序、WebChat 等）
- 所有连接的节点（iOS/Android），并在节点连接时作为初始“当前状态”推送。

## 客户端行为

### macOS 应用程序

- 使用全局列表来控制 `VoiceWakeRuntime` 触发器。
- 在声音唤醒设置中编辑“触发词”会调用 `voicewake.set`，然后依赖广播来同步其他客户端。

### iOS 节点

- 使用全局列表进行 `VoiceWakeManager` 触发检测。
- 在设置中编辑唤醒词会调用 `voicewake.set`（通过网关 WS）并保持本地唤醒词检测响应。

### Android 节点

- 在设置中暴露一个唤醒词编辑器。
- 通过网关 WS 调用 `voicewake.set` 以便编辑在所有地方同步。