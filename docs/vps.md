---
summary: "VPS hosting hub for OpenClaw (Oracle/Fly/Hetzner/GCP/exe.dev)"
read_when:
  - You want to run the Gateway in the cloud
  - You need a quick map of VPS/hosting guides
title: "VPS Hosting"
---
# VPS 托管

此中心链接到支持的 VPS/托管指南，并从高层解释云部署的工作原理。

## 选择提供商

- **Railway**（一键 + 浏览器设置）：[Railway](/install/railway)
- **Northflank**（一键 + 浏览器设置）：[Northflank](/install/northflank)
- **Oracle Cloud (Always Free)**：[Oracle](/platforms/oracle) — $0/月（Always Free，ARM；容量/注册可能不稳定）
- **Fly.io**：[Fly.io](/install/fly)
- **Hetzner (Docker)**：[Hetzner](/install/hetzner)
- **GCP (Compute Engine)**：[GCP](/install/gcp)
- **exe.dev**（VM + HTTPS 代理）：[exe.dev](/install/exe-dev)
- **AWS (EC2/Lightsail/free tier)**：也能很好地工作。视频指南：
  [https://x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)

## 云设置工作原理

- **Gateway 运行在 VPS 上**并拥有状态 + 工作区。
- 您可以通过 **Control UI** 或 **Tailscale/SSH** 从笔记本电脑/手机连接。
- 将 VPS 视为 source of truth 并 **备份** 状态 + 工作区。
- 安全默认值：保持 Gateway 在 loopback 上并通过 SSH 隧道或 Tailscale Serve 访问它。
  如果您绑定到 `lan`/`tailnet`，需要 `gateway.auth.token` 或 `gateway.auth.password`。

远程访问：[Gateway 远程](/gateway/remote)  
平台中心：[Platforms](/platforms)

## VPS 上的共享公司代理

当用户在同一个信任边界内（例如一个公司团队），且代理仅用于业务时，这是一个有效的设置。

- 将其保留在独立的运行时中（VPS/VM/容器 + 专用的 OS 用户/账户）。
- 不要将该运行时登录到个人 Apple/Google 账户或个人浏览器/密码管理器配置文件中。
- 如果用户之间相互敌对，请按 gateway/host/OS 用户进行拆分。

安全模型详情：[Security](/gateway/security)

## 在 VPS 上使用 Nodes

您可以将 Gateway 保留在云端，并在本地设备（Mac/iOS/Android/headless）上配对 **nodes**。Nodes 提供本地屏幕/摄像头/画布和 `system.run` 功能，同时 Gateway 保持在云端。

文档：[Nodes](/nodes), [Nodes CLI](/cli/nodes)

## 小型 VM 和 ARM 主机的启动调优

如果在低功耗 VM（或 ARM 主机）上感觉 CLI 命令缓慢，请启用 Node 的模块编译缓存：

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE` 可缩短重复命令的启动时间。
- `OPENCLAW_NO_RESPAWN=1` 避免来自自重生路径的额外启动开销。
- 首次命令运行会预热缓存；后续运行速度更快。
- 关于 Raspberry Pi 的具体信息，请参阅 [Raspberry Pi](/platforms/raspberry-pi)。

### systemd 调优清单（可选）

对于使用 `systemd` 的 VM 主机，请考虑：

- 添加服务环境变量以稳定启动路径：
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- 保持重启行为明确：
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- 优先为状态/缓存路径使用 SSD 支持的磁盘，以减少随机 I/O 冷启动惩罚。

示例：

```bash
sudo systemctl edit openclaw
```

```ini
[Service]
Environment=OPENCLAW_NO_RESPAWN=1
Environment=NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
Restart=always
RestartSec=2
TimeoutStartSec=90
```

`Restart=` 策略如何帮助自动恢复：
[systemd 可以自动化服务恢复](https://www.redhat.com/en/blog/systemd-automate-recovery)。