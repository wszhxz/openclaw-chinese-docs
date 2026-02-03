---
summary: "Terminal UI (TUI): connect to the Gateway from any machine"
read_when:
  - You want a beginner-friendly walkthrough of the TUI
  - You need the complete list of TUI features, commands, and shortcuts
title: "TUI"
---
# 终端UI（TUI）

## 快速入门

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

如果网关使用密码认证，请使用 `--password`。

## 你将看到的内容

- 标题栏：连接URL、当前代理、当前会话。
- 聊天记录：用户消息、助手回复、系统通知、工具卡片。
- 状态栏：连接/运行状态（连接中、运行中、流式传输、空闲、错误）。
- 底部栏：连接状态 + 代理 + 会话 + 模型 + 思考/详细/推理 + 令牌计数 + 发送。
- 输入区域：带自动补全功能的文本编辑器。

## 思维模型：代理 + 会话

- 代理是唯一的标识符（例如 `main`、`research`）。网关会暴露该列表。
- 会话属于当前代理。
- 会话键存储为 `agent:<agentId>:<sessionKey>`。
  - 如果输入 `/session main`，TUI 会将其扩展为 `agent:<currentAgent>:main`。
  - 如果输入 `/session agent:other:main`，则会显式切换到该代理会话。
- 会话作用域：
  - `per-sender`（默认）：每个代理有多个会话。
  - `global`：TUI 始终使用 `global` 会话（选择器可能为空）。
- 当前代理 + 会话始终在底部栏中可见。

## 发送 + 发送

- 消息发送到网关；默认情况下不发送给提供方。
- 启用发送：
  - `/deliver on`
  - 或通过设置面板
  - 或使用 `openclaw tui --deliver` 启动

## 选择器 + 覆盖层

- 模型选择器：列出可用模型并设置会话覆盖。
- 代理选择器：选择不同的代理。
- 会话选择器：仅显示当前代理的会话。
- 设置：切换发送、工具输出扩展和思考可见性。

## 键盘快捷键

- Enter：发送消息
- Esc：中止当前运行
- Ctrl+C：清除输入（按两次退出）
- Ctrl+D：退出
- Ctrl+L：模型选择器
- Ctrl+G：代理选择器
- Ctrl+P：会话选择器
- Ctrl+O：切换工具输出扩展
- Ctrl+T：切换思考可见性（重新加载历史记录）

## 斜杠命令

核心命令：

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
- `/abort`（中止当前运行）
- `/settings`
- `/exit`

其他网关斜杠命令（例如 `/context`）会转发到网关并作为系统输出显示。详见 [斜杠命令](/tools/slash-commands)。

## 本地shell命令

- 以 `!` 开头的行会在TUI主机上运行本地shell命令。
- 每个会话TUI会提示一次以允许本地执行；拒绝则该会话的 `!` 功能将被禁用。
- 命令在TUI工作目录的全新、非交互式shell中运行（无持久 `cd`/环境）。
- 单独的 `!` 会被发送为普通消息；前导空格不会触发本地执行。

## 工具输出

- 工具调用以带有参数和结果的卡片形式显示。
- Ctrl+O 在折叠/展开视图之间切换。
- 工具运行时，部分更新会实时流式传输到同一卡片中。

## 历史记录 + 流式传输

- 连接时，TUI 会加载最新历史记录（默认 200 条消息）。
- 流式响应会原地更新，直到最终完成。
- TUI 还会监听代理工具事件以提供更丰富的工具卡片。

## 连接详情

- TUI 会以 `mode: "tui"` 的身份注册到网关。
- 重新连接时会显示系统消息；事件间隔会在日志中显示。

## 选项

- `--url <url>`：网关 WebSocket URL（默认为配置或 `ws://127.0.0.1:<port>`）
- `--token <token>`：网关令牌（如需要）
- `--password <password>`：网关密码（如需要）
- `--session <key>`：会话键（默认：`main`，或当作用域为全局时为 `global`）
- `--deliver`：将助手回复发送给提供方（默认关闭）
- `--thinking <level>`：覆盖发送时的思考级别
- `--timeout-ms <ms>`：代理超时时间（以毫秒为单位，默认为 `agents.defaults