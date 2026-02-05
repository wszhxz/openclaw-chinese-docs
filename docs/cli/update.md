---
summary: "CLI reference for `openclaw update` (safe-ish source update + gateway auto-restart)"
read_when:
  - You want to update a source checkout safely
  - You need to understand `--update` shorthand behavior
title: "update"
---
# `openclaw update`

安全地更新OpenClaw并在稳定/测试/开发频道之间切换。

如果您是通过**npm/pnpm**（全局安装，无git元数据）安装的，更新将通过[更新](/install/updating)中的包管理器流程进行。

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

- `--no-restart`: 更新成功后跳过重启Gateway服务。
- `--channel <stable|beta|dev>`: 设置更新频道（git + npm；保存在配置中）。
- `--tag <dist-tag|version>`: 仅此更新覆盖npm dist-tag或版本。
- `--json`: 打印机器可读的`UpdateRunResult` JSON。
- `--timeout <seconds>`: 每步超时时间（默认为1200秒）。

注意：降级需要确认，因为旧版本可能会破坏配置。

## `update status`

显示活动更新频道+git标签/分支/SHA（对于源码检出），以及更新可用性。

```bash
openclaw update status
openclaw update status --json
openclaw update status --timeout 10
```

选项：

- `--json`: 打印机器可读的状态JSON。
- `--timeout <seconds>`: 检查的超时时间（默认为3秒）。

## `update wizard`

交互式流程以选择更新频道并确认是否在更新后重启Gateway（默认是重启）。如果您在没有git检出的情况下选择了`dev`，它会提供创建一个的机会。

## 它的作用

当您明确切换频道(`--channel ...`)时，OpenClaw也会保持安装方法的一致性：

- `dev` → 确保一个git检出（默认：`~/openclaw`，使用`OPENCLAW_GIT_DIR`覆盖），
  更新它，并从该检出安装全局CLI。
- `stable`/`beta` → 使用匹配的dist-tag从npm安装。

## Git检出流程

频道：

- `stable`: 检出最新的非测试标签，然后构建+医生检查。
- `beta`: 检出最新的`-beta`标签，然后构建+医生检查。
- `dev`: 检出`main`，然后获取+变基。

高层次概述：

1. 需要干净的工作树（无未提交更改）。
2. 切换到选定的频道（标签或分支）。
3. 获取上游（仅限开发）。
4. 开发专用：在临时工作树中进行预检lint + TypeScript构建；如果尖端失败，则回退最多10个提交以找到最新的干净构建。
5. 变基到选定的提交（仅限开发）。
6. 安装依赖项（首选pnpm；回退到npm）。
7. 构建+构建控制UI。
8. 运行`openclaw doctor`作为最终的“安全更新”检查。
9. 将插件同步到活动频道（开发使用捆绑扩展；稳定/测试使用npm）并更新npm安装的插件。

## `--update`简写

`openclaw --update`重写为`openclaw update`（适用于shell和启动脚本）。

## 参见

- `openclaw doctor`（在git检出时提供先运行更新的选项）
- [开发频道](/install/development-channels)
- [更新](/install/updating)
- [CLI参考](/cli)