---
summary: "Global voice wake words (Gateway-owned) and how they sync across nodes"
read_when:
  - Changing voice wake words behavior or defaults
  - Adding new node platforms that need wake word sync
title: "Voice Wake"
---
# 语音唤醒（全局唤醒词）

OpenClaw 将**唤醒词视为由网关拥有的单个全局列表**。

- **没有每个节点的自定义唤醒词**。
- **任何节点/应用界面都可以编辑**该列表；更改由网关持久化并广播给所有人。
- 每个设备仍然保持自己的**语音唤醒启用/禁用**开关（本地用户体验 + 权限不同）。

## 存储（网关主机）

唤醒词存储在网关机器上：

- `~/.config/openclaw/gateway/wake_words.json`

形状：

```
string[]
```

## 协议

### 方法

- `set_wake_words` → `wake_words_set`
- `get_wake_words` 带参数 `{}` → `wake_words_list`

注意事项：

- 触发词会被规范化（修剪，空值丢弃）。空列表回退到默认值。
- 为安全起见强制执行限制（数量/长度上限）。

### 事件

- `wake_words_changed` 载荷 `string[]`

接收者：

- 所有 WebSocket 客户端（macOS 应用、WebChat 等）
- 所有连接的节点（iOS/Android），以及在节点连接时作为初始"当前状态"推送。

## 客户端行为

### macOS 应用

- 使用全局列表来控制 `voice_wake_trigger` 触发。
- 在语音唤醒设置中编辑"触发词"会调用 `set_wake_words`，然后依赖广播来保持其他客户端同步。

### iOS 节点

- 使用全局列表进行 `voice_wake_detected` 触发检测。
- 在设置中编辑唤醒词会调用 `set_wake_words`（通过网关 WS）并保持本地唤醒词检测响应。

### Android 节点

- 在设置中提供唤醒词编辑器。
- 通过网关 WS 调用 `set_wake_words` 以便编辑在各处同步。