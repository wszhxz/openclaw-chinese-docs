---
summary: "How OpenClaw memory works (workspace files + automatic memory flush)"
read_when:
  - You want the memory file layout and workflow
  - You want to tune the automatic pre-compaction memory flush
---
# 内存

OpenClaw 内存是 **代理工作区中的纯 Markdown 文件**。这些文件是
事实来源；模型只会“记住”写入磁盘的内容。

内存搜索工具由活动内存插件提供（默认：
`memory-core`). 使用 `plugins.slots.memory = "none"` 禁用内存插件。

## 内存文件 (Markdown)

默认工作区布局使用两个内存层：

- `memory/YYYY-MM-DD.md`
  - 每日日志（仅追加）。
  - 会话开始时读取今天和昨天的日志。
- `MEMORY.md` (可选)
  - 精心策划的长期记忆。
  - **仅在主私有会话中加载**（从不加载到群组上下文中）。

这些文件位于工作区下 (`agents.defaults.workspace`, 默认
`~/clawd`). 有关完整布局，请参阅 [代理工作区](/concepts/agent-workspace)。

## 何时写入内存

- 决策、偏好和持久事实写入 `MEMORY.md`。
- 日常笔记和运行上下文写入 `memory/YYYY-MM-DD.md`。
- 如果有人让你“记住这个”，把它写下来（不要保留在RAM中）。
- 这个区域仍在发展。提醒模型存储记忆是有帮助的；它会知道该做什么。
- 如果你想让某些内容记住，**请求机器人将其写入** 内存。

## 自动内存刷新（预压缩提示）

当会话接近 **自动压缩** 时，OpenClaw 触发一个 **静默、代理回合** 提醒模型在
上下文压缩之前写入持久内存。默认提示明确说明模型 _可以回复_，但通常
`NO_REPLY` 是正确的响应，因此用户不会看到这个回合。

这由 `agents.defaults.compaction.memoryFlush` 控制：

```json5
{
  agents: {
    defaults: {
      compaction: {
        reserveTokensFloor: 20000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store.",
        },
      },
    },
  },
}
```

详细信息：

- **软阈值**：当会话令牌估计超过
  `contextWindow - reserveTokensFloor - softThresholdTokens` 时触发刷新。
- **默认静默**：提示包括 `NO_REPLY` 因此不会传递任何内容。
- **两个提示**：用户提示加上系统提示附加了提醒。
- **每次压缩周期一次刷新**（在 `sessions.json` 中跟踪）。
- **工作区必须可写**：如果会话在沙盒中运行
  使用 `workspaceAccess: "ro"` 或 `"none"`，则跳过刷新。

有关完整的压缩生命周期，请参阅
[会话管理 + 压缩](/reference/session-management-compaction)。

## 向量内存搜索

OpenClaw 可以在 `MEMORY.md` 和 `memory/*.md` 上构建一个小的向量索引，以便语义查询即使措辞不同也能找到相关笔记。

默认设置：

- 默认启用。
- 监控内存文件的变化（防抖动）。
- 默认使用远程嵌入。如果 `memorySearch.provider` 未设置，OpenClaw 自动选择：
  1. 如果配置了 `memorySearch.local.modelPath` 且文件存在，则使用 `local`。
  2. 如果可以解析 OpenAI 密钥，则使用 `openai`。
  3. 如果可以解析 Gemini 密钥，则使用 `gemini`。
  4. 否则，内存搜索保持禁用状态直到配置。
- 本地模式使用 node-llama-cpp 并可能需要 `pnpm approve-builds`。
- 使用 sqlite-vec（如果可用）来加速 SQLite 内部的向量搜索。

远程嵌入 **需要** 嵌入提供者的 API 密钥。OpenClaw
从认证配置文件、`models.providers.*.apiKey` 或环境变量中解析密钥。Codex OAuth 仅涵盖聊天/补全，**不** 满足内存搜索的嵌入需求。对于 Gemini，请使用 `GEMINI_API_KEY` 或
`models.providers.google.apiKey`。当使用自定义的 OpenAI 兼容端点时，
设置 `memorySearch.remote.apiKey`（以及可选的 `memorySearch.remote.headers`）。

### QMD 后端（实验性）

设置 `memory.backend = "qmd"` 以替换内置的 SQLite 索引器为
[QMD](https://github.com/tobi/qmd)：一个本地优先的搜索侧边车，结合了
BM25 + 向量 + 重排序。Markdown 仍然是事实来源；OpenClaw 调用 QMD 进行检索。关键点：

**先决条件**

- 默认禁用。按配置启用 (`memory.backend = "qmd"`)。
- 单独安装 QMD CLI (`bun install -g github.com/tobi/qmd` 或获取
  发布版本)，并确保 `qmd` 二进制文件在网关的 `PATH` 上。
- QMD 需要一个允许扩展的 SQLite 构建 (`brew install sqlite` 在
  macOS 上)。
- QMD 通过 Bun + `node-llama-cpp` 完全本地运行，并在首次使用时自动从 HuggingFace 下载 GGUF 模型（无需单独的 Ollama 守护进程）。
- 网关通过设置 `XDG_CONFIG_HOME` 和
  `XDG_CACHE_HOME` 在 `~/.openclaw/agents/<agentId>/qmd/` 下的独立 XDG 主目录中运行 QMD。
- 操作系统支持：安装 Bun + SQLite 后，macOS 和 Linux 可直接使用。Windows 最佳支持通过 WSL2。

**侧边车如何运行**

- 网关在 `~/.openclaw/agents/<agentId>/qmd/` 下写入一个独立的 QMD 主目录（配置 + 缓存 + sqlite 数据库）。
- 集合从 `memory.qmd.paths`（加上默认工作区内存文件）重写到 `index.yml`，然后在启动时和可配置的时间间隔 (`memory.qmd.update.interval`，默认 5 分钟) 运行 `qmd update` + `qmd embed`。
- 搜索通过 `qmd query --json` 进行。如果 QMD 失败或二进制文件丢失，OpenClaw 自动回退到内置的 SQLite 管理器，以便内存工具继续工作。
- **首次搜索可能较慢**：QMD 可能在第一次 `qmd query` 运行时下载本地 GGUF 模型（重排序/查询扩展）。
  - OpenClaw 在运行 QMD 时自动设置 `XDG_CONFIG_HOME`/`XDG_CACHE_HOME`。
  - 如果您希望手动预下载模型（并预热 OpenClaw 使用的同一索引），使用代理的 XDG 目录运行一次查询。

OpenClaw 的 QMD 状态存储在您的 **state dir** 下（默认为 `~/.openclaw`）。
您可以通过导出 OpenClaw 使用的相同 XDG 变量将 `qmd` 指向相同的索引：

```bash
    # Pick the same state dir OpenClaw uses
    STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
    if [ -d "$HOME/.moltbot" ] && [ ! -d "$HOME/.openclaw" ] \
      && [ -z "${OPENCLAW_STATE_DIR:-}" ]; then
      STATE_DIR="$HOME/.moltbot"
    fi

    export XDG_CONFIG_HOME="$STATE_DIR/agents/main/qmd/xdg-config"
    export XDG_CACHE_HOME="$STATE_DIR/agents/main/qmd/xdg-cache"

    # (Optional) force an index refresh + embeddings
    qmd update
    qmd embed

    # Warm up / trigger first-time model downloads
    qmd query "test" -c memory-root --json >/dev/null 2>&1
    ```

**配置表面 (`memory.qmd.*`)**

- `command`（默认 `qmd`）：覆盖可执行文件路径。
- `includeDefaultMemory`（默认 `true`）：自动索引 `MEMORY.md` + `memory/**/*.md`。
- `paths[]`：添加额外的目录/文件 (`path`，可选 `pattern`，可选
  稳定 `name`)。
- `sessions`：选择会话 JSONL 索引 (`enabled`，`retentionDays`，
  `exportDir`)。
- `update`：控制刷新频率 (`interval`，`debounceMs`，`onBoot`，`embedInterval`)。
- `limits`：限制召回负载 (`maxResults`，`maxSnippetChars`，
  `maxInjectedChars`，`timeoutMs`)。
- `scope`：与 [`session.sendPolicy`](/gateway/configuration#session) 的架构相同。
  默认为仅 DM (`deny` all，`allow` 直接聊天)；放宽以在群组/频道中显示 QMD 命中。
- 来自工作区外部的代码片段在 `memory_search` 结果中显示为 `qmd/<collection>/<relative-path>`；`memory_get`
  理解该前缀并从配置的 QMD 集合根读取。
- 当 `memory.qmd.sessions.enabled = true`，OpenClaw 将清理后的会话
  转录（用户/助手轮次）导出到 `~/.openclaw/agents/<id>/qmd/sessions/` 下的专用 QMD 集合中，
  因此 `memory_search` 可以回忆最近的对话而不接触内置的 SQLite 索引。
- `memory_search` 代码片段现在在 `memory.citations` 为 `auto`/`on` 时包含一个 `Source: <path#line>` 页脚；设置 `memory.citations = "off"` 以保持路径元数据内部（代理仍然接收路径用于
  `memory_get`，但代码片段文本省略了页脚且系统提示代理不要引用它）。

**示例**

```json5
memory: {
  backend: "qmd",
  citations: "auto",
  qmd: {
    includeDefaultMemory: true,
    update: { interval: "5m", debounceMs: 15000 },
    limits: { maxResults: 6, timeoutMs: 4000 },
    scope: {
      default: "deny",
      rules: [{ action: "allow", match: { chatType: "direct" } }]
    },
    paths: [
      { name: "docs", path: "~/notes", pattern: "**/*.md" }
    ]
  }
}
```

**引用和回退**

- `memory.citations` 无论后端为何 (`auto`/`on`/`off`) 都适用。
- 当 `qmd` 运行时，我们标记 `status().backend = "qmd"` 以便诊断显示哪个引擎提供了结果。如果 QMD 子进程退出或无法解析 JSON 输出，搜索管理器会记录警告并返回内置提供程序（现有的 Markdown 嵌入），直到 QMD 恢复。

### 额外的内存路径

如果您想索引默认工作区布局之外的 Markdown 文件，请添加显式路径：

```json5
agents: {
  defaults: {
    memorySearch: {
      extraPaths: ["../team-docs", "/srv/shared-notes/overview.md"]
    }
  }
}
```

注意事项：

- 路径可以是绝对路径或相对于工作区的路径。
- 目录会递归扫描以查找 `.md` 文件。
- 仅索引 Markdown 文件。
- 忽略符号链接（文件或目录）。

### Gemini 嵌入（原生）

将提供程序设置为 `gemini` 以直接使用 Gemini 嵌入 API：

```json5
agents: {
  defaults: {
    memorySearch: {
      provider: "gemini",
      model: "gemini-embedding-001",
      remote: {
        apiKey: "YOUR_GEMINI_API_KEY"
      }
    }
  }
}
```

注意事项：

- `remote.baseUrl` 是可选的（默认为 Gemini API 基础 URL）。
- `remote.headers` 允许您根据需要添加额外的标头。
- 默认模型：`gemini-embedding-001`。

如果您想使用 **自定义的 OpenAI 兼容端点**（OpenRouter、vLLM 或代理），您可以使用带有 OpenAI 提供程序的 `remote` 配置：

```json5
agents: {
  defaults: {
    memorySearch: {
      provider: "openai",
      model: "text-embedding-3-small",
      remote: {
        baseUrl: "https://api.example.com/v1/",
        apiKey: "YOUR_OPENAI_COMPAT_API_KEY",
        headers: { "X-Custom-Header": "value" }
      }
    }
  }
}
```

如果您不想设置 API 密钥，请使用 `memorySearch.provider = "local"` 或设置
`memorySearch.fallback = "none"`。

备用方案：

- `memorySearch.fallback` 可以是 `openai`、`gemini`、`local` 或 `none`。
- 备用提供程序仅在主要嵌入提供程序失败时使用。

批量索引（OpenAI + Gemini）：

- 默认情况下对 OpenAI 和 Gemini 嵌入启用。设置 `agents.defaults.memorySearch.remote.batch.enabled = false` 以禁用。
- 默认行为等待批量完成；如有需要，请调整 `remote.batch.wait`、`remote.batch.pollIntervalMs` 和 `remote.batch.timeoutMinutes`。
- 设置 `remote.batch.concurrency` 以控制我们并行提交多少个批量作业（默认：2）。
- 批量模式适用于 `memorySearch.provider = "openai"` 或 `"gemini"` 并使用相应的 API 密钥。
- Gemini 批量作业使用异步嵌入批量端点，并且需要 Gemini Batch API 的可用性。

为什么 OpenAI 批量处理速度快且便宜：

- 对于大规模回填，OpenAI 通常是我们的最快选项，因为我们可以在单个批处理作业中提交许多嵌入请求，并让 OpenAI 异步处理它们。
- OpenAI 为批处理 API 工作负载提供折扣定价，因此大型索引运行通常比同步发送相同请求更便宜。
- 有关详细信息，请参阅 OpenAI 批处理 API 文档和定价：
  - https://platform.openai.com/docs/api-reference/batch
  - https://platform.openai.com/pricing

配置示例：

```json5
agents: {
  defaults: {
    memorySearch: {
      provider: "openai",
      model: "text-embedding-3-small",
      fallback: "openai",
      remote: {
        batch: { enabled: true, concurrency: 2 }
      },
      sync: { watch: true }
    }
  }
}
```

工具：

- `memory_search` — 返回带有文件和行范围的代码片段。
- `memory_get` — 按路径读取内存文件内容。

本地模式：

- 设置 `agents.defaults.memorySearch.provider = "local"`。
- 提供 `agents.defaults.memorySearch.local.modelPath` (GGUF 或 `hf:` URI)。
- 可选：设置 `agents.defaults.memorySearch.fallback = "none"` 以避免远程回退。

### 内存工具的工作原理

- `memory_search` 对 `MEMORY.md` + `memory/**/*.md` 中的 Markdown 块（~400 个标记目标，80 个标记重叠）进行语义搜索。它返回代码片段文本（最多 ~700 个字符）、文件路径、行范围、分数、提供商/模型以及是否从本地 → 远程嵌入回退。不返回完整文件内容。
- `memory_get` 读取特定的内存 Markdown 文件（相对于工作区），可选地从起始行开始并读取 N 行。`MEMORY.md` / `memory/` 之外的路径会被拒绝。
- 仅当 `memorySearch.enabled` 对代理解析为真时，两个工具才被启用。

### 索引的内容（及时间）

- 文件类型：仅 Markdown (`MEMORY.md`, `memory/**/*.md`)。
- 索引存储：每个代理的 SQLite 数据库位于 `~/.openclaw/memory/<agentId>.sqlite`（通过 `agents.defaults.memorySearch.store.path` 配置，支持 `{agentId}` 标记）。
- 新鲜度：`MEMORY.md` + `memory/` 的监视器标记索引为脏（防抖 1.5 秒）。同步在会话开始、搜索时或按间隔调度，并异步运行。会话记录使用增量阈值触发后台同步。
- 重新索引触发器：索引存储嵌入 **提供商/模型 + 终端指纹 + 分块参数**。如果这些中的任何一个发生变化，OpenClaw 会自动重置并重新索引整个存储。

### 混合搜索（BM25 + 向量）

启用时，OpenClaw 结合：

- **向量相似性**（语义匹配，措辞可以不同）
- **BM25 关键词相关性**（精确标记如 ID、环境变量、代码符号）

如果您的平台上全文搜索不可用，OpenClaw 将回退到仅向量搜索。

#### 为什么是混合搜索？

向量搜索非常适合“这意味着同样的事情”：

- “Mac Studio gateway host” vs “运行网关的机器”
- “debounce file updates” vs “避免每次写入时索引”

但它在精确、高信号标记上可能较弱：

- IDs (`a828e60`, `b3b9895a…`)
- code symbols (`memorySearch.query.hybrid`)
- error strings (“sqlite-vec unavailable”)

BM25（全文检索）则相反：在精确匹配方面表现强劲，在同义句匹配方面较弱。
混合搜索是实用的中间地带：**同时使用两种检索信号**，因此对于“自然语言”查询和“大海捞月”查询都能获得良好的结果。

#### 我们如何合并结果（当前设计）

实现概要：

1. 从两方面检索候选池：

- **向量**：按余弦相似度取前`maxResults * candidateMultiplier`个。
- **BM25**：按FTS5 BM25排名取前`maxResults * candidateMultiplier`个（数值越低越好）。

2. 将BM25排名转换为0到1左右的分数：

- `textScore = 1 / (1 + max(0, bm25Rank))`

3. 按块ID合并候选者并计算加权分数：

- `finalScore = vectorWeight * vectorScore + textWeight * textScore`

注意事项：

- `vectorWeight` + `textWeight` 在配置解析中归一化为1.0，因此权重表现为百分比。
- 如果嵌入不可用（或提供者返回零向量），我们仍然运行BM25并返回关键字匹配。
- 如果无法创建FTS5，我们将保持仅向量搜索（不会硬性失败）。

这并不是“信息检索理论上的完美”，但它简单、快速，并且在真实笔记上通常能提高召回率/精确度。
如果我们以后想变得更复杂，常见的下一步是互惠排名融合（RRF）或在混合前进行评分标准化（最小/最大或z分数）。

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

### 嵌入缓存

OpenClaw可以在SQLite中缓存**块嵌入**，因此重新索引和频繁更新（尤其是会话记录）不会重新嵌入未更改的文本。

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

### 会话内存搜索（实验性）

您可以选择性地索引**会话记录**并通过`memory_search`展示它们。
此功能受一个实验性标志控制。

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

注意事项：

- 会话索引是**可选的**（默认关闭）。
- 会话更新会被防抖处理，并且在超过阈值时**异步索引**（尽力而为）。
- `memory_search` 永远不会因为索引而阻塞；结果可能会在后台同步完成之前稍微过时。
- 结果仍然只包括代码片段；`memory_get` 仍然仅限于内存文件。
- 会话索引按代理隔离（只有该代理的会话日志会被索引）。
- 会话日志存储在磁盘上 (`~/.openclaw/agents/<agentId>/sessions/*.jsonl`)。任何具有文件系统访问权限的进程/用户都可以读取它们，因此将磁盘访问视为信任边界。为了更严格的隔离，请在单独的操作系统用户或主机下运行代理。

阈值（默认值显示如下）：

```json5
agents: {
  defaults: {
    memorySearch: {
      sync: {
        sessions: {
          deltaBytes: 100000,   // ~100 KB
          deltaMessages: 50     // JSONL lines
        }
      }
    }
  }
}
```

### SQLite 向量加速 (sqlite-vec)

当可用时，OpenClaw 使用 sqlite-vec 扩展将嵌入存储在
SQLite 虚拟表 (`vec0`) 中，并在数据库中执行向量距离查询。
这使得搜索速度加快，而无需将每个嵌入加载到 JS 中。

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

注意事项：

- `enabled` 默认为 true；当禁用时，搜索会回退到对存储嵌入进行的进程内余弦相似度计算。
- 如果缺少 sqlite-vec 扩展或无法加载，OpenClaw 会记录错误并继续使用 JS 回退（没有向量表）。
- `extensionPath` 覆盖捆绑的 sqlite-vec 路径（适用于自定义构建或非标准安装位置）。

### 本地嵌入自动下载

- 默认本地嵌入模型：`hf:ggml-org/embeddinggemma-300M-GGUF/embeddinggemma-300M-Q8_0.gguf`（约0.6 GB）。
- 当 `memorySearch.provider = "local"` 时，`node-llama-cpp` 解析 `modelPath`；如果缺少 GGUF，则会**自动下载**到缓存（或 `local.modelCacheDir` 如果已设置），然后加载它。重试时会恢复下载。
- 原生构建要求：运行 `pnpm approve-builds`，选择 `node-llama-cpp`，然后 `pnpm rebuild node-llama-cpp`。
- 备用方案：如果本地设置失败且 `memorySearch.fallback = "openai"`，我们会自动切换到远程嵌入 (`openai/text-embedding-3-small` 除非被覆盖) 并记录原因。

### 自定义 OpenAI 兼容端点示例

```json5
agents: {
  defaults: {
    memorySearch: {
      provider: "openai",
      model: "text-embedding-3-small",
      remote: {
        baseUrl: "https://api.example.com/v1/",
        apiKey: "YOUR_REMOTE_API_KEY",
        headers: {
          "X-Organization": "org-id",
          "X-Project": "project-id"
        }
      }
    }
  }
}
```

注意事项：

- `remote.*` 优先于 `models.providers.openai.*`。
- `remote.headers` 与 OpenAI 头部合并；在键冲突时远程版本获胜。省略 `remote.headers` 以使用 OpenAI 默认值。