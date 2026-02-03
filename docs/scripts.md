---
summary: "Repository scripts: purpose, scope, and safety notes"
read_when:
  - Running scripts from the repo
  - Adding or changing scripts under ./scripts
title: "Scripts"
---
# 脚本

`scripts/` 目录包含用于本地工作流和运维任务的辅助脚本。
当任务明显与脚本相关时使用这些脚本；否则优先使用 CLI。

## 规范

- 除非在文档或发布检查清单中引用，否则脚本是**可选的**。
- 当存在 CLI 界面时优先使用（示例：认证监控使用 `openclaw models status --check`）。
- 假设脚本是主机特定的；在新机器上运行前请先阅读脚本。

## Git 钩子

- `scripts/setup-git-hooks.js`：在 Git 仓库内对 `core.hooksPath` 进行尽力而为的设置。
- `scripts/format-staged.js`：用于预提交格式化的 staged `src/` 和 `test/` 文件。

## 认证监控脚本

认证监控脚本的文档见此处：
[/automation/auth-monitoring](/automation/auth-monitoring)

## 添加脚本时

- 保持脚本专注并做好文档说明。
- 在相关文档中添加简短条目（若缺失则创建新文档）。