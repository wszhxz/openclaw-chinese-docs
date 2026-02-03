---
summary: "Automated, hardened OpenClaw installation with Ansible, Tailscale VPN, and firewall isolation"
read_when:
  - You want automated server deployment with security hardening
  - You need firewall-isolated setup with VPN access
  - You're deploying to remote Debian/Ubuntu servers
title: "Ansible"
---
# Ansible 安装

将 OpenClaw 部署到生产服务器的推荐方式是通过 **[openclaw-ansible](https://github.com/openclaw/openclaw-ansible)** —— 一个以安全为首要目标的自动化安装工具。

## 快速入门

一键安装：

```bash
curl -fsSL https://raw.githubusercontent.com/openclaw/openclaw-ansible/main/install.sh | bash
```

> **📦 完整指南：[github.com/openclaw/openclaw-ansible](https://github.com/openclaw/openclaw-ansible)**
>
> openclaw-ansible 仓库是 Ansible 部署的权威来源。本页面是快速概览。

## 您将获得

- 🔒 **以防火墙为先的安全性**：UFW + Docker 隔离（仅 SSH + Tailscale 可访问）
- 🔐 **Tailscale VPN**：无需公开暴露服务即可实现安全远程访问
- 🐳 **Docker**：隔离的沙箱容器，仅限本地主机绑定
- 🛡️ **纵深防御**：4 层安全架构
- 🚀 **一键设置**：几分钟内完成完整部署
- 🔧 **Systemd 集成**：启动时自动启动并启用强化安全

## 要求

- **操作系统**：Debian 11+ 或 Ubuntu 20.04+
- **权限**：Root 或 sudo 权限
- **网络**：用于包安装的互联网连接
- **Ansible**：2.14+（由快速入门脚本自动安装）

## 安装内容

Ansible playbook 安装并配置以下内容：

1. **Tailscale**（用于安全远程访问的 mesh VPN）
2. **UFW 防火墙**（仅开放 SSH + Tailscale 端口）
3. **Docker CE + Compose V2**（用于代理沙箱）
4. **Node.js 22.x + pnpm**（运行时依赖）
5. **OpenClaw**（基于主机，非容器化）
6. **Systemd 服务**（启动时自动启动并启用安全强化）

注意：网关直接运行在主机上（不在 Docker 中），但代理沙箱使用 Docker 实现隔离。详情请参见 [Sandboxing](/gateway/sandboxing)。

## 安装后设置

安装完成后，切换到 openclaw 用户：

```bash
sudo -i -u openclaw
```

安装后脚本将引导您完成以下步骤：

1. **入职向导**：配置 OpenClaw 设置
2. **提供者登录**：连接 WhatsApp/Telegram/Discord/Signal
3. **网关测试**：验证安装
4. **Tailscale 设置**：连接到您的 VPN 网格

### 快速命令

```bash
# 检查服务状态
sudo systemctl status openclaw

# 查看实时日志
sudo journalctl -u openclaw -f

# 重启网关
sudo systemctl restart openclaw

# 提供者登录（以 openclaw 用户运行）
sudo -i -u openclaw
openclaw channels login
```

## 安全架构

### 4 层防御

1. **防火墙（UFW）**：仅公开 SSH（22）+ Tailscale（41641/udp）
2. **VPN（Tailscale）**：仅通过 VPN 网格访问网关
3. **Docker 隔离**：DOCKER-USER iptables 链防止外部端口暴露
4. **Systemd 强化**：NoNewPrivileges、PrivateTmp、无特权用户

### 验证

测试外部攻击面：

```bash
nmap -p- YOUR_SERVER_IP
```

应仅显示 **端口 22**（SSH）开放。所有其他服务（网关、Docker）均被锁定。

### Docker 可用性

Docker 用于 **代理沙箱**（隔离的工具执行），而不是用于运行网关本身。网关仅绑定到本地主机，并通过 Tailscale VPN 访问。

请参见 [Multi-Agent Sandbox & Tools](/multi-agent-sandbox-tools) 了解沙箱配置。

## 手动安装

如果您更倾向于手动控制而非自动化：

```bash
# 1. 安装先决条件
sudo apt update && sudo apt install -y ansible git

# 2. 克隆仓库
git clone https://github.com/openclaw/openclaw-ansible.git
cd openclaw-ansible

# 3. 安装 Ansible 集合
ansible-galaxy collection install -r requirements.yml

# 4. 运行 playbook
./run-playbook.sh

# 或直接运行（然后手动执行 /tmp/openclaw-setup.sh）
# ansible-playbook playbook.yml --ask-become-pass
```

## 更新 OpenClaw

Ansible 安装程序为手动更新设置了 OpenClaw。有关标准更新流程，请参见 [Updating](/install/updating)。

要重新运行 Ansible playbook（例如进行配置更改）：

```bash
cd openclaw-ansible
./run-playbook.sh
```

注意：此操作是幂等的，可以安全地多次运行。

## 故障排除

### 防火墙阻止了我的连接

如果您被锁定：

- 首先确保可以通过 Tailscale VPN 访问
- SSH 访问（端口 22）始终允许
- 网关 **仅** 通过 Tailscale 访问（设计如此）

### 服务无法启动

```bash
# 检查日志
sudo journalctl -u openclaw -n 100

# 验证权限
sudo ls -la /opt/openclaw

# 测试手动启动
sudo -i -u openclaw
cd ~/openclaw
pnpm start
```

### Docker 沙箱问题

```bash
# 验证 Docker 是否正在运行
sudo systemctl status docker

# 检查沙箱镜像
sudo docker images | grep openclaw-s