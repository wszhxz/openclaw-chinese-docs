---
summary: "Gateway lifecycle on macOS (launchd)"
read_when:
  - Integrating the mac app with the gateway lifecycle
title: "Gateway Lifecycle"
---
# macOS上的网关生命周期

macOS应用程序默认通过**launchd管理网关**，而不是将其作为子进程启动。它首先尝试连接到配置端口上已运行的网关；如果没有可访问的实例，则通过外部`openclaw` CLI启用launchd服务（无嵌入式运行时）。这为您提供可靠的登录自动启动和崩溃重启功能。

子进程模式（由应用程序直接启动网关）**目前未使用**。如果您需要与UI更紧密的耦合，请在终端中手动运行网关。

## 默认行为（launchd）

- 应用程序安装一个用户级LaunchAgent，标记为`bot.molt.gateway`
  （或在使用`--profile`/`OPENCLAW_PROFILE`时为`bot.molt.<profile>`；支持旧版`com.openclaw.*`）。
- 当本地模式启用时，应用程序确保LaunchAgent已加载并在需要时启动网关。
- 日志写入launchd网关日志路径（在调试设置中可见）。

常用命令：

```bash
launchctl kickstart -k gui/$UID/bot.molt.gateway
launchctl bootout gui/$UID/bot.molt.gateway
```

在运行命名配置文件时，将标签替换为`bot.molt.<profile>`。

## 未签名的开发构建

`scripts/restart-mac.sh --no-sign`用于没有签名密钥的快速本地构建。为了防止launchd指向未签名的中继二进制文件，它：

- 写入`~/.openclaw/disable-launchagent`。

`scripts/restart-mac.sh`的签名运行会清除此覆盖，如果存在标记。要手动重置：

```bash
rm ~/.openclaw/disable-launchagent
```

## 仅附加模式

要强制macOS应用程序**从不安装或管理launchd**，请使用`--attach-only`（或`--no-launchd`）启动。这设置了`~/.openclaw/disable-launchagent`，因此应用程序仅附加到已运行的网关。您可以在调试设置中切换相同的行为。

## 远程模式

远程模式从不启动本地网关。应用程序通过SSH隧道连接到远程主机，并通过该隧道进行连接。

## 为什么我们偏好launchd

- 登录时自动启动。
- 内置的重启/KeepAlive语义。
- 可预测的日志和监督。

如果将来再次需要真正的子进程模式，应将其记录为单独的、明确的开发人员专用模式。