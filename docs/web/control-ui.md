---
summary: "Browser-based control UI for the Gateway (chat, nodes, config)"
read_when:
  - You want to operate the Gateway from a browser
  - You want Tailnet access without SSH tunnels
title: "Control UI"
---
# 控制界面（浏览器）

控制界面是一个由网关提供的小型**Vite + Lit**单页应用程序：

- 默认：`http://<host>:18789/`
- 可选前缀：设置`gateway.controlUi.basePath`（例如`/openclaw`）

它直接与同一端口上的网关WebSocket通信。

## 快速打开（本地）

如果网关在同一台计算机上运行，请打开：

- [http://127.0.0.1:18789/](http://127.0.0.1:18789/)（或[http://localhost:18789/](http://localhost:18789/)）

如果页面加载失败，请先启动网关：`openclaw gateway`。

认证在WebSocket握手期间通过以下方式提供：

- `connect.params.auth.token`
- `connect.params.auth.password`
  仪表板设置面板允许您存储令牌；密码不会被持久化。
  入门向导默认生成一个网关令牌，因此首次连接时请在此处粘贴。

## 设备配对（首次连接）

当您从新的浏览器或设备连接到控制界面时，即使您处于同一个Tailnet中，网关也要求进行**一次性配对批准**。这是为了防止未经授权的访问的安全措施。

**您将看到的内容：** "disconnected (1008): pairing required"

**要批准设备：**

```bash
# List pending requests
openclaw devices list

# Approve by request ID
openclaw devices approve <requestId>
```

一旦批准，该设备将被记住，并且除非您使用`openclaw devices revoke --device <id> --role <role>`撤销，否则不需要重新批准。有关令牌轮换和撤销的信息，请参阅[设备CLI](/cli/devices)。

**注意事项：**

- 本地连接（`127.0.0.1`）自动批准。
- 远程连接（局域网、Tailnet等）需要显式批准。
- 每个浏览器配置文件生成唯一的设备ID，因此切换浏览器或清除浏览器数据将需要重新配对。

## 语言支持

控制界面可以根据您的浏览器区域设置在首次加载时本地化，并且您可以从访问卡的语言选择器中稍后覆盖它。

- 支持的区域设置：`en`, `zh-CN`, `zh-TW`, `pt-BR`, `de`, `es`
- 非英语翻译在浏览器中延迟加载。
- 选定的区域设置保存在浏览器存储中，并在未来的访问中重用。
- 缺失的翻译键回退到英语。

## 它可以做什么（当前）

- 通过网关WS与模型聊天（`chat.history`, `chat.send`, `chat.abort`, `chat.inject`）
- 在聊天中流式传输工具调用+实时工具输出卡片（代理事件）
- 通道：WhatsApp/Telegram/Discord/Slack+插件通道（Mattermost等）状态+二维码登录+每通道配置（`channels.status`, `web.login.*`, `config.patch`）
- 实例：存在列表+刷新（`system-presence`）
- 会话：列表+每个会话的思考/详细覆盖（`sessions.list`, `sessions.patch`）
- 计划任务：列表/添加/编辑/运行/启用/禁用+运行历史（`cron.*`）
- 技能：状态、启用/禁用、安装、API密钥更新（`skills.*`）
- 节点：列表+功能（`node.list`）
- 执行批准：编辑网关或节点允许列表+询问策略以获取`exec host=gateway/node`（`exec.approvals.*`）
- 配置：查看/编辑`~/.openclaw/openclaw.json`（`config.get`, `config.set`）
- 配置：应用+验证重启（`config.apply`）并唤醒最后活动的会话
- 配置写入包括基础哈希保护以防止并发编辑冲突
- 配置模式+表单渲染（`config.schema`，包括插件+通道模式）；原始JSON编辑器仍然可用
- 调试：状态/健康/模型快照+事件日志+手动RPC调用（`status`, `health`, `models.list`）
- 日志：带有过滤/导出的网关文件日志实时尾随（`logs.tail`）
- 更新：运行包/ git更新+重启（`update.run`）并附带重启报告

计划任务面板说明：

- 对于隔离的任务，默认交付为宣布摘要。如果您希望仅内部运行，可以切换到无。
- 当选择宣布时，会出现频道/目标字段。
- Webhook模式使用`delivery.mode = "webhook"`并将`delivery.to`设置为有效的HTTP(S) webhook URL。
- 对于主会话任务，Webhook和无交付模式可用。
- 高级编辑控件包括运行后删除、清除代理覆盖、cron精确/交错选项、代理模型/思考覆盖以及尽力而为的交付切换。
- 表单验证是内联的，具有字段级别的错误；无效值将禁用保存按钮直到修复。
- 设置`cron.webhookToken`以发送专用承载令牌，如果省略则不带身份验证头发送webhook。
- 废弃的回退：存储的旧版任务仍可使用`notify: true`直到迁移。

## 聊天行为

- `chat.send` 是**非阻塞**的：它立即通过`{ runId, status: "started" }`确认，并通过`chat`事件流式传输响应。
- 使用相同的`idempotencyKey`重新发送时，在运行过程中返回`{ status: "in_flight" }`，完成后返回`{ status: "ok" }`。
- `chat.history`响应大小受UI安全限制。当转录条目太大时，网关可能会截断长文本字段，省略大量元数据块，并用占位符(`[chat.history omitted: message too large]`)替换过大的消息。
- `chat.inject`向会话转录附加助手注释，并广播`chat`事件用于仅UI更新（无代理运行，无频道传递）。
- 停止：
  - 单击**停止**（调用`chat.abort`）
  - 输入`/stop`（或独立的中止短语如`stop`, `stop action`, `stop run`, `stop openclaw`, `please stop`）以带外中止
  - `chat.abort`支持`{ sessionKey }`（无`runId`）以中止该会话的所有活动运行
- 中止部分保留：
  - 当运行被中止时，部分助手文本仍可以在UI中显示
  - 当缓冲输出存在时，网关将中止的部分助手文本持久化到转录历史中
  - 持久化的条目包含中止元数据，以便转录消费者可以区分中止部分和正常完成输出

## Tailnet访问（推荐）

### 集成Tailscale Serve（首选）

保持网关在环回地址上，并让Tailscale Serve通过HTTPS代理它：

```bash
openclaw gateway --tailscale serve
```

打开：

- `https://<magicdns>/`（或您配置的`gateway.controlUi.basePath`）

默认情况下，当`gateway.auth.allowTailscale`为`true`时，控制界面/WebSocket Serve请求可以通过Tailscale身份头（`tailscale-user-login`）进行身份验证。OpenClaw通过使用`tailscale whois`解析`x-forwarded-for`地址并与头部匹配来验证身份，并且仅在接受带有Tailscale的`x-forwarded-*`头部的环回请求时接受这些身份。如果您希望即使对于Serve流量也要求令牌/密码，请设置`gateway.auth.allowTailscale: false`（或强制`gateway.auth.mode: "password"`）。无令牌的Serve身份验证假设网关主机是可信的。如果不可信的本地代码可能在该主机上运行，则要求令牌/密码身份验证。

### 绑定到tailnet + 令牌

```bash
openclaw gateway --bind tailnet --token "$(openssl rand -hex 32)"
```

然后打开：

- `http://<tailscale-ip>:18789/`（或您配置的`gateway.controlUi.basePath`）

将令牌粘贴到UI设置中（作为`connect.params.auth.token`发送）。

## 不安全的HTTP

如果您通过纯HTTP（`http://<lan-ip>`或`http://<tailscale-ip>`）打开仪表板，浏览器将在**非安全上下文**中运行并阻止WebCrypto。默认情况下，OpenClaw**阻止**没有设备身份的控制界面连接。

**建议的解决方法：** 使用HTTPS（Tailscale Serve）或在本地打开UI：

- `https://<magicdns>/`（Serve）
- `http://127.0.0.1:18789/`（在网关主机上）

**不安全身份验证切换行为：**

```json5
{
  gateway: {
    controlUi: { allowInsecureAuth: true },
    bind: "tailnet",
    auth: { mode: "token", token: "replace-me" },
  },
}
```

`allowInsecureAuth`不会绕过控制界面设备身份或配对检查。

**仅限紧急情况：**

```json5
{
  gateway: {
    controlUi: { dangerouslyDisableDeviceAuth: true },
    bind: "tailnet",
    auth: { mode: "token", token: "replace-me" },
  },
}
```

`dangerouslyDisableDeviceAuth`禁用控制界面设备身份检查，这是一个严重的安全降级。紧急使用后应迅速恢复。

有关HTTPS设置指南，请参见[Tailscale](/gateway/tailscale)。

## 构建UI

网关从`dist/control-ui`提供静态文件。使用以下命令构建它们：

```bash
pnpm ui:build # auto-installs UI deps on first run
```

可选绝对基址（当您希望固定资源URL时）：

```bash
OPENCLAW_CONTROL_UI_BASE_PATH=/openclaw/ pnpm ui:build
```

对于本地开发（单独的开发服务器）：

```bash
pnpm ui:dev # auto-installs UI deps on first run
```

然后将UI指向您的网关WS URL（例如`ws://127.0.0.1:18789`）。

## 调试/测试：开发服务器+远程网关

控制界面是静态文件；WebSocket目标是可配置的，并且可以与HTTP源不同。当您希望本地使用Vite开发服务器但网关在其他地方运行时，这非常有用。

1. 启动UI开发服务器：`pnpm ui:dev`
2. 打开类似以下的URL：

```text
http://localhost:5173/?gatewayUrl=ws://<gateway-host>:18789
```

可选的一次性身份验证（如果需要）：

```text
http://localhost:5173/?gatewayUrl=wss://<gateway-host>:18789#token=<gateway-token>
```

注意事项：

- `gatewayUrl` 在加载后存储在localStorage中，并从URL中移除。
- `token` 被导入到当前标签页的内存中，并从URL中剥离；它不会存储在localStorage中。
- `password` 仅保留在内存中。
- 当设置`gatewayUrl` 时，UI不会回退到配置或环境凭据。请明确提供`token`（或`password`）。缺少明确的凭据将被视为错误。
- 当网关位于TLS后面（如Tailscale Serve、HTTPS代理等）时，请使用`wss://`。
- `gatewayUrl` 仅在顶级窗口（非嵌入式）中被接受，以防止点击劫持。
- 非回环Control UI部署必须明确设置`gateway.controlUi.allowedOrigins`（完整来源）。这包括远程开发设置。
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true` 启用Host-header源回退模式，但这是一种危险的安全模式。

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