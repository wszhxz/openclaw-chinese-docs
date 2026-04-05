---
summary: "CLI reference for `openclaw dns` (wide-area discovery helpers)"
read_when:
  - You want wide-area discovery (DNS-SD) via Tailscale + CoreDNS
  - You’re setting up split DNS for a custom discovery domain (example: openclaw.internal)
title: "dns"
---
# `openclaw dns`

DNS 广域网发现助手（Tailscale + CoreDNS）。当前专注于 macOS + Homebrew CoreDNS。

相关：

- 网关发现：[发现](/gateway/discovery)
- 广域网发现配置：[配置](/gateway/configuration)

## 设置

```bash
openclaw dns setup
openclaw dns setup --domain openclaw.internal
openclaw dns setup --apply
```

## `dns setup`

为单播 DNS-SD 发现计划或应用 CoreDNS 设置。

选项：

- `--domain <domain>`: 广域网发现域名（例如 `openclaw.internal`）
- `--apply`: 安装或更新 CoreDNS 配置并重启服务（需要 sudo；仅限 macOS）

显示内容：

- 解析后的发现域名
- 区域文件路径
- 当前 tailnet IP
- 推荐的 `openclaw.json` 发现配置
- 要设置的 Tailscale Split DNS 名称服务器/域名值

注意：

- 若未提供 `--apply`，该命令仅为规划助手，并输出推荐设置。
- 如果省略 `--domain`，OpenClaw 将从配置中使用 `discovery.wideArea.domain`。
- `--apply` 目前仅支持 macOS，且预期使用 Homebrew CoreDNS。
- `--apply` 如有需要则初始化区域文件，确保存在 CoreDNS 导入部分，并重启 `coredns` brew 服务。