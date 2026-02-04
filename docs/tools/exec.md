---
summary: "Exec tool usage, stdin modes, and TTY support"
read_when:
  - Using or modifying the exec tool
  - Debugging stdin or TTY behavior
title: "Exec Tool"
---
# 执行工具

在工作区中运行shell命令。支持通过`process`进行前台和后台执行。
如果`process`被禁止，`exec`将同步运行并忽略`yieldMs`/`background`。
后台会话按代理划分；`process`仅能看到同一代理的会话。

## 参数

- `command` (必需)
- `workdir` (默认为当前工作目录)
- `env` (键/值覆盖)
- `yieldMs` (默认10000): 延迟后自动后台执行
- `background` (布尔值): 立即后台执行
- `timeout` (秒，默认1800): 到期后终止
- `pty` (布尔值): 当可用时在伪终端中运行 (仅限TTY的CLI、编码代理、终端UI)
- `host` (`sandbox | gateway | node`): 执行位置
- `security` (`deny | allowlist | full`): 对于`gateway`/`node`的强制模式
- `ask` (`off | on-miss | always`): 对于`gateway`/`node`的审批提示
- `node` (字符串): `host=node`的节点ID/名称
- `elevated` (布尔值): 请求提升模式 (网关主机); 只有当`security=full`解析为`full`时才强制执行

注意事项：

- `host`默认为`sandbox`。
- 当沙箱关闭时，忽略`elevated` (exec已经在主机上运行)。
- `gateway`/`node`审批由`~/.openclaw/exec-approvals.json`控制。
- `node`需要配对节点 (配套应用或无头节点主机)。
- 如果有多个节点可用，请设置`exec.node`或`tools.exec.node`以选择一个。
- 在非Windows主机上，如果设置了`SHELL`，exec使用`SHELL`; 如果`SHELL`是`fish`，它优先使用`bash` (或`sh`)
  从`PATH`以避免与fish不兼容的脚本，然后如果两者都不存在则回退到`SHELL`。
- 主机执行 (`gateway`/`node`) 拒绝`env.PATH`和加载器覆盖 (`LD_*`/`DYLD_*`) 以
  防止二进制劫持或注入代码。
- 重要：沙箱默认是**关闭**的。如果沙箱关闭，`host=sandbox`直接在
  网关主机上运行 (无容器) 并且**不需要审批**。要要求审批，请使用
  `host=gateway`并配置exec审批 (或启用沙箱)。

## 配置

- `tools.exec.notifyOnExit` (默认: true): 当为true时，后台化的exec会话会在退出时排队系统事件并请求心跳。
- `tools.exec.approvalRunningNoticeMs` (默认: 10000): 当审批门控的exec运行时间超过此值时发出单个“正在运行”的通知 (0禁用)。
- `tools.exec.host` (默认: `sandbox`)
- `tools.exec.security` (默认: 沙箱时为`deny`，网关+节点时为`allowlist`，未设置时)
- `tools.exec.ask` (默认: `on-miss`)
- `tools.exec.node` (默认: 未设置)
- `tools.exec.pathPrepend`: 要附加到`PATH`的目录列表以供exec运行。
- `tools.exec.safeBins`: 仅stdin安全的二进制文件，可以在没有显式白名单条目的情况下运行。

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

- `host=gateway`: 将您的登录shell `PATH` 合并到exec环境中。`env.PATH` 覆盖
  被主机执行拒绝。守护进程本身仍然使用最小的 `PATH`:
  - macOS: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `/bin`
  - Linux: `/usr/local/bin`, `/usr/bin`, `/bin`
- `host=sandbox`: 在容器内运行 `sh -lc` (登录shell)，因此 `/etc/profile` 可能重置 `PATH`。
  OpenClaw通过内部环境变量在加载配置文件后附加 `env.PATH` (无shell插值);
  `tools.exec.pathPrepend` 也适用于此。
- `host=node`: 只有您传递的非阻止的env覆盖会被发送到节点。`env.PATH` 覆盖
  被主机执行拒绝。无头节点主机仅接受 `PATH` 当它附加节点主机
  PATH (无替换)。macOS节点完全丢弃 `PATH` 覆盖。

每个代理节点绑定 (在配置中使用代理列表索引):

```bash
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
```

控制UI: 节点选项卡包含一个小的“Exec节点绑定”面板用于相同设置。

## 会话覆盖 (`/exec`)

使用 `/exec` 设置 **每个会话** 的默认值 `host`, `security`, `ask`, 和 `node`。
发送 `/exec` 不带参数以显示当前值。

示例：

```
/exec host=gateway security=allowlist ask=on-miss node=mac-1
```

## 授权模型

`/exec` 仅适用于 **授权发送者** (通道白名单/配对加上 `commands.useAccessGroups`)。
它仅更新 **会话状态** 并不写入配置。要硬禁用exec，请通过工具
策略 (`tools.deny: ["exec"]` 或每个代理) 拒绝它。除非您明确设置
`security=full` 和 `ask=off`，否则主机审批仍然适用。

## Exec审批 (配套应用 / 节点主机)

沙盒代理可以在`exec`在网关或节点主机上运行之前要求每个请求的审批。
有关策略、白名单和UI流程，请参阅 [Exec审批](/tools/exec-approvals)。

当需要审批时，exec工具立即返回
`status: "approval-pending"` 和一个审批ID。一旦被批准（或拒绝/超时），
网关发出系统事件 (`Exec finished` / `Exec denied`)。如果命令仍在
运行超过 `tools.exec.approvalRunningNoticeMs`，发出单个 `Exec running` 通知。

## 白名单 + 安全二进制文件

白名单强制匹配 **解析后的二进制路径** 仅 (无basename匹配)。当
`security=allowlist`，shell命令只有在每个管道段都被
白名单或安全二进制文件允许时才会自动允许。链式 (`;`, `&&`, `||`) 和重定向在
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

发送按键 (tmux风格)：

```json
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Enter"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["C-c"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Up","Up","Enter"]}
```

提交 (仅发送CR)：

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

- 仅适用于OpenAI/OpenAI Codex模型。
- 工具策略仍然适用；`allow: ["exec"]` 隐式允许 `apply_patch`。
- 配置位于 `tools.exec.applyPatch` 下。