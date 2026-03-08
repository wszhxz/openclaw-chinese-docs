---
summary: "CLI reference for `openclaw daemon` (legacy alias for gateway service management)"
read_when:
  - You still use `openclaw daemon ...` in scripts
  - You need service lifecycle commands (install/start/stop/restart/status)
title: "daemon"
---
# `openclaw daemon`

网关服务的旧版别名。

`openclaw daemon ...` 与 `openclaw gateway ...` 服务命令映射到相同的服务控制面。

## 用法

```bash
openclaw daemon status
openclaw daemon install
openclaw daemon start
openclaw daemon stop
openclaw daemon restart
openclaw daemon uninstall
```

## 子命令

- `status`: 显示服务安装状态并探测网关健康状态
- `install`: 安装服务 (`launchd`/`systemd`/`schtasks`)
- `uninstall`: 移除服务
- `start`: 启动服务
- `stop`: 停止服务
- `restart`: 重启服务

## 通用选项

- `status`: `--url`, `--token`, `--password`, `--timeout`, `--no-probe`, `--deep`, `--json`
- `install`: `--port`, `--runtime <node|bun>`, `--token`, `--force`, `--json`
- 生命周期 (`uninstall|start|stop|restart`): `--json`

注意：

- `status` 在可能时解析用于探测认证的已配置 auth SecretRefs。
- 在 Linux systemd 安装中，`status` token-drift 检查包括 `Environment=` 和 `EnvironmentFile=` 单元源。
- 当 token auth 需要 token 且 `gateway.auth.token` 为 SecretRef 管理时，`install` 验证 SecretRef 是否可解析，但不将解析后的 token 持久化到服务环境元数据中。
- 如果 token auth 需要 token 且配置的 token SecretRef 未解析，安装失败。
- 如果同时配置了 `gateway.auth.token` 和 `gateway.auth.password` 且 `gateway.auth.mode` 未设置，安装将被阻止，直到显式设置模式。

## 推荐

使用 [`openclaw gateway`](/cli/gateway) 获取当前文档和示例。