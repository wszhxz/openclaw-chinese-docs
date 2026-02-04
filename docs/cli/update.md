---
summary: "CLI reference for `openclaw update` (safe-ish source update + gateway auto-restart)"
read_when:
  - You want to update a source checkout safely
  - You need to understand `--update` shorthand behavior
title: "update"
---
# `openclaw update`

安全地更新 OpenClaw 并在稳定/测试/开发渠道之间切换。

如果您是通过 **npm/pnpm** 安装的（全局安装，无 git 元数据），则更新将通过 [Updating](/install/updating) 中的包管理器流程进行。

## 使用方法

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

- `--no-restart`: 更新成功后跳过重启 Gateway 服务。
- `--channel <stable|beta|dev>`: 设置更新渠道（git + npm；保存在配置中）。
- `--tag <dist-tag|version>`: 仅此更新覆盖 npm 的 dist-tag 或版本。
- `--json`: 打印机器可读的 `UpdateRunResult` JSON。
- `--timeout <seconds>`: 每步超时时间（默认为 1200 秒）。

注意：降级需要确认，因为旧版本可能会破坏配置。

## `update status`

显示活动更新渠道 + git 标签/分支/SHA（对于源码检出），以及更新可用性。

```bash
openclaw update status
openclaw update status --json
openclaw update status --timeout 10
```

选项：

- `--json`: 打印机器可读的状态 JSON。
- `--timeout <seconds>`: 检查的超时时间（默认为 3 秒）。

## `update wizard`

交互式流程以选择更新渠道，并确认更新后是否重启 Gateway（默认是重启）。如果您选择 `dev` 而没有 git 检出，则会提供创建一个的选项。

## 它的作用

当您显式切换渠道 (`--channel ...`) 时，OpenClaw 还会保持安装方法的一致：

- `dev` → 确保有一个 git 检出（默认: `~/openclaw`，使用 `OPENCLAW_GIT_DIR` 覆盖），
  更新它，并从该检出安装全局 CLI。
- `stable`/`beta` → 使用匹配的 dist-tag 从 npm 安装。

## Git 检出流程

渠道：

- `stable`: 检出最新的非测试标签，然后构建 + 医疗检查。
- `beta`: 检出最新的 `-beta` 标签，然后构建 + 医疗检查。
- `dev`: 检出 `main`，然后获取 + 重新变基。

高层次概述：

1. 需要干净的工作树（无未提交更改）。
2. 切换到选定的渠道（标签或分支）。
3. 获取上游（仅限开发）。
4. 开发专用：在临时工作树中进行预飞行 lint + TypeScript 构建；如果尖端失败，则回溯最多 10 次提交以找到最新的干净构建。
5. 重新变基到选定的提交（仅限开发）。
6. 安装依赖（首选 pnpm；回退到 npm）。
7. 构建 + 构建控制 UI。
8. 运行 `openclaw doctor` 作为最终的“安全更新”检查。
9. 将插件同步到活动渠道（开发使用捆绑扩展；稳定/测试使用 npm）并更新 npm 安装的插件。

## `--update` 简写

`openclaw --update` 重写为 `openclaw update`（适用于 shell 和启动脚本）。

## 参见

- `openclaw doctor`（在 git 检出时提供先运行更新的选项）
- [开发渠道](/install/development-channels)
- [更新](/install/updating)
- [CLI 参考](/cli)