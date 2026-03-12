---
summary: "Perplexity Search API setup for web_search"
read_when:
  - You want to use Perplexity Search for web search
  - You need PERPLEXITY_API_KEY setup
title: "Perplexity Search"
---
# Perplexity 搜索 API

OpenClaw 在启用 `web_search` 工具且 `provider: "perplexity"` 被设置时，使用 Perplexity 搜索 API。  
Perplexity 搜索返回结构化结果（标题、URL、摘要），适用于快速研究。

## 获取 Perplexity API 密钥

1. 在 <https://www.perplexity.ai/settings/api> 创建一个 Perplexity 账户  
2. 在控制台中生成一个 API 密钥  
3. 将密钥存储在配置文件中（推荐），或在 Gateway 环境中设置 `PERPLEXITY_API_KEY`。

## 配置示例

```json5
{
  tools: {
    web: {
      search: {
        provider: "perplexity",
        perplexity: {
          apiKey: "pplx-...",
        },
      },
    },
  },
}
```

## 从 Brave 切换过来

```json5
{
  tools: {
    web: {
      search: {
        provider: "perplexity",
        perplexity: {
          apiKey: "pplx-...",
        },
      },
    },
  },
}
```

## 密钥设置位置（推荐）

**推荐方式：** 运行 `openclaw configure --section web`。它会将密钥存储在  
`~/.openclaw/openclaw.json` 下的 `tools.web.search.perplexity.apiKey` 中。

**环境变量替代方式：** 在 Gateway 进程环境中设置 `PERPLEXITY_API_KEY`。对于已安装的 gateway，将其放入 `~/.openclaw/.env`（或您的服务环境）中。参见 [环境变量](/help/faq#how-does-openclaw-load-environment-variables)。

## 工具参数

| 参数                  | 描述                                                  |
| --------------------- | ----------------------------------------------------- |
| `query`               | 搜索查询（必需）                                      |
| `count`               | 返回结果数量（1–10，默认值：5）                       |
| `country`             | 两位字母 ISO 国家代码（例如："US"、"DE"）            |
| `language`            | ISO 639-1 语言代码（例如："en"、"de"、"fr"）         |
| `freshness`           | 时间筛选器：`day`（24 小时）、`week`、`month` 或 `year` |
| `date_after`          | 仅返回此日期之后发布的结果（YYYY-MM-DD）              |
| `date_before`         | 仅返回此日期之前发布的结果（YYYY-MM-DD）              |
| `domain_filter`       | 域名白名单/黑名单数组（最多 20 个）                   |
| `max_tokens`          | 总内容预算（默认值：25000，最大值：1000000）         |
| `max_tokens_per_page` | 每页 Token 限制（默认值：2048）                      |

**示例：**

```javascript
// Country and language-specific search
await web_search({
  query: "renewable energy",
  country: "DE",
  language: "de",
});

// Recent results (past week)
await web_search({
  query: "AI news",
  freshness: "week",
});

// Date range search
await web_search({
  query: "AI developments",
  date_after: "2024-01-01",
  date_before: "2024-06-30",
});

// Domain filtering (allowlist)
await web_search({
  query: "climate research",
  domain_filter: ["nature.com", "science.org", ".edu"],
});

// Domain filtering (denylist - prefix with -)
await web_search({
  query: "product reviews",
  domain_filter: ["-reddit.com", "-pinterest.com"],
});

// More content extraction
await web_search({
  query: "detailed AI research",
  max_tokens: 50000,
  max_tokens_per_page: 4096,
});
```

### 域名过滤规则

- 每个过滤器最多支持 20 个域名  
- 同一请求中不得混合使用白名单与黑名单  
- 黑名单条目需使用 `-` 前缀（例如：`["-reddit.com"]`）

## 注意事项

- Perplexity 搜索 API 返回结构化的网页搜索结果（标题、URL、摘要）  
- 结果默认缓存 15 分钟（可通过 `cacheTtlMinutes` 配置）

请参阅 [网络工具](/tools/web) 查看完整的 `web_search` 配置。  
更多详情，请参阅 [Perplexity 搜索 API 文档](https://docs.perplexity.ai/docs/search/quickstart)。