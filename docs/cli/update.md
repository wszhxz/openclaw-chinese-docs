---
summary: "CLI reference for `openclaw update` (safe-ish source update + gateway auto-restart)"
read_when:
  - You want to update a source checkout safely
  - You need to understand `--update` shorthand behavior
title: "update"
---
# `openclaw update`

安全地更新 OpenClaw 并在稳定版/测试版/开发版通道之间切换。

如果您是通过 **npm/pnpm** 安装的（全局安装，无 Git 元数据），则更新将通过 [Updating](/install/updating) 中的包管理器流程进行。

## 使用方式

```bash
openclaw update
openclaw update status
openclaw update wizard
openclaw update --channel beta
openclaw update --channel dev
openclaw update --tag beta
openclaw update --no-restart
openclaw update --json
openclaw --update
```

## 选项

- `--no-restart`: 在更新成功后跳过重启网关服务。
- `--channel <stable|beta|dev>`: 设置更新通道（git + npm；保存在配置中）。
- `--tag <dist-tag|version>`: 仅针对本次更新覆盖 npm 发布标签或版本。
- `--json`: 输出可机读的 `UpdateRunResult` JSON。
- ``--timeout <seconds>`: 每个步骤的超时时间（默认是 1200 秒）。

注意：降级需要确认，因为旧版本可能会破坏配置。

## `update status`

显示当前的更新通道 + git 标签/分支/SHA（用于源代码检出），以及更新的可用性。

```bash
openclaw update status
openclaw update status --json
openclaw update status --timeout 10
```

选项：

- `--json`: 输出可机读的状态 JSON。
- `--timeout <seconds>`: 检查的超时时间（默认是 3 秒）。

## `update wizard`

交互式流程，用于选择更新通道并确认更新后是否重启网关（默认是重启）。如果您在没有 Git 检出的情况下选择 `dev`，它会提供创建一个的选项。

## 功能说明

当您显式切换通道（`--channel ...`）时，OpenClaw 也会保持安装方法同步：

- `dev` → 确保一个 Git 检出（默认：`~/openclaw`，通过 `OPENCLAW_GIT_DIR` 覆盖），更新它，并从该检出安装全局 CLI。
- `stable`/`beta` → 使用匹配的发布标签通过 npm 安装。

## Git 检出流程

通道：

- `stable`: 检出最新的非 beta 标签，然后构建 + 检查。
- `beta`: 检出最新的 `-beta` 标签，然后构建 + 检查。
- `dev`: 检出 `main`，然后获取 + 拉取合并。

总体步骤：

1. 需要一个干净的工作树（无未提交的更改）。
2. 切换到所选通道（标签或分支）。
3. 获取上游（仅 dev）。
4. 仅 dev：在临时工作树中进行预检查 lint + TypeScript 构建；如果尖端失败，则回溯到最近的 10 个提交以找到最新的干净构建。
5. 仅 dev：基于所选提交重新基于（rebase）。
6. 安装依赖（优先使用 pnpm；npm 作为回退）。
7. 构建 + 构建控制 UI。
8. 最后运行 `openclaw doctor` 作为“安全更新”检查。
9. 将插件同步到当前通道（dev 使用捆绑扩展；stable/beta 使用 npm），并更新 npm 安装的插件。

## `--update` 快捷方式

`openclaw --update` 重写为 `openclaw update`（对 shell 和启动脚本很有用）。

## 参见

- `openclaw doctor`（在 Git 检出上提供运行更新的选项）
- [开发通道](/install/development-channels)
- [更新](/install/updating)
- [CLI 参考](/cli)