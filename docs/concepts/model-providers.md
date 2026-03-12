---
summary: "Model provider overview with example configs + CLI flows"
read_when:
  - You need a provider-by-provider model setup reference
  - You want example configs or CLI onboarding commands for model providers
title: "Model Providers"
---
# 模型提供商

本页面涵盖 **大语言模型（LLM）/模型提供商**（不包括 WhatsApp/Telegram 等聊天渠道）。  
有关模型选择规则，请参阅 [/concepts/models](/concepts/models)。

## 快速规则

- 模型引用使用 `provider/model`（例如：`opencode/claude-opus-4-6`）。
- 若设置了 `agents.defaults.models`，则其将成为白名单。
- CLI 辅助命令：`openclaw onboard`、`openclaw models list`、`openclaw models set <provider/model>`。

## API 密钥轮换

- 支持为选定的提供商启用通用密钥轮换。
- 可通过以下方式配置多个密钥：
  - `OPENCLAW_LIVE_<PROVIDER>_KEY`（单次实时覆盖，最高优先级）
  - `<PROVIDER>_API_KEYS`（逗号或分号分隔的列表）
  - `<PROVIDER>_API_KEY`（主密钥）
  - `<PROVIDER>_API_KEY_*`（编号列表，例如 `<PROVIDER>_API_KEY_1`）
- 对于 Google 提供商，`GOOGLE_API_KEY` 也会作为备用密钥包含在内。
- 密钥选择顺序保留优先级并自动去重。
- 仅当响应为限流错误时（例如 `429`、`rate_limit`、`quota`、`resource exhausted`），请求才会使用下一个密钥重试。
- 非限流类失败将立即报错；不会尝试密钥轮换。
- 当所有候选密钥均失败时，最终错误将来自最后一次尝试。

## 内置提供商（pi-ai 目录）

OpenClaw 预装了 pi‑ai 目录。这些提供商 **无需** 配置 `models.providers`；只需设置认证信息并选择模型即可。

### OpenAI

- 提供商：`openai`
- 认证：`OPENAI_API_KEY`
- 可选密钥轮换：`OPENAI_API_KEYS`、`OPENAI_API_KEY_1`、`OPENAI_API_KEY_2`，以及 `OPENCLAW_LIVE_OPENAI_KEY`（单次覆盖）
- 示例模型：`openai/gpt-5.4`、`openai/gpt-5.4-pro`
- CLI：`openclaw onboard --auth-choice openai-api-key`
- 默认传输协议为 `auto`（优先使用 WebSocket，SSE 作为备选）
- 可通过 `agents.defaults.models["openai/<model>"].params.transport`（`"sse"`、`"websocket"` 或 `"auto"`）按模型覆盖
- OpenAI 响应 WebSocket 预热默认启用，由 `params.openaiWsWarmup` 控制（`true`/`false`）
- 可通过 `agents.defaults.models["openai/<model>"].params.serviceTier` 启用 OpenAI 优先处理

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- 提供商：`anthropic`
- 认证：`ANTHROPIC_API_KEY` 或 `claude setup-token`
- 可选密钥轮换：`ANTHROPIC_API_KEYS`、`ANTHROPIC_API_KEY_1`、`ANTHROPIC_API_KEY_2`，以及 `OPENCLAW_LIVE_ANTHROPIC_KEY`（单次覆盖）
- 示例模型：`anthropic/claude-opus-4-6`
- CLI：`openclaw onboard --auth-choice token`（粘贴 setup-token）或 `openclaw models auth paste-token --provider anthropic`
- 政策说明：setup-token 支持仅为技术兼容性；Anthropic 过去曾限制部分订阅用户在 Claude Code 之外使用该功能。请核实当前 Anthropic 条款，并根据自身风险承受能力做出决策。
- 建议：相比订阅 setup-token 认证，Anthropic API 密钥认证是更安全、更推荐的方式。

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code（Codex）

- 提供商：`openai-codex`
- 认证：OAuth（ChatGPT）
- 示例模型：`openai-codex/gpt-5.4`
- CLI：`openclaw onboard --auth-choice openai-codex` 或 `openclaw models auth login --provider openai-codex`
- 默认传输协议为 `auto`（优先使用 WebSocket，SSE 作为备选）
- 可通过 `agents.defaults.models["openai-codex/<model>"].params.transport`（`"sse"`、`"websocket"` 或 `"auto"`）按模型覆盖
- 政策说明：OpenAI Codex OAuth 明确支持用于 OpenClaw 等外部工具/工作流。

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

### OpenCode Zen

- 提供商：`opencode`
- 认证：`OPENCODE_API_KEY`（或 `OPENCODE_ZEN_API_KEY`）
- 示例模型：`opencode/claude-opus-4-6`
- CLI：`openclaw onboard --auth-choice opencode-zen`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini（API 密钥）

- 提供商：`google`
- 认证：`GEMINI_API_KEY`
- 可选密钥轮换：`GEMINI_API_KEYS`、`GEMINI_API_KEY_1`、`GEMINI_API_KEY_2`、`GOOGLE_API_KEY`（备用）、以及 `OPENCLAW_LIVE_GEMINI_KEY`（单次覆盖）
- 示例模型：`google/gemini-3.1-pro-preview`、`google/gemini-3-flash-preview`
- 兼容性：旧版 OpenClaw 配置中使用的 `google/gemini-3.1-flash-preview` 将被规范化为 `google/gemini-3-flash-preview`
- CLI：`openclaw onboard --auth-choice gemini-api-key`

### Google Vertex、Antigravity 和 Gemini CLI

- 提供商：`google-vertex`、`google-antigravity`、`google-gemini-cli`
- 认证：Vertex 使用 gcloud ADC；Antigravity/Gemini CLI 使用各自独立的认证流程
- 注意：Antigravity 和 Gemini CLI 在 OpenClaw 中的 OAuth 集成属于非官方支持。部分用户报告称，在使用第三方客户端后遭遇 Google 账户限制。请审阅 Google 相关条款，如决定继续使用，请务必使用非关键账户。
- Antigravity OAuth 以捆绑插件形式提供（`google-antigravity-auth`，默认禁用）。
  - 启用：`openclaw plugins enable google-antigravity-auth`
  - 登录：`openclaw models auth login --provider google-antigravity --set-default`
- Gemini CLI OAuth 以捆绑插件形式提供（`google-gemini-cli-auth`，默认禁用）。
  - 启用：`openclaw plugins enable google-gemini-cli-auth`
  - 登录：`openclaw models auth login --provider google-gemini-cli --set-default`
  - 注意：您 **无需** 将 client id 或 secret 粘贴至 `openclaw.json`。CLI 登录流程会将令牌存储在网关主机的认证配置文件中。

### Z.AI（GLM）

- 提供商：`zai`
- 认证：`ZAI_API_KEY`
- 示例模型：`zai/glm-5`
- CLI：`openclaw onboard --auth-choice zai-api-key`
  - 别名：`z.ai/*` 和 `z-ai/*` 将规范化为 `zai/*`

### Vercel AI Gateway

- 提供商：`vercel-ai-gateway`
- 认证：`AI_GATEWAY_API_KEY`
- 示例模型：`vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI：`openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- 提供商：`kilocode`
- 认证：`KILOCODE_API_KEY`
- 示例模型：`kilocode/anthropic/claude-opus-4.6`
- CLI：`openclaw onboard --kilocode-api-key <key>`
- 基础 URL：`https://api.kilo.ai/api/gateway/`
- 扩展内置目录包括：GLM-5 Free、MiniMax M2.5 Free、GPT-5.2、Gemini 3 Pro Preview、Gemini 3 Flash Preview、Grok Code Fast 1 和 Kimi K2.5。

设置详情请参阅 [/providers/kilocode](/providers/kilocode)。

### 其他内置提供商

- OpenRouter：`openrouter`（`OPENROUTER_API_KEY`）
- 示例模型：`openrouter/anthropic/claude-sonnet-4-5`
- Kilo Gateway：`kilocode`（`KILOCODE_API_KEY`）
- 示例模型：`kilocode/anthropic/claude-opus-4.6`
- xAI：`xai`（`XAI_API_KEY`）
- Mistral：`mistral`（`MISTRAL_API_KEY`）
- 示例模型：`mistral/mistral-large-latest`
- CLI：`openclaw onboard --auth-choice mistral-api-key`
- Groq：`groq`（`GROQ_API_KEY`）
- Cerebras：`cerebras`（`CEREBRAS_API_KEY`）
  - Cerebras 上的 GLM 模型使用 ID `zai-glm-4.7` 和 `zai-glm-4.6`。
  - OpenAI 兼容的基础 URL：`https://api.cerebras.ai/v1`。
- GitHub Copilot：`github-copilot`（`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`）
- Hugging Face Inference：`huggingface`（`HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN`）—— OpenAI 兼容路由；示例模型：`huggingface/deepseek-ai/DeepSeek-R1`；CLI：`openclaw onboard --auth-choice huggingface-api-key`。详见 [Hugging Face（Inference）](/providers/huggingface)。

## 通过 `models.providers`（自定义/基础 URL）添加的提供商

使用 `models.providers`（或 `models.json`）可添加 **自定义** 提供商或 OpenAI/Anthropic 兼容代理。

### Moonshot AI（Kimi）

Moonshot 使用 OpenAI 兼容端点，因此需将其配置为自定义提供商：

- 提供商：`moonshot`
- 认证：`MOONSHOT_API_KEY`
- 示例模型：`moonshot/kimi-k2.5`

Kimi K2 模型 ID：

<!-- markdownlint-disable MD037 -->

{/_ moonshot-kimi-k2-model-refs:start _/ && null}

<!-- markdownlint-enable MD037 -->

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-0905-preview`
- `moonshot/kimi-k2-turbo-preview`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
  <!-- markdownlint-disable MD037 -->
  {/_ moonshot-kimi-k2-model-refs:end _/ && null}
  <!-- markdownlint-enable MD037 -->

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

- 提供商：`kimi-coding`
- 认证：`KIMI_API_KEY`
- 示例模型：`kimi-coding/k2p5`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi-coding/k2p5" } },
  },
}
```

### Qwen OAuth（免费层）

Qwen 通过设备码流程提供对 Qwen Coder + Vision 的 OAuth 访问权限。启用捆绑插件后登录：

```bash
openclaw plugins enable qwen-portal-auth
openclaw models auth login --provider qwen-portal --set-default
```

模型引用：

- `qwen-portal/coder-model`
- `qwen-portal/vision-model`

设置详情及注意事项请参阅 [/providers/qwen](/providers/qwen)。

### Volcano Engine（Doubao）

Volcano Engine（火山引擎）提供对中国境内 Doubao 及其他模型的访问支持。

- 提供商：`volcengine`（编程用途：`volcengine-plan`）
- 认证：`VOLCANO_ENGINE_API_KEY`
- 示例模型：`volcengine/doubao-seed-1-8-251228`
- CLI：`openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine/doubao-seed-1-8-251228" } },
  },
}
```

可用模型：

- `volcengine/doubao-seed-1-8-251228`（Doubao Seed 1.8）
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127`（Kimi K2.5）
- `volcengine/glm-4-7-251222`（GLM 4.7）
- `volcengine/deepseek-v3-2-251201`（DeepSeek V3.2 128K）

编程模型（`volcengine-plan`）：

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus（国际版）

BytePlus ARK 为国际用户提供与火山引擎（Volcano Engine）相同的模型访问能力。

- 提供商：`byteplus`（编码：`byteplus-plan`）
- 认证方式：`BYTEPLUS_API_KEY`
- 示例模型：`byteplus/seed-1-8-251228`
- CLI：`openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus/seed-1-8-251228" } },
  },
}
```

可用模型：

- `byteplus/seed-1-8-251228`（Seed 1.8）
- `byteplus/kimi-k2-5-260127`（Kimi K2.5）
- `byteplus/glm-4-7-251222`（GLM 4.7）

代码模型（`byteplus-plan`）：

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic 在 `synthetic` 提供商后提供与 Anthropic 兼容的模型：

- 提供商：`synthetic`
- 认证方式：`SYNTHETIC_API_KEY`
- 示例模型：`synthetic/hf:MiniMaxAI/MiniMax-M2.5`
- CLI：`openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.5", name: "MiniMax M2.5" }],
      },
    },
  },
}
```

### MiniMax

MiniMax 通过 `models.providers` 进行配置，因其使用自定义端点：

- MiniMax（Anthropic 兼容）：`--auth-choice minimax-api`
- 认证方式：`MINIMAX_API_KEY`

详见 [/providers/minimax](/providers/minimax)，了解配置步骤、模型选项及配置片段。

### Ollama

Ollama 是一个本地大语言模型（LLM）运行时环境，提供与 OpenAI 兼容的 API：

- 提供商：`ollama`
- 认证方式：无需认证（本地服务器）
- 示例模型：`ollama/llama3.3`
- 安装地址：[https://ollama.ai](https://ollama.ai)

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

当 Ollama 在本地以 `http://127.0.0.1:11434/v1` 运行时，系统将自动检测。详见 [/providers/ollama](/providers/ollama)，获取模型推荐及自定义配置说明。

### vLLM

vLLM 是一个本地（或自托管）的、与 OpenAI 兼容的服务端：

- 提供商：`vllm`
- 认证方式：可选（取决于您的服务端配置）
- 默认基础 URL：`http://127.0.0.1:8000/v1`

如需启用本地自动发现功能（若您的服务端未强制要求认证，任意值均可）：

```bash
export VLLM_API_KEY="vllm-local"
```

然后指定一个模型（请替换为 `/v1/models` 返回的模型 ID 之一）：

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

详见 [/providers/vllm](/providers/vllm) 获取详细信息。

### 本地代理（LM Studio、vLLM、LiteLLM 等）

示例（OpenAI 兼容）：

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/minimax-m2.5-gs32" },
      models: { "lmstudio/minimax-m2.5-gs32": { alias: "Minimax" } },
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
            id: "minimax-m2.5-gs32",
            name: "MiniMax M2.5",
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

注意事项：

- 对于自定义提供商，`reasoning`、`input`、`cost`、`contextWindow` 和 `maxTokens` 均为可选项。  
  若省略，OpenClaw 将默认采用以下值：
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- 建议：显式设置与您的代理/模型限制相匹配的具体值。
- 对于非原生端点上的 `api: "openai-completions"`（即任何非空的 `baseUrl`，且其主机名不为 `api.openai.com`），OpenClaw 将强制设为 `compat.supportsDeveloperRole: false`，以避免因不支持的 `developer` 角色而导致提供商返回 400 错误。
- 若 `baseUrl` 为空或被省略，OpenClaw 将保持默认的 OpenAI 行为（该行为解析为 `api.openai.com`）。
- 出于安全性考虑，在非原生 `openai-completions` 端点上，即使显式设置了 `compat.supportsDeveloperRole: true`，仍将被覆盖。

## CLI 示例

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

另请参阅：[/gateway/configuration](/gateway/configuration)，查看完整配置示例。