---
summary: "CLI reference for `openclaw update` (safe-ish source update + gateway auto-restart)"
read_when:
  - You want to update a source checkout safely
  - You need to understand `--update` shorthand behavior
title: "update"
---
# `openclaw update`

安全地更新 OpenClaw 并在 stable/beta/dev 通道之间切换。

如果您通过 **npm/pnpm/bun**（全局安装，无 git 元数据）安装，则更新将通过 [更新](/install/updating) 中的包管理器流程进行。

## 用法

```bash
openclaw update
openclaw update status
openclaw update wizard
openclaw update --channel beta
openclaw update --channel dev
openclaw update --tag beta
openclaw update --tag main
openclaw update --dry-run
openclaw update --no-restart
openclaw update --yes
openclaw update --json
openclaw --update
```

## 选项

- `--no-restart`: 成功更新后跳过重启 Gateway 服务。
- `--channel <stable|beta|dev>`: 设置更新通道（git + npm；配置中持久化）。
- `--tag <dist-tag|version|spec>`: 仅覆盖本次更新的软件包目标。对于软件包安装，`main` 映射到 `github:openclaw/openclaw#main`。
- `--dry-run`: 预览计划的更新操作（通道/标签/目标/重启流程），无需写入配置、安装、同步插件或重启。
- `--json`: 打印机器可读的 `UpdateRunResult` JSON。
- `--timeout <seconds>`: 每步超时时间（默认为 1200 秒）。
- `--yes`: 跳过确认提示（例如降级确认）

注意：降级需要确认，因为旧版本可能会破坏配置。

## `update status`

显示当前活动更新通道 + git 标签/分支/SHA（针对源码检出），以及更新可用性。

```bash
openclaw update status
openclaw update status --json
openclaw update status --timeout 10
```

选项：

- `--json`: 打印机器可读的状态 JSON。
- `--timeout <seconds>`: 检查超时时间（默认为 3 秒）。

## `update wizard`

交互式流程，用于选择更新通道并确认更新后是否重启 Gateway（默认为重启）。如果您在没有 git 检出的情况下选择 `dev`，它将提供创建选项。

选项：

- `--timeout <seconds>`: 每个更新步骤的超时时间（默认 `1200`）

## 功能说明

当您显式切换通道时（`--channel ...`），OpenClaw 也会保持安装方法一致：

- `dev` → 确保存在 git 检出（默认：`~/openclaw`，使用 `OPENCLAW_GIT_DIR` 覆盖），更新它，并从该检出安装全局 CLI。
- `stable` → 使用 `latest` 从 npm 安装。
- `beta` → 优先使用 npm dist-tag `beta`，但如果缺少 beta 或比当前稳定版旧，则回退到 `latest`。

Gateway 核心自动更新器（当通过配置启用时）重用此相同的更新路径。

## Git 检出流程

通道：

- `stable`: 检出最新的非 beta 标签，然后构建 + doctor。
- `beta`: 优先使用最新的 `-beta` 标签，但如果缺少 beta 或比最新稳定版旧，则回退到最新的稳定版标签。
- `dev`: 检出 `main`，然后获取 + 变基。

高级概述：

1. 需要干净的工作树（无未提交的更改）。
2. 切换到选定的通道（标签或分支）。
3. 获取上游（仅限 dev）。
4. 仅限 dev：在临时工作树中进行预检 lint + TypeScript 构建；如果最新版本失败，则回溯最多 10 个提交以找到最新的干净构建。
5. 变基到选定的提交（仅限 dev）。
6. 安装依赖（首选 pnpm；npm 回退；bun 保留作为次要兼容性回退）。
7. 构建 + 构建控制 UI。
8. 运行 `openclaw doctor` 作为最终的“安全更新”检查。
9. 将插件同步到活动通道（dev 使用捆绑扩展；stable/beta 使用 npm）并更新 npm 安装的插件。

## `--update` 简写

`openclaw --update` 重写为 `openclaw update`（适用于 shell 和启动器脚本）。

## 参见

- `openclaw doctor`（在 git 检出上提供先运行更新）
- [开发通道](/install/development-channels)
- [更新](/install/updating)
- [CLI 参考](/cli)