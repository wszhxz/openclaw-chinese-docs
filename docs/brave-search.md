---
summary: "Brave Search API setup for web_search"
read_when:
  - You want to use Brave Search for web_search
  - You need a BRAVE_API_KEY or plan details
title: "Brave Search (legacy path)"
---
# Brave Search API

OpenClaw 将 Brave Search API 作为 `web_search` 提供商支持。

## 获取 API 密钥

1. 在 [https://brave.com/search/api/](https://brave.com/search/api/) 创建 Brave Search API 账户
2. 在仪表板中，选择 **Search** 计划并生成 API 密钥。
3. 将密钥存储在配置中，或在网关环境中设置 `BRAVE_API_KEY`。

## 配置示例

```json5
{
  plugins: {
    entries: {
      brave: {
        config: {
          webSearch: {
            apiKey: "BRAVE_API_KEY_HERE",
            mode: "web", // or "llm-context"
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "brave",
        maxResults: 5,
        timeoutSeconds: 30,
      },
    },
  },
}
```

特定于提供程序的 Brave 搜索设置现在位于 `plugins.entries.brave.config.webSearch.*` 下。
传统的 `tools.web.search.apiKey` 仍通过兼容性层加载，但它不再是标准的配置路径。

`webSearch.mode` 控制 Brave 传输：

- `web`（默认）：带有标题、URL 和摘要的正常 Brave 网页搜索
- `llm-context`：Brave LLM Context API，包含预提取的文本块和用于溯源的来源

## 工具参数

| 参数     | 描述                                                         |
| ------------- | ------------------------------------------------------------------- |
| `query`       | 搜索查询（必需）                                             |
| `count`       | 返回结果的数量（1-10，默认值：5）                      |
| `country`     | 2 位 ISO 国家代码（例如："US"，"DE"）                        |
| `language`    | 搜索结果的语言代码（ISO 639-1，例如："en"，"de"，"fr"） |
| `search_lang` | Brave 搜索语言代码（例如：`en`，`en-gb`，`zh-hans`）         |
| `ui_lang`     | UI 元素的 ISO 语言代码                                   |
| `freshness`   | 时间过滤器：`day`（24 小时），`week`，`month`，或 `year`                |
| `date_after`  | 仅发布在此日期之后的结果（YYYY-MM-DD）                 |
| `date_before` | 仅发布在此日期之前的结果（YYYY-MM-DD）                |

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

- OpenClaw 使用 Brave **Search** 计划。如果您拥有传统订阅（例如每月 2,000 次查询的原始免费计划），它仍然有效，但不包括较新的功能，如 LLM Context 或更高的速率限制。
- 每个 Brave 计划都包含 **每月 5 美元的免费额度**（可续期）。Search 计划每 1,000 次请求收费 5 美元，因此该额度覆盖每月 1,000 次查询。请在 Brave 仪表板中设置使用限制以避免意外费用。有关当前计划，请参阅 [Brave API 门户](https://brave.com/search/api/)。
- Search 计划包含 LLM Context 端点和 AI 推理权限。存储结果以训练或调整模型需要具有明确存储权限的计划。请参阅 Brave [服务条款](https://api-dashboard.search.brave.com/terms-of-service)。
- `llm-context` 模式返回定位来源条目，而不是正常的网页搜索摘要格式。
- `llm-context` 模式不支持 `ui_lang`，`freshness`，`date_after` 或 `date_before`。
- `ui_lang` 必须包含像 `en-US` 这样的区域子标签。
- 结果默认缓存 15 分钟（可通过 `cacheTtlMinutes` 配置）。

有关完整的 web_search 配置，请参阅 [Web 工具](/tools/web)。