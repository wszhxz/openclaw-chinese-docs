---
summary: "Use OpenRouter's unified API to access many models in OpenClaw"
read_when:
  - You want a single API key for many LLMs
  - You want to run models via OpenRouter in OpenClaw
title: "OpenRouter"
---
# OpenRouter

OpenRouter 提供一个 **统一的 API**，通过单一端点和 API 密钥将请求路由到多个模型。它与 OpenAI 兼容，因此大多数 OpenAI SDK 通过更改基础 URL 即可使用。

## CLI 配置

```bash
openclaw onboard --auth-choice apiKey --token-provider openrouter --token "$OPENROUTER_API_KEY"
```

## 配置片段

```json5
{
  env: { OPENROUTER_API_KEY: "sk-or-..." },
  agents: {
    defaults: {
      model: { primary: "openrouter/anthropic/claude-sonnet-4-5" },
    },
  },
}
```

## 注意事项

- 模型引用格式为 `openrouter/<provider>/<model>`。
- 如需更多模型/提供者选项，请参见 [/concepts/model-providers](/concepts/model-providers)。
- OpenRouter 在内部使用您的 API 密钥作为 Bearer 令牌。