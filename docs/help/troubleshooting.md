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

如果网关可达，执行深度探针：

```bash
openclaw status --deep
```

## 常见的“它坏了”情况

### `openclaw: command not found`

几乎总是 Node/npm 路径问题。从这里开始：

- [安装（Node/npm 路径合理性）](/install#nodejs--npm-path-sanity)

### 安装程序失败（或需要完整日志）

以详细模式重新运行安装程序以查看完整追踪和 npm 输出：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
```

对于 beta 安装：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
```

您也可以设置 `OPENCLAW_VERBOSE=1` 代替标志。

### 网关“未授权”，无法连接或持续重连

- [网关故障排除](/gateway/troubleshooting)
- [网关认证](/gateway/authentication)

### 控制 UI 在 HTTP 上失败（需要设备身份）

- [网关故障排除](/gateway/troubleshooting)
- [控制 UI](/web/control-ui#insecure-http)

### `docs.openclaw.ai` 显示 SSL 错误（Comcast/Xfinity）

某些 Comcast/Xfinity 连接通过 Xfinity 高级安全功能阻止 `docs.openclaw.ai`。
禁用高级安全功能或将 `docs.openclaw.ai` 添加到允许列表，然后重试。

- Xfinity 高级安全帮助：https://www.xfinity.com/support/articles/using-xfinity-xfi-advanced-security
- 快速合理性检查：尝试移动热点或 VPN 以确认是否为 ISP 级别过滤

### 服务显示运行中，但 RPC 探针失败

- [网关故障排除](/gateway/troubleshooting)
- [后台进程/服务](/gateway/background-process)

### 模型/认证失败（速率限制、计费、“所有模型失败”）

- [模型](/cli/models)
- [OAuth/认证概念](/concepts/oauth)

### `/model` 显示 `model not allowed`

这通常意味着 `agents.defaults.models` 配置为允许列表。当它非空时，
只能选择那些提供者/模型键。

- 检查允许列表：`openclaw config get agents.defaults.models`
- 添加您想要的模型（或清除允许列表）并重试 `/model`
- 使用 `/models` 浏览允许的提供者/模型

### 提交问题时

粘贴一个安全报告：

```bash
openclaw status --all
```

如果可以，请包含 `openclaw logs --follow` 的相关日志尾部。