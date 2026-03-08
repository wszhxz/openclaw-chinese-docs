---
summary: "Run OpenClaw Gateway 24/7 on a cheap Hetzner VPS (Docker) with durable state and baked-in binaries"
read_when:
  - You want OpenClaw running 24/7 on a cloud VPS (not your laptop)
  - You want a production-grade, always-on Gateway on your own VPS
  - You want full control over persistence, binaries, and restart behavior
  - You are running OpenClaw in Docker on Hetzner or a similar provider
title: "Hetzner"
---
# OpenClaw 部署于 Hetzner (Docker, 生产环境 VPS 指南)

## 目标

在 Hetzner VPS 上使用 Docker 运行持久的 OpenClaw Gateway，具备持久状态、内置二进制文件和安全重启行为。

如果你想要“全天候 OpenClaw，每月约 5 美元”，这是最简单可靠的设置。
Hetzner 价格会有变动；选择最小的 Debian/Ubuntu VPS，如果遇到 OOM 再升级。

安全模型提醒：

- 公司共享代理在所有人都处于同一信任边界且运行时仅用于业务时是可以的。
- 保持严格分离：专用 VPS/运行时 + 专用账户；该主机上没有个人 Apple/Google/浏览器/密码管理器配置文件。
- 如果用户彼此对立，按 gateway/host/OS 用户分割。

参见 [安全性](/gateway/security) 和 [VPS 托管](/vps)。

## 我们在做什么（简单术语）？

- 租用一台小型 Linux 服务器 (Hetzner VPS)
- 安装 Docker (隔离的应用运行时)
- 在 Docker 中启动 OpenClaw Gateway
- 在主机上持久化 `~/.openclaw` + `~/.openclaw/workspace` ( survives 重启/重建)
- 通过 SSH 隧道从笔记本电脑访问控制 UI

Gateway 可通过以下方式访问：

- 来自笔记本电脑的 SSH 端口转发
- 直接端口暴露（如果你自己管理防火墙和令牌）

本指南假设 Hetzner 上使用 Ubuntu 或 Debian。  
如果你在其他 Linux VPS 上，相应映射软件包。
对于通用 Docker 流程，参见 [Docker](/install/docker)。

---

## 快速路径（经验丰富的操作员）

1. 配置 Hetzner VPS
2. 安装 Docker
3. 克隆 OpenClaw 仓库
4. 创建持久化主机目录
5. 配置 `.env` 和 `docker-compose.yml`
6. 将所需的二进制文件内置到镜像中
7. `docker compose up -d`
8. 验证持久化和 Gateway 访问

---

## 你需要什么

- 具有 root 访问权限的 Hetzner VPS
- 来自笔记本电脑的 SSH 访问权限
- 基本熟悉 SSH + 复制/粘贴
- 约 20 分钟
- Docker 和 Docker Compose
- 模型认证凭证
- 可选提供商凭证
  - WhatsApp QR
  - Telegram bot token
  - Gmail OAuth

---

## 1) 配置 VPS

在 Hetzner 中创建 Ubuntu 或 Debian VPS。

以 root 身份连接：

```bash
ssh root@YOUR_VPS_IP
```

本指南假设 VPS 是有状态的。
不要将其视为一次性基础设施。

---

## 2) 安装 Docker（在 VPS 上）

```bash
apt-get update
apt-get install -y git curl ca-certificates
curl -fsSL https://get.docker.com | sh
```

验证：

```bash
docker --version
docker compose version
```

---

## 3) 克隆 OpenClaw 仓库

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
```

本指南假设你将构建自定义镜像以保证二进制文件的持久性。

---

## 4) 创建持久化主机目录

Docker 容器是临时的。
所有长期状态必须存在于主机上。

```bash
mkdir -p /root/.openclaw/workspace

# Set ownership to the container user (uid 1000):
chown -R 1000:1000 /root/.openclaw
```

---

## 5) 配置环境变量

在仓库根目录创建 `.env`。

```bash
OPENCLAW_IMAGE=openclaw:latest
OPENCLAW_GATEWAY_TOKEN=change-me-now
OPENCLAW_GATEWAY_BIND=lan
OPENCLAW_GATEWAY_PORT=18789

OPENCLAW_CONFIG_DIR=/root/.openclaw
OPENCLAW_WORKSPACE_DIR=/root/.openclaw/workspace

GOG_KEYRING_PASSWORD=change-me-now
XDG_CONFIG_HOME=/home/node/.openclaw
```

生成强密钥：

```bash
openssl rand -hex 32
```

**不要提交此文件。**

---

## 6) Docker Compose 配置

创建或更新 `docker-compose.yml`。

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
      - XDG_CONFIG_HOME=${XDG_CONFIG_HOME}
      - PATH=/home/linuxbrew/.linuxbrew/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
    volumes:
      - ${OPENCLAW_CONFIG_DIR}:/home/node/.openclaw
      - ${OPENCLAW_WORKSPACE_DIR}:/home/node/.openclaw/workspace
    ports:
      # Recommended: keep the Gateway loopback-only on the VPS; access via SSH tunnel.
      # To expose it publicly, remove the `127.0.0.1:` prefix and firewall accordingly.
      - "127.0.0.1:${OPENCLAW_GATEWAY_PORT}:18789"
    command:
      [
        "node",
        "dist/index.js",
        "gateway",
        "--bind",
        "${OPENCLAW_GATEWAY_BIND}",
        "--port",
        "${OPENCLAW_GATEWAY_PORT}",
        "--allow-unconfigured",
      ]
```

`--allow-unconfigured` 仅用于引导方便，它不是正确 gateway 配置的替代品。仍需设置 auth (`gateway.auth.token` 或 password) 并使用安全的 bind 设置进行部署。

---

## 7) 将所需的二进制文件内置到镜像中（关键）

在运行中的容器内安装二进制文件是一个陷阱。
任何在运行时安装的内容都会在重启后丢失。

技能所需的所有外部二进制文件必须在镜像构建时安装。

以下示例仅显示三个常见的二进制文件：

- 用于 Gmail 访问的 `gog`
- 用于 Google Places 的 `goplaces`
- 用于 WhatsApp 的 `wacli`

这些是示例，不是完整列表。
你可以使用相同的模式安装任意数量的二进制文件。

如果你稍后添加依赖额外二进制文件的新技能，你必须：

1. 更新 Dockerfile
2. 重建镜像
3. 重启容器

**Dockerfile 示例**

```dockerfile
FROM node:22-bookworm

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

# Example binary 1: Gmail CLI
RUN curl -L https://github.com/steipete/gog/releases/latest/download/gog_Linux_x86_64.tar.gz \
  | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/gog

# Example binary 2: Google Places CLI
RUN curl -L https://github.com/steipete/goplaces/releases/latest/download/goplaces_Linux_x86_64.tar.gz \
  | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/goplaces

# Example binary 3: WhatsApp CLI
RUN curl -L https://github.com/steipete/wacli/releases/latest/download/wacli_Linux_x86_64.tar.gz \
  | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/wacli

# Add more binaries below using the same pattern

WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY ui/package.json ./ui/package.json
COPY scripts ./scripts

RUN corepack enable
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build
RUN pnpm ui:install
RUN pnpm ui:build

ENV NODE_ENV=production

CMD ["node","dist/index.js"]
```

---

## 8) 构建并启动

```bash
docker compose build
docker compose up -d openclaw-gateway
```

验证二进制文件：

```bash
docker compose exec openclaw-gateway which gog
docker compose exec openclaw-gateway which goplaces
docker compose exec openclaw-gateway which wacli
```

预期输出：

```
/usr/local/bin/gog
/usr/local/bin/goplaces
/usr/local/bin/wacli
```

---

## 9) 验证 Gateway

```bash
docker compose logs -f openclaw-gateway
```

成功：

```
[gateway] listening on ws://0.0.0.0:18789
```

从你的笔记本电脑：

```bash
ssh -N -L 18789:127.0.0.1:18789 root@YOUR_VPS_IP
```

打开：

`http://127.0.0.1:18789/`

粘贴你的 gateway token。

---

## 持久化内容位置（真实来源）

OpenClaw 运行在 Docker 中，但 Docker 不是真实来源。
所有长期状态必须在重启、重建和 reboot 后存活。

| 组件                | 位置                              | 持久化机制             | 备注                             |
| ------------------- | --------------------------------- | ---------------------- | -------------------------------- |
| Gateway 配置        | `/home/node/.openclaw/`           | 主机卷挂载      | 包括 `openclaw.json`, tokens |
| 模型认证配置文件    | `/home/node/.openclaw/`           | 主机卷挂载      | OAuth tokens, API keys           |
| 技能配置            | `/home/node/.openclaw/skills/`    | 主机卷挂载      | 技能级状态                |
| Agent 工作区        | `/home/node/.openclaw/workspace/` | 主机卷挂载      | 代码和 agent 工件         |
| WhatsApp 会话       | `/home/node/.openclaw/`           | 主机卷挂载      | 保留 QR 登录               |
| Gmail keyring       | `/home/node/.openclaw/`           | 主机卷 + 密码 | 需要 `GOG_KEYRING_PASSWORD`  |
| 外部二进制文件      | `/usr/local/bin/`                 | Docker 镜像           | 必须在构建时内置      |
| Node 运行时         | 容器文件系统              | Docker 镜像           | 每次镜像构建时重建        |
| OS 软件包           | 容器文件系统              | Docker 镜像           | 不要在运行时安装        |
| Docker 容器         | 临时                         | 可重启            | 可安全销毁                  |

---

## 基础设施即代码 (Terraform)

对于偏好 infrastructure-as-code 工作流的团队，社区维护的 Terraform 设置提供：

- 模块化 Terraform 配置，具有远程状态管理
- 通过 cloud-init 自动配置
- 部署脚本 (bootstrap, deploy, backup/restore)
- 安全加固 (firewall, UFW, 仅 SSH 访问)
- 用于 gateway 访问的 SSH 隧道配置

**仓库：**

- 基础设施：[openclaw-terraform-hetzner](https://github.com/andreesg/openclaw-terraform-hetzner)
- Docker 配置：[openclaw-docker-config](https://github.com/andreesg/openclaw-docker-config)

此方法补充了上面的 Docker 设置，具有可重复的部署、版本控制的基础设施和自动灾难恢复。

> **注意：** 社区维护。对于问题或贡献，参见上面的仓库链接。