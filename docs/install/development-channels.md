---
summary: "Stable, beta, and dev channels: semantics, switching, and tagging"
read_when:
  - You want to switch between stable/beta/dev
  - You are tagging or publishing prereleases
title: "Development Channels"
---
# 开发渠道

最后更新：2026-01-21

OpenClaw 提供三个更新渠道：

- **stable**：npm dist-tag `latest`。
- **beta**：npm dist-tag `beta`（测试中的构建）。
- **dev**：`main` (git) 的移动 HEAD。npm dist-tag：`dev`（发布时）。

我们将构建发布到 **beta**，测试它们，然后 **将经过审核的构建提升到 `latest`**
不更改版本号 —— dist-tags 是 npm 安装的事实来源。

## 切换渠道

Git checkout:

```bash
openclaw update --channel stable
openclaw update --channel beta
openclaw update --channel dev
```

- `stable`/`beta` 检出最新的匹配标签（通常是同一个标签）。
- `dev` 切换到 `main` 并基于上游变基。

npm/pnpm global install:

```bash
openclaw update --channel stable
openclaw update --channel beta
openclaw update --channel dev
```

这通过相应的 npm dist-tag 更新（`latest`、`beta`、`dev`）。

当您使用 `--channel` **显式** 切换渠道时，OpenClaw 还会对齐
安装方法：

- `dev` 确保 git checkout（默认 `~/openclaw`，可用 `OPENCLAW_GIT_DIR` 覆盖），
  更新它，并从该 checkout 安装全局 CLI。
- `stable`/`beta` 使用匹配的 dist-tag 从 npm 安装。

提示：如果您想并行使用 stable + dev，请保留两个克隆，并将网关指向 stable 的那个。

## 插件和渠道

当您使用 `openclaw update` 切换渠道时，OpenClaw 还会同步插件源：

- `dev` 优先使用来自 git checkout 的捆绑插件。
- `stable` 和 `beta` 恢复 npm 安装的插件包。

## 标签最佳实践

- 标记您希望 git checkouts 落脚的版本（`vYYYY.M.D` 用于 stable，`vYYYY.M.D-beta.N` 用于 beta）。
- `vYYYY.M.D.beta.N` 也被识别用于兼容性，但首选 `-beta.N`。
- 遗留的 `vYYYY.M.D-<patch>` 标签仍被识别为 stable（非 beta）。
- 保持标签不可变：切勿移动或重用标签。
- npm dist-tags 仍然是 npm 安装的事实来源：
  - `latest` → stable
  - `beta` → 候选构建
  - `dev` → 主快照（可选）

## macOS 应用可用性

Beta 和 dev 构建可能 **不** 包含 macOS 应用发布。没关系：

- git tag 和 npm dist-tag 仍然可以发布。
- 在 release notes 或 changelog 中指出“此 beta 版本没有 macOS 构建”。