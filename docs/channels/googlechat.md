---
summary: "Google Chat app support status, capabilities, and configuration"
read_when:
  - Working on Google Chat channel features
title: "Google Chat"
---
# Google Chat (Chat API)

状态：已通过 Google Chat API webhooks（仅限 HTTP）准备好支持 DMs + spaces。

## 快速设置（初学者）

1. 创建 Google Cloud 项目并启用 **Google Chat API**。
   - 前往：[Google Chat API 凭据](https://console.cloud.google.com/apis/api/chat.googleapis.com/credentials)
   - 如果尚未启用，请启用该 API。
2. 创建 **服务账号**：
   - 点击 **创建凭据** > **服务账号**。
   - 命名为您想要的任何名称（例如 `openclaw-chat`）。
   - 留空权限（点击 **继续**）。
   - 留空具有访问权限的主体（点击 **完成**）。
3. 创建并下载 **JSON 密钥**：
   - 在服务账号列表中，点击您刚刚创建的那个。
   - 前往 **密钥** 标签页。
   - 点击 **添加密钥** > **创建新密钥**。
   - 选择 **JSON** 并按 **创建**。
4. 将下载的 JSON 文件存储在网关主机上（例如 `~/.openclaw/googlechat-service-account.json`）。
5. 在 [Google Cloud Console Chat 配置](https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat) 中创建 Google Chat 应用：
   - 填写 **应用信息**：
     - **应用名称**：（例如 `OpenClaw`）
     - **头像 URL**：（例如 `https://openclaw.ai/logo.png`）
     - **描述**：（例如 `Personal AI Assistant`）
   - 启用 **交互功能**。
   - 在 **功能** 下，勾选 **加入空间和群组对话**。
   - 在 **连接设置** 下，选择 **HTTP 端点 URL**。
   - 在 **触发器** 下，选择 **为所有触发器使用通用的 HTTP 端点 URL** 并将其设置为您的网关公共 URL 后跟 `/googlechat`。
     - _提示：运行 `openclaw status` 以查找您的网关公共 URL。_
   - 在 **可见性** 下，勾选 **使此 Chat 应用对 &lt;您的域名&gt; 中的特定人员和组可用**。
   - 在文本框中输入您的电子邮件地址（例如 `user@example.com`）。
   - 点击底部的 **保存**。
6. **启用应用状态**：
   - 保存后，**刷新页面**。
   - 查找 **应用状态** 部分（通常在保存后的顶部或底部附近）。
   - 将状态更改为 **已上线 - 对用户可用**。
   - 再次点击 **保存**。
7. 使用服务账号路径 + webhook 受众配置 OpenClaw：
   - 环境变量：`GOOGLE_CHAT_SERVICE_ACCOUNT_FILE=/path/to/service-account.json`
   - 或配置：`channels.googlechat.serviceAccountFile: "/path/to/service-account.json"`。
8. 设置 webhook 受众类型 + 值（与您的 Chat 应用配置匹配）。
9. 启动网关。Google Chat 将向您的 webhook 路径发送 POST 请求。

## 添加到 Google Chat

一旦网关运行且您的电子邮件已添加到可见性列表：

1. 前往 [Google Chat](https://chat.google.com/)。
2. 点击 **直接消息** 旁边的 **+**（加号）图标。
3. 在搜索栏（通常添加人员的地方）中，输入您在 Google Cloud Console 中配置的 **应用名称**。
   - **注意**：由于这是私有应用，机器人不会出现在“市场”浏览列表中。您必须按名称搜索它。
4. 从结果中选择您的机器人。
5. 点击 **添加** 或 **聊天** 开始 1:1 对话。
6. 发送“你好”以触发助手！

## 公共 URL（仅限 Webhook）

Google Chat webhooks 需要公共 HTTPS 端点。出于安全考虑，**仅将 `/googlechat` 路径** 暴露给互联网。将 OpenClaw 仪表板和其他敏感端点保留在您的私有网络上。

### 选项 A：Tailscale Funnel（推荐）

使用 Tailscale Serve 用于私有仪表板，Funnel 用于公共 webhook 路径。这将保持 `/` 私有，同时仅暴露 `/googlechat`。

1. **检查网关绑定的地址：**

   ```bash
   ss -tlnp | grep 18789
   ```

   注意 IP 地址（例如 `127.0.0.1`、`0.0.0.0` 或您的 Tailscale IP 如 `100.x.x.x`）。

2. **仅将仪表板暴露给 tailnet（端口 8443）：**

   ```bash
   # If bound to localhost (127.0.0.1 or 0.0.0.0):
   tailscale serve --bg --https 8443 http://127.0.0.1:18789

   # If bound to Tailscale IP only (e.g., 100.106.161.80):
   tailscale serve --bg --https 8443 http://100.106.161.80:18789
   ```

3. **仅公开暴露 webhook 路径：**

   ```bash
   # If bound to localhost (127.0.0.1 or 0.0.0.0):
   tailscale funnel --bg --set-path /googlechat http://127.0.0.1:18789/googlechat

   # If bound to Tailscale IP only (e.g., 100.106.161.80):
   tailscale funnel --bg --set-path /googlechat http://100.106.161.80:18789/googlechat
   ```

4. **授权节点以访问 Funnel：**
   如果提示，请访问输出中显示的授权 URL，以便在您的 tailnet 策略中为此节点启用 Funnel。

5. **验证配置：**

   ```bash
   tailscale serve status
   tailscale funnel status
   ```

您的公共 webhook URL 将是：
`https://<node-name>.<tailnet>.ts.net/googlechat`

您的私有仪表板保持仅限 tailnet：
`https://<node-name>.<tailnet>.ts.net:8443/`

在 Google Chat 应用配置中使用公共 URL（不带 `:8443`）。

> 注意：此配置跨重启持久化。要稍后移除它，请运行 `tailscale funnel reset` 和 `tailscale serve reset`。

### 选项 B：反向代理（Caddy）

如果您使用像 Caddy 这样的反向代理，仅代理特定路径：

```caddy
your-domain.com {
    reverse_proxy /googlechat* localhost:18789
}
```

使用此配置，任何请求到 `your-domain.com/` 的请求将被忽略或返回 404，而 `your-domain.com/googlechat` 将安全地路由到 OpenClaw。

### 选项 C：Cloudflare Tunnel

配置隧道的入口规则以仅路由 webhook 路径：

- **路径**：`/googlechat` -> `http://localhost:18789/googlechat`
- **默认规则**：HTTP 404（未找到）

## 工作原理

1. Google Chat 发送 webhook POST 请求到网关。每个请求包含一个 `Authorization: Bearer <token>` 头。
   - 当存在该头时，OpenClaw 在读取/解析完整 webhook 主体之前验证 Bearer 认证。
   - 在主体中携带 `authorizationEventObject.systemIdToken` 的 Google Workspace 附加组件请求通过更严格的预身份验证主体预算支持。
2. OpenClaw 根据配置的 `audienceType` + `audience` 验证令牌：
   - `audienceType: "app-url"` → 受众是您的 HTTPS webhook URL。
   - `audienceType: "project-number"` → 受众是云项目号。
3. 消息按空间路由：
   - DMs 使用会话密钥 `agent:<agentId>:googlechat:direct:<spaceId>`。
   - Spaces 使用会话密钥 `agent:<agentId>:googlechat:group:<spaceId>`。
4. DM 访问默认为配对。未知发送者收到配对代码；使用以下命令批准：
   - `openclaw pairing approve googlechat <code>`
5. 群组空间默认需要 @提及。如果提及检测需要应用程序的用户名，请使用 `botUser`。

## 目标

使用这些标识符进行交付和允许列表：

- 直接消息：`users/<userId>`（推荐）。
- 原始电子邮件 `name@example.com` 是可变的，仅在 `channels.googlechat.dangerouslyAllowNameMatching: true` 时用于直接允许列表匹配。
- 已弃用：`users/<email>` 被视为用户 ID，而不是电子邮件允许列表。
- 空间：`spaces/<spaceId>`。

## 配置亮点

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      // or serviceAccountRef: { source: "file", provider: "filemain", id: "/channels/googlechat/serviceAccount" }
      audienceType: "app-url",
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890", // optional; helps mention detection
      dm: {
        policy: "pairing",
        allowFrom: ["users/1234567890"],
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

注意：

- 服务账号凭据也可以内联传递 `serviceAccount`（JSON 字符串）。
- `serviceAccountRef` 也受支持（env/file SecretRef），包括 `channels.googlechat.accounts.<id>.serviceAccountRef` 下的每账号引用。
- 如果未设置 `webhookPath`，默认 webhook 路径是 `/googlechat`。
- `dangerouslyAllowNameMatching` 重新启用可变电子邮件主体匹配以用于允许列表（紧急模式兼容性模式）。
- 当启用 `actions.reactions` 时，可通过 `reactions` 工具和 `channels action` 使用反应。
- 消息操作暴露 `send` 用于文本，`upload-file` 用于显式附件发送。`upload-file` 接受 `media` / `filePath` / `path` 加上可选的 `message`、`filename` 和线程定位。
- `typingIndicator` 支持 `none`、`message`（默认）和 `reaction`（反应需要用户 OAuth）。
- 附件通过 Chat API 下载并存储在媒体管道中（大小限制由 `mediaMaxMb` 设定）。

秘密引用详情：[秘密管理](/gateway/secrets)。

## 故障排除

### 405 方法不允许

如果 Google Cloud Logs Explorer 显示如下错误：

```
status code: 405, reason phrase: HTTP error response: HTTP/1.1 405 Method Not Allowed
```

这意味着 webhook 处理器未注册。常见原因：

1. **通道未配置**：您的配置中缺少 `channels.googlechat` 部分。使用以下命令验证：

   ```bash
   openclaw config get channels.googlechat
   ```

   如果返回“未找到配置路径”，请添加配置（参见 [配置亮点](#config-highlights)）。

2. **插件未启用**：检查插件状态：

   ```bash
   openclaw plugins list | grep googlechat
   ```

   如果显示“禁用”，请将 `plugins.entries.googlechat.enabled: true` 添加到您的配置。

3. **网关未重启**：添加配置后，重启网关：

   ```bash
   openclaw gateway restart
   ```

验证通道正在运行：

```bash
openclaw channels status
# Should show: Google Chat default: enabled, configured, ...
```

### 其他问题

- 检查 `openclaw channels status --probe` 是否存在身份验证错误或缺失的受众配置。
- 如果没有消息到达，请确认聊天应用的 Webhook URL 和事件订阅。
- 如果提及限制阻止了回复，请将 `botUser` 设置为应用的用户资源名称并验证 `requireMention`。
- 发送测试消息时使用 `openclaw logs --follow`，以查看请求是否到达网关。

相关文档：

- [网关配置](/gateway/configuration)
- [安全](/gateway/security)
- [反应](/tools/reactions)

## 相关

- [频道概览](/channels) — 所有支持的频道
- [配对](/channels/pairing) — 私聊认证和配对流程
- [群组](/channels/groups) — 群聊行为和提及限制
- [频道路由](/channels/channel-routing) — 消息的会话路由
- [安全](/gateway/security) — 访问模型和加固