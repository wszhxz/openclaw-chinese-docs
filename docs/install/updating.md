---
summary: "Updating OpenClaw safely (global install or source), plus rollback strategy"
read_when:
  - Updating OpenClaw
  - Something breaks after an update
title: "Updating"
---
# 更新

OpenClaw 正在快速发展（预“1.0”）。将更新视为交付基础设施：更新 → 运行检查 → 重启（或使用 `openclaw update`，它会自动重启）→ 验证。

## 推荐：重新运行网站安装程序（原地升级）

**首选** 的更新路径是从网站重新运行安装程序。它会检测现有安装，进行原地升级，并在需要时运行 `openclaw doctor`。

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

注意：

- 如果您不想再次运行入门向导，请添加 `--no-onboard`。
- 对于 **源码安装**，使用：
  ```bash
  curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --no-onboard
  ```
  安装程序仅在仓库干净的情况下才会执行 `git pull --rebase`。
- 对于 **全局安装**，脚本会在内部使用 `npm install -g openclaw@latest`。
- 兼容性说明：`clawdbot` 仍然可用作为兼容性适配器。

## 更新前

- 确知您的安装方式：**全局**（npm/pnpm）与 **源码**（git clone）。
- 确知您的网关是如何运行的：**前台终端**与 **受监督服务**（launchd/systemd）。
- 备份您的定制：
  - 配置：`~/.openclaw/openclaw.json`
  - 凭据：`~/.openclaw/credentials/`
  - 工作区：`~/.openclaw/workspace`

## 更新（全局安装）

全局安装（选择一个）：

```bash
npm i -g openclaw@latest
```

```bash
pnpm add -g openclaw@latest
```

我们**不推荐**使用 Bun 作为网关运行时（存在 WhatsApp/Telegram 的 bug）。

要切换更新渠道（git + npm 安装）：

```bash
openclaw update --channel beta
openclaw update --channel dev
openclaw update --channel stable
```

使用 `--tag <dist-tag|version>` 进行一次性安装标签/版本。

参见 [开发渠道](/install/development-channels) 了解渠道语义和发布说明。

注意：在 npm 安装中，网关会在启动时记录更新提示（检查当前渠道标签）。通过 `update.checkOnStart: false` 禁用。

然后：

```bash
openclaw doctor
openclaw gateway restart
openclaw health
```

注意：

- 如果您的网关作为服务运行，建议使用 `openclaw gateway restart` 而不是直接终止 PID。
- 如果您固定在某个特定版本，请参见下方的“回滚/固定”。

## 更新 (`openclaw update`)

对于 **源码安装**（git checkout），建议使用：

```bash
openclaw update
```

它会运行一个相对安全的更新流程：

- 需要干净的工作树。
- 切换到选定的渠道（标签或分支）。
- 获取并变基到配置的上游（开发渠道）。
- 安装依赖、构建、构建控制界面并运行 `openclaw doctor`。
- 默认情况下会重启网关（使用 `--no-restart` 跳过）。

如果您是通过 **npm/pnpm** 安装的（没有 git 元数据），`openclaw update` 将尝试通过包管理器进行更新。如果无法检测到安装，请使用“更新（全局安装）”替代。

## 更新（控制界面 / RPC）

控制界面具有 **更新并重启** 功能（RPC: `update.run`)。它会：

1. 运行与 `openclaw update` 相同的源码更新流程（仅限 git checkout）。
2. 写入一个带有结构化报告的重启哨兵（stdout/stderr 尾部）。
3. 重启网关并向最后一个活动会话发送报告。

如果变基失败，网关会中止并重启而不应用更新。

## 更新（从源码）

从仓库检出：

首选：

```bash
openclaw update
```

手动（等效）：

```bash
git pull
pnpm install
pnpm build
pnpm ui:build # auto-installs UI deps on first run
openclaw doctor
openclaw health
```

注意：

- `pnpm build` 在您运行打包的 `openclaw` 二进制文件（[`openclaw.mjs`](https://github.com/openclaw/openclaw/blob/main/openclaw.mjs)）或使用 Node 运行 `dist/` 时很重要。
- 如果您从仓库检出但没有全局安装，请使用 `pnpm openclaw ...` 进行 CLI 命令。
- 如果您直接从 TypeScript (`pnpm openclaw ...`) 运行，通常不需要重新构建，但**配置迁移仍然适用** → 运行 doctor。
- 在全局和 git 安装之间切换很容易：安装另一种类型，然后运行 `openclaw doctor` 以重写网关服务入口点到当前安装。

## 总是运行：`openclaw doctor`

Doctor 是“安全更新”命令。它故意设计得简单：修复 + 迁移 + 警告。

注意：如果您是 **源码安装**（git checkout），`openclaw doctor` 会先询问是否运行 `openclaw update`。

它通常会执行的操作：

- 迁移已弃用的配置键/旧版配置文件位置。
- 审核 DM 策略并在发现危险的“开放”设置时发出警告。
- 检查网关健康状况并提供重启选项。
- 检测并迁移旧版网关服务（launchd/systemd；旧版 schtasks）到当前 OpenClaw 服务。
- 在 Linux 上，确保 systemd 用户持久化（以便网关在注销后仍能运行）。

详情：[Doctor](/gateway/doctor)

## 启动 / 停止 / 重启网关

CLI（适用于所有操作系统）：

```bash
openclaw gateway status
openclaw gateway stop
openclaw gateway restart
openclaw gateway --port 18789
openclaw logs --follow
```

如果您是受监督的服务：

- macOS launchd（应用程序捆绑的 LaunchAgent）：`launchctl kickstart -k gui/$UID/bot.molt.gateway`（使用 `bot.molt.<profile>`；旧版 `com.openclaw.*` 仍然有效）
- Linux systemd 用户服务：`systemctl --user restart openclaw-gateway[-<profile>].service`
- Windows (WSL2)：`systemctl --user restart openclaw-gateway[-<profile>].service`
  - `launchctl`/`systemctl` 仅在服务已安装时有效；否则运行 `openclaw gateway install`。

运行手册 + 精确的服务标签：[网关运行手册](/gateway)

## 回滚 / 固定（当出现问题时）

### 固定（全局安装）

安装一个已知良好的版本（将 `<version>` 替换为最后正常工作的版本）：

```bash
npm i -g openclaw@<version>
```

```bash
pnpm add -g openclaw@<version>
```

提示：要查看当前发布的版本，请运行 `npm view openclaw version`。

然后重启并重新运行 doctor：

```bash
openclaw doctor
openclaw gateway restart
```

### 按日期固定（源码）

选择一个日期的提交（示例：“2026-01-01 的主分支状态”）：

```bash
git fetch origin
git checkout "$(git rev-list -n 1 --before=\"2026-01-01\" origin/main)"
```

然后重新安装依赖并重启：

```bash
pnpm install
pnpm build
openclaw gateway restart
```

如果您稍后想回到最新版本：

```bash
git checkout main
git pull
```

## 如果您卡住了

- 再次运行 `openclaw doctor` 并仔细阅读输出（它通常会告诉您如何修复）。
- 检查：[故障排除](/gateway/troubleshooting)
- 在 Discord 中提问：https://discord.gg/clawd