---
summary: "CLI reference for `openclaw status` (diagnostics, probes, usage snapshots)"
read_when:
  - You want a quick diagnosis of channel health + recent session recipients
  - You want a pasteable “all” status for debugging
title: "status"
---
# `openclaw 状态`

用于通道 + 会话的诊断信息。

```bash
openclaw status
openclaw status --all
openclaw status --deep
openclaw status --usage
```

说明：

- `--deep` 会运行实时探针（WhatsApp Web + Telegram + Discord + Google Chat + Slack + Signal）。
- 输出包含每个代理的会话存储，当配置了多个代理时。
- 概览包括网关 + 节点主机服务的安装/运行时状态（如果可用）。
- 概览包括更新通道 + git SHA（用于源代码检出）。
- 更新信息显示在概览中；如果存在更新，状态会提示运行 `openclaw update`（参见 [Updating](/install/updating)）。