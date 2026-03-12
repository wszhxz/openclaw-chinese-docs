---
summary: "Windows (WSL2) support + companion app status"
read_when:
  - Installing OpenClaw on Windows
  - Looking for Windows companion app status
title: "Windows (WSL2)"
---
# Windows (WSL2)

在Windows上使用OpenClaw建议**通过WSL2**（推荐Ubuntu）。CLI + Gateway在Linux中运行，这保持了运行时的一致性，并使工具更加兼容（Node/Bun/pnpm、Linux二进制文件、技能）。原生Windows可能会更复杂。WSL2为您提供完整的Linux体验——一条命令即可安装：`wsl --install`。

计划开发原生Windows配套应用程序。

## 安装 (WSL2)

- [入门](/start/getting-started)（在WSL内使用）
- [安装与更新](/install/updating)
- 官方WSL2指南（Microsoft）: [https://learn.microsoft.com/windows/wsl/install](https://learn.microsoft.com/windows/wsl/install)

## Gateway

- [Gateway手册](/gateway)
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

## 在Windows登录前自动启动Gateway

对于无头设置，请确保即使没有人登录到Windows，整个启动链也能运行。

### 1) 保持用户服务无需登录即可运行

在WSL内：

```bash
sudo loginctl enable-linger "$(whoami)"
```

### 2) 安装OpenClaw gateway用户服务

在WSL内：

```bash
openclaw gateway install
```

### 3) 在Windows启动时自动启动WSL

以管理员身份在PowerShell中执行：

```powershell
schtasks /create /tn "WSL Boot" /tr "wsl.exe -d Ubuntu --exec /bin/true" /sc onstart /ru SYSTEM
```

将`Ubuntu`替换为您的发行版名称：

```powershell
wsl --list --verbose
```

### 验证启动链

重启后（在Windows登录之前），从WSL检查：

```bash
systemctl --user is-enabled openclaw-gateway
systemctl --user status openclaw-gateway --no-pager
```

## 高级：通过局域网暴露WSL服务 (portproxy)

WSL有自己的虚拟网络。如果另一台机器需要访问**WSL内部**运行的服务（SSH、本地TTS服务器或Gateway），则必须将Windows端口转发到当前的WSL IP。WSL IP在重启后会改变，因此您可能需要刷新转发规则。

示例（以管理员身份在PowerShell中执行）：

```powershell
$Distro = "Ubuntu-24.04"
$ListenPort = 2222
$TargetPort = 22

$WslIp = (wsl -d $Distro -- hostname -I).Trim().Split(" ")[0]
if (-not $WslIp) { throw "WSL IP not found." }

netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=$ListenPort `
  connectaddress=$WslIp connectport=$TargetPort
```

允许端口通过Windows防火墙（一次性操作）：

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

注意事项：

- 从另一台机器进行SSH连接时目标是**Windows主机IP**（例如：`ssh user@windows-host -p 2222`）。
- 远程节点必须指向一个**可到达**的Gateway URL（不是`127.0.0.1`）；使用`openclaw status --all`来确认。
- 使用`listenaddress=0.0.0.0`进行局域网访问；`127.0.0.1`仅限本地访问。
- 如果希望自动执行此操作，请注册一个计划任务，在登录时运行刷新步骤。

## WSL2逐步安装

### 1) 安装WSL2 + Ubuntu

打开PowerShell（管理员）：

```powershell
wsl --install
# Or pick a distro explicitly:
wsl --list --online
wsl --install -d Ubuntu-24.04
```

如果Windows提示，请重启。

### 2) 启用systemd（Gateway安装必需）

在您的WSL终端中：

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

然后从PowerShell中执行：

```powershell
wsl --shutdown
```

重新打开Ubuntu，然后验证：

```bash
systemctl --user status
```

### 3) 安装OpenClaw（在WSL内）

按照WSL内的Linux入门流程进行安装：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # auto-installs UI deps on first run
pnpm build
openclaw onboard
```

完整指南：[入门](/start/getting-started)

## Windows配套应用

我们目前还没有Windows配套应用。如果您希望贡献代码使其成为现实，欢迎参与。