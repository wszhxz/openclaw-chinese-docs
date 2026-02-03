---
summary: "CLI reference for `openclaw configure` (interactive configuration prompts)"
read_when:
  - You want to tweak credentials, devices, or agent defaults interactively
title: "configure"
---
# `openclaw configure`

交互式提示以设置凭据、设备和代理默认值。

注意：**模型**部分现在包含一个用于 `agents.defaults.models` 允许列表的多选功能（即在 `/model` 中显示的内容以及模型选择器中显示的内容）。

提示：`openclaw config` 不带子命令会打开相同的向导。使用 `openclaw config get|set|unset` 进行非交互式编辑。

相关链接：

- 网关配置参考：[配置](/gateway/configuration)
- 配置 CLI：[Config](/cli/config)

注意事项：

- 选择网关运行的位置始终会更新 `gateway.mode`。如果您只需要此功能，可以选择“继续”而无需配置其他部分。
- 面向频道的服务（如 Slack/Discord/Matrix/Microsoft Teams）在设置期间会提示频道/房间允许列表。您可以输入名称或 ID；向导会在可能的情况下将名称解析为 ID。

## 示例

```bash
openclaw configure
openclaw configure --section models --section channels
```