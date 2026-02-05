---
summary: "macOS app flow for controlling a remote OpenClaw gateway over SSH"
read_when:
  - Setting up or debugging remote mac control
title: "Remote Control"
---
# 远程 OpenClaw (macOS ⇄ 远程主机)

此流程允许 macOS 应用程序充当运行在另一台主机（桌面/服务器）上的 OpenClaw 网关的完整远程控制。这是应用的 **Remote over SSH**（远程运行）功能。所有功能——健康检查、语音唤醒转发和网页聊天——都重用来自 _设置 → 常规_ 的相同远程 SSH 配置。

## 模式

- **本地（此 Mac）**：所有内容都在笔记本电脑上运行。不涉及 SSH。
- **远程通过 SSH（默认）**：OpenClaw 命令在远程主机上执行。mac 应用程序使用 `-o BatchMode` 加上你选择的身份/密钥和本地端口转发打开一个 SSH 连接。
- **远程直接（ws/wss）**：没有 SSH 隧道。mac 应用程序直接连接到网关 URL（例如，通过 Tailscale Serve 或公共 HTTPS 反向代理）。

## 远程传输

远程模式支持两种传输方式：

- **SSH 隧道**（默认）：使用 `ssh -N -L ...` 将网关端口转发到本地主机。由于隧道是回环的，网关会看到节点的 IP 为 `127.0.0.1`。
- **直接（ws/wss）**：直接连接到网关 URL。网关会看到真实的客户端 IP。

## 远程主机上的先决条件

1. 安装 Node + pnpm 并构建/安装 OpenClaw CLI (`pnpm install && pnpm build && pnpm link --global`)。
2. 确保 `openclaw` 在非交互式 shell 的 PATH 中（如果需要，将其符号链接到 `/usr/local/bin` 或 `/opt/homebrew/bin`）。
3. 使用密钥认证打开 SSH。我们建议使用 **Tailscale** IP 以获得局域网外的稳定可达性。

## macOS 应用程序设置

1. 打开 _设置 → 常规_。
2. 在 **OpenClaw 运行** 下，选择 **Remote over SSH** 并设置：
   - **传输**：**SSH 隧道** 或 **直接（ws/wss）**。
   - **SSH 目标**：`user@host`（可选 `:port`）。
     - 如果网关在同一局域网内并广播 Bonjour，请从发现列表中选择它以自动填充此字段。
   - **网关 URL**（仅直接）：`wss://gateway.example.ts.net`（或 `ws://...` 用于本地/局域网）。
   - **身份文件**（高级）：密钥的路径。
   - **项目根目录**（高级）：用于命令的远程检出路径。
   - **CLI 路径**（高级）：可选的可运行 `openclaw` 入口点/二进制文件的路径（当广播时自动填充）。
3. 点击 **测试远程**。成功表示远程 `openclaw status --json` 正确运行。失败通常意味着 PATH/CLI 问题；退出 127 表示远程未找到 CLI。
4. 健康检查和网页聊天现在将自动通过此 SSH 隧道运行。

## 网页聊天

- **SSH 隧道**：网页聊天通过转发的 WebSocket 控制端口（默认 18789）连接到网关。
- **直接（ws/wss）**：网页聊天直接连接到配置的网关 URL。
- 不再有单独的 WebChat HTTP 服务器。

## 权限

- 远程主机需要与本地相同的 TCC 批准（自动化、辅助功能、屏幕录制、麦克风、语音识别、通知）。在该机器上运行入职流程以一次性授予它们。
- 节点通过 `node.list` / `node.describe` 广播其权限状态，因此代理知道哪些功能可用。

## 安全注意事项

- 在远程主机上优先使用回环绑定并通过 SSH 或 Tailscale 连接。
- 如果将网关绑定到非回环接口，请要求令牌/密码认证。
- 查看 [安全](/gateway/security) 和 [Tailscale](/gateway/tailscale)。

## WhatsApp 登录流程（远程）

- 在 **远程主机** 上运行 `openclaw channels login --verbose`。使用手机上的 WhatsApp 扫描 QR 码。
- 如果认证过期，请在该主机上重新运行登录。健康检查将显示链接问题。

## 故障排除

- **退出 127 / 未找到**：`openclaw` 不在非登录 shell 的 PATH 中。将其添加到 `/etc/paths`、你的 shell rc 或符号链接到 `/usr/local/bin`/`/opt/homebrew/bin`。
- **健康探测失败**：检查 SSH 可达性、PATH 以及 Baileys 是否已登录 (`openclaw status --json`)。
- **网页聊天卡住**：确认远程主机上正在运行网关且转发的端口与网关 WS 端口匹配；UI 需要健康的 WS 连接。
- **节点 IP 显示 127.0.0.1**：使用 SSH 隧道时预期如此。如果希望网关看到真实的客户端 IP，请将 **传输** 切换到 **直接（ws/wss）**。
- **语音唤醒**：触发短语在远程模式下会自动转发；不需要单独的转发器。

## 通知声音

从带有 `openclaw` 和 `node.invoke` 的脚本中为每个通知选择声音，例如：

```bash
openclaw nodes notify --node <id> --title "Ping" --body "Remote gateway ready" --sound Glass
```

应用程序中不再有全局“默认声音”开关；调用者根据请求选择声音（或不选择）。

```plaintext
示例代码块
```

`示例行内代码`

**粗体文本**

*斜体文本*

[链接文本](http://example.com)

| 表格 | 示例 |
|------|------|
| 数据 | 数据 |

> 引用文本