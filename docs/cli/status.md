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

注意：

- `--deep` 运行实时探测（WhatsApp Web + Telegram + Discord + Google Chat + Slack + Signal）。
- 当配置了多个代理时，输出包含每个代理的会话存储。
- 概览包含网关 + 节点主机服务的安装/运行时状态（如果可用）。
- 概览包含更新通道 + git SHA（用于源代码检出）。
- 更新信息显示在概览中；如果有可用更新，状态会打印提示以运行 `openclaw update`（参见 [更新](/install/updating)）。
- 只读状态显示（`status`、`status --json`、`status --all`）尽可能解析其目标配置路径支持的 SecretRefs。
- 如果配置了支持的通道 SecretRef 但在当前命令路径中不可用，状态将保持只读并报告降级输出而不是崩溃。人类可读输出显示警告，例如“配置的令牌在当前命令路径中不可用”，并且 JSON 输出包含 `secretDiagnostics`。