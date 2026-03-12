---
summary: "Google Chat app support status, capabilities, and configuration"
read_when:
  - Working on Google Chat channel features
title: "Google Chat"
---
# Google Chat（Chat API）

状态：已准备好通过 Google Chat API Webhook（仅限 HTTP）接收直接消息（DM）和群组空间消息。

## 快速配置（新手向）

1. 创建一个 Google Cloud 项目并启用 **Google Chat API**。
   - 访问地址：[Google Chat API 凭据页面](https://console.cloud.google.com/apis/api/chat.googleapis.com/credentials)
   - 如果尚未启用，请启用该 API。
2. 创建一个 **服务账号（Service Account）**：
   - 点击 **创建凭据** > **服务账号**。
   - 为其命名（例如：`openclaw-chat`）。
   - 权限留空（点击 **继续**）。
   - 授权主体（principals）留空（点击 **完成**）。
3. 创建并下载 **JSON 密钥文件**：
   - 在服务账号列表中，点击刚刚创建的服务账号。
   - 切换到 **密钥（Keys）** 标签页。
   - 点击 **添加密钥** > **创建新密钥**。
   - 选择 **JSON** 格式，然后点击 **创建**。
4. 将下载的 JSON 文件保存至您的网关主机（例如：`~/.openclaw/googlechat-service-account.json`）。
5. 在 [Google Cloud Console Chat 配置页面](https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat) 中创建一个 Google Chat 应用：
   - 填写 **应用信息（Application info）**：
     - **应用名称（App name）**：（例如：`OpenClaw`）
     - **头像 URL（Avatar URL）**：（例如：`https://openclaw.ai/logo.png`）
     - **描述（Description）**：（例如：`Personal AI Assistant`）
   - 启用 **交互功能（Interactive features）**。
   - 在 **功能（Functionality）** 下勾选 **加入群组空间及群聊（Join spaces and group conversations）**。
   - 在 **连接设置（Connection settings）** 下选择 **HTTP 终端 URL（HTTP endpoint URL）**。
   - 在 **触发器（Triggers）** 下选择 **为所有触发器使用同一 HTTP 终端 URL（Use a common HTTP endpoint URL for all triggers）**，并将其设为您网关的公网 URL 后接 `/googlechat`。
     - _提示：运行 `openclaw status` 可获取您网关的公网 URL。_
   - 在 **可见性（Visibility）** 下勾选 **向 &lt;您的域名&gt; 中特定人员和群组提供此 Chat 应用（Make this Chat app available to specific people and groups in &lt;Your Domain&gt;）**。
   - 在文本框中输入您的邮箱地址（例如：`user@example.com`）。
   - 点击底部的 **保存（Save）**。
6. **启用应用状态（Enable the app status）**：
   - 保存后，请**刷新页面**。
   - 查找 **应用状态（App status）** 区域（通常位于保存后的页面顶部或底部）。
   - 将状态更改为 **上线 — 对用户可用（Live - available to users）**。
   - 再次点击 **保存（Save）**。
7. 使用服务账号路径 + Webhook 受众（audience）配置 OpenClaw：
   - 环境变量：`GOOGLE_CHAT_SERVICE_ACCOUNT_FILE=/path/to/service-account.json`
   - 或配置项：`channels.googlechat.serviceAccountFile: "/path/to/service-account.json"`。
8. 设置 Webhook 受众类型（audience type）及其值（需与您的 Chat 应用配置一致）。
9. 启动网关。Google Chat 将向您的 Webhook 路径发起 POST 请求。

## 添加至 Google Chat

当网关正在运行且您的邮箱已添加至可见性列表后：

1. 访问 [Google Chat](https://chat.google.com/)。
2. 在 **直接消息（Direct Messages）** 旁点击 **+**（加号）图标。
3. 在搜索栏（通常用于添加人员的位置）中输入您在 Google Cloud Console 中配置的 **应用名称（App name）**。
   - **注意**：该机器人**不会**出现在“应用市场（Marketplace）”浏览列表中，因为它是一个私有应用。您必须通过名称精确搜索。
4. 从搜索结果中选择您的机器人。
5. 点击 **添加（Add）** 或 **聊天（Chat）** 以启动一对一私聊。
6. 发送 “Hello” 触发助手！

## 公网 URL（仅限 Webhook）

Google Chat Webhook 要求一个公网 HTTPS 终端。出于安全考虑，**仅将 `/googlechat` 路径暴露于互联网**。请将 OpenClaw 控制台及其他敏感终端保留在您的私有网络内。

### 方案 A：Tailscale Funnel（推荐）

对私有控制台使用 Tailscale Serve，对公网 Webhook 路径使用 Funnel。这样可确保 `/` 保持私有，而仅暴露 `/googlechat`。

1. **检查网关绑定的地址：**

   ```bash
   ss -tlnp | grep 18789
   ```

   记下 IP 地址（例如：`127.0.0.1`、`0.0.0.0`，或类似 `100.x.x.x` 的 Tailscale IP）。

2. **仅向 tailnet 暴露控制台（端口 8443）：**

   ```bash
   # If bound to localhost (127.0.0.1 or 0.0.0.0):
   tailscale serve --bg --https 8443 http://127.0.0.1:18789

   # If bound to Tailscale IP only (e.g., 100.106.161.80):
   tailscale serve --bg --https 8443 http://100.106.161.80:18789
   ```

3. **仅将 Webhook 路径公开暴露：**

   ```bash
   # If bound to localhost (127.0.0.1 or 0.0.0.0):
   tailscale funnel --bg --set-path /googlechat http://127.0.0.1:18789/googlechat

   # If bound to Tailscale IP only (e.g., 100.106.161.80):
   tailscale funnel --bg --set-path /googlechat http://100.106.161.80:18789/googlechat
   ```

4. **授权节点访问 Funnel：**  
   若出现提示，请访问输出中显示的授权 URL，以在您的 tailnet 策略中为此节点启用 Funnel。

5. **验证配置：**

   ```bash
   tailscale serve status
   tailscale funnel status
   ```

您的公网 Webhook URL 将是：  
`https://<node-name>.<tailnet>.ts.net/googlechat`

您的私有控制台仍仅限 tailnet 访问：  
`https://<node-name>.<tailnet>.ts.net:8443/`

在 Google Chat 应用配置中，请使用不含 `:8443` 的公网 URL。

> 注意：此配置在重启后仍然有效。如需后续移除，请运行 `tailscale funnel reset` 和 `tailscale serve reset`。

### 方案 B：反向代理（Caddy）

若您使用 Caddy 等反向代理，请仅代理指定路径：

```caddy
your-domain.com {
    reverse_proxy /googlechat* localhost:18789
}
```

在此配置下，任何对 `your-domain.com/` 的请求将被忽略或返回 404，而 `your-domain.com/googlechat` 将被安全地路由至 OpenClaw。

### 方案 C：Cloudflare Tunnel

配置隧道的入口规则，仅路由 Webhook 路径：

- **路径（Path）**：`/googlechat` → `http://localhost:18789/googlechat`
- **默认规则（Default Rule）**：HTTP 404（未找到）

## 工作原理

1. Google Chat 向网关发送 Webhook POST 请求。每个请求均包含一个 `Authorization: Bearer <token>` 请求头。
   - 当存在该请求头时，OpenClaw 会在读取/解析完整 Webhook 请求体前先验证 Bearer 认证。
   - 支持携带 `authorizationEventObject.systemIdToken` 字段的 Google Workspace 插件请求，采用更严格的预认证请求体大小限制。
2. OpenClaw 使用配置的 `audienceType` + `audience` 验证令牌：
   - `audienceType: "app-url"` → 受众（audience）为您的 HTTPS Webhook URL。
   - `audienceType: "project-number"` → 受众（audience）为 Cloud 项目编号。
3. 消息按空间（space）路由：
   - 直接消息（DM）使用会话密钥 `agent:<agentId>:googlechat:dm:<spaceId>`。
   - 群组空间（Spaces）使用会话密钥 `agent:<agentId>:googlechat:group:<spaceId>`。
4. DM 默认采用配对机制。未知发送者将收到配对码；请使用以下命令批准：
   - `openclaw pairing approve googlechat <code>`
5. 群组空间默认要求 @ 提及（@-mention）。若提及检测需依赖应用用户名，请使用 `botUser`。

## 目标标识符（Targets）

使用以下标识符进行消息投递和白名单设置：

- 直接消息（Direct messages）：`users/<userId>`（推荐）。
- 原始邮箱地址 `name@example.com` 是可变的，仅在 `channels.googlechat.dangerouslyAllowNameMatching: true` 时用于直接白名单匹配。
- 已弃用：`users/<email>` 被视为用户 ID，而非邮箱白名单。
- 群组空间（Spaces）：`spaces/<spaceId>`。

## 配置要点

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

说明：

- 服务账号凭据也可以内联方式传入，使用 `serviceAccount`（JSON 字符串）。
- `serviceAccountRef` 同样受支持（环境变量/文件 SecretRef），包括在 `channels.googlechat.accounts.<id>.serviceAccountRef` 下的每账号引用。
- 若未设置 `webhookPath`，默认 Webhook 路径为 `/googlechat`。
- `dangerouslyAllowNameMatching` 重新启用白名单中可变邮箱主体匹配（应急兼容模式）。
- 表情反应（Reactions）可通过 `reactions` 工具和 `channels action` 实现，前提是启用了 `actions.reactions`。
- `typingIndicator` 支持 `none`、`message`（默认）和 `reaction`（表情反应需用户 OAuth 授权）。
- 附件通过 Chat API 下载，并存入媒体处理流水线（大小上限由 `mediaMaxMb` 控制）。

密钥引用详情参见：[密钥管理（Secrets Management）](/gateway/secrets)。

## 故障排查

### 405 Method Not Allowed（不支持的方法）

若 Google Cloud 日志浏览器中显示如下错误：

```
status code: 405, reason phrase: HTTP error response: HTTP/1.1 405 Method Not Allowed
```

表示 Webhook 处理器未注册。常见原因如下：

1. **频道未配置**：您的配置中缺少 `channels.googlechat` 区块。请通过以下命令验证：

   ```bash
   openclaw config get channels.googlechat
   ```

   若返回 “Config path not found”，请添加相应配置（参见 [配置要点](#config-highlights)）。

2. **插件未启用**：检查插件状态：

   ```bash
   openclaw plugins list | grep googlechat
   ```

   若显示 “disabled”，请在配置中添加 `plugins.entries.googlechat.enabled: true`。

3. **网关未重启**：添加配置后，请重启网关：

   ```bash
   openclaw gateway restart
   ```

验证频道是否已运行：

```bash
openclaw channels status
# Should show: Google Chat default: enabled, configured, ...
```

### 其他问题

- 检查 `openclaw channels status --probe` 是否存在身份验证错误或缺少受众配置。
- 如果未收到任何消息，请确认聊天应用的 Webhook URL 及事件订阅设置。
- 如果提及限制（mention gating）阻止了回复，请将 `botUser` 设置为该应用的用户资源名称，并验证 `requireMention`。
- 在发送测试消息时使用 `openclaw logs --follow`，以确认请求是否已到达网关。

相关文档：

- [网关配置](/gateway/configuration)
- [安全性](/gateway/security)
- [回复反应](/tools/reactions)