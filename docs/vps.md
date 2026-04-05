---
summary: "Run OpenClaw on a Linux server or cloud VPS — provider picker, architecture, and tuning"
read_when:
  - You want to run the Gateway on a Linux server or cloud VPS
  - You need a quick map of hosting guides
  - You want generic Linux server tuning for OpenClaw
title: "Linux Server"
sidebarTitle: "Linux Server"
---
# Linux 服务器

在任何 Linux 服务器或云 VPS 上运行 OpenClaw Gateway。本页面帮助您选择提供商，解释云部署的工作原理，并涵盖适用于各地的通用 Linux 调优。

## 选择提供商

<CardGroup cols={2}>
  <Card title="Railway" href="/install/railway">一键式，浏览器设置</Card>
  <Card title="Northflank" href="/install/northflank">一键式，浏览器设置</Card>
  <Card title="DigitalOcean" href="/install/digitalocean">简单的付费 VPS</Card>
  <Card title="Oracle Cloud" href="/install/oracle">永久免费 ARM 层级</Card>
  <Card title="Fly.io" href="/install/fly">Fly Machines</Card>
  <Card title="Hetzner" href="/install/hetzner">Hetzner VPS 上的 Docker</Card>
  <Card title="GCP" href="/install/gcp">Compute Engine</Card>
  <Card title="Azure" href="/install/azure">Linux VM</Card>
  <Card title="exe.dev" href="/install/exe-dev">带 HTTPS 代理的 VM</Card>
  <Card title="Raspberry Pi" href="/install/raspberry-pi">ARM 自托管</Card>
</CardGroup>

**AWS (EC2 / Lightsail / free tier)** 也能很好地工作。
社区视频指南可在以下地址找到
[x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)
（社区资源 -- 可能不再可用）。

## 云设置工作原理

- **Gateway 在 VPS 上运行** 并拥有状态 + 工作区。
- 您通过 **Control UI** 或 **Tailscale/SSH** 从笔记本电脑或手机连接。
- 将 VPS 视为真理来源，并定期 **备份** 状态 + 工作区。
- 安全默认值：保持 Gateway 在回环接口上，并通过 SSH 隧道或 Tailscale Serve 访问。
  如果您绑定到 `lan` 或 `tailnet`，请要求 `gateway.auth.token` 或 `gateway.auth.password`。

相关页面：[Gateway 远程访问](/gateway/remote), [平台中心](/platforms)。

## VPS 上的共享公司代理

当所有用户都在同一信任边界内且代理仅用于业务时，为团队运行单个代理是有效的设置。

- 将其保留在专用运行时中（VPS/VM/容器 + 专用 OS 用户/账户）。
- 不要将该运行时登录到个人 Apple/Google 账户或个人浏览器/密码管理器配置文件中。
- 如果用户之间存在敌对关系，请按网关/主机/OS 用户进行拆分。

安全模型详情：[安全](/gateway/security)。

## 配合 VPS 使用节点

您可以将 Gateway 保留在云端，并在本地设备（Mac/iOS/Android/headless）上配对 **节点**。节点提供本地屏幕/摄像头/画布和 `system.run` 功能，而 Gateway 保持在云端。

文档：[节点](/nodes), [节点 CLI](/cli/nodes)。

## 小型 VM 和 ARM 主机的启动调优

如果在低功率 VM（或 ARM 主机）上感觉 CLI 命令缓慢，请启用 Node 的模块编译缓存：

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE` 可改善重复命令的启动时间。
- `OPENCLAW_NO_RESPAWN=1` 避免了来自自我重新生成路径的额外启动开销。
- 首次命令运行会预热缓存；后续运行速度更快。
- 有关 Raspberry Pi 的具体信息，请参阅 [Raspberry Pi](/install/raspberry-pi)。

### systemd 调优检查清单（可选）

对于使用 `systemd` 的 VM 主机，请考虑：

- 添加服务环境变量以获取稳定的启动路径：
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- 明确重启行为：
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- 优先使用 SSD 支持的磁盘作为状态/缓存路径，以减少随机 I/O 冷启动惩罚。

对于标准的 `openclaw onboard --install-daemon` 路径，编辑用户单元：

```bash
systemctl --user edit openclaw-gateway.service
```

```ini
[Service]
Environment=OPENCLAW_NO_RESPAWN=1
Environment=NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
Restart=always
RestartSec=2
TimeoutStartSec=90
```

如果您故意安装了系统单元而不是用户单元，请通过 `sudo systemctl edit openclaw-gateway.service` 编辑 `openclaw-gateway.service`。

`Restart=` 策略如何帮助自动恢复：
[systemd 可以自动化服务恢复](https://www.redhat.com/en/blog/systemd-automate-recovery)。