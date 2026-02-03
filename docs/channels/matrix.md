---
summary: "Matrix support status, capabilities, and configuration"
read_when:
  - Working on Matrix channel features
title: "Matrix"
---
配置<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context. The document is about setting up a Matrix plugin for OpenClaw, including installation steps, configuration options, and features like E2EE and threading.

First, I'll go through each section carefully. The title is "# Matrix (plugin)", which should be translated as "# 矩阵（插件）". The first paragraph explains that Matrix is an open, decentralized messaging protocol. I need to make sure technical terms like "decentralized" are accurately translated. "Decentralized" becomes "去中心化".

Next, there's a mention of OpenClaw connecting as a Matrix user. I'll translate "user" as "用户" and "homeserver" as "主服务器". The part about needing a Matrix account for the bot should be clear. 

The status section lists supported features. Terms like "Direct messages" become "直接消息", "rooms" as "房间", "threads" as "线程", etc. I need to ensure that the technical terms are consistent throughout the translation.

The "Plugin required" section explains that Matrix is a plugin. I'll translate "ships as a plugin" to "作为插件提供". The installation instructions via CLI and local checkout need to be accurately translated, keeping the code blocks as they are but translating the surrounding text.

In the setup section, steps are numbered. I'll maintain the numbering and translate each instruction. For example, "Create a Matrix account on a homeserver" becomes "在主服务器上创建一个Matrix账户". 

The part about getting an access token uses a curl command. I'll keep the code block intact but translate the explanation around it. Terms like "access token" should be "访问令牌".

Configuration details involve environment variables and config settings. I'll translate terms like "Env" to "环境变量" and "config" to "配置". The JSON examples should remain in code blocks but with Chinese comments if necessary.

The E2EE section explains encryption support. I'll translate "End-to-end encryption" to "端到端加密" and ensure that technical terms related to encryption are correctly rendered. The mention of the Rust crypto SDK should be translated accurately.

Routing model and access control sections have specific terms like "replies", "DMs", "allowlist". I'll use standard translations for these, ensuring consistency. For example, "allowlist" becomes "白名单".

The Rooms section discusses group policies and allowlists. I'll translate terms like "allowlist" and "mention-gated" appropriately. The JSON configuration examples need to be preserved with proper syntax.

Threads section mentions reply threading. I'll translate "reply threading" to "回复线程" and ensure the options like "off", "inbound", "always" are correctly translated.

Capabilities table lists features with status. I'll translate each feature name and status, keeping the table structure intact. For example, "Direct messages" becomes "直接消息" and "Supported" as "支持".

Configuration reference section has various parameters. I'll translate each parameter name and description, ensuring that the technical terms are accurately rendered. For example, "homeserver URL" becomes "主服务器URL".

Throughout the translation, I'll maintain the structure and formatting, keeping code blocks and JSON configurations as they are. I'll also ensure that all technical terms are consistently translated and that the document remains clear and accurate in Chinese. Finally, I'll review the entire translation to check for any errors or inconsistencies, making sure that the translated text reads naturally and maintains the original meaning.
</think>

# 矩阵（插件）

矩阵是一个开放、去中心化的消息协议。OpenClaw 以矩阵 **用户** 的身份连接到任何主服务器，因此你需要一个矩阵账户来使用这个机器人。一旦登录成功，你可以直接与机器人私聊，或者将其邀请到房间（矩阵“群组”）。Beeper 也是一个有效的客户端选项，但需要启用端到端加密（E2EE）。

状态：通过插件支持（@vector-im/matrix-bot-sdk）。支持直接消息、房间、线程、媒体、反应、投票（发送 + 开始投票作为文本）、位置和端到端加密（带加密支持）。

## 所需插件

矩阵作为插件提供，不包含在核心安装中。

通过 CLI（npm 注册表）安装：

```bash
openclaw plugins install @openclaw/matrix
```

本地检出（当从 git 仓库运行时）：

```bash
openclaw plugins install ./extensions/matrix
```

如果你在配置/引导过程中选择了矩阵，并且检测到 git 检出，OpenClaw 会自动提供本地安装路径。

详情：[插件](/plugin)

## 设置

1. 安装矩阵插件：
   - 从 npm：`openclaw plugins install @openclaw/matrix`
   - 从本地检出：`openclaw plugins install ./extensions/matrix`
2. 在主服务器上创建一个矩阵账户：
   - 在 [https://matrix.org/ecosystem/hosting/](https://matrix.org/ecosystem/hosting/) 浏览托管选项
   - 或者自行托管
3. 获取机器人的访问令牌：
   - 使用 curl 在你的主服务器上调用矩阵登录 API：

   ```bash
   curl --request POST \
     --url https://matrix.example.org/_matrix/client/v3/login \
     --header 'Content-Type: application/json' \
     --data '{
     "type": "m.login.password",
     "identifier": {
       "type": "m.id.user",
       "user": "your-user-name"
     },
     "password": "your-password"
   }'
   ```

   - 将 `matrix.example.org` 替换为你的主服务器 URL。
   - 或者设置 `channels.matrix.userId` + `channels.matrix.password`：OpenClaw 会调用相同的登录端点，将访问令牌存储在 `~/.openclaw/credentials/matrix/credentials.json`，并在下次启动时重用。

4. 配置凭证：
   - 环境变量：`MATRIX_HOMESERVER`, `MATRIX_ACCESS_TOKEN`（或 `MATRIX_USER_ID` + `MATRIX_PASSWORD`）
   - 或配置：`channels.matrix.*`
   - 如果两者都设置，配置优先。
   - 使用访问令牌时，用户 ID 会通过 `/whoami` 自动获取。
   - 设置时，`channels.matrix.userId` 应该是完整的矩阵 ID（示例：`@bot:example.org`）。
5. 重启网关（或完成引导）。
6. 从任何矩阵客户端（Element、Beeper 等）与机器人开始私聊或邀请它加入房间（参见 [https://matrix.org/ecosystem/clients/](https://matrix.org/ecosystem/clients/)）。Beeper 需要 E2EE，因此设置 `channels.matrix.encryption: true` 并验证设备。

最小配置（使用访问令牌，用户 ID 自动获取）：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_***",
      dm: { policy: "pairing" },
    },
  },
}
```

E2EE 配置（启用端到端加密）：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_***",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

## 加密（E2EE）

端到端加密通过 Rust 加密 SDK 支持。

启用 `channels.matrix.encryption: true`：

- 如果加密模块加载，加密房间会自动解密。
- 发送到加密房间的出站媒体会加密。
- 首次连接时，OpenClaw 会从你的其他会话请求设备验证。
- 在另一个矩阵客户端（Element 等）中验证设备以启用密钥共享。
- 如果无法加载加密模块，E2EE 将被禁用，加密房间无法解密；OpenClaw 会记录警告。
- 如果看到缺少加密模块的错误（例如 `@matrix-org/matrix-sdk-crypto-nodejs-*`），允许构建脚本为 `@matrix-org/matrix-sdk-crypto-nodejs` 运行 `pnpm rebuild @matrix-org/matrix-sdk-crypto-nodejs` 或使用 `node node_modules/@matrix-org/matrix-sdk-crypto-nodejs`。

## 路由模型

## 访问控制

## 房间

## 线程

## 功能表

## 配置参考

## 配置参数

### 环境变量
- `MATRIX_HOMESERVER`: 主服务器 URL
- `MATRIX_ACCESS_TOKEN`: 访问令牌
- `MATRIX_USER_ID`: 用户 ID
- `MATRIX_PASSWORD`: 密码

### 配置参数
- `channels.matrix.homeserver`: 主服务器 URL
- `channels.matrix.accessToken`: 访问令牌
- `channels.matrix.userId`: 用户 ID
- `channels.matrix.password`: 密码
- `channels.matrix.dm.policy`: DM 策略（默认：pairing）
- `channels.matrix.dm.allowFrom`: DM 白名单（用户 ID 或显示名称）。`open` 需要 `"*"`. 工具会尽可能将名称解析为 ID。
- `channels.matrix.groupPolicy`: 群组策略（默认：allowlist）
-