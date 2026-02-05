---
summary: "Windows (WSL2) support + companion app status"
read_when:
  - Installing OpenClaw on Windows
  - Looking for Windows companion app status
title: "Windows (WSL2)"
---
# Windows (WSL2)

在Windows上推荐通过WSL2（推荐使用Ubuntu）安装OpenClaw。CLI + Gateway运行在Linux内部，这使得运行时保持一致，并使工具更加兼容（Node/Bun/pnpm, Linux二进制文件, 技能）。原生Windows可能会更复杂。WSL2为您提供完整的Linux体验 —— 安装命令：`wsl --install`。

计划推出原生Windows配套应用程序。

## 安装 (WSL2)

- [入门指南](/start/getting-started)（在WSL内部使用）
- [安装与更新](/install/updating)
- 官方WSL2指南（Microsoft）：https://learn.microsoft.com/windows/wsl/install

## Gateway

- [Gateway操作手册](/gateway)
- [配置](/gateway/configuration)

## Gateway服务安装 (CLI)

在WSL2内部：

```
openclaw onboard --install-daemon
```

或者：

```
openclaw gateway install
```

或者：

```
openclaw configure
```

提示时选择**Gateway服务**。

修复/迁移：

```
openclaw doctor
```

## 高级：通过LAN暴露WSL服务（端口代理）

WSL有自己的虚拟网络。如果另一台机器需要访问**在WSL内部运行的服务**（SSH，本地TTS服务器，或Gateway），您必须将Windows端口转发到当前WSL IP。WSL IP在重启后会更改，因此您可能需要刷新转发规则。

示例（以管理员身份运行PowerShell）：

```powershell
$Distro = "Ubuntu-24.04"
$ListenPort = 2222
$TargetPort = 22

$WslIp = (wsl -d $Distro -- hostname -I).Trim().Split(" ")[0]
if (-not $WslIp) { throw "WSL IP not found." }

netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=$ListenPort `
  connectaddress=$WslIp connectport=$TargetPort
```

允许Windows防火墙通过该端口（一次性）：

```powershell
New-NetFirewallRule -DisplayName "WSL SSH $ListenPort" -Direction Inbound `
  -Protocol TCP -LocalPort $ListenPort -Action Allow
```

在WSL重启后刷新portproxy：

```powershell
netsh interface portproxy delete v4tov4 listenport=$ListenPort listenaddress=0.0.0.0 | Out-Null
netsh interface portproxy add v4tov4 listenport=$ListenPort listenaddress=0.0.0.0 `
  connectaddress=$WslIp connectport=$TargetPort | Out-Null
```

注意：

- 从另一台机器进行SSH连接时，目标是**Windows主机IP**（示例：`ssh user@windows-host -p 2222`）。
- 远程节点必须指向一个**可访问的**Gateway URL（不是`127.0.0.1`）；使用
  `openclaw status --all`确认。
- 使用`listenaddress=0.0.0.0`进行局域网访问；`127.0.0.1`仅限本地访问。
- 如果希望自动完成此操作，请注册一个计划任务，在登录时运行刷新步骤。

## 逐步WSL2安装

### 1) 安装WSL2 + Ubuntu

打开PowerShell（管理员）：

```powershell
wsl --install
# Or pick a distro explicitly:
wsl --list --online
wsl --install -d Ubuntu-24.04
```

如果Windows提示，请重启。

### 2) 启用systemd（Gateway安装所需）

在您的WSL终端中：

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

然后从PowerShell：

```powershell
wsl --shutdown
```

重新打开Ubuntu，然后验证：

```bash
systemctl --user status
```

### 3) 在WSL内部安装OpenClaw

按照WSL内部的Linux入门流程进行安装：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # auto-installs UI deps on first run
pnpm build
openclaw onboard
```

完整指南：[入门指南](/start/getting-started)

## Windows配套应用程序

我们目前还没有Windows配套应用程序。如果您愿意贡献，请提供帮助以实现这一目标。