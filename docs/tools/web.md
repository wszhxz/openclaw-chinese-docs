---
summary: "Web search + fetch tools (Brave Search API, Perplexity direct/OpenRouter)"
read_when:
  - You want to enable web_search or web_fetch
  - You need Brave Search API key setup
  - You want to use Perplexity Sonar for web search
title: "Web Tools"
---
# 网络工具

OpenClaw 提供两个轻量级的网络工具：

- `web_search` — 通过 Brave 搜索 API（默认）或 Perplexity Sonar（直接或通过 OpenRouter）搜索网络。
- `web_fetch` — HTTP 获取 + 可读内容提取（HTML → markdown/text）。

这些**不是**浏览器自动化工具。对于 JS 密集型网站或登录操作，请使用
[浏览器工具](/tools/browser)。

## 工作原理

- `web_search` 会调用您配置的提供者并返回结果。
  - **Brave**（默认）：返回结构化结果（标题、URL、摘要）。
  - **Perplexity**：返回 AI 合成答案并附带实时网络搜索的引用。
- 结果按查询缓存 15 分钟（可配置）。
- `web_fetch` 会执行普通的 HTTP GET 请求并提取可读内容
  （HTML → markdown/text）。它**不**执行 JavaScript。
- `web_fetch` 默认启用（除非明确禁用）。

## 选择搜索提供者

| 提供者         | 优点                                 | 缺点                                 | API 密钥                                      |
| -------------- | ------------------------------------ | ------------------------------------ | --------------------------------------------- |
| **Brave**（默认） | 快速、结构化结果、免费层级           | 传统搜索结果                         | `BRAVE_API_KEY`                              |
| **Perplexity**  | AI 合成答案、引用、实时搜索          | 需要 Perplexity 或 OpenRouter 访问权限 | `OPENROUTER_API_KEY` 或 `PERPLEXITY_API_KEY` |

查看 [Brave 搜索设置](/brave-search) 和 [Perplexity Sonar](/perplexity) 以获取提供者特定的详细信息。

在配置中设置提供者：

```json5
{
  tools: {
    web: {
      search: {
        provider: "brave", // 或 "perplexity"
      },
    },
  },
}
```

示例：切换到 Perplexity Sonar（直接 API）：

```json5
{
  tools: {
    web: {
      search: {
        provider: "perplexity",
        perplexity: {
          // API 密钥（如果设置了 OPENROUTER_API_KEY 或 PERPLEXITY_API_KEY 可选）
          apiKey: "pplx-...",
          // 基础 URL（如果省略则使用密钥感知的默认值）
          baseUrl: "https://api.perplexity.ai",
          // 模型（默认为 perplexity/sonar-pro）
          model: "perplexity/sonar-pro",
        },
      },
    },
  },
}
```

## 获取 Brave API 密钥

1. 在 https://brave.com/search/api/ 创建 Brave 搜索 API 账户。
2. 在仪表板中选择 **Data for Search** 计划（不是“Data for AI”），并生成 API 密钥。
3. 运行 `openclaw configure --section web` 将密钥存储在配置中（推荐），或在环境变量中设置 `BRAVE_API_KEY`。

Brave 提供免费层级和付费计划；请查看 Brave API 门户以获取
当前的限制和定价信息。

### 推荐设置密钥的位置

**推荐：** 运行 `openclaw configure --section web`。它会将密钥存储在
`~/.openclaw/openclaw.json` 下的 `tools.web.search.apiKey`。

**环境变量替代方案：** 在网关进程的环境变量中设置 `BRAVE_API_KEY`。对于网关安装，将其放在 `~/.openclaw/.env`（或您的服务环境）。查看 [Env vars](/help/faq#how-does-openclaw-load-environment-variables) 以了解 OpenClaw 如何加载环境变量。

## 使用 Perplexity（直接或通过 OpenRouter）

Perplexity Sonar 模型内置了网络搜索功能，返回 AI 合成答案并附带引用。您可以通过 OpenRouter 使用它们（无需信用卡 - 支持
加密货币/预付卡）。

### 获取 OpenRouter API 密钥

1. 在 https://openrouter.ai/ 创建账户。
2. 添加信用额度（支持加密货币、预付卡或信用卡）。
3. 在账户设置中生成 API 密钥。

### 设置 Perplexity 搜索

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        provider: "perplexity",
        perplexity: {
          // API 密钥（如果设置了 OPENROUTER_API_KEY 或 PERPLEXITY_API_KEY 可选）
          apiKey: "sk-or-v1-...",
          // 基础 URL（如果省略则使用密钥感知的默认值）
          baseUrl: "https://openrouter.ai/api/v1",
          // 模型（默认为 perplexity/sonar-pro）
          model: "perplexity/sonar-pro",
        },
      },
    },
  },
}
```

**环境变量替代方案：** 在网关环境变量中设置 `OPENROUTER_API_KEY` 或 `PERPLEXITY_API_KEY`。对于网关安装，将其放在 `~/.openclaw/.env`。

如果未设置基础 URL，OpenClaw 会根据 API 密钥来源选择默认值：

- `PERPLEXITY_API_KEY` 或 `pplx-...` → `https://api.perplexity.ai`
- `OPENROUTER_API_KEY` 或 `sk-or-v1-...` → `https://openrouter.ai/api/v1`

## Perplexity 模型

### Perplexity 模型

Perplexity 模型是基于大规模语言模型的 AI 模型，能够处理各种自然语言任务，包括文本生成、问答、翻译等。Perplexity 模型具有以下特点：

1. **强大的语言理解能力**：Perplexity 模型基于大量的文本数据进行训练，能够理解复杂的语言结构和语义，从而