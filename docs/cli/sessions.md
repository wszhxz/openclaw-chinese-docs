---
summary: "CLI reference for `openclaw sessions` (list stored sessions + usage)"
read_when:
  - You want to list stored sessions and see recent activity
title: "sessions"
---
# `openclaw sessions`

列出已存储的对话会话。

```bash
openclaw sessions
openclaw sessions --agent work
openclaw sessions --all-agents
openclaw sessions --active 120
openclaw sessions --json
```

作用域选择：

- default：配置的默认代理存储
- `--agent <id>`：一个已配置的代理存储
- `--all-agents`：聚合所有已配置的代理存储
- `--store <path>`：显式指定的存储路径（不能与 `--agent` 或 `--all-agents` 同时使用）

JSON 示例：

`openclaw sessions --all-agents --json`：

```json
{
  "path": null,
  "stores": [
    { "agentId": "main", "path": "/home/user/.openclaw/agents/main/sessions/sessions.json" },
    { "agentId": "work", "path": "/home/user/.openclaw/agents/work/sessions/sessions.json" }
  ],
  "allAgents": true,
  "count": 2,
  "activeMinutes": null,
  "sessions": [
    { "agentId": "main", "key": "agent:main:main", "model": "gpt-5" },
    { "agentId": "work", "key": "agent:work:main", "model": "claude-opus-4-5" }
  ]
}
```

## 清理维护

立即执行维护任务（而非等待下一次写入周期）：

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --agent work --dry-run
openclaw sessions cleanup --all-agents --dry-run
openclaw sessions cleanup --enforce
openclaw sessions cleanup --enforce --active-key "agent:main:telegram:dm:123"
openclaw sessions cleanup --json
```

`openclaw sessions cleanup` 使用配置中的 `session.maintenance` 设置：

- 作用域说明：`openclaw sessions cleanup` 仅维护会话存储/转录内容，**不**清理定时任务运行日志（`cron/runs/<jobId>.jsonl`），后者由 [Cron 配置](/automation/cron-jobs#configuration) 中的 `cron.runLog.maxBytes` 和 `cron.runLog.keepLines` 管理，并在 [Cron 维护](/automation/cron-jobs#maintenance) 中详细说明。

- `--dry-run`：预览在不实际写入的情况下将被清理或截断的条目数量。
  - 在文本模式下，模拟运行（dry-run）将打印每一会话的操作表格（`Action`、`Key`、`Age`、`Model`、`Flags`），以便您查看哪些内容将被保留、哪些将被移除。
- `--enforce`：即使 `session.maintenance.mode` 为 `warn`，也强制执行维护。
- `--active-key <key>`：保护某个特定的活跃密钥免受磁盘配额驱逐。
- `--agent <id>`：对一个已配置的代理存储执行清理。
- `--all-agents`：对所有已配置的代理存储执行清理。
- `--store <path>`：针对某个特定的 `sessions.json` 文件执行清理。
- `--json`：输出 JSON 格式的摘要。若配合 `--all-agents` 使用，则输出中将为每个存储分别提供一份摘要。

`openclaw sessions cleanup --all-agents --dry-run --json`：

```json
{
  "allAgents": true,
  "mode": "warn",
  "dryRun": true,
  "stores": [
    {
      "agentId": "main",
      "storePath": "/home/user/.openclaw/agents/main/sessions/sessions.json",
      "beforeCount": 120,
      "afterCount": 80,
      "pruned": 40,
      "capped": 0
    },
    {
      "agentId": "work",
      "storePath": "/home/user/.openclaw/agents/work/sessions/sessions.json",
      "beforeCount": 18,
      "afterCount": 18,
      "pruned": 0,
      "capped": 0
    }
  ]
}
```

相关文档：

- 会话配置：[配置参考](/gateway/configuration-reference#session)