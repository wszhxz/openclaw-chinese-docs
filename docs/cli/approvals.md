---
summary: "CLI reference for `openclaw approvals` (exec approvals for gateway or node hosts)"
read_when:
  - You want to edit exec approvals from the CLI
  - You need to manage allowlists on gateway or node hosts
title: "approvals"
---
# `openclaw approvals`

管理 **本地主机**、**网关主机** 或 **节点主机** 的 exec 批准。
默认情况下，命令针对磁盘上的本地批准文件。使用 `--gateway` 针对网关，或使用 `--node` 针对特定节点。

相关：

- Exec 批准：[Exec 批准](/tools/exec-approvals)
- 节点：[节点](/nodes)

## 常用命令

```bash
openclaw approvals get
openclaw approvals get --node <id|name|ip>
openclaw approvals get --gateway
```

## 从文件替换批准

```bash
openclaw approvals set --file ./exec-approvals.json
openclaw approvals set --node <id|name|ip> --file ./exec-approvals.json
openclaw approvals set --gateway --file ./exec-approvals.json
```

## 允许列表辅助工具

```bash
openclaw approvals allowlist add "~/Projects/**/bin/rg"
openclaw approvals allowlist add --agent main --node <id|name|ip> "/usr/bin/uptime"
openclaw approvals allowlist add --agent "*" "/usr/bin/uname"

openclaw approvals allowlist remove "~/Projects/**/bin/rg"
```

## 注意事项

- `--node` 使用与 `openclaw nodes` 相同的解析器（id、name、ip 或 id 前缀）。
- `--agent` 默认为 `"*"`，适用于所有代理。
- 节点主机必须广播 `system.execApprovals.get/set`（macOS 应用程序或无头节点主机）。
- 批准文件按主机存储在 `~/.openclaw/exec-approvals.json`。