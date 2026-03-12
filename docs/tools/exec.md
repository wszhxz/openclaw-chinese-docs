---
summary: "Exec tool usage, stdin modes, and TTY support"
read_when:
  - Using or modifying the exec tool
  - Debugging stdin or TTY behavior
title: "Exec Tool"
---
# Exec 工具

在工作区中运行 shell 命令。通过 `process` 支持前台和后台执行。
如果 `process` 被禁止，`exec` 将同步运行并忽略 `yieldMs`/`background`。
后台会话按代理范围划分；`process` 仅能看到来自同一代理的会话。

## 参数

- `command`（必需）
- `workdir`（默认为 cwd）
- `env`（键/值覆盖）
- `yieldMs`（默认 10000）：延迟后自动转入后台
- `background`（布尔值）：立即转入后台
- `timeout`（秒，默认 1800）：到期后终止
- `pty`（布尔值）：当可用时，在伪终端中运行（TTY-only CLIs, 编码代理, 终端 UIs）
- `host` (`sandbox | gateway | node`)：执行位置
- `security` (`deny | allowlist | full`)：对 `gateway`/`node` 的强制模式
- `ask` (`off | on-miss | always`)：对 `gateway`/`node` 的批准提示
- `node` (字符串)：用于 `host=node` 的节点 ID/名称
- `elevated` (布尔值)：请求提升模式（网关主机）；只有当提升解析为 `full` 时才强制 `security=full`

注意事项：

- `host` 默认为 `sandbox`。
- 当沙箱关闭时，`elevated` 被忽略（exec 已经在主机上运行）。
- `gateway`/`node` 批准由 `~/.openclaw/exec-approvals.json` 控制。
- `node` 需要配对节点（伴侣应用或无头节点主机）。
- 如果有多个节点可用，设置 `exec.node` 或 `tools.exec.node` 以选择一个。
- 在非 Windows 主机上，当设置了 `SHELL` 时，exec 使用它；如果 `SHELL` 是 `fish`，则优先使用 `bash`（或 `sh`）从 `PATH` 中避免与 fish 不兼容的脚本，然后回退到 `SHELL` 如果两者都不存在。
- 在 Windows 主机上，exec 优先使用 PowerShell 7 (`pwsh`) 发现（Program Files, ProgramW6432, 然后 PATH），然后回退到 Windows PowerShell 5.1。
- 主机执行 (`gateway`/`node`) 拒绝 `env.PATH` 和加载器覆盖 (`LD_*`/`DYLD_*`) 以防止二进制劫持或注入代码。
- OpenClaw 在生成的命令环境中设置 `OPENCLAW_SHELL=exec`（包括 PTY 和沙箱执行），以便 shell/profile 规则可以检测 exec-tool 上下文。
- 重要：沙箱默认是**关闭**的。如果沙箱关闭且明确配置/请求了 `host=sandbox`，exec 现在将失败而不是默默地在网关主机上运行。
  启用沙箱或使用带有批准的 `host=gateway`。
- 脚本预检（针对常见的 Python/Node shell 语法错误）仅检查有效 `workdir` 边界内的文件。如果脚本路径解析到 `workdir` 外部，则跳过该文件的预检。

## 配置

- `tools.exec.notifyOnExit`（默认：true）：当为 true 时，后台 exec 会话会在退出时排队系统事件并请求心跳。
- `tools.exec.approvalRunningNoticeMs`（默认：10000）：当需要批准的 exec 运行时间超过此值时，发出单个“正在运行”通知（0 表示禁用）。
- `tools.exec.host`（默认：`sandbox`）
- `tools.exec.security`（默认：对于沙箱为 `deny`，对于未设置的网关 + 节点为 `allowlist`）
- `tools.exec.ask`（默认：`on-miss`）
- `tools.exec.node`（默认：未设置）
- `tools.exec.pathPrepend`：在 exec 运行时添加到 `PATH` 前面的目录列表（仅限网关 + 沙箱）。
- `tools.exec.safeBins`：无需显式允许列表条目即可运行的标准输入安全二进制文件。有关行为详情，请参阅 [安全二进制文件](/tools/exec-approvals#safe-bins-stdin-only)。
- `tools.exec.safeBinTrustedDirs`：额外显式的信任目录用于 `safeBins` 路径检查。`PATH` 条目永远不会自动信任。内置默认值为 `/bin` 和 `/usr/bin`。
- `tools.exec.safeBinProfiles`：每个安全二进制文件的可选自定义 argv 策略（`minPositional`, `maxPositional`, `allowedValueFlags`, `deniedFlags`）。

示例：

```json5
{
  tools: {
    exec: {
      pathPrepend: ["~/bin", "/opt/oss/bin"],
    },
  },
}
```

### PATH 处理

- `host=gateway`：将您的登录 shell `PATH` 合并到 exec 环境中。`env.PATH` 覆盖被拒绝用于主机执行。守护进程本身仍然以最小的 `PATH` 运行：
  - macOS: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `/bin`
  - Linux: `/usr/local/bin`, `/usr/bin`, `/bin`
- `host=sandbox`：在容器内运行 `sh -lc`（登录 shell），因此 `/etc/profile` 可能会重置 `PATH`。
  OpenClaw 通过内部环境变量（无 shell 插值）在配置文件源之后前置 `env.PATH`；`tools.exec.pathPrepend` 也适用于这里。
- `host=node`：您传递的非阻塞环境覆盖仅发送到节点。`env.PATH` 覆盖被拒绝用于主机执行，并被节点主机忽略。如果您需要在节点上添加额外的 PATH 条目，请配置节点主机服务环境（systemd/launchd）或将工具安装在标准位置。

每个代理的节点绑定（在配置中使用代理列表索引）：

```bash
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
```

控制 UI：Nodes 标签页包含一个小的“Exec 节点绑定”面板，用于相同的设置。

## 会话覆盖 (`/exec`)

使用 `/exec` 设置 **每个会话** 的默认值 `host`, `security`, `ask` 和 `node`。
发送没有参数的 `/exec` 以显示当前值。

示例：

```
/exec host=gateway security=allowlist ask=on-miss node=mac-1
```

## 授权模型

**授权发送者**（通道允许列表/配对加上 `commands.useAccessGroups`）才会尊重 `/exec`。
它仅更新 **会话状态** 并不写入配置。要硬性禁用 exec，请通过工具策略（`tools.deny: ["exec"]` 或每个代理）拒绝它。
除非您明确设置 `security=full` 和 `ask=off`，否则主机批准仍然适用。

## 执行批准（伴侣应用/节点主机）

沙箱代理可以在网关或节点主机上运行 `exec` 之前要求每次请求的批准。
有关策略、允许列表和 UI 流程，请参阅 [执行批准](/tools/exec-approvals)。

当需要批准时，exec 工具会立即返回 `status: "approval-pending"` 和批准 ID。一旦批准（或拒绝/超时），网关会发出系统事件（`Exec finished` / `Exec denied`）。如果命令在 `tools.exec.approvalRunningNoticeMs` 后仍在运行，则会发出单个 `Exec running` 通知。

## 允许列表 + 安全二进制文件

手动允许列表强制匹配 **已解析的二进制路径**（无基本名匹配）。当 `security=allowlist` 时，只有当每个管道段都在允许列表中或是一个安全二进制文件时，shell 命令才会自动允许。链接（`;`, `&&`, `||`）和重定向在允许列表模式下被拒绝，除非每个顶层段都满足允许列表（包括安全二进制文件）。重定向仍然不支持。

`autoAllowSkills` 是 exec 批准中的一个单独的便捷路径。它不同于手动路径允许列表条目。为了严格的显式信任，请保持 `autoAllowSkills` 禁用。

使用两个控件来完成不同的任务：

- `tools.exec.safeBins`：小型的标准输入流过滤器。
- `tools.exec.safeBinTrustedDirs`：安全二进制文件可执行路径的显式额外信任目录。
- `tools.exec.safeBinProfiles`：自定义安全二进制文件的显式 argv 策略。
- 允许列表：可执行路径的显式信任。

不要将 `safeBins` 视为通用允许列表，也不要添加解释器/运行时二进制文件（例如 `python3`, `node`, `ruby`, `bash`）。如果需要这些，请使用显式的允许列表条目并保持批准提示启用。
`openclaw security audit` 会在缺少显式配置文件的解释器/运行时 `safeBins` 条目时发出警告，而 `openclaw doctor --fix` 可以为缺失的自定义 `safeBinProfiles` 条目提供脚手架。

有关完整的策略详细信息和示例，请参阅 [执行批准](/tools/exec-approvals#safe-bins-stdin-only) 和 [安全二进制文件与允许列表](/tools/exec-approvals#safe-bins-versus-allowlist)。

## 示例

前台：

```json
{ "tool": "exec", "command": "ls -la" }
```

后台 + 轮询：

```json
{"tool":"exec","command":"npm run build","yieldMs":1000}
{"tool":"process","action":"poll","sessionId":"<id>"}
```

发送按键（tmux 风格）：

```json
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Enter"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["C-c"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Up","Up","Enter"]}
```

提交（仅发送 CR）：

```json
{ "tool": "process", "action": "submit", "sessionId": "<id>" }
```

粘贴（默认带括号）：

```json
{ "tool": "process", "action": "paste", "sessionId": "<id>", "text": "line1\nline2\n" }
```

## apply_patch（实验性）

`apply_patch` 是 `exec` 的子工具，用于结构化多文件编辑。
显式启用它：

```json5
{
  tools: {
    exec: {
      applyPatch: { enabled: true, workspaceOnly: true, allowModels: ["gpt-5.2"] },
    },
  },
}
```

注意事项：

- 仅适用于 OpenAI/OpenAI Codex 模型。
- 工具策略仍然适用；`allow: ["exec"]` 隐式允许 `apply_patch`。
- 配置位于 `tools.exec.applyPatch` 下。
- `tools.exec.applyPatch.workspaceOnly` 默认为 `true`（工作区包含）。仅当您有意让 `apply_patch` 写入/删除工作区目录外的内容时，将其设置为 `false`。