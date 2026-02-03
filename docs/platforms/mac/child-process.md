---
summary: "Gateway lifecycle on macOS (launchd)"
read_when:
  - Integrating the mac app with the gateway lifecycle
title: "Gateway Lifecycle"
---
# macOS上的网关生命周期

macOS应用**默认通过launchd管理网关**，并不以子进程形式启动网关。它首先尝试连接到已运行的网关（在配置的端口上）；如果没有找到，则通过外部`openclaw` CLI启用launchd服务（不包含嵌入式运行时）。这可确保登录时可靠自动启动，并在崩溃时重启。

子进程模式（网关由应用直接启动）**当前未使用**。如果需要更紧密地与UI集成，请在终端中手动运行网关。

## 默认行为（launchd）

- 应用安装一个用户级的LaunchAgent，标记为`bot.molt.gateway`（或使用`--profile`/`OPENCLAW_PROFILE`时为`bot.molt.<profile>`；支持旧版`com.openclaw.*`）。
- 当启用本地模式时，应用确保LaunchAgent已加载，并在需要时启动网关。
- 日志写入launchd网关日志路径（可在调试设置中查看）。

常用命令：

```bash
launchctl kickstart -k gui/$UID/bot.molt.gateway
launchctl bootout gui/$UID/bot.molt.gateway
```

在运行命名配置文件时，请将标签替换为`bot.molt.<profile>`。

## 未签名的开发构建

`scripts/restart-mac.sh --no-sign`用于在没有签名密钥时进行快速本地构建。为防止launchd指向未签名的中继二进制文件，它：

- 写入`~/.openclaw/disable-launchagent`。

已签名的`scripts/restart-mac.sh`运行会清除此覆盖（如果存在标记）。手动重置：

```bash
rm ~/.openclaw/disable-launchagent
```

## 仅附加模式

要强制macOS应用**永不安装或管理launchd**，请使用`--attach-only`（或`--no-launchd`）启动。这会设置`~/.openclaw/disable-launchagent`，使应用仅附加到已运行的网关。您也可以在调试设置中切换相同行为。

## 远程模式

远程模式永远不会启动本地网关。应用通过SSH隧道连接到远程主机，并通过该隧道建立连接。

## 为何我们偏好launchd

- 登录时自动启动。
- 内置的重启/保持活动语义。
- 可预测的日志和监督。

如果将来再次需要真正的子进程模式，应将其文档化为一个独立的、明确的仅开发模式。