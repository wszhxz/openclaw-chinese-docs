---
summary: "Optional Docker-based setup and onboarding for OpenClaw"
read_when:
  - You want a containerized gateway instead of local installs
  - You are validating the Docker flow
title: "Docker"
---
# Docker（可选）

Docker 是**可选的**。仅当您想要容器化网关或验证 Docker 流程时使用它。

## Docker 适合我吗？

- **是**：您想要一个隔离的、一次性的网关环境，或者要在没有本地安装的主机上运行 OpenClaw。
- **否**：您在自己的机器上运行，只想要最快的开发循环。请改用正常安装流程。
- **沙箱说明**：代理沙箱也使用 Docker，但它**不**要求整个网关在 Docker 中运行。请参阅 [Sandboxing](/gateway/sandboxing)。

本指南涵盖：

- 容器化网关（Docker 中的完整 OpenClaw）
- 每会话代理沙箱（主机网关 + Docker 隔离的代理工具）

沙箱详情：[Sandboxing](/gateway/sandboxing)

## 要求

- Docker Desktop（或 Docker Engine）+ Docker Compose v2
- 镜像构建至少需要 2 GB RAM（`pnpm install` 在 1 GB 主机上可能会因 OOM-killed 而退出，exit 137）
- 足够的磁盘空间用于镜像 + 日志
- 如果在 VPS/公共主机上运行，请查阅
  [网络暴露的安全加固](/gateway/security#04-network-exposure-bind--port--firewall)，
  尤其是 Docker `DOCKER-USER` 防火墙策略。

## 容器化网关（Docker Compose）

### 快速开始（推荐）

<Note>
Docker defaults here assume bind modes (__CODE_BLOCK_2__/__CODE_BLOCK_3__), not host aliases. Use bind
mode values in __CODE_BLOCK_4__ (for example __CODE_BLOCK_5__ or __CODE_BLOCK_6__), not host aliases like
__CODE_BLOCK_7__ or __CODE_BLOCK_8__.
</Note>

从仓库根目录：

```bash
./docker-setup.sh
```

此脚本：

- 本地构建网关镜像（如果设置了 `OPENCLAW_IMAGE` 则拉取远程镜像）
- 运行入门向导
- 打印可选的提供商设置提示
- 通过 Docker Compose 启动网关
- 生成网关 token 并将其写入 `.env`

可选环境变量：

- `OPENCLAW_IMAGE` — 使用远程镜像而不是本地构建（例如 `ghcr.io/openclaw/openclaw:latest`）
- `OPENCLAW_DOCKER_APT_PACKAGES` — 构建期间安装额外的 apt 包
- `OPENCLAW_EXTENSIONS` — 构建时预安装扩展依赖项（空格分隔的扩展名称，例如 `diagnostics-otel matrix`）
- `OPENCLAW_EXTRA_MOUNTS` — 添加额外的主机绑定挂载
- `OPENCLAW_HOME_VOLUME` — 将 `/home/node` 持久化到命名卷中
- `OPENCLAW_SANDBOX` — 选择加入 Docker 网关沙箱引导。只有明确的真值才能启用它：`1`, `true`, `yes`, `on`
- `OPENCLAW_INSTALL_DOCKER_CLI` — 本地镜像构建的构建参数透传（`1` 在镜像中安装 Docker CLI）。`docker-setup.sh` 在 `OPENCLAW_SANDBOX=1` 进行本地构建时自动设置此项。
- `OPENCLAW_DOCKER_SOCKET` — 覆盖 Docker socket 路径（默认：`DOCKER_HOST=unix://...` 路径，否则 `/var/run/docker.sock`）
- `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` — 紧急突破：允许受信任的私有网络
  `ws://` 作为 CLI/入门客户端路径的目标（默认仅限环回）
- `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` — 禁用容器浏览器加固标志
  `--disable-3d-apis`, `--disable-software-rasterizer`, `--disable-gpu` 当您需要
  WebGL/3D 兼容性时。
- `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` — 当浏览器
  流程需要它们时保持扩展启用（默认在沙箱浏览器中禁用扩展）。
- `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` — 设置 Chromium 渲染进程
  限制；设置为 `0` 以跳过该标志并使用 Chromium 默认行为。

完成后：

- 在浏览器中打开 `http://127.0.0.1:18789/`。
- 将 token 粘贴到控制 UI 中（设置 → token）。
- 需要再次获取 URL？运行 `docker compose run --rm openclaw-cli dashboard --no-open`。

### 为 Docker 网关启用代理沙箱（可选）

`docker-setup.sh` 也可以为 Docker
部署引导 `agents.defaults.sandbox.*`。

启用方式：

```bash
export OPENCLAW_SANDBOX=1
./docker-setup.sh
```

自定义 socket 路径（例如 rootless Docker）：

```bash
export OPENCLAW_SANDBOX=1
export OPENCLAW_DOCKER_SOCKET=/run/user/1000/docker.sock
./docker-setup.sh
```

注意：

- 脚本仅在沙箱先决条件通过后挂载 `docker.sock`。
- 如果沙箱设置无法完成，脚本将重置
  `agents.defaults.sandbox.mode` 为 `off` 以避免过时/损坏的沙箱配置
  在重新运行时。
- 如果缺少 `Dockerfile.sandbox`，脚本将打印警告并继续；
  如果需要，使用 `scripts/sandbox-setup.sh` 构建 `openclaw-sandbox:bookworm-slim`。
- 对于非本地 `OPENCLAW_IMAGE` 值，镜像必须已包含 Docker
  CLI 支持以执行沙箱。

### 自动化/CI（非交互式，无 TTY 噪音）

对于脚本和 CI，使用 `-T` 禁用 Compose 伪 TTY 分配：

```bash
docker compose run -T --rm openclaw-cli gateway probe
docker compose run -T --rm openclaw-cli devices list --json
```

如果您的自动化未导出 Claude 会话变量，现在将它们留空默认会在 `docker-compose.yml` 中解析为
空值，以避免重复出现 "variable is not set"
警告。

### 共享网络安全说明（CLI + gateway）

`openclaw-cli` 使用 `network_mode: "service:openclaw-gateway"` 以便 CLI 命令可以
在 Docker 中通过 `127.0.0.1` 可靠地到达网关。

将此视为共享信任边界：环回绑定不是这两者之间的隔离
容器。如果您需要更强的分离，请从单独的容器/主机
网络路径运行命令，而不是捆绑的 `openclaw-cli` 服务。

为了减少 CLI 进程受损时的影响，compose 配置丢弃
`NET_RAW`/`NET_ADMIN` 并在 `openclaw-cli` 上启用 `no-new-privileges`。

它在主机上写入配置/工作区：

- `~/.openclaw/`
- `~/.openclaw/workspace`

在 VPS 上运行？请参阅 [Hetzner (Docker VPS)](/install/hetzner)。

### 使用远程镜像（跳过本地构建）

官方预构建镜像发布在：

- [GitHub Container Registry 包](https://github.com/openclaw/openclaw/pkgs/container/openclaw)

使用镜像名称 `ghcr.io/openclaw/openclaw`（不是类似命名的 Docker Hub
镜像）。

常用标签：

- `main` — 来自 `main` 的最新构建
- `<version>` — 发布标签构建（例如 `2026.2.26`）
- `latest` — 最新稳定发布标签

### 基础镜像元数据

主 Docker 镜像当前使用：

- `node:22-bookworm`

Docker 镜像现在发布 OCI base-image 注解（sha256 是一个示例，
并指向该标签的固定多架构 manifest 列表）：

- `org.opencontainers.image.base.name=docker.io/library/node:22-bookworm`
- `org.opencontainers.image.base.digest=sha256:b501c082306a4f528bc4038cbf2fbb58095d583d0419a259b2114b5ac53d12e9`
- `org.opencontainers.image.source=https://github.com/openclaw/openclaw`
- `org.opencontainers.image.url=https://openclaw.ai`
- `org.opencontainers.image.documentation=https://docs.openclaw.ai/install/docker`
- `org.opencontainers.image.licenses=MIT`
- `org.opencontainers.image.title=OpenClaw`
- `org.opencontainers.image.description=OpenClaw gateway and CLI runtime container image`
- `org.opencontainers.image.revision=<git-sha>`
- `org.opencontainers.image.version=<tag-or-main>`
- `org.opencontainers.image.created=<rfc3339 timestamp>`

参考：[OCI 镜像注解](https://github.com/opencontainers/image-spec/blob/main/annotations.md)

发布上下文：此仓库的标签历史已在
`v2026.2.22` 及更早的 2026 标签中使用 Bookworm（例如 `v2026.2.21`, `v2026.2.9`）。

默认情况下，设置脚本从源代码构建镜像。要拉取预构建
镜像，请在运行脚本前设置 `OPENCLAW_IMAGE`：

```bash
export OPENCLAW_IMAGE="ghcr.io/openclaw/openclaw:latest"
./docker-setup.sh
```

脚本检测到 `OPENCLAW_IMAGE` 不是默认值 `openclaw:local`，并且
运行 `docker pull` 而不是 `docker build`。其他一切（入门，
网关启动，token 生成）工作方式相同。

`docker-setup.sh` 仍然从仓库根目录运行，因为它使用本地
`docker-compose.yml` 和辅助文件。`OPENCLAW_IMAGE` 跳过本地镜像构建
时间；它不替换 compose/setup 工作流。

### Shell 辅助工具（可选）

为了更轻松的日常 Docker 管理，安装 `ClawDock`：

```bash
mkdir -p ~/.clawdock && curl -sL https://raw.githubusercontent.com/openclaw/openclaw/main/scripts/shell-helpers/clawdock-helpers.sh -o ~/.clawdock/clawdock-helpers.sh
```

**添加到您的 shell 配置 (zsh)：**

```bash
echo 'source ~/.clawdock/clawdock-helpers.sh' >> ~/.zshrc && source ~/.zshrc
```

然后使用 `clawdock-start`, `clawdock-stop`, `clawdock-dashboard` 等。运行 `clawdock-help` 查看所有命令。

详见 [`ClawDock` 辅助工具 README](https://github.com/openclaw/openclaw/blob/main/scripts/shell-helpers/README.md)。

### 手动流程 (compose)

```bash
docker build -t openclaw:local -f Dockerfile .
docker compose run --rm openclaw-cli onboard
docker compose up -d openclaw-gateway
```

注意：从仓库根目录运行 `docker compose ...`。如果您启用了
`OPENCLAW_EXTRA_MOUNTS` 或 `OPENCLAW_HOME_VOLUME`，设置脚本会写入
`docker-compose.extra.yml`；在其他地方运行 Compose 时包含它：

```bash
docker compose -f docker-compose.yml -f docker-compose.extra.yml <command>
```

### 控制 UI token + 配对 (Docker)

如果您看到"unauthorized"或"disconnected (1008): pairing required"，获取一个
新的 dashboard 链接并批准浏览器设备：

```bash
docker compose run --rm openclaw-cli dashboard --no-open
docker compose run --rm openclaw-cli devices list
docker compose run --rm openclaw-cli devices approve <requestId>
```

更多详情：[Dashboard](/web/dashboard), [Devices](/cli/devices)。

### 额外挂载（可选）

如果您想将额外的主机目录挂载到容器中，设置
`OPENCLAW_EXTRA_MOUNTS` 在运行 `docker-setup.sh` 之前。这接受一个
逗号分隔的 Docker 绑定挂载列表，并将它们应用于
`openclaw-gateway` 和 `openclaw-cli`，通过生成 `docker-compose.extra.yml`。

示例：

```bash
export OPENCLAW_EXTRA_MOUNTS="$HOME/.codex:/home/node/.codex:ro,$HOME/github:/home/node/github:rw"
./docker-setup.sh
```

注意：

- 路径必须在 macOS/Windows 上与 Docker Desktop 共享。
- 每个条目必须是 `source:target[:options]`，不能包含空格、制表符或换行符。
- 如果编辑了 `OPENCLAW_EXTRA_MOUNTS`，请重新运行 `docker-setup.sh` 以重新生成额外的 compose 文件。
- `docker-compose.extra.yml` 是自动生成的。不要手动编辑它。

### 持久化整个容器主目录（可选）

如果希望 `/home/node` 在容器重建后持久存在，请通过 `OPENCLAW_HOME_VOLUME` 设置一个命名卷。这将创建一个 Docker 卷并将其挂载到 `/home/node`，同时保留标准的 config/workspace 绑定挂载。此处请使用命名卷（而非绑定路径）；对于绑定挂载，请使用 `OPENCLAW_EXTRA_MOUNTS`。

示例：

```bash
export OPENCLAW_HOME_VOLUME="openclaw_home"
./docker-setup.sh
```

您可以将其与额外挂载结合使用：

```bash
export OPENCLAW_HOME_VOLUME="openclaw_home"
export OPENCLAW_EXTRA_MOUNTS="$HOME/.codex:/home/node/.codex:ro,$HOME/github:/home/node/github:rw"
./docker-setup.sh
```

注意：

- 命名卷必须匹配 `^[A-Za-z0-9][A-Za-z0-9_.-]*$`。
- 如果更改了 `OPENCLAW_HOME_VOLUME`，请重新运行 `docker-setup.sh` 以重新生成额外的 compose 文件。
- 命名卷将一直持久存在，直到使用 `docker volume rm <name>` 将其移除。

### 安装额外的 apt 包（可选）

如果需要在镜像内部使用系统包（例如构建工具或媒体库），请在运行 `docker-setup.sh` 之前设置 `OPENCLAW_DOCKER_APT_PACKAGES`。这会在镜像构建期间安装包，因此即使容器被删除，它们也会保留。

示例：

```bash
export OPENCLAW_DOCKER_APT_PACKAGES="ffmpeg build-essential"
./docker-setup.sh
```

注意：

- 此项接受以空格分隔的 apt 包名称列表。
- 如果更改了 `OPENCLAW_DOCKER_APT_PACKAGES`，请重新运行 `docker-setup.sh` 以重建镜像。

### 预安装扩展依赖项（可选）

拥有自己 `package.json` 的扩展（例如 `diagnostics-otel`、`matrix`、`msteams`）会在首次加载时安装其 npm 依赖项。若要将这些依赖项直接嵌入镜像中，请在运行 `docker-setup.sh` 之前设置 `OPENCLAW_EXTENSIONS`：

```bash
export OPENCLAW_EXTENSIONS="diagnostics-otel matrix"
./docker-setup.sh
```

或者直接构建时：

```bash
docker build --build-arg OPENCLAW_EXTENSIONS="diagnostics-otel matrix" .
```

注意：

- 此项接受扩展目录名称的空格分隔列表（位于 `extensions/` 下）。
- 仅影响拥有 `package.json` 的扩展；没有该文件的轻量级插件将被忽略。
- 如果更改了 `OPENCLAW_EXTENSIONS`，请重新运行 `docker-setup.sh` 以重建镜像。

### 高级用户/全功能容器（可选）

默认 Docker 镜像采用 **安全优先** 策略，并以非 root `node` 用户身份运行。这保持了较小的攻击面，但意味着：

- 运行时无法安装系统包
- 默认没有 Homebrew
- 没有 bundled Chromium/Playwright 浏览器

如果想要功能更全面的容器，请使用这些可选配置：

1. **持久化 `/home/node`** 以便浏览器下载和工具缓存得以保留：

```bash
export OPENCLAW_HOME_VOLUME="openclaw_home"
./docker-setup.sh
```

2. **将系统依赖项嵌入镜像**（可重复 + 持久）：

```bash
export OPENCLAW_DOCKER_APT_PACKAGES="git curl jq"
./docker-setup.sh
```

3. **安装 Playwright 浏览器而不使用 `npx`**（避免 npm 覆盖冲突）：

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

如果需要 Playwright 安装系统依赖项，请使用 `OPENCLAW_DOCKER_APT_PACKAGES` 重建镜像，而不是在运行时使用 `--with-deps`。

4. **持久化 Playwright 浏览器下载**：

- 在 `docker-compose.yml` 中设置 `PLAYWRIGHT_BROWSERS_PATH=/home/node/.cache/ms-playwright`。
- 确保 `/home/node` 通过 `OPENCLAW_HOME_VOLUME` 持久化，或通过 `OPENCLAW_EXTRA_MOUNTS` 挂载 `/home/node/.cache/ms-playwright`。

### 权限 + EACCES

镜像以 `node` (uid 1000) 身份运行。如果在 `/home/node/.openclaw` 上看到权限错误，请确保主机绑定挂载的所有者为 uid 1000。

示例（Linux 主机）：

```bash
sudo chown -R 1000:1000 /path/to/openclaw-config /path/to/openclaw-workspace
```

如果为了方便选择以 root 身份运行，您需接受相应的安全权衡。

### 更快的重建（推荐）

为了加快重建速度，请调整 Dockerfile 顺序以便缓存依赖层。这样可以避免重新运行 `pnpm install`，除非 lockfiles 发生变化：

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

### 渠道设置（可选）

使用 CLI 容器配置渠道，然后在需要时重启 gateway。

WhatsApp (QR)：

```bash
docker compose run --rm openclaw-cli channels login
```

Telegram (bot token)：

```bash
docker compose run --rm openclaw-cli channels add --channel telegram --token "<token>"
```

Discord (bot token)：

```bash
docker compose run --rm openclaw-cli channels add --channel discord --token "<token>"
```

文档：[WhatsApp](/channels/whatsapp), [Telegram](/channels/telegram), [Discord](/channels/discord)

### OpenAI Codex OAuth（无头 Docker）

如果在向导中选择 OpenAI Codex OAuth，它会打开一个浏览器 URL 并尝试捕获 `http://127.0.0.1:1455/auth/callback` 上的回调。在 Docker 或无头设置中，该回调可能会显示浏览器错误。复制您最终到达的完整重定向 URL 并将其粘贴回向导中以完成认证。

### 健康检查

容器探测端点（无需认证）：

```bash
curl -fsS http://127.0.0.1:18789/healthz
curl -fsS http://127.0.0.1:18789/readyz
```

别名：`/health` 和 `/ready`。

`/healthz` 是一个浅层存活探测，用于判断"gateway 进程是否运行”。`/readyz` 在启动宽限期内保持 ready 状态，仅在宽限期后所需的托管渠道仍断开连接或随后断开连接时变为 `503`。

Docker 镜像包含一个内置的 `HEALTHCHECK`，它在后台 ping `/healthz`。简单来说：Docker 会持续检查 OpenClaw 是否仍有响应。如果检查持续失败，Docker 会将容器标记为 `unhealthy`，编排系统（Docker Compose 重启策略、Swarm、Kubernetes 等）可以自动重启或替换它。

认证深度健康快照（gateway + channels）：

```bash
docker compose exec openclaw-gateway node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"
```

### E2E 冒烟测试 (Docker)

```bash
scripts/e2e/onboard-docker.sh
```

### QR 导入冒烟测试 (Docker)

```bash
pnpm test:docker:qr
```

### LAN 与 loopback (Docker Compose)

`docker-setup.sh` 默认 `OPENCLAW_GATEWAY_BIND=lan`，以便通过 Docker 端口发布实现主机对 `http://127.0.0.1:18789` 的访问。

- `lan`（默认）：主机浏览器 + 主机 CLI 可以访问发布的 gateway 端口。
- `loopback`：只有容器网络命名空间内的进程可以直接访问 gateway；主机发布的端口访问可能会失败。

设置脚本还会在 onboarding 后固定 `gateway.mode=local`，以便 Docker CLI 命令默认 targeting 本地 loopback。

旧版配置注意：在 `gateway.bind` 中使用 bind mode 值（`lan` / `loopback` / `custom` / `tailnet` / `auto`），而非主机别名（`0.0.0.0`, `127.0.0.1`, `localhost`, `::`, `::1`）。

如果看到 Docker CLI 命令出现 `Gateway target: ws://172.x.x.x:18789` 或重复的 `pairing required` 错误，请运行：

```bash
docker compose run --rm openclaw-cli config set gateway.mode local
docker compose run --rm openclaw-cli config set gateway.bind lan
docker compose run --rm openclaw-cli devices list --url ws://127.0.0.1:18789
```

### 注意

- Gateway bind 默认为 `lan` 以供容器使用（`OPENCLAW_GATEWAY_BIND`）。
- Dockerfile CMD 使用 `--allow-unconfigured`；带有 `gateway.mode` 而非 `local` 的挂载配置仍将启动。覆盖 CMD 以强制执行防护。
- gateway 容器是 sessions (`~/.openclaw/agents/<agentId>/sessions/`) 的真实来源。

### 存储模型

- **持久化主机数据：** Docker Compose 将 `OPENCLAW_CONFIG_DIR` 绑定挂载到 `/home/node/.openclaw`，将 `OPENCLAW_WORKSPACE_DIR` 绑定挂载到 `/home/node/.openclaw/workspace`，因此这些路径在容器替换后得以保留。
- **临时 Sandbox tmpfs：** 当启用 `agents.defaults.sandbox` 时，Sandbox 容器使用 `tmpfs` 用于 `/tmp`、`/var/tmp` 和 `/run`。这些挂载与顶层 Compose 栈分离，并随 Sandbox 容器消失。
- **磁盘增长热点：** 关注 `media/`、`agents/<agentId>/sessions/sessions.json`、transcript JSONL 文件、`cron/runs/*.jsonl` 以及 `/tmp/openclaw/` 下的滚动文件日志（或您配置的 `logging.file`）。如果您还在 Docker 之外运行 macOS 应用，其服务日志又是分开的：`~/.openclaw/logs/gateway.log`、`~/.openclaw/logs/gateway.err.log` 和 `/tmp/openclaw/openclaw-gateway.log`。

## Agent Sandbox（主机 gateway + Docker 工具）

深入了解：[Sandboxing](/gateway/sandboxing)

### 功能说明

当启用 `agents.defaults.sandbox` 时，**非主 sessions** 在 Docker 容器内运行工具。gateway 保留在您的主机上，但工具执行是隔离的：

- 范围：默认为 `"agent"`（每个 agent 一个容器 + 工作区）
- 范围：`"session"` 用于每 session 隔离
- 每范围工作区文件夹挂载在 `/workspace`
- 可选 agent 工作区访问 (`agents.defaults.sandbox.workspaceAccess`)
- 允许/拒绝工具策略（拒绝优先）
- 入站媒体被复制到活动的 Sandbox 工作区 (`media/inbound/*`) 以便工具可以读取它（使用 `workspaceAccess: "rw"` 时，这将落入 agent 工作区）

警告：`scope: "shared"` 禁用跨会话隔离。所有会话共享一个容器和一个工作区。

### 每个智能体的沙箱配置文件（多智能体）

如果您使用多智能体路由，每个智能体可以覆盖沙箱 + 工具设置：
`agents.list[].sandbox` 和 `agents.list[].tools`（加上 `agents.list[].tools.sandbox.tools`）。这让您可以在一个网关中运行混合访问级别：

- 完全访问（个人智能体）
- 只读工具 + 只读工作区（家庭/工作智能体）
- 无文件系统/Shell 工具（公共智能体）

参见 [多智能体沙箱与工具](/tools/multi-agent-sandbox-tools) 了解示例、优先级和故障排除。

### 默认行为

- 镜像：`openclaw-sandbox:bookworm-slim`
- 每个智能体一个容器
- 智能体工作区访问：`workspaceAccess: "none"`（默认）使用 `~/.openclaw/sandboxes`
  - `"ro"` 将沙箱工作区保持在 `/workspace` 并将智能体工作区只读挂载到 `/agent`（禁用 `write`/`edit`/`apply_patch`）
  - `"rw"` 将智能体工作区读写挂载到 `/workspace`
- 自动修剪：空闲 > 24 小时 或 存在时间 > 7 天
- 网络：默认 `none`（如果需要出站流量请明确选择加入）
  - `host` 被阻止。
  - `container:<id>` 默认被阻止（命名空间加入风险）。
- 默认允许：`exec`, `process`, `read`, `write`, `edit`, `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status`
- 默认拒绝：`browser`, `canvas`, `nodes`, `cron`, `discord`, `gateway`

### 启用沙箱

如果您计划在 `setupCommand` 中安装包，注意：

- 默认 `docker.network` 为 `"none"`（无出站流量）。
- `docker.network: "host"` 被阻止。
- `docker.network: "container:<id>"` 默认被阻止。
- 紧急覆盖（break-glass）：`agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`。
- `readOnlyRoot: true` 阻止包安装。
- `user` 必须是 root 才能用于 `apt-get`（省略 `user` 或设置 `user: "0:0"`）。
  当 `setupCommand`（或 docker 配置）更改时，OpenClaw 会自动重新创建容器，除非容器是 **最近使用过的**（约 5 分钟内）。热容器会记录一条警告，包含确切的 `openclaw sandbox recreate ...` 命令。

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

加固配置项位于 `agents.defaults.sandbox.docker` 下：
`network`, `user`, `pidsLimit`, `memory`, `memorySwap`, `cpus`, `ulimits`,
`seccompProfile`, `apparmorProfile`, `dns`, `extraHosts`,
`dangerouslyAllowContainerNamespaceJoin`（仅限紧急覆盖）。

多智能体：通过 `agents.list[].sandbox.{docker,browser,prune}.*` 覆盖每个智能体的 `agents.defaults.sandbox.{docker,browser,prune}.*`
（当 `agents.defaults.sandbox.scope` / `agents.list[].sandbox.scope` 为 `"shared"` 时忽略）。

### 构建默认沙箱镜像

```bash
scripts/sandbox-setup.sh
```

这使用 `Dockerfile.sandbox` 构建 `openclaw-sandbox:bookworm-slim`。

### 沙箱通用镜像（可选）

如果您想要一个带有通用构建工具（Node、Go、Rust 等）的沙箱镜像，请构建通用镜像：

```bash
scripts/sandbox-common-setup.sh
```

这构建 `openclaw-sandbox-common:bookworm-slim`。要使用它：

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

要在沙箱内运行浏览器工具，请构建浏览器镜像：

```bash
scripts/sandbox-browser-setup.sh
```

这使用 `Dockerfile.sandbox-browser` 构建 `openclaw-sandbox-browser:bookworm-slim`。容器运行启用 CDP 的 Chromium 以及可选的 noVNC 观察器（通过 Xvfb 实现有头模式）。

注意：

- 有头模式（Xvfb）相比无头模式减少机器人拦截。
- 可以通过设置 `agents.defaults.sandbox.browser.headless=true` 继续使用无头模式。
- 不需要完整的桌面环境（GNOME）；Xvfb 提供显示。
- 浏览器容器默认使用专用的 Docker 网络（`openclaw-sandbox-browser`）而不是全局 `bridge`。
- 可选的 `agents.defaults.sandbox.browser.cdpSourceRange` 通过 CIDR 限制容器边缘 CDP 入站流量（例如 `172.21.0.1/32`）。
- noVNC 观察器访问默认受密码保护；OpenClaw 提供一个短寿命的观察器令牌 URL，服务于本地引导页面并将密码保留在 URL 片段中（而不是 URL 查询参数）。
- 浏览器容器启动默认值对于共享/容器工作负载是保守的，包括：
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
  - 如果设置了 `agents.defaults.sandbox.browser.noSandbox`，`--no-sandbox` 和 `--disable-setuid-sandbox` 也会被追加。
  - 上述三个图形加固标志是可选的。如果您的工作负载需要 WebGL/3D，设置 `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` 以在不使用 `--disable-3d-apis`、`--disable-software-rasterizer` 和 `--disable-gpu` 的情况下运行。
  - 扩展行为由 `--disable-extensions` 控制，并且可以通过 `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` 禁用（启用扩展），用于依赖扩展的页面或扩展密集型工作流。
  - `--renderer-process-limit=2` 也可通过 `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT` 配置；设置 `0` 以让 Chromium 选择其默认进程限制，当需要调整浏览器并发时。

默认值在捆绑镜像中默认应用。如果您需要不同的 Chromium 标志，请使用自定义浏览器镜像并提供您自己的入口点。

使用配置：

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

启用时，智能体接收：

- 一个沙箱浏览器控制 URL（用于 `browser` 工具）
- 一个 noVNC URL（如果启用且 headless=false）

记住：如果您使用工具允许列表，添加 `browser`（并将其从拒绝列表中移除），否则工具仍将受阻。
修剪规则（`agents.defaults.sandbox.prune`）也适用于浏览器容器。

### 自定义沙箱镜像

构建您自己的镜像并将配置指向它：

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
- 如果 `allow` 为空：所有工具（除拒绝外）均可用。
- 如果 `allow` 非空：只有 `allow` 中的工具可用（减去拒绝）。

### 修剪策略

两个配置项：

- `prune.idleHours`：移除 X 小时内未使用的容器（0 = 禁用）
- `prune.maxAgeDays`：移除存在时间超过 X 天的容器（0 = 禁用）

示例：

- 保持繁忙会话但限制生命周期：
  `idleHours: 24`, `maxAgeDays: 7`
- 从不修剪：
  `idleHours: 0`, `maxAgeDays: 0`

### 安全说明

- 硬墙仅适用于 **工具**（exec/read/write/edit/apply_patch）。
- 仅限主机的工具如 browser/camera/canvas 默认被阻止。
- 允许在沙箱中使用 `browser` **会破坏隔离**（浏览器在主机上运行）。

## 故障排除

- 镜像缺失：使用 [`scripts/sandbox-setup.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/sandbox-setup.sh) 构建或设置 `agents.defaults.sandbox.docker.image`。
- 容器未运行：它将按需为每个会话自动创建。
- 沙箱中的权限错误：设置 `docker.user` 为匹配您挂载工作区所有权的 UID:GID（或 chown 工作区文件夹）。
- 未找到自定义工具：OpenClaw 使用 `sh -lc`（登录 Shell）运行命令，这会 source `/etc/profile` 并可能重置 PATH。设置 `docker.env.PATH` 以前置您的自定义工具路径（例如 `/custom/bin:/usr/local/share/npm-global/bin`），或在 Dockerfile 中的 `/etc/profile.d/` 下添加脚本。