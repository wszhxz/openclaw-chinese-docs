---
summary: "Audit what can spend money, which keys are used, and how to view usage"
read_when:
  - You want to understand which features may call paid APIs
  - You need to audit keys, costs, and usage visibility
  - You’re explaining /status or /usage cost reporting
title: "API Usage and Costs"
---
# API 使用及费用

本文档列出了**可以调用API密钥的功能**及其费用出现的位置。它专注于
OpenClaw中可以生成提供商使用或付费API调用的功能。

## 费用出现的位置（聊天 + CLI）

**每会话费用快照**

- `/status` 显示当前会话模型、上下文使用情况以及最后回复的标记。
- 如果模型使用**API密钥认证**，`/status` 还会显示最后回复的**预计费用**。

**每消息费用页脚**

- `/usage full` 为每个回复附加一个使用情况页脚，包括**预计费用**（仅限API密钥）。
- `/usage tokens` 仅显示标记；OAuth流程隐藏美元费用。

**CLI使用窗口（提供商配额）**

- `openclaw status --usage` 和 `openclaw channels list` 显示提供商的**使用窗口**
  （配额快照，而非每消息费用）。

详见[标记使用及费用](/token-use)获取详细信息和示例。

## 密钥如何被发现

OpenClaw可以从以下位置获取凭据：

- **身份验证配置文件**（每个代理，存储在 `auth-profiles.json` 中）。
- **环境变量**（例如 `OPENAI_API_KEY`，`BRAVE_API_KEY`，`FIRECRAWL_API_KEY`）。
- **配置** (`models.providers.*.apiKey`，`tools.web.search.*`，`tools.web.fetch.firecrawl.*`，
  `memorySearch.*`，`talk.apiKey`)。
- **技能** (`skills.entries.<name>.apiKey`)，这些技能可能将密钥导出到技能进程的环境中。

## 可以消耗密钥的功能

### 1) 核心模型响应（聊天 + 工具）

每个回复或工具调用都会使用**当前模型提供商**（OpenAI、Anthropic 等）。这是
主要的使用和费用来源。

详见[模型](/providers/models)获取定价配置和[标记使用及费用](/token-use)获取显示信息。

### 2) 媒体理解（音频/图像/视频）

传入的媒体可以在回复运行之前进行摘要/转录。这会使用模型/提供商API。

- 音频：OpenAI / Groq / Deepgram（现在**存在密钥时自动启用**）。
- 图像：OpenAI / Anthropic / Google。
- 视频：Google。

详见[媒体理解](/nodes/media-understanding)。

### 3) 内存嵌入 + 语义搜索

语义内存搜索在配置为远程提供商时使用**嵌入API**：

- `memorySearch.provider = "openai"` → OpenAI 嵌入
- `memorySearch.provider = "gemini"` → Gemini 嵌入
- 如果本地嵌入失败，可选回退到 OpenAI

您可以将其保持本地，使用 `memorySearch.provider = "local"`（不使用API）。

详见[内存](/concepts/memory)。

### 4) 网络搜索工具（Brave / Perplexity 通过 OpenRouter）

`web_search` 使用API密钥并可能会产生使用费用：

- **Brave 搜索API**：`BRAVE_API_KEY` 或 `tools.web.search.apiKey`
- **Perplexity**（通过 OpenRouter）：`PERPLEXITY_API_KEY` 或 `OPENROUTER_API_KEY`

**Brave 免费层（慷慨的）：**

- **每月2,000次请求**
- **每秒1次请求**
- **需要信用卡**进行验证（除非升级，否则不收费）

详见[网络工具](/tools/web)。

### 5) 网络抓取工具（Firecrawl）

当存在API密钥时，`web_fetch` 可以调用 **Firecrawl**：

- `FIRECRAWL_API_KEY` 或 `tools.web.fetch.firecrawl.apiKey`

如果未配置Firecrawl，该工具将回退到直接抓取 + 可读性（无付费API）。

详见[网络工具](/tools/web)。

### 6) 提供商使用快照（状态/健康）

某些状态命令会调用**提供商使用端点**以显示配额窗口或认证健康状况。
这些通常是低流量调用，但仍会命中提供商API：

- `openclaw status --usage`
- `openclaw models status --json`

详见[模型 CLI](/cli/models)。

### 7) 压缩保护摘要

压缩保护可以使用**当前模型**对会话历史进行摘要，在运行时会调用提供商API。

详见[会话管理 + 压缩](/reference/session-management-compaction)。

### 8) 模型扫描 / 探测

`openclaw models scan` 可以探测 OpenRouter 模型，并在启用探测时使用 `OPENROUTER_API_KEY`。

详见[模型 CLI](/cli/models)。

### 9) Talk（语音）

Talk 模式在配置时可以调用 **ElevenLabs**：

- `ELEVENLABS_API_KEY` 或 `talk.apiKey`

详见[Talk 模式](/nodes/talk)。

### 10) 技能（第三方API）

技能可以在 `skills.entries.<name>.apiKey` 中存储 `apiKey`。如果技能使用该密钥进行外部
API调用，根据技能提供商的不同可能会产生费用。

详见[技能](/tools/skills)。