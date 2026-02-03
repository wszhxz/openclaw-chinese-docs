---
summary: "Use Z.AI (GLM models) with OpenClaw"
read_when:
  - You want Z.AI / GLM models in OpenClaw
  - You need a simple ZAI_API_KEY setup
title: "Z.AI"
---
# Z.AI

Z.AI 是 **GLM** 模型的 API 平台。它为 GLM 提供 REST API 接口，并使用 API 密钥进行身份验证。在 Z.AI 控制台创建您的 API 密钥。OpenClaw 使用 `zai` 提供者并配合 Z.AI API 密钥。

## CLI 设置

```bash
openclaw onboard --auth-choice zai-api-key
# 或非交互式
openclaw onboard --zai-api-key "$ZAI_API_KEY"
```

## 配置片段

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-4.7" } } },
}
```

## 注意事项

- GLM 模型以 `zai/<model>` 格式提供（示例：`zai/glm-4.7`）。
- 查看 [/providers/glm](/providers/glm) 了解模型家族概览。
- Z.AI 使用 API 密钥进行 Bearer 认证。