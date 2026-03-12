---
summary: "Run OpenClaw in a rootless Podman container"
read_when:
  - You want a containerized gateway with Podman instead of Docker
title: "Podman"
---
# Podman

以**无根（rootless）** 方式在 Podman 容器中运行 OpenClaw 网关。所用镜像与 Docker 相同（构建自仓库中的 [Dockerfile](https://github.com/openclaw/openclaw/blob/main/Dockerfile)）。

## 要求

- Podman（无根模式）
- Sudo 权限用于一次性初始化（创建用户、构建镜像）

## 快速开始

**1. 一次性初始化**（从仓库根目录执行；将创建用户、构建镜像并安装启动脚本）：

```bash
./setup-podman.sh
```

此步骤还会创建一个最小化的 `~openclaw/.openclaw/openclaw.json`（设置 `gateway.mode="local"`），使网关可在不运行向导的情况下直接启动。

默认情况下，容器**不会**被安装为 systemd 服务，需手动启动（见下文）。如需生产级部署（支持自动启动与崩溃重启），请改用 systemd Quadlet 用户服务方式安装：

```bash
./setup-podman.sh --quadlet
```

（或设置 `OPENCLAW_PODMAN_QUADLET=1`；使用 `--container` 仅安装容器和启动脚本。）

可选的构建时环境变量（在运行 `setup-podman.sh` 前设置）：

- `OPENCLAW_DOCKER_APT_PACKAGES` —— 在镜像构建过程中安装额外的 apt 包
- `OPENCLAW_EXTENSIONS` —— 预安装扩展依赖项（空格分隔的扩展名列表，例如 `diagnostics-otel matrix`）

**2. 启动网关**（手动方式，适用于快速冒烟测试）：

```bash
./scripts/run-openclaw-podman.sh launch
```

**3. 入门向导**（例如添加频道或提供方）：

```bash
./scripts/run-openclaw-podman.sh launch setup
```

然后打开 `http://127.0.0.1:18789/`，并使用 `~openclaw/.openclaw/.env` 中的令牌（或初始化脚本输出的令牌）。

## systemd（Quadlet，可选）

若已运行 `./setup-podman.sh --quadlet`（或 `OPENCLAW_PODMAN_QUADLET=1`），则会安装一个 [Podman Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) 单元，使网关作为 `openclaw` 用户的 systemd 用户服务运行。该服务将在初始化结束时被启用并启动。

- **启动：** `sudo systemctl --machine openclaw@ --user start openclaw.service`
- **停止：** `sudo systemctl --machine openclaw@ --user stop openclaw.service`
- **状态：** `sudo systemctl --machine openclaw@ --user status openclaw.service`
- **日志：** `sudo journalctl --machine openclaw@ --user -u openclaw.service -f`

Quadlet 文件位于 `~openclaw/.config/containers/systemd/openclaw.container`。如需修改端口或环境变量，请编辑该文件（或其引用的 `.env`），然后执行 `sudo systemctl --machine openclaw@ --user daemon-reload` 并重启服务。若为 `openclaw` 用户启用了 lingering（初始化脚本在 `loginctl` 可用时会自动完成此操作），则系统启动时服务将自动运行。

若初始部署未使用 Quadlet，后续需补加 Quadlet 支持，请重新运行：`./setup-podman.sh --quadlet`。

## `openclaw` 用户（非登录型）

`setup-podman.sh` 将创建一个专用的系统用户 `openclaw`：

- **Shell：** `nologin` —— 禁止交互式登录，降低攻击面。
- **主目录：** 例如 `/home/openclaw` —— 存放 `~/.openclaw`（配置与工作区）及启动脚本 `run-openclaw-podman.sh`。
- **无根 Podman：** 该用户必须拥有 **subuid** 和 **subgid** 范围。多数发行版在创建用户时会自动分配这些范围。若初始化脚本打印警告，请向 `/etc/subuid` 和 `/etc/subgid` 添加如下行：

  ```text
  openclaw:100000:65536
  ```

  然后以该用户身份启动网关（例如通过 cron 或 systemd）：

  ```bash
  sudo -u openclaw /home/openclaw/run-openclaw-podman.sh
  sudo -u openclaw /home/openclaw/run-openclaw-podman.sh setup
  ```

- **配置权限：** 仅 `openclaw` 和 root 可访问 `/home/openclaw/.openclaw`。如需编辑配置，请在网关运行后使用控制界面，或执行 `sudo -u openclaw $EDITOR /home/openclaw/.openclaw/openclaw.json`。

## 环境与配置

- **令牌（Token）：** 存储于 `~openclaw/.openclaw/.env` 中，键名为 `OPENCLAW_GATEWAY_TOKEN`。若缺失，`setup-podman.sh` 和 `run-openclaw-podman.sh` 将自动生成（使用 `openssl`、`python3` 或 `od`）。
- **可选配置：** 在该 `.env` 中，可设置提供方密钥（例如 `GROQ_API_KEY`、`OLLAMA_API_KEY`）及其他 OpenClaw 环境变量。
- **主机端口：** 默认情况下，脚本将映射 `18789`（网关）和 `18790`（桥接）。启动时可通过 `OPENCLAW_PODMAN_GATEWAY_HOST_PORT` 和 `OPENCLAW_PODMAN_BRIDGE_HOST_PORT` 覆盖**主机端口**映射。
- **网关绑定地址：** 默认情况下，`run-openclaw-podman.sh` 以 `--bind loopback` 启动网关，确保本地安全访问。如需在局域网内暴露服务，请设置 `OPENCLAW_GATEWAY_BIND=lan` 并在 `openclaw.json` 中配置 `gateway.controlUi.allowedOrigins`（或显式启用 host-header 回退机制）。
- **路径：** 主机上的配置与工作区默认路径为 `~openclaw/.openclaw` 和 `~openclaw/.openclaw/workspace`。可通过 `OPENCLAW_CONFIG_DIR` 和 `OPENCLAW_WORKSPACE_DIR` 覆盖启动脚本所用的主机路径。

## 存储模型

- **持久化主机数据：** `OPENCLAW_CONFIG_DIR` 和 `OPENCLAW_WORKSPACE_DIR` 将被绑定挂载至容器内，并在主机上保留状态。
- **临时沙箱 tmpfs：** 若启用 `agents.defaults.sandbox`，工具沙箱容器将把 `tmpfs` 挂载至 `/tmp`、`/var/tmp` 和 `/run`。这些路径基于内存，随沙箱容器销毁而消失；顶层 Podman 容器本身不添加任何 tmpfs 挂载。
- **磁盘增长热点路径：** 需重点关注的主要路径包括 `media/`、`agents/<agentId>/sessions/sessions.json`、转录 JSONL 文件、`cron/runs/*.jsonl`，以及 `/tmp/openclaw/` 下的滚动日志文件（或您配置的 `logging.file`）。

`setup-podman.sh` 当前会将镜像 tar 包暂存于私有临时目录，并在初始化过程中打印所选基础目录。对于非 root 用户运行场景，仅当该基础目录安全可用时才接受 `TMPDIR`；否则依次回退至 `/var/tmp` 和 `/tmp`。保存的 tar 包保持所有者独占权限，并流式写入目标用户的 `podman load`，因此调用方私有临时目录不会阻碍初始化流程。

## 实用命令

- **日志：** 使用 Quadlet：`sudo journalctl --machine openclaw@ --user -u openclaw.service -f`；使用脚本：`sudo -u openclaw podman logs -f openclaw`
- **停止：** 使用 Quadlet：`sudo systemctl --machine openclaw@ --user stop openclaw.service`；使用脚本：`sudo -u openclaw podman stop openclaw`
- **再次启动：** 使用 Quadlet：`sudo systemctl --machine openclaw@ --user start openclaw.service`；使用脚本：重新运行启动脚本或执行 `podman start openclaw`
- **删除容器：** `sudo -u openclaw podman rm -f openclaw` —— 主机上的配置与工作区将被保留

## 故障排除

- **配置或认证配置文件权限拒绝（EACCES）：** 容器默认以 `--userns=keep-id` 运行，且 UID/GID 与执行脚本的宿主机用户一致。请确保宿主机上的 `OPENCLAW_CONFIG_DIR` 和 `OPENCLAW_WORKSPACE_DIR` 归属该用户。
- **网关启动被阻塞（缺少 `gateway.mode=local`）：** 请确认 `~openclaw/.openclaw/openclaw.json` 存在且设置了 `gateway.mode="local"`。若缺失，`setup-podman.sh` 将自动创建该文件。
- **`openclaw` 用户无法运行无根 Podman：** 请检查 `/etc/subuid` 和 `/etc/subgid` 是否包含针对 `openclaw` 的条目（例如 `openclaw:100000:65536`）。若缺失，请添加并重启。
- **容器名称已被占用：** 启动脚本使用 `podman run --replace`，因此再次启动时将覆盖现有容器。如需手动清理：`podman rm -f openclaw`。
- **以 `openclaw` 用户运行时脚本未找到：** 请确保已执行 `setup-podman.sh`，使 `run-openclaw-podman.sh` 已复制至 `openclaw` 用户主目录（例如 `/home/openclaw/run-openclaw-podman.sh`）。
- **Quadlet 服务未找到或启动失败：** 编辑 `.container` 文件后，请运行 `sudo systemctl --machine openclaw@ --user daemon-reload`。Quadlet 要求 cgroups v2：`podman info --format '{{.Host.CgroupsVersion}}'` 应显示 `2`。

## 可选：以您自己的用户身份运行

如需以普通用户身份（而非专用 `openclaw` 用户）运行网关：请先构建镜像，创建含 `OPENCLAW_GATEWAY_TOKEN` 的 `~/.openclaw/.env`，再使用 `--userns=keep-id` 及挂载到您 `~/.openclaw` 的参数运行容器。启动脚本专为 `openclaw` 用户流程设计；对于单用户场景，您可手动运行脚本中的 `podman run` 命令，并将配置与工作区指向您的主目录。**推荐大多数用户采用 `setup-podman.sh` 方式，以 `openclaw` 用户身份运行，从而实现配置与进程的完全隔离。**