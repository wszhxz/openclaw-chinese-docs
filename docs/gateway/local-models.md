---
summary: "Run OpenClaw on local LLMs (LM Studio, vLLM, LiteLLM, custom OpenAI endpoints)"
read_when:
  - You want to serve models from your own GPU box
  - You are wiring LM Studio or an OpenAI-compatible proxy
  - You need the safest local model guidance
title: "Local Models"
---
# 本地模型

本地部署是可行的，但 OpenClaw 需要大上下文 + 强提示注入防御。小显卡会截断上下文并导致安全漏洞。目标要高：**≥2 个满载的 Mac Studio 或等效 GPU 配置（约 $30,000+）**。单个 **24 GB** GPU 仅适用于轻量提示且延迟较高。使用你能运行的 **最大/完整尺寸模型变体**；高度量化或“小”检查点会增加提示注入风险（参见 [安全](/gateway/security)）。

## 推荐配置：LM Studio + MiniMax M2.1（响应 API，完整尺寸）

当前最佳本地堆栈。在 LM Studio 中加载 MiniMax M2.1，启用本地服务器（默认 `http://127.0.0.1:1234`），并通过响应 API 分离推理过程与最终文本。

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/minimax-m2.1-gs32" },
      models: {
        "anthropic/claude-opus-4-5": { alias: "Opus" },
        "lmstudio/minimax-m2.1-gs32": { alias: "MiniMax" },
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
            id: "minimax-m2.1-gs32",
            name: "MiniMax M2.1 GS32",
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

**设置检查清单**

- 安装 LM Studio: https://lmstudio.ai
- 在 LM Studio 中下载 **可用的最新 MiniMax M2.1 构建版本**（避免“小”/高度量化的变体），启动服务器，确认 `http://127.0.0.1:1234/v1/models` 列出该模型。
- 保持模型加载；冷启动会增加启动延迟。
- 如果你的 LM Studio 构建版本不同，请调整 `contextWindow`/`maxTokens`。
- 对于 WhatsApp，使用响应 API 以确保仅发送最终文本。

即使在本地运行时，也应保持托管模型的配置；使用 `models.mode: "merge"` 以确保回退选项始终可用。

### 混合配置：托管主模型，本地回退

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-5",
        fallbacks: ["lmstudio/minimax-m2.1-gs32", "anthropic/claude-opus-4-5"],
      },
      models: {
        "anthropic/claude-sonnet-4-5": { alias: "Sonnet" },
        "lmstudio/minimax-m2.1-gs32": { alias: "MiniMax Local" },
        "anthropic/claude-opus-4-5": { alias: "Opus" },
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
            id: "minimax-m2.1-gs32",
            name: "MiniMax M2.1 GS32",
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

### 本地优先 + 托管安全网

交换主模型和回退模型的顺序；保持相同的提供者块和 `models.mode: "merge"`，以便本地设备宕机时可回退到 Sonnet 或 Opus。

### 区域托管 / 数据路由

- OpenRouter 上也存在托管的 MiniMax/Kimi/GLM 变体，且支持区域绑定端点（例如，美国托管）。在该平台选择区域变体，以在使用 `models.mode: "merge"` 进行 Anthropic/OpenAI 回退时保持流量在你选择的司法管辖区。
- 仅本地部署仍是最强的隐私路径；当需要提供方功能但希望控制数据流时，区域托管路由是中间方案。

## 其他 OpenAI 兼容的本地代理

vLLM、LiteLLM、OAI-proxy 或自定义网关如果暴露 OpenAI 风格的 `/v1` 端点即可使用。将上面的提供者块替换为你的端点和模型 ID：

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
            name: "本地模型",
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

保持 `models.mode: "merge