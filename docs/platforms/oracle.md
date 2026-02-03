---
summary: "OpenClaw on Oracle Cloud (Always Free ARM)"
read_when:
  - Setting up OpenClaw on Oracle Cloud
  - Looking for low-cost VPS hosting for OpenClaw
  - Want 24/7 OpenClaw on a small server
title: "Oracle Cloud"
---
# Oracle Cloud（OCI）上的OpenClaw

## 目标

在Oracle Cloud的**Always Free** ARM层级上运行一个持久的OpenClaw网关。

Oracle的免费层级可以是OpenClaw的理想选择（尤其是如果您已有OCI账户），但它也伴随着一些权衡：

- ARM架构（大多数功能正常，但某些二进制文件可能仅限x86）
- 容量和注册可能较为麻烦

## 成本比较（2026）

| 提供商     | 计划            | 规格                  | 价格/月 | 备注                 |
|------------|----------------|-----------------------|---------|----------------------|
| Oracle Cloud | Always Free ARM | 最多4个OCPU，24GB内存 | $0      | ARM，容量有限        |
| Hetzner    | CX22           | 2个vCPU，4GB内存       | ~$4     | 最便宜的付费选项     |
| DigitalOcean | Basic          | 1个vCPU，1GB内存       | $6      | 简单的UI，文档良好   |
| Vultr      | Cloud Compute  | 1个vCPU，1GB内存       | $6      | 多个位置             |
| Linode     | Nanode         | 1个vCPU，1GB内存       | $5      | 现在属于Akamai       |

---

## 先决条件

- Oracle Cloud账户（[注册](https://www.oracle.com/cloud/free/)）——如果遇到问题，请参阅[社区注册指南](https://gist.github.com/rssnyder/51e3cfedd730e7dd5f4a816143b25dbd)
- Tailscale账户（[tailscale.com](https://tailscale.com)免费）
- 约30分钟

## 1) 创建OCI实例

1. 登录[Oracle Cloud控制台](https://cloud.oracle.com/)
2. 导航到**计算 → 实例 → 创建实例**
3. 配置：
   - **名称：** `openclaw`
   - **镜像：** Ubuntu 24.04（aarch64）
   - **形状：** `VM.Standard.A1.Flex`（Ampere ARM）
   - **OCPU：** 2（或最多4个）
   - **内存：** 12GB（或最多24GB）
   - **启动卷：** 50GB（最多200GB免费）
   - **SSH密钥：** 添加您的公钥
4. 点击**创建**
5. 记录公网IP地址

**提示：** 如果实例创建失败并提示“容量不足”，请尝试不同的可用域或稍后再试。免费层级的容量有限。

## 2) 连接并更新

```bash
# 通过公网IP连接
ssh ubuntu@YOUR_PUBLIC_IP

# 更新系统
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential
```

**注意：** `build-essential`是某些依赖项在ARM架构上编译所必需的。

## 3) 配置用户和主机名

```bash
# 设置主机名
sudo hostnamectl set-hostname openclaw

# 为ubuntu用户设置密码
sudo passwd ubuntu

# 启用持续登录（在注销后保持用户服务运行）
sudo loginctl enable-linger ubuntu
```

## 4) 安装Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh --hostname=openclaw
```

这将启用Tailscale SSH，因此您可以从任何设备通过`ssh openclaw`连接到您的tailnet——无需公网IP。

验证：

```bash
tailscale status
```

**从现在起，通过Tailscale连接：** `ssh ubuntu@openclaw`（或使用Tailscale IP）。

## 5) 安装OpenClaw

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
source ~/.bashrc
```

当提示“您想如何孵化您的机器人？”时，选择**“稍后执行”**。

> 注意：如果您遇到ARM原生构建问题，请先尝试系统包（例如`sudo apt install -y build-essential`），然后再使用Homebrew。

## 6) 配置网关（回环 + 令牌认证）并启用Tailscale服务

使用令牌认证作为默认方式。它具有可预测性，并且无需任何“不安全认证”控制UI标志。

```bash
# 在VM上保持网关私有
openclaw config set gateway.listen 127.0.0.1:1234

# 设置令牌认证
openclaw config set auth.type token

# 启用Tailscale服务
openclaw config set tailscale.enable true
```

## 7) 配置网关

```bash
# 设置网关监听地址
openclaw config set gateway.listen 127.0.0.1:1234

# 设置令牌认证
openclaw config set auth.type token

# 启用Tailscale服务
openclab config set tailscale.enable true
```

## 8) 配置安全设置

```bash
# 设置防火墙规则
iptables -A INPUT -s 127.0.0.1 -p tcp --dport 1234 -j ACCEPT
iptables -A INPUT -s 127.0.0.1 -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -s 127.0.0.1 -p tcp --dport 443 -j ACCEPT
```

## 9) 配置日志记录

```bash
# 设置日志记录
openclaw config set log.level debug
```

## 10) 配置监控

```bash
# 设置监控
openclaw config set monitoring.enabled true
```

## 11) 配置备份

```bash
# 设置备份