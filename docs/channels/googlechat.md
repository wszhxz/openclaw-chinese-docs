---
summary: "Google Chat app support status, capabilities, and configuration"
read_when:
  - Working on Google Chat channel features
title: "Google Chat"
---
# Google Chat（Chat API）

状态：已通过 Google Chat API Webhook 准备好进行 DMs + 空间（仅 HTTP）。

## 快速设置（初学者）

1. 创建一个 Google Cloud 项目并启用 **Google Chat API**。
   - 前往：[Google Chat API 凭据](https://console.cloud.google.com/apis/api/chat.googleapis.com/credentials)
   - 如果尚未启用 API，请启用该 API。
2. 创建一个 **服务账户**：
   - 点击 **创建凭据** > **服务账户**。
   - 将其命名为您想要的名称（例如，`openclaw-chat`）。
   - 留空权限（点击 **继续**）。
   - 留空具有访问权限的主体（点击 **完成**）。
3. 创建并下载 **JSON 密钥**：
   - 在服务账户列表中，点击您刚刚创建的账户。
   - 前往 **密钥** 标签。
   - 点击 **添加密钥** > **创建新密钥**。
   - 选择 **JSON** 并点击 **创建**。
4. 将下载的 JSON 文件存储在您的网关主机上（例如，`~/.openclaw/googlechat-service-account.json`）。
5. 在 [Google Cloud Console Chat 配置](https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat) 中创建一个 Google Chat 应用：
   - 填写 **应用信息**：
     - **应用名称**：（例如 `OpenClaw`）
     - **头像 URL**：（例如 `https://openclaw.ai/logo.png`）
     - **描述**：（例如 `个人 AI 助手`）
   - 启用 **交互功能**。
   - 在 **功能** 下，勾选 **加入空间和群组对话**。
   - 在 **连接设置** 下，选择 **HTTP 端点 URL**。
   - 在 **触发器** 下，选择 **为所有触发器使用一个公共 HTTP 端点 URL**，并将其设置为您的网关的公共 URL 后跟 `/googlechat`。
     - _提示：运行 `openclaw status` 可以找到您的网关的公共 URL。_
   - 在 **可见性** 下，勾选 **在 &lt;您的域&gt; 中让此 Chat 应用对特定人员和组可用**。
   - 在文本框中输入您的电子邮件地址（例如 `user@example.com`）。
   - 点击 **保存**。
6. **启用应用状态**：
   - 保存后，**刷新页面**。
   - 查找 **应用状态** 部分（通常在保存后接近顶部或底部）。
   - 将状态更改为 **运行中 - 对用户可用**。
   - 点击 **保存**。
7. 使用服务账户路径 + Webhook 接收者配置 OpenClaw：
   - 环境变量：`GOOGLE_CHAT_SERVICE_ACCOUNT_FILE=/path/to/service-account.json`
   - 或配置：`channels.googlechat.serviceAccountFile: "/path/to/service-account.json"`。
8. 设置 Webhook 接收者类型 + 值（与您的 Chat 应用配置匹配）。
9. 启动网关。Google Chat 将会向您的 Webhook 路径发送 POST 请求。

## 添加到 Google Chat

一旦网关正在运行且您的电子邮件地址已添加到可见性列表中：

1. 前往 [Google Chat](https://chat.google.com/)。
2. 点击 **+**（加号）图标，位于 **直接消息** 旁边。
3. 在搜索栏（通常用于添加人员）中，输入您在 Google Cloud 控制台中配置的 **应用名称**。
   - **注意**：由于这是一个私有应用，机器人不会出现在“市场”浏览列表中。您必须通过名称搜索它。
4. 从结果中选择您的机器人。
5. 点击 **添加** 或 **聊天** 以开始一对一的对话。
6. 发送 "Hello" 以触发助手！

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公共 URL（仅 Webhook）

Google Chat Webhook 需要一个公共 HTTPS 端点。出于安全考虑，建议使用 HTTPS。如果未设置，将默认使用 `/googlechat`。

## 公