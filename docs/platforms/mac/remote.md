---
summary: "macOS app flow for controlling a remote OpenClaw gateway over SSH"
read_when:
  - Setting up or debugging remote mac control
title: "Remote Control"
---
# 远程 OpenClaw (macOS ⇄ 远程主机)

此流程使 macOS 应用能够作为在另一个主机(桌面/服务器)上运行的 OpenClaw 网关的完整远程控制。这是应用的**通过 SSH 远程**(远程运行)功能。所有功能——健康检查、语音唤醒转发和网页聊天——都重用来自_设置 → 常规_的相同远程 SSH 配置。

## 模式

- **本地(此 Mac)**：所有内容都在笔记本电脑上运行。不涉及 SSH。
- **通过 SSH 远程(默认)**：OpenClaw 命令在远程主机上执行。mac 应用使用 `-o BatchMode` 加上您选择的身份/密钥和本地端口转发打开 SSH 连接。
- **远程直连(ws/wss)**：无 SSH 隧道。mac 应用直接连接到网关 URL(例如，通过 Tailscale Serve 或公共 HTTPS 反向代理)。

## 远程传输

远程模式支持两种传输方式：

- **SSH 隧道**(默认)：使用 `ssh -N -L ...` 将网关端口转发到 localhost。由于隧道是回环的，网关将看到节点的 IP 为 `127.0.0.1`。
- **直连(ws/wss)**：直接连接到网关 URL。网关看到真实的客户端 IP。

## 远程主机的先决条件

1. 安装 Node + pnpm 并构建/安装 OpenClaw CLI (`pnpm install && pnpm build && pnpm link --global`)。
2. 确保 `openclaw` 在非交互式 shell 的 PATH 中(如有需要，链接到 `/usr/local/bin` 或 `/opt/homebrew/bin`)。
3. 使用密钥认证打开 SSH。我们推荐使用**Tailscale** IP 以获得离网时的稳定可达性。

## macOS 应用设置

1. 打开_设置 → 常规_。
2. 在**OpenClaw 运行**下，选择**通过 SSH 远程**并设置：
   - **传输**：**SSH 隧道**或**直连(ws/wss)**。
   - **SSH 目标**：`user@host`(可选 `:port`)。
     - 如果网关在同一局域网中并广播了 Bonjour，请从发现列表中选择它以自动填充此字段。
   - **网关 URL**(仅限直连)：`wss://gateway.example.ts.net`(或 `ws://...` 用于本地/局域网)。
   - **身份文件**(高级)：您的密钥路径。
   - **项目根目录**(高级)：用于命令的远程检出路径。
   - **CLI 路径**(高级)：可选的 `openclaw` 入口点/二进制文件的可运行路径(广告时自动填充)。
3. 点击**测试远程**。成功表示远程 `openclaw status --json` 正确运行。失败通常意味着 PATH/CLI 问题；退出码 127 表示远程找不到 CLI。
4. 健康检查和网页聊天现在将自动通过此 SSH 隧道运行。

## 网页聊天

- **SSH 隧道**：网页聊天通过转发的 WebSocket 控制端口(默认 18789)连接到网关。
- **直连(ws/wss)**：网页聊天直接连接到配置的网关 URL。
- 不再有单独的 WebChat HTTP 服务器。

## 权限

- 远程主机需要与本地相同的 TCC 批准(自动化、辅助功能、屏幕录制、麦克风、语音识别、通知)。在该机器上运行入门设置以一次性授予它们。
- 节点通过 `node.list` / `node.describe` 广播它们的权限状态，以便代理知道可用内容。

## 安全注意事项

- 优先在远程主机上使用回环绑定，并通过 SSH 或 Tailscale 连接。
- 如果您将网关绑定到非回环接口，请要求令牌/密码认证。
- 参见[安全性](/gateway/security)和[Tailscale](/gateway/tailscale)。

## WhatsApp 登录流程(远程)

- 在**远程主机**上运行 `openclaw channels login --verbose`。用手机上的 WhatsApp 扫描二维码。
- 如果认证过期，请在该主机上重新运行登录。健康检查将显示链接问题。

## 故障排除

- **exit 127 / not found**：`openclaw` 对于非登录 shell 不在 PATH 中。将其添加到 `/etc/paths`、您的 shell rc 或链接到 `/usr/local/bin`/`/opt/homebrew/bin`。
- **健康探测失败**：检查 SSH 可达性、PATH 和 Baileys 是否已登录(`openclaw status --json`)。
- **网页聊天卡住**：确认网关正在远程主机上运行且转发的端口与网关 WS 端口匹配；UI 需要健康的 WS 连接。
- **节点 IP 显示 127.0.0.1**：SSH 隧道的预期行为。如果您希望网关看到真实的客户端 IP，请将**传输**切换到**直连(ws/wss)**。
- **语音唤醒**：触发短语在远程模式下自动转发；不需要单独的转发器。

## 通知声音

从脚本中为每个通知选择声音，使用 `openclaw` 和 `node.invoke`，例如：

```bash
openclaw nodes notify --node <id> --title "Ping" --body "Remote gateway ready" --sound Glass
```

应用中不再有全局的"默认声音"开关；调用者为每个请求选择声音(或无)。