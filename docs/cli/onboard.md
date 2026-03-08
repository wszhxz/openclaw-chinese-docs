---
summary: "CLI reference for `openclaw onboard` (interactive onboarding wizard)"
read_when:
  - You want guided setup for gateway, workspace, auth, channels, and skills
title: "onboard"
---
# `openclaw onboard`

交互式入门向导（本地或远程网关设置）。

## 相关指南

- CLI 入门中心：[入门向导 (CLI)](/start/wizard)
- 入门概览：[入门概览](/start/onboarding-overview)
- CLI 入门参考：[CLI 入门参考](/start/wizard-cli-reference)
- CLI 自动化：[CLI 自动化](/start/wizard-cli-automation)
- macOS 入门：[入门 (macOS 应用)](/start/onboarding)

## 示例

```bash
openclaw onboard
openclaw onboard --flow quickstart
openclaw onboard --flow manual
openclaw onboard --mode remote --remote-url wss://gateway-host:18789
```

对于明文私有网络 ``ws://`` 目标（仅限受信任网络），在入门流程环境中设置 ``OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1``。

非交互式自定义提供者：

```bash
openclaw onboard --non-interactive \
  --auth-choice custom-api-key \
  --custom-base-url "https://llm.example.com/v1" \
  --custom-model-id "foo-large" \
  --custom-api-key "$CUSTOM_API_KEY" \
  --secret-input-mode plaintext \
  --custom-compatibility openai
```

``--custom-api-key`` 在非交互模式下是可选的。如果省略，入门检查 ``CUSTOM_API_KEY``。

将提供者密钥存储为引用而非明文：

```bash
openclaw onboard --non-interactive \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

使用 ``--secret-input-mode ref``，入门将写入基于 env 的引用，而不是明文密钥值。
对于由 auth-profile 支持的提供者，这将写入 ``keyRef`` 条目；对于自定义提供者，这将把 ``models.providers.<id>.apiKey`` 作为 env 引用写入（例如 ``{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }``）。

非交互式 ``ref`` 模式契约：

- 在入门流程环境中设置提供者环境变量（例如 ``OPENAI_API_KEY``）。
- 除非也设置了该环境变量，否则不要传递内联密钥标志（例如 ``--openai-api-key``）。
- 如果在不设置所需环境变量的情况下传递了内联密钥标志，入门将快速失败并提供指导。

非交互模式下的网关令牌选项：

- ``--gateway-auth token --gateway-token <token>`` 存储明文令牌。
- ``--gateway-auth token --gateway-token-ref-env <name>`` 将 ``gateway.auth.token`` 存储为 env SecretRef。
- ``--gateway-token`` 和 ``--gateway-token-ref-env`` 互斥。
- ``--gateway-token-ref-env`` 需要在入门流程环境中设置非空环境变量。
- 使用 ``--install-daemon`` 时，当令牌认证需要令牌时，SecretRef 管理的网关令牌会被验证，但不会作为解析后的明文持久化到主管服务环境元数据中。
- 使用 ``--install-daemon`` 时，如果令牌模式需要令牌且配置的令牌 SecretRef 未解析，入门将关闭并失败，同时提供修复指导。
- 使用 ``--install-daemon`` 时，如果同时配置了 ``gateway.auth.token`` 和 ``gateway.auth.password`` 且 ``gateway.auth.mode`` 未设置，入门将阻止安装，直到明确设置模式。

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

带有引用模式的交互式入门行为：

- 提示时选择 **使用秘密引用**。
- 然后选择以下任一：
  - 环境变量
  - 配置的密钥提供者 (``file`` 或 ``exec``)
- 入门在保存引用之前会执行快速预检验证。
  - 如果验证失败，入门会显示错误并允许您重试。

非交互式 Z.AI 端点选择：

注意：``--auth-choice zai-api-key`` 现在会自动检测适合您密钥的最佳 Z.AI 端点（首选带有 ``zai/glm-5`` 的一般 API）。
如果您特别想要 GLM Coding Plan 端点，请选择 ``zai-coding-global`` 或 ``zai-coding-cn``。

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

- ``quickstart``：最小提示，自动生成网关令牌。
- ``manual``：端口/绑定/认证的完整提示（``advanced`` 的别名）。
- 本地入门 DM 范围行为：[CLI 入门参考](/start/wizard-cli-reference#outputs-and-internals)。
- 最快优先聊天：``openclaw dashboard``（控制 UI，无需通道设置）。
- 自定义提供者：连接任何兼容 OpenAI 或 Anthropic 的端点，包括未列出的托管提供者。使用 Unknown 进行自动检测。

## 常见后续命令

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
__CODE_BLOCK_41__ does not imply non-interactive mode. Use __CODE_BLOCK_42__ for scripts.
</Note>