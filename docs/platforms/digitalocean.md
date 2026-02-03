---
summary: "OpenClaw on DigitalOcean (simple paid VPS option)"
read_when:
  - Setting up OpenClaw on DigitalOcean
  - Looking for cheap VPS hosting for OpenClaw
title: "DigitalOcean"
---
# 在DigitalOcean上使用OpenClaw

## 目标

在DigitalOcean上运行一个持久的OpenClaw网关，费用为**每月6美元**（或使用预留定价每月4美元）。

如果你想选择每月0美元的选项，并且不介意ARM架构和提供商特定的设置，可以查看[Oracle Cloud指南](/platforms/oracle)。

## 成本比较（2026）

| 提供商     | 计划            | 规格                  | 每月价格    | 备注                                 |
|------------|----------------|-----------------------|------------|--------------------------------------|
| Oracle Cloud | 总是免费ARM     | 最多4个OCPU，24GB内存 | 0美元      | ARM架构，容量/注册限制较多           |
| Hetzner    | CX22           | 2个vCPU，4GB内存      | 3.79欧元 (~4美元) | 最便宜的付费选项                     |
| DigitalOcean | 基础           | 1个vCPU，1GB内存      | 6美元      | 简单的UI，文档良好                   |
| Vultr      | 云计算         | 1个v. CPU，1GB内存    | 6美元      | 支持多个位置                         |
| Linode     | Nanode         | 1个vCPU，1GB内存      | 5美元      | 现在属于Akamai                       |

**选择提供商：**

- DigitalOcean：最简单的用户体验 + 可预测的设置（本指南）
- Hetzner：性价比高（查看[Hetzner指南](/platforms/hetzner)）
- Oracle Cloud：可以每月0美元，但设置更复杂且仅支持ARM架构（查看[Oracle指南](/platforms/oracle)）

---

## 先决条件

- DigitalOcean账户（[注册并获得200美元免费信用](https://m.do.co/c/signup)）
- SSH密钥对（或愿意使用密码认证）
- 约20分钟

## 1) 创建Droplet

1. 登录到[DigitalOcean](https://cloud.digitalocean.com/)
2. 点击**创建 → Droplets**
3. 选择：
   - **区域：** 离你（或你的用户）最近的区域
   - **镜像：** Ubuntu 24.04 LTS
   - **大小：** 基础 → 常规 → **6美元/月**（1个vCPU，1GB内存，25GB SSD）
   - **认证：** SSH密钥（推荐）或密码
4. 点击**创建Droplet**
5. 记录IP地址

## 2) 通过SSH连接

```bash
ssh root@YOUR_DROPLET_IP
```

## 3) 安装OpenClaw

```bash
# 更新系统
apt update && apt upgrade -y

# 安装Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs

# 安装OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# 验证
openclaw --version
```

## 4) 运行注册

```bash
openclaw onboard --install-daemon
```

向导将引导你完成以下步骤：

- 模型认证（API密钥或OAuth）
- 通道设置（Telegram、WhatsApp、Discord等）
- 网关令牌（自动生成）
- 守护进程安装（systemd）

## 5) 验证网关

```bash
# 检查状态
openclaw status

# 检查服务
systemctl --user status openclaw-gateway.service

# 查看日志
journalctl --user -u openclaw-gateway.service -f
```

## 6) 访问仪表板

网关默认绑定到环回地址。要访问控制UI：

**选项A：SSH隧道（推荐）**

```bash
# 从本地机器
ssh -L 18789:localhost:18789 root@YOUR_DROPLET_IP

# 然后打开：http://localhost:18789
```

**选项B：Tailscale Serve（HTTPS，仅限环回）**

```bash
# 在Droplet上
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# 配置网关使用Tailscale Serve
openclaw config set gateway.tailscale.mode serve
openclaw gateway restart
```

打开：`https://<magicdns>/`

说明：

- Serve保持网关仅限环回，并通过Tailscale身份头进行认证。
- 如果需要要求令牌/密码，设置`gateway.auth.allowTailscale: false`或使用`gateway.auth.mode: "password"`。

**选项C：Tailnet绑定（不使用Serve）**

```bash
openclaw config set gateway.bind tailnet
openclaw gateway restart
```

打开：`http://<tailscale-ip>:18789`（需要令牌）。

## 7) 连接你的通道

### Telegram

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

### WhatsApp

```bash
openclaw channels login whatsapp
# 扫描二维码
```

查看[通道](/channels)了解其他提供商。

---

## 1GB内存的优化

6美元的Droplet只有1GB内存。为了保持顺畅运行：

### 添加交换空间（推荐）

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 使用更轻量的模型

如果你遇到内存不足问题，可以考虑：

- 使用基于API的模型（Claude、GPT）而不是本地模型
- 将`agents.defaults.model.primary`设置为更小的模型

### 监控内存

```bash
free -h
htop
```

---

## 持久性

所有状态数据存储在：

- `~/.openclaw/` — 配置、凭证、会话数据
- `~/.openclaw/workspace/` — 工作空间（SOUL.md、记忆等）

这些数据在重启后仍然存在。建议定期备份：

```bash
tar -czvf openclaw-backup.tar.gz ~/.openclaw ~/.openclaw/workspace
```

---

## Oracle Cloud免费替代方案

Oracle Cloud提供**始终免费**的ARM实例，其性能显著高于此处的任何付费选项 —— 每月0美元。

| 你将获得的资源      | 规格                  |
|---------------------|-----------------------|
| **4个OCPU**         | ARM Ampere A1         |
| **24GB内存**        | 足够使用              |
| **200GB