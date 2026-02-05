---
summary: "OpenClaw on DigitalOcean (simple paid VPS option)"
read_when:
  - Setting up OpenClaw on DigitalOcean
  - Looking for cheap VPS hosting for OpenClaw
title: "DigitalOcean"
---
# DigitalOcean 上的 OpenClaw

## 目标

在 DigitalOcean 上运行一个持久化的 OpenClaw 网关，每月费用为 **$6**（或使用预留定价每月 $4）。

如果您想要零成本选项且不介意 ARM 架构和特定供应商设置，请参阅 [Oracle Cloud 指南](/platforms/oracle)。

## 成本对比（2026年）

| 提供商       | 套餐            | 规格                   | 月价格      | 备注                                  |
| ------------ | --------------- | ---------------------- | ----------- | ------------------------------------- |
| Oracle Cloud | Always Free ARM | 最多 4 OCPU，24GB 内存 | $0          | ARM架构，容量有限/注册异常          |
| Hetzner      | CX22            | 2 vCPU，4GB 内存       | €3.79 (~$4) | 最便宜的付费选项                      |
| DigitalOcean | Basic           | 1 vCPU，1GB 内存       | $6          | 简单界面，良好文档                    |
| Vultr        | Cloud Compute   | 1 vCPU，1GB 内存       | $6          | 多个位置                              |
| Linode       | Nanode          | 1 vCPU，1GB 内存       | $5          | 现已并入 Akamai                       |

**选择提供商：**

- DigitalOcean：最简单的用户体验 + 可预测的设置（本指南）
- Hetzner：良好的性价比（参见 [Hetzner 指南](/platforms/hetzner)）
- Oracle Cloud：可以每月 $0，但更复杂且仅支持 ARM 架构（参见 [Oracle 指南](/platforms/oracle)）

---

## 先决条件

- DigitalOcean 账户（[使用 $200 免费信用额度注册](https://m.do.co/c/signup)）
- SSH 密钥对（或愿意使用密码认证）
- 约 20 分钟时间

## 1) 创建 Droplet

1. 登录 [DigitalOcean](https://cloud.digitalocean.com/)
2. 点击 **创建 → Droplets**
3. 选择：
   - **区域：** 距离您（或您的用户）最近的区域
   - **镜像：** Ubuntu 24.04 LTS
   - **大小：** Basic → Regular → **$6/月**（1 vCPU，1GB 内存，25GB SSD）
   - **认证：** SSH 密钥（推荐）或密码
4. 点击 **创建 Droplet**
5. 记下 IP 地址

## 2) 通过 SSH 连接

```bash
ssh root@YOUR_DROPLET_IP
```

## 3) 安装 OpenClaw

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

## 4) 运行入门向导

```bash
openclaw onboard --install-daemon
```

向导将引导您完成：

- 模型认证（API 密钥或 OAuth）
- 频道设置（Telegram，WhatsApp，Discord 等）
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

网关默认绑定到本地回环。要访问控制 UI：

**选项 A：SSH 隧道（推荐）**

```bash
# From your local machine
ssh -L 18789:localhost:18789 root@YOUR_DROPLET_IP

# Then open: http://localhost:18789
```

**选项 B：Tailscale Serve（HTTPS，仅回环）**

```bash
# On the droplet
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# Configure Gateway to use Tailscale Serve
openclaw config set gateway.tailscale.mode serve
openclaw gateway restart
```

打开：`https://<magicdns>/`

注意事项：

- Serve 保持网关仅限回环，并通过 Tailscale 身份头进行身份验证。
- 如需要求令牌/密码，请设置 `gateway.auth.allowTailscale: false` 或使用 `gateway.auth.mode: "password"`。

**选项 C：Tailnet 绑定（无 Serve）**

```bash
openclaw config set gateway.bind tailnet
openclaw gateway restart
```

打开：`http://<tailscale-ip>:18789`（需要令牌）。

## 7) 连接您的频道

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

其他提供商请参见 [频道](/channels)。

---

## 1GB 内存优化

$6 的 droplet 只有 1GB 内存。为确保运行顺畅：

### 添加交换空间（推荐）

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 使用较轻量级模型

如果遇到内存不足问题，请考虑：

- 使用基于 API 的模型（Claude，GPT）而不是本地模型
- 将 `agents.defaults.model.primary` 设置为较小的模型

### 监控内存

```bash
free -h
htop
```

---

## 持久化

所有状态存储在：

- `~/.openclaw/` — 配置、凭据、会话数据
- `~/.openclaw/workspace/` — 工作区（SOUL.md，内存等）

这些在重启后仍然存在。定期备份：

```bash
tar -czvf openclaw-backup.tar.gz ~/.openclaw ~/.openclaw/workspace
```

---

## Oracle Cloud 免费替代方案

Oracle Cloud 提供 **永久免费** 的 ARM 实例，其性能远超此处任何付费选项——每月 $0。

| 您获得的内容      | 规格                   |
| ----------------- | ---------------------- |
| **4 OCPU**        | ARM Ampere A1          |
| **24GB 内存**     | 完全足够               |
| **200GB 存储**    | 块卷                   |
| **永久免费**      | 不产生信用卡费用       |

**注意事项：**

- 注册可能比较麻烦（失败时重试）
- ARM 架构——大部分功能正常工作，但某些二进制文件需要 ARM 版本

完整设置指南请参见 [Oracle Cloud](/platforms/oracle)。有关注册技巧和故障排除注册过程，请参见此 [社区指南](https://gist.github.com/rssnyder/51e3cfedd730e7dd5f4a816143b25dbd)。

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

- [Hetzner 指南](/platforms/hetzner) — 更便宜，更强大
- [Docker 安装](/install/docker) — 容器化设置
- [Tailscale](/gateway/tailscale) — 安全远程访问
- [配置](/gateway/configuration) — 完整配置参考