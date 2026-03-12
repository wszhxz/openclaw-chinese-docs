---
summary: "OpenClaw macOS companion app (menu bar + gateway broker)"
read_when:
  - Implementing macOS app features
  - Changing gateway lifecycle or node bridging on macOS
title: "macOS App"
---
# OpenClaw macOS Companion (菜单栏 + 网关代理)

macOS 应用程序是 OpenClaw 的**菜单栏伴侣**。它拥有权限，管理/连接到本地网关（launchd 或手动），并将 macOS 功能暴露给代理作为节点。

## 它的功能

- 在菜单栏中显示原生通知和状态。
- 拥有 TCC 提示（通知、辅助功能、屏幕录制、麦克风、语音识别、自动化/AppleScript）。
- 运行或连接到网关（本地或远程）。
- 暴露仅限 macOS 的工具（Canvas, Camera, Screen Recording, `system.run`）。
- 在**远程**模式下启动本地节点主机服务（launchd），并在**本地**模式下停止它。
- 可选地托管 **PeekabooBridge** 用于 UI 自动化。
- 根据请求通过 npm/pnpm 安装全局 CLI (`openclaw`)（不推荐使用 bun 作为网关运行时）。

## 本地模式与远程模式

- **本地**（默认）：如果存在正在运行的本地网关，应用程序将连接到该网关；否则，它将通过 `openclaw gateway install` 启用 launchd 服务。
- **远程**：应用程序通过 SSH/Tailscale 连接到网关，并且永远不会启动本地进程。
  应用程序启动本地**节点主机服务**，以便远程网关可以访问这台 Mac。
  应用程序不会将网关作为子进程生成。

## Launchd 控制

应用程序管理每个用户的 LaunchAgent，标签为 `ai.openclaw.gateway`
（或在使用 `--profile`/`OPENCLAW_PROFILE` 时为 `ai.openclaw.<profile>`；遗留的 `com.openclaw.*` 仍然卸载）。

```bash
launchctl kickstart -k gui/$UID/ai.openclaw.gateway
launchctl bootout gui/$UID/ai.openclaw.gateway
```

当运行命名配置文件时，将标签替换为 `ai.openclaw.<profile>`。

如果未安装 LaunchAgent，请从应用程序启用它或运行
`openclaw gateway install`。

## 节点功能 (mac)

macOS 应用程序作为一个节点呈现。常用命令：

- Canvas: `canvas.present`, `canvas.navigate`, `canvas.eval`, `canvas.snapshot`, `canvas.a2ui.*`
- Camera: `camera.snap`, `camera.clip`
- Screen: `screen.record`
- System: `system.run`, `system.notify`

节点报告一个 `permissions` 映射，以便代理可以决定允许什么。

节点服务 + 应用程序 IPC：

- 当无头节点主机服务运行（远程模式）时，它作为节点连接到网关 WS。
- `system.run` 在 macOS 应用程序（UI/TCC 上下文）中通过本地 Unix 套接字执行；提示和输出保留在应用程序内。

图（SCI）：

```
Gateway -> Node Service (WS)
                 |  IPC (UDS + token + HMAC + TTL)
                 v
             Mac App (UI + TCC + system.run)
```

## 执行批准 (system.run)

`system.run` 由 macOS 应用程序中的**执行批准**控制（设置 → 执行批准）。
安全 + 询问 + 允许列表存储在 Mac 上的本地位置：

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

注意事项：

- `allowlist` 条目是已解析二进制路径的 glob 模式。
- 包含 shell 控制或扩展语法的原始 shell 命令文本 (`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`) is treated as an allowlist miss and requires explicit approval (or allowlisting the shell binary).
- Choosing “Always Allow” in the prompt adds that command to the allowlist.
- `system.run` environment overrides are filtered (drops `PATH`, `DYLD_*`, `LD_*`, `NODE_OPTIONS`, `PYTHON*`, `PERL*`, `RUBYOPT`, `SHELLOPTS`, `PS4`) and then merged with the app’s environment.
- For shell wrappers (`bash|sh|zsh ... -c/-lc`), request-scoped environment overrides are reduced to a small explicit allowlist (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
- For allow-always decisions in allowlist mode, known dispatch wrappers (`env`, `nice`, `nohup`, `stdbuf`, `timeout`) persist inner executable paths instead of wrapper paths. If unwrapping is not safe, no allowlist entry is persisted automatically.

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

## State dir placement (macOS)

Avoid putting your OpenClaw state dir in iCloud or other cloud-synced folders.
Sync-backed paths can add latency and occasionally cause file-lock/sync races for
sessions and credentials.

Prefer a local non-synced state path such as:

```bash
OPENCLAW_STATE_DIR=~/.openclaw
```

If `openclaw doctor` detects state under:

- `~/Library/Mobile Documents/com~apple~CloudDocs/...`
- `~/Library/CloudStorage/...`

it will warn and recommend moving back to a local path.

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
  IP as `127.0.0.1`。如果您希望客户端的真实 IP 出现，请使用 **Direct (ws/wss)** 传输（参见 [macOS 远程访问](/platforms/mac/remote)）。

有关设置步骤，请参阅 [macOS 远程访问](/platforms/mac/remote)。有关协议详情，请参阅 [网关协议](/gateway/protocol)。

## 相关文档

- [网关手册](/gateway)
- [网关 (macOS)](/platforms/mac/bundled-gateway)
- [macOS 权限](/platforms/mac/permissions)
- [Canvas](/platforms/mac/canvas)