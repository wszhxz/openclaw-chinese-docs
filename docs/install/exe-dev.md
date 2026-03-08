---
summary: "Run OpenClaw Gateway on exe.dev (VM + HTTPS proxy) for remote access"
read_when:
  - You want a cheap always-on Linux host for the Gateway
  - You want remote Control UI access without running your own VPS
title: "exe.dev"
---
# exe.dev

目标：在 exe.dev VM 上运行 OpenClaw Gateway，可通过以下方式从您的笔记本电脑访问：`https://<vm-name>.exe.xyz`

本页面假设使用 exe.dev 的默认 **exeuntu** 镜像。如果您选择了不同的发行版，请相应地映射软件包。

## 初学者快速路径

1. [https://exe.new/openclaw](https://exe.new/openclaw)
2. 根据需要填写您的 auth key/token
3. 点击 VM 旁边的 "Agent"，然后等待...
4. ???
5. 获利

## 您需要什么

- exe.dev 账户
- `ssh exe.dev` 访问 [exe.dev](https://exe.dev) 虚拟机（可选）

## 使用 Shelley 自动安装

Shelley，[exe.dev](https://exe.dev) 的 agent，可以使用我们的 prompt 立即安装 OpenClaw。使用的 prompt 如下：

```
Set up OpenClaw (https://docs.openclaw.ai/install) on this VM. Use the non-interactive and accept-risk flags for openclaw onboarding. Add the supplied auth or token as needed. Configure nginx to forward from the default port 18789 to the root location on the default enabled site config, making sure to enable Websocket support. Pairing is done by "openclaw devices list" and "openclaw devices approve <request id>". Make sure the dashboard shows that OpenClaw's health is OK. exe.dev handles forwarding from port 8000 to port 80/443 and HTTPS for us, so the final "reachable" should be <vm-name>.exe.xyz, without port specification.
```

## 手动安装

## 1) 创建 VM

从您的设备：

```bash
ssh exe.dev new
```

然后连接：

```bash
ssh <vm-name>.exe.xyz
```

提示：保持此 VM 为 **stateful**。OpenClaw 将状态存储在 `~/.openclaw/` 和 `~/.openclaw/workspace/` 下。

## 2) 安装先决条件（在 VM 上）

```bash
sudo apt-get update
sudo apt-get install -y git curl jq ca-certificates openssl
```

## 3) 安装 OpenClaw

运行 OpenClaw 安装脚本：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

## 4) 设置 nginx 将 OpenClaw 代理到端口 8000

使用以下内容编辑 `/etc/nginx/sites-enabled/default`：

```
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    listen 8000;
    listen [::]:8000;

    server_name _;

    location / {
        proxy_pass http://127.0.0.1:18789;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings for long-lived connections
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

## 5) 访问 OpenClaw 并授予权限

访问 `https://<vm-name>.exe.xyz/`（参见 onboarding 中的 Control UI 输出）。如果提示进行 auth，请粘贴 VM 上来自 `gateway.auth.token` 的 token（使用 `openclaw config get gateway.auth.token` 检索，或使用 `openclaw doctor --generate-gateway-token` 生成一个）。使用 `openclaw devices list` 和 `openclaw devices approve <requestId>` 批准设备。如有疑问，请从浏览器使用 Shelley！

## 远程访问

远程访问由 [exe.dev](https://exe.dev) 的 authentication 处理。默认情况下，来自端口 8000 的 HTTP 流量被转发到 `https://<vm-name>.exe.xyz` 并带有 email auth。

## 更新

```bash
npm i -g openclaw@latest
openclaw doctor
openclaw gateway restart
openclaw health
```

指南：[更新](/install/updating)