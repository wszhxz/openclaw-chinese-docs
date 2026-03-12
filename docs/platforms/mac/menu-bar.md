---
summary: "Menu bar status logic and what is surfaced to users"
read_when:
  - Tweaking mac menu UI or status logic
title: "Menu Bar"
---
# 菜单栏状态逻辑

## 显示内容

- 我们在菜单栏图标和菜单的第一行状态中显示当前代理工作状态。
- 当工作活跃时，健康状态会被隐藏；当所有会话都处于空闲状态时，它会重新出现。
- 菜单中的“节点”块仅列出**设备**（通过`node.list`配对的节点），不包括客户端/存在条目。
- 当提供者使用快照可用时，“使用情况”部分会出现在上下文下。

## 状态模型

- 会话：事件带有`runId`（每次运行）加上有效负载中的`sessionKey`。"主要"会话是关键的`main`；如果不存在，则回退到最近更新的会话。
- 优先级：总是主要优先。如果主要活跃，其状态立即显示。如果主要空闲，则显示最近活跃的非主要会话。我们不会在活动过程中切换；只有在当前会话变为空闲或主要变为活跃时才会切换。
- 活动类型：
  - `job`：高级命令执行(`state: started|streaming|done|error`)。
  - `tool`：与`toolName`和`meta/args`一起的`phase: start|result`。

## IconState 枚举 (Swift)

- `idle`
- `workingMain(ActivityKind)`
- `workingOther(ActivityKind)`
- `overridden(ActivityKind)`（调试覆盖）

### ActivityKind → 图形符号

- `exec` → 💻
- `read` → 📄
- `write` → ✍️
- `edit` → 📝
- `attach` → 📎
- 默认 → 🛠️

### 视觉映射

- `idle`：正常生物。
- `workingMain`：带有图形符号的徽章，全色调，“工作”动画腿。
- `workingOther`：带有图形符号的徽章，静音色调，无匆忙。
- `overridden`：无论活动如何，都使用所选的图形符号/色调。

## 状态行文本（菜单）

- 当工作活跃时：`<Session role> · <activity label>`
  - 示例：`Main · exec: pnpm test`, `Other · read: apps/macos/Sources/OpenClaw/AppState.swift`。
- 当空闲时：回退到健康摘要。

## 事件摄入

- 来源：控制通道`agent`事件(`ControlChannel.handleAgentEvent`)。
- 解析字段：
  - `stream: "job"`与`data.state`用于开始/停止。
  - `stream: "tool"`与`data.phase`, `name`, 可选的`meta`/`args`。
- 标签：
  - `exec`：`args.command`的第一行。
  - `read`/`write`：缩短路径。
  - `edit`：路径加上从`meta`/差异计数推断的变化类型。
  - 回退：工具名称。

## 调试覆盖

- 设置 ▸ 调试 ▸ “图标覆盖”选择器：
  - `System (auto)`（默认）
  - `Working: main`（每种工具类型）
  - `Working: other`（每种工具类型）
  - `Idle`
- 通过`@AppStorage("iconOverride")`存储；映射到`IconState.overridden`。

## 测试检查清单

- 触发主要会话作业：验证图标是否立即切换且状态行显示主要标签。
- 在主要空闲时触发非主要会话作业：图标/状态显示非主要；直到完成前保持稳定。
- 在其他活动时启动主要：图标立即切换到主要。
- 快速工具爆发：确保徽章不闪烁（工具结果上的TTL宽限期）。
- 所有会话空闲后，健康行重新出现。