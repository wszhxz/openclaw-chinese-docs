---
summary: "Updating OpenClaw safely (global install or source), plus rollback strategy"
read_when:
  - Updating OpenClaw
  - Something breaks after an update
title: "Updating"
---
# 更新

OpenClaw 发展迅速（pre "1.0"）。对待更新要像对待发布基础设施一样：更新 → 运行检查 → 重启（或使用 `openclaw update`，它会重启）→ 验证。

## 推荐：重新运行网站安装程序（原地升级）

**首选**的更新路径是从网站重新运行安装程序。它会检测现有安装，原地升级，并在需要时运行 `openclaw doctor`。

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

注意：

- 如果不想再次运行引导向导，请添加 `--no-onboard`。
- 对于 **源码安装**，使用：

  ```bash
  curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --no-onboard
  ```

  仅当 repo 干净时，安装程序才会 `git pull --rebase`。

- 对于 **全局安装**，脚本底层使用 `npm install -g openclaw@latest`。
- 遗留说明：`clawdbot` 作为兼容性 shim 仍然可用。

## 更新前

- 了解你的安装方式：**全局** (npm/pnpm) 还是 **源码** (git clone)。
- 了解你的 Gateway 运行方式：**前台终端** 还是 **托管服务** (launchd/systemd)。
- 快照你的定制内容：
  - 配置：`~/.openclaw/openclaw.json`
  - 凭证：`~/.openclaw/credentials/`
  - 工作区：`~/.openclaw/workspace`

## 更新（全局安装）

全局安装（任选其一）：

```bash
npm i -g openclaw@latest
```

```bash
pnpm add -g openclaw@latest
```

我们 **不** 推荐将 Bun 用于 Gateway 运行时（WhatsApp/Telegram bugs）。

切换更新渠道（git + npm 安装）：

```bash
openclaw update --channel beta
openclaw update --channel dev
openclaw update --channel stable
```

使用 `--tag <dist-tag|version>` 进行一次性安装标签/版本。

参见 [开发渠道](/install/development-channels) 了解渠道语义和发布说明。

注意：在 npm 安装上，gateway 会在启动时记录更新提示（检查当前渠道标签）。可通过 `update.checkOnStart: false` 禁用。

### 核心自动更新器（可选）

自动更新器默认 **关闭**，它是核心 Gateway 功能（不是插件）。

```json
{
  "update": {
    "channel": "stable",
    "auto": {
      "enabled": true,
      "stableDelayHours": 6,
      "stableJitterHours": 12,
      "betaCheckIntervalHours": 1
    }
  }
}
```

行为：

- `stable`：当看到新版本时，OpenClaw 等待 `stableDelayHours`，然后在 `stableJitterHours` 内应用确定的按安装抖动（spread rollout）。
- `beta`：按 `betaCheckIntervalHours` 频率检查（默认：每小时），并在有更新时应用。
- `dev`：不自动应用；使用手动 `openclaw update`。

使用 `openclaw update --dry-run` 在启用自动化之前预览更新操作。

然后：

```bash
openclaw doctor
openclaw gateway restart
openclaw health
```

注意：

- 如果你的 Gateway 作为服务运行，`openclaw gateway restart` 优于杀死 PIDs。
- 如果你锁定在特定版本，请参阅下面的“回滚 / 锁定”。

## 更新（`openclaw update`）

对于 **源码安装**（git checkout），推荐：

```bash
openclaw update
```

它运行一个较安全的更新流程：

- 需要干净的 worktree。
- 切换到选定的渠道（tag 或 branch）。
- 获取 + 变基到配置的上游（dev 渠道）。
- 安装依赖，构建，构建 Control UI，并运行 `openclaw doctor`。
- 默认重启 gateway（使用 `--no-restart` 跳过）。

如果你通过 **npm/pnpm** 安装（无 git 元数据），`openclaw update` 将尝试通过你的包管理器更新。如果无法检测安装，请改用“更新（全局安装）”。

## 更新（Control UI / RPC）

Control UI 具有 **Update & Restart**（RPC：`update.run`）。它：

1. 运行与 `openclaw update` 相同的源码更新流程（仅 git checkout）。
2. 写入带有结构化报告的重启哨兵（stdout/stderr tail）。
3. 重启 gateway 并向最后一个活动会话 ping 报告。

如果变基失败，gateway 将中止并在不应用更新的情况下重启。

## 更新（源码）

从 repo checkout：

推荐：

```bash
openclaw update
```

手动（大致等效）：

```bash
git pull
pnpm install
pnpm build
pnpm ui:build # auto-installs UI deps on first run
openclaw doctor
openclaw health
```

注意：

- 当你运行打包的 `openclaw` 二进制文件（[`openclaw.mjs`](https://github.com/openclaw/openclaw/blob/main/openclaw.mjs)）或使用 Node 运行 `dist/` 时，`pnpm build` 很重要。
- 如果你从 repo checkout 运行 without 全局安装，使用 `pnpm openclaw ...` 用于 CLI 命令。
- 如果你直接从 TypeScript 运行（`pnpm openclaw ...`），通常无需重建，但 **配置迁移仍然适用** → 运行 doctor。
- 在全局和 git 安装之间切换很容易：安装另一种风味，然后运行 `openclaw doctor` 以便 gateway 服务入口点重写为当前安装。

## 始终运行：`openclaw doctor`

Doctor 是“安全更新”命令。它故意很无聊：修复 + 迁移 + 警告。

注意：如果你在 **源码安装**（git checkout）上，`openclaw doctor` 将提供先运行 `openclaw update` 的选项。

典型操作：

- 迁移已弃用的配置键/遗留配置文件位置。
- 审计 DM 策略并在危险的 "open" 设置上警告。
- 检查 Gateway 健康状态并可提供重启。
- 检测并迁移旧的 gateway 服务（launchd/systemd; 遗留 schtasks）到当前 OpenClaw 服务。
- 在 Linux 上，确保 systemd 用户驻留（以便 Gateway 在注销后存活）。

详情：[Doctor](/gateway/doctor)

## 启动 / 停止 / 重启 Gateway

CLI（无论 OS 如何均有效）：

```bash
openclaw gateway status
openclaw gateway stop
openclaw gateway restart
openclaw gateway --port 18789
openclaw logs --follow
```

如果你被托管：

- macOS launchd (app-bundled LaunchAgent): `launchctl kickstart -k gui/$UID/ai.openclaw.gateway` (使用 `ai.openclaw.<profile>`; 遗留 `com.openclaw.*` 仍然有效)
- Linux systemd 用户服务：`systemctl --user restart openclaw-gateway[-<profile>].service`
- Windows (WSL2): `systemctl --user restart openclaw-gateway[-<profile>].service`
  - `launchctl`/`systemctl` 仅在服务安装时有效；否则运行 `openclaw gateway install`。

Runbook + 确切服务标签：[Gateway runbook](/gateway)

## 回滚 / 锁定（当出现问题时）

### 锁定（全局安装）

安装已知稳定版本（将 `<version>` 替换为最后一个有效版本）：

```bash
npm i -g openclaw@<version>
```

```bash
pnpm add -g openclaw@<version>
```

提示：查看当前发布版本，运行 `npm view openclaw version`。

然后重启 + 重新运行 doctor：

```bash
openclaw doctor
openclaw gateway restart
```

### 按日期锁定（源码）

选择一个日期的 commit（示例："2026-01-01 的 main 状态"）：

```bash
git fetch origin
git checkout "$(git rev-list -n 1 --before=\"2026-01-01\" origin/main)"
```

然后重新安装依赖 + 重启：

```bash
pnpm install
pnpm build
openclaw gateway restart
```

如果你想稍后回到最新版：

```bash
git checkout main
git pull
```

## 如果卡住了

- 再次运行 `openclaw doctor` 并仔细阅读输出（它通常会告诉你修复方法）。
- 检查：[故障排除](/gateway/troubleshooting)
- 在 Discord 询问：[https://discord.gg/clawd](https://discord.gg/clawd)