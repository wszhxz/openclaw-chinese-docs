---
summary: "Use OpenAI via API keys or Codex subscription in OpenClaw"
read_when:
  - You want to use OpenAI models in OpenClaw
  - You want Codex subscription auth instead of API keys
title: "OpenAI"
---
# OpenAI

OpenAI 为 GPT 模型提供开发者 API。Codex 支持通过 **ChatGPT 登录**获取订阅访问权限，或通过 **API 密钥**登录实现按用量计费的访问方式。Codex 云服务要求使用 ChatGPT 登录。OpenAI 明确支持在外部工具/工作流（例如 OpenClaw）中使用基于订阅的 OAuth 认证。

## 选项 A：OpenAI API 密钥（OpenAI 平台）

**最适合场景：** 直接调用 API 并按用量计费。  
请从 OpenAI 控制台获取您的 API 密钥。

### CLI 配置

```bash
openclaw onboard --auth-choice openai-api-key
# or non-interactive
openclaw onboard --openai-api-key "$OPENAI_API_KEY"
```

### 配置片段

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

OpenAI 当前的 API 模型文档中列出了用于直接调用 OpenAI API 的模型 `gpt-5.4` 和 `gpt-5.4-pro`。OpenClaw 将二者均通过 `openai/*` Responses 路径进行转发。

## 选项 B：OpenAI Code（Codex）订阅

**最适合场景：** 使用 ChatGPT/Codex 订阅权限而非 API 密钥。  
Codex 云服务要求使用 ChatGPT 登录；而 Codex CLI 同时支持 ChatGPT 登录和 API 密钥登录。

### CLI 配置（Codex OAuth）

```bash
# Run Codex OAuth in the wizard
openclaw onboard --auth-choice openai-codex

# Or run OAuth directly
openclaw models auth login --provider openai-codex
```

### 配置片段（Codex 订阅）

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

OpenAI 当前的 Codex 文档将 `gpt-5.4` 列为当前 Codex 模型。OpenClaw 将其映射为 `openai-codex/gpt-5.4`，以支持 ChatGPT/Codex OAuth 使用方式。

### 传输协议默认设置

OpenClaw 对模型流式响应使用 `pi-ai`。对于 `openai/*` 和 `openai-codex/*`，默认传输协议为 `"auto"`（优先使用 WebSocket，SSE 作为备选方案）。

您可以设置 `agents.defaults.models.<provider/model>.params.transport`：

- `"sse"`：强制使用 SSE  
- `"websocket"`：强制使用 WebSocket  
- `"auto"`：先尝试 WebSocket，失败后回退至 SSE  

对于 `openai/*`（Responses API），当启用 WebSocket 传输时，OpenClaw 默认也启用 WebSocket 预热功能（`openaiWsWarmup: true`）。

相关 OpenAI 文档：

- [使用 WebSocket 的实时 API](https://platform.openai.com/docs/guides/realtime-websocket)  
- [流式 API 响应（SSE）](https://platform.openai.com/docs/guides/streaming-responses)

```json5
{
  agents: {
    defaults: {
      model: { primary: "openai-codex/gpt-5.4" },
      models: {
        "openai-codex/gpt-5.4": {
          params: {
            transport: "auto",
          },
        },
      },
    },
  },
}
```

### OpenAI WebSocket 预热

OpenAI 文档中将预热描述为可选功能。OpenClaw 默认为 `openai/*` 启用该功能，以降低使用 WebSocket 传输时首轮响应的延迟。

### 禁用预热

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: false,
          },
        },
      },
    },
  },
}
```

### 显式启用预热

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: true,
          },
        },
      },
    },
  },
}
```

### OpenAI 优先级处理

OpenAI 的 API 通过 `service_tier=priority` 提供优先级处理能力。在 OpenClaw 中，设置 `agents.defaults.models["openai/<model>"].params.serviceTier` 即可在直接发送 `openai/*` Responses 请求时透传该字段。

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

支持的取值包括 `auto`、`default`、`flex` 和 `priority`。

### OpenAI Responses 服务端压缩

对于直接调用的 OpenAI Responses 模型（即使用 `api: "openai-responses"` 的 `openai/*`，且在 `api.openai.com` 上启用了 `baseUrl`），OpenClaw 现在自动启用 OpenAI 服务端压缩负载提示（payload hints）：

- 强制启用 `store: true`（除非模型兼容性配置设置了 `supportsStore: false`）  
- 注入 `context_management: [{ type: "compaction", compact_threshold: ... }]`  

默认情况下，`compact_threshold` 是模型 `contextWindow` 的 `70%`（若不可用则为 `80000`）。

### 显式启用服务端压缩

当您希望在兼容的 Responses 模型上强制注入 `context_management`（例如 Azure OpenAI Responses）时，请使用此配置：

```json5
{
  agents: {
    defaults: {
      models: {
        "azure-openai-responses/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
          },
        },
      },
    },
  },
}
```

### 使用自定义阈值启用

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
            responsesCompactThreshold: 120000,
          },
        },
      },
    },
  },
}
```

### 禁用服务端压缩

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: false,
          },
        },
      },
    },
  },
}
```

`responsesServerCompaction` 仅控制 `context_management` 的注入行为。对于直接调用的 OpenAI Responses 模型，仍会强制启用 `store: true`，除非兼容性配置中设置了 `supportsStore: false`。

## 注意事项

- 模型引用始终使用 `provider/model`（参见 [/concepts/models](/concepts/models)）。  
- 认证详情及复用规则详见 [/concepts/oauth](/concepts/oauth)。