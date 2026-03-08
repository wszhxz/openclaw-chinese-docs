---
summary: "CLI reference for `openclaw voicecall` (voice-call plugin command surface)"
read_when:
  - You use the voice-call plugin and want the CLI entry points
  - You want quick examples for `voicecall call|continue|status|tail|expose`
title: "voicecall"
---
# `openclaw voicecall`

`voicecall` 是一个由插件提供的命令。仅当安装并启用了语音通话插件时才会显示。

主要文档：

- 语音通话插件：[Voice Call](/plugins/voice-call)

## 常用命令

```bash
openclaw voicecall status --call-id <id>
openclaw voicecall call --to "+15555550123" --message "Hello" --mode notify
openclaw voicecall continue --call-id <id> --message "Any questions?"
openclaw voicecall end --call-id <id>
```

## 暴露 Webhook（Tailscale）

```bash
openclaw voicecall expose --mode serve
openclaw voicecall expose --mode funnel
openclaw voicecall expose --mode off
```

安全说明：仅将 Webhook 端点暴露给您信任的网络。可能情况下，优先使用 Tailscale Serve 而不是 Funnel。