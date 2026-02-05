---
summary: "Windows (WSL2) support + companion app status"
read_when:
  - Installing OpenClaw on Windows
  - Looking for Windows companion app status
title: "Windows (WSL2)"
---
# Windows (WSL2)

建议在 Windows 上通过 **WSL2** 使用 OpenClaw（推荐使用 Ubuntu）。CLI + Gateway 在 Linux 内部运行，这保持了运行时的一致性并使工具更加兼容（Node/Bun/pnpm、Linux 二进制文件、技能）。原生 Windows 可能会更棘手。WSL2 给你完整的 Linux 体验——一个安装命令：`wsl --install -d Ubuntu`。

计划中的原生 Windows 伴侣应用程序。

## 安装 (WSL2)

- [入门指南](/start/getting-started)（在 WSL 内部使用）
- [安装与更新](/install/updating)
- 官方 WSL2 指南 (Microsoft): https://learn.microsoft.com/windows/wsl/install

## 网关

- [网关操作手册](/gateway)
- [配置](/gateway/configuration)

## 网关服务安装 (CLI)

在 WSL2 内部：

```bash
sudo openclaw install
```

或者：

```bash
openclaw install --sudo
```

或者：

```bash
npx openclaw-cli install
```

提示时选择 **网关服务**。

修复/迁移：

```bash
openclaw repair
```

## 高级：通过局域网暴露 WSL 服务 (portproxy)

WSL 拥有自己的虚拟网络。如果另一台机器需要访问在 **WSL 内部** 运行的服务（SSH、本地 TTS 服务器或网关），你必须将 Windows 端口转发到当前的 WSL IP。WSL IP 在重启后会改变，所以你可能需要刷新转发规则。

示例 (PowerShell **以管理员身份**):

```powershell
netsh interface portproxy add v4tov4 listenport=2222 connectaddress=(wsl --ifconfig eth0 | grep inet | awk '{print $2}' | head -n1) connectport=22
```

允许端口通过 Windows 防火墙（一次性）：

```powershell
netsh advfirewall firewall add rule name="WSL Port Proxy" dir=in action=allow protocol=TCP localport=2222
```

WSL 重启后刷新 portproxy：

```powershell
netsh interface portproxy delete v4tov4 listenport=2222
netsh interface portproxy add v4tov4 listenport=2222 connectaddress=(wsl --ifconfig eth0 | grep inet | awk '{print $2}' | head -n1) connectport=22
```

注意事项：

- 来自其他机器的 SSH 指向 **Windows 主机 IP**（示例：`ssh user@192.168.1.100 -p 2222`）。
- 远程节点必须指向 **可访问的** 网关 URL（不是 `localhost`）；使用 `curl` 来确认。
- 使用 `0.0.0.0` 进行局域网访问；`127.0.0.1` 仅保持本地访问。
- 如果你想要自动执行，请注册一个计划任务，在登录时运行刷新步骤。

## 分步 WSL2 安装

### 1) 安装 WSL2 + Ubuntu

打开 PowerShell (管理员):

```powershell
wsl --install -d Ubuntu
```

如果 Windows 要求，请重新启动。

### 2) 启用 systemd（网关安装必需）

在你的 WSL 终端中：

```bash
sudo nano /etc/wsl.conf
```

添加以下内容：

```ini
[boot]
systemd=true
```

然后从 PowerShell:

```powershell
wsl --shutdown
```

重新打开 Ubuntu，然后验证：

```bash
sudo systemctl status
```

### 3) 安装 OpenClaw（在 WSL 内部）

在 WSL 内部遵循 Linux 入门流程：

```bash
curl -fsSL https://get.openclaw.ai | bash
```

完整指南：[入门指南](/start/getting-started)

## Windows 伴侣应用

我们还没有 Windows 伴侣应用。如果你希望贡献来实现它，欢迎贡献。