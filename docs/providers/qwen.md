---
summary: "Use Qwen OAuth (free tier) in OpenClaw"
read_when:
  - You want to use Qwen with OpenClaw
  - You want free-tier OAuth access to Qwen Coder
title: "Qwen"
---
# Qwen

Qwen 提供了一个免费层级的 OAuth 流程用于 Qwen Coder 和 Qwen Vision 模型
（每天 2,000 次请求，受 Qwen 速率限制）。

## 启用插件

```bash
openclaw plugins enable qwen-portal-auth
```

启用后重启网关。

## 认证

```bash
openclaw models auth login --provider qwen-portal --set-default
```

这将运行 Qwen 设备代码 OAuth 流程，并将一个提供者条目写入你的
`models.json`（以及一个 `qwen` 别名以便快速切换）。

## 模型 ID

- `qwen-portal/coder-model`
- `qwen-portal/vision-model`

使用以下命令切换模型：

```bash
openclaw models set qwen-portal/coder-model
```

## 重用 Qwen Code CLI 登录

如果你已经使用 Qwen Code CLI 登录过，OpenClaw 将在加载认证存储时从 `~/.qwen/oauth_creds.json` 同步凭据。
你仍然需要一个 `models.providers.qwen-portal` 条目（使用上面的登录命令创建一个）。

## 注意事项

- 令牌会自动刷新；如果刷新失败或访问被撤销，请重新运行登录命令。
- 默认基础 URL：`https://portal.qwen.ai/v1`（如果 Qwen 提供不同的端点，则使用 `models.providers.qwen-portal.baseUrl` 覆盖）。
- 有关提供者范围的规则，请参阅 [模型提供者](/concepts/model-providers)。