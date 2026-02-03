---
summary: "Windows (WSL2) support + companion app status"
read_when:
  - Installing OpenClaw on Windows
  - Looking for Windows companion app status
title: "Windows (WSL2)"
---
# Windows（WSL2）

在 Windows 上运行 OpenClaw 建议通过 **WSL2**（推荐 Ubuntu）。CLI + 网关会在 Linux 环境中运行，这可以保持运行时的一致性，并使工具兼容性大幅提升（Node/Bun/pnpm、Linux 二进制文件、技能）。原生 Windows 可能会更复杂。WSL2 会提供完整的 Linux 体验——只需一条命令即可安装：`wsl --install`。

原生 Windows 伴侣应用正在计划中。

## 安装（WSL2）

- [入门指南](/start/getting-started)（在 WSL 内使用）
- [安装与更新](/install/updating)
- 官方 WSL2 指南（Microsoft）：https://learn.microsoft.com/windows/wsl/install

## 网关

- [网关运行手册](/gateway)
- [配置](/gateway/configuration)

## 网关服务安装（CLI）

在 WSL2 中：

```
openclaw onboard --install-daemon
```

或：

```
openclaw gateway install
```

或：

```
openclaw configure
```

提示时选择 **网关服务**。

修复/迁移：

```
openclaw doctor
```

## 高级：通过 LAN 暴露 WSL 服务（端口代理）

WSL 有自己的虚拟网络。如果另一台机器需要访问正在 **WSL 内运行** 的服务（SSH、本地 TTS 服务器或网关），则必须将 Windows 端口转发到当前 WSL 的 IP 地址。WSL 的 IP 地址在重启后会变化，因此可能需要刷新转发规则。

示例（以管理员身份运行 PowerShell）：

```powershell
$Distro = "Ubuntu-24.04"
$ListenPort = 2222
$TargetPort = 22

$WslIp = (wsl -d $Distro -- hostname -I).Trim().Split(" ")[0]
if (-not $WslIp) { throw "未找到 WSL IP 地址。" }

netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=$ListenPort `
  connectaddress=$WslIp connectport=$TargetPort
```

通过 Windows 防火墙允许端口（一次性）：

```powershell
New-NetFirewallRule -DisplayName "WSL SSH $ListenPort" -Direction Inbound `
  -Protocol TCP -LocalPort $ListenPort -Action Allow
```

在 WSL 重启后刷新端口代理：

```powershell
netsh interface portproxy delete v4tov4 listenport=$ListenPort listenaddress=0.0.0.0 | Out-Null
netsh interface portproxy add v4tov4 listenport=$ListenPort listenaddress=0.0.0.0 `
  connectaddress=$WslIp connectport=$TargetPort | Out-Null
```

注意事项：

- 从另一台机器 SSH 到 **Windows 主机 IP**（示例：`ssh user@windows-host -p 2222`）。
- 远程节点必须指向一个 **可到达** 的网关 URL（不能使用 `127.0.0.1`）；使用 `openclaw status --all` 确认。
- 使用 `listenaddress=0.0.0.0` 以实现 LAN 访问；`127.0.0.1` 仅限本地访问。
- 如果希望自动完成此操作，可注册一个计划任务，在登录时运行刷新步骤。

## WSL2 安装步骤指南

### 1) 安装 WSL2 + Ubuntu

打开 PowerShell（管理员）：

```powershell
wsl --install
# 或显式选择一个发行版：
wsl --list --online
wsl --install -d Ubuntu-24.04
```

如果 Windows 提示重启，请执行。

### 2) 启用 systemd（网关安装必需）

在 WSL 终端中：

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

然后从 PowerShell：

```powershell
wsl --shutdown
```

重新打开 Ubuntu，然后验证：

```bash
systemctl --user status
```

### 3) 安装 OpenClaw（在 WSL 内）

在 WSL 中按照 Linux 入门流程操作：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # 第一次运行时会自动安装 UI 依赖
pnpm build
openclaw onboard
```

完整指南：[入门指南](/start/getting-started)

## Windows 伴侣应用

目前我们尚未推出 Windows 伴侣应用。如果您希望贡献代码以实现该功能，欢迎提交贡献。