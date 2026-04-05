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
openclaw sessions --verbose
openclaw sessions --json
```

范围选择：

- default: 配置的默认代理存储
- `--verbose`: 详细日志记录
- `--agent <id>`: 单个配置的代理存储
- `--all-agents`: 聚合所有配置的代理存储
- `--store <path>`: 显式存储路径（不能与 `--agent` 或 `--all-agents` 组合）

`openclaw sessions --all-agents` 读取配置的代理存储。网关和 ACP 会话发现的范围更广：它们还包含位于默认 `agents/` 根目录或模板化 `session.store` 根目录下的仅磁盘存储。这些发现的存储必须解析为代理根目录内的常规 `sessions.json` 文件；符号链接和根目录外路径将被跳过。

JSON 示例：

`openclaw sessions --all-agents --json`:

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
    { "agentId": "work", "key": "agent:work:main", "model": "claude-opus-4-6" }
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
openclaw sessions cleanup --enforce --active-key "agent:main:telegram:direct:123"
openclaw sessions cleanup --json
```

`openclaw sessions cleanup` 使用配置中的 `session.maintenance` 设置：

- 范围说明：`openclaw sessions cleanup` 仅维护会话存储/会话记录。它不会修剪 cron 运行日志 (`cron/runs/<jobId>.jsonl`)，这些日志由 [Cron 配置](/automation/cron-jobs#configuration) 中的 `cron.runLog.maxBytes` 和 `cron.runLog.keepLines` 管理，并在 [Cron 维护](/automation/cron-jobs#maintenance) 中解释。

- `--dry-run`: 预览在不写入的情况下将修剪/限制多少条目。
  - 在文本模式下，dry-run 打印每个会话的操作表 (`Action`, `Key`, `Age`, `Model`, `Flags`)，以便您可以查看保留与移除的内容。
- `--enforce`: 即使 `session.maintenance.mode` 为 `warn` 也应用维护。
- `--fix-missing`: 移除缺少会话记录文件的条目，即使它们通常尚未达到老化/淘汰标准。
- `--active-key <key>`: 保护特定活动密钥免受磁盘预算驱逐。
- `--agent <id>`: 为一个配置的代理存储运行清理。
- `--all-agents`: 为所有配置的代理存储运行清理。
- `--store <path>`: 针对特定 `sessions.json` 文件运行。
- `--json`: 打印 JSON 摘要。带有 `--all-agents` 时，输出包含每个存储的一个摘要。

`openclaw sessions cleanup --all-agents --dry-run --json`:

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