---
summary: "CLI reference for `openclaw memory` (status/index/search)"
read_when:
  - You want to index or search semantic memory
  - You’re debugging memory availability or indexing
title: "memory"
---
# `openclaw memory`

管理语义记忆索引和搜索。
由活动记忆插件提供（默认：`memory-core`；设置 `plugins.slots.memory = "none"` 以禁用）。

相关：

- 记忆概念：[记忆](/concepts/memory)
- 插件：[插件](/tools/plugin)

## 示例

```bash
openclaw memory status
openclaw memory status --deep
openclaw memory index --force
openclaw memory search "meeting notes"
openclaw memory search --query "deployment" --max-results 20
openclaw memory status --json
openclaw memory status --deep --index
openclaw memory status --deep --index --verbose
openclaw memory status --agent main
openclaw memory index --agent main --verbose
```

## 选项

`memory status` 和 `memory index`：

- `--agent <id>`：限定范围为单个 agent。如果没有此选项，这些命令将为每个配置的 agent 运行；如果未配置 agent 列表，则回退到默认 agent。
- `--verbose`：在探测和索引期间发出详细日志。

`memory status`：

- `--deep`：探测 vector + embedding 可用性。
- `--index`：如果 store 处于 dirty 状态则运行重新索引（隐含 `--deep`）。
- `--json`：打印 JSON 输出。

`memory index`：

- `--force`：强制完全重新索引。

`memory search`：

- 查询输入：传递位置参数 `[query]` 或 `--query <text>`。
- 如果两者都提供，`--query` 优先。
- 如果两者都未提供，命令将报错退出。
- `--agent <id>`：限定范围为单个 agent（默认：默认 agent）。
- `--max-results <n>`：限制返回的结果数量。
- `--min-score <n>`：过滤掉低分匹配项。
- `--json`：打印 JSON 结果。

注意：

- `memory index --verbose` 打印每个阶段的详细信息（provider, model, sources, batch activity）。
- `memory status` 包含通过 `memorySearch.extraPaths` 配置的任何额外路径。
- 如果有效活动记忆远程 API 密钥字段配置为 SecretRefs，命令将从活动 gateway 快照解析这些值。如果 gateway 不可用，命令将快速失败。
- Gateway 版本偏差注意：此命令路径需要支持 `secrets.resolve` 的 gateway；较旧的 gateway 将返回 unknown-method 错误。