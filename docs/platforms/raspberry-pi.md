---
summary: "OpenClaw on Raspberry Pi (budget self-hosted setup)"
read_when:
  - Setting up OpenClaw on a Raspberry Pi
  - Running OpenClaw on ARM devices
  - Building a cheap always-on personal AI
title: "Raspberry Pi"
---
# OpenClaw on Raspberry Pi

## 目标

在Raspberry Pi上运行一个持久、始终在线的OpenClaw网关，一次性成本约为**35-80美元**（无月费）。

非常适合：

- 24/7个人AI助手
- 家庭自动化中心
- 低功耗、始终可用的Telegram/WhatsApp机器人

## 硬件要求

| Pi型号        | 内存     | 是否可行   | 备注                              |
| --------------- | ------- | -------- | ---------------------------------- |
| **Pi 5**        | 4GB/8GB | ✅ 最佳  | 最快，推荐               |
| **Pi 4**        | 4GB     | ✅ 良好  | 大多数用户的最佳选择          |
| **Pi 4**        | 2GB     | ✅ 可行    | 可用，需添加交换空间                    |
| **Pi 4**        | 1GB     | ⚠️ 紧凑 | 可能需要交换空间，最小配置 |
| **Pi 3B+**      | 1GB     | ⚠️ 慢  | 可用但反应迟缓                 |
| **Pi Zero 2 W** | 512MB   | ❌       | 不推荐                    |

**最低规格:** 1GB内存，1核，500MB磁盘  
**推荐:** 2GB以上内存，64位操作系统，16GB以上SD卡（或USB SSD）

## 所需物品

- Raspberry Pi 4或5（推荐2GB以上）
- MicroSD卡（16GB以上）或USB SSD（性能更佳）
- 电源（推荐官方Pi电源适配器）
- 网络连接（以太网或WiFi）
- 约30分钟时间

## 1) 刷写操作系统

使用**Raspberry Pi OS Lite (64-bit)** — 对于无头服务器不需要桌面环境。

1. 下载[Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. 选择操作系统: **Raspberry Pi OS Lite (64-bit)**
3. 点击齿轮图标 (⚙️) 进行预配置：
   - 设置主机名: `gateway-host`
   - 启用SSH
   - 设置用户名/密码
   - 配置WiFi（如果不使用以太网）
4. 将其刷写到您的SD卡/USB驱动器
5. 插入并启动Pi

## 2) 通过SSH连接

```bash
ssh user@gateway-host
# or use the IP address
ssh user@192.168.x.x
```

## 3) 系统设置

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git curl build-essential

# Set timezone (important for cron/reminders)
sudo timedatectl set-timezone America/Chicago  # Change to your timezone
```

## 4) 安装Node.js 22 (ARM64)

```bash
# Install Node.js via NodeSource
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version  # Should show v22.x.x
npm --version
```

## 5) 添加Swap（对于2GB或更少内存非常重要）

Swap可以防止内存不足导致的崩溃：

```bash
# Create 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Optimize for low RAM (reduce swappiness)
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 6) 安装OpenClaw

### 选项A：标准安装（推荐）

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### 选项B：可修改安装（适合调试）

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
npm install
npm run build
npm link
```

可修改安装可以让您直接访问日志和代码 —— 有助于调试特定于ARM的问题。

## 7) 运行引导程序

```bash
openclaw onboard --install-daemon
```

按照向导操作：

1. **网关模式:** 本地
2. **认证:** 推荐使用API密钥（OAuth在无头Pi上可能不稳定）
3. **通道:** Telegram是最容易开始的
4. **守护进程:** 是（systemd）

## 8) 验证安装

```bash
# Check status
openclaw status

# Check service
sudo systemctl status openclaw

# View logs
journalctl -u openclaw -f
```

## 9) 访问仪表板

由于Pi是无头的，使用SSH隧道：

```bash
# From your laptop/desktop
ssh -L 18789:localhost:18789 user@gateway-host

# Then open in browser
open http://localhost:18789
```

或者使用Tailscale进行始终在线的访问：

```bash
# On the Pi
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Update config
openclaw config set gateway.bind tailnet
sudo systemctl restart openclaw
```

---

## 性能优化

### 使用USB SSD（大幅改进）

SD卡速度慢且易磨损。USB SSD显著提高性能：

```bash
# Check if booting from USB
lsblk
```

请参阅[Pi USB启动指南](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#usb-mass-storage-boot)进行设置。

### 加速CLI启动（模块编译缓存）

在低功耗Pi主机上，启用Node的模块编译缓存，以便重复运行CLI时更快：

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF' # pragma: allowlist secret
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

注意事项：

- `NODE_COMPILE_CACHE` 加速后续运行 (`status`, `health`, `--help`)。
- `/var/tmp` 比 `/tmp` 更好地经受重启。
- `OPENCLAW_NO_RESPAWN=1` 避免CLI自重生带来的额外启动成本。
- 第一次运行会预热缓存；后续运行受益最多。

### systemd启动调整（可选）

如果这台Pi主要用于运行OpenClaw，添加一个服务drop-in以减少重启抖动并保持启动环境稳定：

```bash
sudo systemctl edit openclaw
```

```ini
[Service]
Environment=OPENCLAW_NO_RESPAWN=1
Environment=NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
Restart=always
RestartSec=2
TimeoutStartSec=90
```

然后应用：

```bash
sudo systemctl daemon-reload
sudo systemctl restart openclaw
```

如果可能，请将OpenClaw状态/缓存保留在SSD支持的存储上，以避免冷启动时SD卡随机I/O瓶颈。

`Restart=` 策略如何帮助自动恢复：
[systemd可以自动恢复服务](https://www.redhat.com/en/blog/systemd-automate-recovery)。

### 减少内存使用

```bash
# Disable GPU memory allocation (headless)
echo 'gpu_mem=16' | sudo tee -a /boot/config.txt

# Disable Bluetooth if not needed
sudo systemctl disable bluetooth
```

### 监控资源

```bash
# Check memory
free -h

# Check CPU temperature
vcgencmd measure_temp

# Live monitoring
htop
```

---

## ARM特定说明

### 二进制兼容性

大多数OpenClaw功能在ARM64上工作良好，但一些外部二进制文件可能需要ARM构建：

| 工具               | ARM64状态 | 备注                               |
| ------------------ | ------------ | ----------------------------------- |
| Node.js            | ✅           | 工作良好                         |
| WhatsApp (Baileys) | ✅           | 纯JS，无问题                  |
| Telegram           | ✅           | 纯JS，无问题                  |
| gog (Gmail CLI)    | ⚠️           | 检查是否有ARM版本               |
| Chromium (浏览器) | ✅           | `sudo apt install chromium-browser` |

如果某个技能失败，请检查其二进制文件是否有ARM构建。许多Go/Rust工具都有；有些则没有。

### 32位与64位

**始终使用64位操作系统。** Node.js和许多现代工具都需要它。检查方法：

```bash
uname -m
# Should show: aarch64 (64-bit) not armv7l (32-bit)
```

---

## 推荐模型设置

由于Pi只是网关（模型在云端运行），请使用基于API的模型：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallbacks": ["openai/gpt-4o-mini"]
      }
    }
  }
}
```

**不要尝试在Pi上运行本地LLM** — 即使是小模型也太慢了。让Claude/GPT来处理繁重的工作。

---

## 开机自动启动

引导程序会设置这一点，但要验证：

```bash
# Check service is enabled
sudo systemctl is-enabled openclaw

# Enable if not
sudo systemctl enable openclaw

# Start on boot
sudo systemctl start openclaw
```

---

## 故障排除

### 内存不足 (OOM)

```bash
# Check memory
free -h

# Add more swap (see Step 5)
# Or reduce services running on the Pi
```

### 性能缓慢

- 使用USB SSD代替SD卡
- 禁用未使用的服务: `sudo systemctl disable cups bluetooth avahi-daemon`
- 检查CPU节流: `vcgencmd get_throttled`（应返回 `0x0`）

### 服务无法启动

```bash
# Check logs
journalctl -u openclaw --no-pager -n 100

# Common fix: rebuild
cd ~/openclaw  # if using hackable install
npm run build
sudo systemctl restart openclaw
```

### ARM二进制文件问题

如果某个技能因“exec format error”失败：

1. 检查该二进制文件是否有ARM64构建
2. 尝试从源代码构建
3. 或者使用支持ARM的Docker容器

### WiFi断开

对于使用WiFi的无头Pi：

```bash
# Disable WiFi power management
sudo iwconfig wlan0 power off

# Make permanent
echo 'wireless-power off' | sudo tee -a /etc/network/interfaces
```

---

## 成本比较

| 设置          | 一次性成本 | 月成本 | 备注                     |
| -------------- | ------------- | ------------ | ------------------------- |
| **Pi 4 (2GB)** | ~$45          | $0           | + 电力 (~$5/年)          |
| **Pi 4 (4GB)** | ~$55          | $0           | 推荐               |
| **Pi 5 (4GB)** | ~$60          | $0           | 最佳性能          |
| **Pi 5 (8GB)** | ~$80          | $0           | 过剩但面向未来 |
| DigitalOcean   | $0            | $6/月        | $72/年                  |
| Hetzner        | $0            | €3.79/月     | ~$50/年                 |

**收支平衡:** 一台Pi大约在6-12个月内就能相对于云VPS回本。

---

## 参考资料

- [Linux指南](/platforms/linux) — 通用Linux设置
- [DigitalOcean指南](/platforms/digitalocean) — 云替代方案
- [Hetzner指南](/install/hetzner) — Docker设置
- [Tailscale](/gateway/tailscale) — 远程访问
- [节点](/nodes) — 将您的笔记本电脑/手机与Pi网关配对