---
summary: "CLI reference for `openclaw approvals` (exec approvals for gateway or node hosts)"
read_when:
  - You want to edit exec approvals from the CLI
  - You need to manage allowlists on gateway or node hosts
title: "approvals"
---
# `openclaw 审批`

管理 **本地主机**、**网关主机** 或 **节点主机** 的执行审批。
默认情况下，命令会针对磁盘上的本地审批文件。使用 `--gateway` 指向网关，或使用 `--node` 指向特定节点。

相关：

- 执行审批：[执行审批](/tools/exec-approvals)
- 节点：[节点](/nodes)

## 常用命令

```bash
openclaw 审批 get
openclaw 审批 get --node <id|name|ip>
openclaw 审批 get --gateway
```

## 从文件替换审批

```bash
openclaw 审批 set --file ./exec-approvals.json
openclaw 审批 set --node <id|name|ip> --file ./exec-approvals.json
openclaw 审批 set --gateway --file ./exec-approvals.json
```

## 允许列表助手

```bash
openclaw 审批 允许列表 add "~/Projects/**/bin/rg"
openclaw 审批 允许列表 add --agent main --node <id|name|ip> "/usr/bin/uptime"
openclaw 审批 允许列表 add --agent "*" "/usr/bin/uname"

openclaw 审批 允许列表 remove "~/Projects/**/bin/rg"
```

## 注意事项

- `--node` 使用与 `openclaw nodes` 相同的解析器（支持 id、name、ip 或 id 前缀）。
- `--agent` 默认为 `"*"`, 适用于所有代理。
- 节点主机必须公告 `system.execApprovals.get/set`（macOS 应用或无头节点主机）。
- 审批文件按主机存储在 `~/.openclaw/exec-approvals.json`。