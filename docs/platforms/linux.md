---
summary: "Linux support + companion app status"
read_when:
  - Looking for Linux companion app status
  - Planning platform coverage or contributions
title: "Linux App"
---
# Linux 应用

网关在 Linux 上完全支持。**Node 是推荐的运行时环境**。
Bun 不推荐用于网关（WhatsApp/Telegram 存在错误）。

原生 Linux 伴侣应用正在计划中。如果您想帮助构建一个，欢迎贡献。

## 初学者快速路径（VPS）

1. 安装 Node 22+
2. `npm i -g openclaw@latest`
3. `openclaw onboard --install-daemon`
4. 从您的笔记本电脑：`ssh -N -L 18789:12.7.0.0.1:18789 <user>@<host>`
5. 打开 `http://127.0.0.1:18789/` 并粘贴您的令牌

分步 VPS 指南：[exe.dev](/platforms/exe-dev)

## 安装

- [入门指南](/start/getting-started)
- [安装与更新](/install/updating)
- 可选流程：[Bun（实验性）](/install/bun)，[Nix](/install/nix)，[Docker](/install/docker)

## 网关

- [网关运行手册](/gateway)
- [配置](/gateway/configuration)

## 网关服务安装（CLI）

使用以下任一命令：

```
openclaw onboard --install-daemon
```

或：

```
openclaw gateway install
```

或：

```
openclaw configure
```

在提示时选择 **网关服务**。

修复/迁移：

```
openclaw doctor
```

## 系统控制（systemd 用户单元）

OpenClaw 默认安装一个 systemd **用户**服务。使用 **系统** 服务用于共享或始终运行的服务器。完整的单元示例和指导信息位于 [网关运行手册](/gateway)。

最小化设置：

创建 `~/.config/systemd/user/openclaw-gateway[-<profile>].service`：

```
[Unit]
Description=OpenClaw 网关（配置文件：<profile>, 版本：<version>）
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

启用服务：

```
systemctl --user enable --now openclaw-gateway[-<profile>].service
```