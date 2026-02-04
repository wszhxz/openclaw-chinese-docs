---

summary: "Browser-based control UI for the Gateway (chat, nodes, config)"
read_when:
  - You want to operate the Gateway from a browser
  - You want Tailnet access without SSH tunnels
title: "Control UI"

---
# 控制UI（浏览器）

控制UI是一个小型的 **Vite + Lit** 单页应用，由网关提供服务：

- 默认地址：`http://<host>:18789/`
- 可选前缀：设置 `gateway.controlUi.basePath`（例如 `/openclaw`）

它通过与网关WebSocket在同一端口进行直接通信。

## 快速打开（本地）

如果网关运行在同一台计算机上，打开：

- http://127.0.0.1:18789/（或 http://localhost:18789/）

如果页面无法加载，请先启动网关：`openclaw gateway`。

认证信息通过WebSocket握手期间提供：

- `connect.params.auth.token`
- `connect.params.auth.password`
  控制台设置面板允许您存储令牌；密码不会被持久化。
  入门向导默认生成网关令牌，因此首次连接时请将令牌粘贴在此处。

## 设备配对（首次连接）

当您从新浏览器或设备连接到控制UI时，网关
需要 **一次性配对授权** —— 即使您在与 `gateway.auth.allowTailscale: true` 的同一Tailnet中。这是为了防止未经授权访问的安全措施。

**您将看到：** "disconnected (1008): 需要配对"

**授权设备：**

```bash
# List pending requests
openclaw devices list

# Approve by request ID
openclaw devices approve <requestId>
```

授权后，设备将被记住，除非您使用 `openclaw devices revoke --device <id> --role <role>` 撤销授权，否则无需重新授权。有关令牌轮换和撤销，请参见
[设备CLI](/cli/devices)。

**注意事项：**

- 本地连接（`127.0.0.1`）会自动授权。
- 远程连接（LAN、Tailnet等）需要显式授权。
- 每个浏览器配置文件生成唯一的设备ID，因此切换浏览器或清除浏览器数据将需要重新配对。

## 当前功能

- 通过网关WS与模型聊天（`chat.history`、`chat.send`、`chat.abort`、`chat.inject`）
- 在聊天中流式传输工具调用 + 实时工具输出卡片（代理事件）
- 通道：WhatsApp/Telegram/Discord/Slack + 插件通道（Mattermost等）状态 + QR登录 + 每个通道配置（`channels.status`、`web.login.*`、`config.patch`）
- 实例：在线列表 + 刷新（`system-presence`）
- 会话：列表 + 每个会话的思考/详细模式覆盖（`sessions.list`、`sessions.patch`）
- 定时任务：列表/添加/运行/启用/禁用 + 运行历史（`cron.*`）
- 技能：状态、启用/禁用、安装、API密钥更新（`skills.*`）
- 节点：列表 + 功能（`node.list`）
- 执行授权：编辑网关或节点白名单 + 查询 `exec host=gateway/node` 的策略（`exec.approvals.*`）
- 配置：查看/编辑 `~/.openclaw/openclaw.json`（`config.get`、`config.set`）
- 配置：应用 + 通过验证重启（`config.apply`）并唤醒最后一个活跃会话
- 配置写入包含基础哈希保护以防止并发编辑覆盖
- 配置模式 + 表单渲染（`config.schema`，包括插件 + 通道模式）；原始JSON编辑器仍可用
- 调试：状态/健康/模型快照 + 事件日志 + 手动RPC调用（`status`、`health`、`models.list`）
- 日志：带过滤/导出功能的网关文件日志实时尾随（`logs.tail`）
- 更新：运行包/ git 更新 + 重启（`update.run`）并生成重启报告

## 聊天行为

- `chat.send` 是 **非阻塞**：它会立即通过 `{ runId, status: "started" }` 返回确认，并通过 `chat` 事件流式传输响应。
- 使用相同的 `idempotencyKey` 重新发送时，运行中返回 `{ status: "in_flight" }`，完成后返回 `{ status: "ok" }`。
- `chat.inject` 会向会话记录添加助手注释，并广播 `chat` 事件用于UI-only更新（无代理运行，无通道分发）。
- 停止：
  - 点击 **停止**（调用 `chat.abort`）
  - 输入 `/stop`（或 `stop|esc|abort|wait|exit|interrupt`）中止非绑定操作
  - `chat.abort` 支持 `{ sessionKey }`（无 `runId`）中止该会话的所有活跃运行

## Tailnet访问（推荐）

### 集成Tailscale Serve（首选）

保持网关在环回地址，并让Tailscale Serve通过HTTPS代理它：

```bash
openclaw gateway --tailscale serve
```

打开：

- `https://<magicdns>/`（或您配置的 `gateway.controlUi.basePath`）

默认情况下，Serve请求可以通过Tailscale身份头（`tailscale-user-login`）进行身份验证，当 `gateway.auth.allowTailscale` 是 `true` 时。OpenClaw 通过解析 `x-forwarded-for` 地址与 `tailscale whois` 匹配头来验证身份，并且仅在请求通过Tailscale的 `x-forwarded-*` 头到达环回时接受这些请求。如果您希望即使对Serve流量也要求令牌/密码，请设置 `gateway.auth.allowTailscale: false`（或强制 `gateway.auth.mode: "password"`）。

### 绑定到tailnet + 令牌

```bash
openclaw gateway --bind tailnet --token "$(openssl rand -hex 32)"
```

然后打开：

- `http://<tailscale-ip>:18789/`（或您配置的 `gateway.controlUi.basePath`）

将令牌粘贴到UI设置中（以 `connect.params.auth.token` 发送）。

## 不安全HTTP

如果您通过普通HTTP（`http://<lan-ip>` 或 `http://<tailscale-ip>`）打开仪表板，浏览器将在 **非安全上下文中运行** 并阻止WebCrypto。默认情况下，OpenClaw **阻止** 没有设备身份的控制UI连接。

**推荐修复：** 使用HTTPS（Tailscale Serve）或本地打开UI：

- `https://<magicdns>/`（Serve）
- `http://127.0.0.1:18789/`（在网关主机上）

**降级示例（仅HTTP令牌）：**

```json5
{
  gateway: {
    controlUi: { allowInsecureAuth: true },
    bind: "tailnet",
    auth: { mode: "token", token: "replace-me" },
  },
}
```

这会禁用控制UI的设备身份 + 配对（即使在HTTPS上）。仅在您信任网络时使用。

## 构建UI

## 调试测试