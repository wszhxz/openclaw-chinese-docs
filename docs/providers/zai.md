---
summary: "Use Z.AI (GLM models) with OpenClaw"
read_when:
  - You want Z.AI / GLM models in OpenClaw
  - You need a simple ZAI_API_KEY setup
title: "Z.AI"
---
# Z.AI

Z.AI 是 **GLM** 模型的 API 平台。它为 GLM 提供 REST API，并使用 API 密钥进行身份验证。请在 Z.AI 控制台中创建您的 API 密钥。OpenClaw 使用带有 Z.AI API 密钥的 `zai` 提供程序。

## CLI 配置

```bash
openclaw onboard --auth-choice zai-api-key
# or non-interactive
openclaw onboard --zai-api-key "$ZAI_API_KEY"
```

## 配置片段

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5" } } },
}
```

## 注意事项

- GLM 模型以 `zai/<model>` 形式提供（例如：`zai/glm-5`）。
- Z.AI 工具调用流式传输默认启用 `tool_stream`。将 `agents.defaults.models["zai/<model>"].params.tool_stream` 设置为 `false` 可禁用该功能。
- 有关模型系列概览，请参阅 [/providers/glm](/providers/glm)。
- Z.AI 使用您的 API 密钥进行 Bearer 认证。