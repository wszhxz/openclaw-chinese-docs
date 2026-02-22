---
summary: "Google Chat app support status, capabilities, and configuration"
read_when:
  - Working on Google Chat channel features
title: "Google Chat"
---
# Google Chat (Chat API)

状态：通过 Google Chat API 网络钩子（仅限 HTTP）已准备好用于直接消息和空间。

## 快速设置（初学者）

1. 创建一个 Google Cloud 项目并启用 **Google Chat API**。
   - 访问：[Google Chat API 凭据](https://console.cloud.google.com/apis/api/chat.googleapis.com/credentials)
   - 如果尚未启用，请启用 API。
2. 创建一个 **服务账号**：
   - 点击 **创建凭据** > **服务账号**。
   - 命名为任意名称（例如，`openclaw-chat`）。
   - 权限留空（点击 **继续**）。
   - 授权主体留空（点击 **完成**）。
3. 创建并下载 **JSON 密钥**：
   - 在服务账号列表中，点击你刚刚创建的服务账号。
   - 进入 **密钥** 选项卡。
   - 点击 **添加密钥** > **创建新密钥**。
   - 选择 **JSON** 并点击 **创建**。
4. 将下载的 JSON 文件存储在网关主机上（例如，`~/.openclaw/googlechat-service-account.json`）。
5. 在 [Google Cloud 控制台 Chat 配置](https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat) 中创建一个 Google Chat 应用：
   - 填写 **应用信息**：
     - **应用名称**：（例如 `OpenClaw`）
     - **头像 URL**：（例如 `https://openclaw.ai/logo.png`）
     - **描述**：（例如 `Personal AI Assistant`）
   - 启用 **交互功能**。
   - 在 **功能** 下，勾选 **加入空间和群组对话**。
   - 在 **连接设置** 下，选择 **HTTP 终端点 URL**。
   - 在 **触发器** 下，选择 **对所有触发器使用通用 HTTP 终端点 URL**，并将其设置为你的网关的公共 URL 加上 `/googlechat`。
     - _提示：运行 `openclaw status` 查找你的网关的公共 URL。_
   - 在 **可见性** 下，勾选 **使此 Chat 应用对 <您的域名> 中的特定人员和组可用**。
   - 在文本框中输入你的电子邮件地址（例如 `user@example.com`）。
   - 点击底部的 **保存**。
6. **启用应用状态**：
   - 保存后，**刷新页面**。
   - 查找 **应用状态** 部分（通常在保存后顶部或底部）。
   - 将状态更改为 **实时 - 对用户可用**。
   - 再次点击 **保存**。
7. 使用服务账号路径 + 网络钩子受众配置 OpenClaw：
   - 环境变量: `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE=/path/to/service-account.json`
   - 或配置: `channels.googlechat.serviceAccountFile: "/path/to/service-account.json"`。
8. 设置网络钩子受众类型 + 值（与你的 Chat 应用配置匹配）。
9. 启动网关。Google Chat 将向你的网络钩子路径发送 POST 请求。

## 添加到 Google Chat

一旦网关正在运行且你的电子邮件已添加到可见性列表：

1. 访问 [Google Chat](https://chat.google.com/)。
2. 点击 **Direct Messages** 旁边的 **+**（加号）图标。
3. 在搜索栏（通常用于添加人员的地方），输入你在 Google Cloud 控制台中配置的 **应用名称**。
   - **注意**：机器人不会出现在“市场”浏览列表中，因为它是一个私有应用。必须通过名称搜索它。
4. 从结果中选择你的机器人。
5. 点击 **添加** 或 **聊天** 开始一对一对话。
6. 发送 "Hello" 触发助手！

## 公共 URL（仅限网络钩子）

Google Chat 网络钩子需要一个公共 HTTPS 终端点。出于安全考虑，**仅将 `/googlechat` 路径**暴露给互联网。将 OpenClaw 仪表板和其他敏感终端点保留在私有网络中。

### 选项 A：Tailscale Funnel（推荐）

使用 Tailscale Serve 用于私有仪表板，Funnel 用于公共网络钩子路径。这将使 `/` 保持私有，同时仅暴露 `/googlechat`。

1. **检查你的网关绑定到什么地址：**

   ```bash
   ss -tlnp | grep 18789
   ```

   记下 IP 地址（例如，`127.0.0.1`，`0.0.0.0`，或你的 Tailscale IP 如 `100.x.x.x`）。

2. **仅将仪表板暴露给 tailnet（端口 8443）：**

   ```bash
   # If bound to localhost (127.0.0.1 or 0.0.0.0):
   tailscale serve --bg --https 8443 http://127.0.0.1:18789

   # If bound to Tailscale IP only (e.g., 100.106.161.80):
   tailscale serve --bg --https 8443 http://100.106.161.80:18789
   ```

3. **仅公开网络钩子路径：**

   ```bash
   # If bound to localhost (127.0.0.1 or 0.0.0.0):
   tailscale funnel --bg --set-path /googlechat http://127.0.0.1:18789/googlechat

   # If bound to Tailscale IP only (e.g., 100.106.161.80):
   tailscale funnel --bg --set-path /googlechat http://100.106.161.80:18789/googlechat
   ```

4. **授权节点以访问 Funnel：**
   如果提示，请访问输出中显示的授权 URL 以在你的 tailnet 策略中为该节点启用 Funnel。

5. **验证配置：**

   ```bash
   tailscale serve status
   tailscale funnel status
   ```

你的公共网络钩子 URL 将为：
`https://<node-name>.<tailnet>.ts.net/googlechat`

你的私有仪表板保持 tailnet 专用：
`https://<node-name>.<tailnet>.ts.net:8443/`

在 Google Chat 应用配置中使用公共 URL（不带 `:8443`）。

> 注意：此配置在重启后仍然有效。稍后要移除它，请运行 `tailscale funnel reset` 和 `tailscale serve reset`。

### 选项 B：反向代理（Caddy）

如果你使用反向代理如 Caddy，仅代理特定路径：

```caddy
your-domain.com {
    reverse_proxy /googlechat* localhost:18789
}
```

使用此配置，任何对 `your-domain.com/` 的请求将被忽略或返回 404，而 `your-domain.com/googlechat` 将安全地路由到 OpenClaw。

### 选项 C：Cloudflare Tunnel

配置隧道的入口规则以仅路由网络钩子路径：

- **路径**：`/googlechat` -> `http://localhost:18789/googlechat`
- **默认规则**：HTTP 404（未找到）

## 工作原理

1. Google Chat 向网关发送网络钩子 POST 请求。每个请求包含一个 `Authorization: Bearer <token>` 头。
2. OpenClaw 验证令牌与配置的 `audienceType` + `audience`：
   - `audienceType: "app-url"` → 受众是你的 HTTPS 网络钩子 URL。
   - `audienceType: "project-number"` → 受众是云项目编号。
3. 消息按空间路由：
   - 直接消息使用会话密钥 `agent:<agentId>:googlechat:dm:<spaceId>`。
   - 空间使用会话密钥 `agent:<agentId>:googlechat:group:<spaceId>`。
4. 默认情况下，直接消息访问是配对的。未知发送者会收到配对代码；批准使用：
   - `openclaw pairing approve googlechat <code>`
5. 默认情况下，组空间需要 @提及。如果提及检测需要应用的用户名，请使用 `botUser`。

## 目标

使用这些标识符进行传递和白名单：

- 直接消息：`users/<userId>`（推荐）或原始电子邮件 `name@example.com`（可变主体）。
- 已弃用：`users/<email>` 被视为用户 ID，而不是电子邮件白名单。
- 空间：`spaces/<spaceId>`。

## 配置亮点

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url",
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890", // optional; helps mention detection
      dm: {
        policy: "pairing",
        allowFrom: ["users/1234567890", "name@example.com"],
      },
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": {
          allow: true,
          requireMention: true,
          users: ["users/1234567890"],
          systemPrompt: "Short answers only.",
        },
      },
      actions: { reactions: true },
      typingIndicator: "message",
      mediaMaxMb: 20,
    },
  },
}
```

注意事项：

- 服务账号凭据也可以通过 `serviceAccount`（JSON 字符串）内联传递。
- 如果未设置 `webhookPath`，默认网络钩子路径为 `/googlechat`。
- 当启用 `actions.reactions` 时，反应可通过 `reactions` 工具和 `channels action` 提供。
- `typingIndicator` 支持 `none`，`message`（默认），和 `reaction`（反应需要用户 OAuth）。
- 附件通过 Chat API 下载并通过媒体管道存储（大小受 `mediaMaxMb` 限制）。

## 故障排除

### 405 方法不允许

如果 Google Cloud 日志浏览器显示错误，如：

```
status code: 405, reason phrase: HTTP error response: HTTP/1.1 405 Method Not Allowed
```

这意味着网络钩子处理程序未注册。常见原因：

1. **通道未配置**：你的配置中缺少 `channels.googlechat` 部分。验证：

   ```bash
   openclaw config get channels.googlechat
   ```

   如果返回 "配置路径未找到"，添加配置（参见 [配置亮点](#config-highlights)）。

2. **插件未启用**：检查插件状态：

   ```bash
   openclaw plugins list | grep googlechat
   ```

   如果显示 "禁用"，在配置中添加 `plugins.entries.googlechat.enabled: true`。

3. **网关未重启**：添加配置后，重启网关：

   ```bash
   openclaw gateway restart
   ```

验证通道是否正在运行：

```bash
openclaw channels status
# Should show: Google Chat default: enabled, configured, ...
```

### 其他问题

- 检查 `openclaw channels status --probe` 以查找身份验证错误或缺失的受众配置。
- 如果没有消息到达，请确认 Chat 应用的网络钩子 URL + 事件订阅。
- 如果提及门控阻止回复，请将 `botUser` 设置为应用的用户资源名称并验证 `requireMention`。
- 在发送测试消息时使用 `openclaw logs --follow` 查看请求是否到达网关。

相关文档：

- [网关配置](/gateway/configuration)
- [安全性](/gateway/security)
- [反应](/tools/reactions)