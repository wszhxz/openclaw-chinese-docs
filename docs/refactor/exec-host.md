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
- 保持默认设置 **安全**：除非显式启用，否则不进行跨主机执行。
- 将执行拆分为一个带有可选UI（macOS应用）的 **无头运行器服务** 通过本地IPC。
- 提供 **每个代理** 的策略、允许列表、询问模式和节点绑定。
- 支持 **询问模式**，无论是否使用允许列表。
- 跨平台：Unix套接字 + 令牌认证（macOS/Linux/Windows 平等）。

## 非目标

- 不进行旧允许列表迁移或旧架构支持。
- 不支持节点执行的 PTY/流式传输（仅聚合输出）。
- 除了现有的 Bridge + Gateway 之外，不引入新的网络层。

## 决策（锁定）

- **配置键：** `exec.host` + `exec.security`（允许每个代理覆盖）。
- **提升权限：** 保持 `/elevated` 作为网关完全访问的别名。
- **询问默认值：** `on-miss`。
- **批准存储：** `~/.openclaw/exec-approvals.json`（JSON，无旧版迁移）。
- **运行器：** 无头系统服务；UI 应用托管一个用于批准的 Unix 套接字。
- **节点身份：** 使用现有的 `nodeId`。
- **套接字认证：** Unix 套接字 + 令牌（跨平台）；如果需要，以后再拆分。
- **节点主机状态：** `~/.openclaw/node.json`（节点ID + 配对令牌）。
- **macOS 执行主机：** 在 macOS 应用中运行 `system.run`；节点主机服务通过本地IPC转发请求。
- **无 XPC 辅助工具：** 仅使用 Unix 套接字 + 令牌 + 同伴检查。

## 关键概念

### 主机

- `sandbox`：Docker 执行（当前行为）。
- `gateway`：在网关主机上执行。
- `node`：通过 Bridge 在节点运行器上执行 (`system.run`)。

### 安全模式

- `deny`：始终阻止。
- `allowlist`：仅允许匹配项。
- `full`：允许所有内容（相当于提升权限）。

### 询问模式

- `off`：从不询问。
- `on-miss`：仅在允许列表不匹配时询问。
- `always`：每次都询问。

询问 **独立** 于允许列表；允许列表可以与 `always` 或 `on-miss` 结合使用。

### 策略解析（每次执行）

1. 解析 `exec.host`（工具参数 → 代理覆盖 → 全局默认）。
2. 解析 `exec.security` 和 `exec.ask`（相同优先级）。
3. 如果主机是 `sandbox`，继续进行本地沙盒执行。
4. 如果主机是 `gateway` 或 `node`，在该主机上应用安全性和询问策略。

## 默认安全性

- 默认 `exec.host = sandbox`。
- 默认 `exec.security = deny` 对于 `gateway` 和 `node`。
- 默认 `exec.ask = on-miss`（仅在安全策略允许的情况下相关）。
- 如果没有设置节点绑定，**代理可以针对任何节点**，但只有在策略允许的情况下才能这样做。

## 配置表面

### 工具参数

- `exec.host`（可选）：`sandbox | gateway | node`。
- `exec.security`（可选）：`deny | allowlist | full`。
- `exec.ask`（可选）：`off | on-miss | always`。
- `exec.node`（可选）：当 `host=node` 时使用的节点ID/名称。

### 配置键（全局）

- `tools.exec.host`
- `tools.exec.security`
- `tools.exec.ask`
- `tools.exec.node`（默认节点绑定）

### 配置键（每个代理）

- `agents.list[].tools.exec.host`
- `agents.list[].tools.exec.security`
- `agents.list[].tools.exec.ask`
- `agents.list[].tools.exec.node`

### 别名

- `/elevated on` = 设置代理会话的 `tools.exec.host=gateway`，`tools.exec.security=full`。
- `/elevated off` = 恢复代理会话的先前执行设置。

## 批准存储（JSON）

路径：`~/.openclaw/exec-approvals.json`

目的：

- 执行主机（网关或节点运行器）的本地策略 + 允许列表。
- 当没有UI可用时的询问回退。
- UI客户端的IPC凭证。

建议架构（v1）：

```json
{
  "version": 1,
  "socket": {
    "path": "~/.openclaw/exec-approvals.sock",
    "token": "base64-opaque-token"
  },
  "defaults": {
    "security": "deny",
    "ask": "on-miss",
    "askFallback": "deny"
  },
  "agents": {
    "agent-id-1": {
      "security": "allowlist",
      "ask": "on-miss",
      "allowlist": [
        {
          "pattern": "~/Projects/**/bin/rg",
          "lastUsedAt": 0,
          "lastUsedCommand": "rg -n TODO",
          "lastResolvedPath": "/Users/user/Projects/.../bin/rg"
        }
      ]
    }
  }
}
```

注意：

- 没有旧版允许列表格式。
- `askFallback` 仅在需要 `ask` 且无法访问UI时适用。
- 文件权限：`0600`。

## 运行器服务（无头）

### 角色

- 在本地强制执行 `exec.security` + `exec.ask`。
- 执行系统命令并返回输出。
- 发射Bridge事件以进行执行生命周期（可选但推荐）。

### 服务生命周期

- 在macOS上为Launchd/守护进程；在Linux/Windows上为系统服务。
- 批准JSON是执行主机本地的。
- UI托管一个本地Unix套接字；运行器按需连接。

## UI集成（macOS应用）

### IPC

- Unix套接字位于 `~/.openclaw/exec-approvals.sock`（0600）。
- 令牌存储在 `exec-approvals.json`（0600）。
- 同伴检查：仅同一UID。
- 挑战/响应：nonce + HMAC(令牌, 请求哈希) 以防止重放。
- 短TTL（例如，10秒）+ 最大有效负载 + 速率限制。

### 询问流程（macOS应用执行主机）

1. 节点服务从网关接收 `system.run`。
2. 节点服务连接到本地套接字并发送提示/执行请求。
3. 应用验证同伴 + 令牌 + HMAC + TTL，如有必要则显示对话框。
4. 应用在UI上下文中执行命令并返回输出。
5. 节点服务将输出返回给网关。

如果缺少UI：

- 应用 `askFallback` (`deny|allowlist|full`)。

### 图表（SCI）

```
Agent -> Gateway -> Bridge -> Node Service (TS)
                         |  IPC (UDS + token + HMAC + TTL)
                         v
                     Mac App (UI + TCC + system.run)
```

## 节点身份 + 绑定

- 使用来自Bridge配对的现有 `nodeId`。
- 绑定模型：
  - `tools.exec.node` 将代理限制到特定节点。
  - 如果未设置，代理可以选择任何节点（策略仍然强制执行默认值）。
- 节点选择解析：
  - `nodeId` 精确匹配
  - `displayName`（规范化）
  - `remoteIp`
  - `nodeId` 前缀（>= 6个字符）

## 事件

### 谁能看到事件

- 系统事件是 **每个会话** 的，并在下次提示时显示给代理。
- 存储在网关的内存队列中 (`enqueueSystemEvent`)。

### 事件文本

- `Exec started (node=<id>, id=<runId>)`
- `Exec finished (node=<id>, id=<runId>, code=<code>)` + 可选输出尾部
- `Exec denied (node=<id>, id=<runId>, <reason>)`

### 传输

选项A（推荐）：

- 运行器发送Bridge `event` 帧 `exec.started` / `exec.finished`。
- 网关 `handleBridgeEvent` 将这些映射到 `enqueueSystemEvent`。

选项B：

- 网关 `exec` 工具直接处理生命周期（仅同步）。

## 执行流程

### 沙盒主机

- 现有的 `exec` 行为（Docker或未沙盒化时为主机）。
- 仅在非沙盒模式下支持PTY。

### 网关主机

- 网关进程在其自己的机器上执行。
- 强制执行本地 `exec-approvals.json`（安全/询问/允许列表）。

### 节点主机

- 网关调用 `node.invoke` 与 `system.run`。
- 运行器强制执行本地批准。
- 运行器返回聚合的stdout/stderr。
- 可选的Bridge事件用于开始/完成/拒绝。

## 输出限制

- 将组合的stdout+stderr限制在 **200k**；为事件保留 **尾部20k**。
- 使用清晰的后缀截断（例如，`"… (truncated)"`）。

## 斜杠命令

- `/exec host=<sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>`
- 每个代理、每个会话的覆盖；除非通过配置保存，否则是非持久化的。
- `/elevated on|off|ask|full` 仍然是 `host=gateway security=full` 的快捷方式（`full` 跳过批准）。

## 跨平台故事

- 运行器服务是可移植的执行目标。
- UI是可选的；如果缺少，则应用 `askFallback`。
- Windows/Linux 支持相同的批准 JSON + 套接字协议。

## 实施阶段

### 第一阶段：配置 + 执行路由

- 为 `exec.host`，`exec.security`，`exec.ask`，`exec.node` 添加配置架构。
- 更新工具管道以尊重 `exec.host`。
- 添加 `/exec` 斜杠命令并保留 `/elevated` 别名。

### 第二阶段：批准存储 + 网关强制执行

- 实现 `exec-approvals.json` 读取器/写入器。
- 强制执行 `gateway` 主机的允许列表 + 询问模式。
- 添加输出限制。

### 第三阶段：节点运行器强制执行

- 更新节点运行器以强制执行允许列表 + 询问。
- 为 macOS 应用 UI 添加 Unix 套接字提示桥接。
- 连接 `askFallback`。

### 第四阶段：事件

- 添加节点 → 网关 Bridge 事件以进行执行生命周期。
- 映射到 `enqueueSystemEvent` 以进行代理提示。

### 第五阶段：UI 磨光

- Mac 应用：允许列表编辑器、每个代理切换器、询问策略 UI。
- 节点绑定控件（可选）。

## 测试计划

- 单元测试：允许列表匹配（通配符 + 大小写不敏感）。
- 单元测试：策略解析优先级（工具参数 → 代理覆盖 → 全局）。
- 集成测试：节点运行器拒绝/允许/询问流程。
- Bridge 事件测试：节点事件 → 系统事件路由。

## 开放风险

- UI不可用：确保 `askFallback` 得到尊重。
- 长时间运行的命令：依赖超时 + 输出限制。
- 多节点歧义：除非节点绑定或显式节点参数，否则出错。

## 相关文档

- [Exec 工具](/tools/exec)
- [Exec 批准](/tools/exec-approvals)
- [节点](/nodes)
- [提升模式](/tools/elevated)