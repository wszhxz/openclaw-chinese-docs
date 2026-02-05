---
title: Fly.io
description: Deploy OpenClaw on Fly.io
---
# Fly.io 部署

**目标：** 在 [Fly.io](https://fly.io) 机器上运行的 OpenClaw 网关，具有持久存储、自动 HTTPS 和 Discord/频道访问功能。

## 您需要准备

- 已安装 [flyctl CLI](https://fly.io/docs/hands-on/install-flyctl/)
- Fly.io 账户（免费套餐可用）
- 模型认证：Anthropic API 密钥（或其他提供商密钥）
- 频道凭证：Discord 机器人令牌、Telegram 令牌等。

## 初学者快速路径

1. 克隆仓库 → 自定义 `fly.toml`
2. 创建应用 + 卷 → 设置密钥
3. 使用 `fly deploy` 部署
4. SSH 登录创建配置或使用控制界面

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

**提示：** 选择靠近您的区域。常用选项：`lhr`（伦敦）、`iad`（弗吉尼亚）、`sjc`（圣何塞）。

## 2) 配置 fly.toml

编辑 `fly.toml` 以匹配您的应用名称和需求。

**安全说明：** 默认配置暴露公共 URL。如需无公共 IP 的强化部署，请参阅[私有部署](#private-deployment-hardened) 或使用 `fly.private.toml`。

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

| 设置                           | 原因                                                                        |
| ------------------------------ | --------------------------------------------------------------------------- |
| `--bind lan`                   | 绑定到 `0.0.0.0` 以便 Fly 的代理可以访问网关                              |
| `--allow-unconfigured`         | 在没有配置文件的情况下启动（您稍后会创建一个）                                |
| `internal_port = 3000`         | 必须与 `--port 3000`（或 `OPENCLAW_GATEWAY_PORT`）匹配以进行 Fly 健康检查           |
| `memory = "2048mb"`            | 512MB 太小；推荐 2GB                                                        |
| `OPENCLAW_STATE_DIR = "/data"` | 在卷上持久化状态                                                            |

## 3) 设置密钥

``
```bash
# Required: Gateway token (for non-loopback binding)
fly secrets set OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)

# Model provider API keys
fly secrets set ANTHROPIC_API_KEY=sk-ant-...
```

# 可选：其他提供商
fly secrets set OPENAI_API_KEY=sk-...
fly secrets set GOOGLE_API_KEY=...

# 频道令牌
fly secrets set DISCORD_BOT_TOKEN=MTQ...
```bash
fly deploy
```
```bash
fly status
fly logs
```
```
[gateway] listening on ws://0.0.0.0:3000 (PID xxx)
[discord] logged in to discord as xxx
```
```bash
fly ssh console
```
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
```bash
exit
fly machine restart <machine-id>
```
```bash
fly open
```
```bash
fly logs              # Live logs
fly logs --no-tail    # Recent logs
```
```bash
fly ssh console
```
````
127.0.0.1
````
```
0.0.0.0
```
```
--bind lan
```
`fly.toml`。

### 健康检查失败 / 连接被拒绝

Fly 无法在配置的端口上连接到网关。

**修复：** 确保 `internal_port` 与网关端口匹配（设置 `--port 3000` 或 `OPENCLAW_GATEWAY_PORT=3000`）。

### OOM / 内存问题

容器持续重启或被终止。迹象：`SIGABRT`、`v8::internal::Runtime_AllocateInYoungGeneration` 或静默重启。

**修复：** 在 `fly.toml` 中增加内存：

```toml
[[vm]]
  memory = "2048mb"
```

或者更新现有机器：

```bash
fly machine update <machine-id> --vm-memory 2048 -y
```

**注意：** 512MB 太小了。1GB 可能可以工作，但在负载下或详细日志记录时可能会出现 OOM。**建议使用 2GB。**

### 网关锁定问题

网关拒绝启动并显示"已在运行"错误。

这发生在容器重启但 PID 锁定文件仍保留在卷上时。

**修复：** 删除锁定文件：

```bash
fly ssh console --command "rm -f /data/gateway.*.lock"
fly machine restart <machine-id>
```

锁定文件位于 `/data/gateway.*.lock`（不在子目录中）。

### 配置未被读取

如果使用 `--allow-unconfigured`，网关会创建一个最小配置。您的自定义配置在 `/data/openclaw.json` 应在重启时被读取。

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

**注意：** 如果文件已存在，`fly sftp` 可能会失败。请先删除：

```bash
fly ssh console --command "rm /data/openclaw.json"
```

### 状态未持久化

如果重启后丢失凭据或会话，则状态目录正在写入容器文件系统。

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

如果您需要更改启动命令而无需完全重新部署：

```bash
# Get machine ID
fly machines list

# Update command
fly machine update <machine-id> --command "node dist/index.js gateway --port 3000 --bind lan" -y

# Or with memory increase
fly machine update <machine-id> --vm-memory 2048 --command "node dist/index.js gateway --port 3000 --bind lan" -y
```

**注意：** 在 `fly deploy` 之后，机器命令可能会重置为 `fly.toml` 中的内容。如果您进行了手动更改，请在部署后重新应用它们。

## 私有部署（强化）

默认情况下，Fly 分配公共 IP，使您的网关可在 `https://your-app.fly.dev` 访问。这很方便，但意味着您的部署可被互联网扫描器（Shodan、Censys 等）发现。

对于**无公共暴露**的强化部署，请使用私有模板。

### 何时使用私有部署

- 您只发起**出站**调用/消息（无入站webhook）
- 您使用**ngrok或Tailscale**隧道进行任何webhook回调
- 您通过**SSH、代理或WireGuard**访问网关，而不是浏览器
- 您希望部署对互联网扫描器**隐藏**

### 设置

使用以下配置代替标准配置：

```yaml
# fly.toml
[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = false
  min_machines_running = 0
  processes = ["app"]
```

或者转换现有部署：

```bash
fly scale count 0 --region [region]
fly deploy --detach
```

在此之后，`fly ips list` 应该只显示 `private` 类型IP：

```bash
TYPE   ADDRESS                                REGION  
private  fd7a:115c:a1e0:ab12:4843:cd96:626f:2000  lax   
```

### 访问私有部署

由于没有公共URL，请使用以下方法之一：

**选项1：本地代理（最简单）**

```bash
fly proxy 8080:8080
# Then visit http://localhost:8080
```

**选项2：WireGuard VPN**

```bash
fly wireguard web
# Then visit the private IPv6 address shown
```

**选项3：仅SSH**

```bash
fly ssh console
# Then curl localhost:8080 or use port forwarding
```

### 私有部署的Webhooks

如果您需要webhook回调（Twilio、Telnyx等）而无需公开暴露：

1. **ngrok隧道** - 在容器内部或作为sidecar运行ngrok
2. **Tailscale Funnel** - 通过Tailscale暴露特定路径
3. **仅出站** - 某些提供商（Twilio）在没有webhook的情况下出站调用也能正常工作

带有ngrok的语音通话配置示例：

```yaml
# docker-compose.yml
services:
  app:
    # ... other config
    environment:
      - WEBHOOK_HOST=your-tunnel.ngrok.io  # Public tunnel hostname
  ngrok:
    image: ngrok/ngrok:latest
    command: ["http", "app:8080"]
    ports:
      - "4040:4040"  # ngrok dashboard
    depends_on:
      - app
```

ngrok隧道在容器内部运行并提供公共webhook URL，而无需暴露Fly应用本身。将 `WEBHOOK_HOST` 设置为公共隧道主机名，以便接受转发的主机头。

### 安全优势

| 方面              | 公共         | 私有       |
| ----------------- | ------------ | ---------- |
| 互联网扫描器      | 可发现       | 隐藏       |
| 直接攻击          | 可能         | 已阻止     |
| 控制UI访问        | 浏览器       | 代理/VPN   |
| Webhook传递       | 直接         | 通过隧道   |

## 注意事项

- Fly.io 使用 **x86 架构**（非 ARM）
- Dockerfile 与两种架构都兼容
- 对于 WhatsApp/Telegram 入门，请使用 `fly launch`
- 持久化数据存储在挂载点 `/data` 的卷上
- Signal 需要 Java + signal-cli；使用自定义镜像并将内存保持在 2GB 以上。

## 费用

使用推荐配置（1GB 存储，2GB 内存）：

- 根据使用情况约为 $10-15/月
- 免费层级包含一些额度

详情请参见 [Fly.io 定价](https://fly.io/docs/about/pricing/)。