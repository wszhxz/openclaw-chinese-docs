---
summary: "Hugging Face Inference setup (auth + model selection)"
read_when:
  - You want to use Hugging Face Inference with OpenClaw
  - You need the HF token env var or CLI auth choice
title: "Hugging Face (Inference)"
---
# Hugging Face（推理）

[Hugging Face 推理服务提供商](https://huggingface.co/docs/inference-providers) 通过一个统一的路由 API 提供与 OpenAI 兼容的聊天补全功能。您只需一个令牌，即可访问多种模型（如 DeepSeek、Llama 等）。OpenClaw 使用 **与 OpenAI 兼容的端点**（仅限聊天补全）；如需文本生成图像、嵌入向量或语音功能，请直接使用 [HF 推理客户端](https://huggingface.co/docs/api-inference/quicktour)。

- 服务提供商：`huggingface`  
- 认证方式：`HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN`（具备 **调用推理服务提供商** 权限的细粒度令牌）  
- API：与 OpenAI 兼容（`https://router.huggingface.co/v1`）  
- 计费方式：单个 HF 令牌；[定价](https://huggingface.co/docs/inference-providers/pricing) 遵循各提供商费率，并提供免费额度。

## 快速开始

1. 在 [Hugging Face → 设置 → 令牌](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained) 页面创建一个具备 **调用推理服务提供商** 权限的细粒度令牌。  
2. 运行初始化流程，在提供商下拉菜单中选择 **Hugging Face**，然后按提示输入您的 API 密钥：

```bash
openclaw onboard --auth-choice huggingface-api-key
```

3. 在 **默认 Hugging Face 模型** 下拉菜单中，选择您希望使用的模型（当您拥有有效令牌时，该列表将从推理 API 动态加载；否则显示内置列表）。您的选择将被保存为默认模型。  
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

此操作将把 `huggingface/deepseek-ai/DeepSeek-R1` 设为默认模型。

## 环境说明

如果 Gateway 以守护进程方式运行（launchd/systemd），请确保 `HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN` 对该进程可用（例如，置于 `~/.openclaw/.env` 中，或通过 `env.shellEnv` 设置）。

## 模型发现与初始化下拉菜单

OpenClaw 通过**直接调用推理端点**来发现模型：

```bash
GET https://router.huggingface.co/v1/models
```

（可选：发送 `Authorization: Bearer $HUGGINGFACE_HUB_TOKEN` 或 `$HF_TOKEN` 获取完整模型列表；部分端点在未认证时仅返回子集。）响应格式为 OpenAI 风格的 `{ "object": "list", "data": [ { "id": "Qwen/Qwen3-8B", "owned_by": "Qwen", ... }, ... ] }`。

当您通过初始化流程、`HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN` 配置 Hugging Face API 密钥后，OpenClaw 将使用该 GET 请求发现可用的聊天补全模型。在 **交互式初始化流程** 中，您输入令牌后，将看到一个由该列表填充的 **默认 Hugging Face 模型** 下拉菜单（若请求失败，则显示内置目录）。在运行时（例如 Gateway 启动时），若已配置密钥，OpenClaw 将再次调用 **GET** `https://router.huggingface.co/v1/models` 刷新目录。该列表将与内置目录合并（用于补充上下文窗口大小、成本等元数据）。若请求失败或未设置密钥，则仅使用内置目录。

## 模型名称与可编辑选项

- **API 返回的名称**：模型显示名称在 API 返回 `name`、`title` 或 `display_name` 时，**由 GET /v1/models 响应动态填充**；否则从模型 ID 推导得出（例如 `deepseek-ai/DeepSeek-R1` → “DeepSeek R1”）。  
- **覆盖显示名称**：您可在配置中为每个模型设置自定义标签，使其在 CLI 和 UI 中按您期望的方式显示：

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

- **提供商 / 策略选择**：在 **模型 ID 后添加后缀**，以指定路由器如何选择后端：  
  - **`:fastest`** —— 最高吞吐量（由路由器自动选择；提供商选择被**锁定**——不显示交互式后端选择器）。  
  - **`:cheapest`** —— 每输出 token 成本最低（由路由器自动选择；提供商选择被**锁定**）。  
  - **`:provider`** —— 强制指定特定后端（例如 `:sambanova`、`:together`）。  

  当您在初始化模型下拉菜单中选择 **:cheapest** 或 **:fastest**（例如）时，提供商即被锁定：路由器将依据成本或速度决策，且不会显示可选的“偏好特定后端”步骤。您可将这些后缀作为独立条目添加至 `models.providers.huggingface.models`，或在 `model.primary` 中直接设置带后缀的模型 ID。您也可在 [推理服务提供商设置](https://hf.co/settings/inference-providers) 中设定默认顺序（无后缀 = 按该顺序使用）。

- **配置合并规则**：合并配置时，`models.providers.huggingface.models` 中已存在的条目（例如 `models.json` 中的条目）将被保留。因此，您在此处设置的任何自定义 `name`、`alias` 或模型选项均会被保留。

## 模型 ID 与配置示例

模型引用采用 `huggingface/<org>/<model>` 格式（Hub 风格 ID）。以下列表来自 **GET** `https://router.huggingface.co/v1/models`；您的目录可能包含更多模型。

**推理端点返回的示例 ID：**

| 模型                      | 引用（前缀为 `huggingface/`）    |
| ------------------------- | ----------------------------------- |
| DeepSeek R1               | `deepseek-ai/DeepSeek-R1`           |
| DeepSeek V3.2             | `deepseek-ai/DeepSeek-V3.2`         |
| Qwen3 8B                  | `Qwen/Qwen3-8B`                     |
| Qwen2.5 7B Instruct       | `Qwen/Qwen2.5-7B-Instruct`          |
| Qwen3 32B                 | `Qwen/Qwen3-32B`                    |
| Llama 3.3 70B Instruct    | `meta-llama/Llama-3.3-70B-Instruct` |
| Llama 3.1 8B Instruct     | `meta-llama/Llama-3.1-8B-Instruct`  |
| GPT-OSS 120B              | `openai/gpt-oss-120b`               |
| GLM 4.7                   | `zai-org/GLM-4.7`                   |
| Kimi K2.5                 | `moonshotai/Kimi-K2.5`              |

您可在模型 ID 后追加 `:fastest`、`:cheapest` 或 `:provider`（例如 `:together`、`:sambanova`）。您可在 [推理服务提供商设置](https://hf.co/settings/inference-providers) 中设定默认顺序；详见 [推理服务提供商文档](https://huggingface.co/docs/inference-providers) 及 **GET** `https://router.huggingface.co/v1/models` 获取完整列表。

### 完整配置示例

**主用 DeepSeek R1，Qwen 作为备用：**

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

**以 Qwen 为默认模型，并提供 :cheapest 和 :fastest 变体：**

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

**DeepSeek + Llama + GPT-OSS 并配置别名：**

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

**使用 :provider: 强制指定特定后端：**

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

**多个 Qwen 和 DeepSeek 模型并附加策略后缀：**

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