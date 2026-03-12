---
summary: "Background exec execution and process management"
read_when:
  - Adding or modifying background exec behavior
  - Debugging long-running exec tasks
title: "Background Exec and Process Tool"
---
# 后台执行 + 进程管理工具

OpenClaw 通过 `exec` 工具运行 shell 命令，并将长时间运行的任务保留在内存中。`process` 工具用于管理这些后台会话。

## exec 工具

关键参数：

- `command`（必需）
- `yieldMs`（默认值为 10000）：延迟至此毫秒数后自动转入后台
- `background`（布尔值）：立即转入后台
- `timeout`（单位：秒，默认值为 1800）：超时后终止该进程
- `elevated`（布尔值）：若启用/允许提权模式，则在宿主机上运行
- 需要真实的 TTY？请设置 `pty: true`。
- `workdir`、`env`

行为说明：

- 前台运行直接返回输出。
- 当转入后台（显式触发或超时触发）时，该工具返回 `status: "running"` + `sessionId` 及一段简短的尾部输出。
- 输出内容保留在内存中，直至该会话被轮询或清除。
- 若 `process` 工具被禁用，则 `exec` 将以同步方式运行，并忽略 `yieldMs`/`background`。
- 派生出的 exec 命令将接收 `OPENCLAW_SHELL=exec`，以支持上下文感知的 shell/profile 规则。

## 子进程桥接

当在 exec/process 工具之外启动长时间运行的子进程时（例如 CLI 自重启或网关辅助程序），请附加子进程桥接助手（child-process bridge helper），以便在退出或出错时转发终止信号并分离监听器。此举可避免 systemd 下出现孤儿进程，并确保各平台关机行为的一致性。

环境变量覆盖项：

- `PI_BASH_YIELD_MS`：默认 yield 时间（毫秒）
- `PI_BASH_MAX_OUTPUT_CHARS`：内存中输出容量上限（字符数）
- `OPENCLAW_BASH_PENDING_MAX_OUTPUT_CHARS`：每个 stdout/stderr 流待处理容量上限（字符数）
- `PI_BASH_JOB_TTL_MS`：已完成会话的生存时间（毫秒，限定范围为 1 分钟至 3 小时）

配置项（推荐方式）：

- `tools.exec.backgroundMs`（默认值为 10000）
- `tools.exec.timeoutSec`（默认值为 1800）
- `tools.exec.cleanupMs`（默认值为 1800000）
- `tools.exec.notifyOnExit`（默认值为 true）：当后台 exec 退出时，入队一个系统事件并请求心跳。
- `tools.exec.notifyOnExitEmptySuccess`（默认值为 false）：设为 true 时，还会为成功完成但未产生任何输出的后台运行任务入队完成事件。

## process 工具

支持的操作：

- `list`：列出正在运行及已结束的会话
- `poll`：拉取某一会话的新输出（同时报告退出状态）
- `log`：读取聚合后的输出（支持 `offset` + `limit`）
- `write`：向进程发送标准输入（`data`，可选 `eof`）
- `kill`：终止一个后台会话
- `clear`：从内存中移除一个已完成的会话
- `remove`：若正在运行则终止；否则若已结束则清除

注意事项：

- 仅后台会话会被列出并驻留于内存中。
- 进程重启后所有会话将丢失（无磁盘持久化）。
- 会话日志仅在您运行 `process poll/log` 且工具结果被记录时，才会保存至聊天历史中。
- `process` 按代理（agent）作用域隔离；它仅显示由该代理启动的会话。
- `process list` 包含一个派生字段 `name`（命令动词 + 目标），便于快速扫描。
- `process log` 使用基于行的 `offset`/`limit`。
- 当同时省略 `offset` 和 `limit` 时，返回最后 200 行，并附带分页提示。
- 当提供 `offset` 但省略 `limit` 时，返回从 `offset` 至末尾的内容（不截断为 200 行）。

## 示例

运行一个长时间任务，并稍后轮询：

```json
{ "tool": "exec", "command": "sleep 5 && echo done", "yieldMs": 1000 }
```

```json
{ "tool": "process", "action": "poll", "sessionId": "<id>" }
```

立即以后台方式启动：

```json
{ "tool": "exec", "command": "npm run build", "background": true }
```

发送标准输入：

```json
{ "tool": "process", "action": "write", "sessionId": "<id>", "data": "y\n" }
```