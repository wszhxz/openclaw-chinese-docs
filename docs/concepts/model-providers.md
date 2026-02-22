---
summary: "Model provider overview with example configs + CLI flows"
read_when:
  - You need a provider-by-provider model setup reference
  - You want example configs or CLI onboarding commands for model providers
title: "Model Providers"
---
# 模型提供商

本页面涵盖 **LLM/模型提供商**（不是WhatsApp/Telegram等聊天渠道）。
有关模型选择规则，请参阅 [/concepts/models](/concepts/models)。

## 快速规则

- 模型引用使用 `provider/model`（示例：`opencode/claude-opus-4-6`）。
- 如果设置了 `agents.defaults.models`，则成为允许列表。
- CLI 辅助工具：`openclaw onboard`，`openclaw models list`，`openclaw models set <provider/model>`。

## API 密钥轮换

- 支持选定提供商的通用提供商轮换。
- 通过以下方式配置多个密钥：
  - `OPENCLAW_LIVE_<PROVIDER>_KEY`（单个实时覆盖，优先级最高）
  - `<PROVIDER>_API_KEYS`（逗号或分号分隔列表）
  - `<PROVIDER>_API_KEY`（主密钥）
  - `<PROVIDER>_API_KEY_*`（编号列表，例如 `<PROVIDER>_API_KEY_1`）
- 对于Google提供商，还包括 `GOOGLE_API_KEY` 作为后备。
- 密钥选择顺序保留优先级并去重。
- 仅在收到速率限制响应时（例如 `429`，`rate_limit`，`quota`，`resource exhausted`），才会使用下一个密钥重试请求。
- 非速率限制失败会立即失败；不会尝试密钥轮换。
- 当所有候选密钥都失败时，将返回最后一次尝试的最终错误。

## 内置提供商（pi-ai 目录）

OpenClaw 随附 pi‑ai 目录。这些提供商不需要 **任何**
`models.providers` 配置；只需设置身份验证并选择一个模型。

### OpenAI

- 提供商: `openai`
- 身份验证: `OPENAI_API_KEY`
- 可选轮换: `OPENAI_API_KEYS`，`OPENAI_API_KEY_1`，`OPENAI_API_KEY_2`，加上 `OPENCLAW_LIVE_OPENAI_KEY`（单个覆盖）
- 示例模型: `openai/gpt-5.1-codex`
- CLI: `openclaw onboard --auth-choice openai-api-key`

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.1-codex" } } },
}
```

### Anthropic

- 提供商: `anthropic`
- 身份验证: `ANTHROPIC_API_KEY` 或 `claude setup-token`
- 可选轮换: `ANTHROPIC_API_KEYS`，`ANTHROPIC_API_KEY_1`，`ANTHROPIC_API_KEY_2`，加上 `OPENCLAW_LIVE_ANTHROPIC_KEY`（单个覆盖）
- 示例模型: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice token`（粘贴setup-token）或 `openclaw models auth paste-token --provider anthropic`

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- 提供商: `openai-codex`
- 身份验证: OAuth（ChatGPT）
- 示例模型: `openai-codex/gpt-5.3-codex`
- CLI: `openclaw onboard --auth-choice openai-codex` 或 `openclaw models auth login --provider openai-codex`

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.3-codex" } } },
}
```

### OpenCode Zen

- 提供商: `opencode`
- 身份验证: `OPENCODE_API_KEY`（或 `OPENCODE_ZEN_API_KEY`）
- 示例模型: `opencode/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice opencode-zen`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini (API key)

- 提供者: `google`
- 认证: `GEMINI_API_KEY`
- 可选轮换: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, `GOOGLE_API_KEY` 备用，以及 `OPENCLAW_LIVE_GEMINI_KEY` (单个覆盖)
- 示例模型: `google/gemini-3-pro-preview`
- 命令行界面: `openclaw onboard --auth-choice gemini-api-key`

### Google Vertex, Antigravity, 和 Gemini 命令行界面

- 提供者: `google-vertex`, `google-antigravity`, `google-gemini-cli`
- 认证: Vertex 使用 gcloud ADC；Antigravity/Gemini 命令行界面使用各自的认证流程
- Antigravity OAuth 作为捆绑插件提供 (`google-antigravity-auth`, 默认禁用)。
  - 启用: `openclaw plugins enable google-antigravity-auth`
  - 登录: `openclaw models auth login --provider google-antigravity --set-default`
- Gemini 命令行界面 OAuth 作为捆绑插件提供 (`google-gemini-cli-auth`, 默认禁用)。
  - 启用: `openclaw plugins enable google-gemini-cli-auth`
  - 登录: `openclaw models auth login --provider google-gemini-cli --set-default`
  - 注意: 您**不**需要将客户端 ID 或密钥粘贴到 `openclaw.json`。命令行登录流程会在网关主机的身份验证配置文件中存储令牌。

### Z.AI (GLM)

- 提供者: `zai`
- 认证: `ZAI_API_KEY`
- 示例模型: `zai/glm-4.7`
- 命令行界面: `openclaw onboard --auth-choice zai-api-key`
  - 别名: `z.ai/*` 和 `z-ai/*` 规范化为 `zai/*`

### Vercel AI 网关

- 提供者: `vercel-ai-gateway`
- 认证: `AI_GATEWAY_API_KEY`
- 示例模型: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- 命令行界面: `openclaw onboard --auth-choice ai-gateway-api-key`

### 其他内置提供者

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- 示例模型: `openrouter/anthropic/claude-sonnet-4-5`
- xAI: `xai` (`XAI_API_KEY`)
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - Cerebras 上的 GLM 模型使用 ID `zai-glm-4.7` 和 `zai-glm-4.6`。
  - OpenAI 兼容的基础 URL: `https://api.cerebras.ai/v1`。
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Hugging Face 推理: `huggingface` (`HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN`) — OpenAI 兼容路由器；示例模型: `huggingface/deepseek-ai/DeepSeek-R1`；命令行界面: `openclaw onboard --auth-choice huggingface-api-key`。参见 [Hugging Face (推理)](/providers/huggingface)。

## 通过 `models.providers` (自定义/基础 URL) 的提供者

使用 `models.providers` (或 `models.json`) 添加 **自定义** 提供者或
OpenAI/Anthropic 兼容代理。

### Moonshot AI (Kimi)

Moonshot 使用 OpenAI 兼容的端点，因此将其配置为自定义提供者：

- 提供者: `moonshot`
- 认证: `MOONSHOT_API_KEY`
- 示例模型: `moonshot/kimi-k2.5`

Kimi K2 模型 ID:

{/_moonshot-kimi-k2-model-refs:start_/ && null}

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-0905-preview`
- `moonshot/kimi-k2-turbo-preview`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
  {/_moonshot-kimi-k2-model-refs:end_/ && null}

```json5
{
  agents: {
    defaults: { model: { primary: "moonshot/kimi-k2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5" }],
      },
    },
  },
}
```

### Kimi Coding

Kimi Coding 使用 Moonshot AI 的 Anthropic 兼容端点：

- Provider: `kimi-coding`
- Auth: `KIMI_API_KEY`
- Example model: `kimi-coding/k2p5`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi-coding/k2p5" } },
  },
}
```

### Qwen OAuth (免费层)

Qwen 通过设备代码流提供对 Qwen Coder + Vision 的 OAuth 访问。
启用捆绑插件，然后登录：

```bash
openclaw plugins enable qwen-portal-auth
openclaw models auth login --provider qwen-portal --set-default
```

模型引用：

- `qwen-portal/coder-model`
- `qwen-portal/vision-model`

有关设置详细信息和注意事项，请参阅 [/providers/qwen](/providers/qwen)。

### 火山引擎 (Doubao)

火山引擎 (Volcano Engine) 提供对中国市场的 Doubao 和其他模型的访问。

- Provider: `volcengine` (coding: `volcengine-plan`)
- Auth: `VOLCANO_ENGINE_API_KEY`
- Example model: `volcengine/doubao-seed-1-8-251228`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine/doubao-seed-1-8-251228" } },
  },
}
```

可用模型：

- `volcengine/doubao-seed-1-8-251228` (Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` (Kimi K2.5)
- `volcengine/glm-4-7-251222` (GLM 4.7)
- `volcengine/deepseek-v3-2-251201` (DeepSeek V3.2 128K)

编码模型 (`volcengine-plan`)：

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### 字节跳动 (国际)

字节跳动 ARK 为国际用户提供与火山引擎相同的模型访问。

- Provider: `byteplus` (coding: `byteplus-plan`)
- Auth: `BYTEPLUS_API_KEY`
- Example model: `byteplus/seed-1-8-251228`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus/seed-1-8-251228" } },
  },
}
```

可用模型：

- `byteplus/seed-1-8-251228` (Seed 1.8)
- `byteplus/kimi-k2-5-260127` (Kimi K2.5)
- `byteplus/glm-4-7-251222` (GLM 4.7)

编码模型 (`byteplus-plan`)：

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic 提供 `synthetic` 提供商后的 Anthropic 兼容模型：

- Provider: `synthetic`
- Auth: `SYNTHETIC_API_KEY`
- Example model: `synthetic/hf:MiniMaxAI/MiniMax-M2.1`
- CLI: `openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.1" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.1", name: "MiniMax M2.1" }],
      },
    },
  },
}
```

### MiniMax

MiniMax 通过 `models.providers` 进行配置，因为它使用自定义端点：

- MiniMax (Anthropic 兼容): `--auth-choice minimax-api`
- 认证: `MINIMAX_API_KEY`

有关设置详细信息、模型选项和配置片段，请参阅 [/providers/minimax](/providers/minimax)。

### Ollama

Ollama 是一个本地 LLM 运行时，提供 OpenAI 兼容的 API：

- 提供者: `ollama`
- 认证: 无需认证（本地服务器）
- 示例模型: `ollama/llama3.3`
- 安装: [https://ollama.ai](https://ollama.ai)

```bash
# Install Ollama, then pull a model:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

当在 `http://127.0.0.1:11434/v1` 本地运行时，会自动检测到 Ollama。有关模型推荐和自定义配置，请参阅 [/providers/ollama](/providers/ollama)。

### vLLM

vLLM 是一个本地（或自托管）的 OpenAI 兼容服务器：

- 提供者: `vllm`
- 认证: 可选（取决于您的服务器）
- 默认基础 URL: `http://127.0.0.1:8000/v1`

要选择本地自动发现（如果您的服务器不强制认证，则任何值都有效）：

```bash
export VLLM_API_KEY="vllm-local"
```

然后设置一个模型（替换为由 `/v1/models` 返回的 ID 中的一个）：

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

有关详细信息，请参阅 [/providers/vllm](/providers/vllm)。

### 本地代理（LM Studio、vLLM、LiteLLM 等）

示例（OpenAI 兼容）：

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/minimax-m2.1-gs32" },
      models: { "lmstudio/minimax-m2.1-gs32": { alias: "Minimax" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "LMSTUDIO_KEY",
        api: "openai-completions",
        models: [
          {
            id: "minimax-m2.1-gs32",
            name: "MiniMax M2.1",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

注意：

- 对于自定义提供者，`reasoning`、`input`、`cost`、`contextWindow` 和 `maxTokens` 是可选的。
  当省略时，OpenClaw 默认为：
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- 建议：设置与您的代理/模型限制相匹配的显式值。

## CLI 示例

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

另请参阅：[/gateway/configuration](/gateway/configuration) 获取完整的配置示例。