---
summary: "macOS app flow for controlling a remote OpenClaw gateway over SSH"
read_when:
  - Setting up or debugging remote mac control
title: "Remote Control"
---
# 远程 OpenClaw (macOS ⇄ 远程主机)

此流程允许 macOS 应用作为运行在另一台主机（桌面/服务器）上的 OpenClaw 网关的完整远程控制。这是应用的 **通过 SSH 远程**（远程运行）功能。所有功能——健康检查、语音唤醒转发和网页聊天——均复用来自 _设置 → 通用_ 的相同远程 SSH 配置。

## 模式

- **本地（此 Mac）**：所有操作都在笔记本电脑上运行，不涉及 SSH。
- **通过 SSH 远程（默认）**：OpenClaw 命令在远程主机上执行。Mac 应用通过 `-o BatchMode` 参数打开 SSH 连接，并使用您选择的身份/密钥和本地端口转发。
- **直接连接 (ws/wss)**：不使用 SSH 隧道。Mac 应用直接连接到网关 URL（例如，通过 Tailscale Serve 或公共 HTTPS 反向代理）。

## 远程传输方式

远程模式支持两种传输方式：

- **SSH 隧道**（默认）：使用 `ssh -N -L ...` 将网关端口转发到本地主机。由于隧道是环回连接，网关将看到节点的 IP 为 `127.0.0.1`。
- **直接连接 (ws/wss)**：直接连接到网关 URL。网关将看到真实的客户端 IP。

## 远程主机的前置条件

1. 安装 Node + pnpm 并构建/安装 OpenClaw CLI (`pnpm install && pnpm build && pnpm link --global`).
2. 确保 `openclaw` 在非交互式 shell 的 PATH 中（如需，可将符号链接放入 `/usr/local/bin` 或 `/opt/homebrew/bin`）。
3. 使用 SSH 密钥认证。我们推荐使用 **Tailscale** IP 以确保离局域网的稳定可达性。

## macOS 应用设置

1. 打开 _设置 → 通用_。
2. 在 **OpenClaw 运行** 下，选择 **通过 SSH 远程**，并设置：
   - **传输方式**：**SSH 隧道** 或 **直接连接 (ws/wss)**。
   - **SSH 目标**：`user@host`（可选 `:port`）。
     - 如果网关在同一局域网内并广播了 Bonjour，可从发现列表中选择以自动填充此字段。
   - **网关 URL**（仅限直接连接）：`wss://gateway.example.ts.net`（或 `ws://...` 用于本地/LAN）。
   - **身份文件**（高级）：您的密钥路径。
   - **项目根目录**（高级）：用于命令的远程检出路径。
   - **CLI 路径**（高级）：可选的 `openclaw` 可执行入口/二进制文件路径（在广播时自动填充）。
3. 点击 **测试远程**。成功表示远程 `openclaw status --json` 正常运行。失败通常意味着 PATH/CLI 问题；退出码 127 表示远程未找到 CLI。
4. 健康检查和网页聊天将通过此 SSH 隧道自动运行。

## 网页聊天

- **SSH 隧道**：网页聊天通过转发的 WebSocket 控制端口（默认 18789）连接到网关。
- **直接连接 (ws/wss)**：网页聊天直接连接到配置的网关 URL。
- 不再有单独的 WebChat HTTP 服务器。

## 权限

- 远程主机需要与本地相同的 TCC 授权（自动化、辅助功能、屏幕录制、麦克风、语音识别、通知）。在该机器上运行入职流程以一次性授予这些权限。
- 节点通过 `node.list` / `node.describe` 广播其权限状态，以便代理知道可用内容。

## 安全注意事项

- 建议在远程主机上使用环回绑定，并通过 SSH 或 Tailscale 连接。
- 如果将网关绑定到非环回接口，请要求令牌/密码认证。
- 参见 [安全](/gateway/security) 和 [Tailscale](/gateway/tailscale)。

## WhatsApp 登录流程（远程）

- 在远程主机上运行 `openclaw channels login --verbose`。使用手机上的 WhatsApp 扫描二维码。
- 如果认证过期，重新在该主机上运行登录。健康检查将显示链接问题。

## 故障排除

- **退出码 127 / 未找到**：`openclaw` 未在非登录 shell 的 PATH 中。将其添加到 `/etc/paths`、您的 shell rc 文件或符号链接到 `/usr/local/bin`/`/opt/homebrew/bin`。
- **健康检查失败**：检查 SSH 可达性、PATH 和 Baileys 是否已登录 (`openclaw status --json`)。
- **网页聊天卡住**：确认网关在远程主机上运行，并且转发的端口与网关 WS 端口匹配；UI 需要健康的 WS 连接。
- **节点 IP 显示为 127.0.0.1**：预期在 SSH 隧道中。如果您希望网关看到真实的客户端 IP，请将 **传输方式** 切换为 **直接连接 (ws/wss)**。
- **语音唤醒**：远程模式下触发短语会自动转发；无需单独转发器。

## 通知声音

通过脚本使用 `openclaw` 和 `node.invoke` 为每个通知选择声音，例如：

```bash
openclaw nodes notify --node <id> --title "Ping" --body "远程网关就绪" --sound Glass
```

应用中不再有全局的“默认声音”切换选项；调用者根据每个请求选择声音（或无声音）。