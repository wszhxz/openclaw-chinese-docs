---
summary: "CLI reference for `openclaw pairing` (approve/list pairing requests)"
read_when:
  - You’re using pairing-mode DMs and need to approve senders
title: "pairing"
---
# `openclaw pairing`

批准或检查 DM 配对请求（适用于支持配对的频道）。

相关：

- 配对流程：[Pairing](/channels/pairing)

## 命令

```bash
openclaw pairing list telegram
openclaw pairing list --channel telegram --account work
openclaw pairing list telegram --json

openclaw pairing approve <code>
openclaw pairing approve telegram <code>
openclaw pairing approve --channel telegram --account work <code> --notify
```

## `pairing list`

列出单个频道的待处理配对请求。

选项：

- `[channel]`: 位置参数频道 ID
- `--channel <channel>`: 显式频道 ID
- `--account <accountId>`: 多账户频道的账户 ID
- `--json`: 机器可读输出

注意：

- 如果配置了多个支持配对的频道，则必须通过位置参数或使用 `--channel` 提供频道。
- 只要频道 ID 有效，允许使用扩展频道。

## `pairing approve`

批准待处理的配对代码并允许该发送者。

用法：

- `openclaw pairing approve <channel> <code>`
- `openclaw pairing approve --channel <channel> <code>`
- `openclaw pairing approve <code>` 当仅配置了一个支持配对的频道时

选项：

- `--channel <channel>`: 显式频道 ID
- `--account <accountId>`: 多账户频道的账户 ID
- `--notify`: 在同一频道向请求者发送确认信息

## 注意

- 频道输入：以位置参数传递 (`pairing list telegram`) 或使用 `--channel <channel>`。
- `pairing list` 支持用于多账户频道的 `--account <accountId>`。
- `pairing approve` 支持 `--account <accountId>` 和 `--notify`。
- 如果仅配置了一个支持配对的频道，则允许使用 `pairing approve <code>`。