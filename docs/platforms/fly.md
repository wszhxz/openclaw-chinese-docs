---
title: Fly.io
description: Deploy OpenClaw on Fly.io
---
# Fly.io 部署

**目标:** 在 [Fly.io](https://fly.io) 机器上运行带有持久存储、自动 HTTPS 和 Discord/频道访问权限的 OpenClaw Gateway。

## 所需条件

- 已安装的 [flyctl CLI](https://fly.io/docs/hands-on/install-flyctl/)
- Fly.io 账户（免费层即可）
- 模型认证：Anthropic API 密钥（或其他提供商密钥）
- 频道凭证：Discord 机器人令牌、Telegram 令牌等

## 初学者快速路径

1. 克隆仓库 → 自定义 `fly.toml`
2. 创建应用 + 卷 → 设置密钥
3. 使用 `fly deploy` 部署
4. 通过 SSH 进入创建配置或使用控制 UI

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
| `--allow-unconfigured`         | 启动时不使用配置文件（稍后会创建一个）                      |
| `internal_port = 3000`         | 必须与 `--port 3000`（或 `OPENCLAW_GATEWAY_PORT`）匹配以供 Fly 健康检查 |
| `memory = "2048mb"`            | 512MB 太小；建议 2GB                                         |
| `OPENCLAW_STATE_DIR = "/data"` | 在卷上持久化状态                                                |

## 3) 设置密钥

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

**注意:**

- 非回环绑定 (`--bind lan`) 需要 `OPENCLAW_GATEWAY_TOKEN` 以确保安全。
- 将这些令牌视为密码。
- **优先使用环境变量而不是配置文件** 来处理所有 API 密钥和令牌。这可以防止密钥意外地出现在 `openclaw.json` 中被泄露或记录。

## 4) 部署

```bash
fly deploy
```

首次部署会构建 Docker 镜像（约 2-3 分钟）。后续部署速度更快。

部署后验证：

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

通过 SSH 进入机器以创建适当的配置：

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

**注意:** 使用 `OPENCLAW_STATE_DIR=/data` 时，配置路径为 `/data/openclaw.json`。

**注意:** Discord 令牌可以来自：

- 环境变量: `DISCORD_BOT_TOKEN`（推荐用于密钥）
- 配置文件: `channels.discord.token`

如果使用环境变量，则无需在配置中添加令牌。网关会自动读取 `DISCORD_BOT_TOKEN`。

重启以应用更改：

```bash
exit
fly machine restart <machine-id>
```

## 6) 访问网关

### 控制 UI

在浏览器中打开：

```bash
fly open
```

或访问 `https://my-openclaw.fly.dev/`

粘贴你的网关令牌（来自 `OPENCLAW_GATEWAY_TOKEN`）以进行身份验证。

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

网关绑定到 `127.0.0.1` 而不是 `0.0.0.0`。

**解决方法:** 在 `fly.toml` 中的进程命令中添加 `--bind lan`。

### 健康检查失败 / 连接被拒绝

Fly 无法在配置端口上访问网关。

**解决方法:** 确保 `internal_port` 匹配网关端口（设置 `--port 3000` 或 `OPENCLAW_GATEWAY_PORT=3000`）。

### OOM / 内存问题

容器不断重启或被终止。迹象：`SIGABRT`，`v8::internal::Runtime_AllocateInYoungGeneration` 或静默重启。

**解决方法:** 增加 `fly.toml` 中的内存：

```toml
[[vm]]
  memory = "2048mb"
```

或更新现有机器：

```bash
fly machine update <machine-id> --vm-memory 2048 -y
```

**注意:** 512MB 太小。1GB 可能可行但在负载下或启用详细日志记录时可能会 OOM。**建议使用 2GB。**

### 网关锁定问题

网关由于“已运行”错误而拒绝启动。

这发生在容器重启但 PID 锁定文件保留在卷上时。

**解决方法:** 删除锁定文件：

```bash
fly ssh console --command "rm -f /data/gateway.*.lock"
fly machine restart <machine-id>
```

锁定文件位于 `/data/gateway.*.lock`（不在子目录中）。

### 配置未被读取

如果使用 `--allow-unconfigured`，网关会创建一个最小配置。你的自定义配置 `/data/openclaw.json` 应该在重启时被读取。

验证配置是否存在：

```bash
fly ssh console --command "cat /data/openclaw.json"
```

### 通过 SSH 编写配置

`fly ssh console -C` 命令不支持 shell 重定向。要编写配置文件：

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

如果重启后丢失凭据或会话，状态目录正在写入容器文件系统。

**解决方法:** 确保 `OPENCLAW_STATE_DIR=/data` 在 `fly.toml` 中设置并重新部署。

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

如果你需要更改启动命令而无需完全重新部署：

```bash
# Get machine ID
fly machines list

# Update command
fly machine update <machine-id> --command "node dist/index.js gateway --port 3000 --bind lan" -y

# Or with memory increase
fly machine update <machine-id> --vm-memory 2048 --command "node dist/index.js gateway --port 3000 --bind lan" -y
```

**注意:** 在 `fly deploy` 之后，机器命令可能会重置为 `fly.toml` 中的内容。如果你进行了手动更改，请在部署后重新应用它们。

## 私有部署（加固）

默认情况下，Fly 分配公共 IP，使你的网关可以通过 `https://your-app.fly.dev` 访问。这很方便，但意味着你的部署可被互联网扫描器（Shodan、Censys 等）发现。

为了实现没有公共暴露的加固部署，请使用私有模板。

### 何时使用私有部署

- 你只进行 **出站** 调用/消息（无入站 Webhook）
- 你使用 **ngrok 或 Tailscale** 隧道进行任何 Webhook 回调
- 你通过 **SSH、代理或 WireGuard** 而不是浏览器访问网关
- 你希望部署 **隐藏在互联网扫描器之外**

### 设置

使用 `fly.private.toml` 而不是标准配置：

```bash
# Deploy with private config
fly deploy -c fly.private.toml
```

或将现有部署转换为私有部署：

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

完成此操作后，`fly ips list` 应仅显示 `private` 类型的 IP：

```
VERSION  IP                   TYPE             REGION
v6       fdaa:x:x:x:x::x      private          global
```

### 访问私有部署

由于没有公共 URL，请使用以下方法之一：

**选项 1: 本地代理（最简单）**

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

### 私有部署中的 Webhook

如果你需要在没有公共暴露的情况下进行 Webhook 回调（Twilio、Telnyx 等）：

1. **ngrok 隧道** - 在容器内部或作为边车运行 ngrok
2. **Tailscale Funnel** - 通过 Tailscale 暴露特定路径
3. **仅出站** - 某些提供商（Twilio）在没有 Webhook 的情况下也能正常进行出站调用

使用 ngrok 的示例语音呼叫配置：

```json
{
  "plugins": {
    "entries": {
      "voice-call": {
        "enabled": true,
        "config": {
          "provider": "twilio",
          "tunnel": { "provider": "ngrok" }
        }
      }
    }
  }
}
```

ngrok 隧道在容器内部运行，并提供一个公共 Webhook URL 而不暴露 Fly 应用本身。

### 安全优势

| 方面            | 公共       | 私有    |
| ----------------- | ------------ | ---------- |
| 互联网扫描器 | 可发现     | 隐藏     |
| 直接攻击    | 可能     | 阻止    |
| 控制 UI 访问 | 浏览器      | 代理/VPN  |
| Webhook 交付  | 直接       | 通过隧道 |

## 注意事项

- Fly.io 使用 **x86 架构**（不是 ARM）
- Dockerfile 兼容两种架构
- 对于 WhatsApp/Telegram 入门，使用 `fly ssh console`
- 持久数据存储在卷上的 `/data`
- Signal 需要 Java + signal-cli；使用自定义镜像并将内存保持在 2GB+

## 成本

使用推荐配置 (`shared-cpu-2x`, 2GB 内存)：

- 根据使用情况约为每月 $10-15
- 免费层包括一些额度

详情请参阅 [Fly.io 定价](https://fly.io/docs/about/pricing/)。