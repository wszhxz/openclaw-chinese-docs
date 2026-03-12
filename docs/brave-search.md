---
summary: "Brave Search API setup for web_search"
read_when:
  - You want to use Brave Search for web_search
  - You need a BRAVE_API_KEY or plan details
title: "Brave Search"
---
# Brave Search API

OpenClaw 支持将 Brave Search 作为 ``web_search`` 的网络搜索服务提供商。

## 获取 API 密钥

1. 在 [https://brave.com/search/api/](https://brave.com/search/api/) 创建一个 Brave Search API 账户。  
2. 在控制台中，选择 **Data for Search** 套餐并生成一个 API 密钥。  
3. 将密钥存储在配置文件中（推荐），或在网关环境中设置 ``BRAVE_API_KEY``。

## 配置示例

````json5
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
````

## 工具参数

| 参数 | 描述 |
| ------ | ---- |
| ``query`` | 搜索查询（必需） |
| ``count`` | 返回结果数量（1–10，默认为 5） |
| ``country`` | 两位字母 ISO 国家代码（例如："US"、"DE"） |
| ``language`` | 搜索结果所用的 ISO 639-1 语言代码（例如："en"、"de"、"fr"） |
| ``ui_lang`` | 用户界面元素所用的 ISO 语言代码 |
| ``freshness`` | 时间筛选器：``day``（24 小时）、``week``、``month`` 或 ``year`` |
| ``date_after`` | 仅返回此日期之后发布的搜索结果（YYYY-MM-DD 格式） |
| ``date_before`` | 仅返回此日期之前发布的搜索结果（YYYY-MM-DD 格式） |

**示例：**

````javascript
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
````

## 注意事项

- **Data for AI** 套餐 **不兼容** ``web_search``。  
- Brave 提供付费套餐；请查阅 Brave API 门户以了解当前配额限制。  
- Brave 服务条款对搜索结果在某些人工智能相关场景下的使用作出了限制。请审阅 Brave 服务条款，并确认您的预期用途符合规定。如涉及法律问题，请咨询您的法律顾问。  
- 结果默认缓存 15 分钟（可通过 ``cacheTtlMinutes`` 进行配置）。

有关完整的 `web_search` 配置，请参阅 [Web 工具](/tools/web)。