---
summary: "CLI reference for `openclaw memory` (status/index/search/promote)"
read_when:
  - You want to index or search semantic memory
  - You’re debugging memory availability or indexing
  - You want to promote recalled short-term memory into `MEMORY.md`
title: "memory"
---
# `openclaw memory`

管理语义记忆索引和搜索。
由活动内存插件提供（默认值：`memory-core`；设置 `plugins.slots.memory = "none"` 以禁用）。

相关：

- 内存概念：[Memory](/concepts/memory)
- 插件：[Plugins](/tools/plugin)

## 示例

```bash
openclaw memory status
openclaw memory status --deep
openclaw memory status --fix
openclaw memory index --force
openclaw memory search "meeting notes"
openclaw memory search --query "deployment" --max-results 20
openclaw memory promote --limit 10 --min-score 0.75
openclaw memory promote --apply
openclaw memory promote --json --min-recall-count 0 --min-unique-queries 0
openclaw memory status --json
openclaw memory status --deep --index
openclaw memory status --deep --index --verbose
openclaw memory status --agent main
openclaw memory index --agent main --verbose
```

## 选项

`memory status` 和 `memory index`：

- `--agent <id>`：限定为单个代理。若无此参数，这些命令将为每个配置的代理运行；如果未配置代理列表，则回退到默认代理。
- `--verbose`：在探测和索引期间输出详细日志。

`memory status`：

- `--deep`：探测向量 + 嵌入可用性。
- `--index`：如果存储脏数据则运行重新索引（隐含 `--deep`）。
- `--fix`：修复过时的回忆锁并标准化提升元数据。
- `--json`：打印 JSON 输出。

`memory index`：

- `--force`：强制完全重新索引。

`memory search`：

- 查询输入：传递位置参数 `[query]` 或 `--query <text>`。
- 如果两者都提供，`--query` 优先。
- 如果两者均未提供，命令将报错退出。
- `--agent <id>`：限定为单个代理（默认：默认代理）。
- `--max-results <n>`：限制返回结果的数量。
- `--min-score <n>`：过滤低分匹配项。
- `--json`：打印 JSON 结果。

`memory promote`：

预览并应用短期记忆提升。

```bash
openclaw memory promote [--apply] [--limit <n>] [--include-promoted]
```

- `--apply` -- 将提升写入 `MEMORY.md`（默认：仅预览）。
- `--limit <n>` -- 限制显示候选项的数量。
- `--include-promoted` -- 包含之前周期中已提升的条目。

完整选项：

- 使用加权回忆信号（`frequency`, `relevance`, `query diversity`, `recency`）对来自 `memory/YYYY-MM-DD.md` 的短期候选项进行排名。
- 使用当 `memory_search` 返回每日内存命中时捕获的回忆事件。
- 可选自动做梦模式：当 `plugins.entries.memory-core.config.dreaming.mode` 为 `core`、`deep` 或 `rem` 时，`memory-core` 自动管理一个后台触发提升的 cron 任务（无需手动 `openclaw cron add`）。
- `--agent <id>`：限定为单个代理（默认：默认代理）。
- `--limit <n>`：最大返回/应用的候选项数量。
- `--min-score <n>`：最小加权提升分数。
- `--min-recall-count <n>`：候选项所需的最小回忆次数。
- `--min-unique-queries <n>`：候选项所需的最小不同查询次数。
- `--apply`：将选定的候选项追加到 `MEMORY.md` 并标记为已提升。
- `--include-promoted`：在输出中包含已提升的候选项。
- `--json`：打印 JSON 输出。

## 做梦（实验性）

做梦是记忆的夜间反思过程。它被称为“做梦”，因为系统会回顾白天回忆过的内容，并决定哪些值得长期保留。

- 它是可选的，默认禁用。
- 使用 `plugins.entries.memory-core.config.dreaming.mode` 启用它。
- 您可以通过聊天使用 `/dreaming off|core|rem|deep` 切换模式。运行 `/dreaming`（或 `/dreaming options`）查看每种模式的作用。
- 启用后，`memory-core` 会自动创建和维护托管的 cron 任务。
- 如果您希望启用做梦但暂停自动提升，请将 `dreaming.limit` 设置为 `0`。
- 排名使用加权信号：回忆频率、检索相关性、查询多样性和时间近期性（最近的回忆随时间衰减）。
- 只有满足质量阈值时才会提升到 `MEMORY.md`，因此长期内存保持高信号强度，而不是收集一次性细节。

默认模式预设：

- `core`：每天在 `0 3 * * *`、`minScore=0.75`、`minRecallCount=3`、`minUniqueQueries=2`
- `deep`：每 12 小时（`0 */12 * * *`）、`minScore=0.8`、`minRecallCount=3`、`minUniqueQueries=3`
- `rem`：每 6 小时（`0 */6 * * *`）、`minScore=0.85`、`minRecallCount=4`、`minUniqueQueries=3`

示例：

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "mode": "core"
          }
        }
      }
    }
  }
}
```

注意：

- `memory index --verbose` 打印各阶段详情（提供商、模型、来源、批处理活动）。
- `memory status` 包含通过 `memorySearch.extraPaths` 配置的任何额外路径。
- 如果有效活动内存远程 API 密钥字段配置为 SecretRefs，该命令将从活动网关快照解析这些值。如果网关不可用，命令将快速失败。
- 网关版本偏差说明：此命令路径需要支持 `secrets.resolve` 的网关；旧版网关将返回未知方法错误。
- 做梦节奏默认为每种模式的预设时间表。使用 `plugins.entries.memory-core.config.dreaming.frequency` 作为 cron 表达式覆盖节奏（例如 `0 3 * * *`），并使用 `timezone`、`limit`、`minScore`、`minRecallCount` 和 `minUniqueQueries` 进行微调。