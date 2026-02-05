---
summary: "Exec approvals, allowlists, and sandbox escape prompts"
read_when:
  - Configuring exec approvals or allowlists
  - Implementing exec approval UX in the macOS app
  - Reviewing sandbox escape prompts and implications
title: "Exec Approvals"
---
# 执行审批

执行审批是让沙盒代理在真实主机（`gateway` 或 `node`）上运行命令的 **配套应用程序/节点主机防护栏**。可以将其视为安全联锁：只有当策略 + 允许列表 + （可选）用户审批都同意时，才允许执行命令。
执行审批是 **除了** 工具策略和提升门控之外的（除非将提升设置为 `full`，这将跳过审批）。
有效策略是 `tools.exec.*` 和审批默认值中 **更严格的**；如果省略了审批字段，则使用 `tools.exec` 的值。

如果配套应用程序UI **不可用**，任何需要提示的请求将由 **ask 回退**（默认：拒绝）解决。

## 应用范围

执行审批在执行主机上本地强制执行：

- **网关主机** → 网关机器上的 `openclaw` 进程
- **节点主机** → 节点运行器（macOS 配套应用程序或无头节点主机）

macOS 分割：

- **节点主机服务**通过本地 IPC 将 `system.run` 转发到 **macOS 应用程序**。
- **macOS 应用程序** 强制执行审批并以 UI 上下文执行命令。

## 设置和存储

审批存储在执行主机上的本地 JSON 文件中：

`~/.openclaw/exec-approvals.json`

示例架构：

```json
{
  "version": 1,
  "socket": {
    "path": "~/.openclaw/exec-approvals.sock",
    "token": "base64url-token"
  },
  "defaults": {
    "security": "deny",
    "ask": "on-miss",
    "askFallback": "deny",
    "autoAllowSkills": false
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "askFallback": "deny",
      "autoAllowSkills": true,
      "allowlist": [
        {
          "id": "B0C8C0B3-2C2D-4F8A-9A3C-5A4B3C2D1E0F",
          "pattern": "~/Projects/**/bin/rg",
          "lastUsedAt": 1737150000000,
          "lastUsedCommand": "rg -n TODO",
          "lastResolvedPath": "/Users/user/Projects/.../bin/rg"
        }
      ]
    }
  }
}
```

## 策略选项

### 安全性 (`exec.security`)

- **deny**: 阻止所有主机执行请求。
- **allowlist**: 仅允许允许列表中的命令。
- **full**: 允许所有内容（等同于提升）。

### Ask (`exec.ask`)

- **off**: 从不提示。
- **on-miss**: 仅在允许列表不匹配时提示。
- **always**: 对每个命令都提示。

### Ask 回退 (`askFallback`)

如果需要提示但无法访问 UI，则回退决定：

- **deny**: 阻止。
- **allowlist**: 仅在允许列表匹配时允许。
- **full**: 允许。

## 允许列表（每个代理）

允许列表是 **每个代理** 的。如果存在多个代理，请在 macOS 应用程序中切换正在编辑的代理。模式是 **不区分大小写的通配符匹配**。
模式应解析为 **二进制路径**（仅基于名称的条目将被忽略）。加载时，旧的 `agents.default` 条目将迁移到 `agents.main`。

示例：

- `~/Projects/**/bin/bird`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

每个允许列表条目跟踪：

- **id** 用于 UI 标识的稳定 UUID（可选）
- **最后使用时间戳**
- **最后使用的命令**
- **最后解析的路径**

## 自动允许技能 CLI

当启用 **自动允许技能 CLI** 时，由已知技能引用的可执行文件被视为节点上的允许列表（macOS 节点或无头节点主机）。这使用 `skills.bins` 通过网关 RPC 获取技能二进制列表。如果您希望严格的手动允许列表，请禁用此功能。

## 安全二进制（仅限 stdin）

`tools.exec.safeBins` 定义了一个小型的 **仅限 stdin** 的二进制文件列表（例如 `jq`），这些二进制文件可以在允许列表模式下 **无需** 显式允许列表条目即可运行。安全二进制文件拒绝位置文件参数和路径样式的令牌，因此它们只能操作传入流。
在允许列表模式下，不允许自动链式 shell 和重定向。

链式 shell (`&&`, `||`, `;`) 在每个顶级段满足允许列表时被允许（包括安全二进制文件或技能自动允许）。重定向在允许列表模式下仍然不受支持。
命令替换 (`$()` / 反引号) 在允许列表解析期间被拒绝，包括在双引号内；如果需要字面 `$()` 文本，请使用单引号。

默认安全二进制文件：`jq`, `grep`, `cut`, `sort`, `uniq`, `head`, `tail`, `tr`, `wc`。

## 控制 UI 编辑

使用 **控制 UI → 节点 → 执行审批** 卡片来编辑默认设置、每个代理的覆盖和允许列表。选择一个范围（默认或代理），调整策略，添加/删除允许列表模式，然后 **保存**。UI 显示每个模式的 **最后使用** 元数据，以便您可以保持列表整洁。

目标选择器选择 **网关**（本地审批）或 **节点**。节点必须通告 `system.execApprovals.get/set`（macOS 应用程序或无头节点主机）。
如果节点尚未通告执行审批，请直接编辑其本地 `~/.openclaw/exec-approvals.json`。

CLI: `openclaw approvals` 支持网关或节点编辑（参见 [审批 CLI](/cli/approvals)）。

## 审批流程

当需要提示时，网关向操作员客户端广播 `exec.approval.requested`。控制 UI 和 macOS 应用程序通过 `exec.approval.resolve` 解析它，然后网关将批准的请求转发到节点主机。

当需要审批时，执行工具会立即返回一个审批 ID。使用该 ID 来关联后续的系统事件 (`Exec finished` / `Exec denied`)。如果在超时之前没有收到决策，则请求被视为审批超时，并作为拒绝原因显示。

确认对话框包括：

- 命令 + 参数
- 当前工作目录
- 代理 ID
- 解析后的可执行文件路径
- 主机 + 策略元数据

操作：

- **允许一次** → 立即运行
- **始终允许** → 添加到允许列表 + 运行
- **拒绝** → 阻止

## 将审批转发到聊天频道

您可以将执行审批提示转发到任何聊天频道（包括插件频道），并通过 `/approve` 批准它们。这使用正常的出站交付管道。

配置：

```json5
{
  approvals: {
    exec: {
      enabled: true,
      mode: "session", // "session" | "targets" | "both"
      agentFilter: ["main"],
      sessionFilter: ["discord"], // substring or regex
      targets: [
        { channel: "slack", to: "U12345678" },
        { channel: "telegram", to: "123456789" },
      ],
    },
  },
}
```

聊天回复：

```
/approve <id> allow-once
/approve <id> allow-always
/approve <id> deny
```

### macOS IPC 流程

```
Gateway -> Node Service (WS)
                 |  IPC (UDS + token + HMAC + TTL)
                 v
             Mac App (UI + approvals + system.run)
```

安全注意事项：

- Unix 套接字模式 `0600`，令牌存储在 `exec-approvals.json` 中。
- 同 UID 对等检查。
- 挑战/响应（随机数 + HMAC 令牌 + 请求哈希）+ 短 TTL。

## 系统事件

执行生命周期以系统消息的形式呈现：

- `Exec running`（仅当命令超过运行通知阈值时）
- `Exec finished`
- `Exec denied`

这些消息在节点报告事件后发布到代理的会话中。
网关主机执行审批在命令完成后发出相同的生命周期事件（可选地在超过阈值时发出）。
审批门控的执行重用审批 ID 作为这些消息中的 `runId` 以便轻松关联。

## 影响

- **full** 功能强大；尽可能使用允许列表。
- **ask** 让您保持知情，同时仍允许快速审批。
- 每个代理的允许列表防止一个代理的审批泄露到其他代理。
- 审批仅适用于来自 **授权发送者** 的主机执行请求。未经授权的发送者无法发出 `/exec`。
- `/exec security=full` 是授权操作员的会话级别便利功能，设计上跳过审批。
  为了硬阻止主机执行，请将审批安全性设置为 `deny` 或通过工具策略拒绝 `exec` 工具。

相关：

- [执行工具](/tools/exec)
- [提升模式](/tools/elevated)
- [技能](/tools/skills)