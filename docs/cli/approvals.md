---
summary: "CLI reference for `openclaw approvals` (exec approvals for gateway or node hosts)"
read_when:
  - You want to edit exec approvals from the CLI
  - You need to manage allowlists on gateway or node hosts
title: "approvals"
---
# `openclaw approvals`

管理 **本地主机**、**网关主机** 或 **节点主机** 的执行审批。
默认情况下，命令针对磁盘上的本地审批文件。使用 `--gateway` 针对网关，或使用 `--node` 针对特定节点。

别名：`openclaw exec-approvals`

相关：

- 执行审批：[执行审批](/tools/exec-approvals)
- 节点：[节点](/nodes)

## 常用命令

```bash
openclaw approvals get
openclaw approvals get --node <id|name|ip>
openclaw approvals get --gateway
```

`openclaw approvals get` 现在显示本地、网关和节点目标的实际执行策略：

- 请求的 `tools.exec` 策略
- 主机审批文件策略
- 应用优先级规则后的有效结果

优先级是有意设计的：

- 主机审批文件是强制执行的真实来源
- 请求的 `tools.exec` 策略可以缩小或扩大意图，但有效结果仍源自主机规则
- `--node` 将节点主机审批文件与网关 `tools.exec` 策略结合，因为两者在运行时仍然适用
- 如果网关配置不可用，CLI 将回退到节点审批快照，并指出无法计算最终运行时策略

## 从文件替换审批

```bash
openclaw approvals set --file ./exec-approvals.json
openclaw approvals set --stdin <<'EOF'
{ version: 1, defaults: { security: "full", ask: "off" } }
EOF
openclaw approvals set --node <id|name|ip> --file ./exec-approvals.json
openclaw approvals set --gateway --file ./exec-approvals.json
```

`set` 接受 JSON5，而不仅仅是严格 JSON。使用 `--file` 或 `--stdin`，不要同时使用。

## “永不提示”/YOLO 示例

对于不应在执行审批时停止的主机，将主机审批默认值设置为 `full` + `off`：

```bash
openclaw approvals set --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

节点变体：

```bash
openclaw approvals set --node <id|name|ip> --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

这仅更改 **主机审批文件**。为了保持请求的 OpenClaw 策略一致，还请设置：

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
```

此示例中为何使用 `tools.exec.host=gateway`：

- `host=auto` 仍然意味着“可用沙箱时使用沙箱，否则使用网关”。
- YOLO 关注的是审批，而不是路由。
- 如果您希望在配置了沙箱时仍希望主机执行，请使用 `gateway` 或 `/exec host=gateway` 明确指定主机选择。

这与当前的主机默认 YOLO 行为相匹配。如果您需要审批，请收紧它。

## 白名单助手

```bash
openclaw approvals allowlist add "~/Projects/**/bin/rg"
openclaw approvals allowlist add --agent main --node <id|name|ip> "/usr/bin/uptime"
openclaw approvals allowlist add --agent "*" "/usr/bin/uname"

openclaw approvals allowlist remove "~/Projects/**/bin/rg"
```

## 通用选项

`get`、`set` 和 `allowlist add|remove` 均支持：

- `--node <id|name|ip>`
- `--gateway`
- 共享节点 RPC 选项：`--url`、`--token`、`--timeout`、`--json`

目标说明：

- 无目标标志表示磁盘上的本地审批文件
- `--gateway` 针对网关主机审批文件
- `--node` 在解析 ID、名称、IP 或 ID 前缀后针对一个节点主机

`allowlist add|remove` 还支持：

- `--agent <id>`（默认为 `*`）

## 注意事项

- `--node` 使用与 `openclaw nodes` 相同的解析器（ID、名称、IP 或 ID 前缀）。
- `--agent` 默认为 `"*"`，适用于所有代理。
- 节点主机必须通告 `system.execApprovals.get/set`（macOS 应用程序或无头节点主机）。
- 审批文件按主机存储在 `~/.openclaw/exec-approvals.json`。