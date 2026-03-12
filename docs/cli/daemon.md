---
summary: "CLI reference for `openclaw daemon` (legacy alias for gateway service management)"
read_when:
  - You still use `openclaw daemon ...` in scripts
  - You need service lifecycle commands (install/start/stop/restart/status)
title: "daemon"
---
# `openclaw daemon`

网关服务管理命令的旧别名。

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

- `status`: 显示服务安装状态并探测网关健康状况  
- `install`: 安装服务（`launchd`/`systemd`/`schtasks`）  
- `uninstall`: 卸载服务  
- `start`: 启动服务  
- `stop`: 停止服务  
- `restart`: 重启服务  

## 常用选项

- `status`: `--url`, `--token`, `--password`, `--timeout`, `--no-probe`, `--deep`, `--json`  
- `install`: `--port`, `--runtime <node|bun>`, `--token`, `--force`, `--json`  
- 生命周期（`uninstall|start|stop|restart`）: `--json`  

注意事项：

- `status` 在可能的情况下，解析配置的 auth SecretRefs 以用于探测认证。  
- 在 Linux systemd 安装中，`status` 的 token-drift 检查同时涵盖 `Environment=` 和 `EnvironmentFile=` 单元源。  
- 当 token 认证需要一个 token，且 `gateway.auth.token` 由 SecretRef 管理时，`install` 会验证该 SecretRef 是否可解析，但不会将解析出的 token 持久化到服务环境元数据中。  
- 如果 token 认证需要一个 token，而配置的 token SecretRef 无法解析，则安装操作将失败并关闭。  
- 如果同时配置了 `gateway.auth.token` 和 `gateway.auth.password`，且 `gateway.auth.mode` 未设置，则安装操作将被阻塞，直至显式设置 mode。

## 推荐

请使用 [`openclaw gateway`](/cli/gateway) 获取当前文档和示例。