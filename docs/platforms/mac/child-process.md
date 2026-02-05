---
summary: "Gateway lifecycle on macOS (launchd)"
read_when:
  - Integrating the mac app with the gateway lifecycle
title: "Gateway Lifecycle"
---
# macOS 上的网关生命周期

macOS 应用默认通过 **launchd 管理网关**，而不是作为子进程启动网关。它首先尝试连接到配置端口上已经运行的网关；如果没有可访问的网关，它会通过外部的 `openclaw` CLI 启用 launchd 服务（无嵌入式运行时）。这为您提供了可靠的登录自动启动和崩溃重启功能。

子进程模式（由应用直接启动的网关）**目前未使用**。如果您需要与 UI 更紧密的耦合，请在终端中手动运行网关。

## 默认行为（launchd）

- 应用安装一个每用户 LaunchAgent，标记为 `bot.molt.gateway`
  （或在使用 `--profile`/`OPENCLAW_PROFILE` 时为 `bot.molt.<profile>`；支持旧版 `com.openclaw.*`）。
- 当启用本地模式时，应用确保 LaunchAgent 已加载，并在需要时启动网关。
- 日志写入 launchd 网关日志路径（在调试设置中可见）。

常用命令：

```bash
launchctl kickstart -k gui/$UID/bot.molt.gateway
launchctl bootout gui/$UID/bot.molt.gateway
```

运行命名配置文件时将标签替换为 `bot.molt.<profile>`。

## 未签名开发构建

`scripts/restart-mac.sh --no-sign` 用于没有签名密钥时的快速本地构建。为了防止 launchd 指向未签名的中继二进制文件，它：

- 写入 `~/.openclaw/disable-launchagent`。

`scripts/restart-mac.sh` 的签名运行会在标记存在时清除此覆盖。要手动重置：

```bash
rm ~/.openclaw/disable-launchagent
```

## 仅附加模式

要强制 macOS 应用**从不安装或管理 launchd**，请使用 `--attach-only`（或 `--no-launchd`）启动它。这会设置 `~/.openclaw/disable-launchagent`，
因此应用只会连接到已运行的网关。您可以在调试设置中切换相同的行为。

## 远程模式

远程模式从不启动本地网关。应用使用 SSH 隧道连接到远程主机并通过该隧道连接。

## 为什么我们更喜欢 launchd

- 登录时自动启动。
- 内置重启/KeepAlive 语义。
- 可预测的日志和监控。

如果将来再次需要真正的子进程模式，应该将其记录为单独的、明确的仅开发模式。