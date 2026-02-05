---
summary: "Exec tool usage, stdin modes, and TTY support"
read_when:
  - Using or modifying the exec tool
  - Debugging stdin or TTY behavior
title: "Exec Tool"
---
# Exec 工具

在工作区中运行 shell 命令。支持通过 `process` 进行前台和后台执行。
如果 `process` 被禁止，`exec` 将同步运行并忽略 `yieldMs`/`background`。
后台会话按代理范围划分；`process` 仅能看到同一代理的会话。

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
- `ask` (`off | on-miss | always`): 对于 `gateway`/`node` 的批准提示
- `node` (字符串): `host=node` 的节点 ID/名称
- `elevated` (布尔值): 请求提升模式 (网关主机)；仅当 `security=full` 解析为 `full` 时强制

注意事项：

- `host` 默认为 `sandbox`。
- 当沙箱关闭时，忽略 `elevated` (exec 已经在主机上运行)。
- `gateway`/`node` 的批准由 `~/.openclaw/exec-approvals.json` 控制。
- `node` 需要配对节点 (配套应用或无头节点主机)。
- 如果有多个节点可用，请设置 `exec.node` 或 `tools.exec.node` 以选择一个。
- 在非 Windows 主机上，如果设置了 `SHELL`，exec 使用 `SHELL`；如果 `SHELL` 是 `fish`，它优先使用 `bash` (或 `sh`)
  从 `PATH` 以避免不兼容 fish 的脚本，然后在两者都不存在时回退到 `SHELL`。
- 主机执行 (`gateway`/`node`) 拒绝 `env.PATH` 和加载器覆盖 (`LD_*`/`DYLD_*`) 以
  防止二进制劫持或注入代码。
- 重要：默认情况下，沙箱是 **关闭** 的。如果沙箱关闭，`host=sandbox` 直接在
  网关主机 (无容器) 上运行并且 **不需要批准**。要需要批准，请使用
  `host=gateway` 并配置 exec 批准 (或启用沙箱)。

## 配置

- `tools.exec.notifyOnExit` (默认: true): 当为真时，后台化的 exec 会话会在退出时排队系统事件并请求心跳。
- `tools.exec.approvalRunningNoticeMs` (默认: 10000): 当审批门控的 exec 运行时间超过此时间时发出单个“正在运行”通知 (0 禁用)。
- `tools.exec.host` (默认: `sandbox`)
- `tools.exec.security` (默认: 沙箱时为 `deny`，网关 + 节点时未设置为 `allowlist`)
- `tools.exec.ask` (默认: `on-miss`)
- `tools.exec.node` (默认: 未设置)
- `tools.exec.pathPrepend`: 要前置到 `PATH` 的目录列表用于 exec 运行。
- `tools.exec.safeBins`: 仅 stdin 安全的二进制文件可以在没有显式白名单条目的情况下运行。

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
  被主机执行拒绝。守护进程本身仍然使用最小的 `PATH`:
  - macOS: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `/bin`
  - Linux: `/usr/local/bin`, `/usr/bin`, `/bin`
- `host=sandbox`: 在容器内运行 `sh -lc` (登录 shell)，因此 `/etc/profile` 可能重置 `PATH`。
  OpenClaw 通过内部环境变量在配置文件加载后前置 `env.PATH` (无 shell 插值)；
  `tools.exec.pathPrepend` 也适用于此。
- `host=node`: 仅发送您传递的非阻止 env 覆盖到节点。`env.PATH` 覆盖
  被主机执行拒绝。无头节点主机仅接受 `PATH` 当它前置节点主机
  PATH (无替换)。macOS 节点完全丢弃 `PATH` 覆盖。

每个代理的节点绑定 (在配置中使用代理列表索引)：

```bash
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
```

控制界面: 节点选项卡包含一个小的“Exec 节点绑定”面板用于相同设置。

## 会话覆盖 (`/exec`)

使用 `/exec` 设置 `host`, `security`, `ask`, 和 `node` 的 **每个会话** 默认值。
发送 `/exec` 不带参数以显示当前值。

示例：

```
/exec host=gateway security=allowlist ask=on-miss node=mac-1
```

## 授权模型

`/exec` 仅被 **授权发送者** (通道白名单/配对加上 `commands.useAccessGroups`) 荣誉。
它仅更新 **会话状态** 并不写入配置。要硬禁用 exec，请通过工具
策略 (`tools.deny: ["exec"]` 或每个代理) 拒绝它。除非您明确设置
`security=full` 和 `ask=off`，否则主机批准仍然适用。

## Exec 批准 (配套应用 / 节点主机)

沙盒代理可以在 `exec` 在网关或节点主机上运行之前要求每个请求的批准。
参见 [Exec 批准](/tools/exec-approvals) 了解策略、白名单和 UI 流程。

当需要批准时，exec 工具立即返回
`status: "approval-pending"` 和一个批准 ID。一旦批准 (或拒绝 / 超时)，
网关发出系统事件 (`Exec finished` / `Exec denied`)。如果命令仍在
运行超过 `tools.exec.approvalRunningNoticeMs`，发出单个 `Exec running` 通知。

## 白名单 + 安全二进制文件

白名单强制匹配 **解析后的二进制路径** 仅 (无基名匹配)。当
`security=allowlist`，shell 命令仅在每个管道段都是
白名单或安全二进制文件时自动允许。链式 (`;`, `&&`, `||`) 和重定向在
白名单模式下被拒绝。

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

发送按键 (tmux 风格)：

```json
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Enter"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["C-c"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Up","Up","Enter"]}
```

提交 (仅发送 CR)：

```json
{ "tool": "process", "action": "submit", "sessionId": "<id>" }
```

粘贴 (默认用方括号括起来)：

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
      applyPatch: { enabled: true, allowModels: ["gpt-5.2"] },
    },
  },
}
```

注意事项：

- 仅适用于 OpenAI/OpenAI Codex 模型。
- 工具策略仍然适用；`allow: ["exec"]` 隐式允许 `apply_patch`。
- 配置位于 `tools.exec.applyPatch` 下。