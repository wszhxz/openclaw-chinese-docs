---
summary: "Audit what can spend money, which keys are used, and how to view usage"
read_when:
  - You want to understand which features may call paid APIs
  - You need to audit keys, costs, and usage visibility
  - You’re explaining /status or /usage cost reporting
title: "API Usage and Costs"
---
# API 使用与费用

本文档列出了**可调用 API 密钥的功能**，以及其费用在何处体现。重点介绍可能产生供应商用量或付费 API 调用的 OpenClaw 功能。

## 费用体现位置（聊天界面 + CLI）

**每会话费用快照**

- `/status` 显示当前会话所用模型、上下文用量及上一次响应的 token 数量。
- 若模型使用 **API 密钥认证**，`/status` 还将显示上一条回复的**预估费用**。

**每条消息的费用页脚**

- `/usage full` 为每条回复附加用量页脚，包含**预估费用**（仅限 API 密钥方式）。
- `/usage tokens` 仅显示 token 数量；OAuth 流程中隐藏美元金额。

**CLI 用量窗口（供应商配额）**

- `openclaw status --usage` 和 `openclaw channels list` 显示供应商的**用量窗口**  
  （即配额快照，而非按消息计费）。

详情与示例请参阅 [Token 使用与费用](/reference/token-use)。

## 密钥发现方式

OpenClaw 可从以下位置获取凭据：

- **认证配置文件**（每个智能体专属，存储于 `auth-profiles.json` 中）。
- **环境变量**（例如 `OPENAI_API_KEY`、`BRAVE_API_KEY`、`FIRECRAWL_API_KEY`）。
- **配置文件**（`models.providers.*.apiKey`、`tools.web.search.*`、`tools.web.fetch.firecrawl.*`、  
  `memorySearch.*`、`talk.apiKey`）。
- **技能**（`skills.entries.<name>.apiKey`），其可能将密钥导出至技能进程的环境变量中。

## 可消耗密钥的功能

### 1) 核心模型响应（聊天 + 工具）

每次回复或工具调用均使用**当前模型供应商**（如 OpenAI、Anthropic 等）。这是用量与费用的主要来源。

定价配置请参阅 [模型](/providers/models)，显示方式请参阅 [Token 使用与费用](/reference/token-use)。

### 2) 媒体理解（音频/图像/视频）

传入的媒体内容可在生成回复前进行摘要或转录，此过程调用模型/供应商 API。

- 音频：OpenAI / Groq / Deepgram（现当密钥存在时**自动启用**）。
- 图像：OpenAI / Anthropic / Google。
- 视频：Google。

详见 [媒体理解](/nodes/media-understanding)。

### 3) 记忆嵌入 + 语义搜索

当语义记忆搜索配置为远程供应商时，将使用**嵌入 API**：

- `memorySearch.provider = "openai"` → OpenAI 嵌入
- `memorySearch.provider = "gemini"` → Gemini 嵌入
- `memorySearch.provider = "voyage"` → Voyage 嵌入
- `memorySearch.provider = "mistral"` → Mistral 嵌入
- `memorySearch.provider = "ollama"` → Ollama 嵌入（本地/自托管；通常不产生托管 API 计费）
- 若本地嵌入失败，可选择回退至远程供应商

您可通过 `memorySearch.provider = "local"` 完全保持本地运行（无 API 用量）。

详见 [记忆](/concepts/memory)。

### 4) 网络搜索工具

`web_search` 使用 API 密钥，具体是否产生费用取决于您的供应商：

- **Perplexity 搜索 API**：`PERPLEXITY_API_KEY`
- **Brave 搜索 API**：`BRAVE_API_KEY` 或 `tools.web.search.apiKey`
- **Gemini（Google 搜索）**：`GEMINI_API_KEY`
- **Grok（xAI）**：`XAI_API_KEY`
- **Kimi（Moonshot）**：`KIMI_API_KEY` 或 `MOONSHOT_API_KEY`

详见 [网络工具](/tools/web)。

### 5) 网络抓取工具（Firecrawl）

当存在 API 密钥时，`web_fetch` 可调用 **Firecrawl**：

- `FIRECRAWL_API_KEY` 或 `tools.web.fetch.firecrawl.apiKey`

若未配置 Firecrawl，该工具将回退至直接抓取 + readability（不调用付费 API）。

详见 [网络工具](/tools/web)。

### 6) 供应商用量快照（状态/健康检查）

部分状态命令会调用**供应商用量端点**，以显示配额窗口或认证健康状况。  
此类调用频率通常较低，但仍会访问供应商 API：

- `openclaw status --usage`
- `openclaw models status --json`

详见 [模型 CLI](/cli/models)。

### 7) 压缩保护机制中的摘要生成

压缩保护机制可使用**当前模型**对会话历史进行摘要，该操作运行时将调用供应商 API。

详见 [会话管理与压缩](/reference/session-management-compaction)。

### 8) 模型扫描 / 探测

`openclaw models scan` 可探测 OpenRouter 模型，并在启用探测功能时使用 `OPENROUTER_API_KEY`。

详见 [模型 CLI](/cli/models)。

### 9) Talk（语音）

Talk 模式在配置后可调用 **ElevenLabs**：

- `ELEVENLABS_API_KEY` 或 `talk.apiKey`

详见 [Talk 模式](/nodes/talk)。

### 10) 技能（第三方 API）

技能可在 `skills.entries.<name>.apiKey` 中存储 `apiKey`。若技能使用该密钥调用外部 API，则可能根据其供应商产生相应费用。

详见 [技能](/tools/skills)。