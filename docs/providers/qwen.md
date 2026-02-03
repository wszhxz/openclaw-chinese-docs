---
summary: "Use Qwen OAuth (free tier) in OpenClaw"
read_when:
  - You want to use Qwen with OpenClaw
  - You want free-tier OAuth access to Qwen Coder
title: "Qwen"
---
# 通义千问

通义千问为通义千问代码模型和通义千问视觉模型提供免费层级的OAuth流程
（每日2,000次请求，受通义速率限制约束）。

## 启用插件

```bash
openclaw plugins enable qwen-portal-auth
```

启用后重启网关。

## 认证

```bash
openclaw models auth login --provider qwen-portal --set-default
```

此操作运行通义设备码OAuth流程，并将提供者条目写入您的
`models.json`（同时添加一个`qwen`别名以便快速切换）。

## 模型ID

- `qwen-portal/coder-model`
- `qwen-portal/vision-model`

切换模型使用：

```bash
openclaw models set qwen-portal/coder-model
```

## 重用通义代码CLI登录

如果您已使用通义代码CLI登录，OpenClaw会在加载认证存储时从 `~/.qwen/oauth_creds.json` 同步凭证。您仍需要一个
`models.providers.qwen-portal` 条目（使用上方登录命令创建该条目）。

## 注意事项

- 令牌会自动刷新；如果刷新失败或访问被撤销，请重新运行登录命令。
- 默认基础URL：`https://portal.qwen.ai/v1`（若通义提供不同的端点，请使用
  `models.providers.qwen-portal.baseUrl` 覆盖）。
- 有关提供者范围的规则，请参阅 [模型提供者](/concepts/model-providers)。