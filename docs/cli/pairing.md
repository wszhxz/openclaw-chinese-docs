---
summary: "CLI reference for `openclaw pairing` (approve/list pairing requests)"
read_when:
  - You’re using pairing-mode DMs and need to approve senders
title: "pairing"
---
# `openclaw pairing`

批准或检查 DM 配对请求（适用于支持配对的频道）。

相关文档：

- 配对流程：[配对](/channels/pairing)

## 命令

```bash
openclaw pairing list telegram
openclaw pairing list --channel telegram --account work
openclaw pairing list telegram --json

openclaw pairing approve telegram <code>
openclaw pairing approve --channel telegram --account work <code> --notify
```

## 注意事项

- 频道输入：可通过位置参数传入（`pairing list telegram`），或使用 `--channel <channel>` 指定。
- `pairing list` 支持多账号频道的 `--account <accountId>`。
- `pairing approve` 支持 `--account <accountId>` 和 `--notify`。
- 若仅配置了一个支持配对的频道，则允许使用 `pairing approve <code>`。