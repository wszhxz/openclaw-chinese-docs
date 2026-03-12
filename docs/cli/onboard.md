---
summary: "CLI reference for `openclaw onboard` (interactive onboarding wizard)"
read_when:
  - You want guided setup for gateway, workspace, auth, channels, and skills
title: "onboard"
---
# `openclaw onboard`

交互式入门向导（本地或远程网关配置）。

## 相关指南

- CLI 入门中心：[入门向导（CLI）](/start/wizard)  
- 入门概述：[入门概述](/start/onboarding-overview)  
- CLI 入门参考：[CLI 入门参考](/start/wizard-cli-reference)  
- CLI 自动化：[CLI 自动化](/start/wizard-cli-automation)  
- macOS 入门：[入门（macOS 应用）](/start/onboarding)

## 示例

```bash
openclaw onboard
openclaw onboard --flow quickstart
openclaw onboard --flow manual
openclaw onboard --mode remote --remote-url wss://gateway-host:18789
```

对于明文私有网络 `ws://` 目标（仅限受信任网络），在入门流程环境中设置  
`OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`。

非交互式自定义提供程序：

```bash
openclaw onboard --non-interactive \
  --auth-choice custom-api-key \
  --custom-base-url "https://llm.example.com/v1" \
  --custom-model-id "foo-large" \
  --custom-api-key "$CUSTOM_API_KEY" \
  --secret-input-mode plaintext \
  --custom-compatibility openai
```

在非交互模式下，`--custom-api-key` 是可选的。若省略，入门流程将检查 `CUSTOM_API_KEY`。

将提供程序密钥以引用方式存储，而非明文：

```bash
openclaw onboard --non-interactive \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

启用 `--secret-input-mode ref` 后，入门流程将写入环境支持的引用（env-backed refs），而非明文密钥值。  
对于基于认证配置文件（auth-profile）的提供程序，这会写入 `keyRef` 条目；对于自定义提供程序，则会将 `models.providers.<id>.apiKey` 作为环境引用（env ref）写入（例如 `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`）。

非交互式 `ref` 模式的约定：

- 在入门流程环境中设置提供程序环境变量（例如 `OPENAI_API_KEY`）。  
- 不要传递内联密钥标志（例如 `--openai-api-key`），除非该环境变量也已设置。  
- 若传递了内联密钥标志但未设置对应必需的环境变量，入门流程将快速失败，并提供操作指引。

非交互模式下的网关令牌选项：

- `--gateway-auth token --gateway-token <token>` 存储明文令牌。  
- `--gateway-auth token --gateway-token-ref-env <name>` 将 `gateway.auth.token` 存储为环境 SecretRef。  
- `--gateway-token` 和 `--gateway-token-ref-env` 互斥。  
- `--gateway-token-ref-env` 要求入门流程环境中存在非空的环境变量。  
- 启用 `--install-daemon` 后，当令牌认证需要令牌时，SecretRef 管理的网关令牌将被验证，但不会以解析后的明文形式持久化到 supervisor 服务环境元数据中。  
- 启用 `--install-daemon` 后，若令牌模式需要令牌而所配置的令牌 SecretRef 未解析，入门流程将严格失败，并提供修复指引。  
- 启用 `--install-daemon` 后，若同时配置了 `gateway.auth.token` 和 `gateway.auth.password`，且 `gateway.auth.mode` 未设置，入门流程将阻塞安装，直至显式设置模式。

示例：

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN \
  --accept-risk
```

引用模式下的交互式入门行为：

- 提示时选择 **使用密钥引用（Use secret reference）**。  
- 然后选择以下任一方式：  
  - 环境变量  
  - 已配置的密钥提供程序（`file` 或 `exec`）  
- 入门流程将在保存引用前执行快速预检验证。  
  - 若验证失败，入门流程将显示错误并允许您重试。

非交互式 Z.AI 端点选择：

注意：`--auth-choice zai-api-key` 现在可自动检测最适合您密钥的 Z.AI 端点（优先选择通用 API，即 `zai/glm-5`）。  
若您明确希望使用 GLM 编码计划（GLM Coding Plan）端点，请选择 `zai-coding-global` 或 `zai-coding-cn`。

```bash
# Promptless endpoint selection
openclaw onboard --non-interactive \
  --auth-choice zai-coding-global \
  --zai-api-key "$ZAI_API_KEY"

# Other Z.AI endpoint choices:
# --auth-choice zai-coding-cn
# --auth-choice zai-global
# --auth-choice zai-cn
```

非交互式 Mistral 示例：

```bash
openclaw onboard --non-interactive \
  --auth-choice mistral-api-key \
  --mistral-api-key "$MISTRAL_API_KEY"
```

流程说明：

- `quickstart`：最小化提示，自动为网关生成令牌。  
- `manual`：完整提示（端口/绑定/认证），等同于 `advanced` 的别名。  
- 本地入门 DM 作用域行为：[CLI 入门参考](/start/wizard-cli-reference#outputs-and-internals)。  
- 首次聊天最快方式：`openclaw dashboard`（控制 UI，无需通道设置）。  
- 自定义提供程序：连接任意兼容 OpenAI 或 Anthropic 的端点，包括未列出的托管服务。使用 Unknown 可自动检测。

## 常见后续命令

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
__CODE_BLOCK_41__ does not imply non-interactive mode. Use __CODE_BLOCK_42__ for scripts.
</Note>