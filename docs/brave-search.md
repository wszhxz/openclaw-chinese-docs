---
summary: "Brave Search API setup for web_search"
read_when:
  - You want to use Brave Search for web_search
  - You need a BRAVE_API_KEY or plan details
title: "Brave Search"
---
# Brave Search API

OpenClaw 支持将 Brave Search 作为 `web_search` 的 Web 搜索提供商。

## 获取 API 密钥

1. 在 [https://brave.com/search/api/](https://brave.com/search/api/) 创建 Brave Search API 账户
2. 在仪表板中，选择 **Data for Search** 计划并生成 API 密钥。
3. 将密钥存储在配置中（推荐），或在网关环境中设置 `BRAVE_API_KEY`。

## 配置示例

```json5
{
  tools: {
    web: {
      search: {
        provider: "brave",
        apiKey: "BRAVE_API_KEY_HERE",
        maxResults: 5,
        timeoutSeconds: 30,
      },
    },
  },
}
```

## 工具参数

| 参数 | 描述 |
| --- | --- |
| `query` | 搜索查询（必需） |
| `count` | 返回结果的数量（1-10，默认：5） |
| `country` | 2 字母 ISO 国家代码（例如："US"、"DE"） |
| `language` | 搜索结果的语言代码（ISO 639-1，例如："en"、"de"、"fr"） |
| `ui_lang` | UI 元素的 ISO 语言代码 |
| `freshness` | 时间过滤器：`day`（24 小时）、`week`、`month` 或 `year` |
| `date_after` | 仅发布于此日期之后的结果（YYYY-MM-DD） |
| `date_before` | 仅发布于此日期之前的结果（YYYY-MM-DD） |

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
```

## 注意事项

- Data for AI 计划与 `web_search` **不**兼容。
- Brave 提供付费计划；请查看 Brave API 门户以了解当前限制。
- Brave 条款包含对搜索结果某些 AI 相关使用的限制。请审查 Brave 服务条款并确认您的预期用途符合规定。如有法律问题，请咨询法律顾问。
- 结果默认缓存 15 分钟（可通过 `cacheTtlMinutes` 配置）。

有关完整的 web_search 配置，请参阅 [Web tools](/tools/web)。