---
summary: "CLI reference for `openclaw memory` (status/index/search)"
read_when:
  - You want to index or search semantic memory
  - You’re debugging memory availability or indexing
title: "memory"
---
# `openclaw 内存`

管理语义内存索引和搜索。
由活动内存插件提供（默认：`memory-core`；设置 `plugins.slots.memory = "none"` 以禁用）。

相关：

- 内存概念：[内存](/concepts/memory)
- 插件：[插件](/plugins)

## 示例

```bash
openclaw 内存 状态
openclaw 内存 状态 --deep
openclaw 内存 状态 --deep --index
openclaw 内存 状态 --deep --index --verbose
openclaw 内存 索引
openclaw 内存 索引 --verbose
openclaw 内存 搜索 "release checklist"
openclaw 内存 状态 --agent main
openclaw 内存 索引 --agent main --verbose
```

## 选项

通用：

- `--agent <id>`：限定到单个代理（默认：所有配置的代理）。
- `--verbose`：在探测和索引过程中输出详细日志。

说明：

- `memory 状态 --deep` 会探测向量 + 嵌入的可用性。
- `memory 状态 --deep --index` 如果存储已脏则执行重新索引。
- `memory 索引 --verbose` 会打印各阶段的详细信息（提供者、模型、来源、批次活动）。
- `memory 状态` 包括通过 `memorySearch.extraPaths` 配置的任何额外路径。