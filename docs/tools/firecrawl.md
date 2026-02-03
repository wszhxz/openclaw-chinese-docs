---
summary: "Firecrawl fallback for web_fetch (anti-bot + cached extraction)"
read_when:
  - You want Firecrawl-backed web extraction
  - You need a Firecrawl API key
  - You want anti-bot extraction for web_fetch
title: "Firecrawl"
---
# Firecrawl

OpenClaw 可以将 **Firecrawl** 作为 `web_fetch` 的备用提取器。它是一个托管的内容提取服务，支持机器人规避和缓存，有助于处理 JS 密集型网站或阻止普通 HTTP 提取的页面。

## 获取 API 密钥

1. 创建 Firecrawl 账户并生成 API 密钥。
2. 将其存储在配置中或在网关环境变量中设置 `FIRECRAWL_API_KEY`。

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

说明：

- 当存在 API 密钥时，`firecrawl.enabled` 默认为 true。
- `maxAgeMs` 控制缓存结果的最大年龄（毫秒）。默认为 2 天。

## 机器人规避 / 代理模式

Firecrawl 提供了一个 **代理模式** 参数用于机器人规避（`basic`、`stealth` 或 `auto`）。
OpenClaw 对 Firecrawl 请求始终使用 `proxy: "auto"` 加上 `storeInCache: true`。
如果未指定代理模式，Firecrawl 默认为 `auto`。`auto` 会在基本代理尝试失败时自动切换为隐身代理，这可能比仅使用基本代理消耗更多积分。

## `web_fetch` 如何使用 Firecrawl

`web_fetch` 提取顺序：

1. Readability（本地）
2. Firecrawl（如已配置）
3. 基础 HTML 清理（最后的备用方案）

完整网络工具设置请参见 [Web 工具](/tools/web)。