---
summary: "Hugging Face Inference setup (auth + model selection)"
read_when:
  - You want to use Hugging Face Inference with OpenClaw
  - You need the HF token env var or CLI auth choice
title: "Hugging Face (Inference)"
---
# Hugging Face (推理)

[Hugging Face 推理提供商](https://huggingface.co/docs/inference-providers)通过单一路由器API提供与OpenAI兼容的聊天补全功能。您可以通过一个令牌访问许多模型（DeepSeek, Llama等）。OpenClaw使用**与OpenAI兼容的端点**（仅限聊天补全）；对于文本到图像、嵌入或语音，请直接使用[HF推理客户端](https://huggingface.co/docs/api-inference/quicktour)。

- 提供商: `huggingface`
- 认证: `HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN`（具有**调用推理提供商**权限的细粒度令牌）
- API: 与OpenAI兼容 (`https://router.huggingface.co/v1`)
- 计费: 单个HF令牌；[定价](https://huggingface.co/docs/inference-providers/pricing)遵循提供商费率并包含免费层级。

## 快速入门

1. 在[Hugging Face → 设置 → 令牌](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained)创建一个具有**调用推理提供商**权限的细粒度令牌。
2. 运行入职流程并在提供商下拉菜单中选择**Hugging Face**，然后在提示时输入您的API密钥：

```bash
openclaw onboard --auth-choice huggingface-api-key
```

3. 在**默认Hugging Face模型**下拉菜单中选择您想要的模型（当您有一个有效的令牌时，列表从推理API加载；否则显示内置列表）。您的选择将作为默认模型保存。
4. 您也可以稍后在配置中设置或更改默认模型：

```json5
{
  agents: {
    defaults: {
      model: { primary: "huggingface/deepseek-ai/DeepSeek-R1" },
    },
  },
}
```

## 非交互式示例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice huggingface-api-key \
  --huggingface-api-key "$HF_TOKEN"
```

这将设置 `huggingface/deepseek-ai/DeepSeek-R1` 为默认模型。

## 环境说明

如果网关作为守护进程运行（launchd/systemd），请确保 `HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN`
对该进程可用（例如，在 `~/.openclaw/.env` 中或通过
`env.shellEnv`）。

## 模型发现和入职下拉菜单

OpenClaw通过直接调用**推理端点**来发现模型：

```bash
GET https://router.huggingface.co/v1/models
```

（可选：发送 `Authorization: Bearer $HUGGINGFACE_HUB_TOKEN` 或 `$HF_TOKEN` 获取完整列表；某些端点在未经身份验证的情况下返回子集。）响应是OpenAI风格的 `{ "object": "list", "data": [ { "id": "Qwen/Qwen3-8B", "owned_by": "Qwen", ... }, ... ] }`。

当您配置Hugging Face API密钥（通过入职、`HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN`），OpenClaw使用此GET请求发现可用的聊天补全模型。在**交互式入职**过程中，输入令牌后，您会看到一个从该列表填充的**默认Hugging Face模型**下拉菜单（如果请求失败，则显示内置目录）。在运行时（例如网关启动时），当存在密钥时，OpenClaw再次调用**GET** `https://router.huggingface.co/v1/models` 刷新目录。该列表与内置目录合并（用于上下文窗口和成本等元数据）。如果请求失败或未设置密钥，则仅使用内置目录。

## 模型名称和可编辑选项

- **API中的名称:** 当API返回 `name`, `title`, 或 `display_name` 时，模型显示名称从 **GET /v1/models** 加载；否则，它从模型ID派生（例如 `deepseek-ai/DeepSeek-R1` → “DeepSeek R1”）。
- **覆盖显示名称:** 您可以在配置中为每个模型设置自定义标签，以便在CLI和UI中按您希望的方式显示：

```json5
{
  agents: {
    defaults: {
      models: {
        "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1 (fast)" },
        "huggingface/deepseek-ai/DeepSeek-R1:cheapest": { alias: "DeepSeek R1 (cheap)" },
      },
    },
  },
}
```

- **提供商/策略选择:** 向**模型ID**附加后缀以选择路由器如何选择后端：
  - **`:fastest`** — 最高吞吐量（路由器选择；提供商选择**锁定** — 无交互式后端选择器）。
  - **`:cheapest`** — 每个输出令牌最低成本（路由器选择；提供商选择**锁定**）。
  - **`:provider`** — 强制特定后端（例如 `:sambanova`, `:together`）。

  当您选择 **:cheapest** 或 **:fastest**（例如，在入职模型下拉菜单中），提供商被锁定：路由器根据成本或速度进行选择，并不显示可选的“首选特定后端”步骤。您可以在 `models.providers.huggingface.models` 中添加这些作为单独条目或使用带有后缀的 `model.primary`。您还可以在[推理提供商设置](https://hf.co/settings/inference-providers)中设置默认顺序（无后缀 = 使用该顺序）。

- **配置合并:** 当配置合并时，`models.providers.huggingface.models` 中的现有条目（例如在 `models.json` 中）将被保留。因此，您在那里设置的任何自定义 `name`, `alias` 或模型选项都将被保留。

## 模型ID和配置示例

模型引用使用形式 `huggingface/<org>/<model>`（Hub样式ID）。下面的列表来自 **GET** `https://router.huggingface.co/v1/models`；您的目录可能包含更多。

**示例ID（来自推理端点）:**

| 模型                  | 引用（前缀为 `huggingface/`）    |
| ---------------------- | ----------------------------------- |
| DeepSeek R1            | `deepseek-ai/DeepSeek-R1`           |
| DeepSeek V3.2          | `deepseek-ai/DeepSeek-V3.2`         |
| Qwen3 8B               | `Qwen/Qwen3-8B`                     |
| Qwen2.5 7B Instruct    | `Qwen/Qwen2.5-7B-Instruct`          |
| Qwen3 32B              | `Qwen/Qwen3-32B`                    |
| Llama 3.3 70B Instruct | `meta-llama/Llama-3.3-70B-Instruct` |
| Llama 3.1 8B Instruct  | `meta-llama/Llama-3.1-8B-Instruct`  |
| GPT-OSS 120B           | `openai/gpt-oss-120b`               |
| GLM 4.7                | `zai-org/GLM-4.7`                   |
| Kimi K2.5              | `moonshotai/Kimi-K2.5`              |

您可以向模型ID附加 `:fastest`, `:cheapest`, 或 `:provider`（例如 `:together`, `:sambanova`）。在[推理提供商设置](https://hf.co/settings/inference-providers)中设置默认顺序；参阅[推理提供商](https://huggingface.co/docs/inference-providers)和 **GET** `https://router.huggingface.co/v1/models` 获取完整列表。

### 完整配置示例

**主要DeepSeek R1，Qwen备用:**

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "huggingface/deepseek-ai/DeepSeek-R1",
        fallbacks: ["huggingface/Qwen/Qwen3-8B"],
      },
      models: {
        "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1" },
        "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
      },
    },
  },
}
```

**Qwen作为默认，带有 :cheapest 和 :fastest 变体:**

```json5
{
  agents: {
    defaults: {
      model: { primary: "huggingface/Qwen/Qwen3-8B" },
      models: {
        "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
        "huggingface/Qwen/Qwen3-8B:cheapest": { alias: "Qwen3 8B (cheapest)" },
        "huggingface/Qwen/Qwen3-8B:fastest": { alias: "Qwen3 8B (fastest)" },
      },
    },
  },
}
```

**DeepSeek + Llama + GPT-OSS 带有别名:**

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "huggingface/deepseek-ai/DeepSeek-V3.2",
        fallbacks: [
          "huggingface/meta-llama/Llama-3.3-70B-Instruct",
          "huggingface/openai/gpt-oss-120b",
        ],
      },
      models: {
        "huggingface/deepseek-ai/DeepSeek-V3.2": { alias: "DeepSeek V3.2" },
        "huggingface/meta-llama/Llama-3.3-70B-Instruct": { alias: "Llama 3.3 70B" },
        "huggingface/openai/gpt-oss-120b": { alias: "GPT-OSS 120B" },
      },
    },
  },
}
```

**使用 :provider: 强制特定后端:**

```json5
{
  agents: {
    defaults: {
      model: { primary: "huggingface/deepseek-ai/DeepSeek-R1:together" },
      models: {
        "huggingface/deepseek-ai/DeepSeek-R1:together": { alias: "DeepSeek R1 (Together)" },
      },
    },
  },
}
```

**多个Qwen和DeepSeek模型带策略后缀:**

```json5
{
  agents: {
    defaults: {
      model: { primary: "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest" },
      models: {
        "huggingface/Qwen/Qwen2.5-7B-Instruct": { alias: "Qwen2.5 7B" },
        "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest": { alias: "Qwen2.5 7B (cheap)" },
        "huggingface/deepseek-ai/DeepSeek-R1:fastest": { alias: "DeepSeek R1 (fast)" },
        "huggingface/meta-llama/Llama-3.1-8B-Instruct": { alias: "Llama 3.1 8B" },
      },
    },
  },
}
```