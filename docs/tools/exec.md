---
summary: "Exec tool usage, stdin modes, and TTY support"
read_when:
  - Using or modifying the exec tool
  - Debugging stdin or TTY behavior
title: "Exec Tool"
---
# 执行工具

在工作区中运行 shell 命令。支持通过 `process` 实现前台 + 后台执行。如果 `process` 被禁用，`exec` 会同步运行并忽略 `yieldMs`/`background`。后台会话按代理进行作用域划分；`process` 仅能看到来自同一代理的会话。

## 参数

- `command`（必需）
- `workdir`（默认为当前目录）
- `env`（键/值覆盖）
- `yieldMs`（默认 10000）：延迟后自动进入后台
- `background`（布尔值）：立即进入后台
- `timeout`（秒，默认 1800）：超时后终止
- `pty`（布尔值）：在可用时以伪终端运行（仅 TTY CLI、编码代理、终端 UI）
- `host`（`sandbox` | `gateway` | `node`）：执行位置
- `security`（`deny` | `allowlist` | `full`）：`gateway`/`node` 的执行模式
- `ask`（`off` | `on-miss` | `always`）：`gateway`/`node` 的审批提示
- `node`（字符串）：`host=node` 时的节点 ID/名称
- `elevated`（布尔值）：请求提升模式（网关主机）；`security=full` 仅在 elevated 解析为 `full` 时强制

说明：

- `host` 默认为 `sandbox`。
- 当禁用沙箱时，`elevated` 被忽略（exec 已在主机上运行）。
- `gateway`/`node` 的审批由 `~/.openclaw/exec-approvals.json` 控制。
- `node` 需要配对的节点（配套应用或无头节点主机）。
- 若有多个节点可用，通过设置 `exec.node` 或 `tools.exec.node` 选择一个。
- 在非 Windows 主机上，exec 会使用 `SHELL`（若设置）；若 `SHELL` 为 `fish`，则优先使用 `bash`（或 `sh`）从 `PATH` 避免 fish 不兼容脚本，若两者都不存在则回退到 `SHELL`。
- 主机执行（`gateway`/`node`）拒绝 `env.PATH` 和加载器覆盖（`LD_*`/`DYLD_*`）以防止二进制劫持或注入代码。
- 重要：沙箱默认是**关闭的**。若沙箱关闭，`host=sandbox` 会直接在网关主机上运行（无容器）且**无需审批**。若需要审批，使用 `host=gateway` 并配置 exec 审批（或启用沙箱）。

## 配置

- `tools.exec.notifyOnExit`（默认：true）：当为 true 时，后台执行会话会在退出时排队系统事件并请求心跳。
- `tools.exec.approvalRunningNoticeMs`（默认：10000）：当审批门控的执行运行时间超过此值时，发出一次“正在运行”通知（0 禁用）。
- `tools.exec.host`（默认：`sandbox`）
- `tools.exec.security`（沙箱默认为 `deny`，网关 + 节点默认为 `allowlist`）
- `tools.exec.ask`（默认：`on-miss`）
- `tools.exec.node`（默认：未设置）
- `tools.exec.pathPrepend`：添加到 `PATH` 的目录列表。
- `tools.exec.safeBins`：仅 stdin 安全二进制文件，可无需显式白名单条目运行。

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

- `host=gateway`：将你的登录 shell `PATH` 合并到执行环境。主机执行时 `env.PATH` 覆盖被拒绝。守护进程本身仍使用最小的 `PATH`：
  - macOS：`/opt/homebrew/bin`、`/usr/local/bin`、`/usr/bin`、`/bin`
  - Linux：`/usr/local/bin`、`/usr/bin`、`/bin`
- `host=sandbox`：在容器内运行 `sh -lc`（登录 shell），因此 `/etc/profile` 可能重置 `PATH`。OpenClaw 通过内部环境变量在加载配置文件后优先 `env.PATH`（无 shell 插值）；`tools.exec.pathPrepend` 也适用于此处。
- `host=node`：仅非被阻止的环境覆盖会被发送到节点。主机执行时 `env.PATH` 覆盖被拒绝。无头节点主机仅在 `PATH` 前缀节点主机 `PATH` 时接受 `PATH`（无替换）。macOS 节点完全丢弃 `PATH` 覆盖。

按代理绑定节点（在配置中使用代理列表索引）：

```bash
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
```

控制 UI：节点标签包含一个小型“执行节点绑定”面板用于相同设置。

## 会话覆盖（`/exec`）

使用 `/exec` 设置 **每会话** 的默认 `host`、`security`、`ask` 和 `node`。发送 `/exec` 无参数显示当前值。

示例：

```
/exec host=gateway security=allowlist ask=on-miss node=mac-1
```

## 授权模型

`/exec` 仅对 **授权发送者**（通道