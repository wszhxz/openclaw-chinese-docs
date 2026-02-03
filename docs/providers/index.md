---
summary: "Model providers (LLMs) supported by OpenClaw"
read_when:
  - You want to choose a model provider
  - You need a quick overview of supported LLM backends
title: "Model Providers"
---
# 模型提供商

OpenClaw 可以使用许多 LLM 提供商。选择一个提供商，进行身份验证，然后将默认模型设置为 `provider/model`。

寻找聊天渠道文档（WhatsApp/Telegram/Discord/Slack/Mattermost（插件）等）？请参阅 [Channels](/channels)。

## 精选：威尼斯（威尼斯 AI）

威尼斯是我们推荐的以隐私为先的推理设置，支持使用 Opus 处理复杂任务。

- 默认模型：`venice/llama-3.3-70b`
- 综合最佳模型：`venice/claude-opus-45`（Opus 仍是性能最强的模型）

请参阅 [威尼斯 AI](/providers/venice)。

## 快速入门

1. 通过提供商进行身份验证（通常使用 `openclaw onboard` 命令）。
2. 设置默认模型：

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-5" } } },
}
```

## 提供商文档

- [OpenAI（API + Codex）](/providers/openai)
- [Anthropic（API + Claude Code CLI）](/providers/anthropic)
- [Qwen（OAuth）](/providers/qwen)
- [OpenRouter](/providers/openrouter)
- [Vercel AI Gateway](/providers/vercel-ai-gateway)
- [Moonshot AI（Kimi + Kimi Coding）](/providers/moonshot)
- [OpenCode Zen](/providers/opencode)
- [Amazon Bedrock](/bedrock)
- [Z.AI](/providers/zai)
- [小米](/providers/xiaomi)
- [GLM 模型](/providers/glm)
- [MiniMax](/providers/minimax)
- [威尼斯（威尼斯 AI，隐私导向）](/providers/venice)
- [Ollama（本地模型）](/providers/ollama)

## 转录提供商

- [Deepgram（音频转录）](/providers/deepgram)

## 社区工具

- [Claude Max API 代理](/providers/claude-max-api-proxy) - 将 Claude Max/Pro 订阅用作 OpenAI 兼容的 API 端点

如需完整的提供商目录（xAI、Groq、Mistral 等）和高级配置，请参阅 [模型提供商](/concepts/model-providers)。