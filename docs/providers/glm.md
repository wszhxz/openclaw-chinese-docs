---
summary: "GLM model family overview + how to use it in OpenClaw"
read_when:
  - You want GLM models in OpenClaw
  - You need the model naming convention and setup
title: "GLM Models"
---
# GLM模型

GLM是一个**模型家族**（而非公司），可通过Z.AI平台访问。在OpenClaw中，GLM模型通过`zai`服务提供商和模型ID（如`zai/glm-4.7`）进行访问。

## CLI配置

```bash
openclaw onboard --auth-choice zai-api-key
```

## 配置片段

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-4.7" } } },
}
```

## 注意事项

- GLM版本和可用性可能发生变化；请查看Z.AI的文档以获取最新信息。
- 示例模型ID包括`glm-4.7`和`glm-4.6`。
- 有关服务提供商的详细信息，请参见[/providers/zai](/providers/zai)。