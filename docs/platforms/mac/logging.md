---
summary: "OpenClaw logging: rolling diagnostics file log + unified log privacy flags"
read_when:
  - Capturing macOS logs or investigating private data logging
  - Debugging voice wake/session lifecycle issues
title: "macOS Logging"
---
# 日志记录 (macOS)

## 滚动诊断文件日志 (调试面板)

OpenClaw 通过 swift-log（默认为统一日志记录）路由 macOS 应用程序日志，并且在需要持久化捕获时可以写入本地滚动文件日志到磁盘。

- 详细程度: **调试面板 → 日志 → 应用程序日志记录 → 详细程度**
- 启用: **调试面板 → 日志 → 应用程序日志记录 → “写入滚动诊断日志 (JSONL)”**
- 位置: `~/Library/Logs/OpenClaw/diagnostics.jsonl` (自动轮转；旧文件会附加后缀 `.1`, `.2`, …)
- 清除: **调试面板 → 日志 → 应用程序日志记录 → “清除”**

注意:

- 默认情况下此功能是**关闭的**。仅在主动调试时启用。
- 将文件视为敏感信息；未经审查不要分享。

## macOS 上统一日志记录的私有数据

除非子系统选择加入 `privacy -off`，否则统一日志记录会红acted 大多数负载。根据 Peter 在 macOS [日志记录隐私诡计](https://steipete.me/posts/2025/logging-privacy-shenanigans) (2025) 的文章，这由 `/Library/Preferences/Logging/Subsystems/` 中以子系统名称为键的 plist 控制。只有新的日志条目才会拾取该标志，因此在重现问题之前启用它。

## 为 OpenClaw 启用 (`bot.molt`)

- 首先将 plist 写入临时文件，然后以 root 身份原子安装：

```bash
cat <<'EOF' >/tmp/bot.molt.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>DEFAULT-OPTIONS</key>
    <dict>
        <key>Enable-Private-Data</key>
        <true/>
    </dict>
</dict>
</plist>
EOF
sudo install -m 644 -o root -g wheel /tmp/bot.molt.plist /Library/Preferences/Logging/Subsystems/bot.molt.plist
```

- 不需要重启；logd 会快速注意到文件，但只有新的日志行将包含私有负载。
- 使用现有的辅助工具查看更丰富的输出，例如 `./scripts/clawlog.sh --category WebChat --last 5m`。

## 调试后禁用

- 移除覆盖: `sudo rm /Library/Preferences/Logging/Subsystems/bot.molt.plist`。
- 可选运行 `sudo log config --reload` 强制 logd 立即丢弃覆盖。
- 记住此界面可能包含电话号码和消息正文；仅在您积极需要额外详细信息时保留 plist。