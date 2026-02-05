---
summary: "Troubleshooting hub: symptoms → checks → fixes"
read_when:
  - You see an error and want the fix path
  - The installer says “success” but the CLI doesn’t work
title: "Troubleshooting"
---
# 故障排除

## 前60秒

按顺序运行以下命令：

```bash
openclaw status
openclaw status --all
openclaw gateway probe
openclaw logs --follow
openclaw doctor
```

如果网关可达，进行深入探测：

```bash
openclaw status --deep
```

## 常见的“坏了”情况

### `openclaw: command not found`

几乎总是Node/npm PATH问题。从这里开始：

- [安装 (Node/npm PATH 检查)](/install#nodejs--npm-path-sanity)

### 安装程序失败（或需要完整日志）

以详细模式重新运行安装程序以查看完整跟踪和npm输出：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
```

对于测试版安装：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
```

您也可以设置`OPENCLAW_VERBOSE=1`而不是标志。

### 网关“未授权”，无法连接，或不断重新连接

- [网关故障排除](/gateway/troubleshooting)
- [网关身份验证](/gateway/authentication)

### 控制UI在HTTP上失败（需要设备身份）

- [网关故障排除](/gateway/troubleshooting)
- [控制UI](/web/control-ui#insecure-http)

### `docs.openclaw.ai` 显示SSL错误（Comcast/Xfinity）

一些Comcast/Xfinity连接通过Xfinity高级安全阻止`docs.openclaw.ai`。
禁用高级安全或在允许列表中添加`docs.openclaw.ai`，然后重试。

- Xfinity高级安全帮助：https://www.xfinity.com/support/articles/using-xfinity-xfi-advanced-security
- 快速检查：尝试移动热点或VPN以确认是ISP级别的过滤

### 服务显示正在运行，但RPC探测失败

- [网关故障排除](/gateway/troubleshooting)
- [后台进程 / 服务](/gateway/background-process)

### 模型/身份验证失败（速率限制，计费，“所有模型失败”）

- [模型](/cli/models)
- [OAuth / 身份验证概念](/concepts/oauth)

### `/model` 显示 `model not allowed`

这通常意味着`agents.defaults.models`被配置为允许列表。当它不为空时，
只有这些提供商/模型密钥可以被选择。

- 检查允许列表：`openclaw config get agents.defaults.models`
- 添加您想要的模型（或清除允许列表），然后重试`/model`
- 使用`/models`浏览允许的提供商/模型

### 当提交问题时

粘贴一个安全报告：

```bash
openclaw status --all
```

如果可以，请包含来自`openclaw logs --follow`的相关日志尾部。