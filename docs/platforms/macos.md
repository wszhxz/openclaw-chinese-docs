---
summary: "OpenClaw macOS companion app (menu bar + gateway broker)"
read_when:
  - Implementing macOS app features
  - Changing gateway lifecycle or node bridging on macOS
title: "macOS App"
---
# OpenClaw macOS Companion (菜单栏 + 网关代理)

macOS 应用程序是 OpenClaw 的 **菜单栏伴侣**。它拥有权限，本地管理/连接到网关（通过 launchd 或手动），并向代理暴露 macOS 功能作为节点。

## 它的作用

- 在菜单栏中显示原生通知和状态。
- 拥有 TCC 提示（通知、辅助功能、屏幕录制、麦克风、语音识别、自动化/AppleScript）。
- 运行或连接到网关（本地或远程）。
- 暴露仅限 macOS 的工具（画布、相机、屏幕录制、`system.run`）。
- 以 **远程** 模式（launchd）启动本地节点主机服务，并在 **本地** 模式下停止它。
- 可选地托管 **PeekabooBridge** 用于 UI 自动化。
- 根据请求通过 npm/pnpm 安装全局 CLI (`openclaw`)（不建议使用 bun 作为网关运行时）。

## 本地模式 vs 远程模式

- **本地**（默认）：如果存在正在运行的本地网关，则应用程序附加到该网关；否则通过 `openclaw gateway install` 启用 launchd 服务。
- **远程**：应用程序通过 SSH/Tailscale 连接到网关，从不启动本地进程。
  应用程序启动本地 **节点主机服务**，以便远程网关可以访问此 Mac。
  应用程序不会将网关作为子进程启动。

## Launchd 控制

应用程序管理一个按用户标记的 LaunchAgent，标记为 `bot.molt.gateway`
（或 `bot.molt.<profile>` 当使用 `--profile`/`OPENCLAW_PROFILE`；遗留的 `com.openclaw.*` 仍然卸载）。

```bash
launchctl kickstart -k gui/$UID/bot.molt.gateway
launchctl bootout gui/$UID/bot.molt.gateway
```

运行命名配置文件时，将标签替换为 `bot.molt.<profile>`。

如果未安装 LaunchAgent，请从应用程序启用或运行
`openclaw gateway install`。

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

图示（SCI）：

```
Gateway -> Node Service (WS)
                 |  IPC (UDS + token + HMAC + TTL)
                 v
             Mac App (UI + TCC + system.run)
```

## 执行批准（system.run）

`system.run` 由 macOS 应用程序中的 **执行批准** 控制（设置 → 执行批准）。
安全性和允许列表存储在 Mac 的本地位置：

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

- `allowlist` 条目是已解析二进制路径的通配符模式。
- 包含 shell 控制或扩展语法的原始 shell 命令文本 (`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`) is treated as an allowlist miss and requires explicit approval (or allowlisting the shell binary).
- Choosing “Always Allow” in the prompt adds that command to the allowlist.
- `system.run` environment overrides are filtered (drops `PATH`, `DYLD_*`, `LD_*`, `NODE_OPTIONS`, `PYTHON*`, `PERL*`, `RUBYOPT`) and then merged with the app’s environment.

## Deep links

The app registers the `openclaw://` URL scheme for local actions.

### `openclaw://agent`

Triggers a Gateway `agent` request.

```bash
open 'openclaw://agent?message=Hello%20from%20deep%20link'
```

Query parameters:

- `message` (required)
- `sessionKey` (optional)
- `thinking` (optional)
- `deliver` / `to` / `channel` (optional)
- `timeoutSeconds` (optional)
- `key` (optional unattended mode key)

Safety:

- Without `key`, the app prompts for confirmation.
- Without `key`, the app enforces a short message limit for the confirmation prompt and ignores `deliver` / `to` / `channel`.
- With a valid `key`, the run is unattended (intended for personal automations).

## Onboarding flow (typical)

1. Install and launch **OpenClaw.app**.
2. Complete the permissions checklist (TCC prompts).
3. Ensure **Local** mode is active and the Gateway is running.
4. Install the CLI if you want terminal access.

## Build & dev workflow (native)

- `cd apps/macos && swift build`
- `swift run OpenClaw` (or Xcode)
- Package app: `scripts/package-mac-app.sh`

## Debug gateway connectivity (macOS CLI)

Use the debug CLI to exercise the same Gateway WebSocket handshake and discovery
logic that the macOS app uses, without launching the app.

```bash
cd apps/macos
swift run openclaw-mac connect --json
swift run openclaw-mac discover --timeout 3000 --json
```

Connect options:

- `--url <ws://host:port>`: override config
- `--mode <local|remote>`: resolve from config (default: config or local)
- `--probe`: force a fresh health probe
- `--timeout <ms>`: request timeout (default: `15000`)
- `--json`: structured output for diffing

Discovery options:

- `--include-local`: include gateways that would be filtered as “local”
- `--timeout <ms>`: overall discovery window (default: `2000`)
- `--json`: structured output for diffing

Tip: compare against `openclaw gateway discover --json` to see whether the
macOS app’s discovery pipeline (NWBrowser + tailnet DNS‑SD fallback) differs from
the Node CLI’s `dns-sd` based discovery.

## Remote connection plumbing (SSH tunnels)

When the macOS app runs in **Remote** mode, it opens an SSH tunnel so local UI
components can talk to a remote Gateway as if it were on localhost.

### Control tunnel (Gateway WebSocket port)

- **Purpose:** health checks, status, Web Chat, config, and other control-plane calls.
- **Local port:** the Gateway port (default `18789`), always stable.
- **Remote port:** the same Gateway port on the remote host.
- **Behavior:** no random local port; the app reuses an existing healthy tunnel
  or restarts it if needed.
- **SSH shape:** `ssh -N -L <local>:127.0.0.1:<remote>` with BatchMode +
  ExitOnForwardFailure + keepalive options.
- **IP reporting:** the SSH tunnel uses loopback, so the gateway will see the node
  IP as `127.0.0.1`. 如果您希望真正的客户端 IP 出现，请使用 **直接 (ws/wss)** 传输（参见 [macOS 远程访问](/platforms/mac/remote)）。

有关设置步骤，请参阅 [macOS 远程访问](/platforms/mac/remote)。有关协议详细信息，请参阅 [网关协议](/gateway/protocol)。

## 相关文档

- [网关运行手册](/gateway)
- [网关 (macOS)](/platforms/mac/bundled-gateway)
- [macOS 权限](/platforms/mac/permissions)
- [画布](/platforms/mac/canvas)