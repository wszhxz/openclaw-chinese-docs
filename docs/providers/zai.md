---
summary: "Use Z.AI (GLM models) with OpenClaw"
read_when:
  - You want Z.AI / GLM models in OpenClaw
  - You need a simple ZAI_API_KEY setup
title: "Z.AI"
---
# Z.AI

Z.AI 是 **GLM** 模型的API平台。它为GLM提供REST API，并使用API密钥进行身份验证。您可以在Z.AI控制台中创建API密钥。OpenClaw使用 `zai` 提供商并结合Z.AI API密钥。

## CLI 设置

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

- GLM模型以 `zai/<model>` 的形式提供（示例：`zai/glm-5`）。
- 默认情况下，Z.AI工具调用流式传输已启用 `tool_stream`。将 `agents.defaults.models["zai/<model>"].params.tool_stream` 设置为 `false` 以禁用它。
- 有关模型系列概述，请参阅[/providers/glm](/providers/glm)。
- Z.AI 使用带有您的API密钥的Bearer认证。