---
title: "Memory"
summary: "How OpenClaw memory works (workspace files + automatic memory flush)"
read_when:
  - You want the memory file layout and workflow
  - You want to tune the automatic pre-compaction memory flush
---
# 内存

OpenClaw 的内存是**代理工作区中的纯 Markdown 文件**。这些文件即为唯一真实来源；模型仅“记住”已写入磁盘的内容。

内存搜索工具由当前启用的内存插件提供（默认：`memory-core`）。可通过 `plugins.slots.memory = "none"` 禁用内存插件。

## 内存文件（Markdown）

默认工作区布局采用两层内存结构：

- `memory/YYYY-MM-DD.md`
  - 每日日志（仅追加）。
  - 会话启动时读取今日与昨日内容。
- `MEMORY.md`（可选）
  - 经人工整理的长期记忆。
  - **仅在主私有会话中加载**（绝不在群组上下文中加载）。

这些文件位于工作区目录下（`agents.defaults.workspace`，默认为 `~/.openclaw/workspace`）。完整布局请参阅 [代理工作区](/concepts/agent-workspace)。

## 内存工具

OpenClaw 面向代理暴露了两个用于操作这些 Markdown 文件的工具：

- `memory_search` —— 在已索引片段上执行语义召回。
- `memory_get` —— 针对性地读取特定 Markdown 文件或某行范围。

`memory_get` 现在在文件不存在时（例如：首次写入前的当日日志）**能优雅降级**。内置管理器与 QMD 后端均返回 `{ text: "", path }`，而非抛出 `ENOENT`，因此代理可妥善处理“尚无记录”的情况，并继续其工作流，无需将该工具调用包裹在 try/catch 逻辑中。

## 何时写入内存

- 决策、偏好及持久性事实应写入 `MEMORY.md`。
- 日常笔记与运行时上下文应写入 `memory/YYYY-MM-DD.md`。
- 若有人表示“请记住这一点”，请立即将其写入（切勿仅保留在内存 RAM 中）。
- 此机制仍在持续演进中。适时提醒模型存储记忆是有益的；模型将自行判断应如何操作。
- 若希望某项内容被持久保留，请**明确要求机器人将其写入内存**。

## 自动内存刷新（预压缩提示）

当会话**即将自动压缩**时，OpenClaw 将触发一次**静默的、以代理为中心的轮次**，提醒模型在上下文被压缩**之前**写入持久性记忆。默认提示语明确说明模型 _可作回复_，但通常 `NO_REPLY` 是正确响应，因此用户不会察觉此次轮次。

此行为由 `agents.defaults.compaction.memoryFlush` 控制：

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

详细说明：

- **软阈值**：当会话 token 预估量超过 `contextWindow - reserveTokensFloor - softThresholdTokens` 时触发刷新。
- 默认为**静默模式**：提示语中包含 `NO_REPLY`，因此不向用户输出任何内容。
- **双提示机制**：包含一条用户提示与一条系统提示，共同附加提醒。
- **每个压缩周期仅执行一次刷新**（通过 `sessions.json` 追踪）。
- **工作区必须具备可写权限**：若会话以沙箱方式运行且配置了 `workspaceAccess: "ro"` 或 `"none"`，则跳过刷新。

有关完整的压缩生命周期，请参阅  
[会话管理 + 压缩](/reference/session-management-compaction)。

## 向量内存搜索

OpenClaw 可在 `MEMORY.md` 和 `memory/*.md` 上构建小型向量索引，从而支持语义查询——即使措辞不同，也能找到相关笔记。

默认设置如下：

- 默认启用。
- 监听内存文件变更（带防抖）。
- 内存搜索配置位于 `agents.defaults.memorySearch` 下（非顶层 `memorySearch`）。
- 默认使用远程嵌入（embeddings）。若未设置 `memorySearch.provider`，OpenClaw 将自动选择：
  1. 若已配置 `memorySearch.local.modelPath` 且对应文件存在，则选用 `local`；
  2. 若可解析 OpenAI 密钥，则选用 `openai`；
  3. 若可解析 Gemini 密钥，则选用 `gemini`；
  4. 若可解析 Voyage 密钥，则选用 `voyage`；
  5. 若可解析 Mistral 密钥，则选用 `mistral`；
  6. 否则内存搜索保持禁用状态，直至手动配置。
- 本地模式使用 node-llama-cpp，可能需要 `pnpm approve-builds`。
- 使用 sqlite-vec（若可用）在 SQLite 内加速向量搜索。
- 也支持 `memorySearch.provider = "ollama"` 用于本地/自托管的 Ollama 嵌入（`/api/embeddings`），但该选项不会被自动选中。

远程嵌入**必须**提供对应嵌入服务提供商的 API 密钥。OpenClaw 从认证配置文件、`models.providers.*.apiKey` 或环境变量中解析密钥。Codex OAuth 仅覆盖聊天/补全功能，**无法满足**内存搜索所需的嵌入能力。对于 Gemini，请使用 `GEMINI_API_KEY` 或 `models.providers.google.apiKey`；对于 Voyage，请使用 `VOYAGE_API_KEY` 或 `models.providers.voyage.apiKey`；对于 Mistral，请使用 `MISTRAL_API_KEY` 或 `models.providers.mistral.apiKey`。Ollama 通常无需真实 API 密钥（按本地策略需要时，使用占位符如 `OLLAMA_API_KEY=ollama-local` 即可）。  
当使用自定义 OpenAI 兼容端点时，请设置 `memorySearch.remote.apiKey`（以及可选的 `memorySearch.remote.headers`）。

### QMD 后端（实验性）

设置 `memory.backend = "qmd"` 可将内置 SQLite 索引器替换为  
[QMD](https://github.com/tobi/qmd)：一个以本地优先为设计原则的搜索辅助进程，融合 BM25 + 向量 + 重排序能力。Markdown 仍为唯一真实来源；OpenClaw 通过调用外部 QMD 执行检索。关键要点如下：

**前提条件**

- 默认禁用。需按配置显式启用（`memory.backend = "qmd"`）。
- 需单独安装 QMD CLI（`bun install -g https://github.com/tobi/qmd` 或下载发布版本），并确保 `qmd` 二进制文件位于网关的 `PATH` 路径中。
- QMD 需要支持扩展的 SQLite 构建版本（macOS 上为 `brew install sqlite`）。
- QMD 通过 Bun + `node-llama-cpp` 完全本地运行，并在首次使用时自动从 HuggingFace 下载 GGUF 模型（无需单独运行 Ollama 守护进程）。
- 网关在 `~/.openclaw/agents/<agentId>/qmd/` 下以自包含 XDG home 方式运行 QMD，通过设置 `XDG_CONFIG_HOME` 与 `XDG_CACHE_HOME` 实现。
- 操作系统支持：macOS 与 Linux 在安装 Bun + SQLite 后开箱即用；Windows 推荐通过 WSL2 支持。

**辅助进程运行方式**

- 网关在 `~/.openclaw/agents/<agentId>/qmd/` 下创建自包含的 QMD home（含配置、缓存与 SQLite 数据库）。
- 集合通过 `qmd collection add` 从 `memory.qmd.paths`（加上默认工作区内存文件）创建，随后 `qmd update` 与 `qmd embed` 在启动时及可配置的时间间隔（`memory.qmd.update.interval`，默认为 5 分钟）内运行。
- 网关现于启动时初始化 QMD 管理器，因此即使尚未执行首次 `memory_search` 调用，周期性更新定时器也已就绪。
- 启动时的刷新现默认后台运行，避免阻塞聊天初始化；设置 `memory.qmd.update.waitForBootSync = true` 可恢复此前的阻塞行为。
- 搜索通过 `memory.qmd.searchMode` 执行（默认为 `qmd search --json`；亦支持 `vsearch` 与 `query`）。若所选模式在您的 QMD 构建中拒绝某些标志，OpenClaw 将重试使用 `qmd query`。若 QMD 失败或二进制缺失，OpenClaw 将自动回退至内置 SQLite 管理器，确保内存工具持续可用。
- OpenClaw 当前未暴露 QMD 嵌入批处理大小调优接口；批处理行为由 QMD 自身控制。
- **首次搜索可能较慢**：QMD 可能在首次 `qmd query` 运行时下载本地 GGUF 模型（重排序器/查询扩展器）。
  - OpenClaw 在运行 QMD 时自动设置 `XDG_CONFIG_HOME`/`XDG_CACHE_HOME`。
  - 若希望手动预下载模型（并预热 OpenClaw 所用的同一索引），可使用代理的 XDG 目录运行一次性查询。

OpenClaw 的 QMD 状态存于您的 **state dir**（默认为 `~/.openclaw`）。您可通过导出 OpenClaw 所用的相同 XDG 环境变量，使 `qmd` 指向完全相同的索引：

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

**配置表层（`memory.qmd.*`）**

- `command`（默认值为 `qmd`）：覆盖可执行文件路径。  
- `searchMode`（默认值为 `search`）：选择由哪个 QMD 命令支持 `memory_search`（`search`、`vsearch`、`query`）。  
- `includeDefaultMemory`（默认值为 `true`）：自动索引 `MEMORY.md` + `memory/**/*.md`。  
- `paths[]`：添加额外目录/文件（`path`，可选 `pattern`，可选稳定版 `name`）。  
- `sessions`：启用会话 JSONL 索引（`enabled`、`retentionDays`、`exportDir`）。  
- `update`：控制刷新频率与维护任务执行：（`interval`、`debounceMs`、`onBoot`、`waitForBootSync`、`embedInterval`、`commandTimeoutMs`、`updateTimeoutMs`、`embedTimeoutMs`）。  
- `limits`：限制召回载荷（`maxResults`、`maxSnippetChars`、`maxInjectedChars`、`timeoutMs`）。  
- `scope`：模式与 [``session.sendPolicy``](/gateway/configuration#session) 相同。默认仅限 DM（`deny` 全部，`allow` 仅限直接聊天）；放宽该限制可使 QMD 检索结果在群组/频道中也可见。  
  - `match.keyPrefix` 匹配 **标准化的** 会话键（小写，且已去除任何前导 `agent:<id>:`）。示例：`discord:channel:`。  
  - `match.rawKeyPrefix` 匹配 **原始的** 会话键（小写），包含 `agent:<id>:`。示例：`agent:main:discord:`。  
  - 遗留方式：`match.keyPrefix: "agent:..."` 仍被视为原始键前缀，但为清晰起见，建议优先使用 `rawKeyPrefix`。  
- 当 `scope` 拒绝一次搜索时，OpenClaw 将记录一条警告日志，并附上推导出的 `channel`/`chatType`，以便更轻松地调试空结果。  
- 来自工作区外部的代码片段在 `memory_search` 结果中显示为 `qmd/<collection>/<relative-path>`；`memory_get` 能识别该前缀，并从配置的 QMD 集合根目录读取内容。  
- 当启用 `memory.qmd.sessions.enabled = true` 时，OpenClaw 将脱敏后的会话转录文本（用户/助手轮次）导出至 `~/.openclaw/agents/<id>/qmd/sessions/` 下的专用 QMD 集合，从而使 `memory_search` 可在不访问内置 SQLite 索引的前提下召回近期对话。  
- `memory_search` 代码片段现在在 `memory.citations` 为 `auto`/`on` 时包含一个 `Source: <path#line>` 页脚；设置 `memory.citations = "off"` 可将路径元数据保留在内部（代理仍会接收到路径以用于 `memory_get`，但代码片段文本中将省略页脚，且系统提示会提醒代理不要引用该路径）。

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

**引用与回退机制**

- `memory.citations` 在所有后端（`auto`/`on`/`off`）下均生效。  
- 当 `qmd` 运行时，我们为 `status().backend = "qmd"` 打上标签，以便诊断信息能明确显示由哪个引擎提供结果。若 QMD 子进程退出或无法解析 JSON 输出，搜索管理器将记录一条警告并返回内置提供程序（现有 Markdown 嵌入），直至 QMD 恢复。

### 额外的记忆路径

如需索引默认工作区布局之外的 Markdown 文件，请显式添加路径：

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

- 路径可以是绝对路径，也可以是相对于工作区的路径。  
- 目录将被递归扫描以查找 `.md` 文件。  
- 仅索引 Markdown 文件。  
- 忽略符号链接（文件或目录）。

### Gemini 嵌入（原生）

将提供程序设为 `gemini`，即可直接使用 Gemini 嵌入 API：

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
- `remote.headers` 允许您在必要时添加额外请求头。  
- 默认模型：`gemini-embedding-001`。

如需使用 **自定义 OpenAI 兼容端点**（如 OpenRouter、vLLM 或代理），可配合 OpenAI 提供程序使用 `remote` 配置：

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

如不想设置 API 密钥，可使用 `memorySearch.provider = "local"`，或设置 `memorySearch.fallback = "none"`。

回退机制：

- `memorySearch.fallback` 可设为 `openai`、`gemini`、`voyage`、`mistral`、`ollama`、`local` 或 `none`。  
- 仅当主嵌入提供程序失败时，才会使用回退提供程序。

批量索引（OpenAI + Gemini + Voyage）：

- 默认禁用。设置 `agents.defaults.memorySearch.remote.batch.enabled = true` 即可为大规模语料库索引（OpenAI、Gemini 和 Voyage）启用批量模式。  
- 默认行为为等待整个批次完成；如有需要，可调整 `remote.batch.wait`、`remote.batch.pollIntervalMs` 和 `remote.batch.timeoutMinutes`。  
- 设置 `remote.batch.concurrency` 以控制并行提交的批处理作业数量（默认值：2）。  
- 批量模式在启用 `memorySearch.provider = "openai"` 或 `"gemini"` 时生效，并使用对应的 API 密钥。  
- Gemini 批处理作业使用异步嵌入批处理端点，要求 Gemini 批处理 API 可用。

为何 OpenAI 批处理既快又便宜：

- 对于大规模补全索引，OpenAI 通常是本项目支持的最快选项，因为我们可在单个批处理作业中提交大量嵌入请求，并让 OpenAI 异步处理。  
- OpenAI 为批处理 API 工作负载提供折扣定价，因此大规模索引运行通常比同步发送相同请求更便宜。  
- 更多详情请参阅 OpenAI 批处理 API 文档及定价说明：  
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

- `memory_search` — 返回带文件名和行号范围的代码片段。  
- `memory_get` — 按路径读取记忆文件内容。

本地模式：

- 设置 `agents.defaults.memorySearch.provider = "local"`。  
- 提供 `agents.defaults.memorySearch.local.modelPath`（GGUF 或 `hf:` URI）。  
- 可选：设置 `agents.defaults.memorySearch.fallback = "none"` 以避免远程回退。

### 记忆工具的工作原理

- `memory_search` 对来自 `MEMORY.md` + `memory/**/*.md` 的 Markdown 分块（目标约 400 token，重叠 80 token）进行语义搜索。它返回代码片段文本（上限约 700 字符）、文件路径、行号范围、得分、提供程序/模型，以及是否从本地 → 远程嵌入发生回退。不返回完整文件载荷。  
- `memory_get` 读取特定的记忆 Markdown 文件（相对于工作区路径），可选指定起始行号及读取行数 N。超出 `MEMORY.md` / `memory/` 范围的路径将被拒绝。  
- 仅当 `memorySearch.enabled` 对代理求值为 `true` 时，才启用这两个工具。

### 索引内容（及触发时机）

- 文件类型：仅 Markdown（`MEMORY.md`、`memory/**/*.md`）。  
- 索引存储：每个代理独立的 SQLite 数据库，位于 `~/.openclaw/memory/<agentId>.sqlite`（可通过 `agents.defaults.memorySearch.store.path` 配置，支持 `{agentId}` token）。  
- 新鲜度：监听 `MEMORY.md` + `memory/` 的监视器会在文件变更时将索引标记为“脏”（防抖 1.5 秒）。同步操作将在会话启动时、搜索时或按时间间隔调度，并异步执行。会话转录使用增量阈值来触发后台同步。  
- 重新索引触发条件：索引中存储了嵌入 **提供程序/模型 + 端点指纹 + 分块参数**。若其中任一发生变化，OpenClaw 将自动重置并重新索引整个存储。

### 混合搜索（BM25 + 向量）

启用后，OpenClaw 将结合以下两种方式：

- **向量相似性**（语义匹配，措辞可不同）  
- **BM25 关键词相关性**（精确匹配 ID、环境变量、代码符号等高信号 token）

若您的平台不支持全文搜索，OpenClaw 将自动回退至纯向量搜索。

#### 为何采用混合搜索？

向量搜索擅长处理“含义相同但表述不同”的情形：

- “Mac Studio 网关主机” vs “运行网关的机器”  
- “防抖文件更新” vs “避免每次写入都触发索引”

但在精确、高信号 token 上可能较弱：

- ID（`a828e60`、`b3b9895a…`）  
- 代码符号（`memorySearch.query.hybrid`）  
- 错误字符串（"sqlite-vec unavailable"）

而 BM25（全文搜索）则相反：对精确 token 表现强劲，对同义改写能力较弱。  
混合搜索是一种务实的折中方案：**同时利用两种检索信号**，从而兼顾“自然语言查询”与“大海捞针式查询”的良好效果。

#### 结果合并方式（当前设计）

实现概要：

1. 分别从两个通道获取候选集：

- **向量**：按余弦相似度取前 `maxResults * candidateMultiplier` 个。  
- **BM25**：按 FTS5 BM25 排名（越小越好）取前 `maxResults * candidateMultiplier` 个。

2. 将 BM25 排名转换为近似 0..1 区间的得分：

- `textScore = 1 / (1 + max(0, bm25Rank))`

3. 按分块 ID 合并候选集，并计算加权得分：

- `finalScore = vectorWeight * vectorScore + textWeight * textScore`

注意事项：

- `vectorWeight` + `textWeight` 在配置解析中被归一化为 1.0，因此权重表现为百分比形式。  
- 如果嵌入向量不可用（或提供方返回零向量），我们仍会运行 BM25 并返回关键词匹配结果。  
- 如果无法创建 FTS5，我们将保留仅向量搜索（不触发硬性失败）。  

这并非“信息检索理论意义上的完美方案”，但它简单、快速，并且在实际笔记场景中往往能提升召回率与准确率。  
若后续希望进一步优化，常见进阶方案包括**互惠秩融合（RRF）**，或在混合前对分数进行归一化处理（如 min/max 归一化或 z-score 标准化）。  

#### 后处理流水线  

在合并向量与关键词得分后，有两个可选的后处理阶段，用于在结果送达智能体前进一步精炼结果列表：  

```
Vector + Keyword → Weighted Merge → Temporal Decay → Sort → MMR → Top-K Results
```  

两个阶段均**默认关闭**，且可独立启用。  

#### MMR 重排序（多样性保障）  

混合搜索返回结果时，多个文本块可能包含相似或重叠的内容。  
例如，搜索“家庭网络搭建”可能从不同日期的日常笔记中返回五个几乎完全相同的片段，均提及同一路由器配置。  

**MMR（最大边缘相关性）** 对结果进行重排序，以平衡相关性与多样性，确保顶部结果覆盖查询的不同方面，而非重复相同信息。  

其工作原理如下：  

1. 结果首先依据原始相关性得分（向量 + BM25 加权得分）排序；  
2. MMR 迭代式地选取使以下公式最大化的结果：`λ × relevance − (1−λ) × max_similarity_to_selected`；  
3. 结果之间的相似度通过分词后文本的 **Jaccard 相似度** 计算。  

`lambda` 参数控制相关性与多样性的权衡：  

- `lambda = 1.0` → 纯相关性（无多样性惩罚）  
- `lambda = 0.0` → 最大化多样性（忽略相关性）  
- 默认值：`0.7`（均衡，略微偏向相关性）  

**示例 — 查询：“家庭网络搭建”**  

给定如下记忆文件：  

```
memory/2026-02-10.md  → "Configured Omada router, set VLAN 10 for IoT devices"
memory/2026-02-08.md  → "Configured Omada router, moved IoT to VLAN 10"
memory/2026-02-05.md  → "Set up AdGuard DNS on 192.168.10.2"
memory/network.md     → "Router: Omada ER605, AdGuard: 192.168.10.2, VLAN 10: IoT"
```  

未启用 MMR 时，Top 3 结果为：  

```
1. memory/2026-02-10.md  (score: 0.92)  ← router + VLAN
2. memory/2026-02-08.md  (score: 0.89)  ← router + VLAN (near-duplicate!)
3. memory/network.md     (score: 0.85)  ← reference doc
```  

启用 MMR（λ=0.7）后，Top 3 结果为：  

```
1. memory/2026-02-10.md  (score: 0.92)  ← router + VLAN
2. memory/network.md     (score: 0.85)  ← reference doc (diverse!)
3. memory/2026-02-05.md  (score: 0.78)  ← AdGuard DNS (diverse!)
```  

2 月 8 日的近似重复项被剔除，智能体获得三条互不重叠的信息。  

**启用建议**：若你发现 `memory_search` 返回冗余或近似重复的片段，尤其当日常笔记常在多日间反复提及相似内容时。  

#### 时间衰减（时效性增强）  

使用日常笔记的智能体随时间推移会积累数百个带日期的文件。若不引入衰减机制，六个月前措辞精准的笔记可能压倒昨日关于同一主题的更新。  

**时间衰减** 基于每个结果的年龄对其得分施加指数级乘数，使近期记忆自然排名更高，而旧记忆逐渐淡化：  

```
decayedScore = score × e^(-λ × ageInDays)
```  

其中 `λ = ln(2) / halfLifeDays`。  

采用默认半衰期 30 天时：  

- 当日笔记：原始得分的 **100%**  
- 7 天前：约 **84%**  
- 30 天前：**50%**  
- 90 天前：**12.5%**  
- 180 天前：约 **1.6%**  

**永久有效文件永不衰减**：  

- `MEMORY.md`（根记忆文件）  
- `memory/` 中的非日期型文件（例如 `memory/projects.md`、`memory/network.md`）  
- 此类文件承载持久性参考信息，应始终按正常方式参与排序。  

**带日期的日常文件**（`memory/YYYY-MM-DD.md`）使用从文件名中提取的日期；  
其他来源（如会话转录）则回退至文件修改时间（`mtime`）。  

**示例 — 查询：“Rod 的工作日程是什么？”**  

给定如下记忆文件（今日为 2 月 10 日）：  

```
memory/2025-09-15.md  → "Rod works Mon-Fri, standup at 10am, pairing at 2pm"  (148 days old)
memory/2026-02-10.md  → "Rod has standup at 14:15, 1:1 with Zeb at 14:45"    (today)
memory/2026-02-03.md  → "Rod started new team, standup moved to 14:15"        (7 days old)
```  

未启用衰减时：  

```
1. memory/2025-09-15.md  (score: 0.91)  ← best semantic match, but stale!
2. memory/2026-02-10.md  (score: 0.82)
3. memory/2026-02-03.md  (score: 0.80)
```  

启用衰减（halfLife=30）后：  

```
1. memory/2026-02-10.md  (score: 0.82 × 1.00 = 0.82)  ← today, no decay
2. memory/2026-02-03.md  (score: 0.80 × 0.85 = 0.68)  ← 7 days, mild decay
3. memory/2025-09-15.md  (score: 0.91 × 0.03 = 0.03)  ← 148 days, nearly gone
```  

尽管九月笔记语义匹配度最高，但因陈旧而跌至末位。  

**启用建议**：若你的智能体已积累数月日常笔记，且你发现过时、陈旧的信息常压倒最新上下文，则建议启用该功能。对于以日常笔记为主的场景，30 天半衰期效果良好；若需频繁引用较早笔记，可适当延长（例如设为 90 天）。  

#### 配置  

两项功能均在 `memorySearch.query.hybrid` 下配置：  

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

你可以独立启用任一功能：  

- **仅启用 MMR** —— 适用于存在大量相似笔记、但时间顺序无关紧要的场景；  
- **仅启用时间衰减** —— 适用于时效性关键、但当前结果已具备足够多样性的场景；  
- **两者同时启用** —— 推荐用于拥有大规模、长期运行的日常笔记历史的智能体。  

### 嵌入缓存  

OpenClaw 可将**文本块嵌入向量**缓存在 SQLite 中，从而避免在重新索引或频繁更新（尤其是会话转录）时对未变更文本重复执行嵌入计算。  

配置如下：  

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

你可选择性地索引**会话转录内容**，并通过 `memory_search` 将其呈现出来。此功能受实验性标志管控。  

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

- 会话索引为**显式启用**（默认关闭）；  
- 会话更新经过防抖处理，并在跨越增量阈值后**异步索引**（尽力而为）；  
- `memory_search` 永远不会阻塞索引过程；结果可能略有延迟，直至后台同步完成；  
- 结果仍仅包含文本片段；`memory_get` 的范围仍严格限定于记忆文件；  
- 会话索引按智能体隔离（仅索引该智能体自身的会话日志）；  
- 会话日志存储于磁盘（`~/.openclaw/agents/<agentId>/sessions/*.jsonl`）。任何具有文件系统访问权限的进程或用户均可读取，因此请将磁盘访问视为信任边界。如需更严格的隔离，请在独立操作系统用户或主机下运行智能体。  

增量阈值（默认值如下）：  

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

### SQLite 向量加速（sqlite-vec）  

当 sqlite-vec 扩展可用时，OpenClaw 将嵌入向量存入 SQLite 虚拟表（`vec0`），并在数据库内执行向量距离查询。此举可在不将全部嵌入加载进 JavaScript 的前提下维持搜索速度。  

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

- `enabled` 默认为 true；禁用后，搜索将回退至进程内基于已存储嵌入的余弦相似度计算；  
- 若 sqlite-vec 扩展缺失或加载失败，OpenClaw 将记录错误并继续使用 JS 回退方案（不创建向量表）；  
- `extensionPath` 可覆写内置 sqlite-vec 路径（适用于定制构建或非标准安装路径）。  

### 本地嵌入模型自动下载  

- 默认本地嵌入模型：`hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf`（约 0.6 GB）；  
- 当 `memorySearch.provider = "local"` 时，`node-llama-cpp` 将解析 `modelPath`；若 GGUF 文件缺失，系统将**自动下载**至缓存目录（或指定的 `local.modelCacheDir`），随后加载。下载支持断点续传；  
- 原生构建要求：运行 `pnpm approve-builds`，选择 `node-llama-cpp`，再执行 `pnpm rebuild node-llama-cpp`；  
- 回退机制：若本地配置失败且启用了 `memorySearch.fallback = "openai"`，系统将自动切换至远程嵌入服务（除非另行指定，否则使用 `openai/text-embedding-3-small`），并记录具体原因。  

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

- `remote.*` 优先级高于 `models.providers.openai.*`；  
- `remote.headers` 将与 OpenAI 请求头合并；键冲突时远程头胜出。若省略 `remote.headers`，则使用 OpenAI 默认头。