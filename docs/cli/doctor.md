---
summary: "CLI reference for `openclaw doctor` (health checks + guided repairs)"
read_when:
  - You have connectivity/auth issues and want guided fixes
  - You updated and want a sanity check
title: "doctor"
---
# 健康检查 + 网关与通道的快速修复

相关文档：

- 故障排除：[故障排除](/gateway/troubleshooting)  
- 安全审计：[安全性](/gateway/security)

## 示例

```bash
$ gateway doctor
```

注意事项：

- 交互式提示（例如密钥链/OAuth 修复）仅在 `stdin` 为 TTY 且 `--non-interactive` **未设置** 时运行。无头环境（如 cron、Telegram、无终端）将跳过所有提示。
- `--fix`（`--repair` 的别名）会将备份写入 `~/.openclaw/openclaw.json.bak`，并丢弃未知的配置项，同时逐条列出被移除的配置项。
- 状态完整性检查现已能够检测会话目录中孤立的转录文件，并可将其归档为 `.deleted.<timestamp>`，以安全地释放磁盘空间。
- `doctor` 包含内存搜索就绪性检查，并可在嵌入式凭据缺失时推荐使用 `openclaw configure --section model`。
- 若启用了沙箱模式但 Docker 不可用，`doctor` 将报告一个高置信度警告，并提供修复建议（`install Docker` 或 `openclaw config set agents.defaults.sandbox.mode off`）。

## macOS：`launchctl` 环境变量覆盖

如果您此前运行过 `launchctl setenv OPENCLAW_GATEWAY_TOKEN ...`（或 `...PASSWORD`），该值将覆盖您的配置文件，可能导致持续出现“未授权”错误。

```bash
$ unset GATEWAY_API_KEY
```