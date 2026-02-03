---
summary: "CLI reference for `openclaw dns` (wide-area discovery helpers)"
read_when:
  - You want wide-area discovery (DNS-SD) via Tailscale + CoreDNS
  - You’re setting up split DNS for a custom discovery domain (example: openclaw.internal)
title: "dns"
---
# `openclaw dns`

用于广域网发现的DNS辅助工具（Tailscale + CoreDNS）。目前专注于macOS + Homebrew CoreDNS。

相关：

- 网关发现：[发现](/gateway/discovery)
- 广域网发现配置：[配置](/gateway/configuration)

## 安装

```bash
openclaw dns setup
openclaw dns setup --apply
```