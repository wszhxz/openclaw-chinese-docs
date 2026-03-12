---
summary: "Stable, beta, and dev channels: semantics, switching, and tagging"
read_when:
  - You want to switch between stable/beta/dev
  - You are tagging or publishing prereleases
title: "Development Channels"
---
# 开发通道

最后更新时间：2026-01-21

OpenClaw 提供三个更新通道：

- **stable**：npm dist-tag `latest`。
- **beta**：npm dist-tag `beta`（处于测试阶段的构建）。
- **dev**：`main`（git）的最新提交（moving head）。npm dist-tag：`dev`（发布时）。

我们将构建产物发布至 **beta** 通道，完成测试后，再将经过验证的构建产物**提升至 `latest`**  
而不更改版本号 —— npm 安装所依赖的“事实来源”是 dist-tags。

## 切换通道

Git 检出：

```bash
openclaw update --channel stable
openclaw update --channel beta
openclaw update --channel dev
```

- `stable`/`beta` 检出最新匹配的标签（通常为同一标签）。
- `dev` 切换至 `main` 并在上游分支上执行变基（rebase）。

npm/pnpm 全局安装：

```bash
openclaw update --channel stable
openclaw update --channel beta
openclaw update --channel dev
```

该命令通过对应的 npm dist-tag（`latest`、`beta`、`dev`）进行更新。

当你**显式地**使用 `--channel` 切换通道时，OpenClaw 还会同步调整安装方式：

- `dev` 确保采用 Git 检出方式（默认为 `~/openclaw`，可通过 `OPENCLAW_GIT_DIR` 覆盖），
  更新检出内容，并从该检出中安装全局 CLI。
- `stable`/`beta` 则使用匹配的 dist-tag 从 npm 安装。

提示：若需同时使用 stable 和 dev 版本，可保留两个独立克隆，并将网关指向 stable 克隆。

## 插件与通道

当你使用 `openclaw update` 切换通道时，OpenClaw 还会同步插件源：

- `dev` 优先使用 Git 检出中捆绑的插件。
- `stable` 和 `beta` 则恢复通过 npm 安装的插件包。

## 标签管理最佳实践

- 请为希望 Git 检出落于其上的发布版本打标签（`vYYYY.M.D` 表示 stable，`vYYYY.M.D-beta.N` 表示 beta）。
- `vYYYY.M.D.beta.N` 也受支持以保持兼容性，但推荐使用 `-beta.N`。
- 已废弃的 `vYYYY.M.D-<patch>` 标签仍被识别为 stable（非 beta）版本。
- 请确保标签不可变：切勿移动或复用已有标签。
- npm dist-tags 始终是 npm 安装的“事实来源”：
  - `latest` → stable
  - `beta` → 候选构建（candidate build）
  - `dev` → 主干快照（main snapshot，可选）

## macOS 应用可用性

Beta 和 dev 构建**可能不包含** macOS 应用发布版本。这没有问题：

- Git 标签和 npm dist-tag 仍可正常发布。
- 在发布说明或变更日志中注明：“此 beta 版本暂无 macOS 构建”。