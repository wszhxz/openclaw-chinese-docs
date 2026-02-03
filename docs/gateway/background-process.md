---
summary: "Background exec execution and process management"
read_when:
  - Adding or modifying background exec behavior
  - Debugging long-running exec tasks
title: "Background Exec and Process Tool"
---
# 背景执行 + 进程工具

OpenClaw 通过 `exec` 工具运行 shell 命令，并将长时间运行的任务保留在内存中。`process` 工具管理这些后台会话。

## exec 工具

关键参数：

- `command`（必填）
- `yieldMs`（默认 10000）：在此延迟后自动进入后台
- `background`（布尔值）：立即进入后台
- `timeout`（秒，默认 1800）：在此超时后终止进程
- `elevated`（布尔值）：如果启用了/允许了提升权限模式，则在主机上运行
- 需要真正的 TTY？设置 `pty: true`。
- `workdir`，`env`

行为：

- 前台运行会直接返回输出。
- 当进入后台（显式或超时触发），工具返回 `status: "running"` + `sessionId` 和简短的尾部输出。
- 输出会保留在内存中，直到会话被轮询或清除。
- 如果禁用了 `process` 工具，`exec` 会同步运行并忽略 `yieldMs`/`background`。

## 子进程桥接

当在 exec/process 工具之外启动长时间运行的子进程（例如 CLI 重启或网关辅助程序），请附加子进程桥接辅助程序，以便终止信号被转发，并在退出/错误时断开监听器。这可以避免 systemd 中的孤儿进程，并确保跨平台的关闭行为一致。

环境覆盖：

- `PI_BASH_YIELD_MS`：默认 yield（毫秒）
- `PI_BASH_MAX_OUTPUT_CHARS`：内存中输出上限（字符）
- `OPENCLAW_BASH_PENDING_MAX_OUTPUT_CHARS`：每个流的待处理 stdout/stderr 上限（字符）
- `PI_BASH_JOB_TTL_MS`：已完成会话的 TTL（毫秒，限制在 1 分钟至 3 小时之间）

配置（推荐）：

- `tools.exec.backgroundMs`（默认 10000）
- `tools.exec.timeoutSec`（默认 1800）
- `tools.exec.cleanupMs`（默认 1800000）
- `tools.exec.notifyOnExit`（默认 true）：当后台执行退出时，入队系统事件并请求心跳。

## process 工具

操作：

- `list`：运行中的 + 已完成的会话
- `poll`：为会话获取新输出（同时报告退出状态）
- `log`：读取聚合输出（支持 `offset` + `limit`）
- `write`：发送 stdin（`data`，可选 `eof`）
- `kill`：终止后台会话
- `clear`：从内存中移除已完成的会话
- `remove`：如果正在运行则终止，否则如果已完成则清除

注意事项：

- 仅列出/持久化内存中的后台会话。
- 会话在进程重启时丢失（无磁盘持久化）。
- 会话日志仅在运行 `process poll/log` 并且工具结果被记录时保存到聊天历史中。
- `process` 按代理作用域；它仅能看到由该代理启动的会话。
- `process list` 包含一个派生的 `name`（命令动词 + 目标）以便快速扫描。
- `process log` 使用基于行的 `offset`/`limit`（省略 `offset` 以获取最后 N 行）。

## 示例

运行一个长时间任务并在之后轮询：

```json
{ "tool": "exec", "command": "sleep 5 && echo done", "yieldMs": 1000 }
```

```json
{ "tool": "process", "action": "poll", "sessionId": "<id>" }
```

立即在后台启动：

```json
{ "tool": "exec", "command": "npm run build", "background": true }
```

发送 stdin：

```json
{ "tool": "process", "action": "write", "sessionId": "<id>", "data": "y\n" }
```