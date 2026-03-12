---
title: Sandbox vs Tool Policy vs Elevated
summary: "Why a tool is blocked: sandbox runtime, tool allow/deny policy, and elevated exec gates"
read_when: "You hit 'sandbox jail' or see a tool/elevated refusal and want the exact config key to change."
status: active
---
# 沙箱 vs 工具策略 vs 提权

OpenClaw 包含三个相关（但不同）的控制机制：

1. **沙箱**（``agents.defaults.sandbox.*`` / ``agents.list[].sandbox.*``）决定**工具在何处运行**（Docker 容器内 vs 主机上）。
2. **工具策略**（``tools.*``、``tools.sandbox.tools.*``、``agents.list[].tools.*``）决定**哪些工具可用/被允许调用**。
3. **提权**（``tools.elevated.*``、``agents.list[].tools.elevated.*``）是一种**仅限执行的逃生通道**，用于在启用沙箱时于主机上运行命令。

## 快速调试

使用检查器（inspector）查看 OpenClaw **实际执行的操作**：

````bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
````

它将输出：

- 当前生效的沙箱模式/作用域/工作区访问权限
- 当前会话是否处于沙箱中（主会话 vs 非主会话）
- 当前生效的沙箱工具允许/拒绝规则（以及该规则来源：agent 级、全局级或默认值）
- 提权门控（gates）及修复键路径（fix-it key paths）

## 沙箱：工具运行位置

沙箱行为由 ``agents.defaults.sandbox.mode`` 控制：

- ``"off"``：所有内容均在主机上运行。
- ``"non-main"``：仅非主会话被沙箱化（群组/频道中常见的“意外”行为）。
- ``"all"``：所有内容均被沙箱化。

详见 [沙箱化](/gateway/sandboxing) 中的完整矩阵（作用域、工作区挂载、镜像）。

### 绑定挂载（安全快速检查）

- ``docker.binds`` 会**穿透**沙箱文件系统：您所挂载的内容将以设定的模式（``:ro`` 或 ``:rw``）在容器内可见。
- 若未指定模式，默认为读写；对于源码/密钥等敏感内容，请优先使用 ``:ro``。
- ``scope: "shared"`` 忽略按 agent 设置的绑定挂载（仅全局绑定挂载生效）。
- 绑定 ``/var/run/docker.sock`` 实质上将主机控制权交予沙箱；请仅在明确意图下执行此操作。
- 工作区访问权限（``workspaceAccess: "ro"``/``"rw"``）与绑定模式无关。

## 工具策略：哪些工具存在/可被调用

两个层级起关键作用：

- **工具配置文件**：``tools.profile`` 和 ``agents.list[].tools.profile``（基础白名单）
- **提供方工具配置文件**：``tools.byProvider[provider].profile`` 和 ``agents.list[].tools.byProvider[provider].profile``
- **全局/每 agent 工具策略**：``tools.allow``/``tools.deny`` 和 ``agents.list[].tools.allow``/``agents.list[].tools.deny``
- **提供方工具策略**：``tools.byProvider[provider].allow/deny`` 和 ``agents.list[].tools.byProvider[provider].allow/deny``
- **沙箱工具策略**（仅在启用沙箱时生效）：``tools.sandbox.tools.allow``/``tools.sandbox.tools.deny`` 和 ``agents.list[].tools.sandbox.tools.*``

经验法则：

- ``deny`` 始终具有最高优先级。
- 若 ``allow`` 非空，则其余所有策略均视为被阻断。
- 工具策略是硬性限制：``/exec`` 无法覆盖已被拒绝的 ``exec`` 工具。
- ``/exec`` 仅更改已授权发送者的会话默认设置；它**不授予**工具访问权限。  
  提供方工具键支持两种格式：``provider``（例如 ``google-antigravity``）或 ``provider/model``（例如 ``openai/gpt-5.2``）。

### 工具组（简写形式）

工具策略（全局、agent 级、沙箱级）支持 ``group:*`` 条目，这些条目将展开为多个具体工具：

````json5
{
  tools: {
    sandbox: {
      tools: {
        allow: ["group:runtime", "group:fs", "group:sessions", "group:memory"],
      },
    },
  },
}
````

可用的工具组包括：

- ``group:runtime``：``exec``、``bash``、``process``
- ``group:fs``：``read``、``write``、``edit``、``apply_patch``
- ``group:sessions``：``sessions_list``、``sessions_history``、``sessions_send``、``sessions_spawn``、``session_status``
- ``group:memory``：``memory_search``、``memory_get``
- ``group:ui``：``browser``、``canvas``
- ``group:automation``：``cron``、``gateway``
- ``group:messaging``：``message``
- ``group:nodes``：``nodes``
- ``group:openclaw``：所有内置 OpenClaw 工具（不包含提供方插件）

## 提权：仅限执行的“在主机上运行”

提权**不会**授予额外工具；它仅影响 ``exec``。

- 若您处于沙箱中，``/elevated on``（或带 ``elevated: true`` 的 ``exec``）将在主机上执行（仍可能需审批）。
- 使用 ``/elevated full`` 可跳过当前会话的执行审批。
- 若您本就在直接运行（非沙箱），提权实质上无效果（但仍受门控限制）。
- 提权**不按技能划分作用域**，也**不覆盖**工具的允许/拒绝策略。
- ``/exec`` 与提权相互独立。它仅调整已授权发送者的每会话执行默认行为。

门控（Gates）：

- 启用开关：``tools.elevated.enabled``（以及可选的 ``agents.list[].tools.elevated.enabled``）
- 发送者白名单：``tools.elevated.allowFrom.<provider>``（以及可选的 ``agents.list[].tools.elevated.allowFrom.<provider>``）

详见 [提权模式](/tools/elevated)。

## 常见“沙箱囚禁”问题的修复方法

### “工具 X 被沙箱工具策略阻止”

修复键（任选其一）：

- 禁用沙箱：``agents.defaults.sandbox.mode=off``（或按 agent 设置 ``agents.list[].sandbox.mode=off``）
- 允许该工具在沙箱内运行：
  - 将其从 ``tools.sandbox.tools.deny``（或按 agent 设置的 ``agents.list[].tools.sandbox.tools.deny``）中移除
  - 或将其添加至 ``tools.sandbox.tools.allow``（或按 agent 设置的允许列表）

### “我以为这是主会话，为何却被沙箱化？”

在 ``"non-main"`` 模式下，群组/频道密钥**不属于主会话**。请使用主会话密钥（通过 ``sandbox explain`` 显示）或切换模式为 ``"off"``。