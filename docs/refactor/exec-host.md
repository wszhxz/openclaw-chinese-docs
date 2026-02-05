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

- 添加 `exec.host` + `exec.security` 来路由在**沙箱**、**网关**和**节点**之间的执行。
- 保持默认值**安全**：除非明确启用，否则不允许跨主机执行。
- 将执行拆分为一个**无头运行器服务**，通过本地IPC提供可选UI（macOS应用）。
- 提供**每个代理**的策略、白名单、询问模式和节点绑定。
- 支持**询问模式**，可以与或不与白名单一起工作。
- 跨平台：Unix套接字 + 令牌认证（macOS/Linux/Windows一致性）。

## 非目标

- 不进行遗留白名单迁移或遗留架构支持。
- 不支持节点执行的PTY/流式传输（仅聚合输出）。
- 不在现有Bridge + Gateway之外创建新的网络层。

## 决策（已锁定）

- **配置键：** `exec.host` + `exec.security` （允许每个代理覆盖）。
- **提升权限：** 保持 `/elevated` 作为网关完全访问的别名。
- **询问默认值：** `on-miss`。
- **审批存储：** `~/.openclaw/exec-approvals.json` （JSON，无遗留迁移）。
- **运行器：** 无头系统服务；UI应用托管Unix套接字用于审批。
- **节点身份：** 使用现有的 `nodeId`。
- **套接字认证：** Unix套接字 + 令牌（跨平台）；如有需要稍后分离。
- **节点主机状态：** `~/.openclaw/node.json` （节点ID + 配对令牌）。
- **macOS执行主机：** 在macOS应用内部运行 `system.run` ；节点主机服务通过本地IPC转发请求。
- **无XPC助手：** 坚持使用Unix套接字 + 令牌 + 对等检查。

## 关键概念

### 主机

- `sandbox`：Docker执行（当前行为）。
- `gateway`：在网关主机上执行。
- `node`：通过Bridge在节点运行器上执行（`system.run`）。

### 安全模式

- `deny`：始终阻止。
- `allowlist`：仅允许匹配项。
- `full`：允许所有内容（等同于提升权限）。

### 询问模式

- `off`：从不询问。
- `on-miss`：仅当白名单不匹配时询问。
- `always`：每次都询问。

询问与白名单**独立**；白名单可以与 `always` 或 `on-miss` 一起使用。

### 策略解析（每次执行）

1. 解析 `exec.host` （工具参数 → 代理覆盖 → 全局默认值）。
2. 解析 `exec.security` 和 `exec.ask` （相同优先级）。
3. 如果主机是 `sandbox`，继续进行本地沙箱执行。
4. 如果主机是 `gateway` 或 `node`，在该主机上应用安全+询问策略。

## 默认安全性

- 默认 `exec.host = sandbox`。
- 默认 `exec.security = deny` 用于 `gateway` 和 `node`。
- 默认 `exec.ask = on-miss` （仅在安全允许时相关）。
- 如果未设置节点绑定，**代理可能针对任何节点**，但前提是策略允许。

## 配置表面

### 工具参数

- `exec.host` （可选）：`sandbox | gateway | node`。
- `exec.security` （可选）：`deny | allowlist | full`。
- `exec.ask` （可选）：`off | on-miss | always`。
- `exec.node` （可选）：当 `host=node` 时使用的节点ID/名称。

### 配置键（全局）

- `tools.exec.host`
- `tools.exec.security`
- `tools.exec.ask`
- `tools.exec.node` （默认节点绑定）

### 配置键（每个代理）

- `agents.list[].tools.exec.host`
- `agents.list[].tools.exec.security`
- `agents.list[].tools.exec.ask`
- `agents.list[].tools.exec.node`

### 别名

- `/elevated on` = 为代理会话设置 `tools.exec.host=gateway`、`tools.exec.security=full`。
- `/elevated off` = 恢复代理会话的先前执行设置。

## 审批存储（JSON）

路径：`~/.openclaw/exec-approvals.json`

目的：

- **执行主机**（网关或节点运行器）的本地策略+白名单。
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

注意事项：

- 无遗留白名单格式。
- `askFallback` 仅在需要 `ask` 且无法访问UI时应用。
- 文件权限：`0600`。

## 运行器服务（无头）

### 角色

- 在本地强制执行 `exec.security` + `exec.ask`。
- 执行系统命令并返回输出。
- 发出Bridge事件以执行生命周期（可选但推荐）。

### 服务生命周期

- macOS上的Launchd/守护进程；Linux/Windows上的系统服务。
- 审批JSON位于执行主机本地。
- UI托管本地Unix套接字；运行器按需连接。

## UI集成（macOS应用）

### IPC

- Unix套接字位于 `~/.openclaw/exec-approvals.sock` （0600）。
- 令牌存储在 `exec-approvals.json` （0600）。
- 对等检查：仅限相同UID。
- 挑战/响应：nonce + HMAC(token, request-hash) 以防止重放。
- 短TTL（例如10秒）+ 最大负载 + 速率限制。

### 询问流程（macOS应用执行主机）

1. 节点服务从网关接收 `system.run`。
2. 节点服务连接到本地套接字并发送提示/执行请求。
3. 应用验证对等方+令牌+HMAC+TTL，然后根据需要显示对话框。
4. 应用在UI上下文中执行命令并返回输出。
5. 节点服务将输出返回给网关。

如果UI缺失：

- 应用 `askFallback` （`deny|allowlist|full`）。

### 图表（SCI）

```
Agent -> Gateway -> Bridge -> Node Service (TS)
                         |  IPC (UDS + token + HMAC + TTL)
                         v
                     Mac App (UI + TCC + system.run)
```

## 节点身份+绑定

- 使用来自Bridge配对的现有 `nodeId`。
- 绑定模型：
  - `tools.exec.node` 将代理限制为特定节点。
  - 如果未设置，代理可以选择任何节点（策略仍强制执行默认值）。
- 节点选择解析：
  - `nodeId` 精确匹配
  - `displayName` （标准化）
  - `remoteIp`
  - `nodeId` 前缀（>= 6个字符）

## 事件处理

### 谁能看到事件

- 系统事件是**每个会话**的，并在下一个提示中显示给代理。
- 存储在网关内存队列中（`enqueueSystemEvent`）。

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

### 沙箱主机

- 现有 `exec` 行为（Docker或未沙箱化时的主机）。
- PTY仅在非沙箱模式下受支持。

### 网关主机

- 网关进程在其自己的机器上执行。
- 强制执行本地 `exec-approvals.json` （安全/询问/白名单）。

### 节点主机

- 网关调用 `node.invoke` 与 `system.run`。
- 运行器强制执行本地审批。
- 运行器返回聚合的stdout/stderr。
- 可选的Bridge事件用于开始/完成/拒绝。

## 输出限制

- 将组合的stdout+stderr限制在**200k**；保留**尾部20k**用于事件。
- 用清晰的后缀截断（例如，`"… (truncated)"`）。

## 斜杠命令

- `/exec host=<sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>`
- 每个代理，每个会话覆盖；除非通过配置保存，否则非持久性。
- `/elevated on|off|ask|full` 仍然是 `host=gateway security=full` 的快捷方式（带有 `full` 跳过审批）。

## 跨平台故事

- 运行器服务是可移植的执行目标。
- UI是可选的；如果缺失，应用 `askFallback`。
- Windows/Linux支持相同的审批JSON + 套接字协议。

## 实施阶段

### 第一阶段：配置+执行路由

- 为 `exec.host`、`exec.security`、`exec.ask`、`exec.node` 添加配置架构。
- 更新工具管道以尊重 `exec.host`。
- 添加 `/exec` 斜杠命令并保留 `/elevated` 别名。

### 第二阶段：审批存储+网关强制执行

- 实现 `exec-approvals.json` 读取器/写入器。
- 为 `gateway` 主机强制执行白名单+询问模式。
- 添加输出限制。

### 第三阶段：节点运行器强制执行

- 更新节点运行器以强制执行白名单+询问。
- 向macOS应用UI添加Unix套接字提示桥。
- 连接 `askFallback`。

### 第四阶段：事件

- 为执行生命周期添加节点→网关Bridge事件。
- 映射到 `enqueueSystemEvent` 用于代理提示。

### 第五阶段：UI优化

- Mac应用：白名单编辑器，每个代理切换器，询问策略UI。
- 节点绑定控件（可选）。

## 测试计划

- 单元测试：白名单匹配（通配符+不区分大小写）。
- 单元测试：策略解析优先级（工具参数→代理覆盖→全局）。
- 集成测试：节点运行器拒绝/允许/询问流程。
- Bridge事件测试：节点事件→系统事件路由。

## 开放风险

- UI不可用：确保尊重 `askFallback`。
- 长时间运行的命令：依赖超时+输出限制。
- 多节点歧义：除非节点绑定或显式节点参数，否则报错。

## 相关文档

- [执行工具](/tools/exec)
- [执行审批](/tools/exec-approvals)
- [节点](/nodes)
- [提升模式](/tools/elevated)