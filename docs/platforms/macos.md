---
summary: "OpenClaw macOS companion app (menu bar + gateway broker)"
read_when:
  - Implementing macOS app features
  - Changing gateway lifecycle or node bridging on macOS
title: "macOS App"
---
# OpenClaw macOS Companion (菜单栏 + 网关代理)

macOS 应用程序是 OpenClaw 的 **菜单栏伴侣**。它拥有权限，本地管理/连接到网关（launchd 或手动），并向代理暴露 macOS 功能作为节点。

## 它的作用

- 在菜单栏中显示原生通知和状态。
- 拥有 TCC 提示（通知、辅助功能、屏幕录制、麦克风、语音识别、自动化/AppleScript）。
- 运行或连接到网关（本地或远程）。
- 暴露仅限 macOS 的工具（画布、相机、屏幕录制、`system.run`）。
- 以 **远程** 模式（launchd）启动本地节点主机服务，并在 **本地** 模式下停止它。
- 可选地托管 **PeekabooBridge** 用于 UI 自动化。
- 根据请求通过 npm/pnpm 安装全局 CLI (`openclaw`)（不建议使用 bun 作为网关运行时）。

## 本地与远程模式

- **本地**（默认）：如果存在正在运行的本地网关，则应用程序附加到该网关；否则通过 `openclaw gateway install` 启用 launchd 服务。
- **远程**：应用程序通过 SSH/Tailscale 连接到网关，从不启动本地进程。
  应用程序启动本地 **节点主机服务** 以便远程网关可以访问此 Mac。
  应用程序不会将网关作为子进程生成。

## Launchd 控制

应用程序管理一个带有标签 `bot.molt.gateway` 的每个用户的 LaunchAgent
（或在使用 `--profile`/`OPENCLAW_PROFILE` 时为 `bot.molt.<profile>`；遗留的 `com.openclaw.*` 仍然卸载）。

```bash
launchctl kickstart -k gui/$UID/bot.molt.gateway
launchctl bootout gui/$UID/bot.molt.gateway
```

在运行命名配置文件时，将标签替换为 `bot.molt.<profile>`。

如果未安装 LaunchAgent，请从应用程序启用或运行 `openclaw gateway install`。

## 节点功能（mac）

macOS 应用程序将其自身呈现为节点。常用命令：

- 画布：`canvas.present`, `canvas.navigate`, `canvas.eval`, `canvas.snapshot`, `canvas.a2ui.*`
- 相机：`camera.snap`, `camera.clip`
- 屏幕：`screen.record`
- 系统：`system.run`, `system.notify`

节点报告一个 `permissions` 映射，以便代理决定允许的操作。

节点服务 + 应用程序 IPC：

- 当无头节点主机服务正在运行（远程模式）时，它作为节点连接到网关 WS。
- `system.run` 在 macOS 应用程序（UI/TCC 上下文）中通过本地 Unix 套接字执行；提示和输出保留在应用程序中。

图表（SCI）：

```
Gateway -> Node Service (WS)
                 |  IPC (UDS + token + HMAC + TTL)
                 v
             Mac App (UI + TCC + system.run)
```

## 执行批准（system.run）

`system.run` 由 macOS 应用程序中的 **执行批准** 控制（设置 → 执行批准）。
安全性和询问列表存储在 Mac 的本地位置：

```
~/.openclaw/exec-approvals.json
```

示例：

```json
{
  "version": 1,
  "defaults": {
    "security": "deny",
    "ask": "on-miss"
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "allowlist": [{ "pattern": "/opt/homebrew/bin/rg" }]
    }
  }
}
```

注意：

- `allowlist` 条目是已解析二进制路径的 glob 模式。
- 在提示中选择“始终允许”会将该命令添加到允许列表。
- `system.run` 环境覆盖被过滤（丢弃 `PATH`, `DYLD_*`, `LD_*`, `NODE_OPTIONS`, `PYTHON*`, `PERL*`, `RUBYOPT`），然后与应用程序的环境合并。

## 深链

应用程序注册了 `openclaw://` URL 方案用于本地操作。

### `openclaw://agent`

触发网关 `agent` 请求。

```bash
open 'openclaw://agent?message=Hello%20from%20deep%20link'
```

查询参数：

- `message`（必需）
- `sessionKey`（可选）
- `thinking`（可选）
- `deliver` / `to` / `channel`（可选）
- `timeoutSeconds`（可选）
- `key`（可选非交互模式密钥）

安全性：

- 没有 `key`，应用程序会提示确认。
- 使用有效的 `key`，运行将处于非交互模式（适用于个人自动化）。

## 入门流程（典型）

1. 安装并启动 **OpenClaw.app**。
2. 完成权限检查表（TCC 提示）。
3. 确保 **本地** 模式处于活动状态且网关正在运行。
4. 如果需要终端访问，请安装 CLI。

## 构建与开发工作流（原生）

- `cd apps/macos && swift build`
- `swift run OpenClaw`（或 Xcode）
- 打包应用程序：`scripts/package-mac-app.sh`

## 调试网关连接性（macOS CLI）

使用调试 CLI 来练习与 macOS 应用程序相同的网关 WebSocket 握手和发现逻辑，而不启动应用程序。

```bash
cd apps/macos
swift run openclaw-mac connect --json
swift run openclaw-mac discover --timeout 3000 --json
```

连接选项：

- `--url <ws://host:port>`：覆盖配置
- `--mode <local|remote>`：从配置解析（默认：配置或本地）
- `--probe`：强制进行新的健康探测
- `--timeout <ms>`：请求超时（默认：`15000`）
- `--json`：结构化输出用于差异比较

发现选项：

- `--include-local`：包括会被过滤为“本地”的网关
- `--timeout <ms>`：总体发现窗口（默认：`2000`）
- `--json`：结构化输出用于差异比较

提示：与 `openclaw gateway discover --json` 进行比较，查看 macOS 应用程序的发现管道（NWBrowser + tailnet DNS-SD 备用）是否与 Node CLI 的 `dns-sd` 基于发现不同。

## 远程连接管道（SSH 隧道）

当 macOS 应用程序以 **远程** 模式运行时，它打开一个 SSH 隧道，使本地 UI 组件能够像在本地主机上一样与远程网关通信。

### 控制隧道（网关 WebSocket 端口）

- **目的**：健康检查、状态、Web 聊天、配置和其他控制平面调用。
- **本地端口**：网关端口（默认 `18789`），始终稳定。
- **远程端口**：远程主机上的相同网关端口。
- **行为**：没有随机本地端口；应用程序重用现有的健康隧道或根据需要重新启动它。
- **SSH 形状**：`ssh -N -L <local>:127.0.0.1:<remote>` 带有 BatchMode +
  ExitOnForwardFailure + 保持活动选项。
- **IP 报告**：SSH 隧道使用环回，因此网关会看到节点 IP 为 `127.0.0.1`。如果您希望真实的客户端 IP 出现，请使用 **直接 (ws/wss)** 传输（参见 [macOS 远程访问](/platforms/mac/remote)）。

有关设置步骤，请参阅 [macOS 远程访问](/platforms/mac/remote)。有关协议详细信息，请参阅 [网关协议](/gateway/protocol)。

## 相关文档

- [网关运行手册](/gateway)
- [网关（macOS）](/platforms/mac/bundled-gateway)
- [macOS 权限](/platforms/mac/permissions)
- [画布](/platforms/mac/canvas)