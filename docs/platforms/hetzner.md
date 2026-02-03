---
summary: "Run OpenClaw Gateway 24/7 on a cheap Hetzner VPS (Docker) with durable state and baked-in binaries"
read_when:
  - You want OpenClaw running 24/7 on a cloud VPS (not your laptop)
  - You want a production-grade, always-on Gateway on your own VPS
  - You want full control over persistence, binaries, and restart behavior
  - You are running OpenClaw in Docker on Hetzner or a similar provider
title: "Hetzner"
---
# 在Hetzner上运行OpenClaw（Docker，生产VPS指南）

## 目标

使用Docker在Hetzner VPS上运行一个持久的OpenClaw网关，具备持久化状态、内置二进制文件和安全重启行为。

如果你想获得“每天24小时运行的OpenClaw，花费约5美元”，这是最简单可靠的设置。
Hetzner的定价会变化；选择最小的Debian/Ubuntu VPS，如果遇到内存不足（OOM）问题再升级。

## 我们在做什么（简单说明）？

- 租用一台小型Linux服务器（Hetzner VPS）
- 安装Docker（隔离的应用运行时）
- 在Docker中启动OpenClaw网关
- 在主机上持久化`~/.openclaw` + `~/.openclaw/workspace`（可抵御重启/重建）
- 通过SSH隧道从笔记本电脑访问控制界面

网关可通过以下方式访问：

- 通过SSH端口转发从笔记本电脑访问
- 如果你自行管理防火墙和令牌，可通过直接端口暴露访问

本指南假设使用Hetzner上的Ubuntu或Debian。
如果你使用的是其他Linux VPS，请相应地映射软件包。
关于通用的Docker流程，请参阅[Docker](/install/docker)。

---

## 快速路径（有经验的操作者）

1. 配置Hetzner VPS
2. 安装Docker
3. 克隆OpenClaw仓库
4. 创建持久化主机目录
5. 配置`.env`和`docker-compose.yml`
6. 将所需二进制文件打包进镜像
7. `docker compose up -d`
8. 验证持久化和网关访问

---

## 你需要什么

- 具有root访问权限的Hetzner VPS
- 从笔记本电脑的SSH访问
- 基本的SSH + 复制粘贴操作能力
- 约20分钟
- Docker和Docker Compose
- 模型认证凭证
- 可选的提供商凭证
  - WhatsApp二维码
  - Telegram机器人令牌
  - Gmail OAuth

---

## 1) 配置VPS

在Hetzner上创建一个Ubuntu或Debian VPS。

以root身份连接：

```bash
ssh root@YOUR_VPS_IP
``
```

本指南假设VPS具有持久化状态。
不要将其视为一次性基础设施。

---

## 2) 安装Docker（在VPS上）

```bash
apt-get update
apt-get install -y git curl ca-certificates
curl -fsSL https://get.docker.com | sh
``
```

验证：

```bash
docker --version
docker compose version
``
```

---

## 3) 克隆OpenClaw仓库

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
``
```

本指南假设你将构建自定义镜像以确保二进制文件的持久性。

---

## 4) 创建持久化主机目录

Docker容器是临时的。
所有长期运行的状态必须存储在主机上。

```bash
mkdir -p /root/.openclaw
mkdir -p /root/.openclaw/workspace

# 设置容器用户（uid 1000）的所有权：
chown -R 1000:1000 /root/.openclaw
chown -R 1000:1000 /root/.openclaw/workspace
``
```

---

## 5) 配置环境变量

在仓库根目录创建`.env`文件。

```bash
OPENCLAW_IMAGE=openclaw:latest
OPENCLAW_GATEWAY_TOKEN=change-me-now
OPENCLAW_GATEWAY_BIND=lan
OPENCLAW_GATEWAY_PORT=18789

OPENCLAW_CONFIG_DIR=/root/.openclaw
OPENCLAW_WORKSPACE_DIR=/root/.openclaw/workspace

GOG_KEYRING_PASSWORD=change-me-now
XDG_CONFIG_HOME=/home/node/.openclaw
``
```

生成强密钥：

```bash
openssl rand -hex 32
``
```

**不要提交此文件。**

---

## 6) Docker Compose配置

创建或更新`docker-compose.yml`。

```yaml
services:
  openclaw-gateway:
    image: ${OPENCLAW_IMAGE}
    build: .
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - HOME=/home/node
      - NODE_ENV=production
      - TERM=xterm-256color
      - OPENCLAW_GATEWAY_BIND=${OPENCLAW_GATEWAY_BIND}
      - OPENCLAW_GATEWAY_PORT=${OPENCLAW_GATEWAY_PORT}
      - OPENCLAW_GATEWAY_TOKEN=${OPENCLAW_GATEWAY_TOKEN}
      - GOG_KEYRING_PASSWORD=${GOG_KEYRING_PASSWORD}
    volumes:
      - /root/.openclaw:/root/.openclaw
    ports:
      - "18789:18789"
``
```

---

## 7) 验证持久化和网关访问

```bash
docker compose up -d
``
```

---

## 持久化组件说明

| 组件 | 位置 | 持久化机制 | 说明 |
|------|------|------------|------|
| 网关配置 | `/root/.openclaw` | 主机卷 | 包含`openclaw.json`和令牌 |
| 模型认证配置 | `/root/.openclaw` | 主机卷 | OAuth令牌、API密钥 |
| 技能配置 | `/root/.openclaw/skills/` | 主机卷 | 技能级状态 |
| 代理工作空间 | `/root/.openclaw/workspace/` | 主机卷 | 代码和代理工件 |
| WhatsApp会话 | `/root/.openclaw` | 主机卷 | 保留二维码