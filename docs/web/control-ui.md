---
summary: "Browser-based control UI for the Gateway (chat, nodes, config)"
read_when:
  - You want to operate the Gateway from a browser
  - You want Tailnet access without SSH tunnels
title: "Control UI"
---
# 控制界面（浏览器）

控制界面是一个小型的 **Vite + Lit** 单页应用，由网关提供服务：

- 默认地址：`http://<host>:18789/`
- 可选前缀：设置 `gateway.controlUi.basePath`（例如 `/openclaw`）

它直接通过网关的 WebSocket 连接，使用相同端口。

## 快速打开（本地）

如果网关运行在同一台计算机上，打开：

- `http://127.0.0.1:18789/`（或 `http://localhost:18789/`）

如果页面无法加载，请先启动网关：`openclaw gateway`。

在 WebSocket 握手期间通过以下方式提供身份验证：

- `connect.params.auth.token`
- `connect.params.auth.password`
  控制面板的设置部分允许您存储令牌；密码不会被持久化。
  入门向导默认生成一个网关令牌，因此首次连接时请将此处粘贴该令牌。

## 设备配对（首次连接）

当您从新浏览器或设备连接到控制界面时，网关
需要进行 **一次性配对授权** —— 即使您处于 `gateway.auth.allowTailscale: true` 的相同 Tailnet 中。这是为了防止未经授权访问的安全措施。

**您将看到：** "disconnected (1008): 需要配对"

**授权设备：**

```bash
# 列出待处理的请求
openclaw devices list

# 通过请求 ID 授权
openclaw devices approve <requestId>
```

一旦授权，该设备将被记住，除非您使用 `openclaw devices revoke --device <id> --role <role>` 撤销授权，否则无需重新授权。有关令牌轮换和撤销，请参阅 [Devices CLI](/cli/devices)。

**注意事项：**

- 本地连接 (`127.0.0.1`) 会自动授权。
- 远程连接（局域网、Tailnet 等）需要显式授权。
- 每个浏览器配置文件生成唯一的设备 ID，因此切换浏览器或清除浏览器数据将需要重新配对。

## 控制界面功能（当前）

- 通过网关 WebSocket 与模型聊天 (`chat.history`, `chat.send`, `chat.abort`, `chat.inject`)
- 在聊天中流式传输工具调用 + 实时工具输出卡片（代理事件）
- 通道：WhatsApp/Telegram/Discord/Slack + 插件通道（Mattermost 等）状态 + QR 登录 + 每个通道配置 (`channels.status`, `web.login.*`, `config.patch`)
- 实例：在线列表 + 刷新 (`system-presence`)
- 会话：列表 + 每个会话的思考/详细模式覆盖 (`sessions.list`, `sessions.patch`)
- 定时任务：列表/添加/运行/启用/禁用 + 运行历史 (`cron.*`)
- 技能：状态、启用/禁用、安装、API 密钥更新 (`skills.*`)
- 节点：列表 + 能力 (`node.list`)
- 执行批准：编辑网关或节点白名单 + 查询 `exec host=gateway/node` 的策略 (`exec.approvals.*`)
- 配置：查看/编辑 `~/.openclaw/openclaw.json` (`config.get`, `config.set`)
- 配置：应用 + 重启验证 (`config.apply`) 并唤醒最后一个活跃会话
- 配置写入包含基础哈希保护，防止覆盖并发编辑
- 配置模式 + 表单渲染 (`config.schema`，包括插件 + 通道模式)；原始 JSON 编辑器仍然可用
- 调试：状态/健康/模型快照 + 事件日志 + 手动 RPC 调用 (`status`, `health`, `models.list`)
- 日志：带过滤/导出的网关文件日志实时尾随 (`logs.tail`)
- 更新：运行包/ Git 更新 + 重启 (`update.run`) 并生成重启报告

## 聊天行为

- `chat.send` 是 **非阻塞的**：它会立即返回 `{ runId, status: "started" }` 并通过 `chat` 事件流式传输响应。
- 使用相同的 `idempotencyKey` 重新发送时，运行中返回 `{ status: "in_flight" }`，完成后返回 `{ status: "ok" }`。
- `chat.inject` 会将助手注释附加到会话记录，并广播 `chat` 事件用于 UI 仅更新（无代理运行，无通道分发）。
- 停止：
  - 点击 **停止**（调用 `chat.abort`）
  - 输入 `/stop`（或 `stop|esc|abort|wait|exit|interrupt`）中止非预期操作
  - `chat.abort` 支持 `{ sessionKey }`（不带 `runId`）中止该会话的所有活动运行

## Tailnet 访问（推荐）

### 集成 Tailscale 服务（首选）

将网关保持在回环地址，并让 Tailscale 服务通过 HTTPS 代理：

```bash
openclaw gateway --tailscale serve
```

打开：

- `https://<magicdns>/`（或您配置的 `gateway.controlUi.basePath`）

默认情况下，当 `gateway.auth.allowTailscale` 为 `true` 时，Serve 请求可以通过 Tailscale 身份头（`tailscale-user-login`）进行身份验证。OpenClaw 通过将 `x-forwarded-for` 地址与 `tailscale whois` 匹配来验证身份，并且仅在请求通过回环地址并带有 Tailscale 的 `x-forwarded-*` 头时接受这些请求。如果您希望即使对于 Serve 流量也要求令牌/密码，请设置 `gateway.auth.allowTailscale: false`（或强制 `gateway.auth.mode: "password"`）。

### 绑定到 tailnet + 令牌

```bash
openclaw gateway --bind tailnet --token "$(openssl rand -hex 32)"
```

然后打开：

- `http://<