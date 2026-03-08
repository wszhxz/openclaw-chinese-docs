---
title: Fly.io
description: Deploy OpenClaw on Fly.io
summary: "Step-by-step Fly.io deployment for OpenClaw with persistent storage and HTTPS"
read_when:
  - Deploying OpenClaw on Fly.io
  - Setting up Fly volumes, secrets, and first-run config
---
# Fly.io 部署

**目标：** 在 [Fly.io](https://fly.io) 机器上运行 OpenClaw Gateway，具备持久存储、自动 HTTPS 以及 Discord/频道访问功能。

## 你需要什么

- 已安装 [flyctl CLI](https://fly.io/docs/hands-on/install-flyctl/)
- Fly.io 账户（免费套餐即可）
- 模型认证：所选模型提供商的 API key
- 频道凭证：Discord bot token、Telegram token 等

## 初学者快速路径

1. 克隆 repo → 自定义 `fly.toml`
2. 创建 app + 卷 → 设置 secrets
3. 使用 `fly deploy` 部署
4. SSH 登录创建配置或使用 Control UI

## 1) 创建 Fly 应用

```bash
# Clone the repo
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# Create a new Fly app (pick your own name)
fly apps create my-openclaw

# Create a persistent volume (1GB is usually enough)
fly volumes create openclaw_data --size 1 --region iad
```

**提示：** 选择离你最近的区域。常见选项：`lhr` (伦敦), `iad` (弗吉尼亚), `sjc` (圣何塞)。

## 2) 配置 fly.toml

编辑 `fly.toml` 以匹配你的应用名称和需求。

**安全注意：** 默认配置会暴露一个公共 URL。对于没有公共 IP 的强化部署，请参阅 [Private Deployment](#private-deployment-hardened) 或使用 `fly.private.toml`。

```toml
app = "my-openclaw"  # Your app name
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  NODE_ENV = "production"
  OPENCLAW_PREFER_PNPM = "1"
  OPENCLAW_STATE_DIR = "/data"
  NODE_OPTIONS = "--max-old-space-size=1536"

[processes]
  app = "node dist/index.js gateway --allow-unconfigured --port 3000 --bind lan"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[vm]]
  size = "shared-cpu-2x"
  memory = "2048mb"

[mounts]
  source = "openclaw_data"
  destination = "/data"
```

**关键设置：**

| 设置                        | 原因                                                                         |
| ------------------------------ | --------------------------------------------------------------------------- |
| `--bind lan`                   | 绑定到 `0.0.0.0` 以便 Fly 的 proxy 可以访问网关                     |
| `--allow-unconfigured`         | 在没有配置文件的情况下启动（之后你会创建一个）                      |
| `internal_port = 3000`         | 必须匹配 `--port 3000` (或 `OPENCLAW_GATEWAY_PORT`) 以用于 Fly 健康检查 |
| `memory = "2048mb"`            | 512MB 太小；推荐 2GB                                         |
| `OPENCLAW_STATE_DIR = "/data"` | 在卷上持久化状态                                                |

## 3) 设置 secrets

```bash
# Required: Gateway token (for non-loopback binding)
fly secrets set OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)

# Model provider API keys
fly secrets set ANTHROPIC_API_KEY=sk-ant-...

# Optional: Other providers
fly secrets set OPENAI_API_KEY=sk-...
fly secrets set GOOGLE_API_KEY=...

# Channel tokens
fly secrets set DISCORD_BOT_TOKEN=MTQ...
```

**注意：**

- 非回环 binds (`--bind lan`) 需要 `OPENCLAW_GATEWAY_TOKEN` 以确保安全。
- 将这些 tokens 视为密码。
- **对于所有 API keys 和 tokens，优先使用环境变量而非配置文件**。这可以将 secrets 保持在 `openclaw.json` 之外，避免意外暴露或记录。

## 4) 部署

```bash
fly deploy
```

首次部署会构建 Docker 镜像（约 2-3 分钟）。后续部署会更快。

部署后，验证：

```bash
fly status
fly logs
```

你应该看到：

```
[gateway] listening on ws://0.0.0.0:3000 (PID xxx)
[discord] logged in to discord as xxx
```

## 5) 创建配置文件

SSH 登录机器以创建正确的配置：

```bash
fly ssh console
```

创建配置目录和文件：

```bash
mkdir -p /data
cat > /data/openclaw.json << 'EOF'
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-6",
        "fallbacks": ["anthropic/claude-sonnet-4-5", "openai/gpt-4o"]
      },
      "maxConcurrent": 4
    },
    "list": [
      {
        "id": "main",
        "default": true
      }
    ]
  },
  "auth": {
    "profiles": {
      "anthropic:default": { "mode": "token", "provider": "anthropic" },
      "openai:default": { "mode": "token", "provider": "openai" }
    }
  },
  "bindings": [
    {
      "agentId": "main",
      "match": { "channel": "discord" }
    }
  ],
  "channels": {
    "discord": {
      "enabled": true,
      "groupPolicy": "allowlist",
      "guilds": {
        "YOUR_GUILD_ID": {
          "channels": { "general": { "allow": true } },
          "requireMention": false
        }
      }
    }
  },
  "gateway": {
    "mode": "local",
    "bind": "auto"
  },
  "meta": {
    "lastTouchedVersion": "2026.1.29"
  }
}
EOF
```

**注意：** 使用 `OPENCLAW_STATE_DIR=/data` 时，配置路径为 `/data/openclaw.json`。

**注意：** Discord token 可以来自：

- 环境变量：`DISCORD_BOT_TOKEN` (推荐用于 secrets)
- 配置文件：`channels.discord.token`

如果使用环境变量，无需将 token 添加到配置中。网关会自动读取 `DISCORD_BOT_TOKEN`。

重启以应用：

```bash
exit
fly machine restart <machine-id>
```

## 6) 访问网关

### Control UI

在浏览器中打开：

```bash
fly open
```

或访问 `https://my-openclaw.fly.dev/`

粘贴你的 gateway token（来自 `OPENCLAW_GATEWAY_TOKEN` 的那个）以进行认证。

### 日志

```bash
fly logs              # Live logs
fly logs --no-tail    # Recent logs
```

### SSH 控制台

```bash
fly ssh console
```

## 故障排除

### "App is not listening on expected address"

网关正在绑定到 `127.0.0.1` 而不是 `0.0.0.0`。

**修复：** 在 `fly.toml` 中的进程命令里添加 `--bind lan`。

### 健康检查失败 / 连接被拒绝

Fly 无法在配置的端口上访问网关。

**修复：** 确保 `internal_port` 匹配网关端口（设置 `--port 3000` 或 `OPENCLAW_GATEWAY_PORT=3000`）。

### OOM / 内存问题

容器不断重启或被杀死。迹象：`SIGABRT`、`v8::internal::Runtime_AllocateInYoungGeneration` 或静默重启。

**修复：** 在 `fly.toml` 中增加内存：

```toml
[[vm]]
  memory = "2048mb"
```

或更新现有机器：

```bash
fly machine update <machine-id> --vm-memory 2048 -y
```

**注意：** 512MB 太小。1GB 可能可行，但在负载下或详细日志记录时可能会 OOM。**推荐 2GB。**

### 网关锁问题

网关拒绝启动并出现 "already running" 错误。

当容器重启但 PID lock file 持久化在卷上时会发生这种情况。

**修复：** 删除 lock file：

```bash
fly ssh console --command "rm -f /data/gateway.*.lock"
fly machine restart <machine-id>
```

lock file 位于 `/data/gateway.*.lock` (不在子目录中)。

### 配置未被读取

如果使用 `--allow-unconfigured`，网关会创建一个最小化配置。你的自定义配置位于 `/data/openclaw.json` 应该在重启时被读取。

验证配置是否存在：

```bash
fly ssh console --command "cat /data/openclaw.json"
```

### 通过 SSH 写入配置

`fly ssh console -C` 命令不支持 shell 重定向。要写入配置文件：

```bash
# Use echo + tee (pipe from local to remote)
echo '{"your":"config"}' | fly ssh console -C "tee /data/openclaw.json"

# Or use sftp
fly sftp shell
> put /local/path/config.json /data/openclaw.json
```

**注意：** 如果文件已存在，`fly sftp` 可能会失败。先删除：

```bash
fly ssh console --command "rm /data/openclaw.json"
```

### 状态未持久化

如果重启后丢失凭证或会话，说明 state dir 正在写入容器文件系统。

**修复：** 确保在 `fly.toml` 中设置了 `OPENCLAW_STATE_DIR=/data` 并重新部署。

## 更新

```bash
# Pull latest changes
git pull

# Redeploy
fly deploy

# Check health
fly status
fly logs
```

### 更新机器命令

如果你需要在不完全重新部署的情况下更改启动命令：

```bash
# Get machine ID
fly machines list

# Update command
fly machine update <machine-id> --command "node dist/index.js gateway --port 3000 --bind lan" -y

# Or with memory increase
fly machine update <machine-id> --vm-memory 2048 --command "node dist/index.js gateway --port 3000 --bind lan" -y
```

**注意：** 在 `fly deploy` 之后，机器命令可能会重置为 `fly.toml` 中的内容。如果你进行了手动更改，请在部署后重新应用它们。

## 私有部署（强化）

默认情况下，Fly 会分配公共 IP，使你的网关可在 `https://your-app.fly.dev` 访问。这很方便，但意味着你的部署可被互联网扫描器（Shodan、Censys 等）发现。

对于**无公共暴露**的强化部署，请使用私有模板。

### 何时使用私有部署

- 你仅进行**出站**调用/消息（无入站 webhooks）
- 你使用 **ngrok 或 Tailscale** 隧道进行任何 webhook 回调
- 你通过 **SSH、proxy 或 WireGuard** 访问网关，而不是浏览器
- 你希望部署**对互联网扫描器隐藏**

### 设置

使用 `fly.private.toml` 代替标准配置：

```bash
# Deploy with private config
fly deploy -c fly.private.toml
```

或转换现有部署：

```bash
# List current IPs
fly ips list -a my-openclaw

# Release public IPs
fly ips release <public-ipv4> -a my-openclaw
fly ips release <public-ipv6> -a my-openclaw

# Switch to private config so future deploys don't re-allocate public IPs
# (remove [http_service] or deploy with the private template)
fly deploy -c fly.private.toml

# Allocate private-only IPv6
fly ips allocate-v6 --private -a my-openclaw
```

此后，`fly ips list` 应仅显示 `private` 类型的 IP：

```
VERSION  IP                   TYPE             REGION
v6       fdaa:x:x:x:x::x      private          global
```

### 访问私有部署

由于没有公共 URL，请使用以下方法之一：

**选项 1：本地 proxy（最简单）**

```bash
# Forward local port 3000 to the app
fly proxy 3000:3000 -a my-openclaw

# Then open http://localhost:3000 in browser
```

**选项 2: WireGuard VPN**

```bash
# Create WireGuard config (one-time)
fly wireguard create

# Import to WireGuard client, then access via internal IPv6
# Example: http://[fdaa:x:x:x:x::x]:3000
```

**选项 3: 仅 SSH**

```bash
fly ssh console -a my-openclaw
```

### 私有 deployment 的 Webhooks

如果您需要 webhook callbacks（Twilio、Telnyx 等）而不希望 public exposure：

1. **ngrok tunnel** - 在 container 内或作为 sidecar 运行 ngrok
2. **Tailscale Funnel** - 通过 Tailscale 暴露特定 paths
3. **Outbound-only** - 某些 providers（Twilio）无需 webhooks 即可正常处理 outbound calls

使用 ngrok 的 voice-call config 示例：

```json
{
  "plugins": {
    "entries": {
      "voice-call": {
        "enabled": true,
        "config": {
          "provider": "twilio",
          "tunnel": { "provider": "ngrok" },
          "webhookSecurity": {
            "allowedHosts": ["example.ngrok.app"]
          }
        }
      }
    }
  }
}
```

ngrok tunnel 在 container 内运行，提供 public webhook URL 而不暴露 Fly app 本身。将 `webhookSecurity.allowedHosts` 设置为 public tunnel hostname，以便接受 forwarded host headers。

### 安全优势

| Aspect            | Public       | Private    |
| ----------------- | ------------ | ---------- |
| Internet scanners | 可被发现     | 隐藏       |
| Direct attacks    | 可能         | 被阻止     |
| Control UI access | 浏览器       | Proxy/VPN  |
| Webhook delivery  | 直接         | 通过 tunnel |

## 注意事项

- Fly.io 使用 **x86 architecture**（非 ARM）
- Dockerfile 兼容这两种 architectures
- 对于 WhatsApp/Telegram onboarding，使用 `fly ssh console`
- Persistent data 位于 `/data` 的 volume 上
- Signal 需要 Java + signal-cli；使用 custom image 并保持 memory 在 2GB+。

## 成本

使用推荐 config（`shared-cpu-2x`，2GB RAM）：

- 每月约 10-15 美元，具体取决于 usage
- Free tier 包含一定 allowance

详见 [Fly.io 定价](https://fly.io/docs/about/pricing/)。