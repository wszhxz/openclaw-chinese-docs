---
summary: "Fix Chrome/Brave/Edge/Chromium CDP startup issues for OpenClaw browser control on Linux"
read_when: "Browser control fails on Linux, especially with snap Chromium"
title: "Browser Troubleshooting"
---
# 浏览器故障排除（Linux）

## 问题： "无法在端口18800上启动Chrome CDP"

OpenClaw的浏览器控制服务器无法启动Chrome/Brave/Edge/Chromium，并出现以下错误：

```
{"error":"Error: Failed to start Chrome CDP on port 18800 for profile \"openclaw\"."}
```

### 根本原因

在Ubuntu（以及许多Linux发行版）中，默认的Chromium安装是一个**snap包**。Snap的AppArmor限制干扰了OpenClaw生成和监控浏览器进程的方式。

`apt install chromium` 命令安装了一个重定向到snap的存根包：

```
Note, selecting 'chromium-browser' instead of 'chromium'
chromium-browser is already the newest version (2:1snap1-0ubuntu2).
```

这并不是一个真正的浏览器——它只是一个包装器。

### 解决方案1：安装Google Chrome（推荐）

安装官方的Google Chrome `.deb` 包，该包不会被snap沙箱化：

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y  # if there are dependency errors
```

然后更新您的OpenClaw配置 (`~/.openclaw/openclaw.json`)：

```json
{
  "browser": {
    "enabled": true,
    "executablePath": "/usr/bin/google-chrome-stable",
    "headless": true,
    "noSandbox": true
  }
}
```

### 解决方案2：使用Snap Chromium与仅附加模式

如果您必须使用snap Chromium，请配置OpenClaw以附加到手动启动的浏览器：

1. 更新配置：

```json
{
  "browser": {
    "enabled": true,
    "attachOnly": true,
    "headless": true,
    "noSandbox": true
  }
}
```

2. 手动启动Chromium：

```bash
chromium-browser --headless --no-sandbox --disable-gpu \
  --remote-debugging-port=18800 \
  --user-data-dir=$HOME/.openclaw/browser/openclaw/user-data \
  about:blank &
```

3. 可选地创建一个systemd用户服务来自启动Chrome：

```ini
# ~/.config/systemd/user/openclaw-browser.service
[Unit]
Description=OpenClaw Browser (Chrome CDP)
After=network.target

[Service]
ExecStart=/snap/bin/chromium --headless --no-sandbox --disable-gpu --remote-debugging-port=18800 --user-data-dir=%h/.openclaw/browser/openclaw/user-data about:blank
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

启用命令： `systemctl --user enable --now openclaw-browser.service`

### 验证浏览器是否正常工作

检查状态：

```bash
curl -s http://127.0.0.1:18791/ | jq '{running, pid, chosenBrowser}'
```

测试浏览：

```bash
curl -s -X POST http://127.0.0.1:18791/start
curl -s http://127.0.0.1:18791/tabs
```

### 配置参考

| 选项                   | 描述                                                          | 默认值                                                     |
| ------------------------ | -------------------------------------------------------------------- | ----------------------------------------------------------- |
| `browser.enabled`        | 启用浏览器控制                                               | `true`                                                      |
| `browser.executablePath` | Chromium基础浏览器二进制文件路径 (Chrome/Brave/Edge/Chromium) | 自动检测（优先选择默认浏览器当基于Chromium时） |
| `browser.headless`       | 无GUI运行                                                      | `false`                                                     |
| `browser.noSandbox`      | 添加 `--no-sandbox` 标志（某些Linux设置需要）               | `false`                                                     |
| `browser.attachOnly`     | 不启动浏览器，仅附加到现有浏览器                        | `false`                                                     |
| `browser.cdpPort`        | Chrome DevTools协议端口                                        | `18800`                                                     |

### 问题： "Chrome扩展中继正在运行，但没有标签页连接"

您正在使用 `chrome` 配置文件（扩展中继）。它期望OpenClaw浏览器扩展程序附加到活动标签页。

解决选项：

1. **使用托管浏览器：** `openclaw browser start --browser-profile openclaw`
   （或设置 `browser.defaultProfile: "openclaw"`）。
2. **使用扩展中继：** 安装扩展程序，打开一个标签页，并点击OpenClaw扩展图标以附加它。

注意事项：

- `chrome` 配置文件尽可能使用**系统默认的Chromium浏览器**。
- 本地 `openclaw` 配置文件自动分配 `cdpPort`/`cdpUrl`；仅在远程CDP时设置这些。