---
summary: "CLI reference for `openclaw update` (safe-ish source update + gateway auto-restart)"
read_when:
  - You want to update a source checkout safely
  - You need to understand `--update` shorthand behavior
title: "update"
---
# `openclaw update`

安全地更新 OpenClaw 并在 stable/beta/dev 通道之间切换。

如果您是通过 **npm/pnpm**（全局安装，无 Git 元数据）方式安装的，则更新将通过 [更新](/install/updating) 中所述的包管理器流程完成。

## 使用方法

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

- `--no-restart`：更新成功后跳过重启 Gateway 服务。
- `--channel <stable|beta|dev>`：设置更新通道（适用于 Git + npm；配置中持久化保存）。
- `--tag <dist-tag|version>`：仅对本次更新覆盖 npm dist-tag 或版本号。
- `--dry-run`：预览计划执行的更新操作（通道/标签/目标/重启流程），但不写入配置、不安装、不同步插件、也不重启。
- `--json`：输出机器可读的 `UpdateRunResult` JSON。
- `--timeout <seconds>`：每一步操作的超时时间（默认为 1200 秒）。

注意：降级操作需要确认，因为旧版本可能破坏现有配置。

## `update status`

显示当前激活的更新通道 + Git 标签/分支/提交哈希（适用于源码检出），以及是否有可用更新。

```bash
openclaw update status
openclaw update status --json
openclaw update status --timeout 10
```

选项：

- `--json`：输出机器可读的状态 JSON。
- `--timeout <seconds>`：检查操作的超时时间（默认为 3 秒）。

## `update wizard`

交互式流程，用于选择更新通道，并确认更新后是否重启 Gateway（默认为重启）。如果您选择 `dev` 但尚未进行 Git 检出，系统会提示您创建一个。

## 其作用

当您显式切换通道（`--channel ...`）时，OpenClaw 还会同步保持安装方式一致：

- `dev` → 确保使用 Git 检出（默认为 `~/openclaw`，可通过 `OPENCLAW_GIT_DIR` 覆盖），
  更新该检出，并从此检出中安装全局 CLI。
- `stable`/`beta` → 使用匹配的 dist-tag 从 npm 安装。

Gateway 核心自动更新器（若通过配置启用）复用相同的更新路径。

## Git 检出流程

通道说明：

- `stable`：检出最新的非 beta 标签，然后构建 + 执行 doctor。
- `beta`：检出最新的 `-beta` 标签，然后构建 + 执行 doctor。
- `dev`：检出 `main`，然后获取远程更新 + 变基。

高层流程：

1. 要求工作树干净（无未提交的更改）。
2. 切换到所选通道（标签或分支）。
3. 获取上游更新（仅 dev 通道）。
4. 仅 dev 通道：在临时工作树中预先执行 lint + TypeScript 构建；若最新提交失败，则向上回溯最多 10 次提交，寻找最近一次成功的干净构建。
5. 变基至所选提交（仅 dev 通道）。
6. 安装依赖（优先使用 pnpm；npm 作为备选）。
7. 构建 + 构建 Control UI。
8. 运行 `openclaw doctor` 作为最终“安全更新”检查。
9. 将插件同步至当前活动通道（dev 使用捆绑扩展；stable/beta 使用 npm），并更新已通过 npm 安装的插件。

## `--update` 简写形式

`openclaw --update` 会被重写为 `openclaw update`（适用于 shell 和启动脚本）。

## 参见

- `openclaw doctor`（在 Git 检出情况下，会提示先运行 update）
- [开发通道](/install/development-channels)
- [更新](/install/updating)
- [CLI 参考](/cli)