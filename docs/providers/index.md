---
summary: "Model providers (LLMs) supported by OpenClaw"
read_when:
  - You want to choose a model provider
  - You need a quick overview of supported LLM backends
title: "Model Providers"
---
# 模型提供商

OpenClaw 可以使用多种大语言模型（LLM）提供商。请选择一个提供商，完成身份验证，然后将默认模型设置为 `provider/model`。

需要聊天渠道文档（WhatsApp / Telegram / Discord / Slack / Mattermost（插件）等）？请参阅 [Channels（渠道）](/channels)。

## 快速开始

1. 使用提供商进行身份验证（通常通过 `openclaw onboard`）。
2. 设置默认模型：

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## 提供商文档

- [Amazon Bedrock](/providers/bedrock)
- [Anthropic（API + Claude Code CLI）](/providers/anthropic)
- [Cloudflare AI Gateway](/providers/cloudflare-ai-gateway)
- [GLM models](/providers/glm)
- [Hugging Face（Inference）](/providers/huggingface)
- [Kilocode](/providers/kilocode)
- [LiteLLM（统一网关）](/providers/litellm)
- [MiniMax](/providers/minimax)
- [Mistral](/providers/mistral)
- [Moonshot AI（Kimi + Kimi Coding）](/providers/moonshot)
- [NVIDIA](/providers/nvidia)
- [Ollama（本地模型）](/providers/ollama)
- [OpenAI（API + Codex）](/providers/openai)
- [OpenCode Zen](/providers/opencode)
- [OpenRouter](/providers/openrouter)
- [Qianfan](/providers/qianfan)
- [Qwen（OAuth）](/providers/qwen)
- [Together AI](/providers/together)
- [Vercel AI Gateway](/providers/vercel-ai-gateway)
- [Venice（Venice AI，注重隐私）](/providers/venice)
- [vLLM（本地模型）](/providers/vllm)
- [Xiaomi](/providers/xiaomi)
- [Z.AI](/providers/zai)

## 语音转文字提供商

- [Deepgram（音频转录）](/providers/deepgram)

## 社区工具

- [Claude Max API Proxy](/providers/claude-max-api-proxy) —— 面向 Claude 订阅凭证的社区代理（使用前请务必查阅 Anthropic 的政策与条款）

如需完整提供商目录（xAI、Groq、Mistral 等）及高级配置，请参阅 [Model providers（模型提供商）](/concepts/model-providers)。