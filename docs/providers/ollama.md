---
summary: "Run OpenClaw with Ollama (local LLM runtime)"
read_when:
  - You want to run OpenClaw with local models via Ollama
  - You need Ollama setup and configuration guidance
title: "Ollama"
---
# Ollama

Ollama 是一个本地的大语言模型（LLM）运行时，使您能够在自己的机器上轻松运行开源模型。OpenClaw 与 Ollama 的 OpenAI 兼容 API 集成，并且在您启用 `OLLAMA_API_KEY`（或认证配置文件）且未定义显式的 `models.providers.ollama` 条目时，可以**自动发现具备工具能力的模型**。

## 快速入门

1. 安装 Ollama: https://ollama.ai

2. 拉取模型：

```bash
ollama pull llama3.3
# 或
ollama pull qwen2.5-coder:32b
# 或
ollama pull deepseek-r1:32b
```

3. 启用 Ollama 用于 OpenClaw（任意值均可；Ollama 不需要真实密钥）：

```bash
# 设置环境变量
export OLLAMA_API_KEY="ollama-local"

# 或在配置文件中配置
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

当您设置 `OLLAMA_API_KEY`（或认证配置文件）且**未定义** `models.providers.ollama` 时，OpenClaw 会从本地 Ollama 实例（位于 `http://127.0.0.1:11434`）发现模型：

- 查询 `/api/tags` 和 `/api/show`
- 仅保留报告 `tools` 能力的模型
- 当模型报告 `thinking` 时标记 `reasoning`
- 从 `model_info["<arch>.context_length"]` 读取 `contextWindow`（如有）
- 将 `maxTokens` 设置为上下文窗口的 10 倍
- 将所有费用设置为 `0`

这避免了手动输入模型条目，同时保持目录与 Ollama 能力同步。

查看可用模型：

```bash
ollama list
openclaw models list
```

要添加新模型，只需使用 Ollama 拉取：

```bash
ollama pull mistral
```

新模型将被自动发现并可供使用。

如果您显式设置了 `models.providers.ollama`，则跳过自动发现，必须手动定义模型（见下文）。

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
- 您希望包含未报告工具支持的模型。

```json5
{
  models: {
    providers: {
      ollama: {
        // 使用包含 /v1 的主机以支持 OpenAI 兼容 API
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

如果已设置 `OLLAMA_API_KEY`，您可以在提供者条目中省略 `apiKey`，OpenClaw 会在可用性检查时自动填充。

### 自定义基础 URL（显式配置）

如果 Ollama 运行在不同的主机或端口上（显式配置禁用自动发现，因此需手动定义模型）：

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

配置完成后，所有 Ollama 模型均可使用：

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

## 高级功能

### 推理模型

当 Ollama 在 `/api/show` 中报告 `thinking` 时，OpenClaw 会将模型标记为推理能力：

```bash
ollama pull deepseek-r1:32b
```

### 模型费用

Ollama 是免费的本地运行，因此所有模型费用均设为 $0。

### 上下文窗口

对于自动发现的模型，OpenClaw 会使用 Ollama 报告的上下文窗口（如有），否则默认为 `8192`。您可以在显式提供者配置中覆盖 `contextWindow` 和 `maxTokens`。

## 故障排除

### 未检测到 Ollama

确保 Ollama 正在运行，并且您设置了 `OLLAMA_API_KEY`（或认证配置文件），并且**未定义**显式的 `models.providers.ollama` 条目：

```bash
ollama serve
```

并确保 API 可访问：

```bash
curl http://localhost:11434/api/tags
```

### 没有可用模型

OpenClaw 仅自动发现报告工具支持的模型。如果您的模型未列出，要么：

- 拉取一个具备工具能力的模型，或
- 在 `models.providers.ollama` 中显式定义模型。

添加模型：

```bash
ollama list  # 查看已安装的模型
ollama pull llama3.3  # 拉取模型
```

### 连接被拒绝

检查 Ollama 是否在正确端口运行：

```bash
# 检查 Ollama 是否正在运行
ps aux | grep ollama

# 或重启 Ollama
ollama serve
```

## 参见

- [模型提供者](/concepts/model-providers) - 所有提供者的概述
- [模型选择](/concepts/models) - 如何选择模型
- [配置](/gateway/configuration) - 完整配置参考