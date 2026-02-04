---
summary: "CLI reference for `openclaw memory` (status/index/search)"
read_when:
  - You want to index or search semantic memory
  - You’re debugging memory availability or indexing
title: "memory"
---
# `openclaw memory`

管理语义记忆索引和搜索。
由活动内存插件提供（默认：`memory-core`；设置`plugins.slots.memory = "none"`以禁用）。

相关：

- 内存概念：[Memory](/concepts/memory)
- 插件：[Plugins](/plugins)

## 示例

```bash
openclaw memory status
openclaw memory status --deep
openclaw memory status --deep --index
openclaw memory status --deep --index --verbose
openclaw memory index
openclaw memory index --verbose
openclaw memory search "release checklist"
openclaw memory status --agent main
openclaw memory index --agent main --verbose
```

## 选项

常用：

- `--agent <id>`: 限定到单个代理（默认：所有配置的代理）。
- `--verbose`: 在探测和索引期间输出详细日志。

注意：

- `memory status --deep` 探测向量 + 嵌入可用性。
- `memory status --deep --index` 如果存储已损坏则运行重新索引。
- `memory index --verbose` 打印每个阶段的详细信息（提供者、模型、来源、批处理活动）。
- `memory status` 包括通过`memorySearch.extraPaths`配置的任何额外路径。