---
summary: "Model provider overview with example configs + CLI flows"
read_when:
  - You need a provider-by-provider model setup reference
  - You want example configs or CLI onboarding commands for model providers
title: "Model Providers"
---
# 模型提供者

本页面涵盖 **LLM/模型提供者**（不包括聊天渠道如 WhatsApp/Telegram）。
模型选择规则详见 [/concepts/models](/concepts/models)。

## 快速规则

- 模型引用使用 `provider/model`（示例：`opencode/claude-opus-4-5`）。
- 如果设置了 `agents.defaults.models`，它将成为允许列表。
- CLI 工具：`openclaw onboard`、`openclaw models list`、`openclaw models set <provider/model>`。

## 内置提供者 (pi-ai 目录)

OpenClaw 预装了 pi-ai 目录。这些提供者无需 `models.providers` 配置；只需设置认证并选择模型。

### OpenAI

- 提供者：`openai`
- 认证：`OPENAI_API_KEY`
- 示例模型：`openai/gpt-5.2`
- CLI：`openclaw onboard --auth-choice openai-api-key`

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.2" } } },
}
```

### Anthropic

- 提供者：`anthropic`
- 认证：`ANTHROPIC_API_KEY` 或 `claude setup-token`
- 示例模型：`anthropic/claude-opus-4-5`
- CLI：`openclaw onboard --auth-choice token`（粘贴 setup-token）或 `openclaw models auth paste-token --provider anthropic`

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-5" } } },
}
```

### OpenAI Code (Codex)

- 提供者：`openai-codex`
- 认证：OAuth（ChatGPT）
- 示例模型：`openai-codex/gpt-5.2`
- CLI：`openclaw onboard --auth-choice openai-codex` 或 `openclaw models auth login --provider openai-codex`

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.2" } } },
}
```

### OpenCode Zen

- 提供者：`opencode`
- 认证：`OPENCODE_API_KEY`（或 `OPENCODE_ZEN_API_KEY`）
- 示例模型：`opencode/claude-opus-4-5`
- CLI：`openclaw onboard --auth-choice opencode-zen`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-5" } } },
}
```

### Google Gemini（API 密钥）

- 提供者：`google`
- 认证：`GEMINI_API_KEY`
- 示例模型：`google/gemini-3-pro-preview`
- CLI：`openclaw onboard --auth-choice gemini-api-key`

### Google Vertex、Antigravity 和 Gemini CLI

- 提供者：`google-vertex`、`google-antigravity`、`google-gemini-cli`
- 认证：Vertex 使用 gcloud ADC；Antigravity/Gemini CLI 使用各自的认证流程
- Antigravity OAuth 作为捆绑插件提供（`google-antigravity-auth`，默认禁用）。
  - 启用：`openclaw plugins enable google-antigravity-auth`
  - 登录：`openclaw models auth login --provider google-antigravity --set-default`
- Gemini CLI OAuth 作为捆绑插件提供（`google-gemini-cli-auth`，默认禁用）。
  - 启用：`openclaw plugins enable google-gemini-cli-auth`
  - 登录：`openclaw models auth login --provider google-gemini-cli --set-default`
  - 注意：您**不需要**将客户端 ID 或密钥粘贴到 `openclaw.json` 中。CLI 登录流程会将令牌存储在网关主机的认证配置文件中。

### Z.AI（GLM）

- 提供者：`zai`
- 认证：`ZAI_API_KEY`
- 示例模型：`zai/glm-130b`
- CLI：`openclaw onboard --auth-choice zai`

### Z.AI（GLM）

- 提供者：`zai`
- 认证：`ZAI_API_KEY`
- 示例模型：`zai/glm-130b`
- CLI：`openclaw onboard --auth-choice zai`

### Google Gemini（API 密钥）

- 提供者：`google`
- 认证：`GEMINI_API_KEY`
- 示例模型：`google/gemini-3-pro-preview`
- CLI：`openclaw onboard --auth-choice gemini-api-key`

### Google Vertex、Antigravity 和 Gemini CLI

- 提供者：`google-vertex`、`google-antigravity`、`google-gemini-cli`
- 认证：Vertex 使用 gcloud ADC；Antigravity/Gemini CLI 使用各自的认证流程
- Antigravity OAuth 作为捆绑插件提供（`google-antigravity-auth`，默认禁用）。
  - 启用：`openclab plugins enable google-antigravity-auth`
  - 登录：`openclab models auth login --provider google-antigravity --set-default`
- Gemini CLI OAuth 作为捆绑插件提供（`google-gemini-cli-auth`，默认禁用）。
  - 启用：`openclab plugins enable google-gemini-cli-auth`
  - 登录：`openclab models auth login --provider google-gemini-cli --set-default`
  - 注意：您**不需要**将客户端 ID 或密钥粘贴到 `openclab.json` 中。CLI 登录流程会将令牌存储在网关主机的认证配置文件中。

### Z.AI（GLM）

- 提供者：`zai`
- 认证：`ZAI_API_KEY`
- 示例模型：`zai/glm-130b`
- CLI：`openclab onboard --auth-choice zai`

### Google Gemini（API 密钥）

- 提供者：`google`
- 认证：`GEMINI_API_KEY`
- 示例模型：`google/gemini-3-pro-preview`
- CLI：`openclab onboard --auth-choice gemini-api-key`

### Google Vertex、Antigravity 和 Gemini CLI

- 提供者：`google-vertex`、`google-antigravity`、`google-gemini-cli`
-