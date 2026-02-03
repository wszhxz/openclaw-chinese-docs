---
summary: "OpenClaw logging: rolling diagnostics file log + unified log privacy flags"
read_when:
  - Capturing macOS logs or investigating private data logging
  - Debugging voice wake/session lifecycle issues
title: "macOS Logging"
---
# 日志记录（macOS）

## 旋转诊断文件日志（调试面板）

OpenClaw 通过 swift-log（默认统一日志记录）将 macOS 应用日志路由到系统，并在需要持久捕获时可将本地、旋转的文件日志写入磁盘。

- 详细程度：**调试面板 → 日志 → 应用日志 → 详细程度**
- 启用：**调试面板 → 日志 → 应用日志 → “写入旋转诊断日志（JSONL）”**
- 位置：`~/Library/Logs/OpenClaw/diagnostics.jsonl`（自动轮转；旧文件以 `.1`、`.2` 等后缀命名）
- 清除：**调试面板 → 日志 → 应用日志 → “清除”**

注意事项：

- 此功能**默认关闭**。仅在主动调试时启用。
- 将此文件视为敏感信息；在未经审查的情况下不要分享它。

## macOS 上统一日志记录的私有数据

统一日志记录会屏蔽大多数负载，除非子系统选择启用 `privacy -off`。根据 Peter 在 macOS [日志隐私问题](https://steipete.me/posts/2025/logging-privacy-shenanigans)（2025）的说明，此行为由 `/Library/Preferences/Logging/Subsystems/` 目录下以子系统名称为键的 plist 文件控制。仅新日志条目会继承此标志，因此在重现问题前请先启用它。

## 为 OpenClaw 启用（`bot.molt`）

- 首先将 plist 写入临时文件，然后以 root 权限原子安装：

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
``
- 无需重启；logd 会快速识别文件，但只有新日志行会包含私有负载。
- 使用现有辅助工具查看更丰富的输出，例如 `./scripts/clawlog.sh --category WebChat --last 5m`。

## 调试后禁用

- 移除覆盖：`sudo rm /Library/Preferences/Logging/Subsystems/bot.molt.plist`。
- 可选运行 `sudo log config --reload` 强制 logd 立即丢弃覆盖。
- 请注意此接口可能包含电话号码和消息内容；仅在需要额外详细信息时保留 plist 文件。