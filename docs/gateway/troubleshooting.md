---
summary: "Quick troubleshooting guide for common OpenClaw failures"
read_when:
  - Investigating runtime issues or failures
title: "Troubleshooting"
---
以下是您提供的技术文档的中文翻译，保留了原文的结构和术语，同时确保技术细节准确传达：

---

### 浏览器未启动（Linux）

如果您看到 `"Failed to start Chrome CDP on port 18800"`（无法在端口 18800 上启动 Chrome CDP）：

**最可能的原因**：Ubuntu 上的 Snap 包装的 Chromium。

**快速解决方法**：安装 Google Chrome：

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

然后在配置文件中设置：

```json
{
  "browser": {
    "executablePath": "/usr/bin/google-chrome-stable"
  }
}
```

**完整指南**：参见 [browser-linux-troubleshooting](/tools/browser-linux-troubleshooting)

---

### macOS 特定问题

#### 授予权限时应用崩溃（语音/麦克风）

如果点击隐私提示的 "允许" 时应用消失或显示 "Abort trap 6"：

**解决方法 1：重置 TCC 缓存**

```bash
tccutil reset All bot.molt.mac.debug
```

**解决方法 2：强制使用新捆绑 ID**  
如果重置无效，请更改 [`scripts/package-mac-app.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-app.sh) 中的 `BUNDLE_ID`（例如添加 `.test` 后缀），然后重新构建。这会强制 macOS 将其视为新应用。

---

### 网关卡在 "Starting..." 状态

应用会连接到本地网关的 18789 端口。如果卡住：

**解决方法 1：停止监督进程（推荐）**  
如果网关由 launchd 监督，杀死 PID 会重新启动。先停止监督进程：

```bash
openclaw gateway status
openclaw gateway stop
# 或：launchctl bootout gui/$UID/bot.molt.gateway（替换为 bot.molt.<profile>；旧版 com.openclaw.* 仍有效）
```

**解决方法 2：端口被占用（查找监听进程）**

```bash
lsof -nP -iTCP:18789 -sTCP:LISTEN
```

如果是一个未监督的进程，先尝试优雅停止，再强制终止：

```bash
kill -TERM <PID>
sleep 1
kill -9 <PID> # 最后手段
```

**解决方法 3：检查 CLI 安装**  
确保全局 `openclaw` CLI 已安装且版本匹配应用：

```bash
openclab --version
npm install -g openclaw@<version>
```

---

### 调试模式

获取详细日志：

```bash
# 在配置中开启跟踪日志：
#   ${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw/openclaw.json} -> { logging: { level: "trace" } }
#
# 然后运行带详细输出的命令：
openclaw gateway --verbose
openclab channels login --verbose
```

---

### 日志位置

| 日志类型                         | 存储位置                                                                 |
|------------------------------|--------------------------------------------------------------------------|
| 网关文件日志（结构化）         | `/tmp/openclaw/openclaw-YYYY-MM-DD.log`（或 `logging.file`）             |
| 网关服务日志（监督进程）       | macOS: `$OPENCLAW_STATE_DIR/logs/gateway.log` + `gateway.err.log`（默认: `~/.openclaw/logs/...`；配置文件使用 `~/.openclaw-<profile>/logs/...`）<br />Linux: `journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`<br />Windows: `schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST` |
| 会话文件                       | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                         |
| 媒体缓存                       | `$OPENCLAW_STATE_DIR/media/`                                             |
| 凭据                           | `$OPENCLAW_STATE_DIR/credentials/`                                       |

---

### 健康检查

```bash
# 监督进程 + 探测目标 + 配置路径
openclab gateway status
# 包括系统级扫描（旧版/额外服务，端口监听器）
openclab gateway status --deep

# 网关是否可达？
openclab health --json
# 如果失败，重新运行并包含连接详情：
openclab health --verbose

# 是否有进程在默认端口监听？
lsof -nP -iTCP:18789 -sTCP:LISTEN

# 最近活动（RPC 日志尾部）
openclab logs --follow
# 如果 RPC 不可用，使用备用日志
tail -20 /tmp/openclaw/openclaw-*.log
```

---

### 重置所有内容

终极解决方案：

```bash
openclab gateway stop
# 如果安装了服务并需要干净安装：
# openclab gateway uninstall

trash "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
openclab channels login         # 重新配对 WhatsApp
openclab gateway restart           # 或：openclab gateway
```

⚠️ 此操作将丢失所有会话，并需要重新配对 WhatsApp。

---

### 获取帮助

1. **先检查日志**：`/tmp/openclaw/`（默认：`openclaw-YYYY-MM-DD.log`，或您配置的 `logging.file`）
2. **在 GitHub 上搜索现有问题**
3. **打开新问题时提供以下信息**：
   - OpenClaw 版本
   - 相关日志片段
   - 复现步骤
   - 您的配置（请隐藏敏感信息！）

---

_"您是否尝试过关闭并重新启动？"_ — 每个 IT 人员的口头禅

🦞🔧