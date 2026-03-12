---
summary: "Together AI setup (auth + model selection)"
read_when:
  - You want to use Together AI with OpenClaw
  - You need the API key env var or CLI auth choice
---
# Together AI

[Together AI](https://together.ai) 通过统一的 API 提供对领先开源模型（包括 Llama、DeepSeek、Kimi 等）的访问。

- 提供商：`together`
- 认证方式：`TOGETHER_API_KEY`
- API：兼容 OpenAI

## 快速开始

1. 设置 API 密钥（推荐：为网关保存该密钥）：

```bash
openclaw onboard --auth-choice together-api-key
```

2. 设置默认模型：

```json5
{
  agents: {
    defaults: {
      model: { primary: "together/moonshotai/Kimi-K2.5" },
    },
  },
}
```

## 非交互式示例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

这将把 `together/moonshotai/Kimi-K2.5` 设为默认模型。

## 环境说明

如果网关以守护进程方式运行（launchd/systemd），请确保 `TOGETHER_API_KEY`  
对该进程可用（例如，置于 `~/.openclaw/.env` 中，或通过 `env.shellEnv` 提供）。

## 可用模型

Together AI 提供对多种热门开源模型的访问：

- **GLM 4.7 Fp8** — 默认模型，上下文窗口达 200K
- **Llama 3.3 70B Instruct Turbo** — 快速、高效的指令遵循能力
- **Llama 4 Scout** — 具备图像理解能力的视觉模型
- **Llama 4 Maverick** — 先进的视觉与推理能力
- **DeepSeek V3.1** — 强大的编程与推理模型
- **DeepSeek R1** — 高级推理模型
- **Kimi K2 Instruct** — 高性能模型，上下文窗口达 262K

所有模型均支持标准聊天补全功能，并兼容 OpenAI API。