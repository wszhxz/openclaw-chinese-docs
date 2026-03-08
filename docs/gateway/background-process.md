---
summary: "Background exec execution and process management"
read_when:
  - Adding or modifying background exec behavior
  - Debugging long-running exec tasks
title: "Background Exec and Process Tool"
---
# 后台 Exec + Process 工具

OpenClaw 通过 `exec` 工具运行 shell 命令，并将长时间运行的任务保留在内存中。`process` 工具管理这些后台会话。

## exec 工具

关键参数：

- `command`（必需）
- `yieldMs`（默认 10000）：超过此延迟后自动转入后台
- `background`（bool）：立即转入后台
- `timeout`（秒，默认 1800）：超时后终止进程
- `elevated`（bool）：如果启用了/允许提升模式，则在主机上运行
- 需要真实的 TTY？设置 `pty: true`。
- `workdir`，`env`

行为：

- 前台运行直接返回输出。
- 当转入后台时（显式或超时），工具返回 `status: "running"` + `sessionId` 以及简短的尾部输出。
- 输出保留在内存中，直到会话被轮询或清除。
- 如果 `process` 工具被禁止，`exec` 将同步运行并忽略 `yieldMs`/`background`。
- 生成的 exec 命令接收 `OPENCLAW_SHELL=exec` 以用于上下文感知的 shell/profile 规则。

## 子进程桥接

当在 exec/process 工具之外生成长时间运行的子进程时（例如，CLI 重新生成或网关助手），附加子进程桥接助手，以便终止信号被转发，并且在退出/错误时分离监听器。这避免了 systemd 上的孤儿进程，并保持跨平台关闭行为的一致性。

环境变量覆盖：

- `PI_BASH_YIELD_MS`：默认 yield（ms）
- `PI_BASH_MAX_OUTPUT_CHARS`：内存输出上限（chars）
- `OPENCLAW_BASH_PENDING_MAX_OUTPUT_CHARS`：每个流待处理的 stdout/stderr 上限（chars）
- `PI_BASH_JOB_TTL_MS`：已完成会话的 TTL（ms，限制在 1m–3h）

配置（首选）：

- `tools.exec.backgroundMs`（默认 10000）
- `tools.exec.timeoutSec`（默认 1800）
- `tools.exec.cleanupMs`（默认 1800000）
- `tools.exec.notifyOnExit`（默认 true）：当后台 exec 退出时，入队一个系统事件 + 请求心跳。
- `tools.exec.notifyOnExitEmptySuccess`（默认 false）：当为 true 时，也为产生无输出的成功后台运行入队完成事件。

## process 工具

操作：

- `list`：运行中 + 已完成的会话
- `poll`：排出会话的新输出（也报告退出状态）
- `log`：读取聚合输出（支持 `offset` + `limit`）
- `write`：发送 stdin（`data`，可选 `eof`）
- `kill`：终止后台会话
- `clear`：从内存中移除已完成的会话
- `remove`：如果运行中则终止，否则如果已完成则清除

注意：

- 只有后台会话会被列出/持久化在内存中。
- 进程重启后会话丢失（无磁盘持久化）。
- 只有当你运行 `process poll/log` 且工具结果被记录时，会话日志才会保存到聊天历史中。
- `process` 按 agent 范围限定；它只能看到由该 agent 启动的会话。
- `process list` 包含一个派生的 `name`（命令动词 + 目标）用于快速扫描。
- `process log` 使用基于行的 `offset`/`limit`。
- 当 `offset` 和 `limit` 都被省略时，它返回最后 200 行并包含分页提示。
- 当提供了 `offset` 且省略了 `limit` 时，它返回从 `offset` 到结尾的内容（不限制为 200）。

## 示例

运行长时间任务并稍后轮询：

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