---
summary: "SSH tunnel setup for OpenClaw.app connecting to a remote gateway"
read_when: "Connecting the macOS app to a remote gateway over SSH"
title: "Remote Gateway Setup"
---
# 通过远程网关运行OpenClaw.app

OpenClaw.app使用SSH隧道连接到远程网关。本指南将指导您如何设置。

## 概览

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端机器                          │
│                                                              │
│  OpenClaw.app ──► ws://127.0.0.1:18789 (本地端口)           │
│                     │                                        │
│                     ▼                                        │
│  SSH隧道 ────────────────────────────────────────────────│
│                     │                                        │
└─────────────────────┼──────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                         远程机器                        │
│                                                              │
│  网关WebSocket ──► ws://127.0.0.1:18789 ──►              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 快速设置

### 步骤 1：添加SSH配置

编辑 `~/.ssh/config` 并添加：

```ssh
Host remote-gateway
    HostName <REMOTE_IP>          # 例如：172.27.187.184
    User <REMOTE_USER>            # 例如：jefferson
    LocalForward 18789 127.0.0.1:18789
    IdentityFile ~/.ssh/id_rsa
```

将 `<REMOTE_IP>` 和 `<REMOTE_USER>` 替换为您的值。

### 步骤 2：复制SSH密钥

将您的公钥复制到远程机器（输入密码一次）：

```bash
ssh-copy-id -i ~/.ssh/id_rsa <REMOTE_USER>@<REMOTE_IP>
```

### 步骤 3：设置网关令牌

```bash
launchctl setenv OPENCLAW_GATEWAY_TOKEN "<your-token>"
```

### 步骤 4：启动SSH隧道

```bash
ssh -N remote-gateway &
```

### 步骤 5：重启OpenClaw.app

```bash
# 退出OpenClaw.app（⌘Q），然后重新打开：
open /path/to/OpenClaw.app
```

应用程序现在将通过SSH隧道连接到远程网关。

---

## 登录时自动启动隧道

要使SSH隧道在登录时自动启动，请创建一个启动代理。

### 创建PLIST文件

将以下内容保存为 `~/Library/LaunchAgents/bot.molt.ssh-tunnel.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>bot.molt.ssh-tunnel</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/ssh</string>
        <string>-N</string>
        <string>remote-gateway</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### 加载启动代理

```bash
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/bot.molt.ssh-tunnel.plist
```

隧道现在将：

- 登录时自动启动
- 如果崩溃会重新启动
- 在后台持续运行

注意事项：如果存在，请删除任何遗留的 `com.openclaw.ssh-tunnel` 启动代理。

---

## 故障排除

**检查隧道是否正在运行：**

```bash
ps aux | grep "ssh -N remote-gateway" | grep -v grep
lsof -i :18789
```

**重启隧道：**

```bash
launchctl kickstart -k gui/$UID/bot.molt.ssh-tunnel
```

**停止隧道：**

```bash
launchctl bootout gui/$UID/bot.molt.ssh-tunnel
```

---

## 工作原理

| 组件                            | 功能                                                 |
| ------------------------------------ | ------------------------------------------------------------ |
| `LocalForward 18789 127.0.0.1:18789` | 将本地端口 18789 转发到远程端口 18789               |
| `ssh -N`                             | SSH 无执行远程命令（仅端口转发） |
| `KeepAlive`                          | 如果隧道崩溃会自动重启                  |
| `RunAtLoad`                          | 在代理加载时启动隧道                           |

OpenClaw.app 在您的客户端机器上连接到 `ws://127.0.0.1:18789`。SSH 隧道将此连接转发到远程机器上的 18789 端口，该端口运行着网关。