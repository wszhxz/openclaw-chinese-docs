---
summary: "Run OpenClaw Gateway on exe.dev (VM + HTTPS proxy) for remote access"
read_when:
  - You want a cheap always-on Linux host for the Gateway
  - You want remote Control UI access without running your own VPS
title: "exe.dev"
---
# exe.dev

目标：在 exe.dev 虚拟机上运行 OpenClaw 网关，并可通过以下地址从您的笔记本电脑访问：`https://<vm-name>.exe.xyz`

本页面假设使用 exe.dev 的默认 **exeuntu** 镜像。如果您选择了其他发行版，请相应映射软件包。

## 新手快速入门路径

1. [https://exe.new/openclaw](https://exe.new/openclaw)
2. 根据需要填写您的认证密钥/令牌
3. 点击您虚拟机旁边的“Agent”，然后等待……
4. ???
5. 获益

## 您需要准备的内容

- exe.dev 账户  
- `ssh exe.dev` 对 [exe.dev](https://exe.dev) 虚拟机的访问权限（可选）

## 使用 Shelley 自动安装

Shelley 是 [exe.dev](https://exe.dev) 提供的代理程序，可通过我们的提示语（prompt）即时安装 OpenClaw。所用提示语如下：

```
Set up OpenClaw (https://docs.openclaw.ai/install) on this VM. Use the non-interactive and accept-risk flags for openclaw onboarding. Add the supplied auth or token as needed. Configure nginx to forward from the default port 18789 to the root location on the default enabled site config, making sure to enable Websocket support. Pairing is done by "openclaw devices list" and "openclaw devices approve <request id>". Make sure the dashboard shows that OpenClaw's health is OK. exe.dev handles forwarding from port 8000 to port 80/443 and HTTPS for us, so the final "reachable" should be <vm-name>.exe.xyz, without port specification.
```

## 手动安装

## 1) 创建虚拟机

在您的设备上执行：

```bash
ssh exe.dev new
```

然后连接：

```bash
ssh <vm-name>.exe.xyz
```

提示：请将此虚拟机保持为**有状态（stateful）**。OpenClaw 将状态数据存储在 `~/.openclaw/` 和 `~/.openclaw/workspace/` 目录下。

## 2) 安装依赖项（在虚拟机中执行）

```bash
sudo apt-get update
sudo apt-get install -y git curl jq ca-certificates openssl
```

## 3) 安装 OpenClaw

运行 OpenClaw 安装脚本：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

## 4) 配置 nginx，将 OpenClaw 反向代理至端口 8000

编辑 `/etc/nginx/sites-enabled/default`，内容如下：

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

访问 `https://<vm-name>.exe.xyz/`（参见初始设置过程中控制界面 Control UI 的输出）。如果提示认证，请将虚拟机中 `gateway.auth.token` 文件内的令牌粘贴进去（可通过 `openclaw config get gateway.auth.token` 命令获取，或使用 `openclaw doctor --generate-gateway-token` 生成一个新令牌）。使用 `openclaw devices list` 和 `openclaw devices approve <requestId>` 批准设备。如有疑问，请直接在浏览器中使用 Shelley！

## 远程访问

远程访问由 [exe.dev](https://exe.dev) 的身份验证机制处理。默认情况下，来自端口 8000 的 HTTP 流量将通过邮箱认证方式转发至 `https://<vm-name>.exe.xyz`。

## 更新

```bash
npm i -g openclaw@latest
openclaw doctor
openclaw gateway restart
openclaw health
```

指南：[更新](/install/updating)