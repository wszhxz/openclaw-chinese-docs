---
summary: "Browser-based control UI for the Gateway (chat, nodes, config)"
read_when:
  - You want to operate the Gateway from a browser
  - You want Tailnet access without SSH tunnels
title: "Control UI"
---
# 控制UI（浏览器）

控制UI是一个由网关提供服务的小型**Vite + Lit**单页应用程序：

- 默认：`http://<host>:18789/`
- 可选前缀：设置`gateway.controlUi.basePath`（例如`/openclaw`）

它通过同一端口直接与网关WebSocket通信。

## 快速打开（本地）

如果网关在同一台计算机上运行，请打开：

- http://127.0.0.1:18789/（或http://localhost:18789/）

如果页面加载失败，请先启动网关：`openclaw gateway`。

认证在WebSocket握手期间通过以下方式提供：

- `connect.params.auth.token`
- `connect.params.auth.password`
  仪表板设置面板允许您存储令牌；密码不会被持久化。
  入门向导默认生成网关令牌，因此首次连接时请在此处粘贴。

## 设备配对（首次连接）

当您从新的浏览器或设备连接到控制UI时，网关需要**一次性配对批准**——即使您在同一个Tailnet中使用`gateway.auth.allowTailscale: true`也是如此。这是为了防止未授权访问的安全措施。

**您将看到：**"disconnected (1008): pairing required"

**批准设备的方法：**

```bash
# List pending requests
openclaw devices list

# Approve by request ID
openclaw devices approve <requestId>
```

一旦批准，设备将被记住，除非您使用`openclaw devices revoke --device <id> --role <role>`撤销，否则不需要重新批准。请参阅[设备CLI](/cli/devices)了解令牌轮换和撤销。

**注意事项：**

- 本地连接（`127.0.0.1`）会自动批准。
- 远程连接（局域网、Tailnet等）需要明确批准。
- 每个浏览器配置文件生成一个唯一的设备ID，因此切换浏览器或清除浏览器数据将需要重新配对。

## 功能说明（当前）

- 通过网关WS与模型聊天（`chat.history`、`chat.send`、`chat.abort`、`chat.inject`）
- 在聊天中流式传输工具调用+实时工具输出卡片（代理事件）
- 频道：WhatsApp/Telegram/Discord/Slack + 插件频道（Mattermost等）状态+二维码登录+每个频道配置（`channels.status`、`web.login.*`、`config.patch`）
- 实例：存在列表+刷新（`system-presence`）
- 会话：列表+每个会话的思考/详细覆盖（`sessions.list`、`sessions.patch`）
- 定时任务：列表/添加/运行/启用/禁用+运行历史（`cron.*`）
- 技能：状态、启用/禁用、安装、API密钥更新（`skills.*`）
- 节点：列表+功能（`node.list`）
- 执行批准：编辑网关或节点白名单+为`exec host=gateway/node`询问策略（`exec.approvals.*`）
- 配置：查看/编辑`~/.openclaw/openclaw.json`（`config.get`、`config.set`）
- 配置：应用+带验证的重启（`config.apply`）并唤醒最后活跃的会话
- 配置写入包含基础哈希保护以防止并发编辑冲突
- 配置模式+表单渲染（`config.schema`，包括插件+频道模式）；原始JSON编辑器仍然可用
- 调试：状态/健康/模型快照+事件日志+手动RPC调用（`status`、`health`、`models.list`）
- 日志：网关文件日志的实时尾部显示，带有过滤/导出功能（`logs.tail`）
- 更新：运行包/git更新+重启（`update.run`）并附带重启报告

定时任务面板说明：

- 对于隔离任务，交付默认为宣布摘要。如果您希望仅内部运行，可以切换为无。
- 选择宣布时，频道/目标字段会出现。

## 聊天行为

- `chat.send`是**非阻塞的**：立即使用`{ runId, status: "started" }`确认，响应通过`chat`事件流式传输。
- 使用相同的`idempotencyKey`重新发送会在运行时返回`{ status: "in_flight" }`，完成后返回`{ status: "ok" }`。
- `chat.inject`将助手注释附加到会话记录，并广播`chat`事件用于仅UI更新（无代理运行，无频道交付）。
- 停止：
  - 点击**停止**（调用`chat.abort`）
  - 输入`/stop`（或`stop|esc|abort|wait|exit|interrupt`）以带外中止
  - `chat.abort`支持`{ sessionKey }`（无`runId`）以中止该会话的所有活动运行

## Tailnet访问（推荐）

### 集成Tailscale Serve（首选）

让网关保持在回环地址，让Tailscale Serve使用HTTPS代理：

```bash
openclaw gateway --tailscale serve
```

打开：

- `https://<magicdns>/`（或您配置的`gateway.controlUi.basePath`）

默认情况下，当`gateway.auth.allowTailscale`为`true`时，Serve请求可以通过Tailscale身份头（`tailscale-user-login`）进行认证。OpenClaw通过使用`tailscale whois`解析`x-forwarded-for`地址并将其与头信息匹配来验证身份，仅当请求通过Tailscale的`x-forwarded-*`头命中回环地址时才接受这些请求。如果您希望即使是Serve流量也要求令牌/密码，请设置`gateway.auth.allowTailscale: false`（或强制`gateway.auth.mode: "password"`）。

### 绑定到tailnet + 令牌

```bash
openclaw gateway --bind tailnet --token "$(openssl rand -hex 32)"
```

然后打开：

- `http://<tailscale-ip>:18789/`（或您配置的`gateway.controlUi.basePath`）

将令牌粘贴到UI设置中（作为`connect.params.auth.token`发送）。

## 不安全HTTP

如果您通过纯HTTP（`http://<lan-ip>`或`http://<tailscale-ip>`）打开仪表板，浏览器将在**非安全上下文**中运行并阻止WebCrypto。默认情况下，OpenClaw在没有设备身份的情况下**阻止**控制UI连接。

**推荐修复：**使用HTTPS（Tailscale Serve）或在本地打开UI：

- `https://<magicdns>/`（Serve）
- `http://127.0.0.1:18789/`（在网关主机上）

**降级示例（HTTP上的仅令牌）：**

```json5
{
  gateway: {
    controlUi: { allowInsecureAuth: true },
    bind: "tailnet",
    auth: { mode: "token", token: "replace-me" },
  },
}
```

这将禁用控制UI的设备身份+配对（即使在HTTPS上）。仅当您信任网络时才使用。

有关HTTPS设置指南，请参阅[Tailscale](/gateway/tailscale)。

## 构建UI

网关从`dist/control-ui`提供静态文件。使用以下命令构建：

```bash
pnpm ui:build # auto-installs UI deps on first run
```

可选绝对基础（当您需要固定资源URL时）：

```bash
OPENCLAW_CONTROL_UI_BASE_PATH=/openclaw/ pnpm ui:build
```

用于本地开发（单独的开发服务器）：

```bash
pnpm ui:dev # auto-installs UI deps on first run
```

然后将UI指向您的网关WS URL（例如`ws://127.0.0.1:18789`）。

## 调试/测试：开发服务器+远程网关

控制UI是静态文件；WebSocket目标是可配置的，可以与HTTP来源不同。当您希望本地有Vite开发服务器但网关在其他地方运行时，这很有用。

1. 启动UI开发服务器：`pnpm ui:dev`
2. 打开类似这样的URL：

```text
http://localhost:5173/?gatewayUrl=ws://<gateway-host>:18789
```

可选一次性认证（如需要）：

```text
http://localhost:5173/?gatewayUrl=wss://<gateway-host>:18789&token=<gateway-token>
```

注意事项：

- `gatewayUrl`在加载后存储在localStorage中并从URL中移除。
- `token`存储在localStorage中；`password`仅保留在内存中。
- 当设置`gatewayUrl`时，UI不会回退到配置或环境凭据。
  明确提供`token`（或`password`）。缺少明确凭据是错误。
- 当网关位于TLS后面时（Tailscale Serve、HTTPS代理等），使用`wss://`。
- `gatewayUrl`仅在顶级窗口（非嵌入式）中接受，以防止点击劫持。
- 对于跨源开发设置（例如`pnpm ui:dev`到远程网关），将UI来源添加到`gateway.controlUi.allowedOrigins`。

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