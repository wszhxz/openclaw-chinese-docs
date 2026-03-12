---
summary: "CLI reference for `openclaw configure` (interactive configuration prompts)"
read_when:
  - You want to tweak credentials, devices, or agent defaults interactively
title: "configure"
---
# `openclaw configure`

用于配置凭据、设备及代理默认设置的交互式提示。

注意：**模型（Model）** 部分现在包含一个针对 `agents.defaults.models` 白名单的多选控件（即在 `/model` 和模型选择器中显示的内容）。

提示：直接运行 `openclaw config`（不带子命令）将打开相同的向导。如需非交互式编辑，请使用 `openclaw config get|set|unset`。

相关文档：

- 网关配置参考：[配置](/gateway/configuration)  
- 配置 CLI：[Config](/cli/config)

注意事项：

- 选择网关运行位置时，始终会更新 `gateway.mode`。如果仅需执行此操作，可跳过其他部分并直接选择“继续”。
- 面向通道的服务（如 Slack / Discord / Matrix / Microsoft Teams）在设置过程中会提示输入通道/房间白名单。您可以输入名称或 ID；向导会在可能的情况下将名称解析为 ID。
- 若执行守护进程安装步骤，且启用了令牌认证，则必须提供令牌；而 `gateway.auth.token` 由 SecretRef 管理，`configure` 命令会校验该 SecretRef，但不会将解析出的明文令牌值持久化写入 supervisor 服务的环境元数据中。
- 若启用了令牌认证，但所配置的令牌 SecretRef 尚未解析，则 `configure` 将阻止守护进程安装，并提供可操作的修复指引。
- 若同时配置了 `gateway.auth.token` 和 `gateway.auth.password`，但 `gateway.auth.mode` 未设置，则 `configure` 将阻止守护进程安装，直至显式设置了运行模式（mode）。

## 示例

```bash
openclaw configure
openclaw configure --section model --section channels
```