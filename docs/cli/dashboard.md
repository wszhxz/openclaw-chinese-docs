---
summary: "CLI reference for `openclaw dashboard` (open the Control UI)"
read_when:
  - You want to open the Control UI with your current token
  - You want to print the URL without launching a browser
title: "dashboard"
---
# `openclaw dashboard`

使用当前的 auth 打开 Control UI。

```bash
openclaw dashboard
openclaw dashboard --no-open
```

注意事项：

- `dashboard` 会在可能的情况下解析已配置的 `gateway.auth.token` SecretRefs。
- 对于 SecretRef-managed tokens（已解析或未解析），`dashboard` 会打印/复制/打开一个 non-tokenized URL，以避免在终端输出、剪贴板历史或浏览器启动参数中暴露外部 secrets。
- 如果 `gateway.auth.token` 是 SecretRef-managed 但在此命令路径中未解析，该命令会打印一个 non-tokenized URL 和明确的修复指导，而不是嵌入无效的 token 占位符。