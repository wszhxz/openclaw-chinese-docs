---
summary: "CLI reference for `openclaw memory` (status/index/search)"
read_when:
  - You want to index or search semantic memory
  - You’re debugging memory availability or indexing
title: "memory"
---
# `openclaw memory`

管理语义内存的索引与搜索。  
由活动内存插件提供（默认启用：`memory-core`；设置 `plugins.slots.memory = "none"` 可禁用）。

相关文档：

- 内存概念：[内存](/concepts/memory)  
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

- `--agent <id>`：限定为单个智能体。若未指定，则这些命令将在每个已配置的智能体上运行；若未配置智能体列表，则回退至默认智能体。  
- `--verbose`：在探测和索引过程中输出详细日志。

`memory status`：

- `--deep`：探测向量存储及嵌入可用性。  
- `--index`：当存储状态为“脏”时执行重新索引（隐含 `--deep`）。  
- `--json`：以 JSON 格式打印输出。

`memory index`：

- `--force`：强制执行完整重新索引。

`memory search`：

- 查询输入：可传入位置参数 `[query]` 或 `--query <text>`。  
- 若两者均提供，则以 `--query` 为准。  
- 若两者均未提供，命令将报错退出。  
- `--agent <id>`：限定为单个智能体（默认为默认智能体）。  
- `--max-results <n>`：限制返回结果的数量。  
- `--min-score <n>`：过滤掉低分匹配项。  
- `--json`：以 JSON 格式打印查询结果。

注意事项：

- `memory index --verbose` 将按阶段打印详细信息（提供方、模型、数据源、批处理活动）。  
- `memory status` 包含通过 `memorySearch.extraPaths` 配置的任何额外路径。  
- 若实际生效的内存远程 API 密钥字段被配置为 SecretRefs，该命令将从活动网关快照中解析这些值；若网关不可用，则命令快速失败。  
- 网关版本兼容性说明：此命令路径要求网关支持 `secrets.resolve`；旧版网关将返回“未知方法”错误。