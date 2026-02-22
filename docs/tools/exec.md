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
后台会话按代理划分；`process` 仅能看到同一代理的会话。

## 参数

- `command` (必需)
- `workdir` (默认为 cwd)
- `env` (键/值覆盖)
- `yieldMs` (默认 10000): 延迟后自动后台执行
- `background` (布尔值): 立即后台执行
- `timeout` (秒，默认 1800): 到期后终止
- `pty` (布尔值): 当可用时在伪终端中运行 (仅限 TTY 的 CLI，编码代理，终端 UI)
- `host` (`sandbox | gateway | node`): 执行位置
- `security` (`deny | allowlist | full`): 对于 `gateway`/`node` 的强制模式
- `ask` (`off | on-miss | always`): 对于 `gateway`/`node` 的审批提示
- `node` (字符串): `host=node` 的节点 ID/名称
- `elevated` (布尔值): 请求提升模式 (网关主机)；只有当提升解析为 `full` 时才强制 `security=full`

注意：

- `host` 默认为 `sandbox`。
- 当沙盒关闭时 (`elevated` 被忽略) (exec 已经在主机上运行)。
- `gateway`/`node` 审批由 `~/.openclaw/exec-approvals.json` 控制。
- `node` 需要配对节点 (伴侣应用或无头节点主机)。
- 如果有多个节点可用，请设置 `exec.node` 或 `tools.exec.node` 以选择一个。
- 在非 Windows 主机上，exec 使用 `SHELL`（如果已设置）；如果 `SHELL` 是 `fish`，它优先使用 `bash` (或 `sh`)
  从 `PATH` 以避免与 fish 不兼容的脚本，然后在两者都不存在时回退到 `SHELL`。
- 主机执行 (`gateway`/`node`) 拒绝 `env.PATH` 和加载器覆盖 (`LD_*`/`DYLD_*`) 以
  防止二进制劫持或注入代码。
- 重要：沙盒默认是 **关闭** 的。如果沙盒关闭，`host=sandbox` 直接在
  网关主机上运行 (无容器) 并且 **不需要审批**。要需要审批，请使用
  `host=gateway` 并配置 exec 审批 (或启用沙盒)。
- 脚本预检检查（针对常见的 Python/Node shell 语法错误）仅检查有效
  `workdir` 边界内的文件。如果脚本路径解析到 `workdir` 之外，预检将跳过
  该文件。

## 配置

- `tools.exec.notifyOnExit` (默认: true): 当为真时，后台化的 exec 会话会在退出时排队系统事件并请求心跳。
- `tools.exec.approvalRunningNoticeMs` (默认: 10000): 当审批门控的 exec 运行时间超过此时间时发出单个“正在运行”通知（0 表示禁用）。
- `tools.exec.host` (默认: `sandbox`)
- `tools.exec.security` (默认: 沙盒时为 `deny`，网关 + 节点未设置时为 `allowlist`)
- `tools.exec.ask` (默认: `on-miss`)
- `tools.exec.node` (默认: 未设置)
- `tools.exec.pathPrepend`: 要附加到 `PATH` 的目录列表用于 exec 运行（仅限网关 + 沙盒）。
- `tools.exec.safeBins`: 可以在没有显式白名单条目的情况下运行的仅 stdin 安全二进制文件。有关行为详情，请参阅 [安全二进制文件](/tools/exec-approvals#safe-bins-stdin-only)。

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

- `host=gateway`: 将您的登录 shell `PATH` 合并到 exec 环境中。`env.PATH` 覆盖
  被主机执行拒绝。守护进程本身仍然使用最小的 `PATH` 运行：
  - macOS: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `/bin`
  - Linux: `/usr/local/bin`, `/usr/bin`, `/bin`
- `host=sandbox`: 在容器内运行 `sh -lc` (登录 shell)，因此 `/etc/profile` 可能重置 `PATH`。
  OpenClaw 通过内部环境变量在配置文件加载后附加 `env.PATH`（无 shell 插值）；
  `tools.exec.pathPrepend` 也适用于此。
- `host=node`: 仅发送您传递的非阻止环境覆盖到节点。`env.PATH` 覆盖
  被主机执行拒绝并且被节点主机忽略。如果您需要节点上的其他 PATH 条目，
  配置节点主机服务环境（systemd/launchd）或在标准位置安装工具。

每个代理的节点绑定（在配置中使用代理列表索引）：

```bash
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
```

控制界面：节点选项卡包括一个小的“Exec 节点绑定”面板用于相同设置。

## 会话覆盖 (`/exec`)

使用 `/exec` 设置 `host`, `security`, `ask`, 和 `node` 的 **每会话** 默认值。
发送不带参数的 `/exec` 以显示当前值。

示例：

```
/exec host=gateway security=allowlist ask=on-miss node=mac-1
```

## 授权模型

`/exec` 仅适用于 **授权发送者** (通道白名单/配对加上 `commands.useAccessGroups`)。
它仅更新 **会话状态** 并不写入配置。要硬禁用 exec，请通过工具
策略 (`tools.deny: ["exec"]` 或每个代理) 拒绝它。除非您明确设置
`security=full` 和 `ask=off`，否则主机审批仍然适用。

## Exec 审批 (伴侣应用 / 节点主机)

沙盒代理可以在 `exec` 在网关或节点主机上运行之前要求每个请求的审批。
请参阅 [Exec 审批](/tools/exec-approvals) 了解策略、白名单和用户界面流程。

当需要审批时，exec 工具会立即返回
`status: "approval-pending"` 和一个审批 ID。一旦被批准（或拒绝/超时），
网关会发出系统事件 (`Exec finished` / `Exec denied`)。如果命令仍在
运行超过 `tools.exec.approvalRunningNoticeMs`，会发出单个 `Exec running` 通知。

## 白名单 + 安全二进制文件

白名单强制执行仅匹配 **解析后的二进制路径**（无基名匹配）。当
`security=allowlist`，shell 命令仅在每个管道段都被
白名单或安全二进制文件允许时自动允许。链式操作 (`;`, `&&`, `||`) 和重定向在
白名单模式下被拒绝，除非每个顶级段满足白名单（包括安全二进制文件）。
重定向仍然不受支持。

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

粘贴（默认用方括号括起来）：

```json
{ "tool": "process", "action": "paste", "sessionId": "<id>", "text": "line1\nline2\n" }
```

## apply_patch (实验性)

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

注意：

- 仅适用于 OpenAI/OpenAI Codex 模型。
- 工具策略仍然适用；`allow: ["exec"]` 隐式允许 `apply_patch`。
- 配置位于 `tools.exec.applyPatch` 下。
- `tools.exec.applyPatch.workspaceOnly` 默认为 `true` (工作区包含)。仅当您有意让 `apply_patch` 写入/删除工作区目录之外的内容时才将其设置为 `false`。