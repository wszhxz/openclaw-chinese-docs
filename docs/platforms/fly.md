---
title: Fly.io
description: Deploy OpenClaw on Fly.io
---
# Fly.io 部署

**目标:** 在 [Fly.io](https://fly.io) 机器上运行带有持久化存储、自动 HTTPS 和 Discord/频道访问权限的 OpenClaw Gateway。

## 所需条件

- 已安装的 [flyctl CLI](https://fly.io/docs/hands-on/install-flyctl/)
- Fly.io 账户（免费层即可）
- 模型认证：Anthropic API 密钥（或其他提供商密钥）
- 频道凭证：Discord 机器人令牌、Telegram 令牌等

## 初学者快速路径

1. 克隆仓库 → 自定义 `fly.toml`
2. 创建应用 + 卷 → 设置密钥
3. 使用 `fly deploy` 部署
4. 通过 SSH 进入以创建配置或使用控制 UI

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

**提示:** 选择离你近的区域。常见选项：`lhr`（伦敦），`iad`（弗吉尼亚），`sjc`（圣何塞）。

## 2) 配置 fly.toml

编辑 `fly.toml` 以匹配你的应用名称和需求。

**安全说明:** 默认配置会暴露一个公共 URL。对于没有公共 IP 的加固部署，请参阅 [私有部署](#private-deployment-hardened) 或使用 `fly.private.toml`。

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

**关键设置:**

| 设置                        | 原因                                                                         |
| ------------------------------ | --------------------------------------------------------------------------- |
| `--bind lan`                   | 绑定到 `0.0.0.0` 以便 Fly 的代理可以访问网关                     |
| `--allow-unconfigured`         | 启动时不带配置文件（之后你会创建一个）                      |
| `internal_port = 3000`         | 必须与 `--port 3000`（或 `OPENCLAW_GATEWAY_PORT`）匹配以供 Fly 健康检查 |
| `memory = "2048mb"`            | 512MB 太小；建议 2GB                                         |
| `OPENCLAW_STATE_DIR = "/data"` | 在卷上持久化状态                                                |

## 3) 设置密钥

```bash
# 必需：网关令牌（用于非回环绑定）
fly secrets set OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)

# 模型提供商 API 密钥
fly secrets set ANTHROPIC_API_KEY=sk-ant-...

# 可选: 其他提供商
fly secrets set OPENAI_API_KEY=sk-...
fly secrets set GOOGLE_API_KEY=...

# 频道令牌
fly secrets set DISCORD_BOT_TOKEN=MTQ...
```

**Notes:**

- Non-loopback binds (`--bind lan`) require `OPENCLAW_GATEWAY_TOKEN` for security.
- Treat these tokens like passwords.
- **Prefer env vars over config file** for all API keys and tokens. This keeps secrets out of `openclaw.json` where they could be accidentally exposed or logged.

## 4) Deploy

```bash
fly deploy
```

First deploy builds the Docker image (~2-3 minutes). Subsequent deploys are faster.

After deployment, verify:

```bash
fly status
fly logs
```

You should see:

```
[gateway] listening on ws://0.0.0.0:3000 (PID xxx)
[discord] logged in to discord as xxx
```

## 5) Create config file

SSH into the machine to create a proper config:

```bash
fly ssh console
```

Create the config directory and file:

```bash
mkdir -p /data
cat > /data/openclaw.json << 'EOF'
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-5",
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

**Note:** With `OPENCLAW_STATE_DIR=/data`, the config path is `/data/openclaw.json`.

**Note:** The Discord token can come from either:

- Environment variable: `DISCORD_BOT_TOKEN` (recommended for secrets)
- Config file: `channels.discord.token`

If using env var, no need to add token to config. The gateway reads `DISCORD_BOT_TOKEN` automatically.

Restart to apply:

```bash
exit
fly machine restart <machine-id>
```

## 6) Access the Gateway

### Control UI

Open in browser:

```bash
fly open
```

Or visit `https://my-openclaw.fly.dev/`

Paste your gateway token (the one from `OPENCLAW_GATEWAY_TOKEN`) to authenticate.

### Logs

```bash
fly logs              # 实时日志
fly logs --no-tail    # 最近日志
```

### SSH Console

```bash
fly ssh console
```

## Troubleshooting

### "App is not listening on expected address"

The gateway is binding to `127.0.0.1` instead of `0.0.0.0`.

**Fix:** Add `--bind lan` to your process command in `fly.toml`.

### 健康检查失败 / 连接被拒绝

Fly 无法在配置的端口上访问网关。

**修复:** 确保 `internal_port` 匹配网关端口（设置 `--port 3000` 或 `OPENCLAW_GATEWAY_PORT=3000`）。

### OOM / 内存问题

容器持续重启或被终止。迹象：`SIGABRT`，`v8::internal::Runtime_AllocateInYoungGeneration`，或静默重启。

**修复:** 增加 `fly.toml` 中的内存：

```toml
[[vm]]
  memory = "2048mb"
```

或者更新现有机器：

```bash
fly machine update <machine-id> --vm-memory 2048 -y
```

**注意:** 512MB 太小。1GB 可能可以工作，但在负载下或启用详细日志记录时可能会出现 OOM。**建议使用 2GB。**

### 网关锁定问题

网关由于“已运行”错误而拒绝启动。

当容器重启但 PID 锁定文件保留在卷上时会发生这种情况。

**修复:** 删除锁定文件：

```bash
fly ssh console --command "rm -f /data/gateway.*.lock"
fly machine restart <machine-id>
```

锁定文件位于 `/data/gateway.*.lock`（不在子目录中）。

### 配置未被读取

如果使用 `--allow-unconfigured`，网关会创建一个最小配置。您的自定义配置 `/data/openclaw.json` 应该在重启时被读取。

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

**注意:** 如果文件已存在，`fly sftp` 可能会失败。先删除：

```bash
fly ssh console --command "rm /data/openclaw.json"
```

### 状态未持久化

如果在重启后丢失凭据或会话，状态目录正在写入容器文件系统。

**修复:** 确保 `OPENCLAW_STATE_DIR=/data` 在 `fly.toml` 中设置并重新部署。

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

如果您需要更改启动命令而无需完全重新部署：

```bash
# Get machine ID
fly machines list

# Update command
fly machine update <machine-id> --command "node dist/index.js gateway --port 3000 --bind lan" -y

# Or with memory increase
fly machine update <machine-id> --vm-memory 2048 --command "node dist/index.js gateway --port 3000 --bind lan" -y
```

**注意:** 在 `fly deploy` 之后，机器命令可能会重置为 `fly.toml` 中的内容。如果您进行了手动更改，请在部署后重新应用它们。

## 私有部署（加固）

默认情况下，Fly 分配公共 IP，使您的网关可以通过 `https://your-app.fly.dev` 访问。这很方便，但也意味着您的部署可被互联网扫描器（Shodan、Censys 等）发现。

对于具有**无公共暴露**的加固部署，请使用私有模板。

### 何时使用私有部署

- 您仅进行 **outbound** 调用/消息（不使用入站 Webhook）
- 您使用 **ngrok 或 Tailscale** 隧道进行任何 Webhook 回调
- 您通过 **SSH、代理或 WireGuard** 访问网关，而不是通过浏览器
- 您希望部署 **隐藏在互联网扫描器之外**

### 设置

使用 `fly.private.toml` 而不是标准配置：

```bash
# Deploy with private config
fly deploy -c fly.private.toml
```

或者转换现有部署：

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

之后，`fly ips list` 应该只显示一个 `private` 类型的 IP：

```
VERSION  IP                   TYPE             REGION
v6       fdaa:x:x:x:x::x      private          global
```

### 访问私有部署

由于没有公共 URL，请使用以下方法之一：

**选项 1：本地代理（最简单）**

```bash
# Forward local port 3000 to the app
fly proxy 3000:3000 -a my-openclaw

# Then open http://localhost:3000 in browser
```

**选项 2：WireGuard VPN**

```bash
# Create WireGuard config (one-time)
fly wireguard create

# Import to WireGuard client, then access via internal IPv6
# Example: http://[fdaa:x:x:x:x::x]:3000
```

**选项 3：仅 SSH**

```bash
fly ssh console -a my-openclaw
```

### 私有部署中的 Webhook

如果您需要无需公开暴露的 Webhook 回调（Twilio、Telnyx 等）：

1. **ngrok 隧道** - 在容器内部或作为边车运行 ngrok
2. **Tailscale Funnel** - 通过 Tailscale 暴露特定路径
3. **仅出站** - 某些提供商（Twilio）在没有 Webhook 的情况下可以正常进行出站调用

使用 ngrok 的示例语音呼叫配置：

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

ngrok 隧道在容器内部运行，并提供一个公共 Webhook URL 而不暴露 Fly 应用本身。将 `webhookSecurity.allowedHosts` 设置为公共隧道主机名，以便接受转发的主机头。

### 安全优势

| 方面            | 公共       | 私有    |
| ----------------- | ------------ | ---------- |
| 互联网扫描器 | 可发现     | 隐藏     |
| 直接攻击    | 可能     | 已阻止    |
| 控制 UI 访问 | 浏览器      | 代理/VPN  |
| Webhook 交付  | 直接       | 通过隧道 |

## 注意事项

- Fly.io 使用 **x86 架构**（不是 ARM）
- Dockerfile 兼容两种架构
- 对于 WhatsApp/Telegram 入门，使用 `fly ssh console`
- 持久化数据存储在卷 `/data` 上
- Signal 需要 Java + signal-cli；使用自定义镜像并将内存保持在 2GB 以上。

## 成本

使用推荐配置 (`shared-cpu-2x`, 2GB 内存)：

- 根据使用情况约为每月 $10-15
- 免费层包括一些配额

详情请参见 [Fly.io 定价](https://fly.io/docs/about/pricing/)。