---
summary: "Uninstall OpenClaw completely (CLI, service, state, workspace)"
read_when:
  - You want to remove OpenClaw from a machine
  - The gateway service is still running after uninstall
title: "Uninstall"
---
# 卸载

两种路径：

- **简易路径** 如果 `openclaw` 仍然安装。
- **手动服务移除** 如果 CLI 已经消失但服务仍在运行。

## 简易路径（CLI 仍已安装）

推荐：使用内置卸载程序：

```bash
openclaw uninstall
```

非交互式（自动化 / npx）：

```bash
openclaw uninstall --all --yes --non-interactive
npx -y openclaw uninstall --all --yes --non-interactive
```

手动步骤（相同结果）：

1. 停止网关服务：

```bash
openclaw gateway stop
```

2. 卸载网关服务（launchd/systemd/schtasks）：

```bash
openclaw gateway uninstall
```

3. 删除状态 + 配置：

```bash
rm -rf "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
```

如果您将 `OPENCLAW_CONFIG_PATH` 设置为状态目录之外的自定义位置，请删除该文件。

4. 删除您的工作区（可选，移除代理文件）：

```bash
rm -rf ~/.openclaw/workspace
```

5. 移除 CLI 安装（选择您使用的安装方式）：

```bash
npm rm -g openclaw
pnpm remove -g openclaw
bun remove -g openclaw
```

6. 如果您安装了 macOS 应用程序：

```bash
rm -rf /Applications/OpenClaw.app
```

注意事项：

- 如果您使用了配置文件 (`--profile` / `OPENCLAW_PROFILE`)，请对每个状态目录重复步骤 3（默认值为 `~/.openclaw-<profile>`）。
- 在远程模式下，状态目录位于 **网关主机** 上，因此也需要在那里运行步骤 1-4。

## 手动服务移除（CLI 未安装）

如果网关服务继续运行但 `openclaw` 缺失，请使用此方法。

### macOS (launchd)

默认标签是 `bot.molt.gateway`（或 `bot.molt.<profile>`；旧版 `com.openclaw.*` 可能仍然存在）：

```bash
launchctl bootout gui/$UID/bot.molt.gateway
rm -f ~/Library/LaunchAgents/bot.molt.gateway.plist
```

如果您使用了配置文件，请将标签和 plist 名称替换为 `bot.molt.<profile>`。如果存在任何旧版 `com.openclaw.*` plist，请删除它们。

### Linux (systemd 用户单元)

默认单元名称是 `openclaw-gateway.service`（或 `openclaw-gateway-<profile>.service`）：

```bash
systemctl --user disable --now openclaw-gateway.service
rm -f ~/.config/systemd/user/openclaw-gateway.service
systemctl --user daemon-reload
```

### Windows (计划任务)

默认任务名称是 `OpenClaw Gateway`（或 `OpenClaw Gateway (<profile>)`）。
任务脚本位于您的状态目录下。

```powershell
schtasks /Delete /F /TN "OpenClaw Gateway"
Remove-Item -Force "$env:USERPROFILE\.openclaw\gateway.cmd"
```

如果您使用了配置文件，请删除匹配的任务名称和 `~\.openclaw-<profile>\gateway.cmd`。

## 正常安装与源代码检出

### 正常安装（install.sh / npm / pnpm / bun）

如果您使用了 `https://openclaw.ai/install.sh` 或 `install.ps1`，CLI 是通过 `npm install -g openclaw@latest` 安装的。
使用 `npm rm -g openclaw` 移除它（如果您是通过 `pnpm remove -g` / `bun remove -g` 安装的，则使用这些命令）。

### 源代码检出（git clone）

如果您从仓库检出运行 (`git clone` + `openclaw ...` / `bun run openclaw ...`)：

1. 在删除仓库之前卸载网关服务（使用上述简易路径或手动服务移除）。
2. 删除仓库目录。
3. 如上所示删除状态 + 工作区。