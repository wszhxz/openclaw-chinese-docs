---
summary: "iMessage via BlueBubbles macOS server (REST send/receive, typing, reactions, pairing, advanced actions)."
read_when:
  - Setting up BlueBubbles channel
  - Troubleshooting webhook pairing
  - Configuring iMessage on macOS
title: "BlueBubbles"
---
# BlueBubbles（macOS REST）

状态：捆绑的插件，通过HTTP与BlueBubbles macOS服务器通信。**推荐用于iMessage集成**，因其API更丰富，设置比旧版imsg通道更简单。

## 概述

- 通过BlueBubbles辅助应用在macOS上运行（[bluebubbles.app](https://bluebubbles.app)）。
- 推荐/测试：macOS Sequoia（15）。macOS Tahoe（26）可工作；Tahoe上编辑功能当前损坏，群组图标更新可能报告成功但未同步。
- OpenClaw通过其REST API与之通信（`GET /api/v1/ping`，`POST /message/text`，`POST /chat/:id/*`）。
- 进入消息通过webhook接收；传出回复、输入指示器、已读回执和tapbacks通过REST调用。
- 附件和贴纸作为入站媒体处理（在可能时向代理呈现）。
- 配对/允许列表与其它通道的工作方式相同（`/start/pairing`等），使用`channels.bluebubbles.allowFrom` + 配对码。
- 反应作为系统事件呈现，如同Slack/Telegram，因此代理可以在回复前“提及”它们。
- 高级功能：编辑、撤回、回复线程、消息效果、群组管理。

## 快速入门

1. 在你的Mac上安装BlueBubbles插件。
2. 配置BlueBubbles服务器并确保其通过HTTP运行。
3. 使用OpenClaw工具进行初始化设置。
4. 通过JSON配置文件设置服务器URL、密码和Webhook路径。
5. 验证配置并启动服务。

## 初始化设置

- 使用命令行工具`openclaw onboard`进行初始化。
- 配置文件示例：
  ```json
  {
    "serverUrl": "https://yourserver.com",
    "password": "yourpassword",
    "webhookPath": "/webhook"
  }
  ```
- 确保服务器版本与OpenClaw兼容，并启用必要的API功能。

## 访问控制

- **提及控制**：配置允许的提及模式，以控制群组消息的发送者。
- **群组策略**：设置群组消息的发送权限，如`open`、`allowlist`或`disabled`。
- **允许来源**：定义允许的发送者，包括处理、邮箱、E.164号码、`chat_id:*`和`chat_guid:*`。

## 输入与已读回执

- **输入指示器**：启用或禁用输入状态的显示。
- **已读回执**：配置是否发送已读回执，以通知发送者消息已读。
- **分块模式**：设置文本分块方式，如按长度或换行分块。

## 高级功能

- **反应**：启用或禁用消息反应功能，需BlueBubbles私有API支持。
- **编辑/撤回**：需macOS 13+和兼容的BlueBubbles服务器版本。Tahoe（26）上编辑功能当前损坏。
- **群组图标更新**：可能在Tahoe（26）上不稳定，API可能返回成功但图标未同步。

## 媒体与限制

- **媒体最大MB**：设置入站媒体的大小限制，默认为8MB。
- **文本分块限制**：设置出站文本的分块大小，默认为4000字符。
- **历史记录限制**：设置群组消息的历史记录数量，0表示禁用。

## 配置参考

- **服务器URL**：设置BlueBubbles服务器的地址。
- **密码**：设置API访问密码，需保密。
- **Webhook路径**：配置Webhook的接收路径，确保与服务器配置一致。
- **分块模式**：设置文本分块方式，如按长度或换行分块。
- **多账户配置**：设置多个账户的配置参数。

## 地址与交付目标

- **稳定路由**：优先使用`chat_guid`，如`chat_guid:iMessage;-;+15555550123`（适用于群组）。
- **直接处理**：使用`+15555550123`或`user@example.com`，若无现有DM聊天，OpenClaw将创建新聊天。

## 安全

- **Webhook身份验证**：通过比较`guid`/`password`查询参数或头信息与`channels.bluebubbles.password`进行验证。本地主机请求也接受。
- **保密性**：保持API密码和Webhook端点的机密性，如同处理凭证。
- **反向代理信任**：若使用反向代理，需在代理层要求身份验证，并配置`gateway.trustedProxies`。
- **HTTPS与防火墙**：若在局域网外暴露BlueBubbles服务器，启用HTTPS和防火墙规则。

## 故障排除

- **输入/已读事件停止工作**：检查BlueBubbles Webhook日志，确保网关路径匹配`channels.bluebubbles.webhookPath`。