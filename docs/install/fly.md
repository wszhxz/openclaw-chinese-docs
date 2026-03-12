---
title: Fly.io
description: Deploy OpenClaw on Fly.io
summary: "Step-by-step Fly.io deployment for OpenClaw with persistent storage and HTTPS"
read_when:
  - Deploying OpenClaw on Fly.io
  - Setting up Fly volumes, secrets, and first-run config
---
# Fly.io 部署

**目标：** 在 [Fly.io](https://fly.io) 机器上运行 OpenClaw 网关，具备持久化存储、自动 HTTPS 以及 Discord/频道访问能力。

## 您需要准备的内容

- 已安装 [flyctl CLI](https://fly.io/docs/hands-on/install-flyctl/)
- Fly.io 账户（免费套餐即可使用）
- 模型认证：所选模型提供商的 API 密钥
- 频道凭证：Discord 机器人令牌、Telegram 令牌等

## 新手快速入门路径

1. 克隆仓库 → 自定义 `fly.toml`
2. 创建应用 + 卷 → 设置密钥（secrets）
3. 使用 `fly deploy` 部署
4. 通过 SSH 登录创建配置，或使用控制界面（Control UI）

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

**提示：** 请选择离您地理位置较近的区域。常见选项包括：`lhr`（伦敦）、`iad`（弗吉尼亚）、`sjc`（圣何塞）。

## 2) 配置 fly.toml

编辑 `fly.toml`，使其匹配您的应用名称及需求。

**安全提示：** 默认配置会暴露一个公开 URL。如需部署为无公网 IP 的加固版本，请参阅 [私有部署（加固版）](#private-deployment-hardened)，或使用 `fly.private.toml`。

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

**关键配置项说明：**

| 配置项                         | 原因                                                                         |
| ------------------------------ | --------------------------------------------------------------------------- |
| `--bind lan`                   | 绑定到 `0.0.0.0`，以便 Fly 的代理可访问网关                     |
| `--allow-unconfigured`         | 启动时不依赖配置文件（您将在之后手动创建）                      |
| `internal_port = 3000`         | 必须与 `--port 3000`（或 `OPENCLAW_GATEWAY_PORT`）一致，以满足 Fly 健康检查要求 |
| `memory = "2048mb"`            | 512MB 内存过小；推荐 2GB                                         |
| `OPENCLAW_STATE_DIR = "/data"` | 将状态持久化保存至卷（volume）                                                |

## 3) 设置密钥（secrets）

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

**注意事项：**

- 非回环地址绑定（`--bind lan`）出于安全考虑需启用 `OPENCLAW_GATEWAY_TOKEN`。
- 请将这些令牌视同密码妥善保管。
- **所有 API 密钥和令牌均应优先通过环境变量而非配置文件设置**。此举可避免密钥意外泄露或记录在 `openclaw.json` 中。

## 4) 部署

```bash
fly deploy
```

首次部署将构建 Docker 镜像（约耗时 2–3 分钟），后续部署速度更快。

部署完成后，请验证：

```bash
fly status
fly logs
```

您应看到如下输出：

```
[gateway] listening on ws://0.0.0.0:3000 (PID xxx)
[discord] logged in to discord as xxx
```

## 5) 创建配置文件

通过 SSH 登录机器并创建正式配置：

```bash
fly ssh console
```

创建配置目录及文件：

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

**注意：** 若使用 `OPENCLAW_STATE_DIR=/data`，则配置路径为 `/data/openclaw.json`。

**注意：** Discord 令牌可通过以下任一方式提供：

- 环境变量：`DISCORD_BOT_TOKEN`（推荐用于敏感信息）
- 配置文件：`channels.discord.token`

若使用环境变量，则无需在配置文件中填写令牌；网关会自动读取 `DISCORD_BOT_TOKEN`。

重启以应用更改：

```bash
exit
fly machine restart <machine-id>
```

## 6) 访问网关

### 控制界面（Control UI）

在浏览器中打开：

```bash
fly open
```

或访问 `https://my-openclaw.fly.dev/`

粘贴您的网关令牌（即来自 `OPENCLAW_GATEWAY_TOKEN` 的令牌）进行身份验证。

### 日志

```bash
fly logs              # Live logs
fly logs --no-tail    # Recent logs
```

### SSH 控制台

```bash
fly ssh console
```

## 故障排查

### “应用未在预期地址监听”

网关绑定到了 `127.0.0.1`，而非 `0.0.0.0`。

**解决方法：** 在 `fly.toml` 的进程命令中添加 `--bind lan`。

### 健康检查失败 / 连接被拒绝

Fly 无法在已配置端口上访问网关。

**解决方法：** 确保 `internal_port` 与网关端口一致（设置 `--port 3000` 或 `OPENCLAW_GATEWAY_PORT=3000`）。

### 内存不足（OOM）/ 内存问题

容器持续重启或被强制终止。典型迹象包括：`SIGABRT`、`v8::internal::Runtime_AllocateInYoungGeneration` 或静默重启。

**解决方法：** 在 `fly.toml` 中增加内存限制：

```toml
[[vm]]
  memory = "2048mb"
```

或更新现有机器配置：

```bash
fly machine update <machine-id> --vm-memory 2048 -y
```

**注意：** 512MB 内存过小。1GB 可能勉强运行，但在高负载或详细日志模式下仍可能触发 OOM。**推荐配置为 2GB。**

### 网关锁文件问题

网关启动失败，并报错“已在运行”。

此问题通常发生在容器重启后，卷（volume）上残留了 PID 锁文件。

**解决方法：** 删除锁文件：

```bash
fly ssh console --command "rm -f /data/gateway.*.lock"
fly machine restart <machine-id>
```

锁文件位于 `/data/gateway.*.lock`（不在子目录中）。

### 配置未被读取

若使用 `--allow-unconfigured`，网关会生成一个最小化配置。您自定义的配置文件 `/data/openclaw.json` 应在重启后被加载。

请验证配置文件是否存在：

```bash
fly ssh console --command "cat /data/openclaw.json"
```

### 通过 SSH 编写配置文件

`fly ssh console -C` 命令不支持 shell 重定向。如需写入配置文件，请使用：

```bash
# Use echo + tee (pipe from local to remote)
echo '{"your":"config"}' | fly ssh console -C "tee /data/openclaw.json"

# Or use sftp
fly sftp shell
> put /local/path/config.json /data/openclaw.json
```

**注意：** 若文件已存在，`fly sftp` 可能失败。请先删除原文件：

```bash
fly ssh console --command "rm /data/openclaw.json"
```

### 状态未持久化

若重启后丢失凭证或会话，说明状态目录正写入容器文件系统而非卷。

**解决方法：** 确保 `OPENCLAW_STATE_DIR=/data` 已在 `fly.toml` 中设置，并重新部署。

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

### 更新机器启动命令

如需修改启动命令但不执行完整重新部署：

```bash
# Get machine ID
fly machines list

# Update command
fly machine update <machine-id> --command "node dist/index.js gateway --port 3000 --bind lan" -y

# Or with memory increase
fly machine update <machine-id> --vm-memory 2048 --command "node dist/index.js gateway --port 3000 --bind lan" -y
```

**注意：** 执行 `fly deploy` 后，机器启动命令可能恢复为 `fly.toml` 中定义的内容。若您曾手动修改过该命令，请在部署后重新应用。

## 私有部署（加固版）

默认情况下，Fly 会分配公网 IP，使您的网关可通过 `https://your-app.fly.dev` 访问。这种方式虽便捷，但也意味着您的部署可能被互联网扫描器（如 Shodan、Censys 等）发现。

如需实现**完全无公网暴露**的加固部署，请使用私有模板。

### 适用私有部署的场景

- 您仅发起**出站**调用/消息（无入站 Webhook）
- 您使用 **ngrok 或 Tailscale** 隧道处理任意 Webhook 回调
- 您通过 **SSH、代理或 WireGuard** 访问网关，而非浏览器
- 您希望部署**对互联网扫描器完全不可见**

### 部署步骤

请使用 `fly.private.toml` 替代标准配置：

```bash
# Deploy with private config
fly deploy -c fly.private.toml
```

或转换已有部署：

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

完成上述操作后，`fly ips list` 应仅显示类型为 `private` 的 IP：

```
VERSION  IP                   TYPE             REGION
v6       fdaa:x:x:x:x::x      private          global
```

### 访问私有部署

由于不存在公网 URL，请使用以下任一方式访问：

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

**选项 3：仅使用 SSH**

```bash
fly ssh console -a my-openclaw
```

### 使用私有部署的 Webhook

如果需要 Webhook 回调（例如 Twilio、Telnyx 等），但又不希望服务暴露在公网上：

1. **ngrok 隧道** —— 在容器内或以边车（sidecar）方式运行 ngrok  
2. **Tailscale Funnel** —— 通过 Tailscale 暴露特定路径  
3. **仅出站通信** —— 某些服务商（如 Twilio）在无需 Webhook 的情况下，仍可正常完成出站呼叫  

使用 ngrok 的语音通话配置示例：

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

ngrok 隧道在容器内运行，可提供一个公开的 Webhook URL，而无需将 Fly 应用本身暴露在外。请将 `webhookSecurity.allowedHosts` 设置为公共隧道主机名，以便接受转发的 Host 请求头。

### 安全优势

| 方面               | 公开部署     | 私有部署   |
| ------------------ | ------------ | ---------- |
| 互联网扫描器       | 可被发现     | 隐藏       |
| 直接攻击           | 可能发生     | 被阻止     |
| 控制台界面访问方式 | 浏览器       | 代理 / VPN |
| Webhook 投递方式   | 直接投递     | 经由隧道   |

## 注意事项

- Fly.io 使用 **x86 架构**（非 ARM）  
- 该 Dockerfile 同时兼容两种架构  
- WhatsApp / Telegram 接入时，请使用 `fly ssh console`  
- 持久化数据存储在位于 `/data` 的卷上  
- Signal 需要 Java + signal-cli；请使用自定义镜像，并确保内存不低于 2GB。

## 成本

采用推荐配置（`shared-cpu-2x`，2GB 内存）：

- 每月费用约 $10–15，具体取决于使用量  
- 免费套餐包含一定额度  

详情请参阅 [Fly.io 定价页面](https://fly.io/docs/about/pricing/)。