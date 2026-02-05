---
summary: "Menu bar status logic and what is surfaced to users"
read_when:
  - Tweaking mac menu UI or status logic
title: "Menu Bar"
---
# 菜单栏状态逻辑

## 显示内容

- 我们在菜单栏图标和菜单的第一个状态行中显示当前代理工作状态。
- 工作进行时隐藏健康状态；当所有会话都处于空闲状态时恢复显示。
- 菜单中的"节点"块仅列出**设备**（通过 `node.list` 配对的节点），不包括客户端/在线状态条目。
- 当提供程序使用情况快照可用时，在上下文中会出现"使用情况"部分。

## 状态模型

- 会话：事件随 `runId` （每次运行）以及有效载荷中的 `sessionKey` 到达。"主"会话是关键 `main`；如果不存在，则回退到最近更新的会话。
- 优先级：主会话始终优先。如果主会话处于活动状态，立即显示其状态。如果主会话处于空闲状态，则显示最近活动的非主会话。我们不会在活动过程中反复切换；只有当当前会话变为空闲或主会话变为活动状态时才切换。
- 活动类型：
  - `job`：高级命令执行（`state: started|streaming|done|error`）。
  - `tool`：带有 `phase: start|result` 和 `toolName` 的 `meta/args`。

## IconState 枚举（Swift）

- `idle`
- `workingMain(ActivityKind)`
- `workingOther(ActivityKind)`
- `overridden(ActivityKind)` （调试覆盖）

### ActivityKind → 字形

- `exec` → 💻
- `read` → 📄
- `write` → ✍️
- `edit` → 📝
- `attach` → 📎
- 默认 → 🛠️

### 视觉映射

- `idle`：正常小动物。
- `workingMain`：带字形的徽章，完整着色，腿部"工作"动画。
- `workingOther`：带字形的徽章，静音着色，无快速移动。
- `overridden`：无论活动如何都使用选定的字形/着色。

## 状态行文本（菜单）

- 工作进行时：`<Session role> · <activity label>`
  - 示例：`Main · exec: pnpm test`，`Other · read: apps/macos/Sources/OpenClaw/AppState.swift`。
- 空闲时：回退到健康摘要。

## 事件处理

- 来源：控制通道 `agent` 事件（`ControlChannel.handleAgentEvent`）。
- 解析字段：
  - `stream: "job"` 带有 `data.state` 用于开始/停止。
  - `stream: "tool"` 带有 `data.phase`、`name`，可选的 `meta`/`args`。
- 标签：
  - `exec`：`args.command` 的第一行。
  - `read`/`write`：缩短的路径。
  - `edit`：路径加上从 `meta`/差异计数推断的更改类型。
  - 回退：工具名称。

## 调试覆盖

- 设置 ▸ 调试 ▸ "图标覆盖"选择器：
  - `System (auto)` （默认）
  - `Working: main` （按工具类型）
  - `Working: other` （按工具类型）
  - `Idle`
- 通过 `@AppStorage("iconOverride")` 存储；映射到 `IconState.overridden`。

## 测试清单

- 触发主会话作业：验证图标立即切换且状态行显示主标签。
- 在主会话空闲时触发非主会话作业：图标/状态显示非主会话；保持稳定直到完成。
- 在其他会话活动时启动主会话：图标立即切换到主会话。
- 快速工具突发：确保徽章不会闪烁（工具结果的TTL宽限期）。
- 所有会话空闲后健康行重新出现。