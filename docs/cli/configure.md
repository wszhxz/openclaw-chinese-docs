---
summary: "CLI reference for `openclaw configure` (interactive configuration prompts)"
read_when:
  - You want to tweak credentials, devices, or agent defaults interactively
title: "configure"
---
# `openclaw configure`

用于设置凭据、设备和代理默认值的交互式提示。

注意：**Model** 部分现在包含一个用于
`agents.defaults.models` 允许列表（显示在 `/model` 和模型选择器中）。

提示：`openclaw config` 不带子命令将打开相同的向导。使用
`openclaw config get|set|unset` 进行非交互式编辑。

相关：

- 网关配置参考：[配置](/gateway/configuration)
- Config CLI：[Config](/cli/config)

注意：

- 选择 Gateway 运行位置总会更新 `gateway.mode`。如果只需要此项，您可以选择“继续”而跳过其他部分。
- 面向渠道的服务（Slack/Discord/Matrix/Microsoft Teams）会在设置期间提示输入渠道/房间允许列表。您可以输入名称或 ID；向导会在可能时将名称解析为 ID。
- 如果您运行 daemon 安装步骤，token auth 需要 token，且 `gateway.auth.token` 由 SecretRef 管理，configure 会验证 SecretRef 但不会将解析后的明文 token 值持久化到 supervisor 服务环境元数据中。
- 如果 token auth 需要 token 且配置的 token SecretRef 未解析，configure 会阻止 daemon 安装并提供可操作的修复指导。
- 如果 `gateway.auth.token` 和 `gateway.auth.password` 都已配置且 `gateway.auth.mode` 未设置，configure 会阻止 daemon 安装，直到显式设置 mode。

## 示例

```bash
openclaw configure
openclaw configure --section model --section channels
```