---
summary: "Repository scripts: purpose, scope, and safety notes"
read_when:
  - Running scripts from the repo
  - Adding or changing scripts under ./scripts
title: "Scripts"
---
# 脚本

`scripts/` 目录包含用于本地工作流和运维任务的帮助脚本。
当任务明确与某个脚本相关时使用这些脚本；否则优先使用CLI。

## 约定

- 除非在文档或发布检查列表中引用，否则脚本是**可选**的。
- 当存在CLI界面时优先使用（示例：auth监控使用`openclaw models status --check`）。
- 假设脚本是特定于主机的；在新机器上运行之前请先阅读它们。

## Git钩子

- `scripts/setup-git-hooks.js`: 在git仓库内部时对`core.hooksPath`进行尽力而为的设置。
- `scripts/format-staged.js`: 对暂存的`src/`和`test/`文件进行预提交格式化。

## Auth监控脚本

Auth监控脚本在此处文档化：
[/automation/auth-monitoring](/automation/auth-monitoring)

## 添加脚本时

- 保持脚本专注并进行文档化。
- 在相关文档中添加简短条目（如果缺失则创建一个）。