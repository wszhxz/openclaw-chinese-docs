---
summary: "OpenClaw on DigitalOcean (simple paid VPS option)"
read_when:
  - Setting up OpenClaw on DigitalOcean
  - Looking for cheap VPS hosting for OpenClaw
title: "DigitalOcean"
---
# OpenClaw on DigitalOcean

## 目标

在DigitalOcean上运行一个持久化的OpenClaw网关，每月费用为**$6**（或使用预留定价每月$4）。

如果你想要一个每月$0的选项，并且不介意使用ARM架构和特定提供商的设置，请参阅[Oracle Cloud指南](/platforms/oracle)。

## 成本比较（2026）

| 提供商     | 计划            | 规格                  | 每月价格    | 备注                                 |
| ------------ | --------------- | ---------------------- | ----------- | ------------------------------------- |
| Oracle Cloud | Always Free ARM | 最多4 OCPU, 24GB RAM | $0          | ARM, 容量有限 / 注册quirks |
| Hetzner      | CX22            | 2 vCPU, 4GB RAM        | €3.79 (~$4) | 最便宜的付费选项                  |
| DigitalOcean | Basic           | 1 vCPU, 1GB RAM        | $6          | 简单的UI, 良好的文档                    |
| Vultr        | Cloud Compute   | 1 vCPU, 1GB RAM        | $6          | 多个位置                        |
| Linode       | Nanode          | 1 vCPU, 1GB RAM        | $5          | 现在是Akamai的一部分                    |

**选择提供商：**

- DigitalOcean: 最简单的用户体验 + 预测性设置（本指南）
- Hetzner: 优秀的性价比（参阅[Hetzner指南](/platforms/hetzner)）
- Oracle Cloud: 可以每月$0，但更挑剔且仅限ARM（参阅[Oracle指南](/platforms/oracle)）

---

## 前提条件

- DigitalOcean账户（[注册并获得$200免费信用](https://m.do.co/c/signup)）
- SSH密钥对（或愿意使用密码认证）
- 大约20分钟

## 1) 创建Droplet

1. 登录到[DigitalOcean](https://cloud.digitalocean.com/)
2. 点击 **Create → Droplets**
3. 选择：
   - **区域:** 最接近你的（或你的用户）
   - **镜像:** Ubuntu 24.04 LTS
   - **大小:** Basic → Regular → **$6/mo** (1 vCPU, 1GB RAM, 25GB SSD)
   - **认证:** SSH密钥（推荐）或密码
4. 点击 **Create Droplet**
5. 记下IP地址

## 2) 通过SSH连接

```bash
ssh root@YOUR_DROPLET_IP
```

## 3) 安装OpenClaw

```bash
# Update system
apt update && apt upgrade -y

# Install Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt install -y nodejs

# Install OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# Verify
openclaw --version
```

## 4) 运行入站引导

```bash
openclaw onboard --install-daemon
```

向导将引导你完成以下步骤：

- 模型认证（API密钥或OAuth）
- 通道设置（Telegram, WhatsApp, Discord等）
- 网关令牌（自动生成）
- 守护进程安装（systemd）

## 5) 验证网关

```bash
# Check status
openclaw status

# Check service
systemctl --user status openclaw-gateway.service

# View logs
journalctl --user -u openclaw-gateway.service -f
```

## 6) 访问仪表板

网关默认绑定到回环地址。要访问控制UI：

**选项A: SSH隧道（推荐）**

```bash
# From your local machine
ssh -L 18789:localhost:18789 root@YOUR_DROPLET_IP

# Then open: http://localhost:18789
```

**选项B: Tailscale Serve（HTTPS，仅限回环）**

```bash
# On the droplet
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# Configure Gateway to use Tailscale Serve
openclaw config set gateway.tailscale.mode serve
openclaw gateway restart
```

打开: `https://<magicdns>/`

注意事项：

- Serve保持网关仅限回环，并通过Tailscale身份头进行身份验证。
- 如果需要使用令牌/密码，请设置 `gateway.auth.allowTailscale: false` 或使用 `gateway.auth.mode: "password"`。

**选项C: Tailnet绑定（无Serve）**

```bash
openclaw config set gateway.bind tailnet
openclaw gateway restart
```

打开: `http://<tailscale-ip>:18789` （需要令牌）。

## 7) 连接你的通道

### Telegram

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

### WhatsApp

```bash
openclaw channels login whatsapp
# Scan QR code
```

参阅[通道](/channels)获取其他提供商的信息。

---

## 1GB RAM优化

$6的droplet只有1GB RAM。为了使一切顺利运行：

### 添加交换空间（推荐）

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 使用更轻量级的模型

如果你遇到内存不足的情况，可以考虑：

- 使用基于API的模型（Claude, GPT）而不是本地模型
- 将 `agents.defaults.model.primary` 设置为更小的模型

### 监控内存

```bash
free -h
htop
```

---

## 持久化

所有状态存储在：

- `~/.openclaw/` — 配置、凭据、会话数据
- `~/.openclaw/workspace/` — 工作区（SOUL.md, 内存等）

这些在重启后仍然存在。定期备份它们：

```bash
tar -czvf openclaw-backup.tar.gz ~/.openclaw ~/.openclaw/workspace
```

---

## Oracle Cloud免费替代方案

Oracle Cloud提供**Always Free** ARM实例，其性能远超此处的任何付费选项——每月$0。

| 你将获得      | 规格                  |
| ----------------- | ---------------------- |
| **4 OCPUs**       | ARM Ampere A1          |
| **24GB RAM**      | 足够多了       |
| **200GB存储** | 块卷           |
| **永久免费**  | 无需信用卡收费 |

**注意事项：**

- 注册可能会很挑剔（如果失败请重试）
- ARM架构 — 大多数东西都能工作，但某些二进制文件需要ARM构建

完整的设置指南，请参阅[Oracle Cloud](/platforms/oracle)。有关注册提示和解决注册过程中的问题，请参阅此[社区指南](https://gist.github.com/rssnyder/51e3cfedd730e7dd5f4a816143b25dbd)。

---

## 故障排除

### 网关无法启动

```bash
openclaw gateway status
openclaw doctor --non-interactive
journalctl -u openclaw --no-pager -n 50
```

### 端口已被占用

```bash
lsof -i :18789
kill <PID>
```

### 内存不足

```bash
# Check memory
free -h

# Add more swap
# Or upgrade to $12/mo droplet (2GB RAM)
```

---

## 参见

- [Hetzner指南](/platforms/hetzner) — 更便宜，更强大
- [Docker安装](/install/docker) — 容器化设置
- [Tailscale](/gateway/tailscale) — 安全远程访问
- [配置](/gateway/configuration) — 完整配置参考