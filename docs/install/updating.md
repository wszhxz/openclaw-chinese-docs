---
summary: "Updating OpenClaw safely (global install or source), plus rollback strategy"
read_when:
  - Updating OpenClaw
  - Something breaks after an update
title: "Updating"
---
# 更新

OpenClaw 正在快速迭代（尚处于“1.0”之前阶段）。请将更新视同部署基础设施：更新 → 运行检查 → 重启（或使用 `openclaw update`，该命令会自动重启）→ 验证。

## 推荐方式：重新运行网站安装程序（就地升级）

**首选**的更新路径是从官网重新运行安装程序。它能自动识别已存在的安装、执行就地升级，并在必要时运行 `openclaw doctor`。

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

注意事项：

- 若不希望再次运行新手引导向导，请添加 `--no-onboard`。
- 对于 **源码安装**，请使用：

  ```bash
  curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --no-onboard
  ```

  安装程序 **仅当** 代码仓库处于干净状态时才会执行 `git pull --rebase`。

- 对于 **全局安装**，脚本底层使用的是 `npm install -g openclaw@latest`。
- 兼容性说明：`clawdbot` 仍作为兼容性适配层保留可用。

## 更新前准备

- 明确您的安装方式：**全局安装**（npm/pnpm）还是 **源码安装**（git clone）。
- 明确您的网关运行方式：**前台终端运行** 还是 **受监管的服务**（launchd/systemd）。
- 备份您的定制化配置：
  - 配置文件：`~/.openclaw/openclaw.json`
  - 凭据信息：`~/.openclaw/credentials/`
  - 工作区：`~/.openclaw/workspace`

## 更新（全局安装）

全局安装（任选其一）：

```bash
npm i -g openclaw@latest
```

```bash
pnpm add -g openclaw@latest
```

我们 **不推荐** 使用 Bun 作为网关运行时环境（存在 WhatsApp/Telegram 相关 Bug）。

切换更新通道（适用于 git + npm 安装）：

```bash
openclaw update --channel beta
openclaw update --channel dev
openclaw update --channel stable
```

使用 `--tag <dist-tag|version>` 可指定一次性安装的标签或版本。

详见 [开发通道](/install/development-channels)，了解各通道语义及发布说明。

注意：在 npm 安装中，网关会在启动时记录一条更新提示日志（检查当前通道标签）。可通过 `update.checkOnStart: false` 禁用该功能。

### 核心自动更新器（可选）

自动更新器 **默认关闭**，属于网关核心功能（非插件）。

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

行为说明：

- `stable`：检测到新版本后，OpenClaw 将等待 `stableDelayHours`，随后在 `stableJitterHours` 内应用确定性的每安装实例抖动（实现分批灰度发布）。
- `beta`：按 `betaCheckIntervalHours` 的频率（默认：每小时）检查更新，并在有可用更新时自动应用。
- `dev`：不自动应用更新；需手动执行 `openclaw update`。

使用 `openclaw update --dry-run` 可在启用自动化前预览更新操作。

然后执行：

```bash
openclaw doctor
openclaw gateway restart
openclaw health
```

注意事项：

- 若您的网关以服务形式运行，建议优先使用 `openclaw gateway restart`，而非直接终止进程 PID。
- 若您已固定至特定版本，请参阅下方“回滚 / 版本锁定”。

## 更新（`openclaw update`）

对于 **源码安装**（git checkout），推荐使用：

```bash
openclaw update
```

它执行一套相对安全的更新流程：

- 要求工作树处于干净状态。
- 切换至所选通道（标签或分支）。
- 从已配置的上游（dev 通道）拉取并变基（fetch + rebase）。
- 安装依赖、构建项目、构建控制台 UI，并运行 `openclaw doctor`。
- 默认重启网关（使用 `--no-restart` 可跳过此步骤）。

若您是通过 **npm/pnpm** 安装（无 git 元数据），则 `openclaw update` 将尝试通过包管理器更新。若无法识别安装来源，请改用“更新（全局安装）”。

## 更新（控制台 UI / RPC）

控制台 UI 提供 **更新并重启** 功能（RPC 接口：`update.run`）。其行为如下：

1. 执行与 `openclaw update`（仅限 git checkout）相同的源码更新流程。
2. 写入一个重启标记文件，并附带结构化报告（含 stdout/stderr 尾部日志）。
3. 重启网关，并向最近活跃会话推送该报告。

若变基（rebase）失败，网关将中止更新并重启，不应用任何变更。

## 更新（源码安装）

在代码仓库目录中执行：

推荐方式：

```bash
openclaw update
```

手动方式（功能等效）：

```bash
git pull
pnpm install
pnpm build
pnpm ui:build # auto-installs UI deps on first run
openclaw doctor
openclaw health
```

注意事项：

- 当您运行打包后的 `openclaw` 二进制文件（[`openclaw.mjs`](https://github.com/openclaw/openclaw/blob/main/openclaw.mjs)）或使用 Node 直接运行 `dist/` 时，`pnpm build` 的设置至关重要。
- 若您未进行全局安装，而是直接从仓库目录运行，请对 CLI 命令使用 `pnpm openclaw ...`。
- 若您直接以 TypeScript 方式运行（`pnpm openclaw ...`），通常无需重建，但 **配置迁移仍适用** → 请运行 doctor。
- 在全局安装与 git 安装之间切换非常简单：安装另一种方式后，运行 `openclaw doctor`，即可将网关服务入口点重写为当前安装路径。

## 务必运行：`openclaw doctor`

Doctor 是“安全更新”命令。其设计刻意保持简洁：修复 + 迁移 + 警告。

注意：若您使用的是 **源码安装**（git checkout），`openclaw doctor` 将提示您先运行 `openclaw update`。

典型操作包括：

- 迁移已弃用的配置项 / 遗留配置文件路径。
- 审计 DM 策略，并对高风险的“开放”设置发出警告。
- 检查网关健康状态，并可提供重启建议。
- 检测并迁移旧版网关服务（launchd/systemd；遗留 schtasks）至当前 OpenClaw 服务。
- 在 Linux 上，确保启用 systemd 用户 linger 功能（使网关可在用户登出后继续运行）。

详情见：[Doctor](/gateway/doctor)

## 启动 / 停止 / 重启网关

CLI（适用于所有操作系统）：

```bash
openclaw gateway status
openclaw gateway stop
openclaw gateway restart
openclaw gateway --port 18789
openclaw logs --follow
```

若您使用服务监管机制：

- macOS launchd（应用内嵌 LaunchAgent）：`launchctl kickstart -k gui/$UID/ai.openclaw.gateway`（推荐使用 `ai.openclaw.<profile>`；旧版 `com.openclaw.*` 仍可工作）
- Linux systemd 用户服务：`systemctl --user restart openclaw-gateway[-<profile>].service`
- Windows（WSL2）：`systemctl --user restart openclaw-gateway[-<profile>].service`
  - `launchctl`/`systemctl` 仅在服务已安装时有效；否则请运行 `openclaw gateway install`。

完整运行手册及确切服务名称：[网关运行手册](/gateway)

## 回滚 / 版本锁定（当某些功能异常时）

### 锁定版本（全局安装）

安装一个已知稳定的版本（将 `<version>` 替换为最后一个正常工作的版本）：

```bash
npm i -g openclaw@<version>
```

```bash
pnpm add -g openclaw@<version>
```

提示：要查看当前已发布的版本，请运行 `npm view openclaw version`。

然后重启并再次运行 doctor：

```bash
openclaw doctor
openclaw gateway restart
```

### 锁定版本（源码方式）——按日期

选取某一天的提交（示例：“2026-01-01 当日 main 分支的状态”）：

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

如后续希望恢复至最新版：

```bash
git checkout main
git pull
```

## 若遇到问题无法解决

- 再次运行 `openclaw doctor` 并仔细阅读输出内容（通常其中已包含解决方案）。
- 查阅：[故障排查](/gateway/troubleshooting)
- 在 Discord 中提问：[https://discord.gg/clawd](https://discord.gg/clawd)