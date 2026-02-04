---
summary: "Run OpenClaw with Ollama (local LLM runtime)"
read_when:
  - You want to run OpenClaw with local models via Ollama
  - You need Ollama setup and configuration guidance
title: "Ollama"
---
# Ollama

Ollama 是一个本地LLM运行时，使您能够在机器上轻松运行开源模型。OpenClaw 集成了 Ollama 的 OpenAI 兼容 API，并且当您使用 `OLLAMA_API_KEY`（或身份验证配置文件）并且未定义显式的 `models.providers.ollama` 条目时，可以**自动发现支持工具的模型**。

## 快速入门

1. 安装 Ollama: https://ollama.ai

2. 拉取一个模型：

```bash
ollama pull llama3.3
# or
ollama pull qwen2.5-coder:32b
# or
ollama pull deepseek-r1:32b
```

3. 为 OpenClaw 启用 Ollama（任何值都有效；Ollama 不需要真实的密钥）：

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
      model: { primary: "ollama/llama3.3" },
    },
  },
}
```

## 模型发现（隐式提供者）

当您设置 `OLLAMA_API_KEY`（或身份验证配置文件）并且**不**定义 `models.providers.ollama` 时，OpenClaw 会从本地 Ollama 实例 `http://127.0.0.1:11434` 发现模型：

- 查询 `/api/tags` 和 `/api/show`
- 仅保留报告 `tools` 能力的模型
- 当模型报告 `thinking` 时标记 `reasoning`
- 当可用时从 `model_info["<arch>.context_length"]` 读取 `contextWindow`
- 将 `maxTokens` 设置为上下文窗口的 10 倍
- 将所有成本设置为 `0`

这避免了手动输入模型条目，同时保持目录与 Ollama 的能力一致。

要查看可用的模型：

```bash
ollama list
openclaw models list
```

要添加新模型，只需使用 Ollama 拉取它：

```bash
ollama pull mistral
```

新模型将被自动发现并可供使用。

如果您显式设置 `models.providers.ollama`，则会跳过自动发现，您必须手动定义模型（见下文）。

## 配置

### 基本设置（隐式发现）

启用 Ollama 的最简单方法是通过环境变量：

```bash
export OLLAMA_API_KEY="ollama-local"
```

### 显式设置（手动模型）

在以下情况下使用显式配置：

- Ollama 运行在另一台主机/端口上。
- 您希望强制特定的上下文窗口或模型列表。
- 您希望包括不报告工具支持的模型。

```json5
{
  models: {
    providers: {
      ollama: {
        // Use a host that includes /v1 for OpenAI-compatible APIs
        baseUrl: "http://ollama-host:11434/v1",
        apiKey: "ollama-local",
        api: "openai-completions",
        models: [
          {
            id: "llama3.3",
            name: "Llama 3.3",
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

如果设置了 `OLLAMA_API_KEY`，可以在提供者条目中省略 `apiKey`，OpenClaw 将为其填充以进行可用性检查。

### 自定义基础 URL（显式配置）

如果 Ollama 运行在不同的主机或端口上（显式配置会禁用自动发现，因此必须手动定义模型）：

```json5
{
  models: {
    providers: {
      ollama: {
        apiKey: "ollama-local",
        baseUrl: "http://ollama-host:11434/v1",
      },
    },
  },
}
```

### 模型选择

配置完成后，所有您的 Ollama 模型都将可用：

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/llama3.3",
        fallback: ["ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## 高级

### 推理模型

当 Ollama 在 `/api/show` 中报告 `thinking` 时，OpenClaw 将模型标记为支持推理：

```bash
ollama pull deepseek-r1:32b
```

### 模型成本

Ollama 是免费的并且本地运行，因此所有模型的成本都设置为 $0。

### 上下文窗口

对于自动发现的模型，OpenClaw 使用 Ollama 报告的上下文窗口（如果可用），否则默认为 `8192`。您可以在显式提供者配置中覆盖 `contextWindow` 和 `maxTokens`。

## 故障排除

### 未检测到 Ollama

确保 Ollama 正在运行并且您已设置 `OLLAMA_API_KEY`（或身份验证配置文件），并且您**未**定义显式的 `models.providers.ollama` 条目：

```bash
ollama serve
```

并且 API 是可访问的：

```bash
curl http://localhost:11434/api/tags
```

### 没有可用的模型

OpenClaw 仅自动发现报告工具支持的模型。如果您的模型未列出，则：

- 拉取一个支持工具的模型，或
- 在 `models.providers.ollama` 中显式定义该模型。

要添加模型：

```bash
ollama list  # See what's installed
ollama pull llama3.3  # Pull a model
```

### 连接被拒绝

检查 Ollama 是否在正确的端口上运行：

```bash
# Check if Ollama is running
ps aux | grep ollama

# Or restart Ollama
ollama serve
```

## 参见

- [模型提供者](/concepts/model-providers) - 所有提供者的概述
- [模型选择](/concepts/models) - 如何选择模型
- [配置](/gateway/configuration) - 完整的配置参考