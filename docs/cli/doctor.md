---
summary: "CLI reference for `openclaw doctor` (health checks + guided repairs)"
read_when:
  - You have connectivity/auth issues and want guided fixes
  - You updated and want a sanity check
title: "doctor"
---
# `openclaw doctor`

网关和通道的健康检查与快速修复。

相关：

- 故障排除：[故障排除](/gateway/troubleshooting)
- 安全审计：[安全](/gateway/security)

## 示例

```bash
openclaw doctor
openclaw doctor --repair
openclaw doctor --deep
openclaw doctor --repair --non-interactive
openclaw doctor --generate-gateway-token
```

## 选项

- `--no-workspace-suggestions`: 禁用工作区内存/搜索建议
- `--yes`: 接受默认值而不提示
- `--repair`: 应用推荐的修复而无需提示
- `--fix`: `--repair` 的别名
- `--force`: 应用激进修复，包括必要时覆盖自定义服务配置
- `--non-interactive`: 无提示运行；仅安全迁移
- `--generate-gateway-token`: 生成并配置网关令牌
- `--deep`: 扫描系统服务以查找额外的网关安装

注意：

- 交互式提示（如钥匙串/OAuth 修复）仅在 stdin 为 TTY 且 `--non-interactive` 未被设置时运行。无头运行（cron、Telegram、无终端）将跳过提示。
- `--fix`（`--repair` 的别名）将备份写入 `~/.openclaw/openclaw.json.bak` 并删除未知配置键，列出每个被删除项。
- 状态完整性检查现在可检测 sessions 目录中的孤立转录文件，并可将其归档为 `.deleted.<timestamp>` 以安全释放空间。
- Doctor 还扫描 `~/.openclaw/cron/jobs.json`（或 `cron.store`）以查找遗留的 cron 作业形态，并可在调度器在运行时自动规范化它们之前就地重写它们。
- Doctor 自动迁移遗留的扁平 Talk 配置（`talk.voiceId`、`talk.modelId` 及其同类项）到 `talk.provider` + `talk.providers.<provider>`。
- 重复运行 `doctor --fix` 不再报告/应用 Talk 规范化，除非唯一差异是对象键顺序。
- Doctor 包含内存搜索就绪性检查，当缺少嵌入凭据时可推荐 `openclaw configure --section model`。
- 如果启用了沙盒模式但 Docker 不可用，doctor 会报告显著警告并提供修复方案（`install Docker` 或 `openclaw config set agents.defaults.sandbox.mode off`）。
- 如果 `gateway.auth.token`/`gateway.auth.password` 由 SecretRef 管理且在当前命令路径中不可用，doctor 会报告只读警告且不写入明文回退凭据。
- 如果在修复路径中通道 SecretRef 检查失败，doctor 将继续运行并报告警告，而不是提前退出。
- Telegram `allowFrom` 用户名自动解析（`doctor --fix`）需要当前命令路径中存在可解析的 Telegram 令牌。如果令牌检查不可用，doctor 会报告警告并跳过该次运行的自动解析。

## macOS: `launchctl` 环境变量覆盖

如果您之前运行过 `launchctl setenv OPENCLAW_GATEWAY_TOKEN ...`（或 `...PASSWORD`），该值会覆盖您的配置文件并可能导致持续的“未经授权”错误。

```bash
launchctl getenv OPENCLAW_GATEWAY_TOKEN
launchctl getenv OPENCLAW_GATEWAY_PASSWORD

launchctl unsetenv OPENCLAW_GATEWAY_TOKEN
launchctl unsetenv OPENCLAW_GATEWAY_PASSWORD
```