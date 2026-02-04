---
summary: "CLI reference for `openclaw configure` (interactive configuration prompts)"
read_when:
  - You want to tweak credentials, devices, or agent defaults interactively
title: "configure"
---
# `openclaw configure`

交互式提示以设置凭据、设备和代理默认值。

注意：**Model** 部分现在包括一个用于 `agents.defaults.models` 允许列表的多选（显示在 `/model` 和模型选择器中）。

提示：`openclaw config` 不带子命令会打开相同的向导。使用 `openclaw config get|set|unset` 进行非交互式编辑。

相关：

- 网关配置参考：[Configuration](/gateway/configuration)
- 配置 CLI：[Config](/cli/config)

注意事项：

- 选择网关运行的位置始终会更新 `gateway.mode`。如果只需要这部分，可以选择“继续”而不填写其他部分。
- 面向频道的服务（Slack/Discord/Matrix/Microsoft Teams）在设置期间会提示输入频道/房间允许列表。可以输入名称或ID；向导会在可能的情况下将名称解析为ID。

## 示例

```bash
openclaw configure
openclaw configure --section models --section channels
```