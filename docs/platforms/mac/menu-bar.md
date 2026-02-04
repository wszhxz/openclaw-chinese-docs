---
summary: "Menu bar status logic and what is surfaced to users"
read_when:
  - Tweaking mac menu UI or status logic
title: "Menu Bar"
---
# 菜单栏状态逻辑

## 显示内容

- 我们在菜单栏图标和菜单的第一行状态中显示当前代理工作状态。
- 健康状态在工作活跃时隐藏；当所有会话空闲时恢复。
- 菜单中的“Nodes”块仅列出**设备**（通过 `node.list` 配对的节点），不包括客户端/存在条目。
- 当提供者使用快照可用时，“Usage”部分出现在上下文下。

## 状态模型

- 会话：事件带有 `runId`（每次运行）加上负载中的 `sessionKey`。“主”会话是关键 `main`；如果不存在，我们回退到最近更新的会话。
- 优先级：主始终获胜。如果主处于活动状态，其状态立即显示。如果主空闲，则显示最近活动的非主会话。我们在活动过程中不会来回切换；只有在当前会话空闲或主变为活动状态时才会切换。
- 活动类型：
  - `job`：高级命令执行 (`state: started|streaming|done|error`)。
  - `tool`：`phase: start|result` 带有 `toolName` 和 `meta/args`。

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

- `idle`：正常生物。
- `workingMain`：带有图标的徽章，完全着色，腿“工作”动画。
- `workingOther`：带有图标的徽章，柔和色调，无移动。
- `overridden`：无论活动如何，均使用选定的图标/色调。

## 状态行文本（菜单）

- 当工作处于活动状态：`<Session role> · <activity label>`
  - 示例：`Main · exec: pnpm test`，`Other · read: apps/macos/Sources/OpenClaw/AppState.swift`。
- 当空闲时：回退到健康摘要。

## 事件摄取

- 来源：控制通道 `agent` 事件 (`ControlChannel.handleAgentEvent`)。
- 解析字段：
  - `stream: "job"` 带有 `data.state` 用于开始/停止。
  - `stream: "tool"` 带有 `data.phase`，`name`，可选 `meta`/`args`。
- 标签：
  - `exec`：`args.command` 的第一行。
  - `read`/`write`：缩短的路径。
  - `edit`：路径加上从 `meta`/差异计数推断的更改类型。
  - 回退：工具名称。

## 调试覆盖

- 设置 ▸ 调试 ▸ “图标覆盖”选择器：
  - `System (auto)`（默认）
  - `Working: main`（按工具类型）
  - `Working: other`（按工具类型）
  - `Idle`
- 通过 `@AppStorage("iconOverride")` 存储；映射到 `IconState.overridden`。

## 测试检查表

- 触发主会话作业：验证图标立即切换且状态行显示主标签。
- 在主空闲时触发非主会话作业：图标/状态显示非主；直到完成为止保持稳定。
- 在其他会话处于活动状态时启动主会话：图标立即切换到主。
- 快速工具爆发：确保徽章不闪烁（工具结果的 TTL 宽限期）。
- 所有会话空闲后，健康行重新出现。