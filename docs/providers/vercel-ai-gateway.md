---
title: "Vercel AI Gateway"
summary: "Vercel AI Gateway setup (auth + model selection)"
read_when:
  - You want to use Vercel AI Gateway with OpenClaw
  - You need the API key env var or CLI auth choice
---
# Vercel AI网关

[Vercel AI网关](https://vercel.com/ai-gateway) 通过单一端点提供统一的API，以访问数百个模型。

- 提供商：`vercel-ai-gateway`
- 认证：`AI_GATEWAY_API_KEY`
- API：兼容Anthropic Messages

## 快速入门

1. 设置API密钥（推荐：为网关存储）：

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

如果网关作为守护进程（launchd/systemd）运行，请确保 `AI_GATEWAY_API_KEY` 可用于此进程（例如，在 `~/.openclaw/.env` 或通过 `env.shellEnv`）。