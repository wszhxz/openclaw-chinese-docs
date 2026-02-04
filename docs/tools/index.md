---
summary: "Agent tool surface for OpenClaw (browser, canvas, nodes, message, cron) replacing legacy `openclaw-*` skills"
read_when:
  - Adding or modifying agent tools
  - Retiring or changing `openclaw-*` skills
title: "Tools"
---
# 工具 (OpenClaw)

OpenClaw 提供了 **一等代理工具** 用于浏览器、画布、节点和定时任务。
这些工具替换了旧的 `openclaw-*` 技能：工具是类型化的，不需要 shell，并且代理应直接依赖它们。

## 禁用工具

您可以通过在 `openclaw.json` 中使用 `tools.allow` / `tools.deny` 全局允许或拒绝工具（拒绝优先）。这可以防止不允许的工具被发送到模型提供商。

```json5
{
  tools: { deny: ["browser"] },
}
```

注意事项：

- 匹配不区分大小写。
- 支持 `*` 通配符 (`"*"` 表示所有工具)。
- 如果 `tools.allow` 仅引用未知或未加载的插件工具名称，OpenClaw 会记录警告并忽略白名单，以确保核心工具可用。

## 工具配置文件（基础白名单）

`tools.profile` 在 `tools.allow`/`tools.deny` 之前设置一个 **基础工具白名单**。
每个代理的覆盖：`agents.list[].tools.profile`。

配置文件：

- `minimal`: 仅 `session_status`
- `coding`: `group:fs`, `group:runtime`, `group:sessions`, `group:memory`, `image`
- `messaging`: `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`
- `full`: 无限制（与未设置相同）

示例（默认仅消息传递，允许 Slack + Discord 工具）：

```json5
{
  tools: {
    profile: "messaging",
    allow: ["slack", "discord"],
  },
}
```

示例（编码配置文件，但全局拒绝 exec/process）：

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

## 特定提供商的工具策略

使用 `tools.byProvider` 为特定提供商（或单个 `provider/model`）**进一步限制** 工具，而不更改全局默认设置。
每个代理的覆盖：`agents.list[].tools.byProvider`。

这在 **基础工具配置文件之后** 和 **允许/拒绝列表之前** 应用，
因此只能缩小工具集。
提供商密钥接受 `provider`（例如 `google-antigravity`）或
`provider/model`（例如 `openai/gpt-5.2`）。

示例（保持全局编码配置文件，但 Google Antigravity 的工具最少）：

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

示例（特定提供商/模型的白名单，适用于不可靠的端点）：

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

示例（单个提供商的特定代理覆盖）：

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

## 工具组（快捷方式）

工具策略（全局、代理、沙盒）支持 `group:*` 条目，这些条目展开为多个工具。
在 `tools.allow` / `tools.deny` 中使用这些。

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
- `group:openclaw`: 所有内置 OpenClaw 工具（排除提供商插件）

示例（仅允许文件工具 + 浏览器）：

```json5
{
  tools: {
    allow: ["group:fs", "browser"],
  },
}
```

## 插件 + 工具

插件可以注册核心集之外的 **附加工具**（和 CLI 命令）。
有关安装和配置，请参阅 [插件](/plugin)，有关如何将工具使用指南注入提示，请参阅 [技能](/tools/skills)。某些插件附带自己的技能（例如，语音通话插件）。

可选插件工具：

- [Lobster](/tools/lobster): 类型化的工作流运行时，带有可恢复的审批（需要网关主机上的 Lobster CLI）。
- [LLM Task](/tools/llm-task): 仅 JSON 的 LLM 步骤，用于结构化工作流输出（可选模式验证）。

## 工具清单

### `apply_patch`

对一个或多个文件应用结构化补丁。用于多段编辑。
实验性：通过 `tools.exec.applyPatch.enabled` 启用（仅限 OpenAI 模型）。

### `exec`

在工作区中运行 shell 命令。

核心参数：

- `command`（必需）
- `yieldMs`（超时后自动后台运行，默认 10000）
- `background`（立即后台运行）
- `timeout`（秒；超过则终止进程，默认 1800）
- `elevated`（布尔值；如果启用了提升模式，则在主机上运行；仅在代理沙盒化时改变行为）
- `host` (`sandbox | gateway | node`)
- `security` (`deny | allowlist | full`)
- `ask` (`off | on-miss | always`)
- `node`（`host=node` 的节点 ID/名称）
- 需要真正的 TTY？设置 `pty: true`。

注意事项：

- 当后台运行时，返回 `status: "running"` 并带有 `sessionId`。
- 使用 `process` 轮询/日志/写入/终止/清除后台会话。
- 如果 `process` 被禁止，`exec` 同步运行并忽略 `yieldMs`/`background`。
- `elevated` 受 `tools.elevated` 加上任何 `agents.list[].tools.elevated` 覆盖（两者都必须允许）的限制，并且是 `host=gateway` + `security=full` 的别名。
- `elevated` 仅在代理沙盒化时改变行为（否则它是空操作）。
- `host=node` 可以针对 macOS 伴侣应用程序或无头节点主机 (`openclaw node run`)。
- 网关/节点审批和白名单：[执行审批](/tools/exec-approvals)。

### `process`

管理后台执行会话。

核心操作：

- `list`, `poll`, `log`, `write`, `kill`, `clear`, `remove`

注意事项：

- `poll` 完成时返回新的输出和退出状态。
- `log` 支持基于行的 `offset`/`limit`（省略 `offset` 以获取最后 N 行）。
- `process` 按代理范围划分；其他代理的会话不可见。

### `web_search`

使用 Brave Search API 进行网络搜索。

核心参数：

- `query`（必需）
- `count`（1–10；默认来自 `tools.web.search.maxResults`）

注意事项：

- 需要 Brave API 密钥（推荐：`openclaw configure --section web`，或设置 `BRAVE_API_KEY`）。
- 通过 `tools.web.search.enabled` 启用。
- 响应会被缓存（默认 15 分钟）。
- 请参阅 [Web 工具](/tools/web) 了解设置。

### `web_fetch`

从 URL 获取并提取可读内容（HTML → markdown/文本）。

核心参数：

- `url`（必需）
- `extractMode` (`markdown` | `text`)
- `maxChars`（截断长页面）

注意事项：

- 通过 `tools.web.fetch.enabled` 启用。
- 响应会被缓存（默认 15 分钟）。
- 对于 JS 密集型网站，更喜欢使用浏览器工具。
- 请参阅 [Web 工具](/tools/web) 了解设置。
- 请参阅 [Firecrawl](/tools/firecrawl) 了解可选的反机器人回退。

### `browser`

控制专用的 OpenClaw 管理的浏览器。

核心操作：

- `status`, `start`, `stop`, `tabs`, `open`, `focus`, `close`
- `snapshot`（aria/ai）
- `screenshot`（返回图像块 + `MEDIA:<path>`）
- `act`（UI 操作：点击/输入/按下/悬停/拖动/选择/填充/调整大小/等待/评估）
- `navigate`, `console`, `pdf`, `upload`, `dialog`

配置文件管理：

- `profiles` — 列出所有浏览器配置文件及其状态
- `create-profile` — 创建新配置文件并分配端口（或 `cdpUrl`）
- `delete-profile` — 停止浏览器，删除用户数据，从配置中移除（仅本地）
- `reset-profile` — 终止配置文件端口上的孤立进程（仅本地）

常见参数：

- `profile`（可选；默认为 `browser.defaultProfile`）
- `target` (`sandbox` | `host` | `node`)
- `node`（可选；选择特定节点 ID/名称）
  注意事项：
- 需要 `browser.enabled=true`（默认为 `true`；设置 `false` 以禁用）。
- 所有操作接受可选的 `profile` 参数以支持多实例。
- 当省略 `profile` 时，使用 `browser.defaultProfile`（默认为 "chrome"）。
- 配置文件名称：仅小写字母数字和连字符（最多 64 字符）。
- 端口范围：18800-18899（最多约 100 个配置文件）。
- 远程配置文件仅支持附加（不支持启动/停止/重置）。
- 如果连接了支持浏览器的节点，工具可能会自动路由到它（除非你固定 `target`）。
- `snapshot` 默认为 `ai` 当安装了 Playwright；使用 `aria` 获取辅助树。
- `snapshot` 也支持角色快照选项 (`interactive`, `compact`, `depth`, `selector`)，这些选项返回类似 `e12` 的引用。
- `act` 需要来自 `snapshot` 的 `ref`（来自 AI 快照的数字 `12` 或来自角色快照的 `e12`）；使用 `evaluate` 处理罕见的 CSS 选择器需求。
- 默认避免 `act` → `wait`；仅在例外情况下使用（没有可靠的 UI 状态可等待）。
- `upload` 可以选择传递一个 `ref` 以在武装后自动点击。
- `upload` 也支持 `inputRef`（aria 引用）或 `element`（CSS 选择器）来直接设置 `<input type="file">`。

### `canvas`

驱动节点画布（显示、评估、快照、A2UI）。

核心操作：

- `present`, `hide`, `navigate`, `eval`
- `snapshot`（返回图像块 + `MEDIA:<path>`）
- `a2ui_push`, `a2ui_reset`

注意事项：

- 内部使用网关 `node.invoke`。
- 如果未提供 `node`，工具会选择默认值（单个连接的节点或本地 Mac 节点）。
- A2UI 仅限 v0.8（无 `createSurface`）；CLI 拒绝带有行错误的 v0.9 JSONL。
- 快速测试：`openclaw nodes canvas a2ui push --node <id> --text "Hello from A2UI"`。

### `nodes`

发现和定位配对节点；发送通知；捕获相机/屏幕。

核心操作：

- `status`, `describe`
- `pending`, `approve`, `reject`（配对）
- `notify`（macOS `system.notify`）
- `run`（macOS `system.run`）
- `camera_snap`, `camera_clip`, `screen_record`
- `location_get`

注意事项：

- 相机/屏幕命令需要节点应用程序处于前台。
- 图像返回图像块 + `MEDIA:<path>`。
- 视频返回 `FILE:<path>`（mp4）。
- 位置返回 JSON 有效负载（纬度/经度/精度/时间戳）。
- `run` 参数：`command` argv 数组；可选 `cwd`, `env` (`KEY=VAL`), `commandTimeoutMs`, `invokeTimeoutMs`, `needsScreenRecording`。

示例 (`run`)：

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

- `image`（必需路径或 URL）
- `prompt`（可选；默认为“描述图像。”）
- `model`（可选覆盖）
- `maxBytesMb`（可选大小限制）

注意事项：

- 仅在配置了 `agents.defaults.imageModel`（主或备用）时可用，或者可以从默认模型 + 配置的身份验证推断出隐式的图像模型（最佳努力配对）。
- 直接使用图像模型（独立于主聊天模型）。

### `message`

跨 Discord/Google Chat/Slack/Telegram/WhatsApp/Signal/iMessage/MS Teams 发送消息和频道操作。

核心操作：

- `send`（文本 + 可选媒体；MS Teams 还支持 `card` 用于自适应卡片）
- `poll`（WhatsApp/Discord/MS Teams 投票）
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
- __CODE_BLOCK_