---
summary: "Audit what can spend money, which keys are used, and how to view usage"
read_when:
  - You want to understand which features may call paid APIs
  - You need to audit keys, costs, and usage visibility
  - You’re explaining /status or /usage cost reporting
title: "API Usage and Costs"
---
# API 使用与费用

本文档列出了**可以调用 API 密钥的功能**以及其费用显示位置。重点介绍
OpenClaw 中可能产生提供商使用量或付费 API 调用的功能。

## 费用显示位置（聊天 + CLI）

**每会话费用快照**

- `/status` 显示当前会话模型、上下文使用情况和最后响应令牌。
- 如果模型使用**API 密钥认证**，`/status` 还会显示**预估费用**用于最后回复。

**每消息费用页脚**

- `/usage full` 将使用情况页脚附加到每个回复中，包括**预估费用**（仅限 API 密钥）。
- `/usage tokens` 仅显示令牌；OAuth 流程隐藏美元费用。

**CLI 使用窗口（提供商配额）**

- `openclaw status --usage` 和 `openclaw channels list` 显示提供商**使用窗口**
  （配额快照，非每消息成本）。

详情和示例请参见[令牌使用与费用](/token-use)。

## 密钥发现方式

OpenClaw 可以从以下位置获取凭证：

- **认证配置文件**（每代理，存储在 `auth-profiles.json` 中）。
- **环境变量**（例如 `OPENAI_API_KEY`、`BRAVE_API_KEY`、`FIRECRAWL_API_KEY`）。
- **配置**（`models.providers.*.apiKey`、`tools.web.search.*`、`tools.web.fetch.firecrawl.*`、
  `memorySearch.*`、`talk.apiKey`）。
- **技能**（`skills.entries.<name>.apiKey`）可能将密钥导出到技能进程环境中。

## 可能消耗密钥的功能

### 1) 核心模型响应（聊天 + 工具）

每次回复或工具调用都使用**当前模型提供商**（OpenAI、Anthropic 等）。这是
使用量和费用的主要来源。

详情请参见[模型](/providers/models)了解定价配置和[令牌使用与费用](/token-use)了解显示。

### 2) 媒体理解（音频/图像/视频）

传入媒体可以在回复运行前进行摘要/转录。这会使用模型/提供商 API。

- 音频：OpenAI / Groq / Deepgram（现在**自动启用**当密钥存在时）。
- 图像：OpenAI / Anthropic / Google。
- 视频：Google。

详情请参见[媒体理解](/nodes/media-understanding)。

### 3) 记忆嵌入 + 语义搜索

语义记忆搜索在配置为远程提供商时使用**嵌入 API**：

- `memorySearch.provider = "openai"` → OpenAI 嵌入
- `memorySearch.provider = "gemini"` → Gemini 嵌入
- 如果本地嵌入失败则可选择回退到 OpenAI

您可以使用 `memorySearch.provider = "local"` 保持本地化（无 API 使用）。

详情请参见[记忆](/concepts/memory)。

### 4) 网络搜索工具（通过 OpenRouter 的 Brave / Perplexity）

`web_search` 使用 API 密钥并可能产生使用费用：

- **Brave 搜索 API**：`BRAVE_API_KEY` 或 `tools.web.search.apiKey`
- **Perplexity**（通过 OpenRouter）：`PERPLEXITY_API_KEY` 或 `OPENROUTER_API_KEY`

**Brave 免费层级（慷慨）：**

- **每月 2,000 次请求**
- **每秒 1 次请求**
- **需要信用卡**进行验证（除非升级否则不收费）

详情请参见[网络工具](/tools/web)。

### 5) 网络获取工具（Firecrawl）

当存在 API 密钥时，`web_fetch` 可以调用**Firecrawl**：

- `FIRECRAWL_API_KEY` 或 `tools.web.fetch.firecrawl.apiKey`

如果未配置 Firecrawl，该工具会回退到直接获取 + 可读性（无付费 API）。

详情请参见[网络工具](/tools/web)。

### 6) 提供商使用快照（状态/健康）

某些状态命令调用**提供商使用端点**来显示配额窗口或认证健康状况。
这些通常是低频调用但仍会访问提供商 API：

- `openclaw status --usage`
- `openclaw models status --json`

详情请参见[模型 CLI](/cli/models)。

### 7) 压缩保护摘要

压缩保护可以使用**当前模型**对会话历史进行摘要，运行时会调用提供商 API。

详情请参见[会话管理 + 压缩](/reference/session-management-compaction)。

### 8) 模型扫描 / 探测

`openclaw models scan` 可以探测 OpenRouter 模型并在启用探测时使用 `OPENROUTER_API_KEY`。

详情请参见[模型 CLI](/cli/models)。

### 9) 语音（Talk）

配置后，Talk 模式可以调用**ElevenLabs**：

- `ELEVENLABS_API_KEY` 或 `talk.apiKey`

详情请参见[Talk 模式](/nodes/talk)。

### 10) 技能（第三方 API）

技能可以在 `skills.entries.<name>.apiKey` 中存储 `apiKey`。如果技能使用该密钥进行外部
API 调用，可能会根据技能的提供商产生费用。

详情请参见[技能](/tools/skills)。