---
summary: "CLI reference for `openclaw daemon` (legacy alias for gateway service management)"
read_when:
  - You still use `openclaw daemon ...` in scripts
  - You need service lifecycle commands (install/start/stop/restart/status)
title: "daemon"
---
# `openclaw daemon`

Gateway 服务管理命令的旧版别名。

`openclaw daemon ...` 映射到与 `openclaw gateway ...` 服务命令相同的服务控制面。

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

- `status`: `--url`, `--token`, `--password`, `--timeout`, `--no-probe`, `--require-rpc`, `--deep`, `--json`
- `install`: `--port`, `--runtime <node|bun>`, `--token`, `--force`, `--json`
- 生命周期 (`uninstall|start|stop|restart`): `--json`

注意：

- `status` 在可能时解析用于探测认证的已配置 auth SecretRefs。
- 如果此命令路径中所需的 auth SecretRef 未解析，当探测连接/认证失败时，`daemon status --json` 报告 `rpc.authWarning`；请显式传递 `--token`/`--password` 或先解析秘密源。
- 如果探测成功，则抑制未解析的 auth-ref 警告以避免误报。
- `status --deep` 添加尽力而为的系统级服务扫描。当它找到其他类似网关的服务时，用户输出会打印清理提示，并警告每台机器一个网关仍然是正常推荐。
- 在 Linux systemd 安装上，`status` token-drift 检查包括 `Environment=` 和 `EnvironmentFile=` 单元源。
- 漂移检查使用合并的运行时环境解析 `gateway.auth.token` SecretRefs（优先使用服务命令环境，然后回退到进程环境）。
- 如果 token auth 未有效激活（明确设置 `gateway.auth.mode` 为 `password`/`none`/`trusted-proxy`，或模式未设置且密码可胜出且无 token 候选者可获胜），token-drift 检查跳过配置 token 解析。
- 当 token auth 需要 token 且 `gateway.auth.token` 由 SecretRef 管理时，`install` 验证 SecretRef 是否可解析，但不将解析后的 token 持久化到服务环境元数据中。
- 如果 token auth 需要 token 且配置的 token SecretRef 未解析，安装将失败关闭。
- 如果同时配置了 `gateway.auth.token` 和 `gateway.auth.password` 且 `gateway.auth.mode` 未设置，则安装将被阻止，直到显式设置模式。
- 如果您有意在一台主机上运行多个网关，请隔离端口、配置/状态和工作区；参见 [/gateway#multiple-gateways-same-host](/gateway#multiple-gateways-same-host)。

## 建议

请使用 [`openclaw gateway`](/cli/gateway) 获取当前文档和示例。