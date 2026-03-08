---
summary: "Run OpenClaw on local LLMs (LM Studio, vLLM, LiteLLM, custom OpenAI endpoints)"
read_when:
  - You want to serve models from your own GPU box
  - You are wiring LM Studio or an OpenAI-compatible proxy
  - You need the safest local model guidance
title: "Local Models"
---
# 本地模型

本地部署是可行的，但 OpenClaw 需要大上下文 + 针对提示词注入的强防御。小显存卡会截断上下文并泄露安全性。目标要高：**≥2 台顶配 Mac Studio 或等效 GPU 设备（~3 万美元以上）**。单张 **24 GB** 显卡仅适用于负载较轻的提示词，且延迟较高。使用你能运行的**最大/全尺寸模型变体**；过度量化或“小”检查点会增加提示词注入风险（参见 [安全性](/gateway/security)）。

## 推荐：LM Studio + MiniMax M2.5（Responses API，全尺寸）

当前最佳的本地栈。在 LM Studio 中加载 MiniMax M2.5，启用本地服务器（默认 `http://127.0.0.1:1234`），并使用 Responses API 将推理与最终文本分开。

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/minimax-m2.5-gs32" },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "lmstudio/minimax-m2.5-gs32": { alias: "Minimax" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "minimax-m2.5-gs32",
            name: "MiniMax M2.5 GS32",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**设置清单**

- 安装 LM Studio：[https://lmstudio.ai](https://lmstudio.ai)
- 在 LM Studio 中，下载**可用的最大 MiniMax M2.5 构建版本**（避免“小”/重度量化变体），启动服务器，确认 `http://127.0.0.1:1234/v1/models` 列出了它。
- 保持模型加载状态；冷启动会增加启动延迟。
- 如果你的 LM Studio 构建版本不同，请调整 `contextWindow`/`maxTokens`。
- 对于 WhatsApp，坚持使用 Responses API，以便仅发送最终文本。

即使在运行本地模型时也要保持托管模型配置；使用 `models.mode: "merge"` 以便备用方案保持可用。

### 混合配置：托管为主，本地备用

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-5",
        fallbacks: ["lmstudio/minimax-m2.5-gs32", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-5": { alias: "Sonnet" },
        "lmstudio/minimax-m2.5-gs32": { alias: "MiniMax Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "minimax-m2.5-gs32",
            name: "MiniMax M2.5 GS32",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### 本地优先，带有托管安全网

交换主用和备用顺序；保持相同的 providers 块和 `models.mode: "merge"`，以便当本地机器宕机时可以回退到 Sonnet 或 Opus。

### 区域托管/数据路由

- 托管的 MiniMax/Kimi/GLM 变体也存在于 OpenRouter 上，带有区域固定端点（例如，美国托管）。在那里选择区域变体，以保持流量在你选择的司法管辖区内，同时仍使用 `models.mode: "merge"` 作为 Anthropic/OpenAI 备用。
- 仅本地仍然是最强的隐私路径；当你需要提供商功能但希望控制数据流时，托管区域路由是中间方案。

## 其他兼容 OpenAI 的本地代理

如果 vLLM、LiteLLM、OAI-proxy 或自定义网关暴露了 OpenAI 风格的 `/v1` 端点，它们都可以工作。将上面的 provider 块替换为你的端点和模型 ID：

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

保留 `models.mode: "merge"`，以便托管模型作为备用保持可用。

## 故障排除

- 网关可以到达代理吗？`curl http://127.0.0.1:1234/v1/models`。
- LM Studio 模型未加载？重新加载；冷启动是常见的“挂起”原因。
- 上下文错误？降低 `contextWindow` 或提高你的服务器限制。
- 安全性：本地模型跳过提供商侧过滤器；保持代理范围狭窄并开启压缩，以限制提示词注入的爆炸半径。