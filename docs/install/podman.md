---
summary: "Run OpenClaw in a rootless Podman container"
read_when:
  - You want a containerized gateway with Podman instead of Docker
title: "Podman"
---
# Podman

在 **rootless** Podman 容器中运行 OpenClaw 网关。使用与 Docker 相同的镜像（从仓库构建 [Dockerfile](https://github.com/openclaw/openclaw/blob/main/Dockerfile)）。

## 要求

- Podman (rootless)
- Sudo 用于一次性设置（创建用户，构建镜像）

## 快速开始

**1. 一次性设置**（从仓库根目录；创建用户，构建镜像，安装启动脚本）：

```bash
./setup-podman.sh
```

这还会创建一个最小的 `~openclaw/.openclaw/openclaw.json`（设置 `gateway.mode="local"`），以便网关可以在不运行向导的情况下启动。

默认情况下，容器不会作为 systemd 服务安装，你需要手动启动它（见下文）。对于具有自动启动和重启功能的生产环境设置，请将其作为 systemd Quadlet 用户服务安装：

```bash
./setup-podman.sh --quadlet
```

（或者设置 `OPENCLAW_PODMAN_QUADLET=1`；使用 `--container` 仅安装容器和启动脚本。）

**2. 启动网关**（手动，用于快速测试）：

```bash
./scripts/run-openclaw-podman.sh launch
```

**3. 入门向导**（例如，添加频道或提供商）：

```bash
./scripts/run-openclaw-podman.sh launch setup
```

然后打开 `http://127.0.0.1:18789/` 并使用 `~openclaw/.openclaw/.env` 中的令牌（或设置打印的值）。

## Systemd (Quadlet, 可选)

如果你运行了 `./setup-podman.sh --quadlet`（或 `OPENCLAW_PODMAN_QUADLET=1`），会安装一个 [Podman Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) 单元，使网关作为 systemd 用户服务为 openclaw 用户运行。在设置结束时，服务会被启用并启动。

- **启动:** `sudo systemctl --machine openclaw@ --user start openclaw.service`
- **停止:** `sudo systemctl --machine openclaw@ --user stop openclaw.service`
- **状态:** `sudo systemctl --machine openclaw@ --user status openclaw.service`
- **日志:** `sudo journalctl --machine openclaw@ --user -u openclaw.service -f`

quadlet 文件位于 `~openclaw/.config/containers/systemd/openclaw.container`。要更改端口或环境变量，请编辑该文件（或它引用的 `.env`），然后 `sudo systemctl --machine openclaw@ --user daemon-reload` 并重启服务。在启动时，如果为 openclaw 启用了 lingering，则服务会自动启动（当可用时，setup 会执行此操作）。

要在初始设置未使用 quadlet 的情况下添加 quadlet，请重新运行：`./setup-podman.sh --quadlet`。

## openclaw 用户（非登录）

`setup-podman.sh` 创建了一个专用系统用户 `openclaw`：

- **Shell:** `nologin` — 无交互式登录；减少攻击面。
- **主目录:** 例如 `/home/openclaw` — 包含 `~/.openclaw`（配置，工作区）和启动脚本 `run-openclaw-podman.sh`。
- **Rootless Podman:** 该用户必须有一个 **subuid** 和 **subgid** 范围。许多发行版在创建用户时会自动分配这些。如果 setup 打印警告，请向 `/etc/subuid` 和 `/etc/subgid` 添加行：

  ```text
  openclaw:100000:65536
  ```

  然后以该用户身份启动网关（例如，从 cron 或 systemd）：

  ```bash
  sudo -u openclaw /home/openclaw/run-openclaw-podman.sh
  sudo -u openclaw /home/openclaw/run-openclaw-podman.sh setup
  ```

- **配置:** 仅 `openclaw` 和 root 可以访问 `/home/openclaw/.openclaw`。要编辑配置：在网关运行后使用控制 UI，或 `sudo -u openclaw $EDITOR /home/openclaw/.openclaw/openclaw.json`。

## 环境和配置

- **令牌:** 存储在 `~openclaw/.openclaw/.env` 中作为 `OPENCLAW_GATEWAY_TOKEN`。`setup-podman.sh` 和 `run-openclaw-podman.sh` 如果缺失则生成它（使用 `openssl`，`python3` 或 `od`）。
- **可选:** 在该 `.env` 中，你可以设置提供商密钥（例如 `GROQ_API_KEY`，`OLLAMA_API_KEY`）和其他 OpenClaw 环境变量。
- **主机端口:** 默认情况下，脚本映射 `18789`（网关）和 `18790`（桥接）。通过启动时指定 `OPENCLAW_PODMAN_GATEWAY_HOST_PORT` 和 `OPENCLAW_PODMAN_BRIDGE_HOST_PORT` 来覆盖 **主机** 端口映射。
- **路径:** 主机配置和工作区默认为 `~openclaw/.openclaw` 和 `~openclaw/.openclaw/workspace`。通过启动脚本使用的主机路径来覆盖这些路径，使用 `OPENCLAW_CONFIG_DIR` 和 `OPENCLAW_WORKSPACE_DIR`。

## 有用的命令

- **日志:** 使用 quadlet: `sudo journalctl --machine openclaw@ --user -u openclaw.service -f`。使用脚本: `sudo -u openclaw podman logs -f openclaw`
- **停止:** 使用 quadlet: `sudo systemctl --machine openclaw@ --user stop openclaw.service`。使用脚本: `sudo -u openclaw podman stop openclaw`
- **再次启动:** 使用 quadlet: `sudo systemctl --machine openclaw@ --user start openclaw.service`。使用脚本: 重新运行启动脚本或 `podman start openclaw`
- **删除容器:** `sudo -u openclaw podman rm -f openclaw` — 主机上的配置和工作区将被保留

## 故障排除

- **权限被拒绝 (EACCES) 对于配置或 auth-profiles:** 容器默认为 `--userns=keep-id` 并以与运行脚本的主机用户相同的 uid/gid 运行。确保你的主机 `OPENCLAW_CONFIG_DIR` 和 `OPENCLAW_WORKSPACE_DIR` 由该用户拥有。
- **网关启动被阻止（缺少 `gateway.mode=local`）:** 确保 `~openclaw/.openclaw/openclaw.json` 存在并设置了 `gateway.mode="local"`。`setup-podman.sh` 如果缺失则创建此文件。
- **Rootless Podman 对于用户 openclaw 失败:** 检查 `/etc/subuid` 和 `/etc/subgid` 是否包含 `openclaw` 的行（例如 `openclaw:100000:65536`）。如果缺失，请添加并重启。
- **容器名称已被使用:** 启动脚本使用 `podman run --replace`，因此当你再次启动时，现有容器将被替换。要手动清理: `podman rm -f openclaw`。
- **运行为 openclaw 时找不到脚本:** 确保已运行 `setup-podman.sh`，以便将 `run-openclaw-podman.sh` 复制到 openclaw 的主目录（例如 `/home/openclaw/run-openclaw-podman.sh`）。
- **Quadlet 服务未找到或无法启动:** 编辑 `.container` 文件后运行 `sudo systemctl --machine openclaw@ --user daemon-reload`。Quadlet 需要 cgroups v2: `podman info --format '{{.Host.CgroupsVersion}}'` 应显示 `2`。

## 可选：以你自己的用户身份运行

要以你的普通用户身份运行网关（无需专用 openclaw 用户）：构建镜像，使用 `OPENCLAW_GATEWAY_TOKEN` 创建 `~/.openclaw/.env`，并使用 `--userns=keep-id` 和挂载到你的 `~/.openclaw` 运行容器。启动脚本是为 openclaw 用户流程设计的；对于单用户设置，你可以手动运行脚本中的 `podman run` 命令，将配置和工作区指向你的主目录。推荐大多数用户使用 `setup-podman.sh` 并以 openclaw 用户身份运行，以便隔离配置和进程。