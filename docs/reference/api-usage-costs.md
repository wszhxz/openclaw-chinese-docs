---
summary: "Audit what can spend money, which keys are used, and how to view usage"
read_when:
  - You want to understand which features may call paid APIs
  - You need to audit keys, costs, and usage visibility
  - You’re explaining /status or /usage cost reporting
title: "API Usage and Costs"
---
# API 使用与费用

此文档列出**可以调用 API 密钥的功能**以及其费用显示的位置。重点介绍
可以生成提供商使用或付费 API 调用的 OpenClaw 功能。

## 费用显示位置（聊天 + CLI）

**每会话费用快照**

- `/status` 显示当前会话的模型、上下文使用情况以及最后响应的 token。
- 如果模型使用 **API 密钥认证**，`/status` 还会显示 **预估费用**（仅限 API 密钥）。

**每条消息费用页脚**

- `/usage full` 会在每条回复后附加使用页脚，包括 **预估费用**（仅限 API 密钥）。
- `/usage tokens` 仅显示 token；OAuth 流程隐藏美元费用。

**CLI 使用窗口（提供商配额）**

- `openclaw status --usage` 和 `openclaw channels list` 显示提供商 **使用窗口**
  （配额快照，非每条消息费用）。

详情和示例请参见 [Token 使用与费用](/token-use)。

## 密钥如何被发现

OpenClaw 可以从以下来源获取凭证：

- **认证配置文件**（按代理存储在 `auth-profiles.json`）。
- **环境变量**（例如 `OPENAI_API_KEY`、`BRAVE_API_KEY`、`FIRECRAWL_API_KEY`）。
- **配置**（`models.providers.*.apiKey`、`tools.web.search.*`、`tools.web.fetch.firecrawl.*`、
  `memorySearch.*`、`talk.apiKey`）。
- **技能**（`skills.entries.<name>.apiKey`），可能将密钥导出到技能进程环境变量中。

## 可能消耗密钥的功能

### 1) 核心模型响应（聊天 + 工具）

每次回复或工具调用都使用 **当前模型提供商**（如 OpenAI、Anthropic 等）。这是
主要的使用和费用来源。

定价配置请参见 [模型](/providers/models)，显示详情请参见 [Token 使用与费用](/token-use)。

### 2) 多媒体理解（音频/图像/视频）

在回复运行前，可以对传入的多媒体进行摘要或转录。这使用模型/提供商 API。

- 音频：OpenAI / Groq / Deepgram（当存在密钥时现在 **自动启用**）。
- 图像：OpenAI / Anthropic / Google。
- 视频：Google。

详情请参见 [多媒体理解](/nodes/media-understanding)。

### 3) 内存嵌入 + 语义搜索

语义内存搜索在配置为远程提供商时使用 **嵌入 API**：

- `memorySearch.provider = "openai"` → OpenAI 嵌入
- `memorySearch.provider = "gemini"` → Gemini 嵌入
- 可选地，如果本地嵌入失败则回退到 OpenAI

您可以通过 `memorySearch.provider = "local"` 保持本地（无 API 使用）。

详情请参见 [内存](/concepts/memory)。

### 4) 网络搜索工具（Brave / Perplexity 通过 OpenRouter）

`web_search` 使用 API 密钥，可能会产生使用费用：

- **Brave 搜索 API**：`BRAVE_API_KEY` 或 `tools.web.search.apiKey`
- **Perplexity**（通过 OpenRouter）：`PERPLEXITY_API_KEY` 或 `OPENROUTER_API_KEY`

**Brave 免费层级（慷慨）：**

- **每月 2,000 次请求**
- **每秒 1 次请求**
- **需要信用卡验证**（除非升级，否则不收费）

详情请参见 [网络工具](/tools/web)。

### 5) 网络获取工具（Firecrawl）

`web_fetch` 在存在 API 密钥时可以调用 **Firecrawl**：

- `FIRECRAWL_API_KEY` 或 `tools.web.fetch.firecrawl.apiKey`

如果未配置 Firecrawl，工具将回退到直接获取 + 可读性（无付费 API）。

详情请参见 [网络工具](/tools/web)。

### 6) 提供商使用快照（状态/健康）

某些状态命令调用 **提供商使用端点** 来显示配额窗口或认证健康状况。
这些通常是低流量调用，但仍会调用提供商 API：

- `openclaw status --usage`
- `openclaw models status --json`

详情请参见 [模型 CLI](/cli/models)。

### 7) 压缩保护摘要

压缩保护可以使用 **当前模型** 摘要会话历史，这在运行时会调用提供商 API。

详情请参见 [会话管理 + 压缩](/reference/session-management-compaction)。

### 8) 模型扫描 / 探测

`openclaw models scan` 可以探测 OpenRouter 模型，并在启用探测时使用 `OPENROUTER_API_KEY`。

详情请参见 [模型 CLI](/cli/models)。

### 9) 语音（Talk 模式）

Talk 模式在配置时可以调用 **ElevenLabs**：

- `ELEVENLABS_API_KEY` 或 `talk.apiKey`

详情请参见 [Talk 模式](/nodes/talk)。

### 10) 技能（第三方 API）

技能可以将 `apiKey` 存储在 `skills.entries.<name>.apiKey`。如果技能使用该密钥调用外部 API，则会根据技能提供商产生费用。

详情请参见 [技能](/tools/skills)。