---
summary: "How OpenClaw memory works (workspace files + automatic memory flush)"
read_when:
  - You want the memory file layout and workflow
  - You want to tune the automatic pre-compaction memory flush
title: "Memory"
---
# 内存

## 内存文件（Markdown）

OpenClaw 的内存存储在代理工作区中的纯 Markdown 文件中。内存搜索工具包括向量搜索和 BM25 关键字相关性搜索。如果平台不支持全文搜索，OpenClaw 将回退到仅向量搜索。

## 混合搜索（BM25 + 向量）

当启用时，OpenClaw 会结合以下内容：

- **向量相似性**（语义匹配，措辞可以不同）
- **BM25 关键字相关性**（精确的标记，如 ID、环境变量、代码符号）

如果平台不支持全文搜索，OpenClaw 将回退到仅向量搜索。

### 为什么混合？

向量搜索在“这表示相同的事物”方面表现优异：

- “Mac Studio 网关主机” vs “运行网关的机器”
- “防抖文件更新” vs “避免每次写入时索引”

但向量搜索在精确的高信号标记方面可能较弱：

- ID (`a828e60`, `b3b9895a…`)
- 代码符号 (`memorySearch.query.hybrid`)
- 错误字符串（“sqlite-vec 不可用”）

BM25（全文）则相反：擅长精确标记，但对同义词较弱。混合搜索是务实的中间地带：**使用两种检索信号**，以便在“自然语言”查询和“大海捞针”查询中都能获得良好结果。

### 如何合并结果（当前设计）

实现草图：

1. 从两个方面检索候选池：

- **向量**：按余弦相似度取前 `maxResults * candidateMultiplier` 个结果。
- **BM25**：按 FTS5 BM25 排名（越低越好）取前 `maxResults * candidateMultiplier` 个结果。

2. 将 BM25 排名转换为 0..1 左右的分数：

- `textScore = 1 / (1 + max(0, bm25Rank))`

3. 通过分块 ID 合并候选并计算加权分数：

- `finalScore = vectorWeight * vectorScore + textWeight * textScore`

注释：

- `vectorWeight` + `textWeight` 在配置解析时归一化为 1.0，因此权重行为如同百分比。
- 如果嵌入不可用（或提供者返回零向量），我们仍运行 BM25 并返回关键字匹配。
- 如果无法创建 FTS5，我们保留仅向量搜索（无硬性失败）。

这不是“信息检索理论完美”，但简单、快速，并且在实际笔记中倾向于提高召回率/精确度。如果以后想更复杂，常见的下一步是反向排名融合（RRF）或在混合前进行分数归一化（最小/最大或 z 分数）。

配置：

```json5
agents: {
  defaults: {
    memorySearch: {
      query: {
        hybrid: {
          enabled: true,
          vectorWeight: 0.7,
          textWeight: 0.3,
          candidateMultiplier: 4
        }
      }
    }
  }
}
```

## 嵌入缓存

OpenClaw 可以在 SQLite 中缓存 **分块嵌入**，以便重新索引和频繁更新（尤其是会话转录）不会重新嵌入未更改的文本。

配置：

```json5
agents: {
  defaults: {
    memorySearch: {
      cache: {
        enabled: true,
        maxEntries: 50000
      }
    }
  }
}
```

## 会话内存搜索（实验性）

您可以选择性地索引 **会话转录** 并通过 `memory_search` 表面它们。此功能受实验性标志控制。

```json5
agents: {
  defaults: {
    memorySearch: {
      experimental: { sessionMemory: true },
      sources: ["memory", "sessions"]
    }
  }
}
```

注释：

- 会话索引是 **可选的**（默认关闭）。
- 会话更新被防抖，并在跨越 delta 阈值后 **异步索引**（尽力而为）。
- `memory_search` 从不阻塞索引；结果在后台同步完成前可能略微过时。
- 结果仍仅包含片段；`memory_get` 仍仅限于内存文件。
- 会话索引按代理隔离（仅该代理的会话日志被索引）。
- 会话日志存储在磁盘上（`~/.openclaw/agents/<agentId>/sessions/*.jsonl`）。任何具有文件系统访问权限的进程/用户都可以读取它们，因此将磁盘访问视为信任边界。为了更严格的隔离，可在单独的 OS 用户或主机下运行代理。

Delta 阈值（默认值显示）：

```json5
agents: {
  defaults: {
    memorySearch: {
      sync: {
        sessions: {
          deltaBytes: 100000,   // ~100 KB
          deltaMessages: 50     // JSONL 行
        }
      }
    }
  }
}
```

## SQLite 向量加速（sqlite-vec）

当 sqlite-vec 扩展可用时，OpenClaw 会将嵌入存储在 SQLite 虚拟表（`vec0`）中，并在数据库中执行向量距离查询。这使得搜索快速，无需将每个嵌入加载到 JS 中。

配置（可选）：

```json5
agents: {
  defaults: {
    memorySearch: {
      store: {
        vector: {
          enabled: true,
          extensionPath: "/path/to/sqlite-vec"
        }
      }
    }
  }
}
```

注释：

- `enabled` 默认为 true；禁用时，搜索将回退到对存储嵌入的进程内余弦相似度。
- 如果 sqlite-vec 扩展缺失或加载失败，OpenClaw 会记录错误并继续使用 JS 回退（无向量表）。
- `extensionPath` 覆盖捆绑的 sqlite-vec 路径（用于自定义构建或非标准安装位置）