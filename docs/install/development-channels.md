---
summary: "Stable, beta, and dev channels: semantics, switching, and tagging"
read_when:
  - You want to switch between stable/beta/dev
  - You are tagging or publishing prereleases
title: "Development Channels"
---
# 开发渠道

最后更新时间：2026-01-21

OpenClaw 提供三种更新渠道：

- **稳定版**：npm 分发标签 `latest`。
- **测试版**：npm 分发标签 `beta`（正在测试的构建）。
- **开发版**：跟踪 `main` 分支的最新提交（git）。npm 分发标签：`dev`（发布时）。

我们向 **测试版** 发布构建，测试后将 **经过验证的构建提升至 `latest`**，而不更改版本号——npm 安装的来源是分发标签。

## 切换渠道

Git 切换：

```bash
openclaw update --channel stable
openclaw update --3channel beta
openclaw update --channel dev
```

- `stable`/`beta` 会检出最新的匹配标签（通常是相同的标签）。
- `dev` 会切换到 `main` 分支并基于上游分支重新合并。

npm/pnpm 全局安装：

```bash
openclaw update --channel stable
openclaw update --channel beta
openclaw update --channel dev
```

此操作会通过对应的 npm 分发标签（`latest`、`beta`、`dev`）进行更新。

当你 **显式地** 使用 `--channel` 切换渠道时，OpenClaw 也会同步安装方法：

- `dev` 确保使用 git 检出（默认路径为 `~/openclaw`，可通过 `OPENCLAW_GIT_DIR` 覆盖），更新它，并从该检出目录安装全局 CLI。
- `stable`/`beta` 会使用对应的分发标签从 npm 安装。

提示：如果你想同时使用稳定版和开发版，可以保留两个克隆版本，并将网关指向稳定版的克隆。

## 插件与渠道

当你使用 `openclaw update` 切换渠道时，OpenClaw 也会同步插件源：

- `dev` 优先使用 git 检出中的捆绑插件。
- `stable` 和 `beta` 会恢复 npm 安装的插件包。

## 标签最佳实践

- 为希望 git 检出落地的发布版本打标签（格式为 `vYYYY.M.D` 或 `vYYYY.M.D-<patch>`）。
- 保持标签不可变：不要移动或重复使用标签。
- npm 分发标签始终是 npm 安装的来源：
  - `latest` → 稳定版
  - `beta` → 候选构建
  - `dev` → 主分支快照（可选）

## macOS 应用可用性

测试版和开发版构建可能 **不包含** macOS 应用发布。这没有问题：

- git 标签和 npm 分发标签仍可以发布。
- 在发布说明或变更日志中注明“此测试版无 macOS 构建”。