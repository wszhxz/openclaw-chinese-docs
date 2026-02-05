---
summary: "How OpenClaw memory works (workspace files + automatic memory flush)"
read_when:
  - You want the memory file layout and workflow
  - You want to tune the automatic pre-compaction memory flush
---
# 内存

OpenClaw 内存是 **代理工作区中的纯 Markdown 文件**。文件是事实来源；模型只会“记住”写入磁盘的内容。

内存搜索工具由活动的内存插件提供（默认：`memory-core`）。使用 `plugins.slots.memory = "none"` 禁用内存插件。

## 内存文件（Markdown）

默认的工作区布局使用两个内存层：

- `memory/YYYY-MM-DD.md`
  - 每日日志（仅追加）。
  - 会话开始时读取今天和昨天的日志。
- `MEMORY.md`（可选）
  - 精心策划的长期记忆。
  - **仅在主私有会话中加载**（从不加载到群组上下文中）。

这些文件位于工作区下 (`agents.defaults.workspace`，默认 `~/clawd`)。有关完整布局，请参阅 [代理工作区](/concepts/agent-workspace)。

## 何时写入内存

- 决策、偏好和持久性事实写入 `MEMORY.md`。
- 日常笔记和运行上下文写入 `memory/YYYY-MM-DD.md`。
- 如果有人让你“记住这个”，把它写下来（不要保留在RAM中）。
- 这个区域仍在发展中。提醒模型存储记忆是有帮助的；它会知道该做什么。
- 如果你想让某些内容保留，**请求机器人将其写入** 内存。

## 自动内存刷新（预压缩提示）

当会话接近自动压缩时，OpenClaw 触发一个 **静默、代理式回合**，提醒模型在上下文压缩之前写入持久性内存。默认提示明确说明模型 _可以回复_，但通常 `NO_REPLY` 是正确的响应，因此用户不会看到这个回合。

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

- **软阈值**：当会话令牌估计超过 `contextWindow - reserveTokensFloor - softThresholdTokens` 时触发刷新。
- **默认静默**：提示包括 `NO_REPLY` 因此不会传递任何内容。
- **两个提示**：一个用户提示加上一个系统提示附加了提醒。
- **每次压缩周期一次刷新**（在 `sessions.json` 中跟踪）。
- **工作区必须可写**：如果会话以沙盒模式运行，并且设置了 `workspaceAccess: "ro"` 或 `"none"`，则跳过刷新。

有关完整的压缩生命周期，请参阅 [会话管理 + 压缩](/reference/session-management-compaction)。

## 向量内存搜索

OpenClaw 可以在 `MEMORY.md` 和 `memory/*.md` 上构建一个小的向量索引，以便语义查询即使措辞不同也能找到相关笔记。

默认设置：

- 默认启用。
- 监视内存文件的变化（带防抖）。
- 默认使用远程嵌入。如果未设置 `memorySearch.provider`，OpenClaw 自动选择：
  1. 如果配置了 `memorySearch.local.modelPath` 并且文件存在，则使用 `local`。
  2. 如果可以解析 OpenAI 密钥，则使用 `openai`。
  3. 如果可以解析 Gemini 密钥，则使用 `gemini`。
  4. 否则，内存搜索保持禁用状态直到配置。
- 本地模式使用 node-llama-cpp 并可能需要 `pnpm approve-builds`。
- 使用 sqlite-vec（如果可用）来加速 SQLite 内的向量搜索。

远程嵌入 **需要** 嵌入提供者的 API 密钥。OpenClaw 从认证配置文件、`models.providers.*.apiKey` 或环境变量解析密钥。Codex OAuth 仅涵盖聊天/补全，**不满足** 内存搜索的嵌入需求。对于 Gemini，使用 `GEMINI_API_KEY` 或 `models.providers.google.apiKey`。使用自定义的 OpenAI 兼容端点时，设置 `memorySearch.remote.apiKey`（以及可选的 `memorySearch.remote.headers`）。

### QMD 后端（实验性）

设置 `memory.backend = "qmd"` 以交换内置的 SQLite 索引器为 [QMD](https://github.com/tobi/qmd)：一个本地优先的搜索侧边车，结合 BM25 + 向量 + 重排序。Markdown 仍然是事实来源；OpenClaw 调用 QMD 进行检索。关键点：

**先决条件**

- 默认禁用。按配置选择加入 (`memory.backend = "qmd"`)。
- 单独安装 QMD CLI (`bun install -g github.com/tobi/qmd` 或获取发布版本)，并确保 `qmd` 二进制文件在网关的 `PATH` 上。
- QMD 需要允许扩展的 SQLite 构建 (`brew install sqlite` 在 macOS 上)。
- QMD 通过 Bun + `node-llama-cpp` 完全本地运行，并在首次使用时自动从 HuggingFace 下载 GGUF 模型（无需单独的 Ollama 守护进程）。
- 网关通过设置 `XDG_CONFIG_HOME` 和 `XDG_CACHE_HOME` 在 `~/.openclaw/agents/<agentId>/qmd/` 下创建一个独立的 XDG 主目录来运行 QMD。
- 操作系统支持：安装 Bun + SQLite 后 macOS 和 Linux 可直接使用。Windows 最佳支持通过 WSL2。

**侧边车如何运行**

- 网关在 `~/.openclaw/agents/<agentId>/qmd/` 下写入一个独立的 QMD 主目录（配置 + 缓存 + SQLite 数据库）。
- 集合从 `memory.qmd.paths`（加上默认工作区内存文件）重写到 `index.yml`，然后在启动时和可配置间隔 (`memory.qmd.update.interval`，默认 5 分钟) 运行 `qmd update` + `qmd embed`。
- 搜索通过 `qmd query --json` 运行。如果 QMD 失败或二进制文件丢失，OpenClaw 自动回退到内置的 SQLite 管理器，使内存工具继续工作。
- **第一次搜索可能较慢**：QMD 可能在第一次 `qmd query` 运行时下载本地 GGUF 模型（重排序/查询扩展）。
  - OpenClaw 在运行 QMD 时自动设置 `XDG_CONFIG_HOME`/`XDG_CACHE_HOME`。
  - 如果您希望手动预下载模型（并预热 OpenClaw 使用的相同索引），使用代理的 XDG 目录运行一次性查询。

    OpenClaw 的 QMD 状态位于您的 **状态目录**（默认为 `~/.openclaw`）。
    您可以通过导出 OpenClaw 使用的相同 XDG 变量，将 `qmd` 指向完全相同的索引：

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

- `command`（默认 `qmd`）：覆盖可执行路径。
- `includeDefaultMemory`（默认 `true`）：自动索引 `MEMORY.md` + `memory/**/*.md`。
- `paths[]`：添加额外的目录/文件 (`path`，可选 `pattern`，可选稳定 `name`)。
- `sessions`：选择会话 JSONL 索引 (`enabled`，`retentionDays`，`exportDir`)。
- `update`：控制刷新频率 (`interval`，`debounceMs`，`onBoot`，`embedInterval`)。
- `limits`：限制召回负载 (`maxResults`，`maxSnippetChars`，`maxInjectedChars`，`timeoutMs`)。
- `scope`：与 [`session.sendPolicy`](/gateway/configuration#session) 相同的架构。默认仅限 DM (`deny` 所有，`allow` 直接聊天)；放宽以在群组/频道中显示 QMD 命中。
- 来自工作区外的片段在 `memory_search` 结果中显示为 `qmd/<collection>/<relative-path>`；`memory_get` 理解该前缀并从配置的 QMD 集合根读取。
- 当 `memory.qmd.sessions.enabled = true` 时，OpenClaw 将清理的会话记录（用户/助手回合）导出到专用的 QMD 集合下 `~/.openclaw/agents/<id>/qmd/sessions/`，因此 `memory_search` 可以回忆最近的对话而不接触内置的 SQLite 索引。
- `memory_search` 片段现在在 `memory.citations` 为 `auto`/`on` 时包含一个 `Source: <path#line>` 页脚；设置 `memory.citations = "off"` 以保持路径元数据内部（代理仍然接收路径用于 `memory_get`，但片段文本省略页脚，系统提示警告代理不要引用它）。

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

- `memory.citations` 不管后端 (`auto`/`on`/`off`) 如何都适用。
- 当 `qmd` 运行时，我们标记 `status().backend = "qmd"` 以便诊断显示哪个引擎提供了结果。如果 QMD 子进程退出或无法解析 JSON 输出，搜索管理器记录警告并返回内置提供者（现有的 Markdown 嵌入），直到 QMD 恢复。

### 额外的内存路径

如果您想索引默认工作区布局之外的 Markdown 文件，添加显式路径：

```json5
agents: {
  defaults: {
    memorySearch: {
      extraPaths: ["../team-docs", "/srv/shared-notes/overview.md"]
    }
  }
}
```

注意：

- 路径可以是绝对路径或工作区相对路径。
- 目录递归扫描 `.md` 文件。
- 仅索引 Markdown 文件。
- 忽略符号链接（文件或目录）。

### Gemini 嵌入（原生）

将提供者设置为 `gemini` 以直接使用 Gemini 嵌入 API：

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

注意：

- `remote.baseUrl` 是可选的（默认为 Gemini API 基础 URL）。
- `remote.headers` 允许您根据需要添加额外的头信息。
- 默认模型：`gemini-embedding-001`。

如果您想使用 **自定义的 OpenAI 兼容端点**（OpenRouter、vLLM 或代理），可以使用带有 OpenAI 提供者的 `remote` 配置：

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

如果您不想设置 API 密钥，使用 `memorySearch.provider = "local"` 或设置 `memorySearch.fallback = "none"`。

回退选项：

- `memorySearch.fallback` 可以是 `openai`，`gemini`，`local` 或 `none`。
- 仅在主要嵌入提供者失败时使用回退提供者。

批量索引（OpenAI + Gemini）：

- 默认对 OpenAI 和 Gemini 嵌入启用。设置 `agents.defaults.memorySearch.remote.batch.enabled = false` 以禁用。
- 默认行为等待批量完成；根据需要调整 `remote.batch.wait`，`remote.batch.pollIntervalMs` 和 `remote.batch.timeoutMinutes`。
- 设置 `remote.batch.concurrency` 以控制并行提交的批处理作业数量（默认：2）。
- 批处理模式适用于 `memorySearch.provider = "openai"` 或 `"gemini"` 并使用相应的 API 密钥。
- Gemini 批处理作业使用异步嵌入批处理端点并需要 Gemini 批处理 API 的可用性。

为什么 OpenAI 批处理速度快且便宜：

- 对于大型回填，OpenAI 通常是支持的最快选项，因为我们可以在单个批处理作业中提交许多嵌入请求，并让 OpenAI 异步处理它们。
- OpenAI 为批处理 API 工作负载提供折扣定价，因此大型索引运行通常比同步发送相同请求更便宜。
- 有关 OpenAI 批处理 API 文档和定价的详细信息：
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

- `memory_search` — 返回带有文件 + 行范围的片段。
- `memory_get` — 按路径读取内存文件内容。

本地模式：

- 设置 `agents.defaults.memorySearch.provider = "local"`。
- 提供 `agents.defaults.memorySearch.local.modelPath`（GGUF 或 `hf:` URI）。
- 可选：设置 `agents.defaults.memorySearch.fallback = "none"` 以避免远程回退。

### 内存工具的工作原理

- `memory_search` 语义搜索来自 `MEMORY.md` + `memory/**/*.md` 的 Markdown 块（~400 令牌目标，80 令牌重叠）。它返回片段文本（最多 ~700 字符）、文件路径、行范围、分数、提供者/模型以及是否从本地 → 远程嵌入回退。不返回完整文件负载。
- `memory_get` 读取特定的内存 Markdown 文件（工作区相对），可选地从起始行读取 N 行。`MEMORY.md` / `memory/` 之外的路径被拒绝。
- 仅当 `memorySearch.enabled` 对代理解析为真时，这两个工具才启用。

### 什么会被索引（以及何时）

- 文件类型：仅 Markdown (`MEMORY.md`，`memory/**/*.md`)。
- 索引存储：每个代理的 SQLite 在 `~/.openclaw/memory/<agentId>.sqlite`（通过 `agents.defaults.memorySearch.store.path` 配置，支持 `{agentId}` 令牌）。
- 新鲜度：`MEMORY.md` + `memory/` 的监视器标记索引为脏（防抖 1.5 秒）。同步在会话开始、搜索时或按间隔调度并异步运行。会话记录使用增量阈值触发后台同步。
- 重新索引触发器：索引存储嵌入 **提供者/模型 + 端点指纹 + 分块参数**。如果这些中的任何一个更改，OpenClaw 自动重置并重新索引整个存储。

### 混合搜索（BM25 + 向量）

启用时，OpenClaw 结合：

- **向量相似性**（语义匹配，措辞可以不同）
- **BM25 关键词相关性**（确切的令牌如 ID、环境变量、代码符号）

如果您的平台上全文搜索不可用，OpenClaw 回退到仅向量搜索。

#### 为什么混合？

向量搜索非常适合“这意味着相同的东西”：

- “Mac Studio 网关主机” vs “运行网关的机器”
- “去抖文件更新” vs “避免每次写入时索引”

但它在精确、高信号令牌上可能较弱：

- ID (`a828e60`，`b3b9895a…`)
- 代码符号 (`memorySearch.query.hybrid`)
- 错误字符串（“sqlite-vec 不可用”）

BM25（全文）正好相反：强于精确令牌，弱于同义表达。混合搜索是实用的中间地带：**同时使用两种检索信号** 因此您既能获得“自然语言”查询的良好结果，也能获得“大海捞月”查询的良好结果。

#### 我们如何合并结果（当前设计）

实现草图：

1. 从两边检索候选池：

- **向量**：按余弦相似度排名前 `maxResults * candidateMultiplier`。
- **BM25**：按 FTS5 BM25 排名前 `maxResults * candidateMultiplier`（越低越好）。

2. 将 BM25 排名转换为 0..1 似的分数：

- `textScore = 1 / (1 + max(0, bm25Rank))`

3. 通过块 ID 合并候选并计算加权分数：

- `finalScore = vectorWeight * vectorScore + textWeight * textScore`

注意：

- `vectorWeight` + `textWeight` 在配置解析时归一化为 1.0，因此权重表现为百分比。
- 如果嵌入不可用（或提供者返回零向量），我们仍然运行 BM25 并返回关键词匹配。
- 如果无法创建 FTS5，我们保持仅向量搜索（没有硬故障）。

这不是“信息检索理论完美”，但简单、快速，并且在实际笔记上往往提高召回率/精度。
如果我们以后想变得更复杂，常见的下一步是互惠秩融合（RRF）或在混合前进行评分标准化（最小/最大或 z 分数）。

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

OpenClaw 可以在 SQLite 中缓存 **块嵌入**，因此重新索引和频繁更新（尤其是会话记录）不会重新嵌入未更改的文本。

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

您可以选择索引 **会话记录** 并通过 `memory_search` 显示它们。
这受实验标志的限制。

__CODE_BLOCK_1