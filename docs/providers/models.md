---
summary: "Model providers (LLMs) supported by OpenClaw"
read_when:
  - You want to choose a model provider
  - You want quick setup examples for LLM auth + model selection
title: "Model Provider Quickstart"
---
# 模型提供商

OpenClaw 可以使用许多大型语言模型（LLM）提供商。选择一个，进行身份验证，然后将默认模型设置为 `provider/model`。

## 亮点：威尼斯（威尼斯 AI）

威尼斯是我们推荐的隐私优先推理设置，可选使用 Opus 处理最困难的任务。

- 默认模型：`venice/llama-3.3-70b`
- 综合最佳模型：`venice/claude-opus-45`（Opus 仍然是最强的）

详见 [威尼斯 AI](/providers/venice)。

## 快速入门（两步）

1. 使用提供商进行身份验证（通常通过 `openclaw onboard`）。
2. 设置默认模型：

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-5" } } },
}
```

## 支持的提供商（入门集）

- [OpenAI（API + Codex）](/providers/openai)
- [Anthropic（API + Claude Code CLI）](/providers/anthropic)
- [OpenRouter](/providers/openrouter)
- [Vercel AI Gateway](/providers/vercel-ai-gateway)
- [Moonshot AI（Kimi + Kimi Coding）](/providers/moonshot)
- [Synthetic](/providers/synthetic)
- [OpenCode Zen](/providers/opencode)
- [Z.AI](/providers/zai)
- [GLM 模型](/providers/glm)
- [MiniMax](/providers/minimax)
- [威尼斯（威尼斯 AI）](/providers/venice)
- [Amazon Bedrock](/bedrock)

完整的提供商目录（xAI、Groq、Mistral 等）和高级配置，请参见 [模型提供商](/concepts/model-providers)。