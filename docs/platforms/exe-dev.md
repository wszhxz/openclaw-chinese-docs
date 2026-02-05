---
summary: "Run OpenClaw Gateway on exe.dev (VM + HTTPS proxy) for remote access"
read_when:
  - You want a cheap always-on Linux host for the Gateway
  - You want remote Control UI access without running your own VPS
title: "exe.dev"
---
# exe.dev

目标：在 exe.dev 虚拟机上运行的 OpenClaw 网关，可通过您的笔记本电脑访问：`https://<vm-name>.exe.xyz`

本页面假设使用 exe.dev 的默认 **exeuntu** 镜像。如果您选择了不同的发行版，请相应映射软件包。

## 初学者快速路径

1. [https://exe.new/openclaw](https://exe.new/openclaw)
2. 根据需要填写您的认证密钥/令牌
3. 点击虚拟机旁边的"Agent"，然后等待...
4. ???
5. 完成

## 您需要准备

- exe.dev 账户
- `ssh exe.dev` 访问 [exe.dev](https://exe.dev) 虚拟机的权限（可选）

## 使用 Shelley 自动安装

Shelley，[exe.dev](https://exe.dev) 的代理，可以使用我们的提示立即安装 OpenClaw。
使用的提示如下所示：

```
Set up OpenClaw (https://docs.openclaw.ai/install) on this VM. Use the non-interactive and accept-risk flags for openclaw onboarding. Add the supplied auth or token as needed. Configure nginx to forward from the default port 18789 to the root location on the default enabled site config, making sure to enable Websocket support. Pairing is done by "openclaw devices list" and "openclaw device approve <request id>". Make sure the dashboard shows that OpenClaw's health is OK. exe.dev handles forwarding from port 8000 to port 80/443 and HTTPS for us, so the final "reachable" should be <vm-name>.exe.xyz, without port specification.
```

## 手动安装

## 1) 创建虚拟机

从您的设备执行：

```bash
ssh exe.dev new
```

然后连接：

```bash
ssh <vm-name>.exe.xyz
```

提示：保持此虚拟机为**有状态**。OpenClaw 在 `~/.openclaw/` 和 `~/.openclaw/workspace/` 下存储状态。

## 2) 安装前置依赖（在虚拟机上）

```bash
sudo apt-get update
sudo apt-get install -y git curl jq ca-certificates openssl
```

## 3) 安装 OpenClaw

运行 OpenClaw 安装脚本：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

## 4) 设置 nginx 以将 OpenClaw 代理到端口 8000

编辑 `/etc/nginx/sites-enabled/default`，内容为

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

访问 `https://<vm-name>.exe.xyz/?token=YOUR-TOKEN-FROM-TERMINAL`（参见入门过程中的控制界面输出）。使用 `openclaw devices list` 和 `openclaw devices approve <requestId>` 批准设备。如有疑问，请使用浏览器中的 Shelley！

## 远程访问

远程访问由 [exe.dev](https://exe.dev) 的认证处理。默认情况下，来自端口 8000 的 HTTP 流量通过邮件认证转发到 `https://<vm-name>.exe.xyz`。

## 更新

```bash
npm i -g openclaw@latest
openclaw doctor
openclaw gateway restart
openclaw health
```

指南：[更新](/install/updating)