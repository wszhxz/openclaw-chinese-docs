---
summary: "Quick troubleshooting guide for common OpenClaw failures"
read_when:
  - Investigating runtime issues or failures
title: "Troubleshooting"
---
# 故障排除 🔧

当 OpenClaw 行为异常时，请按照以下步骤进行修复。

如果您只是想快速诊断问题，可以先查看 FAQ 的 [前60秒](/help/faq#first-60-seconds-if-somethings-broken) 部分。本页面深入探讨运行时故障和诊断。

特定提供商的快捷方式：[/channels/troubleshooting](/channels/troubleshooting)

## 状态与诊断

快速诊断命令（按顺序）：

| 命令                            | 它告诉您什么                                                                                      | 何时使用它                                    |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| `openclaw status`                  | 本地摘要：操作系统+更新，网关可达性/模式，服务，代理/会话，提供商配置状态 | 第一检查，快速概览                       |
| `openclaw status --all`            | 完整本地诊断（只读，可粘贴，相对安全）包括日志尾部                                   | 当您需要共享调试报告时             |
| `openclaw status --deep`           | 运行网关健康检查（包括提供商探测；需要可达的网关）                         | 当“已配置”不等于“正在工作”          |
| `openclaw gateway probe`           | 网关发现+可达性（本地+远程目标）                                              | 当您怀疑探测了错误的网关 |
| `openclaw channels status --probe` | 请求正在运行的网关的通道状态（并可选探测）                                    | 当网关可达但通道行为异常  |
| `openclaw gateway status`          | 监督器状态（launchd/systemd/schtasks），运行时PID/退出，最后的网关错误                      | 当服务“看起来已加载”但没有运行  |
| `openclaw logs --follow`           | 实时日志（运行时问题的最佳信号）                                                             | 当您需要实际的失败原因           |

**共享输出：** 优先使用 `openclaw status --all`（它会屏蔽令牌）。如果您粘贴 `openclaw status`，请考虑先设置 `OPENCLAW_SHOW_SECRETS=0`（令牌预览）。

另见：[健康检查](/gateway/health) 和 [日志记录](/logging)。

## 常见问题

### 没有找到提供商 "anthropic" 的 API 密钥

这意味着 **代理的身份验证存储为空** 或缺少 Anthropic 凭证。
身份验证是 **每个代理** 的，新代理不会继承主代理的密钥。

修复选项：

- 重新运行入职程序并为该代理选择 **Anthropic**。
- 或者在 **网关主机** 上粘贴一个设置令牌：
  ```bash
  openclaw models auth setup-token --provider anthropic
  ```
- 或者从主代理目录复制 `auth-profiles.json` 到新代理目录。

验证：

```bash
openclaw models status
```

### OAuth 令牌刷新失败（Anthropic Claude 订阅）

这意味着存储的 Anthropic OAuth 令牌已过期且刷新失败。
如果您使用的是 Claude 订阅（无 API 密钥），最可靠的修复方法是
切换到 **Claude Code 设置令牌** 并粘贴到 **网关主机** 上。

**推荐（设置令牌）：**

```bash
# Run on the gateway host (paste the setup-token)
openclaw models auth setup-token --provider anthropic
openclaw models status
```

如果您在其他地方生成了令牌：

```bash
openclaw models auth paste-token --provider anthropic
openclaw models status
```

更多详情：[Anthropic](/providers/anthropic) 和 [OAuth](/concepts/oauth)。

### 控制 UI 在 HTTP 上失败 ("设备标识符必需" / "连接失败")

如果您通过纯 HTTP 打开仪表板（例如 `http://<lan-ip>:18789/` 或
`http://<tailscale-ip>:18789/`），浏览器会在 **非安全上下文** 中运行
并阻止 WebCrypto，因此无法生成设备标识符。

**修复：**

- 优先通过 [Tailscale Serve](/gateway/tailscale) 使用 HTTPS。
- 或者在网关主机上本地打开：`http://127.0.0.1:18789/`。
- 如果您必须使用 HTTP，请启用 `gateway.controlUi.allowInsecureAuth: true` 并
  使用网关令牌（仅令牌；无设备标识符/配对）。参见
  [控制 UI](/web/control-ui#insecure-http)。

### CI 密钥扫描失败

这意味着 `detect-secrets` 找到了不在基线中的新候选者。
遵循 [密钥扫描](/gateway/security#secret-scanning-detect-secrets)。

### 服务已安装但没有运行

如果网关服务已安装但进程立即退出，服务
可能会“已加载”但实际上没有运行。

**检查：**

```bash
openclaw gateway status
openclaw doctor
```

Doctor/服务将显示运行状态（PID/上次退出）和日志提示。

**日志：**

- 推荐：`openclaw logs --follow`
- 文件日志（始终）：`/tmp/openclaw/openclaw-YYYY-MM-DD.log`（或您的配置 `logging.file`）
- macOS LaunchAgent（如果已安装）：`$OPENCLAW_STATE_DIR/logs/gateway.log` 和 `gateway.err.log`
- Linux systemd（如果已安装）：`journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
- Windows: `schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

**启用更多日志：**

- 提升文件日志详细信息（持久化 JSONL）：
  ```json
  { "logging": { "level": "debug" } }
  ```
- 提升控制台详细程度（仅 TTY 输出）：
  ```json
  { "logging": { "consoleLevel": "debug", "consoleStyle": "pretty" } }
  ```
- 快速提示：`--verbose` 仅影响 **控制台** 输出。文件日志由 `logging.level` 控制。

参见 [/logging](/logging) 以获取格式、配置和访问的完整概述。

### "网关启动被阻止：设置 gateway.mode=local"

这意味着配置存在但 `gateway.mode` 未设置（或不是 `local`)，因此
网关拒绝启动。

**修复（推荐）：**

- 运行向导并将网关运行模式设置为 **本地**：
  ```bash
  openclaw configure
  ```
- 或者直接设置：
  ```bash
  openclaw config set gateway.mode local
  ```

**如果您打算运行远程网关：**

- 设置远程 URL 并保留 `gateway.mode=remote`：
  ```bash
  openclaw config set gateway.mode remote
  openclaw config set gateway.remote.url "wss://gateway.example.com"
  ```

**仅用于临时/开发：** 传递 `--allow-unconfigured` 以在没有
`gateway.mode=local` 的情况下启动网关。

**还没有配置文件？** 运行 `openclaw setup` 创建一个起始配置，然后重新运行
网关。

### 服务环境（PATH + 运行时）

网关服务使用 **最小的 PATH** 以避免 shell/管理器的杂乱：

- macOS: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `/bin`
- Linux: `/usr/local/bin`, `/usr/bin`, `/bin`

这故意排除了版本管理器（nvm/fnm/volta/asdf）和包管理器（pnpm/npm），因为服务不会加载您的 shell 初始化。运行时变量如 `DISPLAY` 应该位于 `~/.openclaw/.env`（由网关早期加载）。
Exec 运行在 `host=gateway` 合并您的登录 shell `PATH` 到 exec 环境，
因此缺少工具通常意味着您的 shell 初始化没有导出它们（或设置
`tools.exec.pathPrepend`)。参见 [/tools/exec](/tools/exec)。

WhatsApp 和 Telegram 通道需要 **Node**；Bun 不受支持。如果您的
服务使用 Bun 或版本管理的 Node 路径，运行 `openclaw doctor`
迁移到系统 Node 安装。

### 技能在沙盒中缺少 API 密钥

**症状：** 技能在主机上正常工作但在沙盒中由于缺少 API 密钥而失败。

**原因：** 沙盒化的 exec 在 Docker 内运行并且 **不** 继承主机 `process.env`。

**修复：**

- 设置 `agents.defaults.sandbox.docker.env`（或每个代理 `agents.list[].sandbox.docker.env`）
- 或将密钥烘焙到自定义沙盒镜像中
- 然后运行 `openclaw sandbox recreate --agent <id>`（或 `--all`）

### 服务正在运行但端口未监听

如果服务报告 **正在运行** 但网关端口上没有监听，网关很可能拒绝绑定。

**这里的“正在运行”含义**

- `Runtime: running` 表示您的监督器（launchd/systemd/schtasks）认为进程是活动的。
- `RPC probe` 表示 CLI 实际上可以连接到网关 WebSocket 并调用 `status`。
- 总是信任 `Probe target:` + `Config (service):` 作为“我们实际尝试了什么？”的行。

**检查：**

- `gateway.mode` 必须是 `local` 对于 `openclaw gateway` 和服务。
- 如果您设置了 `gateway.mode=remote`，**CLI 默认** 使用远程 URL。服务仍然可以本地运行，但您的 CLI 可能正在探测错误的位置。使用 `openclaw gateway status` 查看服务解析的端口 + 探测目标（或传递 `--url`）。
- `openclaw gateway status` 和 `openclaw doctor` 从日志中提取 **最后的网关错误** 当服务看起来正在运行但端口关闭时。
- 非回环绑定 (`lan`/`tailnet`/`custom`，或 `auto` 当回环不可用时) 需要认证：
  `gateway.auth.token` (或 `OPENCLAW_GATEWAY_TOKEN`)。
- `gateway.remote.token` 仅适用于远程 CLI 调用；它 **不** 启用本地认证。
- `gateway.token` 被忽略；使用 `gateway.auth.token`。

**如果 `openclaw gateway status` 显示配置不匹配**

- `Config (cli): ...` 和 `Config (service): ...` 通常应该匹配。
- 如果不匹配，您几乎肯定在服务运行另一个配置的同时编辑了一个配置。
- 修复：从相同的 `--profile` / `OPENCLAW_STATE_DIR` 重新运行 `openclaw gateway install --force` 您希望服务使用的。

**如果 `openclaw gateway status` 报告服务配置问题**

- 监督器配置（launchd/systemd/schtasks）缺少当前默认值。
- 修复：运行 `openclaw doctor` 更新它（或 `openclaw gateway install --force` 进行完整重写）。

**如果 `Last gateway error:` 提到“拒绝绑定 … 无认证”**

- 您将 `gateway.bind` 设置为非回环模式 (`lan`/`tailnet`/`custom`，或 `auto` 当回环不可用时) 但未配置认证。
- 修复：设置 `gateway.auth.mode` + `gateway.auth.token` (或导出 `OPENCLAW_GATEWAY_TOKEN`) 并重启服务。

**如果 `openclaw gateway status` 说 `bind=tailnet` 但未找到 tailnet 接口**

- 网关尝试绑定到 Tailscale IP (100.64.0.0/10) 但主机上未检测到。
- 修复：在该机器上启动 Tailscale（或将 `gateway.bind` 更改为 `loopback`/`lan`）。

**如果 `Probe note:` 说探测使用回环**

- 这对于 `bind=lan` 是预期的：网关监听 `0.0.0.0`（所有接口），回环应仍然可以本地连接。
- 对于远程客户端，使用实际的局域网 IP（不是 `0.0.0.0`) 加上端口，并确保已配置认证。

### 地址已被使用（端口 18789）

这意味着某些东西已经在监听网关端口。

**检查：**

```bash
openclaw gateway status
```

它将显示监听器及其可能的原因（网关已运行，SSH 隧道）。
如果需要，停止服务或选择不同的端口。

### 检测到额外的工作区文件夹

如果您从较旧的安装升级，磁盘上可能仍然有 `~/openclaw`。
多个工作区目录可能导致混乱的身份验证或状态漂移，因为
只有一个工作区处于活动状态。

**修复：** 保留一个活动工作区并归档/删除其余部分。参见
[代理工作区](/concepts/agent-workspace#extra-workspace-folders)。

### 主聊天在沙盒工作区中运行

症状：`pwd` 或文件工具显示 `~/.openclaw/sandboxes/...` 即使您
期望的是主机工作区。

**原因：** `agents.defaults.sandbox.mode: "non-main"` 依赖于 `session.mainKey`（默认 `"main"`）。
组/频道会话使用自己的密钥，因此被视为非主会话
并获得沙盒工作区。

**修复选项：**

- 如果您希望代理使用主机工作区：设置 `agents.list[].sandbox.mode: "off"`。
- 如果您希望在沙盒中访问主机工作区：为该代理设置 `workspaceAccess: "rw"`。

### "代理被中止"

代理在响应过程中被中断。

**原因：**

- 用户发送了 `stop`, `abort`, `esc`, `wait`, 或 `exit`
- 超时
- 进程崩溃

**修复：** 只需再发送一条消息。会话继续。

### "代理在回复前失败：未知模型：anthropic/claude-haiku-3-5"

OpenClaw 故意拒绝 **旧的/不安全的模型**（尤其是那些更容易受到提示注入的模型）。如果您看到此错误，该模型名称不再受支持。

**修复：**

- 为提供商选择一个 **最新的** 模型并更新您的配置或模型别名。
- 如果您不确定哪些模型可用，运行 `openclaw models list` 或
  `openclaw models scan` 并选择一个受支持的模型。
- 检查网关日志以获取详细的失败原因。

另见：[模型 CLI](/cli/models) 和 [模型提供商](/concepts/model-providers)。

### 消息未触发

**检查 1：** 发送者是否被列入白名单？

```bash
openclaw status
```

查找输出中的 `AllowFrom: ...`。

**检查 2：** 对于群聊，是否需要提及？

```bash
# The message must match mentionPatterns or explicit mentions; defaults live in channel groups/guilds.
# Multi-agent: `agents.list[].groupChat.mentionPatterns` overrides global patterns.
grep -n "agents\\|groupChat\\|mentionPatterns\\|channels\\.whatsapp\\.groups\\|channels\\.telegram\\.groups\\|channels\\.imessage\\.groups\\|channels\\.discord\\.guilds" \
  "${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw/openclaw.json}"
```

**检查 3：** 检查日志

```bash
openclaw logs --follow
# or if you want quick filters:
tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)" | grep "blocked\\|skip\\|unauthorized"
```

### 配对码未到达

如果 `dmPolicy` 是 `pairing`，未知发送者应收到一个代码，他们的消息在批准之前会被忽略。

**检查 1：** 是否已经有待处理的请求在等待？

```bash
openclaw pairing list <channel>
```

待处理的 DM 配对请求默认每个通道最多 **3 个**。如果列表已满，新的请求不会生成代码，直到其中一个被批准或过期。

**检查 2：** 请求是否已创建但没有回复？

```bash
openclaw logs --follow | grep "pairing request"
```

**检查 3：** 确认 `dmPolicy` 不是 `open`/`allowlist` 对于该通道。

### 图片 + 提及不起作用

已知问题：当您仅发送带有提及（无其他文本）的图片时，WhatsApp 有时不会包含提及元数据。

**解决方法：** 添加一些带有提及的文本：

- ❌ `@openclaw` + 图片
- ✅ `@openclaw check this` + 图片

### 会话未恢复

**检查 1：** 会话文件是否存在？

```bash
ls -la ~/.openclaw/agents/<agentId>/sessions/
```

**检查 2：** 重置窗口是否太短？

```json
{
  "session": {
    "reset": {
      "mode": "daily",
      "atHour": 4,
      "idleMinutes": 10080 // 7 days
    }
  }
}
```

**检查 3：** 是否有人发送了 `/new`, `/reset` 或重置触发器？

### 代理超时

默认超时时间为 30 分钟。对于长时间任务：

```json
{
  "reply": {
    "timeoutSeconds": 3600 // 1 hour
  }
}
```

或者使用 `process` 工具将长时间命令放入后台。

### WhatsApp 断开连接

```bash
# Check local status (creds, sessions, queued events)
openclaw status
# Probe the running gateway + channels (WA connect + Telegram + Discord APIs)
openclaw status --deep

# View recent connection events
openclaw logs --limit 200 | grep "connection\\|disconnect\\|logout"
```

**修复：** 通常网关运行后会自动重新连接。如果卡住，重启网关进程（无论您如何监督它），或手动运行并启用详细输出：

```bash
openclaw gateway --verbose
```

如果已注销/未链接：

```bash
openclaw channels logout
trash "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials" # if logout can't cleanly remove everything
openclaw channels login --verbose       # re-scan QR
```

### 媒体发送失败

**检查 1：** 文件路径是否有效？

```bash
ls -la /path/to/your/image.jpg
```

**检查 2：** 文件是否太大？

- 图片：最大 6MB
- 音频/视频：最大 16MB
- 文档：最大 100MB

**检查 3：** 检查媒体日志

```bash
grep "media\\|fetch\\|download" "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)" | tail -20
```

### 高内存使用率

OpenClaw 将对话历史保留在内存中。

**修复：** 定期重启或设置会话限制：

```json
{
  "session": {
    "historyLimit": 100 // Max messages to keep
  }
}
```

## 常见故障排除

### “网关无法启动 — 配置无效”

OpenClaw 现在在配置包含未知键、格式错误的值或无效类型时拒绝启动。
这是出于安全性的有意行为。

使用 Doctor 修复：

```bash
openclaw doctor
openclaw doctor --fix
```

注意：

- `openclaw doctor` 报告每个无效条目。
- __CODE_BLOCK_151