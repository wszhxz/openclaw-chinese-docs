---
summary: "CLI reference for `openclaw update` (safe-ish source update + gateway auto-restart)"
read_when:
  - You want to update a source checkout safely
  - You need to understand `--update` shorthand behavior
title: "update"
---
# `openclaw update`

安全地更新 OpenClaw 并在 stable/beta/dev 渠道之间切换。

如果您是通过 **npm/pnpm** 安装的（全局安装，无 git 元数据），更新将通过 [更新](/install/updating) 中的包管理器流程进行。

## 用法

```bash
openclaw update
openclaw update status
openclaw update wizard
openclaw update --channel beta
openclaw update --channel dev
openclaw update --tag beta
openclaw update --dry-run
openclaw update --no-restart
openclaw update --json
openclaw --update
```

## 选项

- `--no-restart`：成功更新后跳过重启 Gateway 服务。
- `--channel <stable|beta|dev>`：设置更新渠道（git + npm；持久化存储在 config 中）。
- `--tag <dist-tag|version>`：仅针对此次更新覆盖 npm dist-tag 或版本。
- `--dry-run`：预览计划的更新操作（渠道/tag/target/restart 流程），而不写入 config、安装、同步插件或重启。
- `--json`：打印机器可读的 `UpdateRunResult` JSON。
- `--timeout <seconds>`：每步超时（默认为 1200s）。

注意：降级需要确认，因为旧版本可能会破坏配置。

## `update status`

显示当前激活的更新渠道 + git tag/branch/SHA（针对源码 checkout），以及更新可用性。

```bash
openclaw update status
openclaw update status --json
openclaw update status --timeout 10
```

选项：

- `--json`：打印机器可读的状态 JSON。
- `--timeout <seconds>`：检查超时（默认为 3s）。

## `update wizard`

交互流程，用于选择更新渠道并确认是否在更新后重启 Gateway
（默认为重启）。如果您在没有 git checkout 的情况下选择 `dev`，它将
提议创建一个。

## 作用

当您显式切换渠道时（`--channel ...`），OpenClaw 还会保持
安装方法一致：

- `dev` → 确保 git checkout（默认：`~/openclaw`，可通过 `OPENCLAW_GIT_DIR` 覆盖），
  更新它，并从该 checkout 安装全局 CLI。
- `stable`/`beta` → 使用匹配的 dist-tag 从 npm 安装。

Gateway 核心自动更新器（当通过 config 启用时）会复用此相同的更新路径。

## Git checkout 流程

渠道：

- `stable`：checkout 最新的非 beta tag，然后 build + doctor。
- `beta`：checkout 最新的 `-beta` tag，然后 build + doctor。
- `dev`：checkout `main`，然后 fetch + rebase。

概要：

1. 需要干净的 worktree（无未提交的更改）。
2. 切换到选定的渠道（tag 或 branch）。
3. 获取 upstream（仅 dev）。
4. 仅 dev：在临时 worktree 中进行 preflight lint + TypeScript build；如果 tip 失败，则回退最多 10 个 commit 以找到最新的干净 build。
5. Rebase 到选定的 commit（仅 dev）。
6. 安装 deps（首选 pnpm；npm 备选）。
7. 构建 + 构建 Control UI。
8. 运行 `openclaw doctor` 作为最终的“安全更新”检查。
9. 同步插件到活动渠道（dev 使用 bundled extensions；stable/beta 使用 npm）并更新 npm 安装的插件。

## `--update` 简写

`openclaw --update` 重写为 `openclaw update`（适用于 shells 和 launcher 脚本）。

## 另请参阅

- `openclaw doctor`（建议在 git checkouts 上首先运行 update）
- [开发渠道](/install/development-channels)
- [更新](/install/updating)
- [CLI 参考](/cli)