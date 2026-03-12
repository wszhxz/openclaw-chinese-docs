---
summary: "GLM model family overview + how to use it in OpenClaw"
read_when:
  - You want GLM models in OpenClaw
  - You need the model naming convention and setup
title: "GLM Models"
---
# GLM 模型

GLM 是一个可通过 Z.AI 平台使用的**模型系列**（而非一家公司）。在 OpenClaw 中，GLM 模型通过 `zai` 提供商及类似 `zai/glm-5` 的模型 ID 进行访问。

## CLI 配置

```bash
openclaw onboard --auth-choice zai-api-key
```

## 配置片段

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5" } } },
}
```

## 注意事项

- GLM 的版本和可用性可能发生变化；请查阅 Z.AI 官方文档以获取最新信息。
- 示例模型 ID 包括 `glm-5`、`glm-4.7` 和 `glm-4.6`。
- 有关提供商的详细信息，请参阅 [/providers/zai](/providers/zai)。