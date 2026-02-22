---
summary: "Model providers (LLMs) supported by OpenClaw"
read_when:
  - You want to choose a model provider
  - You need a quick overview of supported LLM backends
title: "Model Providers"
---
# 模型提供商

OpenClaw 可以使用许多 LLM 提供商。选择一个提供商，进行身份验证，然后设置默认模型为 `provider/model`。

寻找聊天渠道文档（WhatsApp/Telegram/Discord/Slack/Mattermost (插件)/等）？请参阅 [Channels](/channels)。

## 精彩推荐：Venice (Venice AI)

Venice 是我们推荐的 Venice AI 设置，注重隐私保护，并且可以选择使用 Opus 来处理复杂任务。

- 默认: `venice/llama-3.3-70b`
- 最佳整体: `venice/claude-opus-45` (Opus 仍然是最强的)

请参阅 [Venice AI](/providers/venice)。

## 快速开始

1. 使用提供商进行身份验证（通常通过 `openclaw onboard`）。
2. 设置默认模型：

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## 提供商文档

- [OpenAI (API + Codex)](/providers/openai)
- [Anthropic (API + Claude Code CLI)](/providers/anthropic)
- [Qwen (OAuth)](/providers/qwen)
- [OpenRouter](/providers/openrouter)
- [LiteLLM (统一网关)](/providers/litellm)
- [Vercel AI Gateway](/providers/vercel-ai-gateway)
- [Together AI](/providers/together)
- [Cloudflare AI Gateway](/providers/cloudflare-ai-gateway)
- [Moonshot AI (Kimi + Kimi Coding)](/providers/moonshot)
- [OpenCode Zen](/providers/opencode)
- [Amazon Bedrock](/providers/bedrock)
- [Z.AI](/providers/zai)
- [Xiaomi](/providers/xiaomi)
- [GLM models](/providers/glm)
- [MiniMax](/providers/minimax)
- [Venice (Venice AI, 隐私优先)](/providers/venice)
- [Hugging Face (推理)](/providers/huggingface)
- [Ollama (本地模型)](/providers/ollama)
- [vLLM (本地模型)](/providers/vllm)
- [Qianfan](/providers/qianfan)
- [NVIDIA](/providers/nvidia)

## 转录提供商

- [Deepgram (音频转录)](/providers/deepgram)

## 社区工具

- [Claude Max API Proxy](/providers/claude-max-api-proxy) - 使用 Claude Max/Pro 订阅作为与 OpenAI 兼容的 API 端点

有关完整的提供商目录（xAI, Groq, Mistral 等）和高级配置，请参阅 [Model providers](/concepts/model-providers)。