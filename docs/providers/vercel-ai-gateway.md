---
title: "Vercel AI Gateway"
summary: "Vercel AI Gateway setup (auth + model selection)"
read_when:
  - You want to use Vercel AI Gateway with OpenClaw
  - You need the API key env var or CLI auth choice
---
# Vercel AI Gateway

[Vercel AI Gateway](https://vercel.com/ai-gateway) 提供了一个统一的API，通过单个端点访问数百个模型。

- Provider: `vercel-ai-gateway`
- Auth: `AI_GATEWAY_API_KEY`
- API: Anthropic Messages 兼容

## 快速开始

1. 设置API密钥（推荐：将其存储在网关中）：

```bash
openclaw onboard --auth-choice ai-gateway-api-key
```

2. 设置默认模型：

```json5
{
  agents: {
    defaults: {
      model: { primary: "vercel-ai-gateway/anthropic/claude-opus-4.5" },
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

如果网关作为守护进程运行（launchd/systemd），请确保 `AI_GATEWAY_API_KEY`
对该进程可用（例如，在 `~/.openclaw/.env` 中或通过
`env.shellEnv`）。