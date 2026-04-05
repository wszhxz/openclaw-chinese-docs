---
summary: "CLI reference for `openclaw uninstall` (remove gateway service + local data)"
read_when:
  - You want to remove the gateway service and/or local state
  - You want a dry-run first
title: "uninstall"
---
# `openclaw uninstall`

卸载网关服务和本地数据（保留 CLI）。

选项：

- `--service`: 移除网关服务
- `--state`: 移除状态和配置
- `--workspace`: 移除工作区目录
- `--app`: 移除 macOS 应用
- `--all`: 移除服务、状态、工作区和应用
- `--yes`: 跳过确认提示
- `--non-interactive`: 禁用提示；需要 `--yes`
- `--dry-run`: 仅打印操作而不删除文件

示例：

```bash
openclaw backup create
openclaw uninstall
openclaw uninstall --service --yes --non-interactive
openclaw uninstall --state --workspace --yes --non-interactive
openclaw uninstall --all --yes
openclaw uninstall --dry-run
```

注意：

- 如果要在移除状态或工作区之前创建可恢复的快照，请先运行 `openclaw backup create`。
- `--all` 是同时移除服务、状态、工作区和应用的简写。
- `--non-interactive` 需要 `--yes`。