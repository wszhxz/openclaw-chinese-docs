---
summary: "Agent tool surface for OpenClaw (browser, canvas, nodes, message, cron) replacing legacy `openclaw-*` skills"
read_when:
  - Adding or modifying agent tools
  - Retiring or changing `openclaw-*` skills
title: "Tools"
---
# 工具 (OpenClaw)

OpenClaw 提供了**一流的代理工具**，用于浏览器、画布、节点和定时任务。
这些工具取代了旧的 `openclaw-*` 技能：这些工具是类型化的，不需要 shell，并且代理应直接依赖它们。

## 禁用工具

您可以通过 `tools.allow` / `tools.deny` 在 `openclaw.json` 中全局允许/禁止工具（禁止优先）。这可以防止不允许的工具被发送给模型提供者。

```json5
{
  tools: { deny: ["browser"] },
}
```

注意事项：

- 匹配不区分大小写。
- 支持 `*` 通配符（`"*"` 表示所有工具）。
- 如果 `tools.allow` 仅引用未知或未加载的插件工具名称，OpenClaw 会记录警告并忽略允许列表，以便核心工具仍然可用。

## 工具配置文件（基础允许列表）

`tools.profile` 在 `tools.allow`/`tools.deny` 之前设置一个**基础工具允许列表**。每个代理覆盖：`agents.list[].tools.profile`。

配置文件：

- `minimal`: 仅 `session_status`
- `coding`: `group:fs`, `group:runtime`, `group:sessions`, `group:memory`, `image`
- `messaging`: `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`
- `full`: 无限制（与未设置相同）

示例（默认仅消息传递，也允许 Slack + Discord 工具）：

```json5
{
  tools: {
    profile: "messaging",
    allow: ["slack", "discord"],
  },
}
```

示例（编码配置文件，但在任何地方都禁止 exec/process）：

```json5
{
  tools: {
    profile: "coding",
    deny: ["group:runtime"],
  },
}
```

示例（全局编码配置文件，仅支持消息传递的代理）：

```json5
{
  tools: { profile: "coding" },
  agents: {
    list: [
      {
        id: "support",
        tools: { profile: "messaging", allow: ["slack"] },
      },
    ],
  },
}
```

## 提供商特定的工具策略

使用 `tools.byProvider` **进一步限制** 特定提供商的工具（或单个 `provider/model`），而无需更改您的全局默认设置。每个代理覆盖：`agents.list[].tools.byProvider`。

这在基础工具配置文件之后应用，并在允许/禁止列表之前应用，因此它只能缩小工具集。提供商密钥接受 `provider`（例如 `google-antigravity`）或 `provider/model`（例如 `openai/gpt-5.2`）。

示例（保持全局编码配置文件，但为 Google Antigravity 提供最少的工具）：

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
  },
}
```

示例（针对不稳定端点的提供商/模型特定允许列表）：

```json5
{
  tools: {
    allow: ["group:fs", "group:runtime", "sessions_list"],
    byProvider: {
      "openai/gpt-5.2": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

示例（针对单个提供商的代理特定覆盖）：

```json5
{
  agents: {
    list: [
      {
        id: "support",
        tools: {
          byProvider: {
            "google-antigravity": { allow: ["message", "sessions_list"] },
          },
        },
      },
    ],
  },
}
```

## 工具组（简写）

工具策略（全局、代理、沙箱）支持 `group:*` 条目，这些条目扩展为多个工具。在 `tools.allow` / `tools.deny` 中使用这些。

可用组：

- `group:runtime`: `exec`, `bash`, `process`
- `group:fs`: `read`, `write`, `edit`, `apply_patch`
- `group:sessions`: `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status`
- `group:memory`: `memory_search`, `memory_get`
- `group:web`: `web_search`, `web_fetch`
- `group:ui`: `browser`, `canvas`
- `group:automation`: `cron`, `gateway`
- `group:messaging`: `message`
- `group:nodes`: `nodes`
- `group:openclaw`: 所有内置的 OpenClaw 工具（不包括提供商插件）

示例（仅允许文件工具 + 浏览器）：

```json5
{
  tools: {
    allow: ["group:fs", "browser"],
  },
}
```

## 插件 + 工具

插件可以注册超出核心集的**额外工具**（和 CLI 命令）。有关安装和配置，请参阅 [Plugins](/tools/plugin)，有关如何将工具使用指南注入提示中，请参阅 [Skills](/tools/skills)。一些插件随工具一起提供自己的技能（例如，语音呼叫插件）。

可选插件工具：

- [Lobster](/tools/lobster)：具有可恢复批准的类型化工作流运行时（需要在网关主机上安装 Lobster CLI）。
- [LLM Task](/tools/llm-task)：用于结构化工作流输出的 JSON 专用 LLM 步骤（可选模式验证）。
- [Diffs](/tools/diffs)：只读差异查看器和 PNG 或 PDF 文件渲染器，用于前后文本或统一补丁。

## 工具清单

### `apply_patch`

跨一个或多个文件应用结构化补丁。用于多段编辑。
实验性功能：通过 `tools.exec.applyPatch.enabled` 启用（仅限 OpenAI 模型）。
`tools.exec.applyPatch.workspaceOnly` 默认为 `true`（工作区包含）。仅当您有意让 `apply_patch` 在工作区目录外写入/删除时，将其设置为 `false`。

### `exec`

在工作区中运行 shell 命令。

核心参数：

- `command`（必需）
- `yieldMs`（超时后自动后台运行，默认 10000）
- `background`（立即后台运行）
- `timeout`（秒；如果超过则终止进程，默认 1800）
- `elevated`（布尔值；如果启用/允许提升模式，则在主机上运行；仅当代理被沙箱化时改变行为）
- `host` (`sandbox | gateway | node`)
- `security` (`deny | allowlist | full`)
- `ask` (`off | on-miss | always`)
- `node`（用于 `host=node` 的节点 ID/名称）
- 需要真正的 TTY？设置 `pty: true`。

注意事项：

- 后台运行时返回带有 `sessionId` 的 `status: "running"`。
- 使用 `process` 轮询/日志/写入/终止/清除后台会话。
- 如果 `process` 不被允许，`exec` 将同步运行并忽略 `yieldMs`/`background`。
- `elevated` 受 `tools.elevated` 和任何 `agents.list[].tools.elevated` 覆盖控制（两者都必须允许），并且是 `host=gateway` + `security=full` 的别名。
- 当代理被沙箱化时，`elevated` 才会改变行为（否则它是无效操作）。
- `host=node` 可以针对 macOS 伴侣应用程序或无头节点主机 (`openclaw node run`)。
- 网关/节点批准和允许列表：[Exec approvals](/tools/exec-approvals)。

### `process`

管理后台执行会话。

核心操作：

- `list`, `poll`, `log`, `write`, `kill`, `clear`, `remove`

注意事项：

- 完成时 `poll` 返回新的输出和退出状态。
- `log` 支持基于行的 `offset`/`limit`（省略 `offset` 以获取最后 N 行）。
- `process` 按每个代理进行范围划分；其他代理的会话不可见。

### `loop-detection`（工具调用循环防护）

OpenClaw 跟踪最近的工具调用历史，并在检测到重复的无进展循环时阻止或发出警告。
通过 `tools.loopDetection.enabled: true` 启用（默认为 `false`）。

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      historySize: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

- `genericRepeat`：重复相同的工具 + 相同的参数调用模式。
- `knownPollNoProgress`：重复具有相同输出的轮询类工具。
- `pingPong`：交替的 `A/B/A/B` 无进展模式。
- 每个代理覆盖：`agents.list[].tools.loopDetection`。

### `web_search`

使用 Perplexity、Brave、Gemini、Grok 或 Kimi 搜索网络。

核心参数：

- `query`（必需）
- `count`（1–10；默认来自 `tools.web.search.maxResults`）

注意事项：

- 需要所选提供商的 API 密钥（推荐：`openclaw configure --section web`）。
- 通过 `tools.web.search.enabled` 启用。
- 响应被缓存（默认 15 分钟）。
- 请参阅 [Web tools](/tools/web) 进行设置。

### `web_fetch`

从 URL 获取并提取可读内容（HTML → markdown/text）。

核心参数：

- `url`（必需）
- `extractMode` (`markdown` | `text`)
- `maxChars`（截断长页面）

注意事项：

- 通过 `tools.web.fetch.enabled` 启用。
- `maxChars` 由 `tools.web.fetch.maxCharsCap` 限制（默认 50000）。
- 响应被缓存（默认 15 分钟）。
- 对于 JavaScript 丰富的站点，建议使用浏览器工具。
- 请参阅 [Web tools](/tools/web) 进行设置。
- 请参阅 [Firecrawl](/tools/firecrawl) 了解可选的反机器人回退。

### `browser`

控制专用的 OpenClaw 管理的浏览器。

核心操作：

- `status`, `start`, `stop`, `tabs`, `open`, `focus`, `close`
- `snapshot` (aria/ai)
- `screenshot`（返回图像块 + `MEDIA:<path>`）
- `act`（UI 操作：点击/输入/按下/悬停/拖动/选择/填充/调整大小/等待/评估）
- `navigate`, `console`, `pdf`, `upload`, `dialog`

配置文件管理：

- `profiles` — 列出所有浏览器配置文件及其状态
- `create-profile` — 创建具有自动分配端口的新配置文件（或 `cdpUrl`）
- `delete-profile` — 停止浏览器，删除用户数据，从配置中移除（仅限本地）
- `reset-profile` — 在配置文件的端口上杀死孤立进程（仅限本地）

常用参数：

- `profile` (可选; 默认为 `browser.defaultProfile`)
- `target` (`sandbox` | `host` | `node`)
- `node` (可选; 选择特定的节点 ID/名称)
  注释：
- 需要 `browser.enabled=true` (默认是 `true`; 设置 `false` 以禁用)。
- 所有操作都接受可选的 `profile` 参数，以支持多实例。
- 当省略 `profile` 时，使用 `browser.defaultProfile` (默认为 "chrome")。
- 配置文件名：仅小写字母数字和连字符（最多 64 个字符）。
- 端口范围：18800-18899（大约最多 100 个配置文件）。
- 远程配置文件仅支持附加（无启动/停止/重置）。
- 如果连接了浏览器功能节点，工具可能会自动路由到它（除非你固定了 `target`）。
- 安装 Playwright 后，`snapshot` 默认为 `ai`; 使用 `aria` 获取无障碍树。
- `snapshot` 还支持角色快照选项 (`interactive`, `compact`, `depth`, `selector`)，这些选项返回像 `e12` 的引用。
- `act` 需要来自 `snapshot` 的 `ref` (AI 快照中的数值 `12` 或角色快照中的 `e12`); 对于罕见的 CSS 选择器需求，使用 `evaluate`。
- 默认情况下避免 `act` → `wait`; 仅在特殊情况下使用（没有可靠的 UI 状态可以等待）。
- `upload` 可以选择传递一个 `ref` 以便在武装后自动点击。
- `upload` 还支持 `inputRef` (aria 引用) 或 `element` (CSS 选择器) 直接设置 `<input type="file">`。

### `canvas`

驱动节点 Canvas (呈现、评估、快照、A2UI)。

核心操作：

- `present`, `hide`, `navigate`, `eval`
- `snapshot` (返回图像块 + `MEDIA:<path>`)
- `a2ui_push`, `a2ui_reset`

注释：

- 在底层使用网关 `node.invoke`。
- 如果未提供 `node`，工具会选择默认值（单个连接的节点或本地 mac 节点）。
- A2UI 仅限 v0.8 版本（无 `createSurface`）; CLI 会拒绝 v0.9 JSONL 并显示行错误。
- 快速冒烟测试: `openclaw nodes canvas a2ui push --node <id> --text "Hello from A2UI"`。

### `nodes`

发现并定位配对节点；发送通知；捕获摄像头/屏幕。

核心操作：

- `status`, `describe`
- `pending`, `approve`, `reject` (配对)
- `notify` (macOS `system.notify`)
- `run` (macOS `system.run`)
- `camera_list`, `camera_snap`, `camera_clip`, `screen_record`
- `location_get`, `notifications_list`, `notifications_action`
- `device_status`, `device_info`, `device_permissions`, `device_health`

注释：

- 摄像头/屏幕命令需要节点应用程序处于前台。
- 图像返回图像块 + `MEDIA:<path>`。
- 视频返回 `FILE:<path>` (mp4)。
- 位置返回 JSON 负载 (纬度/经度/精度/时间戳)。
- `run` 参数: `command` argv 数组; 可选的 `cwd`, `env` (`KEY=VAL`), `commandTimeoutMs`, `invokeTimeoutMs`, `needsScreenRecording`。

示例 (`run`):

```json
{
  "action": "run",
  "node": "office-mac",
  "command": ["echo", "Hello"],
  "env": ["FOO=bar"],
  "commandTimeoutMs": 12000,
  "invokeTimeoutMs": 45000,
  "needsScreenRecording": false
}
```

### `image`

使用配置的图像模型分析图像。

核心参数：

- `image` (必需的路径或 URL)
- `prompt` (可选; 默认为 "描述图像。")
- `model` (可选覆盖)
- `maxBytesMb` (可选大小限制)

注释：

- 仅当配置了 `agents.defaults.imageModel` (主要或备用) 或者可以从默认模型 + 配置的身份验证中推断出隐式图像模型时可用（尽力匹配）。
- 直接使用图像模型（独立于主聊天模型）。

### `pdf`

分析一个或多个 PDF 文档。

有关完整行为、限制、配置和示例，请参阅 [PDF 工具](/tools/pdf)。

### `message`

跨 Discord/Google Chat/Slack/Telegram/WhatsApp/Signal/iMessage/MS Teams 发送消息和频道操作。

核心操作：

- `send` (文本 + 可选媒体; MS Teams 还支持用于 Adaptive Cards 的 `card`)
- `poll` (WhatsApp/Discord/MS Teams 投票)
- `react` / `reactions` / `read` / `edit` / `delete`
- `pin` / `unpin` / `list-pins`
- `permissions`
- `thread-create` / `thread-list` / `thread-reply`
- `search`
- `sticker`
- `member-info` / `role-info`
- `emoji-list` / `emoji-upload` / `sticker-upload`
- `role-add` / `role-remove`
- `channel-info` / `channel-list`
- `voice-status`
- `event-list` / `event-create`
- `timeout` / `kick` / `ban`

注释：

- `send` 通过网关路由 WhatsApp; 其他渠道直接通信。
- `poll` 对 WhatsApp 和 MS Teams 使用网关; Discord 投票直接通信。
- 当消息工具调用绑定到活动的聊天会话时，发送将被限制在该会话的目标，以避免跨上下文泄露。

### `cron`

管理网关定时任务和唤醒。

核心操作：

- `status`, `list`
- `add`, `update`, `remove`, `run`, `runs`
- `wake` (入队系统事件 + 可选立即心跳)

注释：

- `add` 期望一个完整的定时任务对象（与 `cron.add` RPC 相同的模式）。
- `update` 使用 `{ jobId, patch }` (`id` 为了兼容性而接受)。

### `gateway`

重启或应用更新到正在运行的网关进程（就地）。

核心操作：

- `restart` (授权 + 发送 `SIGUSR1` 以进行进程内重启; `openclaw gateway` 就地重启)
- `config.schema.lookup` (一次检查一个配置路径，而不将整个模式加载到提示上下文中)
- `config.get`
- `config.apply` (验证 + 写入配置 + 重启 + 唤醒)
- `config.patch` (合并部分更新 + 重启 + 唤醒)
- `update.run` (运行更新 + 重启 + 唤醒)

注释：

- `config.schema.lookup` 期望一个目标配置路径，例如 `gateway.auth` 或 `agents.list.*.heartbeat`。
- 当处理 `plugins.entries.<id>` 时，路径可能包括斜杠分隔的插件 ID，例如 `plugins.entries.pack/one.config`。
- 使用 `delayMs` (默认为 2000) 以避免中断正在进行的回复。
- `config.schema` 仍然可用于内部控制 UI 流程，并且不通过代理 `gateway` 工具公开。
- `restart` 默认启用; 设置 `commands.restart: false` 以禁用它。

### `sessions_list` / `sessions_history` / `sessions_send` / `sessions_spawn` / `session_status`

列出会话、检查转录历史记录或将消息发送到另一个会话。

核心参数：

- `sessions_list`: `kinds?`, `limit?`, `activeMinutes?`, `messageLimit?` (0 = 无)
- `sessions_history`: `sessionKey` (或 `sessionId`), `limit?`, `includeTools?`
- `sessions_send`: `sessionKey` (或 `sessionId`), `message`, `timeoutSeconds?` (0 = 发送即忘)
- `sessions_spawn`: `task`, `label?`, `runtime?`, `agentId?`, `model?`, `thinking?`, `cwd?`, `runTimeoutSeconds?`, `thread?`, `mode?`, `cleanup?`, `sandbox?`, `streamTo?`, `attachments?`, `attachAs?`
- `session_status`: `sessionKey?` (默认当前; 接受 `sessionId`), `model?` (`default` 清除覆盖)

注释：

- `main` 是规范的直接聊天键; 全局/未知会被隐藏。
- `messageLimit > 0` 获取每个会话的最后 N 条消息（过滤掉工具消息）。
- 会话定位由 `tools.sessions.visibility` 控制（默认 `tree`: 当前会话 + 孵化的子代理会话）。如果你为多个用户运行共享代理，请考虑设置 `tools.sessions.visibility: "self"` 以防止跨会话浏览。
- 当 `timeoutSeconds > 0` 时，`sessions_send` 会等待最终完成。
- 交付/公告在完成后进行，并尽最大努力; `status: "ok"` 确认代理运行已完成，而不是公告已送达。
- `sessions_spawn` 支持 `runtime: "subagent" | "acp"` (`subagent` 默认)。有关 ACP 运行时行为，请参阅 [ACP 代理](/tools/acp-agents)。
- 对于 ACP 运行时，`streamTo: "parent"` 将初始运行进度摘要作为系统事件路由回请求者会话，而不是直接子交付。
- `sessions_spawn` 启动子代理运行并将公告回复发布回请求者聊天。
  - 支持一次性模式 (`mode: "run"`) 和持久线程绑定模式 (`mode: "session"` 与 `thread: true`)。
  - 如果省略了 `thread: true` 和 `mode`，模式默认为 `session`。
  - `mode: "session"` 需要 `thread: true`。
  - 如果省略了 `runTimeoutSeconds`，OpenClaw 会在设置时使用 `agents.defaults.subagents.runTimeoutSeconds`; 否则超时默认为 `0` (无超时)。
  - Discord 线程绑定流依赖于 `session.threadBindings.*` 和 `channels.discord.threadBindings.*`。
  - 回复格式包括 `Status`, `Result` 和紧凑统计信息。
  - `Result` 是助手完成文本; 如果缺失，则使用最新的 `toolResult` 作为后备。
- 手动完成模式首先直接发送，然后在瞬态失败时使用队列回退和重试 (`status: "ok"` 表示运行已完成，而不是公告已送达)。
- `sessions_spawn` 仅支持子代理运行时的内联文件附件（ACP 拒绝它们）。每个附件都有 `name`, `content` 和可选的 `encoding` (`utf8` 或 `base64`) 和 `mimeType`。文件在 `.openclaw/attachments/<uuid>/` 处物化到子工作区，并带有 `.manifest.json` 元数据文件。工具返回一个收据，包含 `count`, `totalBytes`, 每个文件的 `sha256` 和 `relDir`。附件内容会自动从转录持久化中删除。
  - 通过 `tools.sessions_spawn.attachments` 配置限制 (`enabled`, `maxTotalBytes`, `maxFiles`, `maxFileBytes`, `retainOnSessionKeep`)。
  - `attachAs.mountPath` 是为未来挂载实现保留的提示。
- `sessions_spawn` 是非阻塞的，并立即返回 `status: "accepted"`。
- ACP `streamTo: "parent"` 响应可能包括 `streamLogPath` (会话范围的 `*.acp-stream.jsonl`) 以跟踪进度历史。
- `sessions_send` 运行回复-回声乒乓 (回复 `REPLY_SKIP` 以停止; 最大回合数通过 `session.agentToAgent.maxPingPongTurns`, 0–5)。
- 乒乓之后，目标代理运行一个 **公告步骤**; 回复 `ANNOUNCE_SKIP` 以抑制公告。
- 沙箱夹紧：当当前会话被沙箱化且 `agents.defaults.sandbox.sessionToolsVisibility: "spawned"` 时，OpenClaw 将 `tools.sessions.visibility` 夹紧到 `tree`。

### `agents_list`

列出当前会话可以通过 `sessions_spawn` 定位的代理 ID。

注释：

- 结果仅限于每个代理的允许列表 (`agents.list[].subagents.allowAgents`)。
- 当配置了 `["*"]` 时，工具会包括所有已配置的代理，并标记 `allowAny: true`。

## 参数（通用）

网关支持的工具 (`canvas`, `nodes`, `cron`):

- `gatewayUrl` (默认 `ws://127.0.0.1:18789`)
- `gatewayToken` (如果启用了身份验证)
- `timeoutMs`

注意：当设置了 `gatewayUrl` 时，需要显式包含 `gatewayToken`。工具不会继承配置或环境凭据进行覆盖，缺少显式凭据将导致错误。

浏览器工具：

- `profile` (可选; 默认为 `browser.defaultProfile`)
- `target` (`sandbox` | `host` | `node`)
- `node` (可选; 固定特定节点 ID/名称)

## 推荐的代理流程

浏览器自动化：

1. `browser` → `status` / `start`
2. `snapshot` (ai 或 aria)
3. `act` (点击/输入/按键)
4. 如果需要视觉确认，则使用 `screenshot`

画布渲染：

1. `canvas` → `present`
2. `a2ui_push` (可选)
3. `snapshot`

节点定位：

1. `nodes` → `status`
2. 在选定的节点上执行 `describe`
3. `notify` / `run` / `camera_snap` / `screen_record`

## 安全性

- 避免直接使用 `system.run`; 只有在用户明确同意的情况下才使用 `nodes` → `run`。
- 尊重用户的摄像头/屏幕捕获同意。
- 使用 `status/describe` 确保在调用媒体命令之前获得权限。

## 工具如何呈现给代理

工具通过两个并行渠道暴露：

1. **系统提示文本**：一个人类可读的列表 + 指导。
2. **工具模式**：发送到模型 API 的结构化函数定义。

这意味着代理可以看到“存在哪些工具”和“如何调用它们”。如果某个工具没有出现在系统提示或模式中，模型将无法调用它。