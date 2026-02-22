---
summary: "CLI reference for `openclaw onboard` (interactive onboarding wizard)"
read_when:
  - You want guided setup for gateway, workspace, auth, channels, and skills
title: "onboard"
---
# `openclaw onboard`

交互式引导向导（本地或远程网关设置）。

## 相关指南

- CLI 引导中心：[引导向导 (CLI)](/start/wizard)
- 引导概述：[引导概述](/start/onboarding-overview)
- CLI 引导参考：[CLI 引导参考](/start/wizard-cli-reference)
- CLI 自动化：[CLI 自动化](/start/wizard-cli-automation)
- macOS 引导：[引导 (macOS 应用)](/start/onboarding)

## 示例

```bash
openclaw onboard
openclaw onboard --flow quickstart
openclaw onboard --flow manual
openclaw onboard --mode remote --remote-url ws://gateway-host:18789
```

非交互式自定义提供商：

```bash
openclaw onboard --non-interactive \
  --auth-choice custom-api-key \
  --custom-base-url "https://llm.example.com/v1" \
  --custom-model-id "foo-large" \
  --custom-api-key "$CUSTOM_API_KEY" \
  --custom-compatibility openai
```

`--custom-api-key` 在非交互模式下是可选的。如果省略，则引导检查 `CUSTOM_API_KEY`。

非交互式 Z.AI 终端选择：

注意：`--auth-choice zai-api-key` 现在会自动检测最适合您密钥的 Z.AI 终端（优先使用带有 `zai/glm-5` 的通用 API）。
如果您特别想要 GLM 编码计划终端，请选择 `zai-coding-global` 或 `zai-coding-cn`。

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

流程说明：

- `quickstart`：最少提示，自动生成网关令牌。
- `manual`：端口/绑定/身份验证的完整提示（`advanced` 的别名）。
- 最快首次聊天：`openclaw dashboard`（控制界面，无需频道设置）。
- 自定义提供商：连接任何与 OpenAI 或 Anthropic 兼容的终端，
  包括未列出的托管提供商。使用 Unknown 进行自动检测。

## 常见后续命令

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
__CODE_BLOCK_15__ does not imply non-interactive mode. Use __CODE_BLOCK_16__ for scripts.
</Note>