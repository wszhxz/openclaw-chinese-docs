---
summary: "Brave Search API setup for web_search"
read_when:
  - You want to use Brave Search for web_search
  - You need a BRAVE_API_KEY or plan details
title: "Brave Search"
---
# Brave 搜索 API

OpenClaw 使用 Brave 搜索作为`web_search`的默认提供商。

## 获取 API 密钥

1. 在 https://brave.com/search/api/ 创建 Brave 搜索 API 账户。
2. 在仪表板中选择 **Data for Search** 计划并生成 API 密钥。
3. 将密钥存储在配置中（推荐）或在网关环境变量中设置 `BRAVE_API_KEY`。

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

## 注意事项

- **Data for AI** 计划 **不兼容** `web_search`。
- Brave 提供免费层级和付费计划；请查看 Brave API 门户以获取当前限制信息。

查看 [Web 工具](/tools/web) 以获取完整的 web_search 配置。