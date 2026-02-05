---
summary: "Browser-based control UI for the Gateway (chat, nodes, config)"
read_when:
  - You want to operate the Gateway from a browser
  - You want Tailnet access without SSH tunnels
title: "Control UI"
---
# 控制UI（浏览器）

控制UI是一个由Gateway提供的小型 **Vite + Lit** 单页应用：

- 默认：`http://<host>:18789/`
- 可选前缀：设置 `gateway.controlUi.basePath`（例如 `/openclaw`）

它通过**直接与Gateway WebSocket**在相同端口通信。

## 快速打开（本地）

如果Gateway在同一台计算机上运行，打开：

- http://127.0.0.1:18789/（或 http://localhost:18789/）

如果页面无法加载，请先启动Gateway：`openclaw gateway`。

认证信息通过WebSocket握手提供：

- `connect.params.auth.token`
- `connect.params.auth.password`
  仪表盘设置面板允许你存储一个令牌；密码不会被持久化。
  入门向导默认会生成一个网关令牌，因此首次连接时将其粘贴在这里。

## 设备配对（首次连接）

当你从新的浏览器或设备连接到控制UI时，Gateway需要进行**一次性配对批准**——即使你在同一个Tailnet中与`gateway.auth.allowTailscale: true`。这是一种安全措施，以防止未经授权的访问。

**你会看到：**“断开连接 (1008): 需要配对”

**要批准设备：**

```bash
# List pending requests
openclaw devices list

# Approve by request ID
openclaw devices approve <requestId>
```

一旦批准，设备会被记住，除非你使用`openclaw devices revoke --device <id> --role <role>`撤销批准。有关令牌轮换和撤销的信息，请参阅[设备CLI](/cli/devices)。

**注意事项：**

- 本地连接(`127.0.0.1`)会自动批准。
- 远程连接（LAN、Tailnet等）需要显式批准。
- 每个浏览器配置文件都会生成唯一的设备ID，因此切换浏览器或清除浏览器数据将需要重新配对。

## 它能做什么（今天）

- 通过Gateway WS与模型聊天 (`chat.history`, `chat.send`, `chat.abort`, `chat.inject`)
- 在聊天中流式传输工具调用+实时工具输出卡片（代理事件）
- 通道：WhatsApp/Telegram/Discord/Slack + 插件通道（Mattermost等）状态 + QR登录 + 按通道配置 (`channels.status`, `web.login.*`, `config.patch`)
- 实例：在线列表 + 刷新 (`system-presence`)
- 会话：列表 + 按会话的思考/详细覆盖 (`sessions.list`, `sessions.patch`)
- 计划任务：列表/添加/运行/启用/禁用 + 运行历史 (`cron.*`)
- 技能：状态、启用/禁用、安装、API密钥更新 (`skills.*`)
- 节点：列表 + 功能 (`node.list`)
- 执行批准：编辑网关或节点白名单 + 请求策略 `exec host=gateway/node` (`exec.approvals.*`)
- 配置：查看/编辑 `~/.openclaw/openclaw.json` (`config.get`, `config.set`)
- 配置：应用 + 带验证重启 (`config.apply`) 并唤醒最后活动的会话
- 配置写入包含基础哈希保护，以防止并发编辑冲突
- 配置架构 + 表单渲染 (`config.schema`，包括插件 + 通道架构）；原始JSON编辑器仍然可用
- 调试：状态/健康/模型快照 + 事件日志 + 手动RPC调用 (`status`, `health`, `models.list`)
- 日志：网关文件日志的实时跟踪带过滤/导出 (`logs.tail`)
- 更新：运行包/git更新 + 重启 (`update.run`) 并生成重启报告

## 聊天行为

- `chat.send` 是**非阻塞**的：它立即确认`{ runId, status: "started" }`并通过`chat`事件流式传输响应。
- 使用相同的`idempotencyKey`重新发送时，在运行中返回`{ status: "in_flight" }`，完成后返回`{ status: "ok" }`。
- `chat.inject` 将助手注释附加到会话记录，并广播一个`chat`事件以仅更新UI（无代理运行，无通道传递）。
- 停止：
  - 点击**停止**（调用`chat.abort`）
  - 输入`/stop`（或`stop|esc|abort|wait|exit|interrupt`）以中止带外操作
  - `chat.abort` 支持`{ sessionKey }`（无`runId`）以中止该会话的所有活动运行

## Tailnet访问（推荐）

### 集成Tailscale Serve（首选）

将Gateway保留在回环接口，并让Tailscale Serve通过HTTPS代理它：

```bash
openclaw gateway --tailscale serve
```

打开：

- `https://<magicdns>/`（或你配置的`gateway.controlUi.basePath`）

默认情况下，当`gateway.auth.allowTailscale`为`true`时，Serve请求可以通过Tailscale身份头(`tailscale-user-login`)进行身份验证。OpenClaw通过解析`x-forwarded-for`地址并使用`tailscale whois`与头部匹配来验证身份，并且只接受带有Tailscale的`x-forwarded-*`头部的回环请求。如果你希望即使是Serve流量也要求令牌/密码，请设置`gateway.auth.allowTailscale: false`（或强制`gateway.auth.mode: "password"`）。

### 绑定到tailnet + 令牌

```bash
openclaw gateway --bind tailnet --token "$(openssl rand -hex 32)"
```

然后打开：

- `http://<tailscale-ip>:18789/`（或你配置的`gateway.controlUi.basePath`）

将令牌粘贴到UI设置中（作为`connect.params.auth.token`发送）。

## 不安全的HTTP

如果你通过纯HTTP打开仪表盘 (`http://<lan-ip>` 或 `http://<tailscale-ip>`)，浏览器将在**非安全上下文**下运行并阻止WebCrypto。默认情况下，OpenClaw会**阻止**没有设备身份的控制UI连接。

**推荐修复方法：** 使用HTTPS（Tailscale Serve）或本地打开UI：

- `https://<magicdns>/`（Serve）
- `http://127.0.0.1:18789/`（在网关主机上）

**降级示例（仅通过HTTP使用令牌）：**

```json5
{
  gateway: {
    controlUi: { allowInsecureAuth: true },
    bind: "tailnet",
    auth: { mode: "token", token: "replace-me" },
  },
}
```

这会禁用控制UI的设备身份+配对（即使在HTTPS上也是如此）。仅在你信任网络时使用。

有关HTTPS设置指导，请参阅[Tailscale](/gateway/tailscale)。

## 构建UI

网关从`dist/control-ui`提供静态文件。使用以下命令构建它们：

```bash
pnpm ui:build # auto-installs UI deps on first run
```

可选的绝对基础（当你需要固定的资源URL时）：

```bash
OPENCLAW_CONTROL_UI_BASE_PATH=/openclaw/ pnpm ui:build
```

用于本地开发（单独的开发服务器）：

```bash
pnpm ui:dev # auto-installs UI deps on first run
```

然后将UI指向你的网关WS URL（例如 `ws://127.0.0.1:18789`）。

## 调试/测试：开发服务器 + 远程网关

控制UI是静态文件；WebSocket目标是可配置的，可以与HTTP来源不同。当你希望本地使用Vite开发服务器但网关运行在其他地方时，这非常有用。

1. 启动UI开发服务器：`pnpm ui:dev`
2. 打开一个URL，例如：

```text
http://localhost:5173/?gatewayUrl=ws://<gateway-host>:18789
```

可选的一次性认证（如果需要）：

```text
http://localhost:5173/?gatewayUrl=wss://<gateway-host>:18789&token=<gateway-token>
```

注意事项：

- `gatewayUrl` 在加载后存储在localStorage中，并从URL中移除。
- `token` 存储在localStorage中；`password` 仅保留在内存中。
- 当网关位于TLS后面（Tailscale Serve、HTTPS代理等）时使用`wss://`。
- `gatewayUrl` 仅在顶级窗口（不是嵌入的）中接受，以防止点击劫持。
- 对于跨域开发设置（例如从`pnpm ui:dev`到远程网关），将UI来源添加到`gateway.controlUi.allowedOrigins`。

示例：

```json5
{
  gateway: {
    controlUi: {
      allowedOrigins: ["http://localhost:5173"],
    },
  },
}
```

远程访问设置详情：[远程访问](/gateway/remote)。