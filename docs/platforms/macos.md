---
summary: "OpenClaw macOS companion app (menu bar + gateway broker)"
read_when:
  - Implementing macOS app features
  - Changing gateway lifecycle or node bridging on macOS
title: "macOS App"
---
# OpenClaw macOS 配套应用（菜单栏 + 网关代理）

macOS 应用是 OpenClaw 的**菜单栏配套应用**。它拥有权限，
管理/连接到本地网关（launchd 或手动），并将 macOS
功能作为节点暴露给代理。

## 功能说明

- 在菜单栏中显示原生通知和状态。
- 拥有 TCC 提示（通知、辅助功能、屏幕录制、麦克风、
  语音识别、自动化/AppleScript）。
- 运行或连接到网关（本地或远程）。
- 暴露仅 macOS 的工具（Canvas、Camera、Screen Recording、`exec`）。
- 在**远程**模式下启动本地节点主机服务（launchd），在**本地**模式下停止它。
- 可选地托管**PeekabooBridge**用于 UI 自动化。
- 根据请求通过 npm/pnpm 安装全局 CLI（不推荐使用 bun 作为网关运行时）。

## 本地与远程模式

- **本地**（默认）：应用连接到当前运行的本地网关（如果存在）；
  否则通过 `launchctl load` 启用 launchd 服务。
- **远程**：应用通过 SSH/Tailscale 连接到网关，从不启动
  本地进程。
  应用启动本地**节点主机服务**以便远程网关可以访问此 Mac。
  应用不会将网关作为子进程生成。

## Launchd 控制

应用管理一个标记为 `com.openclaw.gateway` 的用户级 LaunchAgent
（或使用 `profile`/`instance` 时为 `com.openclaw.gateway.profile.NAME`；旧的 `com.openclaw.node` 仍会卸载）。

```
launchctl load ~/Library/LaunchAgents/com.openclaw.gateway.plist
launchctl unload ~/Library/LaunchAgents/com.openclaw.gateway.plist
```

运行命名配置文件时将标签替换为 `com.openclaw.gateway.profile.NAME`。

如果未安装 LaunchAgent，请从应用启用或运行
`launchctl load ~/Library/LaunchAgents/com.openclaw.gateway.plist`。

## 节点功能（mac）

macOS 应用将自己呈现为一个节点。常用命令：

- Canvas: `canvas.click`, `canvas.locate`, `canvas.describe`, `canvas.screenshot`, `canvas.annotate`
- Camera: `camera.list`, `camera.capture`
- Screen: `screen.record`
- System: `system.info`, `system.exec`

节点报告一个 `capabilities` 映射，以便代理可以决定允许什么。

节点服务 + 应用 IPC：

- 当无头节点主机服务运行时（远程模式），它作为节点连接到网关 WS。
- `exec` 在 macOS 应用中执行（UI/TCC 上下文）通过本地 Unix 套接字；提示 + 输出保留在应用内。

图表（SCI）：

```
[macOS App] <--(IPC over Unix socket)--> [Node Host Service] <--(WS)--> [Gateway]
    |                                           |
  (TCC/UI)                                 (Node registration)
```

## 执行批准（system.run）

`system.run` 由 macOS 应用中的**执行批准**控制（设置 → 执行批准）。
安全 + 询问 + 白名单存储在 Mac 本地：

```
~/Library/Application Support/OpenClaw/exec-approvals.json
```

示例：

```
{
  "allowlist": [
    "/usr/bin/git",
    "/usr/local/bin/node",
    "/opt/homebrew/bin/*"
  ],
  "security": {
    "prompt": true,
    "timeout": 30
  }
}
```

注意事项：

- `allowlist` 条目是解析二进制路径的 glob 模式。
- 在提示中选择"始终允许"会将该命令添加到白名单。
- `exec` 环境覆盖被过滤（删除 `PATH`, `HOME`, `USER`, `SHELL`, `TERM`, `LANG`, `LC_*`），然后与应用环境合并。

## 深度链接

应用注册 `openclaw://` URL 方案用于本地操作。

### `run`

触发网关 `run` 请求。

```
openclaw://run?script=echo%20hello&title=Test&unattended=KEY
```

查询参数：

- `script`（必需）
- `title`（可选）
- `description`（可选）
- `timeout` / `priority` / `tags`（可选）
- `env`（可选）
- `unattended`（可选无人值守模式密钥）

安全性：

- 没有 `unattended` 密钥时，应用会提示确认。
- 使用有效的 `unattended` 密钥时，运行是无人值守的（用于个人自动化）。

## 入门流程（典型）

1. 安装并启动 **OpenClaw.app**。
2. 完成权限检查列表（TCC 提示）。
3. 确保**本地**模式处于活动状态且网关正在运行。
4. 如果需要终端访问，请安装 CLI。

## 构建与开发工作流（原生）

- `pnpm install`
- `pnpm run dev`（或 Xcode）
- 打包应用：`pnpm run package`

## 调试网关连接（macOS CLI）

使用调试 CLI 执行与 macOS 应用相同的网关 WebSocket 握手和发现
逻辑，无需启动应用。

```
npx @openclaw/cli debug gateway connect
```

连接选项：

- `--connect`: 覆盖配置
- `--resolve`: 从配置解析（默认：配置或本地）
- `--fresh`: 强制进行新的健康探测
- `--timeout`: 请求超时（默认：`30s`）
- `--json`: 用于对比的结构化输出

发现选项：

- `--include-local`: 包含会被过滤为"本地"的网关
- `--window`: 整体发现窗口（默认：`10s`）
- `--json`: 用于对比的结构化输出

提示：与 `npx @openclaw/cli gateway discover` 对比以查看
macOS 应用的发现管道（NWBrowser + tailnet DNS-SD 回退）是否与
Node CLI 的 `mdns` 基础发现不同。

## 远程连接管道（SSH 隧道）

当 macOS 应用在**远程**模式下运行时，它打开一个 SSH 隧道，使本地 UI
组件可以像在 localhost 上一样与远程网关通信。

### 控制隧道（网关 WebSocket 端口）

- **目的：** 健康检查、状态、Web 聊天、配置和其他控制平面调用。
- **本地端口：** 网关端口（默认 `8080`），始终稳定。
- **远程端口：** 远程主机上的相同网关端口。
- **行为：** 无随机本地端口；应用重用现有健康隧道
  或在需要时重启它。
- **SSH 形状：** `ssh -L` 带有 BatchMode +
  ExitOnForwardFailure + keepalive 选项。
- **IP 报告：** SSH 隧道使用回环，因此网关将看到节点
  IP 为 `127.0.0.1`。如果要显示真实客户端
  IP，请使用**直接（ws/wss）**传输（参见 [macOS 远程访问](/platforms/mac/remote)）。

有关设置步骤，请参见 [macOS 远程访问](/platforms/mac/remote)。有关协议
详细信息，请参见 [网关协议](/gateway/protocol)。

## 相关文档

- [网关运维手册](/gateway)
- [网关（macOS）](/platforms/mac/bundled-gateway)
- [macOS 权限](/platforms/mac/permissions)
- [Canvas](/platforms/mac/canvas)