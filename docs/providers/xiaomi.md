---
summary: "Use Xiaomi MiMo (mimo-v2-flash) with OpenClaw"
read_when:
  - You want Xiaomi MiMo models in OpenClaw
  - You need XIAOMI_API_KEY setup
title: "Xiaomi MiMo"
---
# 小米 MiMo

小米 MiMo 是专为 **MiMo** 模型设计的 API 平台。它提供兼容 OpenAI 和 Anthropic 格式的 REST API，并使用 API 密钥进行身份验证。在 [小米 MiMo 控制台](https://platform.xiaomimimo.com/#/console/api-keys) 创建您的 API 密钥。OpenClaw 使用 `xiaomi` 提供商并配合 Xiaomi MiMo API 密钥。

## 模型概览

- **mimo-v2-flash**：262144 令牌上下文窗口，兼容 Anthropic Messages API。
- 基础 URL：`https://api.xiaomimimo.com/anthropic`
- 授权：`Bearer $XIAOMI_API_KEY`

## CLI 配置

```bash
openclaw onboard --auth-choice xiaomi-api-key
# 或非交互式
openclaw onboard --auth-choice xiaomi-api-key --xiaomi-api-key "$XIAOMI_API_KEY"
```

## 配置片段

```json5
{
  env: { XIAOMI_API_KEY: "your-key" },
  agents: { defaults: { model: { primary: "xiaomi/mimo-v2-flash" } } },
  models: {
    mode: "merge",
    providers: {
      xiaomi: {
        baseUrl: "https://api.xiaomimimo.com/anthropic",
        api: "anthropic-messages",
        apiKey: "XIAOMI_API_KEY",
        models: [
          {
            id: "mimo-v2-flash",
            name: "小米 MiMo V2 Flash",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## 注意事项

- 模型引用：`xiaomi/mimo-v2-flash`。
- 当设置 `XIAOMI_API_KEY`（或存在认证配置文件）时，提供商会自动注入。
- 有关提供商规则，请参阅 [/concepts/model-providers](/concepts/model-providers)。