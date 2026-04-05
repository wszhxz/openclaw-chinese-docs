---
summary: "CLI reference for `openclaw configure` (interactive configuration prompts)"
read_when:
  - You want to tweak credentials, devices, or agent defaults interactively
title: "configure"
---
# `openclaw configure`

交互式提示，用于设置凭据、设备和智能体默认值。

注意：**模型**部分现在包含针对 `agents.defaults.models` 白名单的多选功能（显示在 `/model` 和模型选择器中的内容）。

当 configure 从提供商身份验证选择开始时，default-model 和 allowlist 选择器会自动优先选择该提供商。对于成对的提供商（例如 Volcengine/BytePlus），相同的偏好也会匹配其 coding-plan 变体（`volcengine-plan/*`, `byteplus-plan/*`）。如果 preferred-provider 过滤器会产生空列表，configure 将回退到未过滤的目录，而不是显示空白选择器。

提示：不带子命令运行 `openclaw config` 会打开相同的向导。使用 `openclaw config get|set|unset` 进行非交互式编辑。

对于网页搜索，`openclaw configure --section web` 允许您选择提供商并配置其凭据。某些提供商还会显示特定于提供商的后续提示：

- **Grok** 可提供可选的 `x_search` 设置，使用相同的 `XAI_API_KEY`，并让您选择一个 `x_search` 模型。
- **Kimi** 可能会询问 Moonshot API 区域（`api.moonshot.ai` 与 `api.moonshot.cn`）以及默认的 Kimi 网页搜索模型。

相关：

- Gateway 配置参考：[配置](/gateway/configuration)
- Config CLI：[配置](/cli/config)

## 选项

- `--section <section>`：可重复的部分过滤器

可用部分：

- `workspace`
- `model`
- `web`
- `gateway`
- `daemon`
- `channels`
- `plugins`
- `skills`
- `health`

注意：

- 选择 Gateway 的运行位置总是会更新 `gateway.mode`。如果您只需要这个，可以选择“继续”而不选择其他部分。
- 面向通道的服务（Slack/Discord/Matrix/Microsoft Teams）在设置期间会提示输入通道/房间白名单。您可以输入名称或 ID；向导会在可能时将名称解析为 ID。
- 如果您运行 daemon install 步骤，token auth 需要令牌，且 `gateway.auth.token` 由 SecretRef 管理，configure 会验证 SecretRef，但不会将解析后的明文令牌值持久化到 supervisor service environment metadata 中。
- 如果 token auth 需要令牌且配置的 token SecretRef 未解析，configure 将阻止 daemon install 并提供可操作的修复指导。
- 如果同时配置了 `gateway.auth.token` 和 `gateway.auth.password` 且 `gateway.auth.mode` 未设置，configure 将阻止 daemon install，直到明确设置 mode。

## 示例

```bash
openclaw configure
openclaw configure --section web
openclaw configure --section model --section channels
openclaw configure --section gateway --section daemon
```