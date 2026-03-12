---
summary: "OpenClaw logging: rolling diagnostics file log + unified log privacy flags"
read_when:
  - Capturing macOS logs or investigating private data logging
  - Debugging voice wake/session lifecycle issues
title: "macOS Logging"
---
# 日志记录 (macOS)

## 滚动诊断文件日志（调试面板）

OpenClaw 通过 swift-log 路由 macOS 应用日志（默认为统一日志），并且当您需要持久捕获时，可以将本地的滚动文件日志写入磁盘。

- 详细程度: **调试面板 → 日志 → 应用日志 → 详细程度**
- 启用: **调试面板 → 日志 → 应用日志 → “写入滚动诊断日志 (JSONL)”**
- 位置: `~/Library/Logs/OpenClaw/diagnostics.jsonl`（自动轮转；旧文件后缀为 `.1`, `.2`, …）
- 清除: **调试面板 → 日志 → 应用日志 → “清除”**

注意事项：

- 默认情况下这是**关闭的**。仅在积极调试时启用。
- 将文件视为敏感文件；未经审查不要分享。

## macOS 上统一日志的私有数据

除非子系统选择加入 `privacy -off`，否则统一日志会删除大多数有效负载。根据 Peter 在 [日志隐私操作](https://steipete.me/posts/2025/logging-privacy-shenanigans) (2025) 中的描述，这由 `/Library/Preferences/Logging/Subsystems/` 中的一个 plist 控制，该 plist 以子系统名称为键。只有新的日志条目才会拾取该标志，因此请在重现问题之前启用它。

## 为 OpenClaw 启用 (`ai.openclaw`)

- 先将 plist 写入临时文件，然后作为 root 原子性地安装它：

```bash
cat <<'EOF' >/tmp/ai.openclaw.plist
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
sudo install -m 644 -o root -g wheel /tmp/ai.openclaw.plist /Library/Preferences/Logging/Subsystems/ai.openclaw.plist
```

- 不需要重启；logd 会很快注意到该文件，但只有新的日志行才会包含私有有效负载。
- 使用现有的辅助工具查看更丰富的输出，例如 `./scripts/clawlog.sh --category WebChat --last 5m`。

## 调试后禁用

- 删除覆盖: `sudo rm /Library/Preferences/Logging/Subsystems/ai.openclaw.plist`。
- 可选运行 `sudo log config --reload` 以强制 logd 立即放弃覆盖。
- 请记住，此界面可能包括电话号码和消息正文；仅在您确实需要额外细节时保留 plist。