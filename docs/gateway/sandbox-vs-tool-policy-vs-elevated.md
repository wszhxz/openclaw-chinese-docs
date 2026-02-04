---
title: Sandbox vs Tool Policy vs Elevated
summary: "Why a tool is blocked: sandbox runtime, tool allow/deny policy, and elevated exec gates"
read_when: "You hit 'sandbox jail' or see a tool/elevated refusal and want the exact config key to change."
status: active
---
# 沙盒 vs 工具策略 vs 提升权限

OpenClaw 有三个相关的（但不同的）控制：

1. **沙盒** (`agents.defaults.sandbox.*` / `agents.list[].sandbox.*`) 决定 **工具运行的位置**（Docker vs 主机）。
2. **工具策略** (`tools.*`, `tools.sandbox.tools.*`, `agents.list[].tools.*`) 决定 **哪些工具可用/允许**。
3. **提升权限** (`tools.elevated.*`, `agents.list[].tools.elevated.*`) 是一个 **仅执行的逃生舱**，当你被沙盒化时可以在主机上运行。

## 快速调试

使用检查器查看 OpenClaw 实际上在做什么：

```bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
```

它会打印：

- 有效的沙盒模式/范围/工作区访问
- 当前会话是否被沙盒化（主会话 vs 非主会话）
- 有效的沙盒工具允许/拒绝（以及它来自代理/全局/默认）
- 提升权限门和修复密钥路径

## 沙盒：工具运行的位置

沙盒化由 `agents.defaults.sandbox.mode` 控制：

- `"off"`：所有内容都在主机上运行。
- `"non-main"`：只有非主会话被沙盒化（常见的“惊喜”对于组/频道）。
- `"all"`：所有内容都被沙盒化。

参见 [沙盒化](/gateway/sandboxing) 获取完整的矩阵（范围、工作区挂载、镜像）。

### 绑定挂载（安全快速检查）

- `docker.binds` _穿透_ 沙盒文件系统：无论你挂载什么，都会以你设置的模式在容器内部可见 (`:ro` 或 `:rw`)。
- 如果省略模式，默认是读写；对于源/秘密，建议使用 `:ro`。
- `scope: "shared"` 忽略每个代理的绑定（只应用全局绑定）。
- 绑定 `/var/run/docker.sock` 实际上将主机控制权交给沙盒；只有有意为之才这样做。
- 工作区访问 (`workspaceAccess: "ro"`/`"rw"`) 独立于绑定模式。

## 工具策略：哪些工具存在/可调用

两层很重要：

- **工具配置文件**：`tools.profile` 和 `agents.list[].tools.profile`（基础白名单）
- **提供商工具配置文件**：`tools.byProvider[provider].profile` 和 `agents.list[].tools.byProvider[provider].profile`
- **全局/每个代理工具策略**：`tools.allow`/`tools.deny` 和 `agents.list[].tools.allow`/`agents.list[].tools.deny`
- **提供商工具策略**：`tools.byProvider[provider].allow/deny` 和 `agents.list[].tools.byProvider[provider].allow/deny`
- **沙盒工具策略**（仅在沙盒化时适用）：`tools.sandbox.tools.allow`/`tools.sandbox.tools.deny` 和 `agents.list[].tools.sandbox.tools.*`

经验法则：

- `deny` 总是获胜。
- 如果 `allow` 不为空，则其他所有内容被视为被阻止。
- 工具策略是硬停止：`/exec` 无法覆盖被拒绝的 `exec` 工具。
- `/exec` 仅更改授权发送者的会话默认值；它不授予工具访问权限。
  提供商工具密钥接受 `provider`（例如 `google-antigravity`）或 `provider/model`（例如 `openai/gpt-5.2`）。

### 工具组（快捷方式）

工具策略（全局、代理、沙盒）支持 `group:*` 条目，这些条目会扩展为多个工具：

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

- `group:runtime`: `exec`, `bash`, `process`
- `group:fs`: `read`, `write`, `edit`, `apply_patch`
- `group:sessions`: `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status`
- `group:memory`: `memory_search`, `memory_get`
- `group:ui`: `browser`, `canvas`
- `group:automation`: `cron`, `gateway`
- `group:messaging`: `message`
- `group:nodes`: `nodes`
- `group:openclaw`: 所有内置的 OpenClaw 工具（排除提供商插件）

## 提升权限：仅执行“在主机上运行”

提升权限 **不** 授予额外的工具；它仅影响 `exec`。

- 如果你被沙盒化，`/elevated on`（或带有 `elevated: true` 的 `exec`）将在主机上运行（可能仍需批准）。
- 使用 `/elevated full` 跳过会话的执行批准。
- 如果你已经在直接运行，提升权限实际上是无操作（仍然受限制）。
- 提升权限 **不是** 技能范围内的，并且 **不** 覆盖工具允许/拒绝。
- `/exec` 与提升权限分开。它仅调整授权发送者的会话执行默认值。

门：

- 启用：`tools.elevated.enabled`（可选 `agents.list[].tools.elevated.enabled`）
- 发送者白名单：`tools.elevated.allowFrom.<provider>`（可选 `agents.list[].tools.elevated.allowFrom.<provider>`）

参见 [提升权限模式](/tools/elevated)。

## 常见的“沙盒监狱”修复

### “工具 X 被沙盒工具策略阻止”

修复密钥（选择一个）：

- 禁用沙盒：`agents.defaults.sandbox.mode=off`（或每个代理的 `agents.list[].sandbox.mode=off`）
- 允许工具在沙盒中：
  - 从 `tools.sandbox.tools.deny` 中移除（或每个代理的 `agents.list[].tools.sandbox.tools.deny`）
  - 或添加到 `tools.sandbox.tools.allow`（或每个代理的允许列表）

### “我以为这是主会话，为什么被沙盒化了？”

在 `"non-main"` 模式下，组/频道密钥 **不是** 主会话。使用主会话密钥（由 `sandbox explain` 显示）或切换模式到 `"off"`。