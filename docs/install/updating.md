---
summary: "Updating OpenClaw safely (global install or source), plus rollback strategy"
read_when:
  - Updating OpenClaw
  - Something breaks after an update
title: "Updating"
---
# 更新

OpenClaw 正在快速更新（预 "1.0"）。将更新视为运输基础设施：更新 → 运行检查 → 重启（或使用 `openclaw update`，它会重启）→ 验证。

## 推荐：重新运行网站安装程序（原地升级）

**首选**的更新路径是重新从网站运行安装程序。它会检测现有安装、原地升级，并在需要时运行 `openclaw doctor`。

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

说明：

- 如果你不希望再次运行引导向导，请添加 `--no-onboard`。
- 对于 **源码安装**，使用：
  ```bash
  curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --no-onboard
  ```
  安装程序将仅在仓库干净时执行 `git pull --rebase`。
- 对于 **全局安装**，脚本会使用 `npm install -g openclaw@latest`。
- 旧版说明：`openclaw` 仍作为兼容性 shim 可用。

## 更新前

- 知道你是如何安装的：**全局安装**（npm/pnpm）vs **源码安装**（git clone）。
- 知道你的网关是如何运行的：**前台终端** vs **受监督的服务**（launchd/systemd）。
- 备份你的定制配置：
  - 配置：`~/.openclaw/openclaw.json`
  - 凭据：`~/.openclaw/credentials/`
  - 工作区：`~/.openclaw/workspace`

## 更新（全局安装）

全局安装（选择一种）：

```bash
npm i -g openclaw@latest
```

```bash
pnpm add -g openclaw@latest
```

我们 **不推荐** 使用 Bun 作为网关运行时环境（WhatsApp/Telegram 存在 bug）。

切换更新渠道（git + npm 安装）：

```bash
openclaw update --channel beta
openclaw update --channel dev
openclaw update --channel stable
```

使用 `--tag <dist-tag|version>` 为一次性安装标签/版本。

查看 [开发渠道](/install/development-channels) 了解渠道语义和发布说明。

注意：在 npm 安装时，网关会在启动时记录更新提示（检查当前渠道标签）。通过 `update.checkOnStart: false` 禁用。

然后：

```bash
openclaw doctor
openclaw gateway restart
openclaw health
```

说明：

- 如果你的网关作为服务运行，`openclaw gateway restart` 比杀死 PID 更推荐。
- 如果你固定到特定版本，请参见下方的“回滚 / 固定版本”。

## 更新 (`openclaw update`)

对于 **源码安装**（git checkout），推荐：

```bash
openclaw update
```

它运行一个相对安全的更新流程：

- 需要干净的工作树。
- 切换到选定的渠道（标签或分支）。
- 从配置的上游（dev 渠道）拉取 + 重新基于。
- 安装依赖、构建、构建控制 UI 并运行 `openclaw doctor`。
- 默认重启网关（使用 `--no-restart` 跳过）。

如果你通过 **npm/pnpm** 安装（无 git 元数据），`openclaw update` 将尝试通过包管理器更新。如果无法检测到安装，请改用“更新（全局安装）”。

## 更新（控制 UI / RPC）

控制 UI 有 **更新 & 重启**（RPC: `update.run`）。它：

1. 运行与 `openclaw update` 相同的源码更新流程（仅 git checkout）。
2. 写入重启哨兵并生成结构化报告（stdout/stderr 尾部）。
3. 重启网关并使用报告 ping 最后活跃的会话。

如果 rebase 失败，网关将中止并重启，不应用更新。

## 更新（从源码）

从仓库 checkout：

推荐：

```bash
openclaw update
```

手动（类似）：

```bash
git pull
pnpm install
pnpm build
pnpm ui:build # 第一次运行时自动安装 UI 依赖
openclaw doctor
openclaw health
```

说明：

- `pnpm build` 在运行打包的 `openclaw` 二进制文件（[`openclaw.mjs`](https://github.com/openclaw/openclaw/blob/main/openclaw.mjs)）或使用 Node 运行 `dist/` 时很重要。
- 如果你从仓库 checkout 而非全局安装，使用 `pnpm openclaw ...` 运行 CLI 命令。
- 如果你直接从 TypeScript 运行（`pnpm openclaw ...`），通常不需要重新构建，但 **配置迁移仍适用** → 运行 doctor。
- 在全局和 git 安装之间切换很简单：安装其他版本，然后运行 `openclaw doctor` 以重写网关