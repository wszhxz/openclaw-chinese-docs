---
summary: "Use Venice AI privacy-focused models in OpenClaw"
read_when:
  - You want privacy-focused inference in OpenClaw
  - You want Venice AI setup guidance
title: "Venice AI"
---
# Venice AI（Venice 高亮功能）

**Venice** 是我们主打的 Venice 配置方案，专为注重隐私的推理而设计，可选择性地通过匿名化方式访问专有模型。

Venice AI 提供以隐私为中心的 AI 推理服务，支持无审查模型，并可通过其匿名化代理访问主流专有模型（如 Opus/GPT/Gemini）。所有推理默认私密——不会基于您的数据进行训练，也不会记录日志。

## 为何在 OpenClaw 中使用 Venice

- **私密推理**：面向开源模型（不记录日志）。
- **无审查模型**：按需启用。
- **匿名化访问专有模型**：当质量至关重要时，可访问 Claude、GPT、Gemini 等模型。
- 兼容 OpenAI 的 `/v1` 接口端点。

## 隐私模式

Venice 提供两种隐私级别——理解其区别是选择合适模型的关键：

| 模式         | 描述                                                                                                                       | 模型                                                        |
| ------------ | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **私密**     | 完全私密。提示词/响应**永不存储或记录**。临时性。                                                                           | Llama、Qwen、DeepSeek、Kimi、MiniMax、Venice Uncensored 等。 |
| **匿名化**   | 经 Venice 代理转发，元数据已被剥离。底层服务商（OpenAI、Anthropic、Google、xAI）仅看到已匿名化的请求。                         | Claude、GPT、Gemini、Grok                                     |

## 功能特性

- **以隐私为中心**：可在“私密”（完全私密）与“匿名化”（经代理）模式间自由选择  
- **无审查模型**：可访问不受内容限制的模型  
- **主流模型接入**：通过 Venice 的匿名化代理使用 Claude、GPT、Gemini 和 Grok  
- **兼容 OpenAI 的 API**：标准 `/v1` 接口端点，便于快速集成  
- **流式响应**：✅ 所有模型均支持  
- **函数调用**：✅ 部分模型支持（请查阅各模型能力说明）  
- **视觉能力**：✅ 支持具备视觉能力的模型  
- **无硬性速率限制**：极端用量下可能触发公平使用限流  

## 配置步骤

### 1. 获取 API 密钥

1. 在 [venice.ai](https://venice.ai) 注册账号  
2. 进入 **Settings → API Keys → Create new key**  
3. 复制您的 API 密钥（格式：`vapi_xxxxxxxxxxxx`）

### 2. 配置 OpenClaw

**选项 A：环境变量方式**

```bash
export VENICE_API_KEY="vapi_xxxxxxxxxxxx"
```

**选项 B：交互式配置（推荐）**

```bash
openclaw onboard --auth-choice venice-api-key
```

该操作将：

1. 提示您输入 API 密钥（或复用已存在的 `VENICE_API_KEY`）  
2. 展示所有可用的 Venice 模型  
3. 允许您选择默认模型  
4. 自动完成提供商配置  

**选项 C：非交互式配置**

```bash
openclaw onboard --non-interactive \
  --auth-choice venice-api-key \
  --venice-api-key "vapi_xxxxxxxxxxxx"
```

### 3. 验证配置

```bash
openclaw agent --model venice/kimi-k2-5 --message "Hello, are you working?"
```

## 模型选择

完成配置后，OpenClaw 将列出所有可用的 Venice 模型。请根据实际需求选择：

- **默认模型**：`venice/kimi-k2-5` —— 强大的私密推理能力，且支持视觉功能。  
- **高能力选项**：`venice/claude-opus-4-6` —— Venice 匿名化路径中能力最强的模型。  
- **隐私优先**：选择“私密”类模型以实现完全私密的推理。  
- **能力优先**：选择“匿名化”类模型，通过 Venice 代理访问 Claude、GPT、Gemini。

随时可更改默认模型：

```bash
openclaw models set venice/kimi-k2-5
openclaw models set venice/claude-opus-4-6
```

列出所有可用模型：

```bash
openclaw models list | grep venice
```

## 通过 `openclaw configure` 配置

1. 运行 `openclaw configure`  
2. 选择 **Model/auth**  
3. 选择 **Venice AI**

## 我该选用哪个模型？

| 使用场景                   | 推荐模型                | 原因                                          |
| -------------------------- | ----------------------- | --------------------------------------------- |
| **通用对话（默认）**       | `kimi-k2-5`             | 强大的私密推理能力，且支持视觉功能            |
| **整体最佳质量**           | `claude-opus-4-6`         | Venice 匿名化路径中能力最强的选项             |
| **兼顾隐私与编程**         | `qwen3-coder-480b-a35b-instruct` | 私密编程模型，支持超大上下文                  |
| **私密视觉任务**           | `kimi-k2-5`             | 支持视觉能力，且无需退出私密模式              |
| **快速 + 低成本**          | `qwen3-4b`               | 轻量级推理模型                                |
| **复杂私密任务**           | `deepseek-v3.2`           | 强大推理能力，但暂不支持 Venice 工具调用      |
| **无审查需求**             | `venice-uncensored`         | 不受任何内容限制                              |

## 可用模型（共 41 款）

### 私密模型（26 款）—— 完全私密，不记录日志

| 模型 ID                               | 名称                                | 上下文长度 | 特性                     |
| -------------------------------------- | ----------------------------------- | ---------- | ------------------------ |
| `kimi-k2-5`                            | Kimi K2.5                           | 256k       | 默认模型，支持推理与视觉 |
| `kimi-k2-thinking`                     | Kimi K2 Thinking                    | 256k       | 推理专用                 |
| `llama-3.3-70b`                        | Llama 3.3 70B                       | 128k       | 通用型                   |
| `llama-3.2-3b`                         | Llama 3.2 3B                        | 128k       | 通用型                   |
| `hermes-3-llama-3.1-405b`              | Hermes 3 Llama 3.1 405B             | 128k       | 通用型，禁用工具         |
| `qwen3-235b-a22b-thinking-2507`        | Qwen3 235B Thinking                 | 128k       | 推理专用                 |
| `qwen3-235b-a22b-instruct-2507`        | Qwen3 235B Instruct                 | 128k       | 通用型                   |
| `qwen3-coder-480b-a35b-instruct`       | Qwen3 Coder 480B                    | 256k       | 编程专用                 |
| `qwen3-coder-480b-a35b-instruct-turbo` | Qwen3 Coder 480B Turbo              | 256k       | 编程专用                 |
| `qwen3-5-35b-a3b`                      | Qwen3.5 35B A3B                     | 256k       | 推理与视觉支持           |
| `qwen3-next-80b`                       | Qwen3 Next 80B                      | 256k       | 通用型                   |
| `qwen3-vl-235b-a22b`                   | Qwen3 VL 235B (Vision)              | 256k       | 视觉专用                 |
| `qwen3-4b`                             | Venice Small (Qwen3 4B)             | 32k        | 快速响应，支持推理       |
| `deepseek-v3.2`                        | DeepSeek V3.2                       | 160k       | 推理专用，禁用工具       |
| `venice-uncensored`                    | Venice Uncensored (Dolphin-Mistral) | 32k        | 无审查，禁用工具         |
| `mistral-31-24b`                       | Venice Medium (Mistral)             | 128k       | 视觉支持                 |
| `google-gemma-3-27b-it`                | Google Gemma 3 27B Instruct         | 198k       | 视觉支持                 |
| `openai-gpt-oss-120b`                  | OpenAI GPT OSS 120B                 | 128k       | 通用型                   |
| `nvidia-nemotron-3-nano-30b-a3b`       | NVIDIA Nemotron 3 Nano 30B          | 128k       | 通用型                   |
| `olafangensan-glm-4.7-flash-heretic`   | GLM 4.7 Flash Heretic               | 128k       | 推理专用                 |
| `zai-org-glm-4.6`                      | GLM 4.6                             | 198k       | 通用型                   |
| `zai-org-glm-4.7`                      | GLM 4.7                             | 198k       | 推理专用                 |
| `zai-org-glm-4.7-flash`                | GLM 4.7 Flash                       | 128k       | 推理专用                 |
| `zai-org-glm-5`                        | GLM 5                               | 198k       | 推理专用                 |
| `minimax-m21`                          | MiniMax M2.1                        | 198k       | 推理专用                 |
| `minimax-m25`                          | MiniMax M2.5                        | 198k       | 推理专用                 |

### 匿名化模型（15 款）—— 经 Venice 代理提供

| 模型 ID                        | 名称                           | 上下文长度 | 功能                  |
| ------------------------------- | ------------------------------ | ---------- | ------------------------- |
| `claude-opus-4-6`               | Claude Opus 4.6 (via Venice)   | 1M         | 推理、视觉         |
| `claude-opus-4-5`               | Claude Opus 4.5 (via Venice)   | 198k       | 推理、视觉         |
| `claude-sonnet-4-6`             | Claude Sonnet 4.6 (via Venice) | 1M         | 推理、视觉         |
| `claude-sonnet-4-5`             | Claude Sonnet 4.5 (via Venice) | 198k       | 推理、视觉         |
| `openai-gpt-54`                 | GPT-5.4 (via Venice)           | 1M         | 推理、视觉         |
| `openai-gpt-53-codex`           | GPT-5.3 Codex (via Venice)     | 400k       | 推理、视觉、编程   |
| `openai-gpt-52`                 | GPT-5.2 (via Venice)           | 256k       | 推理                 |
| `openai-gpt-52-codex`           | GPT-5.2 Codex (via Venice)     | 256k       | 推理、视觉、编程   |
| `openai-gpt-4o-2024-11-20`      | GPT-4o (via Venice)            | 128k       | 视觉                    |
| `openai-gpt-4o-mini-2024-07-18` | GPT-4o Mini (via Venice)       | 128k       | 视觉                    |
| `gemini-3-1-pro-preview`        | Gemini 3.1 Pro (via Venice)    | 1M         | 推理、视觉         |
| `gemini-3-pro-preview`          | Gemini 3 Pro (via Venice)      | 198k       | 推理、视觉         |
| `gemini-3-flash-preview`        | Gemini 3 Flash (via Venice)    | 256k       | 推理、视觉         |
| `grok-41-fast`                  | Grok 4.1 Fast (via Venice)     | 1M         | 推理、视觉         |
| `grok-code-fast-1`              | Grok Code Fast 1 (via Venice)  | 256k       | 推理、编程         |

## 模型发现

当设置 ``VENICE_API_KEY`` 时，OpenClaw 会自动从 Venice API 发现模型。如果 API 不可达，则回退至静态目录。

``/models`` 端点为公开端点（列出模型无需身份验证），但执行推理调用需提供有效的 API 密钥。

## 流式传输与工具支持

| 功能              | 支持                                                 |
| -------------------- | ------------------------------------------------------- |
| **流式传输**        | ✅ 所有模型                                           |
| **函数调用** | ✅ 大多数模型（请查阅 API 中的 ``supportsFunctionCalling``） |
| **视觉/图像**    | ✅ 标注有 “Vision” 功能的模型                  |
| **JSON 模式**        | ✅ 通过 ``response_format`` 支持                      |

## 定价

Venice 采用基于积分的计费系统。当前费率请参阅 [venice.ai/pricing](https://venice.ai/pricing)：

- **私有模型**：通常成本更低  
- **匿名化模型**：价格接近直接 API 定价 + 少量 Venice 手续费  

## 对比：Venice 与直接 API

| 方面       | Venice（匿名化）           | 直接 API          |
| ------------ | ----------------------------- | ------------------- |
| **隐私性**  | 元数据已剥离并匿名化 | 关联您的账户 |
| **延迟**  | +10–50ms（代理开销）              | 直连              |
| **功能** | 支持大多数功能       | 全功能支持       |
| **计费**  | 使用 Venice 积分                | 由服务商计费    |

## 使用示例

```bash
# Use the default private model
openclaw agent --model venice/kimi-k2-5 --message "Quick health check"

# Use Claude Opus via Venice (anonymized)
openclaw agent --model venice/claude-opus-4-6 --message "Summarize this task"

# Use uncensored model
openclaw agent --model venice/venice-uncensored --message "Draft options"

# Use vision model with image
openclaw agent --model venice/qwen3-vl-235b-a22b --message "Review attached image"

# Use coding model
openclaw agent --model venice/qwen3-coder-480b-a35b-instruct --message "Refactor this function"
```

## 故障排除

### API 密钥未被识别

```bash
echo $VENICE_API_KEY
openclaw models list | grep venice
```

确保密钥以 ``vapi_`` 开头。

### 模型不可用

Venice 模型目录动态更新。运行 ``openclaw models list`` 查看当前可用模型。部分模型可能暂时离线。

### 连接问题

Venice API 地址为 ``https://api.venice.ai/api/v1``。请确保您的网络允许 HTTPS 连接。

## 配置文件示例

```json5
{
  env: { VENICE_API_KEY: "vapi_..." },
  agents: { defaults: { model: { primary: "venice/kimi-k2-5" } } },
  models: {
    mode: "merge",
    providers: {
      venice: {
        baseUrl: "https://api.venice.ai/api/v1",
        apiKey: "${VENICE_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2-5",
            name: "Kimi K2.5",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 256000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

## 相关链接

- [Venice AI](https://venice.ai)  
- [API 文档](https://docs.venice.ai)  
- [定价](https://venice.ai/pricing)  
- [服务状态](https://status.venice.ai)