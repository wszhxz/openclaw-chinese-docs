---
summary: "Run OpenClaw with Ollama (local LLM runtime)"
read_when:
  - You want to run OpenClaw with local models via Ollama
  - You need Ollama setup and configuration guidance
title: "Ollama"
---
# Ollama

Ollama 是一个本地大语言模型（LLM）运行时环境，可让您轻松在本地机器上运行开源模型。OpenClaw 通过 Ollama 的原生 API（`/api/chat`）与其集成，支持流式响应和工具调用；当您启用 `OLLAMA_API_KEY`（或一个认证配置文件）且未显式定义 `models.providers.ollama` 条目时，OpenClaw 可**自动发现具备工具调用能力的模型**。

<Warning>
**Remote Ollama users**: Do not use the __CODE_BLOCK_3__ OpenAI-compatible URL (__CODE_BLOCK_4__) with OpenClaw. This breaks tool calling and models may output raw tool JSON as plain text. Use the native Ollama API URL instead: __CODE_BLOCK_5__ (no __CODE_BLOCK_6__).
</Warning>

## 快速开始

1. 安装 Ollama：[https://ollama.ai](https://ollama.ai)

2. 拉取一个模型：

```bash
ollama pull gpt-oss:20b
# or
ollama pull llama3.3
# or
ollama pull qwen2.5-coder:32b
# or
ollama pull deepseek-r1:32b
```

3. 为 OpenClaw 启用 Ollama（任意值均可；Ollama 不需要真实密钥）：

```bash
# Set environment variable
export OLLAMA_API_KEY="ollama-local"

# Or configure in your config file
openclaw config set models.providers.ollama.apiKey "ollama-local"
```

4. 使用 Ollama 模型：

```json5
{
  agents: {
    defaults: {
      model: { primary: "ollama/gpt-oss:20b" },
    },
  },
}
```

## 模型发现（隐式提供方）

当您设置了 `OLLAMA_API_KEY`（或一个认证配置文件），且**未**定义 `models.providers.ollama` 时，OpenClaw 将从本地 Ollama 实例（地址为 `http://127.0.0.1:11434`）中自动发现模型：

- 查询 `/api/tags` 和 `/api/show`
- 仅保留声明具备 `tools` 能力的模型
- 当模型声明支持 `thinking` 时，标记为 `reasoning`
- 在可用时，从 `model_info["<arch>.context_length"]` 中读取 `contextWindow`
- 将 `maxTokens` 设置为上下文窗口长度的 10 倍
- 将所有费用设为 `0`

此举可避免手动录入模型条目，同时确保模型目录与 Ollama 的实际能力保持一致。

要查看当前可用的模型列表：

```bash
ollama list
openclaw models list
```

如需添加新模型，只需使用 Ollama 拉取即可：

```bash
ollama pull mistral
```

新模型将被自动发现并立即可供使用。

若您显式设置了 `models.providers.ollama`，则自动发现功能将被跳过，您必须手动定义模型（参见下文）。

## 配置

### 基础配置（隐式发现）

启用 Ollama 的最简单方式是通过环境变量：

```bash
export OLLAMA_API_KEY="ollama-local"
```

### 显式配置（手动定义模型）

在以下情况下，请使用显式配置：

- Ollama 运行在其他主机或端口上。
- 您希望强制指定上下文窗口大小或模型列表。
- 您希望包含那些未声明支持工具调用的模型。

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434",
        apiKey: "ollama-local",
        api: "ollama",
        models: [
          {
            id: "gpt-oss:20b",
            name: "GPT-OSS 20B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 8192,
            maxTokens: 8192 * 10
          }
        ]
      }
    }
  }
}
```

若已设置 `OLLAMA_API_KEY`，则可在提供方条目中省略 `apiKey`，OpenClaw 将自动填充该字段用于可用性检查。

### 自定义基础 URL（显式配置）

若 Ollama 运行在其他主机或端口上（显式配置会禁用自动发现，因此需手动定义模型）：

```json5
{
  models: {
    providers: {
      ollama: {
        apiKey: "ollama-local",
        baseUrl: "http://ollama-host:11434", // No /v1 - use native Ollama API URL
        api: "ollama", // Set explicitly to guarantee native tool-calling behavior
      },
    },
  },
}
```

<Warning>
Do not add __CODE_BLOCK_30__ to the URL. The __CODE_BLOCK_31__ path uses OpenAI-compatible mode, where tool calling is not reliable. Use the base Ollama URL without a path suffix.
</Warning>

### 模型选择

完成配置后，您所有的 Ollama 模型均将可用：

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## 高级功能

### 推理模型

当 Ollama 在 `/api/show` 中报告 `thinking` 时，OpenClaw 将该模型标记为具备推理能力：

```bash
ollama pull deepseek-r1:32b
```

### 模型费用

Ollama 免费且在本地运行，因此所有模型费用均设为 $0。

### 流式传输配置

OpenClaw 的 Ollama 集成默认使用**原生 Ollama API**（`/api/chat`），该 API 完全支持流式响应与工具调用同时进行。无需任何特殊配置。

#### 传统 OpenAI 兼容模式

<Warning>
**Tool calling is not reliable in OpenAI-compatible mode.** Use this mode only if you need OpenAI format for a proxy and do not depend on native tool calling behavior.
</Warning>

若您需要改用 OpenAI 兼容端点（例如，在仅支持 OpenAI 格式的代理之后运行），请显式设置 `api: "openai-completions"`：

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: true, // default: true
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

该模式可能无法同时支持流式响应与工具调用。您可能需要在模型配置中通过 `params: { streaming: false }` 禁用流式响应。

当对 Ollama 使用 `api: "openai-completions"` 时，OpenClaw 默认注入 `options.num_ctx`，以防止 Ollama 静默回退至 4096 的上下文窗口。若您的代理/上游服务拒绝未知的 `options` 字段，请禁用此行为：

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: false,
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

### 上下文窗口

对于自动发现的模型，OpenClaw 在可用时采用 Ollama 报告的上下文窗口大小，否则默认使用 `8192`。您可在显式提供方配置中覆盖 `contextWindow` 和 `maxTokens`。

## 故障排除

### 未检测到 Ollama

请确认 Ollama 正在运行，并已设置 `OLLAMA_API_KEY`（或一个认证配置文件），且**未**定义显式的 `models.providers.ollama` 条目：

```bash
ollama serve
```

并确认 API 可正常访问：

```bash
curl http://localhost:11434/api/tags
```

### 无可选模型

OpenClaw 仅自动发现声明支持工具调用的模型。若您的模型未出现在列表中，则可：

- 拉取一个支持工具调用的模型，或  
- 在 `models.providers.ollama` 中显式定义该模型。

添加模型的方法如下：

```bash
ollama list  # See what's installed
ollama pull gpt-oss:20b  # Pull a tool-capable model
ollama pull llama3.3     # Or another model
```

### 连接被拒绝

请检查 Ollama 是否正在正确的端口上运行：

```bash
# Check if Ollama is running
ps aux | grep ollama

# Or restart Ollama
ollama serve
```

## 参阅

- [模型提供方](/concepts/model-providers) — 所有提供方概述  
- [模型选择](/concepts/models) — 如何选择模型  
- [配置](/gateway/configuration) — 完整配置参考