---
summary: "OpenClaw on Raspberry Pi (budget self-hosted setup)"
read_when:
  - Setting up OpenClaw on a Raspberry Pi
  - Running OpenClaw on ARM devices
  - Building a cheap always-on personal AI
title: "Raspberry Pi"
---
# 在树莓派上运行OpenClaw

## 目标

在树莓派上运行一个持久的、始终开启的OpenClaw网关，一次性成本约$35-80（无月费）。

适用于：

- 24/7个人AI助手
- 家庭自动化中心
- 低功耗、始终可用的Telegram/WhatsApp机器人

## 硬件需求

| 树莓派型号 | 内存 | 是否支持 | 备注 |
| ----------- | --- | --- | --- |
| **树莓派5** | 4GB/8GB | ✅ 推荐 | 最快，推荐使用 |
| **树莓派4** | 4GB | ✅ 良好 | 大多数用户的最佳选择 |
| **树莓派4** | 2GB | ✅ 可行 | 可使用交换文件 |
| **树莓派4** | 1GB | ⚠️ 紧张 | 可使用交换文件，最小配置 |
| **树莓派3B+** | 1GB | ⚠️ 慢 | 可运行但较慢 |
| **树莓派零2W** | 512MB | ❌ | 不推荐 |

**最低配置：** 1GB内存，1核，500MB磁盘  
**推荐配置：** 2GB+内存，64位操作系统，16GB+ SD卡（或USB SSD）

## 您将需要

- 树莓派4或5（推荐2GB+）
- MicroSD卡（16GB+）或USB SSD（性能更好）
- 电源适配器（推荐官方树莓派电源适配器）
- 网络连接（以太网或WiFi）
- 约30分钟

## 1) 安装操作系统

使用 **Raspberry Pi OS Lite（64位）** —— 无需桌面即可运行无头服务器。

1. 下载[Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. 选择操作系统：**Raspberry Pi OS Lite（64位）**
3. 点击齿轮图标（⚙️）进行预配置：
   - 设置主机名：`gateway-host`
   - 启用SSH
   - 设置用户名/密码
   - 配置WiFi（如不使用以太网）
4. 将系统烧录到您的SD卡/USB驱动器
5. 插入并启动树莓派

## 2) 通过SSH连接

```bash
ssh user@gateway-host
# 或使用IP地址
ssh user@192.168.x.x
```

## 3) 系统设置

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件包
sudo apt install -y git curl build-essential

# 设置时区（对cron/提醒很重要）
sudo timedatectl set-timezone America/Chicago  # 更改为您的时区
```

## 4) 安装Node.js 22（ARM64）

```bash
# 通过NodeSource安装Node.js
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 验证
node --version  # 应显示v22.x.x
npm --version
```

## 5) 添加交换文件（2GB或更少内存时重要）

交换文件可防止内存不足崩溃：

```bash
# 创建2GB交换文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 优化低内存（减少交换文件的活跃度）
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 6) 安装OpenClaw

### 选项A：标准安装（推荐）

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### 选项B：可调试安装（用于调试）

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
npm install
npm run build
npm link
```

可调试安装可直接访问日志和代码——对于调试ARM特定问题非常有用。

## 7) 运行引导

```bash
openclaw onboard --install-daemon
```

按照向导操作：

1. **网关模式：本地**
2. **选择存储位置：本地**
3. **启用远程访问：是**
4. **启用日志：是**
5. **完成**

## 8) 验证安装

```bash
openclaw status
openclaw logs
```

## 9) 访问网关

```bash
ssh -L 8080:localhost:8080 user@gateway-host
```

## 10) 性能优化

```bash
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 11) ARM特定注意事项

```bash
echo 'arm64' | sudo tee -a /etc/issue
```

## 12) 推荐配置

```bash
echo 'arm64' | sudo tee -a /etc/issue
```

## 13) 自动启动

```bash
sudo systemctl enable openclaw
```

## 14) 故障排除

```bash
sudo journalctl -u openclaw
```

## 15) 成本比较

| 配置 | 一次性成本 | 月成本 | 备注 |
| --- | --- | --- | --- |
| **树莓派4（2GB）** | ~$45 | $0 | +电源（~$5/年） |
|