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

- `command` (必需)
- `yieldMs` (默认 10000): 超过此延迟后自动后台运行
- `background` (布尔值): 立即后台运行
- `timeout` (秒，默认 1800): 超时后终止进程
- `elevated` (布尔值): 如果启用了提升模式，则在主机上运行
- 需要真实的 TTY？设置 `pty: true`。
- `workdir`, `env`

行为：

- 前台运行直接返回输出。
- 当后台运行（显式或超时），工具返回 `status: "running"` + `sessionId` 和一个简短的尾部。
- 输出保留在内存中，直到会话被轮询或清除。
- 如果 `process` 工具被禁止，`exec` 同步运行并忽略 `yieldMs`/`background`。

## 子进程桥接

当在 exec/process 工具之外生成长时间运行的子进程（例如，CLI 重启或网关辅助程序），附加子进程桥接辅助程序以转发终止信号并在退出/错误时分离监听器。这可以避免 systemd 上的孤立进程，并使跨平台的关闭行为一致。

环境覆盖：

- `PI_BASH_YIELD_MS`: 默认让步 (毫秒)
- `PI_BASH_MAX_OUTPUT_CHARS`: 内存输出上限 (字符)
- `OPENCLAW_BASH_PENDING_MAX_OUTPUT_CHARS`: 每个流的待处理 stdout/stderr 上限 (字符)
- `PI_BASH_JOB_TTL_MS`: 完成会话的 TTL (毫秒，限制在 1 分钟至 3 小时)

配置（首选）：

- `tools.exec.backgroundMs` (默认 10000)
- `tools.exec.timeoutSec` (默认 1800)
- `tools.exec.cleanupMs` (默认 1800000)
- `tools.exec.notifyOnExit` (默认 true): 当后台 exec 退出时，排队系统事件 + 请求心跳。

## process 工具

操作：

- `list`: 正在运行 + 完成的会话
- `poll`: 为会话排干新输出（也报告退出状态）
- `log`: 读取聚合输出（支持 `offset` + `limit`)
- `write`: 发送 stdin (`data`, 可选 `eof`)
- `kill`: 终止后台会话
- `clear`: 从内存中移除完成的会话
- `remove`: 如果正在运行则终止，否则如果已完成则清除

注意事项：

- 仅后台会话会被列出/保留在内存中。
- 进程重启时会话会丢失（没有磁盘持久性）。
- 会话日志仅在运行 `process poll/log` 并记录工具结果时保存到聊天历史中。
- `process` 按代理范围；它只看到该代理启动的会话。
- `process list` 包含派生的 `name`（命令动词 + 目标）用于快速扫描。
- `process log` 使用基于行的 `offset`/`limit`（省略 `offset` 以获取最后 N 行）。

## 示例

运行长时间任务并在稍后轮询：

```json
{ "tool": "exec", "command": "sleep 5 && echo done", "yieldMs": 1000 }
```

```json
{ "tool": "process", "action": "poll", "sessionId": "<id>" }
```

立即开始后台运行：

```json
{ "tool": "exec", "command": "npm run build", "background": true }
```

发送 stdin：

```json
{ "tool": "process", "action": "write", "sessionId": "<id>", "data": "y\n" }
```