---
summary: "CLI reference for `openclaw sessions` (list stored sessions + usage)"
read_when:
  - You want to list stored sessions and see recent activity
title: "sessions"
---
# `openclaw sessions`

列出存储的对话会话。

```bash
openclaw sessions
openclaw sessions --agent work
openclaw sessions --all-agents
openclaw sessions --active 120
openclaw sessions --json
```

作用域选择：

- default：配置的默认 agent 存储
- `--agent <id>`：一个配置的 agent 存储
- `--all-agents`：聚合所有配置的 agent 存储
- `--store <path>`：显式存储路径（不能与 `--agent` 或 `--all-agents` 组合使用）

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

立即运行维护（而不是等待下一个写入周期）：

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --agent work --dry-run
openclaw sessions cleanup --all-agents --dry-run
openclaw sessions cleanup --enforce
openclaw sessions cleanup --enforce --active-key "agent:main:telegram:dm:123"
openclaw sessions cleanup --json
```

`openclaw sessions cleanup` 使用配置中的 `session.maintenance` 设置：

- 作用域说明：`openclaw sessions cleanup` 仅维护会话存储/记录。它不会修剪 cron 运行日志 (`cron/runs/<jobId>.jsonl`)，后者由 [Cron 配置](/automation/cron-jobs#configuration) 中的 `cron.runLog.maxBytes` 和 `cron.runLog.keepLines` 管理，并在 [Cron 维护](/automation/cron-jobs#maintenance) 中解释。

- `--dry-run`：预览将有多少条目会被修剪/限制而不进行写入。
  - 在文本模式下，dry-run 会打印每个会话的操作表 (`Action`, `Key`, `Age`, `Model`, `Flags`)，以便您可以查看哪些会被保留 vs 移除。
- `--enforce`：即使 `session.maintenance.mode` 为 `warn` 时也应用维护。
- `--active-key <key>`：保护特定活动键免受磁盘预算驱逐。
- `--agent <id>`：对一个配置的 agent 存储运行清理。
- `--all-agents`：对所有配置的 agent 存储运行清理。
- `--store <path>`：针对特定 `sessions.json` 文件运行。
- `--json`：打印 JSON 摘要。使用 `--all-agents` 时，输出包含每个存储一个摘要。

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

相关：

- 会话配置：[配置参考](/gateway/configuration-reference#session)