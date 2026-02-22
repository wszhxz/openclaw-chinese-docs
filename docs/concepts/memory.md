---
title: "Memory"
summary: "How OpenClaw memory works (workspace files + automatic memory flush)"
read_when:
  - You want the memory file layout and workflow
  - You want to tune the automatic pre-compaction memory flush
---
# 内存

OpenClaw 内存是 **代理工作区中的纯 Markdown**。文件是事实来源；模型只会“记住”写入磁盘的内容。

内存搜索工具由活动内存插件提供（默认：`memory-core`）。使用 `plugins.slots.memory = "none"` 禁用内存插件。

## 内存文件（Markdown）

默认工作区布局使用两个内存层：

- `memory/YYYY-MM-DD.md`
  - 每日日志（仅追加）。
  - 会话开始时读取今天和昨天的日志。
- `MEMORY.md`（可选）
  - 精选的长期记忆。
  - **仅在主私有会话中加载**（从不加载到群组上下文中）。

这些文件位于工作区下 (`agents.defaults.workspace`，默认 `~/.openclaw/workspace`)。有关完整布局，请参阅[代理工作区](/concepts/agent-workspace)。

## 内存工具

OpenClaw 为这些 Markdown 文件暴露了两个面向代理的工具：

- `memory_search` — 对索引片段的语义回忆。
- `memory_get` — 针对特定 Markdown 文件/行范围的目标读取。

`memory_get` 现在 **在文件不存在时优雅降级**（例如，第一次写入之前的今日日志）。内置管理器和 QMD 后端返回 `{ text: "", path }` 而不是抛出 `ENOENT`，因此代理可以处理“尚未记录”并继续其工作流程而无需将工具调用包装在 try/catch 逻辑中。

## 何时写入内存

- 决策、偏好和持久事实写入 `MEMORY.md`。
- 日常笔记和运行上下文写入 `memory/YYYY-MM-DD.md`。
- 如果有人要求“记住这个”，写下来（不要保留在 RAM 中）。
- 这个区域仍在演变。提醒模型存储记忆是有帮助的；它会知道该做什么。
- 如果希望某件事被记住，**要求机器人将其写入** 内存。

## 自动内存刷新（预压缩 ping）

当会话 **接近自动压缩** 时，OpenClaw 触发一个 **静默、代理式回合**，提醒模型在上下文压缩之前写入持久内存。默认提示明确说明模型 _可能会回复_，但通常 `NO_REPLY` 是正确的响应，因此用户不会看到这个回合。

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

- **Soft threshold**: flush triggers when the session token estimate crosses
  `contextWindow - reserveTokensFloor - softThresholdTokens`.
- **Silent** by默认: prompts include `NO_REPLY` so nothing is delivered.
- **Two prompts**: a user prompt plus a system prompt append the reminder.
- **One flush per compaction cycle** (tracked in `sessions.json`).
- **Workspace must be writable**: if the session runs sandboxed with
  `workspaceAccess: "ro"` or `"none"`, the flush is skipped.

For the full compaction lifecycle, see
[Session management + compaction](/reference/session-management-compaction).

## Vector memory search

OpenClaw can build a small vector index over `MEMORY.md` and `memory/*.md` so
semantic queries can find related notes even when wording differs.

Defaults:

- Enabled by default.
- Watches memory files for changes (debounced).
- Configure memory search under `agents.defaults.memorySearch` (not top-level
  `memorySearch`).
- Uses remote embeddings by default. If `memorySearch.provider` is not set, OpenClaw auto-selects:
  1. `local` if a `memorySearch.local.modelPath` is configured and the file exists.
  2. `openai` if an OpenAI key can be resolved.
  3. `gemini` if a Gemini key can be resolved.
  4. `voyage` if a Voyage key can be resolved.
  5. Otherwise memory search stays disabled until configured.
- Local mode uses node-llama-cpp and may require `pnpm approve-builds`.
- Uses sqlite-vec (when available) to accelerate vector search inside SQLite.

Remote embeddings **require** an API key for the embedding provider. OpenClaw
resolves keys from auth profiles, `models.providers.*.apiKey`, or environment
variables. Codex OAuth only covers chat/completions and does **not** satisfy
embeddings for memory search. For Gemini, use `GEMINI_API_KEY` or
`models.providers.google.apiKey`. For Voyage, use `VOYAGE_API_KEY` or
`models.providers.voyage.apiKey`. When using a custom OpenAI-compatible endpoint,
set `memorySearch.remote.apiKey` (and optional `memorySearch.remote.headers`).

### QMD backend (experimental)

Set `memory.backend = "qmd"` to swap the built-in SQLite indexer for
[QMD](https://github.com/tobi/qmd): a local-first search sidecar that combines
BM25 + vectors + reranking. Markdown stays the source of truth; OpenClaw shells
out to QMD for retrieval. Key points:

**Prereqs**

- 默认情况下处于禁用状态。按配置启用 (`memory.backend = "qmd"`)。
- 单独安装 QMD CLI (`bun install -g https://github.com/tobi/qmd` 或获取
  发布版本) 并确保 `qmd` 二进制文件位于网关的 `PATH`。
- QMD 需要一个允许扩展的 SQLite 构建 (`brew install sqlite` 在
  macOS 上)。
- QMD 通过 Bun + `node-llama-cpp` 完全本地运行，并在首次使用时自动从 HuggingFace 下载 GGUF
  模型（无需单独的 Ollama 守护进程）。
- 网关通过设置 `XDG_CONFIG_HOME` 和
  `XDG_CACHE_HOME` 在 `~/.openclaw/agents/<agentId>/qmd/` 下运行自包含的 XDG 主目录中的 QMD。
- 操作系统支持：安装 Bun + SQLite 后，macOS 和 Linux 可直接使用。Windows 最佳支持方式为通过 WSL2。

**侧车的运行方式**

- 网关在 `~/.openclaw/agents/<agentId>/qmd/` 下写入自包含的 QMD 主目录（配置 + 缓存 + sqlite 数据库）。
- 通过 `qmd collection add` 从 `memory.qmd.paths`
  创建集合（加上默认工作区内存文件），然后在启动时和可配置的时间间隔 (`memory.qmd.update.interval`，
  默认 5 分钟) 运行 `qmd update` + `qmd embed`。
- 网关现在在启动时初始化 QMD 管理器，因此即使在第一次 `memory_search` 调用之前也会启动定期更新计时器。
- 启动刷新现在默认在后台运行，因此不会阻塞聊天启动；设置 `memory.qmd.update.waitForBootSync = true` 以保留之前的
  阻塞行为。
- 搜索通过 `memory.qmd.searchMode` 进行（默认 `qmd search --json`；也支持 `vsearch` 和 `query`）。如果选定模式拒绝了您的 QMD 构建中的标志，OpenClaw 将重试使用 `qmd query`。如果 QMD 失败或二进制文件丢失，OpenClaw 会自动回退到内置的 SQLite 管理器，以便内存工具继续工作。
- OpenClaw 目前不暴露 QMD 嵌入批处理大小调优；批处理行为由 QMD 自身控制。
- **首次搜索可能较慢**：QMD 可能在首次 `qmd query` 运行时下载本地 GGUF 模型（重新排序/查询
  扩展）。
  - OpenClaw 在运行 QMD 时自动设置 `XDG_CONFIG_HOME`/`XDG_CACHE_HOME`。
  - 如果您希望手动预下载模型（并预热 OpenClaw 使用的相同索引），使用代理的 XDG 目录运行一次查询。

    OpenClaw 的 QMD 状态存储在您的 **状态目录** 下（默认为 `~/.openclaw`）。
    您可以通过导出 OpenClaw 使用的相同 XDG 变量来指向完全相同的索引 `qmd`：

    ```bash
    # Pick the same state dir OpenClaw uses
    STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"

    export XDG_CONFIG_HOME="$STATE_DIR/agents/main/qmd/xdg-config"
    export XDG_CACHE_HOME="$STATE_DIR/agents/main/qmd/xdg-cache"

    # (Optional) force an index refresh + embeddings
    qmd update
    qmd embed

    # Warm up / trigger first-time model downloads
    qmd query "test" -c memory-root --json >/dev/null 2>&1
    ```

**配置界面 (`memory.qmd.*`)**

- `command` (默认 `qmd`): 覆盖可执行文件路径。
- `searchMode` (默认 `search`): 选择哪个QMD命令支持
  `memory_search` (`search`, `vsearch`, `query`)。
- `includeDefaultMemory` (默认 `true`): 自动索引 `MEMORY.md` + `memory/**/*.md`。
- `paths[]`: 添加额外的目录/文件 (`path`, 可选 `pattern`, 可选
  稳定 `name`)。
- `sessions`: 启用会话JSONL索引 (`enabled`, `retentionDays`,
  `exportDir`)。
- `update`: 控制刷新频率和维护执行:
  (`interval`, `debounceMs`, `onBoot`, `waitForBootSync`, `embedInterval`,
  `commandTimeoutMs`, `updateTimeoutMs`, `embedTimeoutMs`)。
- `limits`: 限制召回负载 (`maxResults`, `maxSnippetChars`,
  `maxInjectedChars`, `timeoutMs`)。
- `scope`: 与[`session.sendPolicy`](/gateway/configuration#session)相同的架构。
  默认仅限DM (`deny` 全部, `allow` 直接聊天); 放宽松以在群组/频道中显示QMD命中。
  - `match.keyPrefix` 匹配 **规范化** 的会话密钥（小写，去除任何前导 `agent:<id>:`）。示例: `discord:channel:`。
  - `match.rawKeyPrefix` 匹配 **原始** 的会话密钥（小写），包括
    `agent:<id>:`。示例: `agent:main:discord:`。
  - 遗留: `match.keyPrefix: "agent:..."` 仍然被视为原始密钥前缀，
    但建议使用 `rawKeyPrefix` 以提高清晰度。
- 当 `scope` 拒绝搜索时，OpenClaw会记录一个警告，包含派生的
  `channel`/`chatType`，以便更容易调试空结果。
- 来自工作区外的代码片段在 `memory_search` 结果中显示为
  `qmd/<collection>/<relative-path>`；`memory_get`
  理解该前缀并从配置的QMD集合根读取。
- 当 `memory.qmd.sessions.enabled = true`，OpenClaw导出清理后的会话
  对话记录（用户/助手轮次）到 `~/.openclaw/agents/<id>/qmd/sessions/` 下的专用QMD集合，
  因此 `memory_search` 可以回忆最近的对话而不触及内置的SQLite索引。
- `memory_search` 代码片段现在在 `memory.citations` 是 `auto`/`on` 时包含一个 `Source: <path#line>` 页脚；设置 `memory.citations = "off"` 以保持路径元数据内部（代理仍然接收路径用于
  `memory_get`，但代码片段文本省略页脚且系统提示代理不要引用它）。

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
      rules: [
        { action: "allow", match: { chatType: "direct" } },
        // Normalized session-key prefix (strips `agent:<id>:`).
        { action: "deny", match: { keyPrefix: "discord:channel:" } },
        // Raw session-key prefix (includes `agent:<id>:`).
        { action: "deny", match: { rawKeyPrefix: "agent:main:discord:" } },
      ]
    },
    paths: [
      { name: "docs", path: "~/notes", pattern: "**/*.md" }
    ]
  }
}
```

**引用及回退**

- `memory.citations` 适用于任何后端 (`auto`/`on`/`off`)。
- 当 `qmd` 运行时，我们标记 `status().backend = "qmd"` 以便诊断信息显示哪个引擎提供了结果。如果 QMD 子进程退出或无法解析 JSON 输出，搜索管理器会记录警告并返回内置提供程序（现有的 Markdown 嵌入），直到 QMD 恢复。

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

- `remote.baseUrl` 是可选的（默认为 Gemini API 的基本 URL）。
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

如果您不想设置 API 密钥，请使用 `memorySearch.provider = "local"` 或设置 `memorySearch.fallback = "none"`。

回退选项：

- `memorySearch.fallback` 可以是 `openai`、`gemini`、`local` 或 `none`。
- 回退提供程序仅在主要嵌入提供程序失败时使用。

批量索引（OpenAI + Gemini + Voyage）：

- 默认情况下处于禁用状态。设置 `agents.defaults.memorySearch.remote.batch.enabled = true` 以启用大语料库索引（OpenAI, Gemini 和 Voyage）。
- 默认行为是等待批处理完成；如果需要，可以调整 `remote.batch.wait`、`remote.batch.pollIntervalMs` 和 `remote.batch.timeoutMinutes`。
- 设置 `remote.batch.concurrency` 以控制我们并行提交多少批处理作业（默认：2）。
- 批处理模式适用于 `memorySearch.provider = "openai"` 或 `"gemini"` 并使用相应的 API 密钥。
- Gemini 批处理作业使用异步嵌入批处理端点，并且需要 Gemini Batch API 的可用性。

为什么 OpenAI 批处理速度快且便宜：

- 对于大型回填，OpenAI 通常是我们的最快选项，因为我们可以在单个批处理作业中提交许多嵌入请求，并让 OpenAI 异步处理它们。
- OpenAI 为批处理 API 工作负载提供折扣定价，因此大型索引运行通常比同步发送相同请求更便宜。
- 有关详细信息，请参阅 OpenAI 批处理 API 文档和定价：
  - [https://platform.openai.com/docs/api-reference/batch](https://platform.openai.com/docs/api-reference/batch)
  - [https://platform.openai.com/pricing](https://platform.openai.com/pricing)

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
- 提供 `agents.defaults.memorySearch.local.modelPath`（GGUF 或 `hf:` URI）。
- 可选：设置 `agents.defaults.memorySearch.fallback = "none"` 以避免远程回退。

### 内存工具的工作原理

- `memory_search` 从 `MEMORY.md` + `memory/**/*.md` 中对 Markdown 块（~400 令牌目标，80 令牌重叠）进行语义搜索。它返回代码片段文本（最多 ~700 字符）、文件路径、行范围、分数、提供商/模型以及我们是否从本地 → 远程嵌入进行了回退。不返回完整文件内容。
- `memory_get` 读取特定的内存 Markdown 文件（相对于工作区），可选地从起始行开始并读取 N 行。`MEMORY.md` / `memory/` 之外的路径会被拒绝。
- 仅当 `memorySearch.enabled` 对代理解析为真时，这两个工具才被启用。

### 索引的内容（以及何时）

- 文件类型: 仅Markdown (`MEMORY.md`, `memory/**/*.md`).
- 索引存储: 每个代理的SQLite数据库位于 `~/.openclaw/memory/<agentId>.sqlite` (可通过 `agents.defaults.memorySearch.store.path` 配置，支持 `{agentId}` 令牌).
- 新鲜度: 监视器在 `MEMORY.md` + `memory/` 标记索引为脏（防抖1.5秒）。同步在会话开始、搜索时或按间隔进行，并异步运行。会话记录使用增量阈值触发后台同步。
- 重新索引触发器: 索引存储嵌入式 **提供程序/模型 + 终端指纹 + 分块参数**。如果这些中的任何一个发生变化，OpenClaw会自动重置并重新索引整个存储。

### 混合搜索（BM25 + 向量）

启用时，OpenClaw结合：

- **向量相似性**（语义匹配，词序可以不同）
- **BM25关键词相关性**（精确的标记如ID、环境变量、代码符号）

如果您的平台上全文搜索不可用，OpenClaw将回退到仅向量搜索。

#### 为什么使用混合搜索？

向量搜索擅长“意思相同”的情况：

- “Mac Studio网关主机” vs “运行网关的机器”
- “防抖文件更新” vs “避免每次写入时索引”

但它在精确、高信号标记上可能较弱：

- ID (`a828e60`, `b3b9895a…`)
- 代码符号 (`memorySearch.query.hybrid`)
- 错误字符串 ("sqlite-vec 不可用")

BM25（全文）则相反：擅长精确标记，对同义句较弱。
混合搜索是实用的折衷方案：**同时使用两种检索信号**，因此您可以获得对“自然语言”查询和“大海捞月”查询的良好结果。

#### 我们如何合并结果（当前设计）

实现概要：

1. 从两方面检索候选池：

- **向量**: 通过余弦相似性获取前 `maxResults * candidateMultiplier` 项。
- **BM25**: 通过FTS5 BM25排名获取前 `maxResults * candidateMultiplier` 项（数值越低越好）。

2. 将BM25排名转换为0..1左右的分数：

- `textScore = 1 / (1 + max(0, bm25Rank))`

3. 通过块ID合并候选者并计算加权分数：

- `finalScore = vectorWeight * vectorScore + textWeight * textScore`

注意：

- `vectorWeight` + `textWeight` 在配置解析中归一化为1.0，因此权重表现为百分比。
- 如果嵌入式不可用（或提供程序返回零向量），我们仍然运行BM25并返回关键词匹配。
- 如果无法创建FTS5，我们将保持仅向量搜索（不会硬失败）。

这并不是“信息检索理论完美”，但它是简单、快速的，并且通常能提高实际笔记的召回率/精度。
如果我们以后想变得更复杂，常见的下一步是互惠排名融合（RRF）或得分标准化（最小/最大或z分数）之前混合。

#### 后处理管道

在合并向量和关键词得分之后，两个可选的后处理阶段
在结果列表到达代理之前对其进行细化：

```
Vector + Keyword → Weighted Merge → Temporal Decay → Sort → MMR → Top-K Results
```

这两个阶段默认是**关闭的**，可以独立启用。

#### MMR 重新排序（多样性）

当混合搜索返回结果时，多个片段可能包含相似或重叠的内容。
例如，搜索“home network setup”可能会返回五个几乎相同的片段，
这些片段都提到了相同的路由器配置。

**MMR（最大边缘相关性）** 重新排序结果以平衡相关性和多样性，
确保排名靠前的结果涵盖查询的不同方面而不是重复相同的信息。

工作原理：

1. 结果根据其原始相关性进行评分（向量 + BM25 加权分数）。
2. MMR 迭代选择最大化：`λ × relevance − (1−λ) × max_similarity_to_selected` 的结果。
3. 结果之间的相似性使用分词内容的 Jaccard 文本相似性来衡量。

`lambda` 参数控制权衡：

- `lambda = 1.0` → 纯相关性（无多样性惩罚）
- `lambda = 0.0` → 最大多样性（忽略相关性）
- 默认：`0.7`（平衡，轻微的相关性偏差）

**示例 — 查询：“home network setup”**

给定这些记忆文件：

```
memory/2026-02-10.md  → "Configured Omada router, set VLAN 10 for IoT devices"
memory/2026-02-08.md  → "Configured Omada router, moved IoT to VLAN 10"
memory/2026-02-05.md  → "Set up AdGuard DNS on 192.168.10.2"
memory/network.md     → "Router: Omada ER605, AdGuard: 192.168.10.2, VLAN 10: IoT"
```

不使用 MMR — 前 3 个结果：

```
1. memory/2026-02-10.md  (score: 0.92)  ← router + VLAN
2. memory/2026-02-08.md  (score: 0.89)  ← router + VLAN (near-duplicate!)
3. memory/network.md     (score: 0.85)  ← reference doc
```

使用 MMR（λ=0.7）— 前 3 个结果：

```
1. memory/2026-02-10.md  (score: 0.92)  ← router + VLAN
2. memory/network.md     (score: 0.85)  ← reference doc (diverse!)
3. memory/2026-02-05.md  (score: 0.78)  ← AdGuard DNS (diverse!)
```

2 月 8 日的近似重复项被排除在外，代理获得了三个不同的信息片段。

**何时启用：** 如果您注意到 `memory_search` 返回冗余或近似重复的片段，
特别是日常笔记中经常在几天内重复类似的信息。

#### 时间衰减（最新优先）

带有日常笔记的代理会随着时间积累数百个日期文件。如果没有衰减，
六个月前措辞良好的笔记可能会排在昨天同一主题更新之前。

**时间衰减** 根据每个结果的年龄对分数应用指数乘数，
因此最近的记忆自然排名更高而旧的记忆逐渐淡化：

```
decayedScore = score × e^(-λ × ageInDays)
```

其中 `λ = ln(2) / halfLifeDays`。

默认半衰期为 30 天：

- 今天的笔记：**100%** 的原始分数
- 7 天前：**~84%**
- 30 天前：**50%**
- 90 天前：**12.5%**
- 180 天前：**~1.6%**

**永恒文件永远不会衰减：**

- `MEMORY.md`（根记忆文件）
- `memory/` 中的非日期文件（例如，`memory/projects.md`，`memory/network.md`）
- 这些包含应始终正常排名的持久参考信息。

**按日期命名的文件** (`memory/YYYY-MM-DD.md`) 使用从文件名中提取的日期。
其他来源（例如，会话记录）则回退到文件修改时间 (`mtime`)。

**示例 — 查询: "Rod的工作日程是什么？"**

给定这些记忆文件（今天是2月10日）：

```
memory/2025-09-15.md  → "Rod works Mon-Fri, standup at 10am, pairing at 2pm"  (148 days old)
memory/2026-02-10.md  → "Rod has standup at 14:15, 1:1 with Zeb at 14:45"    (today)
memory/2026-02-03.md  → "Rod started new team, standup moved to 14:15"        (7 days old)
```

不衰减：

```
1. memory/2025-09-15.md  (score: 0.91)  ← best semantic match, but stale!
2. memory/2026-02-10.md  (score: 0.82)
3. memory/2026-02-03.md  (score: 0.80)
```

使用衰减（halfLife=30）：

```
1. memory/2026-02-10.md  (score: 0.82 × 1.00 = 0.82)  ← today, no decay
2. memory/2026-02-03.md  (score: 0.80 × 0.85 = 0.68)  ← 7 days, mild decay
3. memory/2025-09-15.md  (score: 0.91 × 0.03 = 0.03)  ← 148 days, nearly gone
```

尽管有最佳的原始语义匹配，但九月的过时笔记降到了底部。

**何时启用：** 如果您的代理有数月的每日笔记，并且发现旧的、过时的信息比近期上下文排名更高。30天的半衰期适用于以每日笔记为主的流程；如果经常引用较旧的笔记，则可以增加它（例如，90天）。

#### 配置

这两个功能都在 `memorySearch.query.hybrid` 下进行配置：

```json5
agents: {
  defaults: {
    memorySearch: {
      query: {
        hybrid: {
          enabled: true,
          vectorWeight: 0.7,
          textWeight: 0.3,
          candidateMultiplier: 4,
          // Diversity: reduce redundant results
          mmr: {
            enabled: true,    // default: false
            lambda: 0.7       // 0 = max diversity, 1 = max relevance
          },
          // Recency: boost newer memories
          temporalDecay: {
            enabled: true,    // default: false
            halfLifeDays: 30  // score halves every 30 days
          }
        }
      }
    }
  }
}
```

您可以独立启用任一功能：

- **仅MMR** — 在您有许多相似笔记但年龄无关紧要时有用。
- **仅时间衰减** — 在最近性很重要但结果已经多样化时有用。
- **两者** — 推荐用于具有大量、长期运行的每日笔记历史的代理。

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

### 会话记忆搜索（实验性）

您可以选择性地索引 **会话记录** 并通过 `memory_search` 展示它们。
此功能受实验性标志保护。

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

- 会话索引是**可选**的（默认关闭）。
- 会话更新会被防抖处理，并且在超过delta阈值时**异步索引**（尽力而为）。
- `memory_search` 永远不会阻塞索引；结果可能在后台同步完成之前稍微过时。
- 结果仍然只包括代码片段；`memory_get` 仅限于内存文件。
- 会话索引按代理隔离（只有该代理的会话日志会被索引）。
- 会话日志存储在磁盘上 (`~/.openclaw/agents/<agentId>/sessions/*.jsonl`)。任何具有文件系统访问权限的进程/用户都可以读取它们，因此将磁盘访问视为信任边界。为了更严格的隔离，请在单独的操作系统用户或主机下运行代理。

Delta阈值（默认值显示如下）：

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

### SQLite向量加速 (sqlite-vec)

当可用时，OpenClaw使用sqlite-vec扩展将嵌入存储在一个
SQLite虚拟表 (`vec0`) 中，并在数据库中执行向量距离查询。
这使得搜索速度加快，而无需将每个嵌入加载到JS中。

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

- `enabled` 默认为true；当禁用时，搜索将回退到对存储的嵌入进行进程内的余弦相似度计算。
- 如果缺少sqlite-vec扩展或无法加载，OpenClaw会记录错误并继续使用JS回退（没有向量表）。
- `extensionPath` 覆盖捆绑的sqlite-vec路径（适用于自定义构建或非标准安装位置）。

### 本地嵌入自动下载

- 默认本地嵌入模型：`hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf` （约0.6 GB）。
- 当 `memorySearch.provider = "local"` 时，`node-llama-cpp` 解析 `modelPath`；如果缺少GGUF，则会**自动下载**到缓存（或 `local.modelCacheDir` 如果已设置），然后加载它。重试时会恢复下载。
- 原生构建要求：运行 `pnpm approve-builds`，选择 `node-llama-cpp`，然后 `pnpm rebuild node-llama-cpp`。
- 回退：如果本地设置失败且 `memorySearch.fallback = "openai"`，我们将自动切换到远程嵌入 (`openai/text-embedding-3-small` 除非被覆盖)，并记录原因。

### 自定义OpenAI兼容端点示例

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

- `remote.*` 的优先级高于 `models.providers.openai.*`。
- `remote.headers` 与 OpenAI 标头合并；在键冲突的情况下远程优先。省略 `remote.headers` 以使用 OpenAI 默认值。