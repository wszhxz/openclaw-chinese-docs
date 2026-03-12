---
summary: "Use Qwen OAuth (free tier) in OpenClaw"
read_when:
  - You want to use Qwen with OpenClaw
  - You want free-tier OAuth access to Qwen Coder
title: "Qwen"
---
# 通义千问

通义千问为通义千问Coder和通义千问Vision模型提供免费层级的OAuth流程  
（每日2,000次请求，受通义千问速率限制约束）。

## 启用插件

```bash
openclaw plugins enable qwen-portal-auth
```

启用后请重启网关。

## 认证

```bash
openclaw models auth login --provider qwen-portal --set-default
```

此命令将运行通义千问设备码OAuth流程，并向您的  
`models.json` 写入一个提供方条目（同时创建一个 `qwen` 别名以便快速切换）。

## 模型ID

- `qwen-portal/coder-model`  
- `qwen-portal/vision-model`  

通过以下命令切换模型：

```bash
openclaw models set qwen-portal/coder-model
```

## 复用通义千问Code CLI登录信息

如果您已使用通义千问Code CLI完成登录，OpenClaw在加载认证存储时将自动从  
`~/.qwen/oauth_creds.json` 同步凭据。您仍需配置一个  
`models.providers.qwen-portal` 条目（可使用上方登录命令创建）。

## 注意事项

- Token支持自动刷新；若刷新失败或访问权限被撤销，请重新运行登录命令。  
- 默认基础URL：`https://portal.qwen.ai/v1`（如通义千问提供了不同的端点，可通过  
  `models.providers.qwen-portal.baseUrl` 覆盖该设置）。  
- 有关提供方范围内的通用规则，请参阅[模型提供方](/concepts/model-providers)。