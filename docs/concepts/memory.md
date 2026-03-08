---
title: "Memory"
summary: "How OpenClaw memory works (workspace files + automatic memory flush)"
read_when:
  - You want the memory file layout and workflow
  - You want to tune the automatic pre-compaction memory flush
---
# 记忆

OpenClaw 记忆是 **代理工作区中的纯 Markdown**。文件是事实来源；模型只“记住”写入磁盘的内容。

记忆搜索工具由活动的记忆插件提供（默认：`memory-core`）。使用 `plugins.slots.memory = "none"` 禁用记忆插件。

## 记忆文件 (Markdown)

默认工作区布局使用两个记忆层：

- `memory/YYYY-MM-DD.md`
  - 每日日志（仅追加）。
  - 会话开始时读取今天 + 昨天的内容。
- `MEMORY.md`（可选）
  - 精选的长期记忆。
  - **仅在主私有会话中加载**（绝不在群组上下文中）。

这些文件位于工作区下（`agents.defaults.workspace`，默认 `~/.openclaw/workspace`）。参见 [代理工作区](/concepts/agent-workspace) 了解完整布局。

## 记忆工具

OpenClaw 为这些 Markdown 文件公开了两个面向代理的工具：

- `memory_search` — 对索引片段的语义回忆。
- `memory_get` — 针对特定 Markdown 文件/行范围的读取。

`memory_get` 现在 **在文件不存在时优雅降级**（例如，首次写入前的今日每日日志）。内置管理器和 QMD 后端都返回 `{ text: "", path }` 而不是抛出 `ENOENT`，因此代理可以处理“尚未记录任何内容”的情况，并继续其工作流，而无需将工具调用包裹在 try/catch 逻辑中。

## 何时写入记忆

- 决策、偏好和持久事实写入 `MEMORY.md`。
- 日常笔记和运行上下文写入 `memory/YYYY-MM-DD.md`。
- 如果有人说“记住这个”，把它写下来（不要保存在 RAM 中）。
- 这个领域仍在发展中。有助于提醒模型存储记忆；它会知道该做什么。
- 如果你想让某些内容持久化，**要求机器人将其写入** 记忆。

## 自动记忆刷新（压缩前 ping）

当会话 **接近自动压缩** 时，OpenClaw 触发一个 **静默的代理轮次**，提醒模型在上下文被压缩 **之前** 写入持久记忆。默认提示明确说明模型 _可以回复_，但通常 `NO_REPLY` 是正确的响应，因此用户永远不会看到此轮次。

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

详情：

- **软阈值**：当会话 token 估计值超过 `contextWindow - reserveTokensFloor - softThresholdTokens` 时触发刷新。
- 默认 **静默**：提示包含 `NO_REPLY`，因此不会传递任何内容。
- **两个提示**：一个用户提示加上一个系统提示附加提醒。
- **每个压缩周期一次刷新**（在 `sessions.json` 中跟踪）。
- **工作区必须可写**：如果会话在 `workspaceAccess: "ro"` 或 `"none"` 下沙箱运行，则跳过刷新。

有关完整的压缩生命周期，参见 [会话管理 + 压缩](/reference/session-management-compaction)。

## 向量记忆搜索

OpenClaw 可以在 `MEMORY.md` 和 `memory/*.md` 上构建小型向量索引，因此即使措辞不同，语义查询也能找到相关笔记。

默认值：

- 默认启用。
- 监视记忆文件的变化（防抖）。
- 在 `agents.defaults.memorySearch` 下配置记忆搜索（而不是顶层 `memorySearch`）。
- 默认使用远程 embeddings。如果未设置 `memorySearch.provider`，OpenClaw 自动选择：
  1. 如果配置了 `memorySearch.local.modelPath` 且文件存在，则使用 `local`。
  2. 如果可以解析 OpenAI key，则使用 `openai`。
  3. 如果可以解析 Gemini key，则使用 `gemini`。
  4. 如果可以解析 Voyage key，则使用 `voyage`。
  5. 如果可以解析 Mistral key，则使用 `mistral`。
  6. 否则记忆搜索保持禁用状态直到配置完成。
- 本地模式使用 node-llama-cpp 并可能需要 `pnpm approve-builds`。
- 使用 sqlite-vec（可用时）加速 SQLite 内部的向量搜索。
- `memorySearch.provider = "ollama"` 也支持本地/自托管 Ollama embeddings (`/api/embeddings`)，但不会自动选择。

远程 embeddings **需要** embedding 提供商的 API key。OpenClaw 从 auth profiles、`models.providers.*.apiKey` 或环境变量解析 keys。Codex OAuth 仅涵盖 chat/completions，**不** 满足记忆搜索的 embeddings 需求。对于 Gemini，使用 `GEMINI_API_KEY` 或 `models.providers.google.apiKey`。对于 Voyage，使用 `VOYAGE_API_KEY` 或 `models.providers.voyage.apiKey`。对于 Mistral，使用 `MISTRAL_API_KEY` 或 `models.providers.mistral.apiKey`。Ollama 通常不需要真实的 API key（当本地策略需要时，像 `OLLAMA_API_KEY=ollama-local` 这样的占位符就足够了）。使用自定义 OpenAI-compatible endpoint 时，设置 `memorySearch.remote.apiKey`（以及可选的 `memorySearch.remote.headers`）。

### QMD 后端（实验性）

设置 `memory.backend = "qmd"` 将内置 SQLite indexer 替换为 [QMD](https://github.com/tobi/qmd)：一个结合 BM25 + vectors + reranking 的 local-first 搜索 sidecar。Markdown 保持为事实来源；OpenClaw 调用 QMD 进行检索。关键点：

**前提条件**

- 默认禁用。每个配置单独启用 (`memory.backend = "qmd"`)。
- 单独安装 QMD CLI (`bun install -g https://github.com/tobi/qmd` 或获取 release)，并确保 `qmd` 二进制文件在网关的 `PATH` 上。
- QMD 需要允许 extensions 的 SQLite 构建（macOS 上的 `brew install sqlite`）。
- QMD 通过 Bun + `node-llama-cpp` 完全本地运行，并在首次使用时从 HuggingFace 自动下载 GGUF 模型（不需要单独的 Ollama daemon）。
- 网关通过设置 `XDG_CONFIG_HOME` 和 `XDG_CACHE_HOME` 在 `~/.openclaw/agents/<agentId>/qmd/` 下的自包含 XDG home 中运行 QMD。
- 操作系统支持：安装 Bun + SQLite 后，macOS 和 Linux 即可开箱即用。Windows 最好通过 WSL2 支持。

**sidecar 如何运行**

- 网关在 `~/.openclaw/agents/<agentId>/qmd/` 下写入一个自包含的 QMD home（config + cache + sqlite DB）。
- Collections 通过 `qmd collection add` 从 `memory.qmd.paths` 创建（加上默认工作区记忆文件），然后 `qmd update` + `qmd embed` 在启动时和可配置的时间间隔 (`memory.qmd.update.interval`，默认 5 m) 运行。
- 网关现在在启动时初始化 QMD 管理器，因此即使在第一次 `memory_search` 调用之前，定期更新计时器也已就绪。
- 启动刷新现在默认在后台运行，因此不会阻塞聊天启动；设置 `memory.qmd.update.waitForBootSync = true` 以保持之前的阻塞行为。
- 搜索通过 `memory.qmd.searchMode` 运行（默认 `qmd search --json`；也支持 `vsearch` 和 `query`）。如果所选模式拒绝您的 QMD 构建上的 flags，OpenClaw 会使用 `qmd query` 重试。如果 QMD 失败或二进制文件缺失，OpenClaw 会自动回退到内置 SQLite 管理器，因此记忆工具可以继续工作。
- OpenClaw 目前不公开 QMD embed batch-size 调整；batch 行为由 QMD 本身控制。
- **首次搜索可能较慢**：QMD 可能在第一次 `qmd query` 运行时下载本地 GGUF 模型（reranker/query expansion）。
  - OpenClaw 在运行 QMD 时自动设置 `XDG_CONFIG_HOME`/`XDG_CACHE_HOME`。
  - 如果您想手动预下载模型（并预热 OpenClaw 使用的相同索引），请使用代理的 XDG dirs 运行一次性查询。

    OpenClaw 的 QMD 状态位于您的 **state dir** 下（默认 `~/.openclaw`）。您可以通过导出 OpenClaw 使用的相同 XDG vars 将 `qmd` 指向完全相同的索引：

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

- ``command``（默认 ``qmd``）：覆盖可执行文件路径。
- ``searchMode``（默认 ``search``）：选择哪个 QMD 命令支持 ``memory_search``（``search``、``vsearch``、``query``）。
- ``includeDefaultMemory``（默认 ``true``）：自动索引 ``MEMORY.md`` + ``memory/**/*.md``。
- ``paths[]``：添加额外目录/文件（``path``，可选 ``pattern``，可选稳定版 ``name``）。
- ``sessions``：选择加入会话 JSONL 索引（``enabled``、``retentionDays``、``exportDir``）。
- ``update``：控制刷新频率和维护执行：（``interval``、``debounceMs``、``onBoot``、``waitForBootSync``、``embedInterval``、``commandTimeoutMs``、``updateTimeoutMs``、``embedTimeoutMs``）。
- ``limits``：限制召回负载（``maxResults``、``maxSnippetChars``、``maxInjectedChars``、``timeoutMs``）。
- ``scope``：与 [``session.sendPolicy``](/gateway/configuration#session) 具有相同的架构。默认为仅 DM（``deny`` 全部，``allow`` 直接聊天）；放宽它以在群组/频道中显示 QMD 命中结果。
  - ``match.keyPrefix`` 匹配 **标准化** 后的会话键（小写化，并移除任何前导 ``agent:<id>:``）。示例：``discord:channel:``。
  - ``match.rawKeyPrefix`` 匹配 **原始** 会话键（小写化），包括 ``agent:<id>:``。示例：``agent:main:discord:``。
  - 遗留：``match.keyPrefix: "agent:..."`` 仍被视为原始键前缀，但为了清晰起见，建议使用 ``rawKeyPrefix``。
- 当 ``scope`` 拒绝搜索时，OpenClaw 会记录一条包含派生的 ``channel`/`chatType`` 的警告，以便更容易调试空结果。
- 源自工作区之外的片段在 ``memory_search`` 结果中显示为 ``qmd/<collection>/<relative-path>``；``memory_get`` 理解该前缀并从配置的 QMD 集合根目录读取。
- 当 ``memory.qmd.sessions.enabled = true`` 时，OpenClaw 将清理后的会话转录本（用户/助手回合）导出到 ``~/.openclaw/agents/<id>/qmd/sessions/`` 下的专用 QMD 集合中，以便 ``memory_search`` 可以回忆最近的对话，而无需触碰内置 SQLite 索引。
- ``memory_search`` 片段现在包含一个 ``Source: <path#line>`` 页脚，当 ``memory.citations`` 为 ``auto`/`on`` 时；设置 ``memory.citations = "off"`` 以保持路径元数据内部化（代理仍然接收用于 ``memory_get`` 的路径，但片段文本省略了页脚，且系统提示警告代理不要引用它）。

**示例**

````json5
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
````

**引用与回退**

- 无论后端如何（``auto`/`on`/`off``），``memory.citations`` 均适用。
- 当 ``qmd`` 运行时，我们标记 ``status().backend = "qmd"``，以便诊断工具显示哪个引擎提供了结果。如果 QMD 子进程退出或无法解析 JSON 输出，搜索管理器会记录警告并返回内置提供者（现有的 Markdown 嵌入），直到 QMD 恢复。

### 额外的内存路径

如果您想索引默认工作区布局之外的 Markdown 文件，请添加显式路径：

````json5
agents: {
  defaults: {
    memorySearch: {
      extraPaths: ["../team-docs", "/srv/shared-notes/overview.md"]
    }
  }
}
````

注意：

- 路径可以是绝对路径或相对于工作区的。
- 目录会递归扫描 ``.md`` 文件。
- 仅索引 Markdown 文件。
- 符号链接被忽略（文件或目录）。

### Gemini 嵌入（原生）

将提供者设置为 ``gemini`` 以直接使用 Gemini 嵌入 API：

````json5
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
````

注意：

- ``remote.baseUrl`` 是可选的（默认为 Gemini API 基础 URL）。
- 如果需要，``remote.headers`` 允许您添加额外的标头。
- 默认模型：``gemini-embedding-001``。

如果您想使用 **自定义 OpenAI 兼容端点**（OpenRouter、vLLM 或代理），您可以使用带有 OpenAI 提供者的 ``remote`` 配置：

````json5
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
````

如果您不想设置 API 密钥，请使用 ``memorySearch.provider = "local"`` 或设置 ``memorySearch.fallback = "none"``。

回退方案：

- ``memorySearch.fallback`` 可以是 ``openai``、``gemini``、``voyage``、``mistral``、``ollama``、``local`` 或 ``none``。
- 仅在主要嵌入提供者失败时才使用回退提供者。

批量索引（OpenAI + Gemini + Voyage）：

- 默认禁用。设置 ``agents.defaults.memorySearch.remote.batch.enabled = true`` 以启用大型语料库索引（OpenAI、Gemini 和 Voyage）。
- 默认行为等待批处理完成；如有需要，调整 ``remote.batch.wait``、``remote.batch.pollIntervalMs`` 和 ``remote.batch.timeoutMinutes``。
- 设置 ``remote.batch.concurrency`` 以控制我们并行提交多少批处理作业（默认值：2）。
- 当 ``memorySearch.provider = "openai"`` 或 ``"gemini"`` 时应用批处理模式，并使用相应的 API 密钥。
- Gemini 批处理作业使用异步嵌入批处理端点，并且需要 Gemini Batch API 可用。

为什么 OpenAI 批处理快速且便宜：

- 对于大量回填，OpenAI 通常是我们支持的最快选项，因为我们可以在单个批处理作业中提交许多嵌入请求，并让 OpenAI 异步处理它们。
- OpenAI 为 Batch API 工作负载提供折扣定价，因此大型索引运行通常比同步发送相同请求更便宜。
- 有关详细信息，请参阅 OpenAI Batch API 文档和定价：
  - [https://platform.openai.com/docs/api-reference/batch](https://platform.openai.com/docs/api-reference/batch)
  - [https://platform.openai.com/pricing](https://platform.openai.com/pricing)

配置示例：

````json5
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
````

工具：

- ``memory_search`` — 返回带有文件 + 行范围的片段。
- ``memory_get`` — 按路径读取内存文件内容。

本地模式：

- 设置 ``agents.defaults.memorySearch.provider = "local"``。
- 提供 ``agents.defaults.memorySearch.local.modelPath``（GGUF 或 ``hf:`` URI）。
- 可选：设置 ``agents.defaults.memorySearch.fallback = "none"`` 以避免远程回退。

### 内存工具的工作原理

- ``memory_search`` 从 ``MEMORY.md`` + ``memory/**/*.md`` 语义搜索 Markdown 块（~400 token 目标，80-token 重叠）。它返回片段文本（上限约 700 字符）、文件路径、行范围、分数、提供者/模型，以及我们是否从本地 → 远程嵌入进行了回退。不返回完整文件负载。
- ``memory_get`` 读取特定的内存 Markdown 文件（相对于工作区），可选择从起始行开始并读取 N 行。超出 ``MEMORY.md`` / ``memory/`` 的路径将被拒绝。
- 仅当 ``memorySearch.enabled`` 对代理解析为 true 时，这两个工具才启用。

### 什么会被索引（以及何时）

- 文件类型：仅限 Markdown（``MEMORY.md``、``memory/**/*.md``）。
- 索引存储：每个代理的 SQLite 位于 ``~/.openclaw/memory/<agentId>.sqlite``（可通过 ``agents.defaults.memorySearch.store.path`` 配置，支持 ``{agentId}`` 令牌）。
- 新鲜度：``MEMORY.md`` + ``memory/`` 上的监视器标记索引为脏（去抖动 1.5 秒）。同步计划在会话开始时、搜索时或按间隔进行，并异步运行。会话转录本使用 delta 阈值触发后台同步。
- 重新索引触发器：索引存储嵌入 **提供者/模型 + 端点指纹 + 分块参数**。如果其中任何一项发生变化，OpenClaw 将自动重置并重新索引整个存储。

### 混合搜索（BM25 + 向量）

启用时，OpenClaw 结合：

- **向量相似度**（语义匹配，措辞可能不同）
- **BM25 关键词相关性**（精确令牌，如 ID、环境变量、代码符号）

如果您的平台上不可用全文搜索，OpenClaw 将回退到仅向量搜索。

#### 为什么是混合？

向量搜索擅长“这意味着同一件事”：

- “Mac Studio 网关主机”vs“运行网关的机器”
- “防抖文件更新”vs“避免每次写入时索引”

但在精确的高信号令牌方面可能较弱：

- ID（``a828e60``、``b3b9895a…``）
- 代码符号（``memorySearch.query.hybrid``）
- 错误字符串（"sqlite-vec unavailable"）

BM25（全文）则相反：在精确令牌方面很强，在改写方面较弱。
混合搜索是务实的中间立场：**同时使用两种检索信号**，以便您在“自然语言”查询和“大海捞针”查询中获得良好的结果。

#### 我们如何合并结果（当前设计）

实现概要：

1. 从两侧检索候选池：

- **向量**：按余弦相似度排名前 ``maxResults * candidateMultiplier``。
- **BM25**：按 FTS5 BM25 排名排名前 ``maxResults * candidateMultiplier``（越低越好）。

2. 将 BM25 排名转换为 0..1 左右的分数：

- ``textScore = 1 / (1 + max(0, bm25Rank))``

3. 按块 ID 合并候选项并计算加权分数：

- ``finalScore = vectorWeight * vectorScore + textWeight * textScore``

注意：

- `vectorWeight` + `textWeight` 在配置解析中被归一化为 1.0，因此权重表现为百分比。
- 如果嵌入不可用（或提供商返回零向量），我们仍然运行 BM25 并返回关键词匹配。
- 如果无法创建 FTS5，我们保留仅向量搜索（不会硬性失败）。

这并非"IR-theory perfect"，但它简单、快速，并且倾向于提高实际笔记的召回率/精确率。
如果我们以后想要更复杂，常见的下一步是在混合之前使用 Reciprocal Rank Fusion (RRF) 或分数归一化（min/max 或 z-score）。

#### 后处理管道

在合并向量和关键词分数后，两个可选的后处理阶段会在结果列表到达代理之前对其进行优化：

```
Vector + Keyword → Weighted Merge → Temporal Decay → Sort → MMR → Top-K Results
```

这两个阶段默认都是 **关闭的**，并且可以独立启用。

#### MMR 重排序（多样性）

当混合搜索返回结果时，多个块可能包含相似或重叠的内容。
例如，搜索 "home network setup" 可能会从不同的每日笔记中返回五个几乎相同的片段，这些都提到了相同的路由器配置。

**MMR (Maximal Marginal Relevance)** 对结果进行重排序，以平衡相关性与多样性，确保顶部结果涵盖查询的不同方面，而不是重复相同的信息。

工作原理：

1. 结果按其原始相关性评分（向量 + BM25 加权分数）。
2. MMR 迭代选择最大化以下内容的结果：`λ × relevance − (1−λ) × max_similarity_to_selected`。
3. 结果之间的相似性使用基于分词内容的 Jaccard 文本相似性来衡量。

`lambda` 参数控制权衡：

- `lambda = 1.0` → 纯相关性（无多样性惩罚）
- `lambda = 0.0` → 最大多样性（忽略相关性）
- 默认值：`0.7`（平衡，轻微相关性偏差）

**示例 — 查询："home network setup"**

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

使用 MMR (λ=0.7) — 前 3 个结果：

```
1. memory/2026-02-10.md  (score: 0.92)  ← router + VLAN
2. memory/network.md     (score: 0.85)  ← reference doc (diverse!)
3. memory/2026-02-05.md  (score: 0.78)  ← AdGuard DNS (diverse!)
```

来自 2 月 8 日的近似重复项被剔除，代理获得三条不同的信息。

**何时启用：** 如果您注意到 `memory_search` 返回冗余或近似重复的片段，尤其是每日笔记经常在不同天重复类似信息时。

#### 时间衰减（近期提升）

带有每日笔记的代理会随着时间积累数百个带日期的文件。如果没有衰减，六个月前措辞良好的笔记可能会排在昨天同一主题更新的前面。

**时间衰减** 根据每个结果的时效性对分数应用指数乘数，因此最近的记忆自然排名更高，而旧的记忆会逐渐淡化：

```
decayedScore = score × e^(-λ × ageInDays)
```

其中 `λ = ln(2) / halfLifeDays`。

使用默认的 30 天半衰期：

- 今天的笔记：原始分数的 **100%**
- 7 天前：**~84%**
- 30 天前：**50%**
- 90 天前：**12.5%**
- 180 天前：**~1.6%**

**永久文件永远不会衰减：**

- `MEMORY.md`（根记忆文件）
- `memory/` 中的非带日期文件（例如 `memory/projects.md`、`memory/network.md`）
- 这些包含持久的参考信息，应始终正常排名。

**带日期的每日文件** (`memory/YYYY-MM-DD.md`) 使用从文件名中提取的日期。
其他来源（例如会话转录）回退到文件修改时间 (`mtime`)。

**示例 — 查询："what's Rod's work schedule?"**

给定这些记忆文件（今天是 2 月 10 日）：

```
memory/2025-09-15.md  → "Rod works Mon-Fri, standup at 10am, pairing at 2pm"  (148 days old)
memory/2026-02-10.md  → "Rod has standup at 14:15, 1:1 with Zeb at 14:45"    (today)
memory/2026-02-03.md  → "Rod started new team, standup moved to 14:15"        (7 days old)
```

不使用衰减：

```
1. memory/2025-09-15.md  (score: 0.91)  ← best semantic match, but stale!
2. memory/2026-02-10.md  (score: 0.82)
3. memory/2026-02-03.md  (score: 0.80)
```

使用衰减 (halfLife=30)：

```
1. memory/2026-02-10.md  (score: 0.82 × 1.00 = 0.82)  ← today, no decay
2. memory/2026-02-03.md  (score: 0.80 × 0.85 = 0.68)  ← 7 days, mild decay
3. memory/2025-09-15.md  (score: 0.91 × 0.03 = 0.03)  ← 148 days, nearly gone
```

过时的 9 月笔记尽管具有最佳的原始语义匹配，但仍降至底部。

**何时启用：** 如果您的代理有数月的每日笔记，并且您发现旧的、过时的信息排在最近上下文的前面。30 天的半衰期适用于每日笔记繁重的工作流；如果您经常参考旧笔记，请增加它（例如 90 天）。

#### 配置

这两个功能均在 `memorySearch.query.hybrid` 下配置：

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

- **仅 MMR** — 当您有许多类似笔记但时效性不重要时有用。
- **仅时间衰减** — 当近期性很重要但您的结果已经多样化时有用。
- **两者** — 推荐用于具有大量、长期运行的每日笔记历史的代理。

### 嵌入缓存

OpenClaw 可以在 SQLite 中缓存 **块嵌入**，因此重新索引和频繁更新（尤其是会话转录）不会重新嵌入未更改的文本。

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

您可以选择索引 **会话转录** 并通过 `memory_search` 展示它们。
这受实验性标志保护。

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

注意：

- 会话索引是 **选择加入的**（默认关闭）。
- 会话更新经过防抖处理，一旦超过 delta 阈值即 **异步索引**（尽力而为）。
- `memory_search` 绝不会因索引而阻塞；结果可能略微过时，直到后台同步完成。
- 结果仍然仅包含片段；`memory_get` 仍限于记忆文件。
- 会话索引按代理隔离（仅索引该代理的会话日志）。
- 会话日志存储在磁盘上 (`~/.openclaw/agents/<agentId>/sessions/*.jsonl`)。任何具有文件系统访问权限的进程/用户都可以读取它们，因此将磁盘访问视为信任边界。为了更严格的隔离，请在单独的操作系统用户或主机下运行代理。

Delta 阈值（显示默认值）：

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

当 sqlite-vec 扩展可用时，OpenClaw 将嵌入存储在 SQLite 虚拟表 (`vec0`) 中，并在数据库中执行向量距离查询。
这使得搜索保持快速，而无需将每个嵌入加载到 JS 中。

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

注意：

- `enabled` 默认为 true；禁用时，搜索回退到对存储嵌入进行进程内余弦相似度计算。
- 如果缺少 sqlite-vec 扩展或加载失败，OpenClaw 会记录错误并继续使用 JS 回退（无向量表）。
- `extensionPath` 覆盖 bundled sqlite-vec 路径（适用于自定义构建或非标准安装位置）。

### 本地嵌入自动下载

- 默认本地嵌入模型：`hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf` (~0.6 GB)。
- 当 `memorySearch.provider = "local"` 时，`node-llama-cpp` 解析 `modelPath`；如果 GGUF 缺失，它会 **自动下载** 到缓存（如果设置了 `local.modelCacheDir` 则下载到此处），然后加载它。下载可在重试时恢复。
- 原生构建要求：运行 `pnpm approve-builds`，选择 `node-llama-cpp`，然后 `pnpm rebuild node-llama-cpp`。
- 回退：如果本地设置失败且 `memorySearch.fallback = "openai"`，我们会自动切换到远程嵌入（`openai/text-embedding-3-small` 除非被覆盖）并记录原因。

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

注意：

- `remote.*` 优先于 `models.providers.openai.*`。
- `remote.headers` 与 OpenAI headers 合并；远程在键冲突时获胜。省略 `remote.headers` 以使用 OpenAI 默认值。