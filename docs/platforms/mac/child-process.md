---
summary: "Gateway lifecycle on macOS (launchd)"
read_when:
  - Integrating the mac app with the gateway lifecycle
title: "Gateway Lifecycle"
---
# macOS上的网关生命周期

macOS应用程序默认**通过launchd管理网关**，而不是将其作为子进程启动。它首先尝试连接到配置端口上已运行的网关；如果没有可连接的网关，则通过外部`openclaw` CLI（无嵌入式运行时）启用launchd服务。这为您提供登录时可靠的自动启动和崩溃后的重启。

直接由应用程序启动的子进程模式今天**未使用**。如果您需要与UI更紧密的耦合，请在终端中手动运行网关。

## 默认行为（launchd）

- 应用程序安装了一个每个用户的LaunchAgent，标签为`ai.openclaw.gateway`
  （或当使用`--profile`/`OPENCLAW_PROFILE`时为`ai.openclaw.<profile>`；旧版`com.openclaw.*`是支持的）。
- 当启用本地模式时，应用程序确保加载了LaunchAgent，并根据需要启动网关。
- 日志写入到launchd网关日志路径（在调试设置中可见）。

常用命令：

```bash
launchctl kickstart -k gui/$UID/ai.openclaw.gateway
launchctl bootout gui/$UID/ai.openclaw.gateway
```

当运行命名配置文件时，将标签替换为`ai.openclaw.<profile>`。

## 未签名的开发构建

`scripts/restart-mac.sh --no-sign`用于当你没有签名密钥时快速本地构建。为了防止launchd指向一个未签名的中继二进制文件，它：

- 写入`~/.openclaw/disable-launchagent`。

如果存在标记，`scripts/restart-mac.sh`的签名运行会清除此覆盖。要手动重置：

```bash
rm ~/.openclaw/disable-launchagent
```

## 仅附加模式

要强制macOS应用程序**从不安装或管理launchd**，请使用`--attach-only`（或`--no-launchd`）启动它。这设置了`~/.openclaw/disable-launchagent`，因此应用程序只附加到已经运行的网关。您可以在调试设置中切换相同的行为。

## 远程模式

远程模式永远不会启动本地网关。应用程序使用SSH隧道连接到远程主机并通过该隧道进行连接。

## 我们为什么偏好launchd

- 登录时自动启动。
- 内置重启/KeepAlive语义。
- 可预测的日志和监督。

如果将来确实需要真正的子进程模式，应将其记录为单独的、明确的仅开发模式。