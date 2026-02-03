---
summary: "OpenClaw macOS companion app (menu bar + gateway broker)"
read_when:
  - Implementing macOS app features
  - Changing gateway lifecycle or node bridging on macOS
title: "macOS App"
---
# OpenClaw macOS 伴侣（菜单栏 + 网关代理）

macOS 应用是 OpenClaw 的 **菜单栏伴侣**，它拥有权限，管理/连接本地网关（launchd 或手动启动），并将 macOS 的功能暴露给代理作为节点。

## 它的功能

- 在菜单栏中显示原生通知和状态。
- 管理 TCC 提示（通知、辅助功能、屏幕录制、麦克风、语音识别、自动化/AppleScript）。
- 运行或连接到网关（本地或远程）。
- 暴露 macOS 专属工具（画布、摄像头、屏幕录制、`system.run`）。
- 以 **远程** 模式启动本地节点主机服务（launchd），并在 **本地** 模式下停止它。
- 可选地托管 **PeekabooBridge** 用于 UI 自动化。
- 在请求时通过 npm/pnpm 安装全局 CLI（`openclaw`）（不推荐使用 bun 作为网关运行时）。

## 本地与远程模式

- **本地**（默认）：如果存在运行中的本地网关，应用会连接到它；否则通过 `openclaw gateway install` 启用 launchd 服务。
- **远程**：应用通过 SSH/Tailscale 连接到网关，且不会启动本地进程。
  应用启动本地 **节点主机服务**，以便远程网关可以访问这台 Mac。
  应用不会将网关作为子进程启动。

## launchd 控制

应用管理一个用户级的 LaunchAgent，标记为 `bot.molt.gateway`（或 `bot.molt.<profile>` 当使用 `--profile`/`OPENCLAW_PROFILE`；旧版 `com.openclaw.*` 仍会卸载）。

```bash
launchctl kickstart -k gui/$UID/bot.molt.gateway
launchctl bootout gui/$UID/bot.molt.gateway
```

在运行命名配置文件时，将标签替换为 `bot.molt.<profile>`。

如果 LaunchAgent 未安装，可通过应用启用，或运行 `openclaw gateway install`。

## 节点功能（mac）

macOS 应用以节点身份呈现。常用命令：

- 画布：`canvas.present`、`canvas.navigate`、`canvas.eval`、`canvas.snapshot`、`canvas.a2ui.*`
- 摄像头：`camera.snap`、`camera.clip`
- 屏幕：`screen.record`
- 系统：`system.run`、`system.notify`

节点报告一个 `permissions` 映射，以便代理决定哪些操作被允许。

节点服务 + 应用 IPC：

- 当无头节点主机服务运行（远程模式）时，它会连接到网关 WebSocket 作为节点。
- `system.run` 在 macOS 应用（UI/TCC 上下文）中通过本地 Unix 套接字执行；提示和输出均保留在应用内。

图示（SCI）：

```
网关 -> 节点服务（WS）
                 |  IPC（UDS + token + HMAC + TTL）
                 v
             Mac 应用（UI + TCC + system.run）
```

## 执行批准（system.run）

`system.run` 由 macOS 应用中的 **执行批准** 控制（设置 → 执行批准）。
安全 + 询问 + 允许列表存储在 Mac 上的以下路径：

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

说明：

- `allowlist` 条目是解析后的二进制路径的通配符模式。
- 在提示中选择“始终允许”会将该命令添加到允许列表中。
- `system.run` 环境变量覆盖会被过滤（删除 `PATH`、`DYLD_*`、`LD_*`、`NODE_OPTIONS`、`PYTHON*`、`PERL*`、`RUBYOPT`），然后与应用的环境变量合并。

## 深度链接

应用注册了 `openclaw://` URL 方案用于本地操作。

### `openclaw://agent`

触发网关的 `agent` 请求。

```bash
open 'openclaw://agent?message=Hello%20from%20deep%20link'
```

查询参数：

- `message`（必需）
- `sessionKey`（可选）
- `thinking`（可选）
- `deliver` / `to` / `channel`（可选）
- `timeoutSeconds`（可选）
- `key`（可选的无人值守模式密钥）

安全性：

- 没有 `key` 时，应用会提示确认。
- 有有效 `key` 时，运行为无人值守模式（适用于个人自动化）。

## 入门流程（典型）

1. 安装并启动 **OpenClaw.app**。
2. 完成权限检查清单（TCC 提示）。
3. 确保 **本地** 模式已激活且