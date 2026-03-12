---
summary: "Use Kilo Gateway's unified API to access many models in OpenClaw"
read_when:
  - You want a single API key for many LLMs
  - You want to run models via Kilo Gateway in OpenClaw
---
# Kilo 网关

Kilo 网关提供一个**统一的 API**，通过单个端点和 API 密钥将请求路由至后端的多个模型。它与 OpenAI 兼容，因此只需切换基础 URL，大多数 OpenAI SDK 即可正常工作。

## 获取 API 密钥

1. 访问 [app.kilo.ai](https://app.kilo.ai)  
2. 登录或创建账户  
3. 进入“API 密钥”页面并生成一个新的密钥  

## CLI 配置

```bash
openclaw onboard --kilocode-api-key <key>
```

或者设置环境变量：

```bash
export KILOCODE_API_KEY="<your-kilocode-api-key>" # pragma: allowlist secret
```

## 配置片段

```json5
{
  env: { KILOCODE_API_KEY: "<your-kilocode-api-key>" }, // pragma: allowlist secret
  agents: {
    defaults: {
      model: { primary: "kilocode/kilo/auto" },
    },
  },
}
```

## 默认模型

默认模型为 `kilocode/kilo/auto`，这是一个智能路由模型，可根据任务类型自动选择最优的底层模型：

- 规划、调试和编排类任务将路由至 Claude Opus  
- 编码编写与探索类任务将路由至 Claude Sonnet  

## 可用模型

OpenClaw 在启动时会动态从 Kilo 网关发现可用模型。使用  
`/models kilocode`  
可查看您账户下所有可用模型的完整列表。

网关上任意可用模型均可通过添加 `kilocode/` 前缀来调用：

```
kilocode/kilo/auto              (default - smart routing)
kilocode/anthropic/claude-sonnet-4
kilocode/openai/gpt-5.2
kilocode/google/gemini-3-pro-preview
...and many more
```

## 注意事项

- 模型引用格式为 `kilocode/<model-id>`（例如：`kilocode/anthropic/claude-sonnet-4`）。  
- 默认模型：`kilocode/kilo/auto`  
- 基础 URL：`https://api.kilo.ai/api/gateway/`  
- 更多模型/提供商选项，请参阅 [/concepts/model-providers](/concepts/model-providers)。  
- Kilo 网关在底层使用您的 API 密钥作为 Bearer Token。