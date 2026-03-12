---
summary: "CLI reference for `openclaw dashboard` (open the Control UI)"
read_when:
  - You want to open the Control UI with your current token
  - You want to print the URL without launching a browser
title: "dashboard"
---
# `openclaw dashboard`

使用当前的身份验证凭据打开控制界面。

```bash
openclaw dashboard
openclaw dashboard --no-open
```

注意事项：

- `dashboard` 在可能的情况下解析已配置的 `gateway.auth.token` SecretRefs。
- 对于由 SecretRef 管理的令牌（无论是否已解析），`dashboard` 会打印/复制/打开一个未经令牌化的 URL，以避免在终端输出、剪贴板历史记录或浏览器启动参数中泄露外部密钥。
- 如果 `gateway.auth.token` 是由 SecretRef 管理但在当前命令路径中未被解析，则该命令将打印一个未经令牌化的 URL 及明确的修复指导，而不是嵌入一个无效的令牌占位符。