---
summary: "Run OpenClaw Gateway 24/7 on a cheap Hetzner VPS (Docker) with durable state and baked-in binaries"
read_when:
  - You want OpenClaw running 24/7 on a cloud VPS (not your laptop)
  - You want a production-grade, always-on Gateway on your own VPS
  - You want full control over persistence, binaries, and restart behavior
  - You are running OpenClaw in Docker on Hetzner or a similar provider
title: "Hetzner"
---
# 在 Hetzner 上运行 OpenClaw（Docker，生产环境 VPS 指南）

## 目标

在 Hetzner VPS 上使用 Docker 持久化运行 OpenClaw 网关，确保状态持久、二进制文件内建、重启行为安全。

如果你希望“以约 $5 的成本实现 OpenClaw 24/7 运行”，这是最简单可靠的部署方案。  
Hetzner 定价可能变动；请选择最小规格的 Debian/Ubuntu VPS，若出现内存不足（OOM），再逐步升级。

安全模型提醒：

- 当所有用户处于同一信任边界且运行时环境仅用于业务用途时，公司共享的智能体是可接受的。
- 请严格隔离：专用 VPS/运行时 + 专用账户；该主机上不得登录任何个人 Apple/Google/浏览器/密码管理器账户。
- 若用户之间存在对抗关系，请按网关/主机/操作系统用户进行拆分。

参见 [安全性](/gateway/security) 和 [VPS 托管](/vps)。

## 我们要做什么（通俗解释）？

- 租用一台小型 Linux 服务器（Hetzner VPS）
- 安装 Docker（隔离的应用运行时）
- 在 Docker 中启动 OpenClaw 网关
- 将 `~/.openclaw` + `~/.openclaw/workspace` 持久化保存至宿主机（可抵御重启/重建）
- 通过 SSH 隧道从你的笔记本电脑访问控制界面（Control UI）

网关可通过以下方式访问：

- 从你的笔记本电脑通过 SSH 端口转发访问
- 若你自行管理防火墙规则与令牌，也可直接暴露端口

本指南假设 Hetzner 上运行的是 Ubuntu 或 Debian。  
若你使用其他 Linux VPS，请相应映射软件包。  
通用 Docker 流程请参阅 [Docker](/install/docker)。

---

## 快速路径（有经验的运维人员）

1. 创建 Hetzner VPS  
2. 安装 Docker  
3. 克隆 OpenClaw 仓库  
4. 创建持久化的宿主机目录  
5. 配置 `.env` 和 `docker-compose.yml`  
6. 将所需二进制文件构建进镜像  
7. `docker compose up -d`  
8. 验证持久化机制及网关访问能力  

---

## 你需要准备什么

- 具备 root 权限的 Hetzner VPS  
- 从你的笔记本电脑可 SSH 访问该 VPS  
- 基本的 SSH 操作与复制粘贴能力  
- 约 20 分钟时间  
- Docker 和 Docker Compose  
- 模型认证凭据  
- 可选的第三方服务凭据  
  - WhatsApp 二维码（QR）  
  - Telegram 机器人令牌（bot token）  
  - Gmail OAuth 凭据  

---

## 1）创建 VPS

在 Hetzner 上创建一台 Ubuntu 或 Debian VPS。

以 root 用户身份连接：

```bash
ssh root@YOUR_VPS_IP
```

本指南假设该 VPS 是有状态的。  
请勿将其视为可随时丢弃的基础设施。

---

## 2）在 VPS 上安装 Docker

```bash
apt-get update
apt-get install -y git curl ca-certificates
curl -fsSL https://get.docker.com | sh
```

验证安装：

```bash
docker --version
docker compose version
```

---

## 3）克隆 OpenClaw 仓库

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
```

本指南假设你将构建自定义镜像，以确保二进制文件持久化。

---

## 4）创建持久化的宿主机目录

Docker 容器本身是临时性的。  
所有长期存在的状态必须保存在宿主机上。

```bash
mkdir -p /root/.openclaw/workspace

# Set ownership to the container user (uid 1000):
chown -R 1000:1000 /root/.openclaw
```

---

## 5）配置环境变量

在仓库根目录下创建 `.env` 文件。

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

**切勿提交此文件。**

---

## 6）Docker Compose 配置

创建或更新 `docker-compose.yml` 文件。

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

`--allow-unconfigured` 仅为初始化提供便利，不能替代正式的网关配置。仍需设置认证（`gateway.auth.token` 或密码），并为你的部署使用安全的 bind 设置。

---

## 7）将必需的二进制文件构建进镜像（关键步骤）

在正在运行的容器中安装二进制文件是一种陷阱。  
任何在运行时安装的内容都会在容器重启后丢失。

所有技能所依赖的外部二进制文件，必须在构建镜像阶段完成安装。

下方示例仅展示三种常见二进制文件：

- `gog`：用于访问 Gmail  
- `goplaces`：用于 Google Places  
- `wacli`：用于 WhatsApp  

这些仅为示例，并非完整列表。  
你可以按相同模式安装任意数量所需的二进制文件。

若后续新增依赖额外二进制文件的技能，则必须：

1. 更新 Dockerfile  
2. 重新构建镜像  
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

## 8）构建并启动

```bash
docker compose build
docker compose up -d openclaw-gateway
```

验证二进制文件是否就绪：

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

## 9）验证网关

```bash
docker compose logs -f openclaw-gateway
```

成功响应示例：

```
[gateway] listening on ws://0.0.0.0:18789
```

在你的笔记本电脑上执行：

```bash
ssh -N -L 18789:127.0.0.1:18789 root@YOUR_VPS_IP
```

打开：

`http://127.0.0.1:18789/`

粘贴你的网关令牌。

---

## 各组件持久化位置（唯一可信源）

OpenClaw 运行于 Docker 中，但 Docker 并非唯一可信源。  
所有长期存在的状态都必须能经受重启、重建和系统重启。

| 组件             | 位置                          | 持久化机制         | 说明                            |
| ---------------- | ----------------------------- | ------------------ | ------------------------------- |
| 网关配置         | `/home/node/.openclaw/`       | 宿主机卷挂载       | 包含 `openclaw.json`、令牌等   |
| 模型认证配置文件 | `/home/node/.openclaw/`       | 宿主机卷挂载       | OAuth 令牌、API 密钥            |
| 技能配置         | `/home/node/.openclaw/skills/`    | 宿主机卷挂载       | 技能级状态                      |
| 智能体工作区     | `/home/node/.openclaw/workspace/` | 宿主机卷挂载       | 代码与智能体产物                |
| WhatsApp 会话    | `/home/node/.openclaw/`       | 宿主机卷挂载       | 保留二维码登录状态              |
| Gmail 密钥环     | `/home/node/.openclaw/`       | 宿主机卷 + 密码    | 需要 `GOG_KEYRING_PASSWORD`          |
| 外部二进制文件   | `/usr/local/bin/`             | Docker 镜像        | 必须在构建镜像时内建            |
| Node 运行时      | 容器文件系统                  | Docker 镜像        | 每次构建镜像时都会重建          |
| 操作系统软件包   | 容器文件系统                  | Docker 镜像        | 切勿在运行时安装                |
| Docker 容器      | 临时性                        | 可重启             | 可安全销毁                      |

---

## 基础设施即代码（Terraform）

对于偏好基础设施即代码（IaC）工作流的团队，社区维护的 Terraform 方案提供以下能力：

- 模块化 Terraform 配置，支持远程状态管理  
- 通过 cloud-init 自动化部署  
- 部署脚本（初始化、部署、备份/恢复）  
- 安全加固（防火墙、UFW、仅允许 SSH 访问）  
- 用于网关访问的 SSH 隧道配置  

**相关仓库：**

- 基础设施：[openclaw-terraform-hetzner](https://github.com/andreesg/openclaw-terraform-hetzner)  
- Docker 配置：[openclaw-docker-config](https://github.com/andreesg/openclaw-docker-config)  

该方案是对上述 Docker 部署的有力补充，可实现可复现的部署、版本可控的基础设施以及自动化的灾难恢复。

> **注意：** 此为社区维护项目。如遇问题或有意贡献，请参考上方仓库链接。