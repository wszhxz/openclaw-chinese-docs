---
summary: "CLI reference for `openclaw reset` (reset local state/config)"
read_when:
  - You want to wipe local state while keeping the CLI installed
  - You want a dry-run of what would be removed
title: "reset"
---
# `openclaw reset`

重置本地配置/状态（保留已安装的 CLI）。

选项：

- `--scope <scope>`: `config`、`config+creds+sessions` 或 `full`
- `--yes`: 跳过确认提示
- `--non-interactive`: 禁用提示；需要 `--scope` 和 `--yes`
- `--dry-run`: 打印操作但不删除文件

示例：

```bash
openclaw backup create
openclaw reset
openclaw reset --dry-run
openclaw reset --scope config --yes --non-interactive
openclaw reset --scope config+creds+sessions --yes --non-interactive
openclaw reset --scope full --yes --non-interactive
```

注意：

- 如果您想在删除本地状态之前创建一个可恢复的快照，请先运行 `openclaw backup create`。
- 如果省略 `--scope`，`openclaw reset` 将使用交互式提示来选择要删除的内容。
- `--non-interactive` 仅在同时设置了 `--scope` 和 `--yes` 时有效。