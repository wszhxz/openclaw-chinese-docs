---
summary: "Run OpenClaw with vLLM (OpenAI-compatible local server)"
read_when:
  - You want to run OpenClaw against a local vLLM server
  - You want OpenAI-compatible /v1 endpoints with your own models
title: "vLLM"
---
# vLLM

vLLM 可通过一个 **与 OpenAI 兼容** 的 HTTP API 提供开源（以及部分自定义）模型服务。OpenClaw 可使用 `openai-completions` API 连接到 vLLM。

当您启用 `VLLM_API_KEY`（若您的服务器未强制要求身份验证，则任意值均可）且**未显式定义** `models.providers.vllm` 条目时，OpenClaw 还可**自动发现** vLLM 中可用的模型。

## 快速开始

1. 启动一个支持 OpenAI 兼容协议的 vLLM 服务。

您的基础 URL 应暴露 `/v1` 接口（例如 `/v1/models`、`/v1/chat/completions`）。vLLM 通常运行于以下地址：

- `http://127.0.0.1:8000/v1`

2. 启用自动发现功能（若未配置身份验证，则任意值均可）：

```bash
export VLLM_API_KEY="vllm-local"
```

3. 选择一个模型（请将其替换为您 vLLM 实例中的某个模型 ID）：

```json5
{
  agents: {
    defaults: {
      model: { primary: "vllm/your-model-id" },
    },
  },
}
```

## 模型发现（隐式提供者）

当设置了 `VLLM_API_KEY`（或存在身份验证配置文件），且您**未定义** `models.providers.vllm` 时，OpenClaw 将查询：

- `GET http://127.0.0.1:8000/v1/models`

……并将返回的模型 ID 转换为模型条目。

若您显式设置了 `models.providers.vllm`，则跳过自动发现机制，您必须手动定义模型。

## 显式配置（手动指定模型）

在以下情况下，请使用显式配置：

- vLLM 运行在不同的主机或端口上。
- 您希望固定 `contextWindow`/`maxTokens` 的值。
- 您的服务器需要真实的 API 密钥（或您希望控制请求头）。

```json5
{
  models: {
    providers: {
      vllm: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "${VLLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "Local vLLM Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## 故障排查

- 检查服务器是否可达：

```bash
curl http://127.0.0.1:8000/v1/models
```

- 若请求因身份验证错误而失败，请设置一个与服务器配置匹配的真实 `VLLM_API_KEY`，或在 `models.providers.vllm` 下显式配置提供者。