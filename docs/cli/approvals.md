---
summary: "CLI reference for `openclaw approvals` (exec approvals for gateway or node hosts)"
read_when:
  - You want to edit exec approvals from the CLI
  - You need to manage allowlists on gateway or node hosts
title: "approvals"
---
# `openclaw approvals`

管理 **本地主机**、**网关主机** 或 **节点主机** 的执行审批（exec approvals）。
默认情况下，命令作用于磁盘上的本地审批文件。使用 `--gateway` 可将目标设为网关，或使用 `--node` 将目标设为特定节点。

相关文档：

- 执行审批：[Exec approvals](/tools/exec-approvals)
- 节点：[Nodes](/nodes)

## 常用命令

```bash
openclaw approvals get
openclaw approvals get --node <id|name|ip>
openclaw approvals get --gateway
```

## 从文件替换审批项

```bash
openclaw approvals set --file ./exec-approvals.json
openclaw approvals set --node <id|name|ip> --file ./exec-approvals.json
openclaw approvals set --gateway --file ./exec-approvals.json
```

## 允许列表（allowlist）辅助工具

```bash
openclaw approvals allowlist add "~/Projects/**/bin/rg"
openclaw approvals allowlist add --agent main --node <id|name|ip> "/usr/bin/uptime"
openclaw approvals allowlist add --agent "*" "/usr/bin/uname"

openclaw approvals allowlist remove "~/Projects/**/bin/rg"
```

## 注意事项

- `--node` 使用与 `openclaw nodes` 相同的解析器（支持 id、name、ip 或 id 前缀）。
- `--agent` 默认为 `"*"`，该值适用于所有代理（agents）。
- 节点主机必须声明 `system.execApprovals.get/set`（macOS 应用程序或无头节点主机）。
- 审批文件按主机分别存储在 `~/.openclaw/exec-approvals.json`。