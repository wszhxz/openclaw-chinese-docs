---
summary: "Use Mistral models and Voxtral transcription with OpenClaw"
read_when:
  - You want to use Mistral models in OpenClaw
  - You need Mistral API key onboarding and model refs
title: "Mistral"
---
# Mistral

OpenClaw 支持 Mistral，用于文本/图像模型路由（`mistral/...`）以及通过 Voxtral 进行音视频转录（media understanding）。  
Mistral 还可用于记忆嵌入（`memorySearch.provider = "mistral"`）。

## CLI 配置

```bash
openclaw onboard --auth-choice mistral-api-key
# or non-interactive
openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
```

## 配置片段（大语言模型提供商）

```json5
{
  env: { MISTRAL_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
}
```

## 配置片段（使用 Voxtral 进行音频转录）

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

## 注意事项

- Mistral 认证使用 `MISTRAL_API_KEY`。  
- 提供商基础 URL 默认为 `https://api.mistral.ai/v1`。  
- 入门默认模型为 `mistral/mistral-large-latest`。  
- Mistral 在媒体理解中的默认音频模型为 `voxtral-mini-latest`。  
- 媒体转录路径使用 `/v1/audio/transcriptions`。  
- 记忆嵌入路径使用 `/v1/embeddings`（默认模型：`mistral-embed`）。