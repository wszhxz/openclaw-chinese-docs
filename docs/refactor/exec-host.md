---
summary: "Refactor plan: exec host routing, node approvals, and headless runner"
read_when:
  - Designing exec host routing or exec approvals
  - Implementing node runner + UI IPC
  - Adding exec host security modes and slash commands
title: "Exec Host Refactor"
---
# 执行主机重构计划

## 目标

- 添加 `exec.host` + `exec.security` 以在 **sandbox**、**gateway** 和 **node** 之间路由执行。
- 保持默认值 **安全**：除非显式启用，否则不跨主机执行。
- 将执行拆分为一个 **无头运行器服务**，通过本地 IPC 提供可选 UI（macOS 应用）。
- 提供 **每代理** 策略、允许列表、询问模式和节点绑定。
- 支持 **询问模式**，无论是否使用允许列表均可工作。
- 跨平台：Unix 套接字 + 令牌认证（macOS/Linux/Windows 兼容）。

## 非目标

- 不支持旧版允许列表迁移或旧版模式支持。
- 不支持节点执行的 PTY/流式传输（仅聚合输出）。
- 除现有 Bridge + Gateway 外，不引入新的网络层。

## 决策（锁定）

- **配置键**：`exec.host` + `exec.security`（允许每代理覆盖）。
- **提升权限**：保持 `/elevated` 作为 gateway 全权限的别名。
- **询问默认值**：`on-miss`。
- **审批存储**：`~/.openclaw/exec-approvals.json`（JSON，不支持旧版迁移）。
- **运行器**：无头系统服务；UI 应用通过 Unix 套接字处理审批。
- **节点身份**：使用现有 `nodeId`。
- **套接字认证**：Unix 套接字 + 令牌（跨平台）；如需可拆分。
- **节点主机状态**：`~/.openclaw/node.json`（节点 ID + 配对令牌）。
- **macOS 执行主机**：在 macOS 应用中运行 `system.run`；节点主机服务通过本地 IPC 转发请求。
- **不使用 XPC 帮助器**：保持 Unix 套接字 + 令牌 + 对等检查。

## 关键概念

### 主机

- `sandbox`：Docker 执行（当前行为）。
- `gateway`：在网关主机上执行。
- `node`：通过 Bridge 在节点运行器上执行（`system.run`）。

### 安全模式

- `deny`：始终阻止。
- `allowlist`：仅允许匹配项。
- `full`：允许所有内容（等同于提升权限）。

### 询问模式

- `off`：从不询问。
- `on-miss`：仅在允许列表不匹配时询问。
- `always`：每次询问。

询问与允许列表 **独立**；允许列表可与 `always` 或 `on-miss` 一起使用。

### 策略解析（每执行）

1. 解析 `exec.host`（工具参数 → 代理覆盖 → 全局默认）。
2. 解析 `exec.security` 和 `exec.ask`（相同优先级）。
3. 如果主机是 `sandbox`，则进行本地沙箱执行。
4. 如果主机是 `gateway` 或 `node`，则在该主机上应用安全 + 询问策略。

## 默认安全性

- 默认 `exec.host = sandbox`。
- 默认 `exec.security = deny`（适用于 `gateway` 和 `node`）。
- 默认 `exec.ask = on-miss`（仅在安全允许时相关）。
- 如果未设置节点绑定，**代理可能针对任何节点**，但仅在策略允许时。

## 配置表面积

### 工具参数

- `exec.host`（可选）：`sandbox | gateway | node`。
- `exec.security`（可选）：`deny | allowlist | full`。
- `exec.ask`（可选）：`off | on-miss | always`。
- `exec.node`（可选）：当 `host=node` 时使用的节点 ID/名称。

### 全局配置键

- `tools.exec.host`
- `tools.exec.security`
- `tools.exec.ask`
- `tools.exec.node`

### 别名

- `/elevated` 保留为别名。

## 审批存储

```json
{
  "socket": "Unix 套接字路径",
  "token": "令牌",
  "allowlist": ["允许项1", "允许项2"],
  "ask": "询问模式"
}
```

## 运行器服务

- 实现无头运行器服务，通过本地 IPC 与 UI 通信。
- 支持 `askFallback` 机制。

## UI 集成

- macOS 应用通过 Unix 套接字桥接询问提示。
- 支持 `askFallback` 逻辑。

## 节点身份

- 使用 `nodeId` 标识节点。
- 配对令牌用于安全验证。

## 事件处理

- 节点 → 网关 Bridge 事件用于执行生命周期。
- 映射到 `enqueueSystemEvent` 以供代理提示。

## 执行流程

- 沙箱、网关、节点的执行流程定义。
- 包括拒绝、允许、询问的逻辑。

## 输出限制

- 命令输出限制，防止资源耗尽。
- 依赖超时和输出限制。

## 命令

- `/exec`：执行命令。
- `/elevated`：保留为别名。

## 跨平台支持

- Unix