---
summary: "Web search + fetch tools (Brave Search API, Perplexity direct/OpenRouter)"
read_when:
  - You want to enable web_search or web_fetch
  - You need Brave Search API key setup
  - You want to use Perplexity Sonar for web search
title: "Web Tools"
---
# Web 工具

OpenClaw 提供两个轻量级的 Web 工具：

- `web_search` — 通过 Brave Search API（默认）或 Perplexity Sonar（直接或通过 OpenRouter）进行网页搜索。
- `web_fetch` — HTTP 获取 + 可读内容提取（HTML → markdown/文本）。

这些 **不是** 浏览器自动化工具。对于需要大量 JavaScript 或登录的网站，请使用
[浏览器工具](/tools/browser)。

## 工作原理

- `web_search` 调用你配置的服务提供商并返回结果。
  - **Brave**（默认）：返回结构化结果（标题、URL、摘要）。
  - **Perplexity**：返回带有实时网络搜索引用的 AI 合成答案。
- 结果按查询缓存 15 分钟（可配置）。
- `web_fetch` 执行普通的 HTTP GET 并提取可读内容
  （HTML → markdown/文本）。它 **不** 执行 JavaScript。
- `web_fetch` 默认启用（除非显式禁用）。

## 选择搜索服务提供商

| 提供商            | 优点                                         | 缺点                                     | API 密钥                                      |
| ------------------- | -------------------------------------------- | ---------------------------------------- | -------------------------------------------- |
| **Brave**（默认） | 快速、结构化结果、免费层级          | 传统的搜索结果               | `BRAVE_API_KEY`                              |
| **Perplexity**      | AI 合成的答案、引用、实时 | 需要 Perplexity 或 OpenRouter 访问 | `OPENROUTER_API_KEY` 或 `PERPLEXITY_API_KEY` |

有关提供商特定详细信息，请参阅 [Brave Search 设置](/brave-search) 和 [Perplexity Sonar](/perplexity)。

在配置中设置提供商：

```json5
{
  tools: {
    web: {
      search: {
        provider: "brave", // or "perplexity"
      },
    },
  },
}
```

示例：切换到 Perplexity Sonar（直接 API）：

```json5
{
  tools: {
    web: {
      search: {
        provider: "perplexity",
        perplexity: {
          apiKey: "pplx-...",
          baseUrl: "https://api.perplexity.ai",
          model: "perplexity/sonar-pro",
        },
      },
    },
  },
}
```

## 获取 Brave API 密钥

1. 在 https://brave.com/search/api/ 创建一个 Brave Search API 账户
2. 在仪表板中选择 **Data for Search** 计划（不是“Data for AI”），然后生成 API 密钥。
3. 运行 `openclaw configure --section web` 将密钥存储在配置中（推荐），或者在环境中设置 `BRAVE_API_KEY`。

Brave 提供免费层级以及付费计划；请查看 Brave API 门户以获取当前限制和定价信息。

### 设置密钥的位置（推荐）

**推荐：** 运行 `openclaw configure --section web`。它将密钥存储在
`~/.openclaw/openclaw.json` 下的 `tools.web.search.apiKey`。

**环境替代方案：** 在网关进程环境中设置 `BRAVE_API_KEY`。对于网关安装，将其放入 `~/.openclaw/.env`（或你的服务环境）。参阅 [环境变量](/help/faq#how-does-openclaw-load-environment-variables)。

## 使用 Perplexity（直接或通过 OpenRouter）

Perplexity Sonar 模型具有内置的网络搜索功能，并返回带有引用的 AI 合成答案。你可以通过 OpenRouter 使用它们（无需信用卡支持加密/预付款）。

### 获取 OpenRouter API 密钥

1. 在 https://openrouter.ai/ 创建一个账户
2. 添加信用额度（支持加密、预付款或信用卡）
3. 在账户设置中生成 API 密钥

### 设置 Perplexity 搜索

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        provider: "perplexity",
        perplexity: {
          // API key (optional if OPENROUTER_API_KEY or PERPLEXITY_API_KEY is set)
          apiKey: "sk-or-v1-...",
          // Base URL (key-aware default if omitted)
          baseUrl: "https://openrouter.ai/api/v1",
          // Model (defaults to perplexity/sonar-pro)
          model: "perplexity/sonar-pro",
        },
      },
    },
  },
}
```

**环境替代方案：** 在网关环境中设置 `OPENROUTER_API_KEY` 或 `PERPLEXITY_API_KEY`。对于网关安装，将其放入 `~/.openclaw/.env`。

如果没有设置基础 URL，OpenClaw 将根据 API 密钥来源选择默认值：

- `PERPLEXITY_API_KEY` 或 `pplx-...` → `https://api.perplexity.ai`
- `OPENROUTER_API_KEY` 或 `sk-or-...` → `https://openrouter.ai/api/v1`
- 未知密钥格式 → OpenRouter（安全回退）

### 可用的 Perplexity 模型

| 模型                            | 描述                          | 最佳用途          |
| -------------------------------- | ------------------------------------ | ----------------- |
| `perplexity/sonar`               | 带有网络搜索的快速问答             | 快速查找     |
| `perplexity/sonar-pro`（默认） | 带有网络搜索的多步骤推理 | 复杂问题 |
| `perplexity/sonar-reasoning-pro` | 思维链分析            | 深度研究     |

## web_search

使用你配置的服务提供商进行网络搜索。

### 要求

- `tools.web.search.enabled` 必须不是 `false`（默认：启用）
- 你选择的服务提供商的 API 密钥：
  - **Brave**：`BRAVE_API_KEY` 或 `tools.web.search.apiKey`
  - **Perplexity**：`OPENROUTER_API_KEY`，`PERPLEXITY_API_KEY`，或 `tools.web.search.perplexity.apiKey`

### 配置

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "BRAVE_API_KEY_HERE", // optional if BRAVE_API_KEY is set
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
    },
  },
}
```

### 工具参数

- `query`（必需）
- `count`（1–10；默认来自配置）
- `country`（可选）：用于区域特定结果的两位字母国家代码（例如，“DE”，“US”，“ALL”）。如果省略，Brave 将选择其默认区域。
- `search_lang`（可选）：搜索结果的 ISO 语言代码（例如，“de”，“en”，“fr”）
- `ui_lang`（可选）：UI 元素的 ISO 语言代码
- `freshness`（可选，仅限 Brave）：按发现时间过滤 (`pd`，`pw`，`pm`，`py`，或 `YYYY-MM-DDtoYYYY-MM-DD`)

**示例：**

```javascript
// German-specific search
await web_search({
  query: "TV online schauen",
  count: 10,
  country: "DE",
  search_lang: "de",
});

// French search with French UI
await web_search({
  query: "actualités",
  country: "FR",
  search_lang: "fr",
  ui_lang: "fr",
});

// Recent results (past week)
await web_search({
  query: "TMBG interview",
  freshness: "pw",
});
```

## web_fetch

获取 URL 并提取可读内容。

### 要求

- `tools.web.fetch.enabled` 必须不是 `false`（默认：启用）
- 可选的 Firecrawl 回退：设置 `tools.web.fetch.firecrawl.apiKey` 或 `FIRECRAWL_API_KEY`。

### 配置

```json5
{
  tools: {
    web: {
      fetch: {
        enabled: true,
        maxChars: 50000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        maxRedirects: 3,
        userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        readability: true,
        firecrawl: {
          enabled: true,
          apiKey: "FIRECRAWL_API_KEY_HERE", // optional if FIRECRAWL_API_KEY is set
          baseUrl: "https://api.firecrawl.dev",
          onlyMainContent: true,
          maxAgeMs: 86400000, // ms (1 day)
          timeoutSeconds: 60,
        },
      },
    },
  },
}
```

### 工具参数

- `url`（必需，仅限 http/https）
- `extractMode` (`markdown` | `text`)
- `maxChars`（截断长页面）

注意事项：

- `web_fetch` 首先使用 Readability（主要内容提取），然后使用 Firecrawl（如果已配置）。如果两者都失败，工具将返回错误。
- Firecrawl 请求使用反机器人模式并默认缓存结果。
- `web_fetch` 发送类似 Chrome 的 User-Agent 并默认使用 `Accept-Language`；如有需要，请覆盖 `userAgent`。
- `web_fetch` 阻止私有/内部主机名并重新检查重定向（使用 `maxRedirects` 限制）。
- `web_fetch` 是尽力提取；某些网站可能需要浏览器工具。
- 有关密钥设置和服务详细信息，请参阅 [Firecrawl](/tools/firecrawl)。
- 响应默认缓存 15 分钟以减少重复获取。
- 如果你使用工具配置文件/白名单，请添加 `web_search`/`web_fetch` 或 `group:web`。
- 如果缺少 Brave 密钥，`web_search` 返回一个包含文档链接的简短设置提示。