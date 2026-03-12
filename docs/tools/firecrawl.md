---
summary: "Firecrawl fallback for web_fetch (anti-bot + cached extraction)"
read_when:
  - You want Firecrawl-backed web extraction
  - You need a Firecrawl API key
  - You want anti-bot extraction for web_fetch
title: "Firecrawl"
---
# Firecrawl

OpenClaw 可以使用 **Firecrawl** 作为 `web_fetch` 的备用提取器。它是一个托管的内容提取服务，支持绕过机器人检测和缓存，这有助于处理大量使用JS的网站或阻止普通HTTP抓取的页面。

## 获取API密钥

1. 创建一个Firecrawl帐户并生成一个API密钥。
2. 将其存储在配置中或在网关环境中设置 `FIRECRAWL_API_KEY`。

## 配置Firecrawl

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

- 当存在API密钥时，`firecrawl.enabled` 默认为 true。
- `maxAgeMs` 控制缓存结果可以有多旧（毫秒）。默认是2天。

## 隐身/绕过机器人检测

Firecrawl 提供了一个用于绕过机器人检测的 **代理模式** 参数 (`basic`, `stealth`, 或 `auto`)。
OpenClaw 对于所有 Firecrawl 请求总是使用 `proxy: "auto"` 加上 `storeInCache: true`。
如果省略了代理，Firecrawl 默认使用 `auto`。`auto` 如果基本尝试失败，则会使用隐身代理重试，这可能会比仅使用基本抓取消耗更多的积分。

## `web_fetch` 如何使用Firecrawl

`web_fetch` 提取顺序：

1. Readability（本地）
2. Firecrawl（如果已配置）
3. 基本HTML清理（最后的备选）

有关完整的网络工具设置，请参阅[Web tools](/tools/web)。