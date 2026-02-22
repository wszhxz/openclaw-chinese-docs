---
summary: "Optional Docker-based setup and onboarding for OpenClaw"
read_when:
  - You want a containerized gateway instead of local installs
  - You are validating the Docker flow
title: "Docker"
---
# Docker (可选)

Docker 是 **可选** 的。仅在您希望使用容器化网关或验证 Docker 流程时使用它。

## Docker 适合我吗？

- **是**：您希望有一个隔离的、临时的网关环境，或者在没有本地安装的情况下运行 OpenClaw。
- **否**：您是在自己的机器上运行，并且只需要最快的开发循环。请使用正常的安装流程。
- **沙箱说明**：代理沙箱也使用 Docker，但它**不需要**整个网关在 Docker 中运行。请参阅 [Sandboxing](/gateway/sandboxing)。

本指南涵盖：

- 容器化网关（完整的 OpenClaw 在 Docker 中）
- 每会话代理沙箱（主机网关 + Docker 隔离的代理工具）

沙箱详细信息：[Sandboxing](/gateway/sandboxing)

## 要求

- Docker Desktop（或 Docker Engine）+ Docker Compose v2
- 足够的磁盘空间用于镜像 + 日志

## 容器化网关 (Docker Compose)

### 快速开始（推荐）

从仓库根目录：

```bash
./docker-setup.sh
```

此脚本：

- 构建网关镜像
- 运行入站向导
- 打印可选的提供商设置提示
- 通过 Docker Compose 启动网关
- 生成网关令牌并写入 `.env`

可选环境变量：

- `OPENCLAW_DOCKER_APT_PACKAGES` — 在构建期间安装额外的 apt 包
- `OPENCLAW_EXTRA_MOUNTS` — 添加额外的主机绑定挂载
- `OPENCLAW_HOME_VOLUME` — 在命名卷中持久化 `/home/node`

完成后：

- 在浏览器中打开 `http://127.0.0.1:18789/`。
- 将令牌粘贴到控制 UI（设置 → 令牌）。
- 需要再次获取 URL？运行 `docker compose run --rm openclaw-cli dashboard --no-open`。

它会在主机上写入 config/workspace：

- `~/.openclaw/`
- `~/.openclaw/workspace`

在 VPS 上运行？请参阅 [Hetzner (Docker VPS)](/install/hetzner)。

### Shell 辅助工具（可选）

为了更轻松地管理日常 Docker，安装 `ClawDock`：

```bash
mkdir -p ~/.clawdock && curl -sL https://raw.githubusercontent.com/openclaw/openclaw/main/scripts/shell-helpers/clawdock-helpers.sh -o ~/.clawdock/clawdock-helpers.sh
```

**添加到您的 shell 配置（zsh）：**

```bash
echo 'source ~/.clawdock/clawdock-helpers.sh' >> ~/.zshrc && source ~/.zshrc
```

然后使用 `clawdock-start`，`clawdock-stop`，`clawdock-dashboard` 等。运行 `clawdock-help` 以查看所有命令。

请参阅 [`ClawDock` 辅助工具 README](https://github.com/openclaw/openclaw/blob/main/scripts/shell-helpers/README.md) 以获取详细信息。

### 手动流程（compose）

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

### 控制 UI 令牌 + 配对（Docker）

如果看到“unauthorized”或“disconnected (1008): pairing required”，获取一个新的仪表板链接并批准浏览器设备：

```bash
docker compose run --rm openclaw-cli dashboard --no-open
docker compose run --rm openclaw-cli devices list
docker compose run --rm openclaw-cli devices approve <requestId>
```

更多详情：[Dashboard](/web/dashboard), [Devices](/cli/devices).

### 额外挂载（可选）

如果您想将其他主机目录挂载到容器中，请在运行`docker-setup.sh`之前设置`OPENCLAW_EXTRA_MOUNTS`。这接受一个以逗号分隔的Docker绑定挂载列表，并通过生成`docker-compose.extra.yml`将其应用于`openclaw-gateway`和`openclaw-cli`。

示例：

```bash
export OPENCLAW_EXTRA_MOUNTS="$HOME/.codex:/home/node/.codex:ro,$HOME/github:/home/node/github:rw"
./docker-setup.sh
```

注意：

- 路径必须与macOS/Windows上的Docker Desktop共享。
- 每个条目必须是`source:target[:options]`，且不能有空格、制表符或换行符。
- 如果您编辑了`OPENCLAW_EXTRA_MOUNTS`，请重新运行`docker-setup.sh`以重新生成额外的compose文件。
- `docker-compose.extra.yml`是自动生成的。请勿手动编辑它。

### 持久化整个容器主目录（可选）

如果您希望`/home/node`在容器重建后仍然存在，请通过`OPENCLAW_HOME_VOLUME`设置一个命名卷。这会创建一个Docker卷并将其挂载到`/home/node`，同时保留标准的配置/工作区绑定挂载。这里使用命名卷（而不是绑定路径）；对于绑定挂载，请使用`OPENCLAW_EXTRA_MOUNTS`。

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

- 命名卷必须匹配`^[A-Za-z0-9][A-Za-z0-9_.-]*$`。
- 如果您更改了`OPENCLAW_HOME_VOLUME`，请重新运行`docker-setup.sh`以重新生成额外的compose文件。
- 命名卷会一直存在，直到使用`docker volume rm <name>`删除为止。

### 安装额外的apt包（可选）

如果您需要镜像内的系统包（例如构建工具或媒体库），请在运行`docker-setup.sh`之前设置`OPENCLAW_DOCKER_APT_PACKAGES`。这会在镜像构建期间安装这些包，因此即使容器被删除，它们也会保留。

示例：

```bash
export OPENCLAW_DOCKER_APT_PACKAGES="ffmpeg build-essential"
./docker-setup.sh
```

注意：

- 这接受一个以空格分隔的apt包名称列表。
- 如果您更改了`OPENCLAW_DOCKER_APT_PACKAGES`，请重新运行`docker-setup.sh`以重新构建镜像。

### 高级用户/全功能容器（可选加入）

默认的Docker镜像是**安全优先**的，并以非root用户`node`运行。这减少了攻击面，但意味着：

- 运行时无法安装系统包
- 默认情况下没有Homebrew
- 没有捆绑的Chromium/Playwright浏览器

如果您需要一个功能更全面的容器，请使用这些可选设置：

1. **持久化 `/home/node`** 以便浏览器下载和工具缓存得以保留：

```bash
export OPENCLAW_HOME_VOLUME="openclaw_home"
./docker-setup.sh
```

2. **将系统依赖项打包到镜像中**（可重复且持久）：

```bash
export OPENCLAW_DOCKER_APT_PACKAGES="git curl jq"
./docker-setup.sh
```

3. **在没有 `npx` 的情况下安装 Playwright 浏览器**（避免 npm 覆盖冲突）：

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

如果您需要 Playwright 安装系统依赖项，请使用 `OPENCLAW_DOCKER_APT_PACKAGES` 重建镜像，
而不是在运行时使用 `--with-deps`。

4. **持久化 Playwright 浏览器下载**：

- 在 `docker-compose.yml` 中设置 `PLAYWRIGHT_BROWSERS_PATH=/home/node/.cache/ms-playwright`。
- 确保通过 `OPENCLAW_HOME_VOLUME` 持久化 `/home/node`，或者通过 `OPENCLAW_EXTRA_MOUNTS` 挂载
  `/home/node/.cache/ms-playwright`。

### 权限 + EACCES

该镜像以 `node`（uid 1000）运行。如果您在 `/home/node/.openclaw` 上看到权限错误，
请确保您的主机绑定挂载由 uid 1000 拥有。

示例（Linux 主机）：

```bash
sudo chown -R 1000:1000 /path/to/openclaw-config /path/to/openclaw-workspace
```

如果您选择为了方便以 root 运行，则接受安全权衡。

### 加速重建（推荐）

为了加速重建，请按顺序组织您的 Dockerfile 以便依赖层被缓存。
这可以避免除非锁文件更改否则重新运行 `pnpm install`：

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

### 通道设置（可选）

使用 CLI 容器配置通道，然后根据需要重启网关。

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

文档：[WhatsApp](/channels/whatsapp)，[Telegram](/channels/telegram)，[Discord](/channels/discord)

### OpenAI Codex OAuth（无头 Docker）

如果您在向导中选择了 OpenAI Codex OAuth，它会打开一个浏览器 URL 并尝试
捕获 `http://127.0.0.1:1455/auth/callback` 上的回调。在 Docker 或无头设置中，该回调可能会显示浏览器错误。
复制您最终到达的完整重定向 URL 并将其粘贴回向导以完成身份验证。

### 健康检查

```bash
docker compose exec openclaw-gateway node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"
```

### 端到端冒烟测试 (Docker)

```bash
scripts/e2e/onboard-docker.sh
```

### QR 导入冒烟测试 (Docker)

```bash
pnpm test:docker:qr
```

### 注意事项

- Gateway 绑定默认为 `lan` 用于容器使用。
- Dockerfile CMD 使用 `--allow-unconfigured`；使用 `gateway.mode` 挂载的配置而不是 `local` 也会启动。覆盖 CMD 以强制执行此保护。
- gateway 容器是会话的真相来源 (`~/.openclaw/agents/<agentId>/sessions/`)。

## 代理沙箱 (主机网关 + Docker 工具)

深入阅读: [沙箱](/gateway/sandboxing)

### 它的作用

当 `agents.defaults.sandbox` 启用时，**非主会话**在 Docker 容器中运行工具。网关保留在您的主机上，但工具执行是隔离的：

- 范围: 默认为 `"agent"`（每个代理一个容器 + 工作区）
- 范围: `"session"` 用于每个会话隔离
- 按范围的工作区文件夹挂载在 `/workspace`
- 可选代理工作区访问 (`agents.defaults.sandbox.workspaceAccess`)
- 允许/拒绝工具策略（拒绝优先）
- 入站媒体被复制到活动沙箱工作区 (`media/inbound/*`) 以便工具可以读取它（使用 `workspaceAccess: "rw"` 时，这会进入代理工作区）

警告: `scope: "shared"` 禁用跨会话隔离。所有会话共享一个容器和一个工作区。

### 按代理的沙箱配置文件（多代理）

如果您使用多代理路由，每个代理可以覆盖沙箱 + 工具设置：`agents.list[].sandbox` 和 `agents.list[].tools`（加上 `agents.list[].tools.sandbox.tools`）。这使您可以在一个网关中运行混合访问级别：

- 完全访问（个人代理）
- 只读工具 + 只读工作区（家庭/工作代理）
- 无文件系统/ shell 工具（公共代理）

参见 [多代理沙箱 & 工具](/tools/multi-agent-sandbox-tools) 获取示例、优先级和故障排除信息。

### 默认行为

- 镜像: `openclaw-sandbox:bookworm-slim`
- 每个代理一个容器
- 代理工作区访问: `workspaceAccess: "none"`（默认）使用 `~/.openclaw/sandboxes`
  - `"ro"` 将沙箱工作区保持在 `/workspace` 并以只读方式挂载代理工作区在 `/agent`（禁用 `write`/`edit`/`apply_patch`）
  - `"rw"` 以读写方式挂载代理工作区在 `/workspace`
- 自动清理: 空闲 > 24小时 或 年龄 > 7天
- 网络: 默认为 `none`（如果需要出口，请显式选择加入）
- 默认允许: `exec`, `process`, `read`, `write`, `edit`, `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status`
- 默认拒绝: `browser`, `canvas`, `nodes`, `cron`, `discord`, `gateway`

### 启用沙箱

如果您计划在 `setupCommand` 中安装包，请注意：

- 默认 `docker.network` 是 `"none"`（无出口）。
- `readOnlyRoot: true` 块阻止包安装。
- `user` 必须是 root 才能 `apt-get`（省略 `user` 或设置 `user: "0:0"`）。
  OpenClaw 在 `setupCommand`（或 docker 配置）更改时自动重新创建容器
  除非容器是 **最近使用** 的（在约 5 分钟内）。热容器
  使用确切的 `openclaw sandbox recreate ...` 命令记录警告。

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

加固选项位于 `agents.defaults.sandbox.docker`：
`network`, `user`, `pidsLimit`, `memory`, `memorySwap`, `cpus`, `ulimits`,
`seccompProfile`, `apparmorProfile`, `dns`, `extraHosts`。

多代理：通过 `agents.list[].sandbox.{docker,browser,prune}.*` 按代理覆盖 `agents.defaults.sandbox.{docker,browser,prune}.*`
（当 `agents.defaults.sandbox.scope` / `agents.list[].sandbox.scope` 是 `"shared"` 时忽略）。

### 构建默认沙箱镜像

```bash
scripts/sandbox-setup.sh
```

这使用 `Dockerfile.sandbox` 构建 `openclaw-sandbox:bookworm-slim`。

### 沙箱通用镜像（可选）

如果您想要一个带有常见构建工具（Node, Go, Rust 等）的沙箱镜像，请构建通用镜像：

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

### 沙盒浏览器镜像

要在沙盒中运行浏览器工具，请构建浏览器镜像：

```bash
scripts/sandbox-browser-setup.sh
```

这使用
`Dockerfile.sandbox-browser` 构建 `openclaw-sandbox-browser:bookworm-slim`。容器运行启用了CDP的Chromium，并且可以选择性地使用noVNC观察器（通过Xvfb进行有头模式）。

注意事项：

- 有头模式（Xvfb）相比无头模式可以减少机器人阻止。
- 通过设置 `agents.defaults.sandbox.browser.headless=true` 仍然可以使用无头模式。
- 不需要完整的桌面环境（GNOME）；Xvfb提供显示。
- 浏览器容器默认使用专用的Docker网络 (`openclaw-sandbox-browser`) 而不是全局 `bridge`。
- 可选的 `agents.defaults.sandbox.browser.cdpSourceRange` 通过CIDR限制容器边缘CDP入口流量（例如 `172.21.0.1/32`）。
- noVNC观察器访问默认是受密码保护的；OpenClaw提供一个短期观察者令牌URL而不是在URL中共享原始密码。

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

启用后，代理会接收：

- 一个沙盒浏览器控制URL（用于 `browser` 工具）
- 一个noVNC URL（如果启用且headless=false）

记住：如果您对工具使用白名单，请添加 `browser`（并从deny中移除）或工具将保持被阻止状态。
修剪规则 (`agents.defaults.sandbox.prune`) 同样适用于浏览器容器。

### 自定义沙盒镜像

构建您自己的镜像并指向配置：

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
- 如果 `allow` 为空：所有工具（除了deny）都可用。
- 如果 `allow` 非空：只有 `allow` 中的工具可用（减去deny）。

### 修剪策略

两个选项：

- `prune.idleHours`：删除X小时内未使用的容器（0 = 禁用）
- `prune.maxAgeDays`：删除超过X天的容器（0 = 禁用）

示例：

- 保留繁忙会话但限制生命周期：
  `idleHours: 24`, `maxAgeDays: 7`
- 从不修剪：
  `idleHours: 0`, `maxAgeDays: 0`

### 安全说明

- 硬墙仅适用于 **工具**（执行/读取/写入/编辑/应用补丁）。
- 像浏览器/摄像头/画布这样的主机专用工具默认被阻止。
- 在沙盒中允许 `browser` **会破坏隔离**（浏览器在主机上运行）。

## 故障排除

- 图像缺失：使用[`scripts/sandbox-setup.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/sandbox-setup.sh) 构建或设置 `agents.defaults.sandbox.docker.image`。
- 容器未运行：它将在会话需求时自动创建。
- 沙箱中的权限错误：将 `docker.user` 设置为与挂载的工作区所有权匹配的 UID:GID（或更改工作区文件夹的所有权）。
- 自定义工具未找到：OpenClaw 使用 `sh -lc`（登录 shell）运行命令，该命令会加载 `/etc/profile` 并可能重置 PATH。将 `docker.env.PATH` 设置为在前面添加自定义工具路径（例如 `/custom/bin:/usr/local/share/npm-global/bin`），或在 Dockerfile 中的 `/etc/profile.d/` 下添加脚本。