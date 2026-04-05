---
summary: "CLI reference for `openclaw onboard` (interactive onboarding)"
read_when:
  - You want guided setup for gateway, workspace, auth, channels, and skills
title: "onboard"
---
# `openclaw onboard`

用于本地或远程 Gateway 设置的交互式接入。

## 相关指南

- CLI 接入中心：[接入 (CLI)](/start/wizard)
- 接入概览：[接入概览](/start/onboarding-overview)
- CLI 接入参考：[CLI 设置参考](/start/wizard-cli-reference)
- CLI 自动化：[CLI 自动化](/start/wizard-cli-automation)
- macOS 接入：[接入 (macOS App)](/start/onboarding)

## 示例

```bash
openclaw onboard
openclaw onboard --flow quickstart
openclaw onboard --flow manual
openclaw onboard --mode remote --remote-url wss://gateway-host:18789
```

对于明文私有网络 ``ws://`` 目标（仅限受信任网络），请在接入流程环境中设置 ``OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1``。

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

``--custom-api-key`` 在非交互模式下是可选的。如果省略，接入将检查 ``CUSTOM_API_KEY``。

非交互式 Ollama：

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --custom-base-url "http://ollama-host:11434" \
  --custom-model-id "qwen3.5:27b" \
  --accept-risk
```

``--custom-base-url`` 默认为 ``http://127.0.0.1:11434``。``--custom-model-id`` 是可选的；如果省略，接入将使用 Ollama 的建议默认值。云模型 ID 如 ``kimi-k2.5:cloud`` 也在此适用。

将提供者密钥存储为引用而非明文：

```bash
openclaw onboard --non-interactive \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

使用 ``--secret-input-mode ref``，接入将写入基于 env 的引用，而不是明文密钥值。
对于由 auth-profile 支持的提供者，这将写入 ``keyRef`` 条目；对于自定义提供者，这将把 ``models.providers.<id>.apiKey`` 作为 env 引用写入（例如 ``{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }``）。

非交互式 ``ref`` 模式约定：

- 在接入流程环境中设置提供者 env 变量（例如 ``OPENAI_API_KEY``）。
- 除非该 env 变量也已设置，否则不要传递内联密钥标志（例如 ``--openai-api-key``）。
- 如果在没有所需 env 变量的情况下传递了内联密钥标志，接入将快速失败并提供指导。

非交互模式下的 Gateway 令牌选项：

- ``--gateway-auth token --gateway-token <token>`` 存储明文令牌。
- ``--gateway-auth token --gateway-token-ref-env <name>`` 将 ``gateway.auth.token`` 存储为 env SecretRef。
- ``--gateway-token`` 和 ``--gateway-token-ref-env`` 互斥。
- ``--gateway-token-ref-env`` 需要接入流程环境中的非空 env 变量。
- 使用 ``--install-daemon`` 时，当令牌认证需要令牌时，SecretRef 管理的 Gateway 令牌会被验证，但不会作为解析后的明文持久化到 supervisor 服务环境元数据中。
- 使用 ``--install-daemon`` 时，如果令牌模式需要令牌且配置的令牌 SecretRef 未解析，接入将关闭并失败，同时提供修复指导。
- 使用 ``--install-daemon`` 时，如果同时配置了 ``gateway.auth.token`` 和 ``gateway.auth.password`` 且 ``gateway.auth.mode`` 未设置，接入将阻止安装，直到明确设置模式。
- 本地接入将 ``gateway.mode="local"`` 写入配置。如果后续配置文件缺少 ``gateway.mode``，请将其视为配置损坏或不完整的手动编辑，而不是有效的本地模式快捷方式。
- ``--allow-unconfigured`` 是一个单独的 Gateway 运行时逃生舱口。这并不意味着接入可以省略 ``gateway.mode``。

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

非交互式本地 Gateway 健康状态：

- 除非您传递 ``--skip-health``，否则接入将在成功退出前等待可访问的本地 Gateway。
- ``--install-daemon`` 首先启动受管理的 Gateway 安装路径。如果没有它，您必须已经运行了一个本地 Gateway，例如 ``openclaw gateway run``。
- 如果您仅在自动化中想要 config/workspace/bootstrap 写入，请使用 ``--skip-health``。
- 在原生 Windows 上，``--install-daemon`` 首先尝试计划任务，如果任务创建被拒绝，则回退到每个用户的启动文件夹登录项。

具有引用模式的交互式接入行为：

- 提示时选择 **使用秘密引用**。
- 然后选择以下任一选项：
  - 环境变量
  - 配置的 Secret 提供者 (``file`` 或 ``exec``)
- 接入在保存引用之前会执行快速预检验证。
  - 如果验证失败，接入将显示错误并允许您重试。

非交互式 Z.AI 端点选择：

注意：``--auth-choice zai-api-key`` 现在会自动检测适合您密钥的最佳 Z.AI 端点（首选带有 ``zai/glm-5`` 的通用 API）。
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

- ``quickstart``：最小提示，自动生成 Gateway 令牌。
- ``manual``：完整的端口/绑定/认证提示（``advanced`` 的别名）。
- 当认证选择暗示首选提供者时，接入会将默认模型和允许列表选择器预过滤到该提供者。对于 Volcengine 和 BytePlus，这也匹配编码计划变体 (``volcengine-plan/*``, ``byteplus-plan/*``)。
- 如果首选提供者过滤器尚未产生任何已加载的模型，接入将回退到未过滤的目录，而不是让选择器为空。
- 在网络搜索步骤中，某些提供者可以触发特定于提供者的后续提示：
  - **Grok** 可以提供可选的 ``x_search`` 设置，使用相同的 ``XAI_API_KEY`` 和 ``x_search`` 模型选择。
  - **Kimi** 可以询问 Moonshot API 区域 (``api.moonshot.ai`` vs ``api.moonshot.cn``) 以及默认的 Kimi 网络搜索模型。
- 本地接入 DM 范围行为：[CLI 设置参考](/start/wizard-cli-reference#outputs-and-internals)。
- 最快优先聊天：``openclaw dashboard``（控制 UI，无需频道设置）。
- 自定义提供者：连接任何 OpenAI 或 Anthropic 兼容的端点，包括未列出的托管提供者。使用 Unknown 进行自动检测。

## 常见后续命令

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
__CODE_BLOCK_62__ does not imply non-interactive mode. Use __CODE_BLOCK_63__ for scripts.
</Note>