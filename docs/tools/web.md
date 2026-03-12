---
summary: "Web search + fetch tools (Perplexity Search API, Brave, Gemini, Grok, and Kimi providers)"
read_when:
  - You want to enable web_search or web_fetch
  - You need Perplexity or Brave Search API key setup
  - You want to use Gemini with Google Search grounding
title: "Web Tools"
---
# Web工具

OpenClaw提供了两个轻量级的Web工具：

- `web_search` — 使用Perplexity Search API、Brave Search API、Gemini（带有Google搜索基础）、Grok或Kimi进行网络搜索。
- `web_fetch` — HTTP获取 + 可读内容提取（HTML → markdown/text）。

这些**不是**浏览器自动化。对于JavaScript密集型网站或登录，请使用
[Browser工具](/tools/browser)。

## 工作原理

- `web_search` 调用您配置的服务提供商并返回结果。
- 结果按查询缓存15分钟（可配置）。
- `web_fetch` 执行简单的HTTP GET并提取可读内容
  （HTML → markdown/text）。它**不**执行JavaScript。
- 默认启用`web_fetch`（除非明确禁用）。

有关特定于提供商的详细信息，请参阅[Perplexity搜索设置](/perplexity)和[Brave搜索设置](/brave-search)。

## 选择搜索引擎提供商

| 提供商                  | 优点                                                                                          | 缺点                                        | API密钥                             |
| ------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------- | ----------------------------------- |
| **Perplexity Search API** | 快速、结构化结果；域名、语言、地区和新鲜度过滤器；内容提取 | —                                           | `PERPLEXITY_API_KEY`                |
| **Brave Search API**      | 快速、结构化结果                                                                      | 较少的过滤选项；适用AI使用条款 | `BRAVE_API_KEY`                     |
| **Gemini**                | Google搜索基础，AI合成                                                       | 需要Gemini API密钥                     | `GEMINI_API_KEY`                    |
| **Grok**                  | xAI网页基础回应                                                                    | 需要xAI API密钥                        | `XAI_API_KEY`                       |
| **Kimi**                  | Moonshot网页搜索能力                                                                | 需要Moonshot API密钥                   | `KIMI_API_KEY` / `MOONSHOT_API_KEY` |

### 自动检测

如果没有显式设置`provider`，OpenClaw将根据可用的API密钥自动检测使用哪个提供商，检查顺序如下：

1. **Brave** — `BRAVE_API_KEY` 环境变量或 `tools.web.search.apiKey` 配置
2. **Gemini** — `GEMINI_API_KEY` 环境变量或 `tools.web.search.gemini.apiKey` 配置
3. **Kimi** — `KIMI_API_KEY` / `MOONSHOT_API_KEY` 环境变量或 `tools.web.search.kimi.apiKey` 配置
4. **Perplexity** — `PERPLEXITY_API_KEY` 环境变量或 `tools.web.search.perplexity.apiKey` 配置
5. **Grok** — `XAI_API_KEY` 环境变量或 `tools.web.search.grok.apiKey` 配置

如果未找到密钥，则回退到Brave（您会收到一个缺少密钥的错误提示，要求您配置一个）。

## 设置网络搜索

使用`openclaw configure --section web`来设置您的API密钥并选择提供商。

### Perplexity搜索

1. 在[perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)创建一个Perplexity帐户
2. 在仪表板中生成API密钥
3. 运行`openclaw configure --section web`以在配置中存储密钥，或在您的环境中设置`PERPLEXITY_API_KEY`。

有关更多详细信息，请参阅[Perplexity搜索API文档](https://docs.perplexity.ai/guides/search-quickstart)。

### Brave搜索

1. 在[brave.com/search/api](https://brave.com/search/api/)创建一个Brave搜索API帐户
2. 在仪表板中，选择**Data for Search**计划（而不是“Data for AI”）并生成API密钥。
3. 运行`openclaw configure --section web`以在配置中存储密钥（推荐），或在您的环境中设置`BRAVE_API_KEY`。

Brave提供付费计划；请查看Brave API门户以获取当前限制和定价。

### 存储密钥的位置

**通过配置（推荐）：** 运行`openclaw configure --section web`。它将密钥存储在`tools.web.search.perplexity.apiKey`或`tools.web.search.apiKey`下。

**通过环境：** 在网关进程环境中设置`PERPLEXITY_API_KEY`或`BRAVE_API_KEY`。对于网关安装，请将其放入`~/.openclaw/.env`（或您的服务环境）。请参阅[环境变量](/help/faq#how-does-openclaw-load-environment-variables)。

### 配置示例

**Perplexity搜索：**

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        provider: "perplexity",
        perplexity: {
          apiKey: "pplx-...", // optional if PERPLEXITY_API_KEY is set
        },
      },
    },
  },
}
```

**Brave搜索：**

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        provider: "brave",
        apiKey: "YOUR_BRAVE_API_KEY", // optional if BRAVE_API_KEY is set // pragma: allowlist secret
      },
    },
  },
}
```

## 使用Gemini（Google搜索基础）

Gemini模型支持内置的[Google搜索基础](https://ai.google.dev/gemini-api/docs/grounding)，该功能返回由实时Google搜索结果支持的AI合成答案，并附有引用。

### 获取Gemini API密钥

1. 前往[Google AI Studio](https://aistudio.google.com/apikey)
2. 创建一个API密钥
3. 在网关环境中设置`GEMINI_API_KEY`，或配置`tools.web.search.gemini.apiKey`

### 设置Gemini搜索

```json5
{
  tools: {
    web: {
      search: {
        provider: "gemini",
        gemini: {
          // API key (optional if GEMINI_API_KEY is set)
          apiKey: "AIza...",
          // Model (defaults to "gemini-2.5-flash")
          model: "gemini-2.5-flash",
        },
      },
    },
  },
}
```

**环境替代方案：** 在网关环境中设置`GEMINI_API_KEY`。
对于网关安装，请将其放入`~/.openclaw/.env`。

### 注意事项

- Gemini基础中的引用URL会从Google的重定向URL自动解析为直接URL。
- 重定向解析使用SSRF防护路径（HEAD + 重定向检查 + http/https验证），然后再返回最终的引用URL。
- 重定向解析使用严格的SSRF默认设置，因此阻止了对私有/内部目标的重定向。
- 默认模型(`gemini-2.5-flash`)快速且经济高效。
  支持基础的任何Gemini模型都可以使用。

## web_search

使用您配置的提供商进行网络搜索。

### 要求

- `tools.web.search.enabled` 不得为 `false`（默认：启用）
- 您所选提供商的API密钥：
  - **Brave**: `BRAVE_API_KEY` 或 `tools.web.search.apiKey`
  - **Perplexity**: `PERPLEXITY_API_KEY` 或 `tools.web.search.perplexity.apiKey`
  - **Gemini**: `GEMINI_API_KEY` 或 `tools.web.search.gemini.apiKey`
  - **Grok**: `XAI_API_KEY` 或 `tools.web.search.grok.apiKey`
  - **Kimi**: `KIMI_API_KEY`, `MOONSHOT_API_KEY`, 或 `tools.web.search.kimi.apiKey`

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

除非另有说明，否则所有参数对Brave和Perplexity都有效。

| 参数             | 描述                                           |
| --------------------- | ----------------------------------------------------- |
| `query`               | 搜索查询（必需）                               |
| `count`               | 返回的结果数量（1-10，默认：5）                  |
| `country`             | 两位ISO国家代码（例如，“US”，“DE”）          |
| `language`            | ISO 639-1语言代码（例如，“en”，“de”）            |
| `freshness`           | 时间过滤：`day`, `week`, `month`, 或 `year`        |
| `date_after`          | 此日期之后的结果（YYYY-MM-DD）                  |
| `date_before`         | 此日期之前的结果（YYYY-MM-DD）                 |
| `ui_lang`             | UI语言代码（仅限Brave）                         |
| `domain_filter`       | 域名允许/拒绝列表数组（仅限Perplexity）     |
| `max_tokens`          | 总内容预算，默认25000（仅限Perplexity） |
| `max_tokens_per_page` | 每页令牌限制，默认2048（仅限Perplexity）  |

**示例：**

```javascript
// German-specific search
await web_search({
  query: "TV online schauen",
  country: "DE",
  language: "de",
});

// Recent results (past week)
await web_search({
  query: "TMBG interview",
  freshness: "week",
});

// Date range search
await web_search({
  query: "AI developments",
  date_after: "2024-01-01",
  date_before: "2024-06-30",
});

// Domain filtering (Perplexity only)
await web_search({
  query: "climate research",
  domain_filter: ["nature.com", "science.org", ".edu"],
});

// Exclude domains (Perplexity only)
await web_search({
  query: "product reviews",
  domain_filter: ["-reddit.com", "-pinterest.com"],
});

// More content extraction (Perplexity only)
await web_search({
  query: "detailed AI research",
  max_tokens: 50000,
  max_tokens_per_page: 4096,
});
```

## web_fetch

获取URL并提取可读内容。

### web_fetch要求

- `tools.web.fetch.enabled` 不得为 `false`（默认：启用）
- 可选的Firecrawl后备：设置`tools.web.fetch.firecrawl.apiKey`或`FIRECRAWL_API_KEY`。

### web_fetch配置

### web_fetch 工具参数

- `url`（必需，仅支持http/https）
- `extractMode` (`markdown` | `text`)
- `maxChars`（截断长页面）

注意事项：

- `web_fetch` 首先使用Readability（主要内容提取），然后使用Firecrawl（如果已配置）。如果两者都失败，工具将返回错误。
- Firecrawl请求默认使用绕过机器人检测模式，并缓存结果。
- `web_fetch` 默认发送类似Chrome的User-Agent和`Accept-Language`；如有需要，可以覆盖`userAgent`。
- `web_fetch` 会阻止私有/内部主机名并重新检查重定向（可以通过`maxRedirects` 限制）。
- `maxChars` 被限制在`tools.web.fetch.maxCharsCap`。
- `web_fetch` 在解析前将下载的响应体大小限制为`tools.web.fetch.maxResponseBytes`；超出大小的响应会被截断，并附带警告。
- `web_fetch` 是尽力而为的提取；某些网站可能需要浏览器工具。
- 有关关键设置和服务详情，请参阅[Firecrawl](/tools/firecrawl)。
- 响应被缓存（默认15分钟），以减少重复获取。
- 如果您使用工具配置文件/允许列表，请添加`web_search`/`web_fetch` 或 `group:web`。
- 如果缺少API密钥，`web_search` 将返回一个简短的设置提示，并附带文档链接。