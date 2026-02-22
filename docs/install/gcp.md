---
summary: "Run OpenClaw Gateway 24/7 on a GCP Compute Engine VM (Docker) with durable state"
read_when:
  - You want OpenClaw running 24/7 on GCP
  - You want a production-grade, always-on Gateway on your own VM
  - You want full control over persistence, binaries, and restart behavior
title: "GCP"
---
# OpenClaw on GCP Compute Engine (Docker, Production VPS Guide)

## 目标

使用 Docker 在 GCP Compute Engine 虚拟机上运行一个持久化的 OpenClaw Gateway，具有持久状态、内置二进制文件和安全的重启行为。

如果您想要“全天候 OpenClaw 约 $5-12/月”，这是在 Google Cloud 上的一个可靠设置。
定价因机器类型和地区而异；选择适合您工作负载的最小 VM，并在遇到内存不足时进行扩展。

## 我们要做什么（简单说明）？

- 创建一个 GCP 项目并启用计费
- 创建一个 Compute Engine 虚拟机
- 安装 Docker（隔离的应用程序运行时）
- 在 Docker 中启动 OpenClaw Gateway
- 在主机上持久化 `~/.openclaw` + `~/.openclaw/workspace`（重启/重建后仍然存在）
- 通过 SSH 隧道从笔记本电脑访问控制 UI

Gateway 可以通过以下方式访问：

- 从笔记本电脑进行 SSH 端口转发
- 如果您自行管理防火墙和令牌，则直接端口暴露

本指南使用 GCP Compute Engine 上的 Debian。
Ubuntu 也可以使用；相应地映射包。
有关通用 Docker 流，请参阅 [Docker](/install/docker)。

---

## 快速路径（有经验的操作员）

1. 创建 GCP 项目 + 启用 Compute Engine API
2. 创建 Compute Engine 虚拟机（e2-small，Debian 12，20GB）
3. 通过 SSH 登录到虚拟机
4. 安装 Docker
5. 克隆 OpenClaw 仓库
6. 创建持久化主机目录
7. 配置 `.env` 和 `docker-compose.yml`
8. 构建所需的二进制文件，构建并启动

---

## 您需要什么

- GCP 账户（e2-micro 符合免费层级）
- 已安装的 gcloud CLI（或使用 Cloud 控制台）
- 笔记本电脑上的 SSH 访问权限
- 基本的 SSH + 复制/粘贴舒适度
- 大约 20-30 分钟
- Docker 和 Docker Compose
- 模型认证凭据
- 可选提供商凭据
  - WhatsApp QR
  - Telegram 机器人令牌
  - Gmail OAuth

---

## 1) 安装 gcloud CLI（或使用控制台）

**选项 A: gcloud CLI**（推荐用于自动化）

从 [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install) 安装

初始化并进行身份验证：

```bash
gcloud init
gcloud auth login
```

**选项 B: Cloud 控制台**

所有步骤都可以通过 [https://console.cloud.google.com](https://console.cloud.google.com) 的 Web 界面完成

---

## 2) 创建 GCP 项目

**CLI:**

```bash
gcloud projects create my-openclaw-project --name="OpenClaw Gateway"
gcloud config set project my-openclaw-project
```

在 [https://console.cloud.google.com/billing](https://console.cloud.google.com/billing) 启用计费（Compute Engine 所需）。

启用 Compute Engine API：

```bash
gcloud services enable compute.googleapis.com
```

**控制台:**

1. 进入 IAM & 管理 > 创建项目
2. 命名并创建
3. 为项目启用计费
4. 导航到 API & 服务 > 启用 API > 搜索“Compute Engine API” > 启用

---

## 3) 创建虚拟机

**机器类型:**

| 类型     | 规格                    | 成本               | 备注              |
| -------- | ------------------------ | ------------------ | ------------------ |
| e2-small | 2 vCPU, 2GB RAM          | ~$12/月            | 推荐        |
| e2-micro | 2 vCPU (共享), 1GB RAM | 免费层适用 | 在负载下可能会内存不足 |

**CLI:**

```bash
gcloud compute instances create openclaw-gateway \
  --zone=us-central1-a \
  --machine-type=e2-small \
  --boot-disk-size=20GB \
  --image-family=debian-12 \
  --image-project=debian-cloud
```

**控制台:**

1. 转到 计算引擎 > 虚拟机实例 > 创建实例
2. 名称: `openclaw-gateway`
3. 区域: `us-central1`, 区域: `us-central1-a`
4. 机器类型: `e2-small`
5. 启动磁盘: Debian 12, 20GB
6. 创建

---

## 4) 通过 SSH 连接到 VM

**CLI:**

```bash
gcloud compute ssh openclaw-gateway --zone=us-central1-a
```

**控制台:**

点击 计算引擎 仪表板中您 VM 旁边的 "SSH" 按钮。

注意: SSH 密钥传播在 VM 创建后可能需要 1-2 分钟。如果连接被拒绝，请等待并重试。

---

## 5) 安装 Docker (在 VM 上)

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

注销并重新登录以使组更改生效:

```bash
exit
```

然后再次通过 SSH 连接:

```bash
gcloud compute ssh openclaw-gateway --zone=us-central1-a
```

验证:

```bash
docker --version
docker compose version
```

---

## 6) 克隆 OpenClaw 仓库

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
```

本指南假设您将构建自定义镜像以保证二进制持久性。

---

## 7) 创建持久主机目录

Docker 容器是临时的。
所有长期状态必须存在于主机上。

```bash
mkdir -p ~/.openclaw
mkdir -p ~/.openclaw/workspace
```

---

## 8) 配置环境变量

在仓库根目录下创建 `.env`。

```bash
OPENCLAW_IMAGE=openclaw:latest
OPENCLAW_GATEWAY_TOKEN=change-me-now
OPENCLAW_GATEWAY_BIND=lan
OPENCLAW_GATEWAY_PORT=18789

OPENCLAW_CONFIG_DIR=/home/$USER/.openclaw
OPENCLAW_WORKSPACE_DIR=/home/$USER/.openclaw/workspace

GOG_KEYRING_PASSWORD=change-me-now
XDG_CONFIG_HOME=/home/node/.openclaw
```

生成强密钥:

```bash
openssl rand -hex 32
```

**不要提交此文件。**

---

## 9) Docker Compose 配置

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
      # Recommended: keep the Gateway loopback-only on the VM; access via SSH tunnel.
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
      ]
```

---

## 10) 将所需的二进制文件烘焙到镜像中（关键）

在运行中的容器内安装二进制文件是一个陷阱。
在运行时安装的任何内容在重启后都会丢失。

所有技能所需的所有外部二进制文件必须在镜像构建时安装。

下面的示例显示了仅三个常见的二进制文件：

- `gog` 用于访问Gmail
- `goplaces` 用于Google Places
- `wacli` 用于WhatsApp

这些是示例，并非完整列表。
您可以使用相同的模式安装所需的任意数量的二进制文件。

如果您以后添加了依赖于其他二进制文件的新技能，您必须：

1. 更新Dockerfile
2. 重新构建镜像
3. 重启容器

**示例Dockerfile**

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

## 11) 构建并启动

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

## 12) 验证网关

```bash
docker compose logs -f openclaw-gateway
```

成功：

```
[gateway] listening on ws://0.0.0.0:18789
```

---

## 13) 从您的笔记本电脑访问

创建一个SSH隧道以转发网关端口：

```bash
gcloud compute ssh openclaw-gateway --zone=us-central1-a -- -L 18789:127.0.0.1:18789
```

在浏览器中打开：

`http://127.0.0.1:18789/`

粘贴您的网关令牌。

---

## 数据持久化位置（真相来源）

OpenClaw运行在Docker中，但Docker不是真相来源。
所有长期状态必须能够经受重启、重建和重新启动。

| 组件           | 位置                          | 持久化机制  | 备注                            |
| ------------------- | --------------------------------- | ---------------------- | -------------------------------- |
| 网关配置      | `/home/node/.openclaw/`           | 主机卷挂载      | 包括`openclaw.json`，令牌 |
| 模型认证配置文件 | `/home/node/.openclaw/`           | 主机卷挂载      | OAuth令牌，API密钥           |
| 技能配置       | `/home/node/.openclaw/skills/`    | 主机卷挂载      | 技能级别状态                |
| 代理工作区     | `/home/node/.openclaw/workspace/` | 主机卷挂载      | 代码和代理工件         |
| WhatsApp会话    | `/home/node/.openclaw/`           | 主机卷挂载      | 保留QR登录               |
| Gmail密钥环       | `/home/node/.openclaw/`           | 主机卷 + 密码 | 需要`GOG_KEYRING_PASSWORD`  |
| 外部二进制文件   | `/usr/local/bin/`                 | Docker镜像           | 必须在构建时烘焙      |
| Node运行时        | 容器文件系统              | Docker镜像           | 每次镜像构建时重建        |
| 操作系统包         | 容器文件系统              | Docker镜像           | 不要在运行时安装        |
| Docker容器    | 临时                         | 可重启            | 可安全销毁                  |

---

## 更新

要更新VM上的OpenClaw：

```bash
cd ~/openclaw
git pull
docker compose build
docker compose up -d
```

---

## 故障排除

**SSH连接被拒绝**

SSH密钥传播可能在VM创建后需要1-2分钟。等待并重试。

**OS登录问题**

检查您的OS登录配置文件：

```bash
gcloud compute os-login describe-profile
```

确保您的账户具有所需的IAM权限（Compute OS Login或Compute OS Admin Login）。

**内存不足（OOM）**

如果使用e2-micro并遇到OOM，请升级到e2-small或e2-medium：

```bash
# Stop the VM first
gcloud compute instances stop openclaw-gateway --zone=us-central1-a

# Change machine type
gcloud compute instances set-machine-type openclaw-gateway \
  --zone=us-central1-a \
  --machine-type=e2-small

# Start the VM
gcloud compute instances start openclaw-gateway --zone=us-central1-a
```

---

## 服务账户（安全最佳实践）

对于个人使用，默认用户账户已经足够。

对于自动化或CI/CD管道，请创建一个具有最小权限的专用服务账户：

1. 创建服务账户：

   ```bash
   gcloud iam service-accounts create openclaw-deploy \
     --display-name="OpenClaw Deployment"
   ```

2. 授予Compute Instance Admin角色（或更窄的自定义角色）：

   ```bash
   gcloud projects add-iam-policy-binding my-openclaw-project \
     --member="serviceAccount:openclaw-deploy@my-openclaw-project.iam.gserviceaccount.com" \
     --role="roles/compute.instanceAdmin.v1"
   ```

避免在自动化中使用Owner角色。遵循最小权限原则。

有关IAM角色的详细信息，请参阅[https://cloud.google.com/iam/docs/understanding-roles](https://cloud.google.com/iam/docs/understanding-roles)。

---

## 下一步操作

- 设置消息通道：[Channels](/channels)
- 将本地设备配对为节点：[Nodes](/nodes)
- 配置网关：[Gateway configuration](/gateway/configuration)