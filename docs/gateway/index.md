---
summary: "Runbook for the Gateway service, lifecycle, and operations"
read_when:
  - Running or debugging the gateway process
title: "Gateway Runbook"
---
以下是该技术文档的中文翻译：

---

**网关服务管理（CLI）**

使用网关CLI进行安装/启动/停止/重启/状态检查：

```bash
openclaw 网关 状态
openclaw 网关 安装
openclaw 网关 停止
openclaw 网关 重启
openclaw 日志 --跟随
```

**说明：**

- `gateway 状态` 默认通过服务解析的端口/配置探测网关RPC（可通过`--url`覆盖）。
- `gateway 状态 --deep` 添加系统级扫描（启动代理/system单位）。
- `gateway 状态 --no-probe` 跳过RPC探测（网络故障时有用）。
- `gateway 状态 --json` 适用于脚本的稳定输出。
- `gateway 状态` 分别报告**监督运行时**（launchd/systemd运行）和**RPC可达性**（WS连接+状态RPC）。
- `gateway 状态` 打印配置路径+探测目标以避免“本地主机 vs LAN绑定”混淆和配置不匹配。
- `gateway 状态` 在服务看起来运行但端口关闭时包含最后一次网关错误行。
- `日志` 通过RPC尾随网关文件日志（无需手动`tail`/`grep`）。
- 如果检测到其他类似网关的服务，CLI会在非OpenClaw配置服务时发出警告。
  我们仍建议**每台机器一个网关**用于大多数设置；使用隔离的配置文件/端口用于冗余或救援机器人。参见[多个网关](/网关/多个网关)。
  - 清理：`openclaw 网关 卸载`（当前服务）和`openclaw 医生`（旧版迁移）。
- `gateway 安装` 在已安装时为无操作；使用`openclaw 网关 安装 --force`重新安装（配置文件/环境/路径更改）。

**捆绑的mac应用：**

- OpenClaw.app 可以捆绑基于Node的网关中继并安装带有标签的用户级启动代理`bot.molt.gateway`（或`bot.molt.<配置文件>`；旧版`com.openclaw.*`标签仍能干净卸载）。
- 要干净停止，使用`openclaw 网关 停止`（或`launchctl bootout gui/$UID/bot.molt.gateway`）。
- 要重启，使用`openclab 网关 重启`（或`launchctl kickstart -k gui/$UID/bot.molt.gateway`）。
  - `launchctl` 仅在启动代理已安装时有效；否则先使用`openclaw 网关 安装`。
  - 运行命名配置文件时将标签替换为`bot.molt.<配置文件>`。

**监督（systemd用户单元）**

OpenClaw在Linux/WSL2上默认安装**systemd用户服务**。我们建议单用户机器使用用户服务（更简单的环境，用户级配置）。
使用**系统服务**用于多用户或始终运行的服务器（无需残留，共享监督）。

`openclaw 网关 安装`写入用户单元。`openclaw 医生`审核单元并可更新为当前推荐默认值。

创建`~/.config/systemd/user/openclaw-gateway[-<配置文件>].service`：

```
[Unit]
Description=OpenClaw 网关（配置文件：<配置文件>, v<版本>）
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw 网关 --端口 18789
Restart=always
RestartSec=5
Environment=OPENCLAW_GATEWAY_TOKEN=
WorkingDirectory=/home/youruser

[Install]
WantedBy=default.target
```

启用残留（确保用户服务在注销/空闲后仍存活）：

```
sudo loginctl enable-linger youruser
```

在Linux/WSL2上运行此操作（可能提示sudo；写入`/var/lib/systemd/linger`）。
然后启用服务：

```
systemctl --user enable --now openclaw-gateway[-<配置文件>].service
```

**替代方案（系统服务）** - 对于始终运行或多用户服务器，您可以安装systemd **系统**单元（无需残留）。
创建`/etc/systemd/system/openclaw-gateway[-<配置文件>].service`（复制上述单元，切换`WantedBy=multi-user.target`，设置`User=` + `WorkingDirectory=`），然后：

```
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-gateway[-<配置文件>].service
```

**Windows（WSL2）**

Windows安装应使用**WSL2**并遵循上述Linux systemd部分。

**操作检查**

- 存活状态：打开WS并发送`req:connect` → 期望`res`带有`payload.type="hello-ok"`（含快照）。
- 就绪状态：调用`health` → 期望`ok: true`且`linkChannel`中存在链接通道（如适用）。
- 调试：订阅`tick`和`presence`事件；确保`status`显示链接/认证时间；presence条目显示网关主机和连接客户端。

**安全保证**

- 默认假设每台主机一个网关；如果运行多个配置文件，隔离端口/状态并定位正确实例。
- 不回退到直接Baileys连接；如果网关不可用，发送操作将快速失败。
- 非连接首帧或格式错误的JSON将被拒绝并关闭套接字。
- 优雅关闭：关闭前发出`shutdown`事件；客户端必须处理关闭+重新连接。

**CLI辅助工具**

- `openclaw 网关 health|status` — 通过网关WS请求健康状态。
- `openclaw 消息 发送 --目标 <号码> --消息 "hi" [--媒体 ...]` — 通过网关发送（WhatsApp的幂等性）。
- `openclaw 代理 --消息 "hi" --到 <号码>` — 运行代理回合（默认等待最终响应）。
- `openclab 网关 调用 <方法> --参数 '{"k":"v"}'` — 调试的原始方法调用器。
- `openclab 网关 停止|重启` — 停止