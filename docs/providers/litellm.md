---
summary: "Run OpenClaw through LiteLLM Proxy for unified model access and cost tracking"
read_when:
  - You want to route OpenClaw through a LiteLLM proxy
  - You need cost tracking, logging, or model routing through LiteLLM
---
# LiteLLM

[LiteLLM](https://litellm.ai) 是一个开源的LLM网关，提供统一的API访问100多个模型提供商。通过LiteLLM路由OpenClaw以实现集中化的成本跟踪、日志记录，并且无需更改OpenClaw配置即可灵活切换后端。

## 为什么在OpenClaw中使用LiteLLM？

- **成本跟踪** — 精确查看OpenClaw在所有模型上的花费
- **模型路由** — 在不更改配置的情况下在Claude、GPT-4、Gemini、Bedrock之间切换
- **虚拟密钥** — 为OpenClaw创建具有支出限制的密钥
- **日志记录** — 完整的请求/响应日志用于调试
- **故障转移** — 如果主提供商宕机，则自动故障转移

## 快速开始

### 通过引导设置

```bash
openclaw onboard --auth-choice litellm-api-key
```

### 手动设置

1. 启动LiteLLM代理：

```bash
pip install 'litellm[proxy]'
litellm --model claude-opus-4-6
```

2. 将OpenClaw指向LiteLLM：

```bash
export LITELLM_API_KEY="your-litellm-key"

openclaw
```

这样就完成了。OpenClaw现在通过LiteLLM进行路由。

## 配置

### 环境变量

```bash
export LITELLM_API_KEY="sk-litellm-key"
```

### 配置文件

```json5
{
  models: {
    providers: {
      litellm: {
        baseUrl: "http://localhost:4000",
        apiKey: "${LITELLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "claude-opus-4-6",
            name: "Claude Opus 4.6",
            reasoning: true,
            input: ["text", "image"],
            contextWindow: 200000,
            maxTokens: 64000,
          },
          {
            id: "gpt-4o",
            name: "GPT-4o",
            reasoning: false,
            input: ["text", "image"],
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "litellm/claude-opus-4-6" },
    },
  },
}
```

## 虚拟密钥

为OpenClaw创建一个专用密钥并设置支出限制：

```bash
curl -X POST "http://localhost:4000/key/generate" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "key_alias": "openclaw",
    "max_budget": 50.00,
    "budget_duration": "monthly"
  }'
```

使用生成的密钥作为 `LITELLM_API_KEY`。

## 模型路由

LiteLLM可以将模型请求路由到不同的后端。在您的LiteLLM `config.yaml` 中进行配置：

```yaml
model_list:
  - model_name: claude-opus-4-6
    litellm_params:
      model: claude-opus-4-6
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: gpt-4o
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY
```

OpenClaw继续请求 `claude-opus-4-6` — LiteLLM处理路由。

## 查看使用情况

检查LiteLLM的仪表板或API：

```bash
# Key info
curl "http://localhost:4000/key/info" \
  -H "Authorization: Bearer sk-litellm-key"

# Spend logs
curl "http://localhost:4000/spend/logs" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

## 注意事项

- LiteLLM默认运行在 `http://localhost:4000`
- OpenClaw通过与OpenAI兼容的 `/v1/chat/completions` 端点连接
- 所有OpenClaw功能都通过LiteLLM工作 — 无限制

## 参见

- [LiteLLM 文档](https://docs.litellm.ai)
- [模型提供商](/concepts/model-providers)