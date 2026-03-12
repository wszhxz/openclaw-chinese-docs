---
title: "Vercel AI Gateway"
summary: "Vercel AI Gateway setup (auth + model selection)"
read_when:
  - You want to use Vercel AI Gateway with OpenClaw
  - You need the API key env var or CLI auth choice
---
# Vercel AI 网关

[Vercel AI 网关](https://vercel.com/ai-gateway) 提供统一的 API，可通过单个端点访问数百种模型。

- 提供商：`vercel-ai-gateway`
- 认证方式：`AI_GATEWAY_API_KEY`
- API：兼容 Anthropic Messages

## 快速开始

1. 设置 API 密钥（建议为网关存储该密钥）：

```bash
openclaw onboard --auth-choice ai-gateway-api-key
```

2. 设置默认模型：

```json5
{
  agents: {
    defaults: {
      model: { primary: "vercel-ai-gateway/anthropic/claude-opus-4.6" },
    },
  },
}
```

## 非交互式示例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice ai-gateway-api-key \
  --ai-gateway-api-key "$AI_GATEWAY_API_KEY"
```

## 环境说明

如果网关以守护进程方式运行（如 launchd 或 systemd），请确保 `AI_GATEWAY_API_KEY`  
对该进程可用（例如，置于 `~/.openclaw/.env` 中，或通过 `env.shellEnv` 提供）。

## 模型 ID 简写

OpenClaw 支持 Vercel Claude 的模型简写引用，并在运行时将其规范化为标准形式：

- `vercel-ai-gateway/claude-opus-4.6` → `vercel-ai-gateway/anthropic/claude-opus-4.6`
- `vercel-ai-gateway/opus-4.6` → `vercel-ai-gateway/anthropic/claude-opus-4-6`