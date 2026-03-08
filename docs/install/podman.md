---
summary: "Run OpenClaw in a rootless Podman container"
read_when:
  - You want a containerized gateway with Podman instead of Docker
title: "Podman"
---
# Podman

在 **rootless** Podman 容器中运行 OpenClaw 网关。使用与 Docker 相同的镜像（从仓库 [Dockerfile](https://github.com/openclaw/openclaw/blob/main/Dockerfile) 构建）。

## 要求

- Podman (rootless)
- Sudo 用于一次性设置（创建用户，构建镜像）

## 快速开始

**1. 一次性设置**（从仓库根目录；创建用户，构建镜像，安装启动脚本）：

```bash
./setup-podman.sh
```

这还会创建一个最小的 `~openclaw/.openclaw/openclaw.json`（设置 `gateway.mode="local"`），以便网关可以在不运行向导的情况下启动。

默认情况下，容器 **不** 安装为 systemd 服务，您需要手动启动它（见下文）。对于具有自动启动和重启功能的生产风格设置，请将其安装为 systemd Quadlet 用户服务：

```bash
./setup-podman.sh --quadlet
```

（或者设置 `OPENCLAW_PODMAN_QUADLET=1`；使用 `--container` 仅安装容器和启动脚本。）

可选的构建时环境变量（在运行 `setup-podman.sh` 之前设置）：

- `OPENCLAW_DOCKER_APT_PACKAGES` — 在镜像构建期间安装额外的 apt 包
- `OPENCLAW_EXTENSIONS` — 预安装扩展依赖项（空格分隔的扩展名，例如 `diagnostics-otel matrix`）

**2. 启动网关**（手动，用于快速烟雾测试）：

```bash
./scripts/run-openclaw-podman.sh launch
```

**3. 入门向导**（例如添加渠道或提供商）：

```bash
./scripts/run-openclaw-podman.sh launch setup
```

然后打开 `http://127.0.0.1:18789/` 并使用来自 `~openclaw/.openclaw/.env` 的 token（或设置打印的值）。

## Systemd (Quadlet, 可选)

如果您运行了 `./setup-podman.sh --quadlet`（或 `OPENCLAW_PODMAN_QUADLET=1`），则会安装一个 [Podman Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) 单元，以便网关作为 openclaw 用户的 systemd 用户服务运行。该服务在设置结束时启用并启动。

- **启动：** `sudo systemctl --machine openclaw@ --user start openclaw.service`
- **停止：** `sudo systemctl --machine openclaw@ --user stop openclaw.service`
- **状态：** `sudo systemctl --machine openclaw@ --user status openclaw.service`
- **日志：** `sudo journalctl --machine openclaw@ --user -u openclaw.service -f`

quadlet 文件位于 `~openclaw/.config/containers/systemd/openclaw.container`。要更改端口或 env，编辑该文件（或其 source 的 `.env`），然后 `sudo systemctl --machine openclaw@ --user daemon-reload` 并重启服务。启动时，如果为 openclaw 启用了 lingering，服务会自动启动（当 loginctl 可用时，设置会执行此操作）。

要在未使用 quadlet 的初始设置 **之后** 添加 quadlet，请重新运行：`./setup-podman.sh --quadlet`。

## The openclaw 用户 (non-login)

`setup-podman.sh` 创建一个专用的系统用户 `openclaw`：

- **Shell：** `nologin` — 无交互式登录；减少攻击面。
- **Home：** 例如 `/home/openclaw` — 包含 `~/.openclaw`（config, workspace）和启动脚本 `run-openclaw-podman.sh`。
- **Rootless Podman：** 用户必须拥有 **subuid** 和 **subgid** 范围。许多 distros 在创建用户时会自动分配这些。如果设置打印警告，请将行添加到 `/etc/subuid` 和 `/etc/subgid`：

  ```text
  openclaw:100000:65536
  ```

  然后以该用户身份启动网关（例如从 cron 或 systemd）：

  ```bash
  sudo -u openclaw /home/openclaw/run-openclaw-podman.sh
  sudo -u openclaw /home/openclaw/run-openclaw-podman.sh setup
  ```

- **Config：** 只有 `openclaw` 和 root 可以访问 `/home/openclaw/.openclaw`。要编辑 config：网关运行后使用 Control UI，或 `sudo -u openclaw $EDITOR /home/openclaw/.openclaw/openclaw.json`。

## 环境和 config

- **Token：** 存储在 `~openclaw/.openclaw/.env` 中作为 `OPENCLAW_GATEWAY_TOKEN`。如果缺失，`setup-podman.sh` 和 `run-openclaw-podman.sh` 会生成它（使用 `openssl`、`python3` 或 `od`）。
- **可选：** 在该 `.env` 中，您可以设置 provider keys（例如 `GROQ_API_KEY`、`OLLAMA_API_KEY`）和其他 OpenClaw env vars。
- **Host ports：** 默认情况下，脚本映射 `18789`（gateway）和 `18790`（bridge）。启动时使用 `OPENCLAW_PODMAN_GATEWAY_HOST_PORT` 和 `OPENCLAW_PODMAN_BRIDGE_HOST_PORT` 覆盖 **host** 端口映射。
- **Gateway bind：** 默认情况下，`run-openclaw-podman.sh` 使用 `--bind loopback` 启动网关以进行安全的本地访问。要在 LAN 上暴露，设置 `OPENCLAW_GATEWAY_BIND=lan` 并在 `openclaw.json` 中配置 `gateway.controlUi.allowedOrigins`（或显式启用 host-header fallback）。
- **Paths：** Host config 和 workspace 默认为 `~openclaw/.openclaw` 和 `~openclaw/.openclaw/workspace`。使用 `OPENCLAW_CONFIG_DIR` 和 `OPENCLAW_WORKSPACE_DIR` 覆盖启动脚本使用的 host paths。

## 存储模型

- **Persistent host data：** `OPENCLAW_CONFIG_DIR` 和 `OPENCLAW_WORKSPACE_DIR` 被 bind-mounted 到容器中并在 host 上保留状态。
- **Ephemeral sandbox tmpfs：** 如果启用 `agents.defaults.sandbox`，工具 sandbox 容器会将 `tmpfs` 挂载到 `/tmp`、`/var/tmp` 和 `/run`。这些路径由 memory-backed 支持并随 sandbox 容器消失；顶层 Podman 容器设置不添加其自己的 tmpfs 挂载。
- **Disk growth hotspots：** 需要关注的主要路径是 `media/`、`agents/<agentId>/sessions/sessions.json`、transcript JSONL 文件、`cron/runs/*.jsonl` 以及 `/tmp/openclaw/` 下的 rolling file logs（或您配置的 `logging.file`）。

`setup-podman.sh` 现在将 image tar 暂存到私有 temp directory 中，并在设置期间打印所选的 base dir。对于 non-root runs，仅当该 base 安全使用时才接受 `TMPDIR`；否则回退到 `/var/tmp`，然后是 `/tmp`。保存的 tar 保持 owner-only，并 streamed 到目标用户的 `podman load`，因此私有 caller temp dirs 不会阻止设置。

## 有用命令

- **日志：** 使用 quadlet：`sudo journalctl --machine openclaw@ --user -u openclaw.service -f`。使用脚本：`sudo -u openclaw podman logs -f openclaw`
- **停止：** 使用 quadlet：`sudo systemctl --machine openclaw@ --user stop openclaw.service`。使用脚本：`sudo -u openclaw podman stop openclaw`
- **再次启动：** 使用 quadlet：`sudo systemctl --machine openclaw@ --user start openclaw.service`。使用脚本：重新运行启动脚本或 `podman start openclaw`
- **移除容器：** `sudo -u openclaw podman rm -f openclaw` — host 上的 config 和 workspace 会被保留

## 故障排除

- **config 或 auth-profiles 上的 Permission denied (EACCES)：** 容器默认为 `--userns=keep-id` 并作为运行脚本的 host 用户的相同 uid/gid 运行。确保您的 host `OPENCLAW_CONFIG_DIR` 和 `OPENCLAW_WORKSPACE_DIR` 由该用户拥有。
- **网关启动被阻止（缺少 `gateway.mode=local`）：** 确保 `~openclaw/.openclaw/openclaw.json` 存在并设置 `gateway.mode="local"`。如果缺失，`setup-podman.sh` 会创建此文件。
- **用户 openclaw 的 Rootless Podman 失败：** 检查 `/etc/subuid` 和 `/etc/subgid` 是否包含 `openclaw` 的行（例如 `openclaw:100000:65536`）。如果缺失则添加并重启。
- **容器名称正在使用：** 启动脚本使用 `podman run --replace`，因此当您再次启动时，现有容器会被替换。要手动清理：`podman rm -f openclaw`。
- **作为 openclaw 运行时未找到脚本：** 确保运行了 `setup-podman.sh`，以便 `run-openclaw-podman.sh` 被复制到 openclaw 的 home（例如 `/home/openclaw/run-openclaw-podman.sh`）。
- **未找到 Quadlet 服务或启动失败：** 编辑 `.container` 文件后运行 `sudo systemctl --machine openclaw@ --user daemon-reload`。Quadlet 需要 cgroups v2：`podman info --format '{{.Host.CgroupsVersion}}'` 应显示 `2`。

## 可选：作为您自己的用户运行

要以普通用户身份运行网关（无专用的 openclaw 用户）：构建镜像，创建带有 `OPENCLAW_GATEWAY_TOKEN` 的 `~/.openclaw/.env`，并使用 `--userns=keep-id` 运行容器并挂载到您的 `~/.openclaw`。启动脚本是为 openclaw-user flow 设计的；对于 single-user setup，您可以改为手动运行脚本中的 `podman run` 命令，将 config 和 workspace 指向您的 home。大多数用户推荐：使用 `setup-podman.sh` 并作为 openclaw 用户运行，以便 config 和 process 被隔离。