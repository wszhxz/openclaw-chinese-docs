---
summary: "GLM model family overview + how to use it in OpenClaw"
read_when:
  - You want GLM models in OpenClaw
  - You need the model naming convention and setup
title: "GLM Models"
---
# GLM models

GLM 是一个 **模型系列**（不是公司），通过 Z.AI 平台提供。在 OpenClaw 中，GLM 模型是通过 `zai` 提供商和模型 ID 如 `zai/glm-5` 访问的。

## CLI setup

```bash
openclaw onboard --auth-choice zai-api-key
```

## Config snippet

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5" } } },
}
```

## Notes

- GLM 版本和可用性可能会发生变化；请查阅 Z.AI 的文档以获取最新信息。
- 示例模型 ID 包括 `glm-5`、`glm-4.7` 和 `glm-4.6`。
- 有关提供商的详细信息，请参阅 [/providers/zai](/providers/zai)。