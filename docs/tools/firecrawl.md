---
summary: "Firecrawl fallback for web_fetch (anti-bot + cached extraction)"
read_when:
  - You want Firecrawl-backed web extraction
  - You need a Firecrawl API key
  - You want anti-bot extraction for web_fetch
title: "Firecrawl"
---
# Firecrawl

OpenClaw 可以使用 **Firecrawl** 作为 `web_fetch` 的备用提取器。它是一个托管的内容提取服务，支持绕过机器人检测和缓存，有助于处理大量使用 JavaScript 的网站或阻止纯 HTTP 请求的页面。

## 获取 API 密钥

1. 创建一个 Firecrawl 账户并生成一个 API 密钥。
2. 将其存储在配置中或在网关环境中设置 `FIRECRAWL_API_KEY`。

## 配置 Firecrawl

```json5
{
  tools: {
    web: {
      fetch: {
        firecrawl: {
          apiKey: "FIRECRAWL_API_KEY_HERE",
          baseUrl: "https://api.firecrawl.dev",
          onlyMainContent: true,
          maxAgeMs: 172800000,
          timeoutSeconds: 60,
        },
      },
    },
  },
}
```

注意事项：

- 当存在 API 密钥时，`firecrawl.enabled` 默认为 true。
- `maxAgeMs` 控制缓存结果可以有多旧（毫秒）。默认为 2 天。

## 隐蔽 / 绕过机器人检测

Firecrawl 提供了一个 **代理模式** 参数用于绕过机器人检测 (`basic`, `stealth`, 或 `auto`)。
OpenClaw 总是使用 `proxy: "auto"` 加上 `storeInCache: true` 进行 Firecrawl 请求。
如果省略了代理，Firecrawl 默认使用 `auto`。`auto` 如果基本尝试失败，则会重试使用隐蔽代理，这可能比仅使用基本抓取消耗更多的信用额度。

## `web_fetch` 如何使用 Firecrawl

`web_fetch` 提取顺序：

1. Readability（本地）
2. Firecrawl（如果已配置）
3. 基本 HTML 清理（最后的备用）

请参阅 [Web 工具](/tools/web) 获取完整的 Web 工具设置。