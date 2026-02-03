---
summary: "OpenClaw CLI reference for `openclaw` commands, subcommands, and options"
read_when:
  - Adding or modifying CLI commands or options
  - Documenting new command surfaces
title: "CLI Reference"
---
以下是您提供的英文内容的中文翻译：

---

**翻译：**

**系统**  
`system event`  
排队系统事件并可选触发心跳（网关RPC）。  
必需：  
- `--text <text>`  

选项：  
- `--mode <now|next-heartbeat>`  
- `--json`  
- `--url`, `--token`, `--timeout`, `--expect-final`  

`system heartbeat last|enable|disable`  
心跳控制（网关RPC）。  
选项：  
- `--json`  
- `--url`, `--token`, `--timeout`, `--expect-final`  

`system presence`  
列出系统存在状态条目（网关RPC）。  
选项：  
- `--json`  
- `--url`, `--token`, `--timeout`, `--expect-final`  

---

**定时任务**  
管理计划任务（网关RPC）。详见 [/automation/cron-jobs](/automation/cron-jobs)。  

子命令：  
- `cron status [--json]`  
- `cron list [--all] [--json]`（默认表格输出；使用 `--json` 获取原始数据）  
- `cron add`（别名：`create`；需 `--name` 和 `--at` | `--every` | `--cron` 中的一个，以及 `--system-event` | `--message` 中的一个负载）  
- `cron edit <id>`（修补字段）  
- `cron rm <id>`（别名：`remove`, `delete`）  
- `cron enable <id>`  
- `cron disable <id>`  
- `cron runs --id <id> [--limit <n>]`  
- `cron run <id> [--force]`  

所有 `cron` 命令均支持 `--url`, `--token`, `--timeout`, `--expect-final`。  

---

**节点主机**  
`node` 运行一个 **无头节点主机** 或将其作为后台服务管理。详见 [`openclaw node`](/cli/node)。  

子命令：  
- `node run --host <gateway-host> --port 18789`  
- `node status`  
- `node install [--host <gateway-host>] [--port <port>] [--tls] [--tls-fingerprint <sha256>] [--node-id <id>] [--display-name <name>] [--runtime <node|bun>] [--force]`  
- `node uninstall`  
- `node stop`  
- `node restart`  

---

**节点**  
`nodes` 与网关通信并针对配对的节点。详见 [/nodes](/nodes)。  

常用选项：  
- `--url`, `--token`, `--timeout`, `--json`  

子命令：  
- `nodes status [--connected] [--last-connected <duration>]`  
- `nodes describe --node <id|name|ip>`  
- `nodes list [--connected] [--last-connected <duration>]`  
- `nodes pending`  
- `nodes approve <requestId>`  
- `nodes reject <requestId>`  
- `nodes rename --node <id|name|ip> --name <displayName>`  
- `nodes invoke --node <id|name|ip> --command <command> [--params <json>] [--invoke-timeout <ms>] [--idempotency-key <key>]`  
- `nodes run --node <id|name|ip> [--cwd <path>] [--env KEY=VAL] [--command-timeout <ms>] [--needs-screen-recording] [--invoke-timeout <ms>] <command...>`（mac节点或无头节点主机）  
- `nodes notify --node <id|name|ip> [--title <text>] [--body <text>] [--sound <name>] [--priority <passive|active|timeSensitive>] [--delivery <system|overlay|auto>] [--invoke-timeout <ms>]`（仅限mac）  

**相机：**  
- `nodes camera list --node <id|name|ip>`  
- `nodes camera snap --node <id|name|ip> [--facing front|back|both] [--device-id <id>] [--max-width <px>] [--quality <0-1>] [--delay-ms <ms>] [--invoke-timeout <ms>]`  
- `nodes camera clip --node <id|name|ip> [--facing front|back] [--device-id <id>] [--duration <ms|10s|1m>] [--no-audio] [--invoke

（由于内容过长，此处仅展示部分翻译。完整翻译需继续处理剩余部分，确保技术术语准确且格式清晰。）