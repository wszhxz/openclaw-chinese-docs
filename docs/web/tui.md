---
summary: "Terminal UI (TUI): connect to the Gateway from any machine"
read_when:
  - You want a beginner-friendly walkthrough of the TUI
  - You need the complete list of TUI features, commands, and shortcuts
title: "TUI"
---
# TUI (终端用户界面)

## 快速开始

1. 启动网关。

```bash
openclaw gateway
```

2. 打开TUI。

```bash
openclaw tui
```

3. 输入消息并按Enter键。

远程网关：

```bash
openclaw tui --url ws://<host>:<port> --token <gateway-token>
```

如果您的网关使用密码认证，请使用`--password`。

## 您所看到的内容

- 页眉：连接URL、当前代理、当前会话。
- 聊天记录：用户消息、助手回复、系统通知、工具卡片。
- 状态行：连接/运行状态（连接中、运行中、流式传输、空闲、错误）。
- 页脚：连接状态 + 代理 + 会话 + 模型 + 思考/详细/推理 + 令牌计数 + 传递。
- 输入：带有自动完成功能的文本编辑器。

## 心智模型：代理 + 会话

- 代理是唯一的标识符（例如 `main`, `research`）。网关公开了这个列表。
- 会话属于当前代理。
- 会话密钥存储为 `agent:<agentId>:<sessionKey>`。
  - 如果您输入 `/session main`，TUI 将其扩展为 `agent:<currentAgent>:main`。
  - 如果您输入 `/session agent:other:main`，则显式切换到该代理会话。
- 会话范围：
  - `per-sender`（默认）：每个代理有多个会话。
  - `global`：TUI 始终使用 `global` 会话（选择器可能为空）。
- 当前代理 + 会话始终在页脚中可见。

## 发送 + 传递

- 消息发送到网关；默认情况下不向提供商传递。
- 开启传递：
  - `/deliver on`
  - 或者通过设置面板
  - 或者以 `openclaw tui --deliver` 启动

## 选择器 + 覆盖层

- 模型选择器：列出可用模型并设置会话覆盖。
- 代理选择器：选择不同的代理。
- 会话选择器：仅显示当前代理的会话。
- 设置：切换传递、工具输出展开和思考可见性。

## 键盘快捷键

- Enter：发送消息
- Esc：中止活动运行
- Ctrl+C：清除输入（按两次退出）
- Ctrl+D：退出
- Ctrl+L：模型选择器
- Ctrl+G：代理选择器
- Ctrl+P：会话选择器
- Ctrl+O：切换工具输出展开
- Ctrl+T：切换思考可见性（重新加载历史）

## 斜杠命令

核心：

- `/help`
- `/status`
- `/agent <id>`（或 `/agents`）
- `/session <key>`（或 `/sessions`）
- `/model <provider/model>`（或 `/models`）

会话控制：

- `/think <off|minimal|low|medium|high>`
- `/verbose <on|full|off>`
- `/reasoning <on|off|stream>`
- `/usage <off|tokens|full>`
- `/elevated <on|off|ask|full>`（别名：`/elev`）
- `/activation <mention|always>`
- `/deliver <on|off>`

会话生命周期：

- `/new` 或 `/reset`（重置会话）
- `/abort`（中止活动运行）
- `/settings`
- `/exit`

其他网关斜杠命令（例如，`/context`）将转发到网关并作为系统输出显示。参见[斜杠命令](/tools/slash-commands)。

## 本地 shell 命令

- 在行首加上 `!` 以在 TUI 主机上运行本地 shell 命令。
- TUI 每次会话提示一次允许本地执行；拒绝将使 `!` 在会话期间禁用。
- 命令在一个新的非交互式 shell 中运行，在 TUI 工作目录中（没有持久的 `cd`/环境）。
- 本地 shell 命令在其环境中接收 `OPENCLAW_SHELL=tui-local`。
- 单独的 `!` 作为普通消息发送；前导空格不会触发本地执行。

## 工具输出

- 工具调用显示为带有参数和结果的卡片。
- Ctrl+O 在折叠/展开视图之间切换。
- 工具运行时，部分更新会流入同一张卡片。

## 历史 + 流式传输

- 连接时，TUI 加载最新的历史记录（默认 200 条消息）。
- 流式响应会在原地更新，直到最终确定。
- TUI 还监听代理工具事件，以获得更丰富的工具卡片。

## 连接详情

- TUI 以 `mode: "tui"` 注册到网关。
- 重新连接时会显示系统消息；日志中会显示事件间隙。

## 选项

- `--url <url>`：网关 WebSocket URL（默认为配置或 `ws://127.0.0.1:<port>`）
- `--token <token>`：网关令牌（如果需要）
- `--password <password>`：网关密码（如果需要）
- `--session <key>`：会话密钥（默认：`main`，或者当范围为全局时为 `global`）
- `--deliver`：将助手回复传递给提供商（默认关闭）
- `--thinking <level>`：覆盖发送时的思考级别
- `--timeout-ms <ms>`：代理超时时间（毫秒，默认为 `agents.defaults.timeoutSeconds`）

注意：当您设置 `--url` 时，TUI 不会回退到配置或环境凭据。
请明确传递 `--token` 或 `--password`。缺少明确的凭据是一个错误。

## 故障排除

发送消息后无输出：

- 在 TUI 中运行 `/status` 以确认网关已连接且处于空闲/忙碌状态。
- 检查网关日志：`openclaw logs --follow`。
- 确认代理可以运行：`openclaw status` 和 `openclaw models status`。
- 如果您期望在聊天频道中收到消息，请启用传递（`/deliver on` 或 `--deliver`）。
- `--history-limit <n>`：要加载的历史条目数（默认 200）

## 连接故障排除

- `disconnected`：确保网关正在运行并且您的 `--url/--token/--password` 是正确的。
- 选择器中没有代理：检查 `openclaw agents list` 和您的路由配置。
- 会话选择器为空：您可能处于全局范围内或尚未有任何会话。