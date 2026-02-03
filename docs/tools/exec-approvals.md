---
summary: "Exec approvals, allowlists, and sandbox escape prompts"
read_when:
  - Configuring exec approvals or allowlists
  - Implementing exec approval UX in the macOS app
  - Reviewing sandbox escape prompts and implications
title: "Exec Approvals"
---
# 执行审批

执行审批是**伴侣应用 / 节点主机守护机制**，用于允许沙箱代理在真实主机（`网关`或`节点`）上运行命令。可以将其视为一种安全联锁机制：只有在策略 + 允许列表 +（可选）用户审批全部同意时，命令才被允许。执行审批**除了**工具策略和提升权限控制（除非提升权限设置为`full`，则跳过审批）之外。有效策略是`tools.exec.*`和审批默认值中**更严格**的；如果未指定审批字段，则使用`tools.exec`的值。

如果**伴侣应用 UI 不可用**，任何需要提示的请求将由**提示回退**（默认：拒绝）解决。

## 适用范围

执行审批在执行主机上本地强制执行：

- **网关主机** → 网关机器上的`openclaw`进程
- **节点主机** → 节点运行器（macOS 伴侣应用或无头节点主机）

macOS 分割：

- **节点主机服务**通过本地 IPC 将`system.run`转发到**macOS 应用**。
- **mac 电脑应用**强制执行审批 + 在 UI 上执行命令。

## 设置和存储

审批存储在执行主机上的本地 JSON 文件中：

`~/.openclaw/exec-approvals.json`

示例模式：

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

## 策略控制

### 安全性（`exec.security`）

- **拒绝**：阻止所有主机执行请求。
- **允许列表**：仅允许允许列表中的命令。
- **完全权限**：允许所有内容（等同于提升权限）。

### 提示（`exec.ask`）

- **关闭**：从不提示。
- **仅在未匹配时提示**：仅在允许列表不匹配时提示。
- **始终提示**：每次命令都提示。

### 提示回退（`askFallback`）

如果需要提示但无法访问 UI，回退决定：

- **拒绝**：阻止。
- **允许列表**：仅在允许列表匹配时允许。
- **完全权限**：允许。

## 允许列表（每代理）

允许列表是**每代理**的。如果存在多个代理，请在 macOS 应用中切换要编辑的代理。模式是**不区分大小写的通配符匹配**。模式应解析为**二进制路径**（仅 basename 的条目将被忽略）。旧的`agents.default`条目在加载时迁移到`agents.main`。

示例：

- `~/Projects/**/bin/bird`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

每个允许列表条目跟踪：

- **id** 用于 UI 身份的稳定 UUID（可选）
- **最后使用时间戳**
- **最后使用的命令**
- **最后解析的路径**

## 自动允许技能 CLI

当**自动允许技能 CLI**启用时，由已知技能引用的可执行文件在节点（macOS 节点或无头节点主机）上被视为允许列表中的条目。此功能通过网关 RPC 使用`skills.bins`获取技能二进制列表。如果您希望使用严格的手动允许列表，请禁用此功能。

## 安全二进制文件（仅标准输入）

`tools.exec.safeBins`定义了一小部分**仅标准输入**的二进制文件（例如`jq`），可以在允许列表模式下**无需显式允许列表条目**运行。安全二进制文件拒绝位置参数和路径样式的令牌，因此只能在传入流上操作。在允许列表模式下，不自动允许 shell 链接和重定向。

当每个顶层段满足允许列表（包括安全二进制文件或技能自动允许）时，允许 shell 链接（`&&`、`||`、`;`）。在允许列表模式下，重定向仍然不被支持。

默认安全二进制文件：`jq`、`grep`、`cut`、`sort`、`uniq`、`head`、`tail`、`tr`、`wc`。

## 控制 UI 编辑

使用**控制 UI → 节点 → 执行审批**卡片编辑默认值、每代理覆盖和允许列表。选择一个范围（默认值或代理），调整策略，添加/删除允许列表模式，然后**保存**。UI 会显示每个模式的**最后使用**元数据，以便您保持列表整洁。

目标选择器选择**网关**（本地审批）或**节点**。节点必须宣布`system.execApprovals.get/set`（macOS 应用或无头节点主机）。如果节点尚未宣布执行审批，请直接编辑其本地`~/.openclaw/exec-approvals.json`。

CLI：`openclaw approvals`支持网关或节点编辑（参见[审批 CLI](/cli/approvals)）。