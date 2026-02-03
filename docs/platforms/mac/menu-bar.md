---
summary: "Menu bar status logic and what is surfaced to users"
read_when:
  - Tweaking mac menu UI or status logic
title: "Menu Bar"
---
# 菜单栏状态逻辑

## 显示内容

- 我们在菜单栏图标和菜单的第一行状态中展示当前代理的工作状态。
- 在工作期间，健康状态会被隐藏；当所有会话空闲时，健康状态会重新显示。
- 菜单中的“节点”区块仅列出**设备**（通过 `node.list` 配对的节点），不包括客户端/存在性条目。
- 当提供程序使用快照可用时，在上下文下会出现“使用”部分。

## 状态模型

- 会话：事件包含 `runId`（按运行划分）和 `sessionKey`（在负载中）。主会话的键为 `main`；如果不存在，则回退到最近更新的会话。
- 优先级：主会话始终优先。如果主会话处于活动状态，其状态会立即显示；如果主会话空闲，则显示最近活跃的非主会话。在活动过程中不会频繁切换状态；仅在当前会话空闲或主会话变为活动时才会切换。
- 活动类型：
  - `job`：高级命令执行（`state: started|streaming|done|error`）。
  - `tool`：`phase: start|result`，包含 `toolName` 和 `meta/args`。

## IconState 枚举（Swift）

- `idle`
- `workingMain(ActivityKind)`
- `workingOther(ActivityKind)`
- `overridden(ActivityKind)`（调试覆盖）

### ActivityKind → 图标

- `exec` → 💻
- `read` → 📄
- `write` → ✍️
- `edit` → 📝
- `attach` → 📎
- 默认 → 🛠️

### 视觉映射

- `idle`：普通生物。
- `workingMain`：带有图标的徽章，全色，腿部“工作”动画。
- `workingOther`：带有图标的徽章，灰度色，无快速移动。
- `overridden`：无论活动状态如何，均使用选定的图标/颜色。

## 状态行文本（菜单）

- 在工作期间：`<会话角色> · <活动标签>`
  - 示例：`主 · 执行: pnpm test`，`其他 · 读取: apps/macos/Sources/OpenClaw/AppState.swift`。
- 在空闲时：回退到健康状态摘要。

## 事件摄入

- 来源：控制通道 `agent` 事件（`ControlChannel.handleAgentEvent`）。
- 解析字段：
  - `stream: "job"` 包含 `data.state` 用于启动/停止。
  - `stream: "tool"` 包含 `data.phase`、`name`，可选 `meta`/`args`。
- 标签：
  - `exec`：`args.command` 的第一行。
  - `read`/`write`：缩短的路径。
  - `edit`：路径加上从 `meta`/diff 计数推断出的更改类型。
  - 默认：工具名称。

## 调试覆盖

- 设置 ▸ 调试 ▸ “图标覆盖”选择器：
  - `系统（自动）`（默认）
  - `工作：主`（按工具类型）
  - `工作：其他`（按工具类型）
  - `空闲`
- 通过 `@AppStorage("iconOverride")` 存储；映射到 `IconState.overridden`。

## 测试清单

- 触发主会话任务：验证图标立即切换且状态行显示主标签。
- 在主会话空闲时触发非主会话任务：图标/状态显示非主会话；直到任务完成保持稳定。
- 在其他会话活跃时启动主会话：图标立即切换为主会话。
- 快速工具爆发：确保徽章不会闪烁（工具结果的 TTL 宽限期）。
- 所有会话空闲后，健康行重新出现。