---
summary: "Run OpenClaw Gateway 24/7 on a GCP Compute Engine VM (Docker) with durable state"
read_when:
  - You want OpenClaw running 24/7 on GCP
  - You want a production-grade, always-on Gateway on your own VM
  - You want full control over persistence, binaries, and restart behavior
title: "GCP"
---
# 在 GCP Compute Engine 上运行 OpenClaw（Docker，生产级 VPS 指南）

## 目标

在 GCP Compute Engine 虚拟机上使用 Docker 持久化运行 OpenClaw 网关，确保状态持久化、二进制文件内置于镜像中，并具备安全的重启行为。

如果你希望以每月约 $5–12 的成本实现 OpenClaw 24/7 全天候运行，那么 Google Cloud 是一个可靠的平台。  
具体费用因机器类型和区域而异；请选择能满足你工作负载的最小规格虚拟机，若遇到内存不足（OOM）问题，再逐步升级。

## 我们在做什么（通俗解释）？

- 创建一个 GCP 项目并启用计费功能  
- 创建一台 Compute Engine 虚拟机  
- 安装 Docker（用于隔离应用运行时环境）  
- 在 Docker 中启动 OpenClaw 网关  
- 将 `~/.openclaw` 和 `~/.openclaw/workspace` 持久化保存至宿主机（可抵御重启或重建）  
- 通过 SSH 隧道从你的笔记本电脑访问控制界面（Control UI）

网关可通过以下方式访问：

- 从你的笔记本电脑进行 SSH 端口转发  
- 若你自行管理防火墙规则与访问令牌，则可直接暴露端口  

本指南基于 GCP Compute Engine 上的 Debian 系统。  
Ubuntu 同样适用；请根据系统对应调整软件包名称。  
如需通用 Docker 流程，请参阅 [Docker](/install/docker)。

---

## 快速路径（面向有经验的运维人员）

1. 创建 GCP 项目并启用 Compute Engine API  
2. 创建 Compute Engine 虚拟机（e2-small，Debian 12，20GB）  
3. 通过 SSH 登录该虚拟机  
4. 安装 Docker  
5. 克隆 OpenClaw 代码仓库  
6. 创建持久化的宿主机目录  
7. 配置 `.env` 和 `docker-compose.yml`  
8. 内置所需二进制文件、构建镜像并启动服务  

---

## 所需前提条件

- GCP 账户（e2-micro 可享受免费额度）  
- 已安装 gcloud CLI（或使用 Cloud Console）  
- 你的笔记本电脑具备 SSH 访问能力  
- 对 SSH 与复制粘贴操作具备基本熟练度  
- 约 20–30 分钟时间  
- Docker 与 Docker Compose  
- 模型认证凭据（Model auth credentials）  
- 可选的第三方服务凭据  
  - WhatsApp QR 码  
  - Telegram bot token  
  - Gmail OAuth 凭据  

---

## 1) 安装 gcloud CLI（或使用 Cloud Console）

**选项 A：gcloud CLI**（推荐用于自动化部署）

从 [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install) 下载安装

初始化并完成身份验证：

```bash
gcloud init
gcloud auth login
```

**选项 B：Cloud Console**

所有步骤均可通过网页界面完成：[https://console.cloud.google.com](https://console.cloud.google.com)

---

## 2) 创建 GCP 项目

**命令行方式（CLI）：**

```bash
gcloud projects create my-openclaw-project --name="OpenClaw Gateway"
gcloud config set project my-openclaw-project
```

前往 [https://console.cloud.google.com/billing](https://console.cloud.google.com/billing) 启用计费功能（Compute Engine 必须启用计费）。

启用 Compute Engine API：

```bash
gcloud services enable compute.googleapis.com
```

**网页控制台方式（Console）：**

1. 进入 IAM 与管理 > 创建项目  
2. 输入项目名称并创建  
3. 为该项目启用计费功能  
4. 进入 API 和服务 > 启用 API > 搜索 “Compute Engine API” > 启用  

---

## 3) 创建虚拟机（VM）

**机器类型说明：**

| 类型       | 规格                     | 月费用     | 说明                                         |
| ------------ | ------------------------ | ------------ | -------------------------------------------- |
| e2-medium    | 2 vCPU，4GB RAM          | ~$25/月      | 本地 Docker 构建最稳定的选择                 |
| e2-small     | 2 vCPU，2GB RAM          | ~$12/月      | Docker 构建的最低推荐配置                    |
| e2-micro     | 2 vCPU（共享），1GB RAM  | 符合免费额度 | Docker 构建常因内存不足失败（退出码 137）   |

**命令行方式（CLI）：**

```bash
gcloud compute instances create openclaw-gateway \
  --zone=us-central1-a \
  --machine-type=e2-small \
  --boot-disk-size=20GB \
  --image-family=debian-12 \
  --image-project=debian-cloud
```

**网页控制台方式（Console）：**

1. 进入 Compute Engine > 虚拟机实例 > 创建实例  
2. 名称：`openclaw-gateway`  
3. 区域：`us-central1`，可用区：`us-central1-a`  
4. 机器类型：`e2-small`  
5. 启动磁盘：Debian 12，20GB  
6. 创建  

---

## 4) 通过 SSH 登录虚拟机

**命令行方式（CLI）：**

```bash
gcloud compute ssh openclaw-gateway --zone=us-central1-a
```

**网页控制台方式（Console）：**

在 Compute Engine 控制台中，点击你所创建虚拟机旁的 “SSH” 按钮。

注意：虚拟机创建后，SSH 密钥传播可能需要 1–2 分钟。若连接被拒绝，请稍等片刻后重试。

---

## 5) 在虚拟机上安装 Docker

```bash
sudo apt-get update
sudo apt-get install -y git curl ca-certificates
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

为使用户组变更生效，请登出并重新登录：

```bash
exit
```

然后再次通过 SSH 登录：

```bash
gcloud compute ssh openclaw-gateway --zone=us-central1-a
```

验证安装是否成功：

```bash
docker --version
docker compose version
```

---

## 6) 克隆 OpenClaw 代码仓库

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
```

本指南假设你将构建自定义镜像，以确保二进制文件持久化。

---

## 7) 创建持久化的宿主机目录

Docker 容器本身是临时性的。  
所有长期存在的状态数据必须保存在宿主机上。

```bash
mkdir -p ~/.openclaw
mkdir -p ~/.openclaw/workspace
```

---

## 8) 配置环境变量

在代码仓库根目录下创建 `.env` 文件。

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

生成高强度密钥：

```bash
openssl rand -hex 32
```

**切勿提交该文件。**

---

## 9) Docker Compose 配置

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

## 10) 将必需的二进制文件内置到镜像中（关键步骤）

在正在运行的容器中安装二进制文件是一种陷阱。  
任何在运行时安装的内容都会在容器重启后丢失。

所有技能（skills）所依赖的外部二进制文件，都必须在构建镜像阶段完成安装。

以下示例仅列出三种常见二进制文件：

- `gog`：用于访问 Gmail  
- `goplaces`：用于调用 Google Places  
- `wacli`：用于 WhatsApp  

这些仅为示例，非完整列表。  
你可以按相同模式安装任意数量所需的二进制文件。

若后续新增依赖其他二进制文件的技能，则必须：

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

## 11) 构建并启动服务

```bash
docker compose build
docker compose up -d openclaw-gateway
```

若构建过程中在 `pnpm install --frozen-lockfile` 阶段出现 `Killed` / `exit code 137` 错误，表明虚拟机内存不足。请至少使用 `e2-small` 规格，或选用 `e2-medium` 以获得更可靠的首次构建体验。

当绑定到局域网（LAN）接口（`OPENCLAW_GATEWAY_BIND=lan`）时，请先配置可信浏览器来源（trusted browser origin），再继续操作：

```bash
docker compose run --rm openclaw-cli config set gateway.controlUi.allowedOrigins '["http://127.0.0.1:18789"]' --strict-json
```

若你修改了网关端口，请将 `18789` 替换为你实际配置的端口号。

验证二进制文件是否就绪：

```bash
docker compose exec openclaw-gateway which gog
docker compose exec openclaw-gateway which goplaces
docker compose exec openclaw-gateway which wacli
```

预期输出如下：

```
/usr/local/bin/gog
/usr/local/bin/goplaces
/usr/local/bin/wacli
```

---

## 12) 验证网关运行状态

```bash
docker compose logs -f openclaw-gateway
```

成功标志：

```
[gateway] listening on ws://0.0.0.0:18789
```

---

## 13) 从你的笔记本电脑访问网关

创建 SSH 隧道以转发网关端口：

```bash
gcloud compute ssh openclaw-gateway --zone=us-central1-a -- -L 18789:127.0.0.1:18789
```

在浏览器中打开：

`http://127.0.0.1:18789/`

获取一个带新令牌的控制台链接：

```bash
docker compose run --rm openclaw-cli dashboard --no-open
```

将该 URL 中的令牌粘贴至控制界面。

若控制界面显示 `unauthorized` 或 `disconnected (1008): pairing required`，请批准当前浏览器设备：

```bash
docker compose run --rm openclaw-cli devices list
docker compose run --rm openclaw-cli devices approve <requestId>
```

---

## 数据持久化位置（数据源真相）

OpenClaw 在 Docker 中运行，但 Docker 并非数据的唯一真实来源。  
所有长期存在的状态都必须能够经受住重启、镜像重建和系统重启。

| 组件               | 位置                              | 持久化机制           | 说明                             |
| ------------------ | --------------------------------- | -------------------- | -------------------------------- |
| 网关配置           | `/home/node/.openclaw/`           | 主机卷挂载           | 包含 `openclaw.json`、令牌     |
| 模型认证配置文件   | `/home/node/.openclaw/`           | 主机卷挂载           | OAuth 令牌、API 密钥             |
| 技能配置           | `/home/node/.openclaw/skills/`    | 主机卷挂载           | 技能级状态                       |
| 智能体工作区       | `/home/node/.openclaw/workspace/` | 主机卷挂载           | 代码与智能体制品                 |
| WhatsApp 会话      | `/home/node/.openclaw/`           | 主机卷挂载           | 保留二维码登录状态               |
| Gmail 密钥环       | `/home/node/.openclaw/`           | 主机卷 + 密码         | 需要 `GOG_KEYRING_PASSWORD`          |
| 外部二进制文件     | `/usr/local/bin/`                 | Docker 镜像           | 必须在构建时嵌入                 |
| Node 运行时        | 容器文件系统                      | Docker 镜像           | 每次构建镜像时都会重建           |
| 操作系统软件包     | 容器文件系统                      | Docker 镜像           | 不得在运行时安装                 |
| Docker 容器        | 临时性                            | 可重启               | 可安全销毁                       |

---

## 更新

在虚拟机上更新 OpenClaw：

```bash
cd ~/openclaw
git pull
docker compose build
docker compose up -d
```

---

## 故障排查

**SSH 连接被拒绝**

虚拟机创建后，SSH 密钥传播可能需要 1–2 分钟。请稍候并重试。

**操作系统登录问题**

检查您的操作系统登录配置文件：

```bash
gcloud compute os-login describe-profile
```

确保您的账号拥有必需的 IAM 权限（Compute OS Login 或 Compute OS Admin Login）。

**内存不足（OOM）**

如果 Docker 构建因 `Killed` 和 `exit code 137` 失败，则表明虚拟机已被 OOM 终止。请升级至 e2-small（最低要求）或 e2-medium（推荐用于可靠的本地构建）：

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

## 服务账号（安全最佳实践）

对于个人使用，您的默认用户账号即可正常工作。

对于自动化任务或 CI/CD 流水线，请创建一个具有最小必要权限的专用服务账号：

1. 创建服务账号：

   ```bash
   gcloud iam service-accounts create openclaw-deploy \
     --display-name="OpenClaw Deployment"
   ```

2. 授予 Compute Instance Admin 角色（或更精细的自定义角色）：

   ```bash
   gcloud projects add-iam-policy-binding my-openclaw-project \
     --member="serviceAccount:openclaw-deploy@my-openclaw-project.iam.gserviceaccount.com" \
     --role="roles/compute.instanceAdmin.v1"
   ```

请勿在自动化场景中使用 Owner 角色。应遵循最小权限原则。

有关 IAM 角色的详细信息，请参阅：[https://cloud.google.com/iam/docs/understanding-roles](https://cloud.google.com/iam/docs/understanding-roles)

---

## 后续步骤

- 设置消息通道：[Channels](/channels)  
- 将本地设备配对为节点：[Nodes](/nodes)  
- 配置网关：[Gateway configuration](/gateway/configuration)