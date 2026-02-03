---
title: Fly.io
description: Deploy OpenClaw on Fly.io
---
# Fly.io 部署

**目标：** 在 [Fly.io](https://fly.io) 机器上运行 OpenClaw 网关，支持持久化存储、自动 HTTPS 和 Discord/频道访问。

## 你需要的工具

- [flyctl CLI](https://fly.io/docs/hands-on/install-flyctl/) 已安装
- Fly.io 账户（免费层级可用）
- 模型认证：Anthropic API 密钥（或其他提供商密钥）
- 频道凭证：Discord 机器人令牌、Telegram 令牌等

## 初学者快速路径

1. 克隆仓库 → 自定义 fly.toml
2. 配置 fly.toml → 设置环境变量
3. 部署应用 → 检查状态和日志

## 配置 fly.toml

### 关键设置

| 项目 | 说明 |
|------|------|
| --bind lan | 绑定本地网络 |
| --port 3000 | 设置端口为 3000 |
| --https | 启用 HTTPS |

## 设置环境变量

```bash
fly secrets set OPENCLAW_GATEWAY_TOKEN=your_token
fly secrets set DISCORD_WEBHOOK_URL=https://discord.com/webhooks
```

## 部署应用

```bash
fly deploy
```

## 检查状态和日志

```bash
fly status
fly logs
```

## 常见问题

### 应用未在预期地址上监听

**解决方法：** 确保 `--bind lan` 和 `--port 3000` 已正确设置。

### 环境变量未设置

**解决方法：** 使用 `fly secrets set` 命令设置所有必要的环境变量。

## 私有部署（强化版）

默认情况下，Fly 会分配公共 IP，使你的网关可通过 `https://your-app.fly.dev` 访问。这虽然方便，但会使你的部署对互联网扫描器（如 Shodan、Censys）可见。

**使用私有模板进行强化部署：**

### 何时使用私有部署

- 你仅进行 **出站** 调用/消息（无入站 Webhook）
- 你使用 **ngrok 或 Tailscale** 隧道进行任何 Webhook 回调
- 你通过 **SSH、代理或 WireGuard** 访问网关（而非浏览器）
- 你希望部署 **隐藏在互联网扫描器之外**

### 设置

使用 `fly.private.toml` 代替标准配置：

```bash
fly deploy -c fly.private.toml
```

或转换现有部署：

```bash
fly ips list -a my-openclaw
fly ips release <public-ipv4> -a my-openclaw
fly ips release <public-ipv6> -a my-openclaw
fly deploy -c fly.private.toml
fly ips allocate-v6 --private -a my-openclaw
```

### 访问私有部署

由于没有公共 URL，使用以下方法：

**选项 1：本地代理（最简单）**

```bash
fly proxy 3000:3000 -a my-openclaw
```

**选项 2：WireGuard VPN**

```bash
fly wireguard create
```

**选项 3：仅 SSH**

```bash
fly ssh console -a my-openclaw
```

### 私有部署的 Webhook

若需 Webhook 回调（Twilio、Telnyx 等）且无公共暴露：

1. **ngrok 隧道** - 在容器内或作为 sidecar 运行 ngrok
2. **Tailscale Funnel** - 通过 Tailscale 暴露特定路径
3. **仅出站** - 某些提供商（Twilio）无需 Webhook 即可正常工作

**ngrok 示例配置：**

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

### 安全优势

| 方面 | 公共 | 私有 |
|------|------|------|
| 互联网扫描器 | 可发现 | 隐藏 |
| 直接攻击 | 可能 | 阻止 |
| 控制 UI 访问 | 浏览器 | 代理/VPN |
| Webhook 交付 | 直接 | 通过隧道 |

## 注意事项

- Fly.io 使用 **x86 架构**（非 ARM）
- Dockerfile 兼容两种架构
- 对于 WhatsApp/Telegram 注册，使用 `fly ssh console`
- 持久化数据存储在 `/data` 目录
- Signal 需要 Java + signal-cli；使用自定义镜像并保持内存为 2GB+

## 成本

推荐配置（`shared-cpu-2x`，2GB RAM）：

- 月费用约 $10-15，具体取决于使用情况
- 免费层级包含部分配额

详情请参阅 [Fly.io 定价](https://fly.io/docs/about/pricing/)。