---
summary: "Stable, beta, and dev channels: semantics, switching, and tagging"
read_when:
  - You want to switch between stable/beta/dev
  - You are tagging or publishing prereleases
title: "Development Channels"
---
# 开发渠道

最后更新时间：2026-01-21

OpenClaw 提供三个更新渠道：

- **stable**: npm dist-tag `latest`。
- **beta**: npm dist-tag `beta` (正在测试的构建)。
- **dev**: `main` 的移动头 (git)。npm dist-tag: `dev` (发布时)。

我们将构建发布到 **beta**，进行测试，然后将经过验证的构建提升到 `latest`
而不更改版本号 —— dist-tags 是 npm 安装的真相来源。

## 切换渠道

Git 切换：

```bash
openclaw update --channel stable
openclaw update --channel beta
openclaw update --channel dev
```

- `stable`/`beta` 检出最新的匹配标签（通常是相同的标签）。
- `dev` 切换到 `main` 并基于上游进行变基。

npm/pnpm 全局安装：

```bash
openclaw update --channel stable
openclaw update --channel beta
openclaw update --channel dev
```

这是通过相应的 npm dist-tag 更新的 (`latest`, `beta`, `dev`)。

当你 **显式** 使用 `--channel` 切换渠道时，OpenClaw 还会同步
安装方法：

- `dev` 确保进行 git 切换（默认 `~/openclaw`，使用 `OPENCLAW_GIT_DIR` 覆盖），
  更新它，并从该切换安装全局 CLI。
- `stable`/`beta` 使用匹配的 dist-tag 从 npm 安装。

提示：如果你想并行使用 stable 和 dev，请保持两个克隆并将网关指向 stable 的一个。

## 插件和渠道

当你使用 `openclaw update` 切换渠道时，OpenClaw 还会同步插件源：

- `dev` 更倾向于从 git 切换中使用的捆绑插件。
- `stable` 和 `beta` 恢复 npm 安装的插件包。

## 标签最佳实践

- 为希望 git 切换着陆的发布打标签 (`vYYYY.M.D` 或 `vYYYY.M.D-<patch>`)。
- 保持标签不可变：永远不要移动或重用标签。
- npm dist-tags 仍然是 npm 安装的真相来源：
  - `latest` → stable
  - `beta` → 候选构建
  - `dev` → 主快照（可选）

## macOS 应用可用性

Beta 和 dev 构建可能 **不** 包含 macOS 应用发布。这没有问题：

- git 标签和 npm dist-tag 仍然可以发布。
- 在发布说明或变更日志中注明“此 beta 版本没有 macOS 构建”。