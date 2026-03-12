---
summary: "Gateway dashboard (Control UI) access and auth"
read_when:
  - Changing dashboard authentication or exposure modes
title: "Dashboard"
---
# 仪表板（控制UI）

网关仪表板是默认在`/`提供的浏览器控制UI
（可以通过`gateway.controlUi.basePath`覆盖）。

快速打开（本地网关）：

- [http://127.0.0.1:18789/](http://127.0.0.1:18789/) （或 [http://localhost:18789/](http://localhost:18789/)）

关键参考：

- [控制UI](/web/control-ui) 用于使用和UI功能。
- [Tailscale](/gateway/tailscale) 用于Serve/Funnel自动化。
- [Web界面](/web) 用于绑定模式和安全注意事项。

身份验证通过`connect.params.auth`在WebSocket握手时强制执行
（令牌或密码）。请参阅[网关配置](/gateway/configuration)中的`gateway.auth`。

安全提示：控制UI是一个**管理界面**（聊天、配置、执行审批）。
不要公开暴露它。UI会在当前标签页的内存中保留仪表板URL令牌，并在加载后从URL中移除它们。
建议使用localhost、Tailscale Serve或SSH隧道。

## 快速路径（推荐）

- 在引导过程之后，CLI会自动打开仪表板并打印一个干净的（非令牌化）链接。
- 随时重新打开：`openclaw dashboard`（复制链接，如果可能的话打开浏览器，如果是无头环境则显示SSH提示）。
- 如果UI提示进行身份验证，请将`gateway.auth.token`（或`OPENCLAW_GATEWAY_TOKEN`）中的令牌粘贴到控制UI设置中。

## 令牌基础（本地与远程）

- **本地主机**：打开`http://127.0.0.1:18789/`。
- **令牌来源**：`gateway.auth.token`（或`OPENCLAW_GATEWAY_TOKEN`）；`openclaw dashboard`可以通过URL片段传递以进行一次性引导，但控制UI不会在localStorage中持久化网关令牌。
- 如果`gateway.auth.token`由SecretRef管理，`openclaw dashboard`设计上会打印/复制/打开一个非令牌化的URL。这避免了在shell日志、剪贴板历史或浏览器启动参数中暴露外部管理的令牌。
- 如果`gateway.auth.token`被配置为SecretRef并且在您的当前shell中未解析，`openclaw dashboard`仍然会打印一个非令牌化的URL以及可操作的身份验证设置指南。
- **非本地主机**：使用Tailscale Serve（如果`gateway.auth.allowTailscale: true`，对于控制UI/WebSocket无需令牌，假设受信任的网关主机；HTTP API仍需要令牌/密码），带有令牌的tailnet绑定，或SSH隧道。请参阅[Web界面](/web)。

## 如果您看到“未经授权”/1008

- 确保网关可访问（本地：`openclaw status`；远程：SSH隧道`ssh -N -L 18789:127.0.0.1:18789 user@host`然后打开`http://127.0.0.1:18789/`）。
- 从网关主机检索或提供令牌：
  - 明文配置：`openclaw config get gateway.auth.token`
  - 由SecretRef管理的配置：解决外部密钥提供商或在此shell中导出`OPENCLAW_GATEWAY_TOKEN`，然后重新运行`openclaw dashboard`
  - 未配置令牌：`openclaw doctor --generate-gateway-token`
- 在仪表板设置中，将令牌粘贴到身份验证字段中，然后连接。