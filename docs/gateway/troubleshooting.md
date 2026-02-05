---
summary: "Quick troubleshooting guide for common OpenClaw failures"
read_when:
  - Investigating runtime issues or failures
title: "Troubleshooting"
---
# 故障排除 🔧

当 OpenClaw 行为异常时，以下是修复方法。

如果您只是想快速诊断，请从 FAQ 的 [前60秒](/help/faq#first-60-seconds-if-somethings-broken) 开始。本页深入探讨运行时故障和诊断。

特定提供商的快捷方式：[/channels/troubleshooting](/channels/troubleshooting)

## 状态与诊断

快速诊断命令（按顺序）：

| 命令                            | 它告诉您什么                                                                                      | 何时使用它                                    |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------- |
| `openclaw status`                  | 本地摘要：操作系统 + 更新，网关可达性/模式，服务，代理/会话，提供商配置状态 | 首次检查，快速概览                       |
| `openclaw status --all`            | 完整的本地诊断（只读，可粘贴，相对安全）包括日志尾部                                   | 当您需要共享调试报告             |
| `openclaw status --deep`           | 运行网关健康检查（包括提供商探测；需要可达的网关）                         | 当“已配置”不等于“正常工作”          |
| `openclaw gateway probe`           | 网关发现 + 可达性（本地 + 远程目标）                                              | 当您怀疑探测了错误的网关 |
| `openclaw channels status --probe` | 请求正在运行的网关通道状态（并可选探测）                                    | 当网关可达但通道行为异常  |
| `openclaw gateway status`          | 监督器状态（launchd/systemd/schtasks），运行时PID/退出，最后的网关错误                      | 当服务“看起来已加载”但没有运行  |
| `openclaw logs --follow`           | 实时日志（运行时问题的最佳信号）                                                             | 当您需要实际的失败原因           |

**共享输出：** 建议使用 `openclaw status --all`（它会隐藏令牌）。如果您粘贴 `openclaw status`，请考虑先设置 `OPENCLAW_SHOW_SECRETS=0`（令牌预览）。

另见：[健康检查](/gateway/health) 和 [日志记录](/logging)。

## 常见问题

### 未找到提供商 "anthropic" 的 API 密钥

这意味着 **代理的身份验证存储为空** 或缺少 Anthropic 凭证。
身份验证是 **每个代理** 的，新代理不会继承主代理的密钥。

解决选项：

- 重新运行入职流程并为该代理选择 **Anthropic**。
- 或在 **网关主机** 上粘贴一个设置令牌：
  ```bash
  openclaw models auth setup-token --provider anthropic
  ```
- 或从主代理目录复制 `auth-profiles.json` 到新代理目录。

验证：

```bash
openclaw models status
```

### OAuth token refresh failed (Anthropic Claude subscription)

这意味着存储的Anthropic OAuth令牌已过期且刷新失败。
如果您使用的是Claude订阅（无API密钥），最可靠的解决方法是
切换到一个 **Claude Code setup-token** 并将其粘贴到 **网关主机** 上。

**推荐（setup-token）：**

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

### 控制UI在HTTP上失败 ("需要设备身份" / "连接失败")

如果您通过纯HTTP（例如 `http://<lan-ip>:18789/` 或
`http://<tailscale-ip>:18789/`）打开仪表板，浏览器将在 **非安全上下文** 中运行
并阻止WebCrypto，因此无法生成设备身份。

**解决方法：**

- 优先使用HTTPS通过 [Tailscale Serve](/gateway/tailscale)。
- 或者在网关主机上本地打开：`http://127.0.0.1:18789/`。
- 如果您必须使用HTTP，请启用 `gateway.controlUi.allowInsecureAuth: true` 并
  使用网关令牌（仅令牌；无需设备身份/配对）。参见
  [控制UI](/web/control-ui#insecure-http)。

### CI Secrets Scan Failed

这意味着 `detect-secrets` 找到了新的候选者尚未在基线中。
按照 [Secret scanning](/gateway/security#secret-scanning-detect-secrets) 进行操作。

### 服务已安装但没有运行

如果网关服务已安装但进程立即退出，服务
可能会显示为“已加载”而实际上没有运行。

**检查：**

```bash
openclaw gateway status
openclaw doctor
```

Doctor/service 将显示运行状态（PID/最后退出）和日志提示。

**日志：**

- 推荐：`openclaw logs --follow`
- 文件日志（始终）：`/tmp/openclaw/openclaw-YYYY-MM-DD.log` （或您配置的 `logging.file`）
- macOS LaunchAgent（如果已安装）：`$OPENCLAW_STATE_DIR/logs/gateway.log` 和 `gateway.err.log`
- Linux systemd（如果已安装）：`journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
- Windows：`schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

**启用更多日志记录：**

- 增加文件日志详细信息（持久化JSONL）：
  ```json
  { "logging": { "level": "debug" } }
  ```
- 增加控制台详细程度（仅TTY输出）：
  ```json
  { "logging": { "consoleLevel": "debug", "consoleStyle": "pretty" } }
  ```
- 快速提示：`--verbose` 仅影响 **控制台** 输出。文件日志由 `logging.level` 控制。

参见 [/logging](/logging) 以获取格式、配置和访问的完整概述。

### "Gateway start blocked: set gateway.mode=local"

这意味着配置存在但 `gateway.mode` 未设置（或不是 `local`），因此
网关拒绝启动。

**解决方法（推荐）：**

- 运行向导并将 Gateway 运行模式设置为 **Local**:
  ```bash
  openclaw configure
  ```
- 或者直接设置：
  ```bash
  openclaw config set gateway.mode local
  ```

**如果您想运行远程 Gateway 而不是本地：**

- 设置一个远程 URL 并保持 `gateway.mode=remote`:
  ```bash
  openclaw config set gateway.mode remote
  openclaw config set gateway.remote.url "wss://gateway.example.com"
  ```

**仅用于临时开发:** 传递 `--allow-unconfigured` 以在没有
`gateway.mode=local` 的情况下启动网关。

**还没有配置文件？** 运行 `openclaw setup` 以创建一个初始配置，然后重新运行
网关。

### 服务环境 (PATH + 运行时)

网关服务使用 **最小化的 PATH** 以避免 shell/管理器的额外内容：

- macOS: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `/bin`
- Linux: `/usr/local/bin`, `/usr/bin`, `/bin`

这故意排除了版本管理器 (nvm/fnm/volta/asdf) 和包管理器 (pnpm/npm)，因为服务不会加载您的 shell 初始化脚本。运行时变量如 `DISPLAY` 应该位于 `~/.openclaw/.env` 中（由网关早期加载）。
Exec 运行在 `host=gateway`，将登录 shell 的 `PATH` 合并到 exec 环境中，
因此缺少工具通常意味着您的 shell 初始化脚本没有导出它们（或者设置
`tools.exec.pathPrepend`)。参见 [/tools/exec](/tools/exec)。

WhatsApp + Telegram 通道需要 **Node**；Bun 不受支持。如果您的
服务是通过 Bun 或版本管理的 Node 路径安装的，请运行 `openclaw doctor`
以迁移到系统 Node 安装。

### 技能在沙箱中缺少 API 密钥

**症状:** 技能在主机上正常工作，但在沙箱中由于缺少 API 密钥而失败。

**原因:** 沙盒化 exec 在 Docker 内部运行并且 **不** 继承主机 `process.env`。

**解决方法:**

- 设置 `agents.defaults.sandbox.docker.env`（或每个代理 `agents.list[].sandbox.docker.env`）
- 或将密钥烘焙到自定义沙箱镜像中
- 然后运行 `openclaw sandbox recreate --agent <id>`（或 `--all`）

### 服务正在运行但端口未监听

如果服务报告 **正在运行** 但网关端口上没有任何内容在监听，网关可能拒绝绑定。

**这里的“正在运行”含义**

- `Runtime: running` 表示您的监督程序（launchd/systemd/schtasks）认为进程是活跃的。
- `RPC probe` 表示 CLI 实际上可以连接到网关 WebSocket 并调用 `status`。
- 始终信任 `Probe target:` + `Config (service):` 作为“我们实际尝试了什么？”的行。

**检查:**

- `gateway.mode` 必须是 `local` 用于 `openclaw gateway` 和服务。
- 如果你设置了 `gateway.mode=remote`，**CLI 默认**使用远程 URL。服务仍然可以本地运行，但你的 CLI 可能会探测错误的位置。使用 `openclaw gateway status` 查看服务的解析端口 + 探测目标（或传递 `--url`）。
- `openclaw gateway status` 和 `openclaw doctor` 在服务看起来正在运行但端口关闭时，从日志中显示**最后一个网关错误**。
- 非回环绑定 (`lan`/`tailnet`/`custom`，或 `auto` 当回环不可用时) 需要身份验证：
  `gateway.auth.token` (或 `OPENCLAW_GATEWAY_TOKEN`)。
- `gateway.remote.token` 仅用于远程 CLI 调用；它**不**启用本地身份验证。
- `gateway.token` 被忽略；使用 `gateway.auth.token`。

**如果 `openclaw gateway status` 显示配置不匹配**

- `Config (cli): ...` 和 `Config (service): ...` 通常应该匹配。
- 如果它们不匹配，你几乎肯定是在编辑一个配置文件而服务正在运行另一个。
- 解决方法：从你希望服务使用的相同 `openclaw gateway install --force` / `--profile` / `OPENCLAW_STATE_DIR` 重新运行 `--profile`。

**如果 `openclaw gateway status` 报告服务配置问题**

- 监督器配置（launchd/systemd/schtasks）缺少当前默认值。
- 解决方法：运行 `openclaw doctor` 进行更新（或 `openclaw gateway install --force` 进行完整重写）。

**如果 `Last gateway error:` 提到“拒绝在没有身份验证的情况下绑定 …”**

- 你将 `gateway.bind` 设置为非回环模式 (`lan`/`tailnet`/`custom`，或 `auto` 当回环不可用时) 但未配置身份验证。
- 解决方法：设置 `gateway.auth.mode` + `gateway.auth.token`（或导出 `OPENCLAW_GATEWAY_TOKEN`）并重启服务。

**如果 `openclaw gateway status` 说 `bind=tailnet` 但未找到尾网接口**

- 网关尝试绑定到 Tailscale IP（100.64.0.0/10），但在主机上未检测到。
- 解决方法：在该机器上启动 Tailscale（或将 `gateway.bind` 更改为 `loopback`/`lan`）。

**如果 `Probe note:` 说探测使用了回环**

- 对于 `bind=lan` 这是预期的：网关监听 `0.0.0.0`（所有接口），回环应仍可本地连接。
- 对于远程客户端，使用实际的局域网 IP（不是 `0.0.0.0`）加上端口，并确保已配置身份验证。

### 地址已被使用（端口 18789）

这意味着某些东西已经在监听网关端口。

**检查：**

```bash
openclaw gateway status
```

它将显示监听器及其可能的原因（网关已运行，SSH 隧道）。
如果需要，停止服务或选择不同的端口。

### 检测到额外的工作区文件夹

如果你从较旧的安装升级，磁盘上可能仍然有 `~/openclaw`。
多个工作区目录可能导致混淆的身份验证或状态漂移，因为
只有一个工作区处于活动状态。

**解决方法：** 保留一个活动工作区并归档/删除其余部分。参见
[代理工作区](/concepts/agent-workspace#extra-workspace-folders)。

### 主聊天在沙盒工作区中运行

症状：`pwd` 或文件工具显示 `~/.openclaw/sandboxes/...` 即使你
期望的是主机工作区。

**原因：** `agents.defaults.sandbox.mode: "non-main"` 基于 `session.mainKey`（默认 `"main"`）。
群组/频道会话使用自己的密钥，因此被视为非主会话并获得沙盒工作区。

**修复选项：**

- 如果你希望代理有主机工作区：设置 `agents.list[].sandbox.mode: "off"`。
- 如果你希望在沙盒中访问主机工作区：为该代理设置 `workspaceAccess: "rw"`。

### "代理被中止"

代理在响应中途被中断。

**原因：**

- 用户发送了 `stop`，`abort`，`esc`，`wait`，或 `exit`
- 超时
- 进程崩溃

**修复：** 只需再发送一条消息。会话将继续。

### "代理在回复前失败：未知模型：anthropic/claude-haiku-3-5"

OpenClaw 故意拒绝 **旧版/不安全的模型**（尤其是那些更容易受到提示注入攻击的模型）。如果你看到此错误，该模型名称不再受支持。

**修复：**

- 选择提供商的 **最新** 模型并更新你的配置或模型别名。
- 如果你不确定哪些模型可用，运行 `openclaw models list` 或
  `openclaw models scan` 并选择一个受支持的模型。
- 检查网关日志以获取详细的失败原因。

参见：[模型 CLI](/cli/models) 和 [模型提供商](/concepts/model-providers)。

### 消息未触发

**检查 1：** 发送者是否在白名单中？

```bash
openclaw status
```

在输出中查找 `AllowFrom: ...`。

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

如果 `dmPolicy` 是 `pairing`，未知发送者应收到一个代码，并且他们的消息在批准之前会被忽略。

**检查 1：** 是否已经有待处理的请求在等待？

```bash
openclaw pairing list <channel>
```

待处理的直接消息配对请求默认每个频道最多 **3 个**。如果列表已满，新的请求不会生成代码，直到其中一个被批准或过期。

**检查 2：** 请求是否已创建但没有回复？

```bash
openclaw logs --follow | grep "pairing request"
```

**检查 3：** 确认 `dmPolicy` 不是 `open`/`allowlist` 对于该频道。

### 图像 + 提及不起作用

已知问题：当你仅发送一个提及（没有其他文本）的图像时，WhatsApp 有时不会包含提及元数据。

**解决方法：** 在提及中添加一些文本：

- ❌ `@openclaw` + image
- ✅ `@openclaw check this` + image

### 会话未恢复

**检查 1:** 会话文件是否存在？

```bash
ls -la ~/.openclaw/agents/<agentId>/sessions/
```

**检查 2:** 重置窗口是否太短？

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

**检查 3:** 是否有人发送了 `/new`，`/reset` 或重置触发器？

### 代理超时

默认超时时间为30分钟。对于长时间任务：

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

**修复:** 通常在网关运行后会自动重新连接。如果卡住了，请重启网关进程（无论您如何监控它），或者使用详细输出手动运行它：

```bash
openclaw gateway --verbose
```

如果您已注销/未链接：

```bash
openclaw channels logout
trash "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials" # if logout can't cleanly remove everything
openclaw channels login --verbose       # re-scan QR
```

### 媒体发送失败

**检查 1:** 文件路径是否有效？

```bash
ls -la /path/to/your/image.jpg
```

**检查 2:** 文件是否太大？

- 图像：最大6MB
- 音频/视频：最大16MB
- 文档：最大100MB

**检查 3:** 检查媒体日志

```bash
grep "media\\|fetch\\|download" "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)" | tail -20
```

### 高内存使用率

OpenClaw 将对话历史保留在内存中。

**修复:** 定期重启或设置会话限制：

```json
{
  "session": {
    "historyLimit": 100 // Max messages to keep
  }
}
```

## 常见故障排除

### “网关无法启动 — 配置无效”

当配置包含未知键、格式错误的值或无效类型时，OpenClaw 现在拒绝启动。
这是出于安全考虑故意为之。

使用 Doctor 进行修复：

```bash
openclaw doctor
openclaw doctor --fix
```

注意事项：

- `openclaw doctor` 报告每个无效条目。
- `openclaw doctor --fix` 应用迁移/修复并重写配置。
- 诊断命令如 `openclaw logs`，`openclaw health`，`openclaw status`，`openclaw gateway status` 和 `openclaw gateway probe` 即使配置无效也会运行。

### “所有模型失败” — 我应该首先检查什么？

- **凭证** 是否存在用于尝试的提供商（身份验证配置文件 + 环境变量）。
- **模型路由**：确认 `agents.defaults.model.primary` 和备用项是您可以访问的模型。
- **网关日志** 在 `/tmp/openclaw/…` 中获取确切的提供商错误。
- **模型状态**：使用 `/model status`（聊天）或 `openclaw models status`（CLI）。

### 我使用的是我的个人WhatsApp号码——为什么自我聊天感觉奇怪？

启用自我聊天模式并将您的号码添加到白名单：

```json5
{
  channels: {
    whatsapp: {
      selfChatMode: true,
      dmPolicy: "allowlist",
      allowFrom: ["+15555550123"],
    },
  },
}
```

参见 [WhatsApp 设置](/channels/whatsapp)。

### WhatsApp 将我登出了。如何重新验证身份？

再次运行登录命令并扫描二维码：

```bash
openclaw channels login
```

### 在 `main` 上构建错误——标准修复路径是什么？

1. `git pull origin main && pnpm install`
2. `openclaw doctor`
3. 检查 GitHub 问题或 Discord
4. 临时解决方法：检出较旧的提交

### npm install 失败（allow-build-scripts / 缺少 tar 或 yargs）。该怎么办？

如果您是从源代码运行，请使用仓库的包管理器：**pnpm**（首选）。
仓库声明了 `packageManager: "pnpm@…"`。

典型恢复方法：

```bash
git status   # ensure you’re in the repo root
pnpm install
pnpm build
openclaw doctor
openclaw gateway restart
```

原因：pnpm 是此仓库配置的包管理器。

### 如何在 git 安装和 npm 安装之间切换？

使用 **网站安装程序** 并通过标志选择安装方法。它
就地升级并重写网关服务以指向新安装。

切换 **到 git 安装**：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --no-onboard
```

切换 **到 npm 全局**：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

注意事项：

- git 流程仅在仓库干净时进行变基。首先提交或暂存更改。
- 切换后，运行：
  ```bash
  openclaw doctor
  openclaw gateway restart
  ```

### Telegram 块流式传输不将文本在工具调用之间拆分。为什么？

块流式传输仅发送 **完整的文本块**。您看到单条消息的常见原因：

- `agents.defaults.blockStreamingDefault` 仍然是 `"off"`。
- `channels.telegram.blockStreaming` 设置为 `false`。
- `channels.telegram.streamMode` 是 `partial` 或 `block` **且草稿流式传输处于活动状态**
  （私人聊天 + 主题）。在这种情况下，草稿流式传输会禁用块流式传输。
- 您的 `minChars` / 合并设置太高，因此块会被合并。
- 模型发出一个大型文本块（没有中途刷新点）。

修复检查清单：

1. 将块流式传输设置放在 `agents.defaults` 下，而不是根目录。
2. 如果您希望实现真正的多消息块回复，请设置 `channels.telegram.streamMode: "off"`。
3. 调试时使用较小的块/合并阈值。

参见 [流式传输](/concepts/streaming)。

### 即使设置了 `requireMention: false`，Discord 也不在我的服务器上回复。为什么？

`requireMention` 仅控制通道通过白名单后的提及门控。
默认情况下 `channels.discord.groupPolicy` 是 **白名单**，因此必须显式启用公会。
如果您设置了 `channels.discord.guilds.<guildId>.channels`，则仅允许列出的频道；省略它以允许公会中的所有频道。

修复检查清单：

1. 设置 `channels.discord.groupPolicy: "open"` **或** 添加一个公会白名单条目（可选添加一个频道白名单）。
2. 在 `channels.discord.guilds.<guildId>.channels` 中使用 **数字频道ID**。
3. 将 `requireMention: false` **放在** `channels.discord.guilds` 下面（全局或每个频道）。
   最顶层的 `channels.discord.requireMention` 不是支持的键。
4. 确保机器人具有 **消息内容意图** 和频道权限。
5. 运行 `openclaw channels status --probe` 获取审计提示。

文档：[Discord](/channels/discord)，[频道故障排除](/channels/troubleshooting)。

### Cloud Code Assist API 错误：无效的工具模式 (400)。接下来怎么办？

这几乎总是 **工具模式兼容性** 问题。Cloud Code Assist 端点接受 JSON 模式的一个严格子集。OpenClaw 清理/规范化当前 `main` 中的工具模式，但修复尚未包含在最新版本中（截至 2026 年 1 月 13 日）。

修复检查清单：

1. **更新 OpenClaw**：
   - 如果可以从源代码运行，请拉取 `main` 并重启网关。
   - 否则，请等待包含模式清理程序的下一个版本发布。
2. 避免使用不支持的关键字，如 `anyOf/oneOf/allOf`，`patternProperties`，
   `additionalProperties`，`minLength`，`maxLength`，`format` 等。
3. 如果定义了自定义工具，请将顶级模式保持为 `type: "object"`，带有 `properties` 和简单的枚举。

参见 [Tools](/tools) 和 [TypeBox 模式](/concepts/typebox)。

## macOS 特定问题

### 授予权限时应用程序崩溃（语音/麦克风）

如果在点击隐私提示中的“允许”时应用程序消失或显示“中止陷阱 6”：

**修复 1：重置 TCC 缓存**

```bash
tccutil reset All bot.molt.mac.debug
```

**修复 2：强制新捆绑包 ID**
如果重置不起作用，请更改 [`scripts/package-mac-app.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-app.sh) 中的 `BUNDLE_ID`（例如，添加一个 `.test` 后缀），然后重新构建。这会强制 macOS 将其视为新应用程序。

### 网关卡在“正在启动...”

应用程序连接到本地网关的端口 `18789`。如果它一直卡住：

**修复 1：停止监督器（首选）**
如果网关由 launchd 监督，终止 PID 只会使它重新生成。首先停止监督器：

```bash
openclaw gateway status
openclaw gateway stop
# Or: launchctl bootout gui/$UID/bot.molt.gateway (replace with bot.molt.<profile>; legacy com.openclaw.* still works)
```

**修复 2：端口被占用（查找监听器）**

```bash
lsof -nP -iTCP:18789 -sTCP:LISTEN
```

如果是非监督进程，先尝试优雅停止，然后升级：

```bash
kill -TERM <PID>
sleep 1
kill -9 <PID> # last resort
```

**修复 3：检查 CLI 安装**
确保已安装全局 `openclaw` CLI 并且与应用程序版本匹配：

```bash
openclaw --version
npm install -g openclaw@<version>
```

## 调试模式

获取详细日志记录：

```bash
# Turn on trace logging in config:
#   ${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw/openclaw.json} -> { logging: { level: "trace" } }
#
# Then run verbose commands to mirror debug output to stdout:
openclaw gateway --verbose
openclaw channels login --verbose
```

## 日志位置

| 日志                               | 位置                                                                                                                                                                                                                                                                                                                    |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 网关文件日志（结构化）    | `/tmp/openclaw/openclaw-YYYY-MM-DD.log` (或 `logging.file`)                                                                                                                                                                                                                                                                 |
| 网关服务日志（supervisor） | macOS: `$OPENCLAW_STATE_DIR/logs/gateway.log` + `gateway.err.log` (默认: `~/.openclaw/logs/...`; 配置文件使用 `~/.openclaw-<profile>/logs/...`)<br />Linux: `journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`<br />Windows: `schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST` |
| 会话文件                     | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                                                                                                                                                                                                                                                                            |
| 媒体缓存                       | `$OPENCLAW_STATE_DIR/media/`                                                                                                                                                                                                                                                                                                |
| 凭证                       | `$OPENCLAW_STATE_DIR/credentials/`                                                                                                                                                                                                                                                                                          |

## 健康检查

```bash
# Supervisor + probe target + config paths
openclaw gateway status
# 包含系统级扫描（遗留/额外服务，端口监听器）
openclaw gateway status --deep

# 网关是否可达？
openclaw health --json
# 如果失败，请使用连接详细信息重新运行：
openclaw health --verbose

# 默认端口上是否有程序在监听？
lsof -nP -iTCP:18789 -sTCP:LISTEN

# 最近的活动（RPC日志尾部）
openclaw logs --follow
# 如果RPC服务不可用，则回退到：
tail -20 /tmp/openclaw/openclaw-*.log
```

## Reset Everything

Nuclear option:

```bash
openclaw gateway stop
# 如果您安装了服务并希望进行干净安装：
# openclaw gateway uninstall

trash "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
openclaw channels login         # 重新配对WhatsApp
openclaw gateway restart           # 或：openclaw gateway
```

⚠️ This loses all sessions and requires re-pairing WhatsApp.

## Getting Help

1. Check logs first: `/tmp/openclaw/` (default: `openclaw-YYYY-MM-DD.log`, or your configured `logging.file`)
2. Search existing issues on GitHub
3. Open a new issue with:
   - OpenClaw version
   - Relevant log snippets
   - Steps to reproduce
   - Your config (redact secrets!)

---

_"Have you tried turning it off and on again?"_ — Every IT person ever

🦞🔧

### Browser Not Starting (Linux)

If you see `"Failed to start Chrome CDP on port 18800"`:

**Most likely cause:** Snap-packaged Chromium on Ubuntu.

**Quick fix:** Install Google Chrome instead:

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

Then set in config:

```json
{
  "browser": {
    "executablePath": "/usr/bin/google-chrome-stable"
  }
}
```

**完整指南：** 请参阅 [browser-linux-troubleshooting](/tools/browser-linux-troubleshooting)