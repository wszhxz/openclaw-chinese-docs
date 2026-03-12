---
summary: "Optional Docker-based setup and onboarding for OpenClaw"
read_when:
  - You want a containerized gateway instead of local installs
  - You are validating the Docker flow
title: "Docker"
---
# Docker（可选）

Docker 是**可选的**。仅当您需要容器化的网关，或希望验证 Docker 流程时才使用它。

## Docker 是否适合我？

- **是**：您需要一个隔离的、一次性的网关环境，或希望在未安装本地依赖的主机上运行 OpenClaw。
- **否**：您正在自己的机器上运行，且仅追求最快的开发循环。请改用常规安装流程。
- **沙箱说明**：代理沙箱也使用 Docker，但它**不要求**整个网关必须运行在 Docker 中。参见 [沙箱](/gateway/sandboxing)。

本指南涵盖以下内容：

- 容器化网关（Docker 中的完整 OpenClaw）
- 每会话代理沙箱（宿主机网关 + Docker 隔离的代理工具）

沙箱详情：[沙箱](/gateway/sandboxing)

## 系统要求

- Docker Desktop（或 Docker Engine）+ Docker Compose v2
- 至少 2 GB 内存用于镜像构建（内存为 1 GB 的主机上，``pnpm install`` 可能因内存不足被系统终止，退出码为 137）
- 足够的磁盘空间以存储镜像和日志
- 若在 VPS/公网主机上运行，请查阅  
  [网络暴露的安全加固](/gateway/security#04-network-exposure-bind--port--firewall)，  
  尤其注意 Docker ``DOCKER-USER`` 防火墙策略。

## 容器化网关（Docker Compose）

### 快速开始（推荐）

<Note>
Docker defaults here assume bind modes (__CODE_BLOCK_2__/__CODE_BLOCK_3__), not host aliases. Use bind
mode values in __CODE_BLOCK_4__ (for example __CODE_BLOCK_5__ or __CODE_BLOCK_6__), not host aliases like
__CODE_BLOCK_7__ or __CODE_BLOCK_8__.
</Note>

从仓库根目录执行：

```bash
./docker-setup.sh
```

该脚本将：

- 在本地构建网关镜像（若设置了 ``OPENCLAW_IMAGE``，则拉取远程镜像）
- 运行入门向导
- 打印可选的提供商配置提示
- 通过 Docker Compose 启动网关
- 生成网关令牌，并将其写入 ``.env``

可选环境变量：

- ``OPENCLAW_IMAGE`` — 使用远程镜像而非本地构建（例如 ``ghcr.io/openclaw/openclaw:latest``）
- ``OPENCLAW_DOCKER_APT_PACKAGES`` — 构建过程中额外安装 apt 包
- ``OPENCLAW_EXTENSIONS`` — 构建时预安装扩展依赖（空格分隔的扩展名列表，例如 ``diagnostics-otel matrix``）
- ``OPENCLAW_EXTRA_MOUNTS`` — 添加额外的宿主机绑定挂载
- ``OPENCLAW_HOME_VOLUME`` — 将 ``/home/node`` 持久化至命名卷
- ``OPENCLAW_SANDBOX`` — 启用 Docker 网关沙箱引导。仅显式“真值”可启用：``1``、``true``、``yes``、``on``
- ``OPENCLAW_INSTALL_DOCKER_CLI`` — 构建参数透传，用于本地镜像构建（``1`` 将在镜像中安装 Docker CLI）。当 ``OPENCLAW_SANDBOX=1`` 为本地构建启用时，``docker-setup.sh`` 会自动设置该变量。
- ``OPENCLAW_DOCKER_SOCKET`` — 覆盖 Docker 套接字路径（默认为 ``DOCKER_HOST=unix://...`` 路径，否则为 ``/var/run/docker.sock``）
- ``OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`` — 应急开关：允许受信任的私有网络 ``ws://`` 目标用于 CLI/入门向导客户端路径（默认仅限回环地址）
- ``OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`` — 禁用容器浏览器强化标志 ``--disable-3d-apis``、``--disable-software-rasterizer``、``--disable-gpu``，当您需要 WebGL/3D 兼容性时启用
- ``OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0`` — 当浏览器流程需要时，保持扩展启用（默认在沙箱浏览器中禁用扩展）
- ``OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`` — 设置 Chromium 渲染进程限制；设为 ``0`` 可跳过该标志并采用 Chromium 默认行为

执行完成后：

- 在浏览器中打开 ``http://127.0.0.1:18789/``
- 将令牌粘贴至控制界面（设置 → 令牌）
- 需要再次获取 URL？运行 ``docker compose run --rm openclaw-cli dashboard --no-open``

### 为 Docker 网关启用代理沙箱（可选）

``docker-setup.sh`` 还可为 Docker 部署引导 ``agents.defaults.sandbox.*``

启用方式：

```bash
export OPENCLAW_SANDBOX=1
./docker-setup.sh
```

自定义套接字路径（例如 rootless Docker）：

```bash
export OPENCLAW_SANDBOX=1
export OPENCLAW_DOCKER_SOCKET=/run/user/1000/docker.sock
./docker-setup.sh
```

注意事项：

- 该脚本仅在沙箱前提条件满足后才挂载 ``docker.sock``
- 若沙箱设置无法完成，脚本会将 ``agents.defaults.sandbox.mode`` 重置为 ``off``，以避免重复运行时残留/损坏的沙箱配置
- 若缺失 ``Dockerfile.sandbox``，脚本将打印警告并继续执行；如需，可通过 ``scripts/sandbox-setup.sh`` 构建 ``openclaw-sandbox:bookworm-slim``
- 对于非本地的 ``OPENCLAW_IMAGE`` 值，镜像必须已内置 Docker CLI 支持，方可执行沙箱操作

### 自动化/CI（非交互式，无 TTY 噪声）

对于脚本和 CI 环境，请使用 ``-T`` 禁用 Compose 的伪 TTY 分配：

```bash
docker compose run -T --rm openclaw-cli gateway probe
docker compose run -T --rm openclaw-cli devices list --json
```

若您的自动化流程未导出 Claude 会话变量，则此时留空将默认解析为空值（``docker-compose.yml``），从而避免反复出现“变量未设置”的警告。

### 共享网络安全性说明（CLI + 网关）

``openclaw-cli`` 使用 ``network_mode: "service:openclaw-gateway"``，以便 CLI 命令可通过 Docker 中的 ``127.0.0.1`` 可靠地访问网关。

请将此视为共享的信任边界：回环绑定并不能在这两个容器之间提供隔离。若您需要更强的隔离性，请改用独立容器/主机网络路径执行命令，而非捆绑的 ``openclaw-cli`` 服务。

为降低 CLI 进程遭入侵后的潜在影响，Compose 配置会移除 ``NET_RAW``/``NET_ADMIN``，并在 ``openclaw-cli`` 上启用 ``no-new-privileges``。

它将配置/工作区写入宿主机：

- ``~/.openclaw/``
- ``~/.openclaw/workspace``

在 VPS 上运行？参见 [Hetzner（Docker VPS）](/install/hetzner)。

### 使用远程镜像（跳过本地构建）

官方预构建镜像发布于：

- [GitHub Container Registry 包](https://github.com/openclaw/openclaw/pkgs/container/openclaw)

请使用镜像名称 ``ghcr.io/openclaw/openclaw``（而非名称相似的 Docker Hub 镜像）。

常用标签：

- ``main`` — 来自 ``main`` 的最新构建
- ``<version>`` — 发布版本标签构建（例如 ``2026.2.26``）
- ``latest`` — 最新稳定发布版本标签

### 基础镜像元数据

主 Docker 镜像当前基于：

- ``node:22-bookworm``

该 Docker 镜像现已发布 OCI 基础镜像注解（sha256 仅为示例，指向该标签所绑定的多架构清单列表）：

- ``org.opencontainers.image.base.name=docker.io/library/node:22-bookworm``
- ``org.opencontainers.image.base.digest=sha256:b501c082306a4f528bc4038cbf2fbb58095d583d0419a259b2114b5ac53d12e9``
- ``org.opencontainers.image.source=https://github.com/openclaw/openclaw``
- ``org.opencontainers.image.url=https://openclaw.ai``
- ``org.opencontainers.image.documentation=https://docs.openclaw.ai/install/docker``
- ``org.opencontainers.image.licenses=MIT``
- ``org.opencontainers.image.title=OpenClaw``
- ``org.opencontainers.image.description=OpenClaw gateway and CLI runtime container image``
- ``org.opencontainers.image.revision=<git-sha>``
- ``org.opencontainers.image.version=<tag-or-main>``
- ``org.opencontainers.image.created=<rfc3339 timestamp>``

参考：[OCI 镜像注解](https://github.com/opencontainers/image-spec/blob/main/annotations.md)

发布上下文：本仓库带标签的历史记录已在 ``v2026.2.22`` 及更早的 2026 标签（例如 ``v2026.2.21``、``v2026.2.9``）中使用 Bookworm。

默认情况下，安装脚本从源码构建镜像。若要改为拉取预构建镜像，请在运行脚本前设置 ``OPENCLAW_IMAGE``：

```bash
export OPENCLAW_IMAGE="ghcr.io/openclaw/openclaw:latest"
./docker-setup.sh
```

脚本检测到 ``OPENCLAW_IMAGE`` 并非默认值 ``openclaw:local``，因此将运行 ``docker pull`` 而非 ``docker build``。其余所有步骤（入门向导、网关启动、令牌生成）均保持不变。

``docker-setup.sh`` 仍需在仓库根目录下运行，因其依赖本地 ``docker-compose.yml`` 和辅助文件。``OPENCLAW_IMAGE`` 跳过本地镜像构建耗时，但不替代 Compose/安装工作流。

### Shell 辅助工具（可选）

为简化日常 Docker 管理，可安装 ``ClawDock``：

```bash
mkdir -p ~/.clawdock && curl -sL https://raw.githubusercontent.com/openclaw/openclaw/main/scripts/shell-helpers/clawdock-helpers.sh -o ~/.clawdock/clawdock-helpers.sh
```

**添加至您的 Shell 配置（zsh）：**

```bash
echo 'source ~/.clawdock/clawdock-helpers.sh' >> ~/.zshrc && source ~/.zshrc
```

随后即可使用 ``clawdock-start``、``clawdock-stop``、``clawdock-dashboard`` 等命令。运行 ``clawdock-help`` 查看全部可用命令。

详情请参阅 [``ClawDock`` 辅助工具 README](https://github.com/openclaw/openclaw/blob/main/scripts/shell-helpers/README.md)。

### 手动流程（Compose）

```bash
docker build -t openclaw:local -f Dockerfile .
docker compose run --rm openclaw-cli onboard
docker compose up -d openclaw-gateway
```

注意：请从仓库根目录运行 ``docker compose ...``。若您启用了 ``OPENCLAW_EXTRA_MOUNTS`` 或 ``OPENCLAW_HOME_VOLUME``，安装脚本将写入 ``docker-compose.extra.yml``；在其他位置运行 Compose 时请一并包含该文件：

```bash
docker compose -f docker-compose.yml -f docker-compose.extra.yml <command>
```

### 控制界面令牌与配对（Docker）

若看到“未授权”或“已断开连接 (1008)：需要配对”，请获取新的仪表板链接并批准浏览器设备：

```bash
docker compose run --rm openclaw-cli dashboard --no-open
docker compose run --rm openclaw-cli devices list
docker compose run --rm openclaw-cli devices approve <requestId>
```

更多细节：[仪表板](/web/dashboard)，[设备](/cli/devices)。

### 额外挂载（可选）

若您希望将更多宿主机目录挂载进容器，请在运行 ``docker-setup.sh`` 前设置 ``OPENCLAW_EXTRA_MOUNTS``。该变量接受逗号分隔的 Docker 绑定挂载列表，并通过生成 ``docker-compose.extra.yml`` 同时应用于 ``openclaw-gateway`` 和 ``openclaw-cli``。

示例：

```bash
export OPENCLAW_EXTRA_MOUNTS="$HOME/.codex:/home/node/.codex:ro,$HOME/github:/home/node/github:rw"
./docker-setup.sh
```

注意事项：

- 路径必须在 macOS/Windows 上与 Docker Desktop 共享。  
- 每一项必须为 `source:target[:options]`，不得包含空格、制表符或换行符。  
- 如果您编辑了 `OPENCLAW_EXTRA_MOUNTS`，请重新运行 `docker-setup.sh` 以重新生成额外的 compose 文件。  
- `docker-compose.extra.yml` 是自动生成的。请勿手动编辑。

### 持久化整个容器主目录（可选）

如果您希望 `/home/node` 在容器重建后仍保持不变，请通过 `OPENCLAW_HOME_VOLUME` 设置一个命名卷。这将创建一个 Docker 卷，并将其挂载到 `/home/node`，同时保留标准的配置/工作区绑定挂载。此处请使用命名卷（而非绑定路径）；如需绑定挂载，请使用 `OPENCLAW_EXTRA_MOUNTS`。

示例：

```bash
export OPENCLAW_HOME_VOLUME="openclaw_home"
./docker-setup.sh
```

您可以将此与额外挂载结合使用：

```bash
export OPENCLAW_HOME_VOLUME="openclaw_home"
export OPENCLAW_EXTRA_MOUNTS="$HOME/.codex:/home/node/.codex:ro,$HOME/github:/home/node/github:rw"
./docker-setup.sh
```

注意事项：

- 命名卷名称必须符合 `^[A-Za-z0-9][A-Za-z0-9_.-]*$`。  
- 如果您更改了 `OPENCLAW_HOME_VOLUME`，请重新运行 `docker-setup.sh` 以重新生成额外的 compose 文件。  
- 命名卷将持续存在，直至使用 `docker volume rm <name>` 显式删除。

### 安装额外的 apt 包（可选）

如果您需要在镜像内安装系统包（例如构建工具或媒体库），请在运行 `docker-setup.sh` 之前设置 `OPENCLAW_DOCKER_APT_PACKAGES`。这将在镜像构建期间安装这些软件包，因此即使容器被删除，它们也会持续存在。

示例：

```bash
export OPENCLAW_DOCKER_APT_PACKAGES="ffmpeg build-essential"
./docker-setup.sh
```

注意事项：

- 此处接受以空格分隔的 apt 软件包名称列表。  
- 如果您更改了 `OPENCLAW_DOCKER_APT_PACKAGES`，请重新运行 `docker-setup.sh` 以重建镜像。

### 预安装扩展依赖项（可选）

带有自身 `package.json` 的扩展（例如 `diagnostics-otel`、`matrix`、`msteams`）会在首次加载时安装其 npm 依赖项。若要将这些依赖项直接打包进镜像，请在运行 `docker-setup.sh` 之前设置 `OPENCLAW_EXTENSIONS`：

```bash
export OPENCLAW_EXTENSIONS="diagnostics-otel matrix"
./docker-setup.sh
```

或在直接构建时使用：

```bash
docker build --build-arg OPENCLAW_EXTENSIONS="diagnostics-otel matrix" .
```

注意事项：

- 此处接受以空格分隔的扩展目录名称列表（位于 `extensions/` 下）。  
- 仅影响含有 `package.json` 的扩展；不含该文件的轻量级插件将被忽略。  
- 如果您更改了 `OPENCLAW_EXTENSIONS`，请重新运行 `docker-setup.sh` 以重建镜像。

### 高级用户 / 全功能容器（可选启用）

默认 Docker 镜像以**安全优先**为设计原则，以非 root 的 `node` 用户身份运行。这能显著缩小攻击面，但同时也意味着：

- 运行时无法安装系统软件包  
- 默认不包含 Homebrew  
- 不附带 Chromium/Playwright 浏览器  

如果您需要功能更全面的容器，请启用以下可选配置项：

1. **持久化 `/home/node`**，使浏览器下载和工具缓存得以保留：

```bash
export OPENCLAW_HOME_VOLUME="openclaw_home"
./docker-setup.sh
```

2. **将系统依赖项打包进镜像**（可重复 + 持久）：

```bash
export OPENCLAW_DOCKER_APT_PACKAGES="git curl jq"
./docker-setup.sh
```

3. **在不使用 `npx` 的前提下安装 Playwright 浏览器**（避免 npm 覆盖冲突）：

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

若您需要 Playwright 安装系统依赖项，请改用 `OPENCLAW_DOCKER_APT_PACKAGES` 重建镜像，而非在运行时使用 `--with-deps`。

4. **持久化 Playwright 浏览器下载内容**：

- 在 `docker-compose.yml` 中设置 `PLAYWRIGHT_BROWSERS_PATH=/home/node/.cache/ms-playwright`。  
- 确保 `/home/node` 通过 `OPENCLAW_HOME_VOLUME` 实现持久化，或通过 `OPENCLAW_EXTRA_MOUNTS` 挂载 `/home/node/.cache/ms-playwright`。

### 权限与 EACCES 错误

该镜像以 `node`（uid 1000）身份运行。若您在 `/home/node/.openclaw` 上遇到权限错误，请确保您的主机绑定挂载目录由 uid 1000 所有。

示例（Linux 主机）：

```bash
sudo chown -R 1000:1000 /path/to/openclaw-config /path/to/openclaw-workspace
```

若您出于便利性选择以 root 身份运行，则需自行承担相应的安全风险。

### 加快重建速度（推荐）

为加快镜像重建速度，请合理组织 Dockerfile 中的指令顺序，使依赖层尽可能被缓存。这样可避免在 lockfile 未变更时重复执行 `pnpm install`：

```dockerfile
FROM node:22-bookworm

# Install Bun (required for build scripts)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN corepack enable

WORKDIR /app

# Cache dependencies unless package metadata changes
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY ui/package.json ./ui/package.json
COPY scripts ./scripts

RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build
RUN pnpm ui:install
RUN pnpm ui:build

ENV NODE_ENV=production

CMD ["node","dist/index.js"]
```

### 通道配置（可选）

使用 CLI 容器配置通道，如有必要，请重启网关。

WhatsApp（二维码）：

```bash
docker compose run --rm openclaw-cli channels login
```

Telegram（机器人令牌）：

```bash
docker compose run --rm openclaw-cli channels add --channel telegram --token "<token>"
```

Discord（机器人令牌）：

```bash
docker compose run --rm openclaw-cli channels add --channel discord --token "<token>"
```

文档：[WhatsApp](/channels/whatsapp)、[Telegram](/channels/telegram)、[Discord](/channels/discord)

### OpenAI Codex OAuth（无头 Docker）

若在向导中选择了 OpenAI Codex OAuth，它会打开一个浏览器 URL 并尝试在 `http://127.0.0.1:1455/auth/callback` 上捕获回调。在 Docker 或无头环境中，该回调可能显示浏览器错误。请复制您最终跳转到的完整重定向 URL，并将其粘贴回向导中以完成认证。

### 健康检查

容器探针端点（无需认证）：

```bash
curl -fsS http://127.0.0.1:18789/healthz
curl -fsS http://127.0.0.1:18789/readyz
```

别名：`/health` 和 `/ready`。

`/healthz` 是一个浅层存活性探针，用于检测“网关进程是否已启动”。  
`/readyz` 在启动宽限期期间保持就绪状态；宽限期结束后，若所需托管通道仍未连接，或之后断开连接，则其状态将变为 `503`。

Docker 镜像内置了一个 `HEALTHCHECK`，它会在后台持续 ping `/healthz`。通俗地说：Docker 会持续检查 OpenClaw 是否仍处于响应状态。若连续探测失败，Docker 将把容器标记为 `unhealthy`，编排系统（如 Docker Compose 重启策略、Swarm、Kubernetes 等）便可自动重启或替换该容器。

经认证的深度健康快照（网关 + 各通道）：

```bash
docker compose exec openclaw-gateway node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"
```

### 端到端冒烟测试（Docker）

```bash
scripts/e2e/onboard-docker.sh
```

### 二维码导入冒烟测试（Docker）

```bash
pnpm test:docker:qr
```

### 局域网 vs 回环地址（Docker Compose）

`docker-setup.sh` 默认将 `OPENCLAW_GATEWAY_BIND=lan` 设为 `http://127.0.0.1:18789`，以便在启用 Docker 端口发布时，主机可正常访问网关。

- `lan`（默认）：主机浏览器和主机 CLI 均可访问已发布的网关端口。  
- `loopback`：仅容器网络命名空间内的进程可直接访问网关；主机发布的端口访问可能失败。

此外，初始化脚本还会在完成引导流程后固定 `gateway.mode=local`，使 Docker CLI 命令默认指向本地回环地址。

旧版配置说明：请在 `gateway.bind` 中使用绑定模式值（`lan` / `loopback` / `custom` / `tailnet` / `auto`），而非主机别名（`0.0.0.0`、`127.0.0.1`、`localhost`、`::`、`::1`）。

若您在执行 Docker CLI 命令时看到 `Gateway target: ws://172.x.x.x:18789` 或反复出现的 `pairing required` 错误，请运行：

```bash
docker compose run --rm openclaw-cli config set gateway.mode local
docker compose run --rm openclaw-cli config set gateway.bind lan
docker compose run --rm openclaw-cli devices list --url ws://127.0.0.1:18789
```

### 注意事项

- 网关绑定默认为 `lan`（适用于容器场景，即 `OPENCLAW_GATEWAY_BIND`）。  
- Dockerfile 中的 CMD 使用 `--allow-unconfigured`；若挂载的配置中含 `gateway.mode` 而非 `local`，仍将成功启动。可通过覆盖 CMD 强制启用该保护机制。  
- 网关容器是会话（`~/.openclaw/agents/<agentId>/sessions/`）的唯一可信来源。

### 存储模型

- **持久化的主机数据**：Docker Compose 将 `OPENCLAW_CONFIG_DIR` 绑定挂载至 `/home/node/.openclaw`，并将 `OPENCLAW_WORKSPACE_DIR` 绑定挂载至 `/home/node/.openclaw/workspace`，因此这些路径可在容器替换后继续保留。  
- **临时沙箱 tmpfs**：当启用 `agents.defaults.sandbox` 时，沙箱容器将使用 `tmpfs` 作为 `/tmp`、`/var/tmp` 和 `/run` 的挂载点。这些挂载点独立于顶层 Compose 栈，且随沙箱容器一同销毁。  
- **磁盘增长热点区域**：请关注 `media/`、`agents/<agentId>/sessions/sessions.json`、转录 JSONL 文件、`cron/runs/*.jsonl`，以及 `/tmp/openclaw/`（或您所配置的 `logging.file`）下的滚动日志文件。若您还在 Docker 外单独运行 macOS 应用程序，其服务日志则完全独立：`~/.openclaw/logs/gateway.log`、`~/.openclaw/logs/gateway.err.log` 和 `/tmp/openclaw/openclaw-gateway.log`。

## 代理沙箱（主机网关 + Docker 工具）

深入解析：[沙箱化](/gateway/sandboxing)

### 功能说明

当启用 `agents.defaults.sandbox` 后，**非主会话**将在 Docker 容器内运行工具。网关仍驻留在您的主机上，而工具执行过程则被隔离：

- 作用域：默认为 `"agent"`（每个代理对应一个容器 + 一个工作区）  
- 作用域：`"session"` 可实现按会话隔离  
- 每个作用域的工作区文件夹挂载于 `/workspace`  
- 可选启用代理工作区访问（`agents.defaults.sandbox.workspaceAccess`）  
- 支持工具允许/拒绝策略（拒绝优先）  
- 入站媒体文件将被复制至当前活跃沙箱工作区（`media/inbound/*`），以便工具读取（若启用 `workspaceAccess: "rw"`，则该文件将落于代理工作区）

警告：`scope: "shared"` 会禁用跨会话隔离。所有会话共享一个容器和一个工作区。

### 每代理沙箱配置文件（多代理）

如果您使用多代理路由，每个代理均可覆盖沙箱及工具设置：  
`agents.list[].sandbox` 和 `agents.list[].tools`（以及 `agents.list[].tools.sandbox.tools`）。这使得您可在同一网关中运行混合访问级别：

- 完全访问权限（个人代理）  
- 只读工具 + 只读工作区（家庭/工作代理）  
- 禁用文件系统/Shell 工具（公共代理）  

示例、优先级顺序及故障排查，请参阅 [多代理沙箱与工具](/tools/multi-agent-sandbox-tools)。

### 默认行为

- 镜像：`openclaw-sandbox:bookworm-slim`  
- 每个代理对应一个容器  
- 代理工作区访问权限：`workspaceAccess: "none"`（默认）使用 `~/.openclaw/sandboxes`  
  - `"ro"` 将沙箱工作区保留在 `/workspace`，并将代理工作区以只读方式挂载至 `/agent`（禁用 `write`/`edit`/`apply_patch`）  
  - `"rw"` 将代理工作区以读写方式挂载至 `/workspace`  
- 自动清理：空闲时间 > 24 小时 或 容器年龄 > 7 天  
- 网络：默认为 `none`（如需出站访问，需显式启用）  
  - `host` 被阻止。  
  - `container:<id>` 默认被阻止（存在命名空间加入风险）。  
- 默认允许的工具：`exec`、`process`、`read`、`write`、`edit`、`sessions_list`、`sessions_history`、`sessions_send`、`sessions_spawn`、`session_status`  
- 默认拒绝的工具：`browser`、`canvas`、`nodes`、`cron`、`discord`、`gateway`

### 启用沙箱

若您计划在 `setupCommand` 中安装软件包，请注意：

- 默认 `docker.network` 为 `"none"`（无出站访问）。  
- `docker.network: "host"` 被阻止。  
- `docker.network: "container:<id>"` 默认被阻止。  
- 紧急覆盖机制：`agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`。  
- `readOnlyRoot: true` 阻止软件包安装。  
- `user` 必须为 root 用户才能执行 `apt-get`（省略 `user` 或设置 `user: "0:0"`）。  
  当 `setupCommand`（或 Docker 配置）发生变更时，OpenClaw 会自动重建容器，**最近使用过**（约 5 分钟内）的容器除外。热容器会在日志中输出警告，并附上确切的 `openclaw sandbox recreate ...` 命令。

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        scope: "agent", // session | agent | shared (agent is default)
        workspaceAccess: "none", // none | ro | rw
        workspaceRoot: "~/.openclaw/sandboxes",
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: {
            nofile: { soft: 1024, hard: 2048 },
            nproc: 256,
          },
          seccompProfile: "/path/to/seccomp.json",
          apparmorProfile: "openclaw-sandbox",
          dns: ["1.1.1.1", "8.8.8.8"],
          extraHosts: ["internal.service:10.0.0.5"],
        },
        prune: {
          idleHours: 24, // 0 disables idle pruning
          maxAgeDays: 7, // 0 disables max-age pruning
        },
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        allow: [
          "exec",
          "process",
          "read",
          "write",
          "edit",
          "sessions_list",
          "sessions_history",
          "sessions_send",
          "sessions_spawn",
          "session_status",
        ],
        deny: ["browser", "canvas", "nodes", "cron", "discord", "gateway"],
      },
    },
  },
}
```

加固控制项位于 `agents.defaults.sandbox.docker` 下：  
`network`、`user`、`pidsLimit`、`memory`、`memorySwap`、`cpus`、`ulimits`、  
`seccompProfile`、`apparmorProfile`、`dns`、`extraHosts`、  
`dangerouslyAllowContainerNamespaceJoin`（仅限紧急覆盖）。

多代理场景：可通过 `agents.list[].sandbox.{docker,browser,prune}.*` 为每个代理单独覆盖 `agents.defaults.sandbox.{docker,browser,prune}.*`（当 `agents.defaults.sandbox.scope` / `agents.list[].sandbox.scope` 为 `"shared"` 时，该设置将被忽略）。

### 构建默认沙箱镜像

```bash
scripts/sandbox-setup.sh
```

此操作使用 `Dockerfile.sandbox` 构建 `openclaw-sandbox:bookworm-slim`。

### 沙箱通用镜像（可选）

若您需要一个预装常用构建工具（Node、Go、Rust 等）的沙箱镜像，请构建通用镜像：

```bash
scripts/sandbox-common-setup.sh
```

此操作构建 `openclaw-sandbox-common:bookworm-slim`。如需使用，请执行：

```json5
{
  agents: {
    defaults: {
      sandbox: { docker: { image: "openclaw-sandbox-common:bookworm-slim" } },
    },
  },
}
```

### 沙箱浏览器镜像

若要在沙箱内运行浏览器工具，请构建浏览器镜像：

```bash
scripts/sandbox-browser-setup.sh
```

此操作使用 `Dockerfile.sandbox-browser` 构建 `openclaw-sandbox-browser:bookworm-slim`。容器运行启用了 CDP 的 Chromium，并可选启用 noVNC 观察器（通过 Xvfb 实现有头模式）。

注意事项：

- 有头模式（Xvfb）相比无头模式更能降低机器人检测概率。  
- 仍可通过设置 `agents.defaults.sandbox.browser.headless=true` 使用无头模式。  
- 无需完整桌面环境（如 GNOME）；Xvfb 即可提供显示支持。  
- 浏览器容器默认使用专用 Docker 网络（`openclaw-sandbox-browser`），而非全局 `bridge`。  
- 可选的 `agents.defaults.sandbox.browser.cdpSourceRange` 可按 CIDR 限制容器边缘 CDP 入站访问（例如 `172.21.0.1/32`）。  
- noVNC 观察器访问默认受密码保护；OpenClaw 提供一个短期有效的观察器令牌 URL，该 URL 指向本地引导页面，并将密码置于 URL 片段（fragment）中（而非查询参数 query）。  
- 浏览器容器启动默认值针对共享/容器化工作负载进行了保守设定，包括：  
  - `--remote-debugging-address=127.0.0.1`  
  - `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`  
  - `--user-data-dir=${HOME}/.chrome`  
  - `--no-first-run`  
  - `--no-default-browser-check`  
  - `--disable-3d-apis`  
  - `--disable-software-rasterizer`  
  - `--disable-gpu`  
  - `--disable-dev-shm-usage`  
  - `--disable-background-networking`  
  - `--disable-features=TranslateUI`  
  - `--disable-breakpad`  
  - `--disable-crash-reporter`  
  - `--metrics-recording-only`  
  - `--renderer-process-limit=2`  
  - `--no-zygote`  
  - `--disable-extensions`  
  - 若设置了 `agents.defaults.sandbox.browser.noSandbox`，则还会追加 `--no-sandbox` 和 `--disable-setuid-sandbox`。  
  - 上述三项图形加固标志为可选。若您的工作负载需要 WebGL/3D 支持，请设置 `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`，以在不启用 `--disable-3d-apis`、`--disable-software-rasterizer` 和 `--disable-gpu` 的情况下运行。  
  - 扩展行为由 `--disable-extensions` 控制，可通过 `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` 禁用扩展（即启用扩展），适用于依赖扩展的网页或重度使用扩展的工作流。  
  - `--renderer-process-limit=2` 也可通过 `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT` 进行配置；设置 `0` 可让 Chromium 在需要调整浏览器并发数时自行选择其默认进程限制。

默认值已内置在打包镜像中。若您需要不同的 Chromium 启动参数，请使用自定义浏览器镜像并提供您自己的入口点（entrypoint）。

使用如下配置：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        browser: { enabled: true },
      },
    },
  },
}
```

自定义浏览器镜像：

```json5
{
  agents: {
    defaults: {
      sandbox: { browser: { image: "my-openclaw-browser" } },
    },
  },
}
```

启用后，代理将收到：

- 沙箱浏览器控制 URL（供 `browser` 工具使用）  
- noVNC URL（若已启用且 `headless=false`）

注意：若您对工具使用白名单机制，请务必添加 `browser`（并从黑名单中移除），否则该工具仍将被阻止。  
清理规则（`agents.defaults.sandbox.prune`）同样适用于浏览器容器。

### 自定义沙箱镜像

构建您自己的镜像，并在配置中指向它：

```bash
docker build -t my-openclaw-sbx -f Dockerfile.sandbox .
```

```json5
{
  agents: {
    defaults: {
      sandbox: { docker: { image: "my-openclaw-sbx" } },
    },
  },
}
```

### 工具策略（允许/拒绝）

- `deny` 优先于 `allow`。  
- 若 `allow` 为空：除黑名单外，所有工具均可用。  
- 若 `allow` 非空：仅 `allow` 中列出的工具可用（黑名单中的工具除外）。

### 清理策略

两个控制参数：

- `prune.idleHours`：移除 X 小时内未使用的容器（0 = 禁用）  
- `prune.maxAgeDays`：移除年龄超过 X 天的容器（0 = 禁用）

示例：

- 保留活跃会话但限制生命周期：  
  `idleHours: 24`、`maxAgeDays: 7`  
- 永不清理：  
  `idleHours: 0`、`maxAgeDays: 0`

### 安全说明

- “硬隔离墙”仅适用于 **工具**（exec/read/write/edit/apply_patch）。  
- 主机专属工具（如 browser/camera/canvas）默认被阻止。  
- 在沙箱中允许 `browser` **会破坏隔离性**（浏览器实际运行于主机上）。

## 故障排查

- 镜像缺失：使用 [`scripts/sandbox-setup.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/sandbox-setup.sh) 构建，或设置 `agents.defaults.sandbox.docker.image`。  
- 容器未运行：容器将在按需创建会话时自动启动。  
- 沙箱内出现权限错误：将 `docker.user` 设置为与挂载工作区所有权匹配的 UID:GID（或对工作区目录执行 `chown`）。  
- 自定义工具未找到：OpenClaw 使用 `sh -lc`（登录 Shell）运行命令，该 Shell 会加载 `/etc/profile`，可能导致 PATH 被重置。请设置 `docker.env.PATH` 以在 PATH 前添加您的自定义工具路径（例如 `/custom/bin:/usr/local/share/npm-global/bin`），或在 Dockerfile 中的 `/etc/profile.d/` 下添加脚本。