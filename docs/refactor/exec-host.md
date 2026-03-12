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

- 添加 `exec.host` + `exec.security`，以在 **沙箱**、**网关** 和 **节点** 之间路由执行。
- 默认配置保持 **安全**：除非显式启用，否则禁止跨主机执行。
- 将执行拆分为一个 **无头运行器服务**，并可通过本地 IPC 提供可选的 UI（macOS 应用）。
- 提供 **按代理** 的策略、白名单、询问模式及节点绑定功能。
- 支持既可与白名单配合使用、也可独立使用的 **询问模式**。
- 跨平台支持：Unix 套接字 + Token 认证（macOS/Linux/Windows 功能一致）。

## 非目标

- 不支持旧版白名单迁移或旧版模式兼容。
- 不为节点执行提供 PTY/流式传输（仅支持聚合输出）。
- 不引入除现有 Bridge + Gateway 之外的新网络层。

## 已确定的决策（锁定）

- **配置项键名**：`exec.host` + `exec.security`（允许按代理覆盖）。
- **提权机制**：保留 `/elevated` 作为网关完全访问权限的别名。
- **询问默认值**：`on-miss`。
- **审批存储**：`~/.openclaw/exec-approvals.json`（JSON 格式，不进行旧版迁移）。
- **运行器**：无头系统服务；UI 应用托管一个 Unix 套接字用于审批。
- **节点身份标识**：复用现有的 `nodeId`。
- **套接字认证**：Unix 套接字 + Token（跨平台）；后续如需可再拆分。
- **节点主机状态**：`~/.openclaw/node.json`（节点 ID + 配对 Token）。
- **macOS 执行主机**：在 macOS 应用内运行 `system.run`；节点主机服务通过本地 IPC 转发请求。
- **不使用 XPC Helper**：坚持采用 Unix 套接字 + Token + 对等方检查。

## 核心概念

### 主机（Host）

- `sandbox`：Docker exec（当前行为）。
- `gateway`：在网关主机上执行。
- `node`：通过 Bridge 在节点运行器上执行（`system.run`）。

### 安全模式（Security mode）

- `deny`：始终阻止。
- `allowlist`：仅允许匹配项。
- `full`：允许全部（等效于提权模式）。

### 询问模式（Ask mode）

- `off`：从不询问。
- `on-miss`：仅当白名单不匹配时询问。
- `always`：每次均询问。

询问行为与白名单 **相互独立**；白名单可与 `always` 或 `on-miss` 配合使用。

### 策略解析（每次执行）

1. 解析 `exec.host`（工具参数 → 代理覆盖 → 全局默认）。
2. 解析 `exec.security` 和 `exec.ask`（优先级相同）。
3. 若主机为 `sandbox`，则执行本地沙箱执行。
4. 若主机为 `gateway` 或 `node`，则在该主机上应用安全策略 + 询问策略。

## 默认安全性

- 默认 `exec.host = sandbox`。
- `gateway` 和 `node` 默认为 `exec.security = deny`。
- 默认 `exec.ask = on-miss`（仅当安全策略允许时生效）。
- 若未设置节点绑定，则 **代理可指向任意节点**，但前提是策略允许。

## 配置面（Config surface）

### 工具参数

- `exec.host`（可选）：`sandbox | gateway | node`。
- `exec.security`（可选）：`deny | allowlist | full`。
- `exec.ask`（可选）：`off | on-miss | always`。
- `exec.node`（可选）：当 `host=node` 时使用的节点 ID/名称。

### 配置项键名（全局）

- `tools.exec.host`
- `tools.exec.security`
- `tools.exec.ask`
- `tools.exec.node`（默认节点绑定）

### 配置项键名（按代理）

- `agents.list[].tools.exec.host`
- `agents.list[].tools.exec.security`
- `agents.list[].tools.exec.ask`
- `agents.list[].tools.exec.node`

### 别名

- `/elevated on` = 为代理会话设置 `tools.exec.host=gateway` 和 `tools.exec.security=full`。
- `/elevated off` = 恢复代理会话之前的执行设置。

## 审批存储（JSON）

路径：`~/.openclaw/exec-approvals.json`

用途：

- 本地策略 + 白名单，适用于 **执行主机**（网关或节点运行器）。
- 当无 UI 可用时，作为询问的后备方案。
- UI 客户端的 IPC 凭据。

建议的 Schema（v1）：

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

说明：

- 不支持旧版白名单格式。
- `askFallback` 仅在 `ask` 被要求且无法连接 UI 时生效。
- 文件权限：`0600`。

## 运行器服务（无头）

### 角色

- 在本地强制执行 `exec.security` + `exec.ask`。
- 执行系统命令并返回输出。
- 发送 Bridge 事件以反映执行生命周期（可选，但推荐启用）。

### 服务生命周期

- macOS 上使用 launchd/daemon；Linux/Windows 上使用系统服务。
- 审批 JSON 文件位于执行主机本地。
- UI 托管一个本地 Unix 套接字；运行器按需连接。

## UI 集成（macOS 应用）

### IPC

- Unix 套接字位于 `~/.openclaw/exec-approvals.sock`（0600 权限）。
- Token 存储于 `exec-approvals.json`（0600 权限）。
- 对等方检查：仅限相同 UID。
- 挑战/响应机制：nonce + HMAC(token, request-hash)，防止重放攻击。
- 短有效期（例如 10 秒）+ 最大载荷限制 + 速率限制。

### 询问流程（macOS 应用执行主机）

1. 节点服务从网关接收 `system.run`。
2. 节点服务连接至本地套接字，并发送提示/执行请求。
3. 应用验证对等方 + Token + HMAC + 有效期，必要时显示对话框。
4. 应用在 UI 上下文中执行命令并返回输出。
5. 节点服务将输出返回给网关。

若 UI 缺失：

- 应用 `askFallback`（`deny|allowlist|full`）。

### 示意图（SCI）

```
Agent -> Gateway -> Bridge -> Node Service (TS)
                         |  IPC (UDS + token + HMAC + TTL)
                         v
                     Mac App (UI + TCC + system.run)
```

## 节点身份标识 + 绑定

- 复用 Bridge 配对中已有的 `nodeId`。
- 绑定模型：
  - `tools.exec.node` 将代理限制到特定节点。
  - 若未设置，则代理可选择任意节点（策略仍强制执行默认值）。
- 节点选择解析规则：
  - `nodeId` 精确匹配
  - `displayName`（规范化后）
  - `remoteIp`
  - `nodeId` 前缀匹配（≥ 6 字符）

## 事件通知（Eventing）

### 事件可见性

- 系统事件按 **会话** 分组，并在下次提示时向代理展示。
- 存储于网关内存队列中（`enqueueSystemEvent`）。

### 事件文本内容

- `Exec started (node=<id>, id=<runId>)`
- `Exec finished (node=<id>, id=<runId>, code=<code>)` + 可选输出尾部
- `Exec denied (node=<id>, id=<runId>, <reason>)`

### 传输方式

选项 A（推荐）：

- 运行器发送 Bridge `event` 帧，经由 `exec.started` / `exec.finished`。
- 网关 `handleBridgeEvent` 将其映射为 `enqueueSystemEvent`。

选项 B：

- 网关 `exec` 工具直接处理生命周期（仅同步方式）。

## 执行流程（Exec flows）

### 沙箱主机（Sandbox host）

- 沿用现有的 `exec` 行为（Docker 或非沙箱模式下的宿主机）。
- PTY 仅在非沙箱模式下支持。

### 网关主机（Gateway host）

- 网关进程在其自身机器上执行。
- 强制执行本地 `exec-approvals.json`（安全/询问/白名单）。

### 节点主机（Node host）

- 网关调用 `node.invoke` 并传入 `system.run`。
- 运行器强制执行本地审批。
- 运行器返回聚合的 stdout/stderr。
- 可选：发送 Bridge 事件以指示开始/完成/拒绝。

## 输出限制（Output caps）

- 合并 stdout+stderr 总大小上限为 **200k**；事件中保留 **尾部 20k**。
- 截断时添加明确后缀（例如 `"… (truncated)"`）。

## 斜杠命令（Slash commands）

- `/exec host=<sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>`
- 按代理、按会话覆盖；除非通过配置保存，否则不持久化。
- `/elevated on|off|ask|full` 仍是 `host=gateway security=full` 的快捷方式（其中 `full` 跳过审批）。

## 跨平台支持（Cross-platform story）

- 运行器服务是可移植的执行目标。
- UI 为可选组件；若缺失，则应用 `askFallback`。
- Windows/Linux 同样支持相同的审批 JSON + 套接字协议。

## 实施阶段（Implementation phases）

### 第一阶段：配置 + 执行路由

- 为 `exec.host`、`exec.security`、`exec.ask`、`exec.node` 添加配置模式。
- 更新工具链以遵循 `exec.host`。
- 添加 `/exec` 斜杠命令，并保留 `/elevated` 别名。

### 第二阶段：审批存储 + 网关强制执行

- 实现 `exec-approvals.json` 的读写器。
- 对 `gateway` 主机强制执行白名单 + 询问模式。
- 添加输出限制。

### 第三阶段：节点运行器强制执行

- 更新节点运行器以强制执行白名单 + 询问。
- 添加 Unix 套接字提示桥接到 macOS 应用 UI。
- 接入 `askFallback`。

### 第四阶段：事件通知

- 添加节点 → 网关的 Bridge 事件，用于执行生命周期管理。
- 映射为 `enqueueSystemEvent`，供代理提示使用。

### 第五阶段：UI 优化

- macOS 应用：白名单编辑器、按代理切换器、询问策略 UI。
- 节点绑定控件（可选）。

## 测试计划（Testing plan）

- 单元测试：白名单匹配（通配符 + 不区分大小写）。
- 单元测试：策略解析优先级（工具参数 → 代理覆盖 → 全局默认）。
- 集成测试：节点运行器拒绝/允许/询问流程。
- Bridge 事件测试：节点事件 → 系统事件路由。

## 待识别风险（Open risks）

- UI 不可用：确保遵守 `askFallback`。
- 长时间运行命令：依赖超时 + 输出限制。
- 多节点歧义：除非设置了节点绑定或显式指定节点参数，否则报错。

## 相关文档（Related docs）

- [Exec 工具](/tools/exec)
- [Exec 审批](/tools/exec-approvals)
- [节点](/nodes)
- [提权模式](/tools/elevated)