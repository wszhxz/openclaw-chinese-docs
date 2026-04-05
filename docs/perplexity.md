---
summary: "Perplexity Search API and Sonar/OpenRouter compatibility for web_search"
read_when:
  - You want to use Perplexity Search for web search
  - You need PERPLEXITY_API_KEY or OPENROUTER_API_KEY setup
title: "Perplexity Search (legacy path)"
---
# Perplexity Search API

OpenClaw 支持将 Perplexity Search API 作为 `web_search` 提供者。
它返回包含 `title`、`url` 和 `snippet` 字段的结构化结果。

为了兼容性，OpenClaw 还支持传统的 Perplexity Sonar/OpenRouter 设置。
如果您使用 `OPENROUTER_API_KEY`、在 `plugins.entries.perplexity.config.webSearch.apiKey` 中使用 `sk-or-...` 密钥，或设置 `plugins.entries.perplexity.config.webSearch.baseUrl` / `model`，提供商将切换到 chat-completions 路径，并返回带有引用的 AI 合成答案，而不是结构化的 Search API 结果。

## 获取 Perplexity API 密钥

1. 在 [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api) 创建 Perplexity 账户
2. 在仪表板中生成 API 密钥
3. 将密钥存储在配置中，或在 Gateway 环境中设置 `PERPLEXITY_API_KEY`。

## OpenRouter 兼容性

如果您之前已为 Perplexity Sonar 使用 OpenRouter，请保留 `provider: "perplexity"`，并在 Gateway 环境中设置 `OPENROUTER_API_KEY`，或在 `plugins.entries.perplexity.config.webSearch.apiKey` 中存储 `sk-or-...` 密钥。

可选的兼容性控制：

- `plugins.entries.perplexity.config.webSearch.baseUrl`
- `plugins.entries.perplexity.config.webSearch.model`

## 配置示例

### 原生 Perplexity Search API

```json5
{
  plugins: {
    entries: {
      perplexity: {
        config: {
          webSearch: {
            apiKey: "pplx-...",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "perplexity",
      },
    },
  },
}
```

### OpenRouter / Sonar 兼容性

```json5
{
  plugins: {
    entries: {
      perplexity: {
        config: {
          webSearch: {
            apiKey: "<openrouter-api-key>",
            baseUrl: "https://openrouter.ai/api/v1",
            model: "perplexity/sonar-pro",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "perplexity",
      },
    },
  },
}
```

## 在哪里设置密钥

**通过配置：**运行 `openclaw configure --section web`。它将密钥存储在 `plugins.entries.perplexity.config.webSearch.apiKey` 下的 `~/.openclaw/openclaw.json` 中。该字段也接受 SecretRef 对象。

**通过环境变量：**在 Gateway 进程环境中设置 `PERPLEXITY_API_KEY` 或 `OPENROUTER_API_KEY`。对于网关安装，将其放入 `~/.openclaw/.env`（或您的服务环境）。请参阅 [Env vars](/help/faq#env-vars-and-env-loading)。

如果配置了 `provider: "perplexity"` 且 Perplexity 密钥 SecretRef 未解析且没有环境变量回退，启动/重载将快速失败。

## 工具参数

这些参数适用于原生 Perplexity Search API 路径。

| 参数             | 描述                                          |
| --------------------- | ---------------------------------------------------- |
| `query`               | 搜索查询（必填）                              |
| `count`               | 返回结果数量（1-10，默认值：5）       |
| `country`             | 2 字母 ISO 国家代码（例如："US", "DE"）         |
| `language`            | ISO 639-1 语言代码（例如："en", "de", "fr"）     |
| `freshness`           | 时间过滤器：`day`（24 小时）、`week`、`month` 或 `year` |
| `date_after`          | 仅返回在此日期之后发布的结果（YYYY-MM-DD）  |
| `date_before`         | 仅返回在此日期之前发布的结果（YYYY-MM-DD） |
| `domain_filter`       | 域名允许列表/拒绝列表数组（最多 20 个）             |
| `max_tokens`          | 总内容预算（默认值：25000，最大值：1000000）  |
| `max_tokens_per_page` | 每页令牌限制（默认值：2048）                 |

对于传统的 Sonar/OpenRouter 兼容路径：

- 接受 `query`、`count` 和 `freshness`
- `count` 仅用于兼容性；响应仍然是带有引用的单个合成答案，而不是 N 结果列表
- 仅限 Search API 的过滤器，如 `country`、`language`、`date_after`、`date_before`、`domain_filter`、`max_tokens` 和 `max_tokens_per_page` 将返回明确错误

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

### 域名过滤器规则

- 每个过滤器最多 20 个域名
- 不能在同一个请求中混合使用允许列表和拒绝列表
- 对拒绝列表条目使用 `-` 前缀（例如：`["-reddit.com"]`）

## 注意事项

- Perplexity Search API 返回结构化的 Web 搜索结果（`title`、`url`、`snippet`）
- OpenRouter 或明确的 `plugins.entries.perplexity.config.webSearch.baseUrl` / `model` 会将 Perplexity 切换回 Sonar chat completions 以进行兼容性处理
- Sonar/OpenRouter 兼容性返回带有引用的单个合成答案，而非结构化结果行
- 结果默认缓存 15 分钟（可通过 `cacheTtlMinutes` 配置）

有关完整的 web_search 配置，请参阅 [Web tools](/tools/web)。
有关更多详细信息，请参阅 [Perplexity Search API docs](https://docs.perplexity.ai/docs/search/quickstart)。