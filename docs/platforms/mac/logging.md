---
summary: "OpenClaw logging: rolling diagnostics file log + unified log privacy flags"
read_when:
  - Capturing macOS logs or investigating private data logging
  - Debugging voice wake/session lifecycle issues
title: "macOS Logging"
---
# 日志记录（macOS）

## 循环诊断文件日志（调试面板）

OpenClaw 通过 swift-log 路由 macOS 应用日志（默认使用统一日志），当您需要持久化捕获时，可以将循环文件日志写入磁盘。

- 详细程度：**调试面板 → 日志 → 应用日志记录 → 详细程度**
- 启用：**调试面板 → 日志 → 应用日志记录 → "写入循环诊断日志（JSONL）"**
- 位置：`~/Library/Logs/OpenClaw/diagnostics.jsonl`（自动循环；旧文件以 `.1`、`.2`、… 为后缀）
- 清除：**调试面板 → 日志 → 应用日志记录 → "清除"**

注意事项：

- 这是**默认关闭的**。仅在积极调试时启用。
- 将文件视为敏感信息；未经审查请勿分享。

## macOS 上的统一日志私有数据

除非子系统选择加入 `privacy -off`，否则统一日志会隐藏大部分有效载荷。根据 Peter 关于 macOS [日志隐私诡计](https://steipete.me/posts/2025/logging-privacy-shenanigans)（2025）的撰写，这由 `/Library/Preferences/Logging/Subsystems/` 中按子系统名称键控的 plist 控制。只有新日志条目才会获取该标志，因此请在重现问题之前启用它。

## 为 OpenClaw 启用（`bot.molt`）

- 首先将 plist 写入临时文件，然后以 root 身份原子性地安装：

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

- 不需要重启；logd 会快速注意到文件，但只有新日志行将包含私有有效载荷。
- 使用现有助手查看更丰富的输出，例如 `./scripts/clawlog.sh --category WebChat --last 5m`。

## 调试后禁用

- 移除覆盖：`sudo rm /Library/Preferences/Logging/Subsystems/bot.molt.plist`。
- 可选运行 `sudo log config --reload` 以强制 logd 立即删除覆盖。
- 记住此功能可能包含电话号码和消息正文；仅在您确实需要额外详细信息时才保留 plist。