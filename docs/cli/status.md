---
summary: "CLI reference for `openclaw status` (diagnostics, probes, usage snapshots)"
read_when:
  - You want a quick diagnosis of channel health + recent session recipients
  - You want a pasteable “all” status for debugging
title: "status"
---
# `openclaw status`

通道和会话的诊断。

```bash
openclaw status
openclaw status --all
openclaw status --deep
openclaw status --usage
```

注意事项：

- `--deep` 运行实时探测（WhatsApp Web + Telegram + Discord + Google Chat + Slack + Signal）。
- 输出包括每个代理的会话存储，当配置了多个代理时。
- 概述包括网关和节点主机服务的安装/运行状态（如果可用）。
- 概述包括更新通道 + git SHA（用于源代码检出）。
- 更新信息显示在概述中；如果有可用更新，状态会打印提示运行 `openclaw update`（参见[更新](/install/updating)）。