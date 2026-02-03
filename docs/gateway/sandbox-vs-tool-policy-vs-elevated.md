---
title: Sandbox vs Tool Policy vs Elevated
summary: "Why a tool is blocked: sandbox runtime, tool allow/deny policy, and elevated exec gates"
read_when: "You hit 'sandbox jail' or see a tool/elevated refusal and want the exact config key to change."
status: active
---
# 沙箱 vs 工具策略 vs 提权

OpenClaw 有三个相关（但不同）的控制项：

1. **沙箱**（`agents.defaults.sandbox.*` / `agents.list[].sandbox.*`）决定**工具在何处运行**（Docker vs 主机）。
2. **工具策略**（`tools.*`, `tools.sandbox.tools.*`, `agents.list[].tools.*`）决定**哪些工具可用/允许**。
3. **提权**（`tools.elevated.*`, `agents.list[].tools.elevated.*`）是一个**仅执行的逃生通道**，当被沙箱限制时可在主机上运行。

## 快速调试

使用检查器查看 OpenClaw 实际在做什么：

```bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
```

它会输出：

- 有效的沙箱模式/作用域/工作区访问权限
- 会话当前是否被沙箱限制（main vs 非main）
- 有效的沙箱工具允许/拒绝（以及是否来自代理/全局/默认）
- 提权门和修复密钥路径

## 沙箱：工具运行位置

沙箱由 `agents.defaults.sandbox.mode` 控制：

- `"off"`：所有内容在主机上运行。
- `"non-main"`：仅非main会话被沙箱限制（常见于群组/频道的“意外”设置）。
- `"all"`：所有内容都被沙箱限制。

完整矩阵请参阅 [沙箱](/gateway/sandboxing)（作用域、工作区挂载、镜像）。

### 绑定挂载（安全快速检查）

- `docker.binds` 会穿透沙箱文件系统：无论你挂载什么内容，都会以你设置的模式（`:ro` 或 `:rw`）在容器中可见。
- 如果你省略模式，默认为读写；建议对源码/密钥使用 `:ro`。
- `scope: "shared"` 忽略每个代理的绑定（仅全局绑定适用）。
- 绑定 `/var/run/docker.sock` 实际上是将主机控制权交给沙箱；仅在有意情况下进行此操作。
- 工作区访问权限（`workspaceAccess: "ro"`/`"rw"`）与绑定模式无关。

## 工具策略：哪些工具存在/可调用

两个层级很重要：

- **工具配置文件**：`tools.profile` 和 `agents.list[].tools.profile`（基础允许列表）
- **提供者工具配置文件**：`tools.byProvider[provider].profile` 和 `agents.list[].tools.byProvider[provider].profile`
- **全局/每个代理工具策略**：`tools.allow`/`tools.deny` 和 `agents.list[].tools.allow`/`agents.list[].tools.deny`
- **提供者工具策略**：`tools.byProvider[provider].allow/deny` 和 `agents.list[].tools.byProvider[provider].allow/deny`
- **沙箱工具策略**（仅当被沙箱限制时适用）：`tools.sandbox.tools.allow`/`tools.sandbox.tools.deny` 和 `agents.list[].tools.sandbox.tools.*`

经验法则：

- `deny` 始终优先。
- 如果 `allow` 非空，其他内容均视为被阻止。
- 工具策略是硬性限制：`/exec` 无法覆盖被拒绝的 `exec` 工具。
- `/exec` 仅更改授权发送者的会话默认设置；它不授予工具访问权限。
  提供者工具密钥接受 `provider`（例如 `google-antigravity`）或 `provider/model`（例如 `openai/gpt-5.2`）。

### 工具组（简写）

工具策略（全局、代理、沙箱）支持 `group:*` 条目，可扩展为多个工具：

```json5
{
  tools: {
    sandbox: {
      tools: {
        allow: ["group:runtime", "group:fs", "group:sessions", "group:memory"],
      },
    },
  },
}
```

可用组：

- `group:runtime`：`exec`、`bash`、`process`
- `group:fs`：`read`、`write`、`edit`、`apply_patch`
- `group:sessions`：`sessions_list`、`sessions_history`、`sessions_send`、`sessions_spawn`、`session_status`
- `group:memory`：`memory_search`、`memory_get`
- `group:ui`：`browser`、`canvas`
- `group:automation`：`cron`、`gateway`
- `group:messaging`：`message`
- `group:nodes`：`nodes`
- `group:openclaw`：所有内置 OpenClaw 工具（排除提供者插件）

## 提权：仅执行“在主机上运行”

提权**不**授予额外工具；它仅影响 `exec`。

- 如果你被沙箱限制，`/elevated on`（或 `exec` 与 `elevated: true`）会在主机上运行（审批仍可能适用）。
- 使用 `/elevated full` 可跳过会话的 `exec` 审批。
- 如果你已经在直接运行，提权实际上是一个无操作（仍受限制）。
- 提权**不**基于技能范围，**不**覆盖工具允许/拒绝。
- `/exec` 与提权是独立的。它仅调整授权发送者的会话默认 `exec` 设置。

门：

- 启用：`tools.elevated.enabled`（可选 `agents.list[].tools.elevated.enabled`）
- 发送者允许列表：`tools.elevated.allowFrom.<provider>`（可选 `agents.list[].tools.elevated.allowFrom.<provider>`）

参阅 [提权模式](/tools/elevated)。

## 常见“沙箱监狱”修复

### “工具 X 被沙箱工具策略阻止”

修复密钥（选一个）：

- 禁用沙箱：`agents.defaults.sandbox.mode=off`（或每个代理 `agents.list[].sandbox.mode=off`）
- 在沙箱内允许该工具：
  - 从 `tools.sandbox.tools.deny` 中移除（或每个代理 `agents.list[].tools.sandbox.tools.deny`）
  - 或将其添加到 `tools.sandbox.tools.allow`（或每个代理允许）

### “我以为这是 main，