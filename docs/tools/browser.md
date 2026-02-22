---
summary: "Integrated browser control service + action commands"
read_when:
  - Adding agent-controlled browser automation
  - Debugging why openclaw is interfering with your own Chrome
  - Implementing browser settings + lifecycle in the macOS app
title: "Browser (OpenClaw-managed)"
---
# 浏览器 (openclaw-managed)

OpenClaw 可以运行一个 **专用的 Chrome/Brave/Edge/Chromium 配置文件**，该配置文件由代理控制。
它与您的个人浏览器隔离，并通过网关内的一个小的本地控制服务进行管理（仅限回环）。

初学者视角：

- 将其视为一个 **独立的、仅代理使用的浏览器**。
- `openclaw` 配置文件 **不会** 触及您的个人浏览器配置文件。
- 代理可以在一个安全的环境中 **打开标签页、读取页面、点击和输入**。
- 默认的 `chrome` 配置文件通过扩展中继使用 **系统默认的 Chromium 浏览器**；切换到 `openclaw` 使用隔离的受管浏览器。

## 您将获得

- 一个名为 **openclaw** 的独立浏览器配置文件（默认橙色强调）。
- 确定性的标签页控制（列出/打开/聚焦/关闭）。
- 代理操作（点击/输入/拖动/选择）、快照、屏幕截图、PDF。
- 可选的多配置文件支持 (`openclaw`, `work`, `remote`, ...)。

此浏览器 **不是** 您的日常浏览器。它是一个安全、隔离的表面，用于代理自动化和验证。

## 快速开始

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

如果您收到“浏览器已禁用”，请在配置中启用它（见下文），然后重启网关。

## 配置文件：`openclaw` 对比 `chrome`

- `openclaw`：受管、隔离的浏览器（无需扩展）。
- `chrome`：扩展中继到您的 **系统浏览器**（需要将 OpenClaw 扩展附加到一个标签页）。

设置 `browser.defaultProfile: "openclaw"` 如果您希望默认使用受管模式。

## 配置

浏览器设置位于 `~/.openclaw/openclaw.json`。

```json5
{
  browser: {
    enabled: true, // default: true
    // cdpUrl: "http://127.0.0.1:18792", // legacy single-profile override
    remoteCdpTimeoutMs: 1500, // remote CDP HTTP timeout (ms)
    remoteCdpHandshakeTimeoutMs: 3000, // remote CDP WebSocket handshake timeout (ms)
    defaultProfile: "chrome",
    color: "#FF4500",
    headless: false,
    noSandbox: false,
    attachOnly: false,
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
  },
}
```

注意事项：

- 浏览器控制服务绑定到一个从 `gateway.port` 派生的环回端口（默认：`18791`，即网关 + 2）。中继使用下一个端口 (`18792`)。
- 如果您覆盖了网关端口 (`gateway.port` 或 `OPENCLAW_GATEWAY_PORT`)，
  派生的浏览器端口会相应地偏移以保持在同一“系列”中。
- `cdpUrl` 在未设置时默认为中继端口。
- `remoteCdpTimeoutMs` 适用于远程（非环回）CDP可达性检查。
- `remoteCdpHandshakeTimeoutMs` 适用于远程CDP WebSocket可达性检查。
- `attachOnly: true` 表示“从不启动本地浏览器；仅在它已经运行时附加。”
- `color` + 每个配置文件的 `color` 会对浏览器UI进行着色，以便您可以看到哪个配置文件处于活动状态。
- 默认配置文件是 `chrome`（扩展中继）。使用 `defaultProfile: "openclaw"` 用于托管浏览器。
- 自动检测顺序：如果系统默认浏览器基于Chromium（Chrome/Brave/Edge等），OpenClaw会自动使用它。设置 `browser.executablePath` 以覆盖自动检测：

CLI示例：

```bash
openclaw config set browser.executablePath "/usr/bin/google-chrome"
```

```json5
// macOS
{
  browser: {
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
  }
}

// Windows
{
  browser: {
    executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
  }
}

// Linux
{
  browser: {
    executablePath: "/usr/bin/brave-browser"
  }
}
```

## 本地控制与远程控制

- **本地控制（默认）：** 网关启动环回控制服务并可以启动本地浏览器。
- **远程控制（节点主机）：** 在拥有浏览器的机器上运行节点主机；网关将浏览器操作代理到该节点。
- **远程CDP：** 设置 `browser.profiles.<name>.cdpUrl`（或 `browser.cdpUrl`）以
  附加到远程基于Chromium的浏览器。在这种情况下，OpenClaw不会启动本地浏览器。

远程CDP URL可以包含认证信息：

- 查询令牌（例如，`https://provider.example?token=<token>`）
- HTTP基本认证（例如，`https://user:pass@provider.example`）

OpenClaw在调用 `/json/*` 端点以及连接到CDP WebSocket时会保留认证信息。建议使用环境变量或秘密管理器而不是将令牌提交到配置文件中。

## 节点浏览器代理（零配置默认）

如果您在拥有浏览器的机器上运行**节点主机**，OpenClaw可以
自动将浏览器工具调用路由到该节点而无需额外的浏览器配置。
这是远程网关的默认路径。

注意事项：

- 节点主机通过一个 **代理命令** 暴露其本地浏览器控制服务器。
- 配置文件来自节点自身的 `browser.profiles` 配置（与本地相同）。
- 如果您不想启用它：
  - 在节点上：`nodeHost.browserProxy.enabled=false`
  - 在网关上：`gateway.nodes.browser.mode="off"`

## Browserless（托管远程 CDP）

[Browserless](https://browserless.io) 是一个托管的 Chromium 服务，通过 HTTPS 暴露
CDP 端点。您可以将 OpenClaw 浏览器配置文件指向一个
Browserless 区域端点，并使用您的 API 密钥进行身份验证。

示例：

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserless",
    remoteCdpTimeoutMs: 2000,
    remoteCdpHandshakeTimeoutMs: 4000,
    profiles: {
      browserless: {
        cdpUrl: "https://production-sfo.browserless.io?token=<BROWSERLESS_API_KEY>",
        color: "#00AA00",
      },
    },
  },
}
```

注意事项：

- 将 `<BROWSERLESS_API_KEY>` 替换为您的真实 Browserless 令牌。
- 选择与您的 Browserless 账户匹配的区域端点（参见他们的文档）。

## 安全性

关键概念：

- 浏览器控制仅限回环；访问通过网关的身份验证或节点配对进行。
- 如果启用了浏览器控制且未配置身份验证，OpenClaw 会在启动时自动生成 `gateway.auth.token` 并将其保存到配置中。
- 将网关和任何节点主机保留在私有网络（如 Tailscale）上；避免公开暴露。
- 将远程 CDP URL/令牌视为机密信息；优先使用环境变量或机密管理器。

远程 CDP 提示：

- 尽可能使用 HTTPS 端点和短期令牌。
- 避免直接在配置文件中嵌入长期令牌。

## 配置文件（多浏览器）

OpenClaw 支持多个命名配置文件（路由配置）。配置文件可以是：

- **openclaw-managed**：一个专用的基于 Chromium 的浏览器实例，具有自己的用户数据目录 + CDP 端口
- **remote**：一个显式的 CDP URL（运行在其他位置的基于 Chromium 的浏览器）
- **extension relay**：通过本地中继 + Chrome 扩展使用现有的 Chrome 标签页

默认设置：

- 如果缺少，会自动创建 `openclaw` 配置文件。
- `chrome` 配置文件内置用于 Chrome 扩展中继（默认指向 `http://127.0.0.1:18792`）。
- 本地 CDP 端口默认从 **18800–18899** 分配。
- 删除配置文件会将其本地数据目录移动到回收站。

所有控制端点接受 `?profile=<name>`；CLI 使用 `--browser-profile`。

## Chrome 扩展中继（使用您的现有 Chrome）

OpenClaw 还可以通过本地 CDP 中继 + Chrome 扩展驱动 **您的现有 Chrome 标签页**（无需单独的“openclaw” Chrome 实例）。

完整指南：[Chrome 扩展](/tools/chrome-extension)

流程：

- Gateway在本地运行（同一台机器）或节点主机运行在浏览器机器上。
- 本地**中继服务器**监听回环`cdpUrl`（默认：`http://127.0.0.1:18792`）。
- 您点击标签页上的**OpenClaw Browser Relay**扩展图标以附加（它不会自动附加）。
- 代理通过正常的`browser`工具控制该标签页，选择正确的配置文件。

如果Gateway运行在其他地方，请在浏览器机器上运行一个节点主机，以便Gateway可以代理浏览器操作。

### 沙盒会话

如果代理会话被沙盒化，`browser`工具可能默认使用`target="sandbox"`（沙盒浏览器）。
Chrome扩展中继接管需要主机浏览器控制，因此可以：

- 以非沙盒模式运行会话，或
- 设置`agents.defaults.sandbox.browser.allowHostControl: true`并在调用工具时使用`target="host"`。

### 设置

1. 加载扩展（开发/未打包）：

```bash
openclaw browser extension install
```

- Chrome → `chrome://extensions` → 启用“开发者模式”
- “加载已解压的扩展程序” → 选择`openclaw browser extension path`打印的目录
- 钉住扩展程序，然后点击您要控制的标签页（徽章显示`ON`）。

2. 使用方法：

- 命令行界面：`openclaw browser --browser-profile chrome tabs`
- 代理工具：`browser`与`profile="chrome"`

可选：如果您想要不同的名称或中继端口，请创建自己的配置文件：

```bash
openclaw browser create-profile \
  --name my-chrome \
  --driver extension \
  --cdp-url http://127.0.0.1:18792 \
  --color "#00AA00"
```

注意事项：

- 此模式依赖于Playwright-on-CDP进行大多数操作（截图/快照/操作）。
- 通过再次点击扩展图标来分离。

## 隔离保证

- **专用用户数据目录**：从不接触您的个人浏览器配置文件。
- **专用端口**：避免`9222`以防止与开发工作流发生冲突。
- **确定性标签页控制**：通过`targetId`目标标签页，而不是“最后一个标签页”。

## 浏览器选择

当本地启动时，OpenClaw选择第一个可用的：

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

您可以使用`browser.executablePath`进行覆盖。

平台：

- macOS：检查`/Applications`和`~/Applications`。
- Linux：查找`google-chrome`，`brave`，`microsoft-edge`，`chromium`等。
- Windows：检查常见的安装位置。

## 控制API（可选）

仅适用于本地集成，Gateway暴露一个小的回环HTTP API：

- 状态/启动/停止: `GET /`, `POST /start`, `POST /stop`
- 标签页: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- 快照/截图: `GET /snapshot`, `POST /screenshot`
- 操作: `POST /navigate`, `POST /act`
- 钩子: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- 下载: `POST /download`, `POST /wait/download`
- 调试: `GET /console`, `POST /pdf`
- 调试: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- 网络: `POST /response/body`
- 状态: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- 状态: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- 设置: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

所有端点接受 `?profile=<name>`。

如果网关认证已配置，浏览器HTTP路由也需要认证：

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` 或使用该密码进行HTTP基本认证

### Playwright 要求

某些功能（导航/操作/AI快照/角色快照，元素截图，PDF）需要
Playwright。如果未安装Playwright，这些端点将返回一个明确的501
错误。对于openclaw管理的Chrome，ARIA快照和基本截图仍然有效。
对于Chrome扩展中继驱动程序，ARIA快照和截图需要Playwright。

如果您看到 `Playwright is not available in this gateway build`，安装完整的
Playwright包（不是 `playwright-core`），然后重启网关，或者重新安装
带有浏览器支持的OpenClaw。

#### Docker Playwright 安装

如果您的网关在Docker中运行，请避免 `npx playwright`（npm覆盖冲突）。
改用捆绑的CLI：

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

要持久化浏览器下载，请设置 `PLAYWRIGHT_BROWSERS_PATH`（例如，
`/home/node/.cache/ms-playwright`），并确保通过 `/home/node` 或绑定挂载持久化 `OPENCLAW_HOME_VOLUME`。参见 [Docker](/install/docker)。

## 工作原理（内部）

高层次流程：

- 小型 **控制服务器** 接受HTTP请求。
- 它通过 **CDP** 连接到基于Chromium的浏览器（Chrome/Brave/Edge/Chromium）。
- 对于高级操作（点击/输入/快照/PDF），它在CDP之上使用 **Playwright**。
- 当缺少Playwright时，仅可用非Playwright操作。

这种设计使代理保持在一个稳定、确定的接口上，同时允许您交换本地/远程浏览器和配置文件。

## CLI 快速参考

所有命令接受 `--browser-profile <name>` 以针对特定配置文件。
所有命令还接受 `--json` 以获得机器可读输出（稳定的负载）。

基础知识：

检查:

- `openclaw browser screenshot`
- `openclaw browser screenshot --full-page`
- `openclaw browser screenshot --ref 12`
- `openclaw browser screenshot --ref e12`
- `openclaw browser snapshot`
- `openclaw browser snapshot --format aria --limit 200`
- `openclaw browser snapshot --interactive --compact --depth 6`
- `openclaw browser snapshot --efficient`
- `openclaw browser snapshot --labels`
- `openclaw browser snapshot --selector "#main" --interactive`
- `openclaw browser snapshot --frame "iframe#main" --interactive`
- `openclaw browser console --level error`
- `openclaw browser errors --clear`
- `openclaw browser requests --filter api --clear`
- `openclaw browser pdf`
- `openclaw browser responsebody "**/api" --max-chars 5000`

操作:

- `openclaw browser navigate https://example.com`
- `openclaw browser resize 1280 720`
- `openclaw browser click 12 --double`
- `openclaw browser click e12 --double`
- `openclaw browser type 23 "hello" --submit`
- `openclaw browser press Enter`
- `openclaw browser hover 44`
- `openclaw browser scrollintoview e12`
- `openclaw browser drag 10 11`
- `openclaw browser select 9 OptionA OptionB`
- `openclaw browser download e12 report.pdf`
- `openclaw browser waitfordownload report.pdf`
- `openclaw browser upload /tmp/openclaw/uploads/file.pdf`
- `openclaw browser fill --fields '[{"ref":"1","type":"text","value":"Ada"}]'`
- `openclaw browser dialog --accept`
- `openclaw browser wait --text "Done"`
- `openclaw browser wait "#main" --url "**/dash" --load networkidle --fn "window.ready===true"`
- `openclaw browser evaluate --fn '(el) => el.textContent' --ref 7`
- `openclaw browser highlight e12`
- `openclaw browser trace start`
- `openclaw browser trace stop`

状态:

- `openclaw browser cookies`
- `openclaw browser cookies set session abc123 --url "https://example.com"`
- `openclaw browser cookies clear`
- `openclaw browser storage local get`
- `openclaw browser storage local set theme dark`
- `openclaw browser storage session clear`
- `openclaw browser set offline on`
- `openclaw browser set headers --headers-json '{"X-Debug":"1"}'`
- `openclaw browser set credentials user pass`
- `openclaw browser set credentials --clear`
- `openclaw browser set geo 37.7749 -122.4194 --origin "https://example.com"`
- `openclaw browser set geo --clear`
- `openclaw browser set media dark`
- `openclaw browser set timezone America/New_York`
- `openclaw browser set locale en-US`
- `openclaw browser set device "iPhone 14"`

注释:

- `upload` 和 `dialog` 是 **arming** 调用；在触发选择器/对话框的点击/按压之前运行它们。
- 下载和跟踪输出路径被限制为 OpenClaw 临时根目录：
  - 跟踪：`/tmp/openclaw` （备用：`${os.tmpdir()}/openclaw`）
  - 下载：`/tmp/openclaw/downloads` （备用：`${os.tmpdir()}/openclaw/downloads`）
- 上传路径被限制为一个 OpenClaw 临时上传根目录：
  - 上传：`/tmp/openclaw/uploads` （备用：`${os.tmpdir()}/openclaw/uploads`）
- `upload` 还可以通过 `--input-ref` 或 `--element` 直接设置文件输入。
- `snapshot`:
  - `--format ai` （Playwright 安装时默认）：返回带有数字引用的 AI 快照 (`aria-ref="<n>"`)。
  - `--format aria`：返回可访问性树（无引用；仅用于检查）。
  - `--efficient` （或 `--mode efficient`）：紧凑角色快照预设（交互式 + 紧凑 + 深度 + 较小 maxChars）。
  - 配置默认值（仅限工具/CLI）：设置 `browser.snapshotDefaults.mode: "efficient"` 以在调用者不传递模式时使用高效快照（参见 [网关配置](/gateway/configuration#browser-openclaw-managed-browser)）。
  - 角色快照选项 (`--interactive`, `--compact`, `--depth`, `--selector`) 强制使用带有类似 `ref=e12` 的引用的角色快照。
  - `--frame "<iframe selector>"` 将角色快照范围限定为 iframe（与类似 `e12` 的角色引用配对）。
  - `--interactive` 输出一个易于选择的交互元素平面列表（最适合驱动操作）。
  - `--labels` 添加一个仅视口的截图，并叠加引用标签（打印 `MEDIA:<path>`）。
- `click`/`type`/等需要来自 `snapshot` 的 `ref` （数字 `12` 或角色引用 `e12`）。
  有意不支持用于操作的 CSS 选择器。

## 快照和引用

OpenClaw 支持两种“快照”样式：

- **AI 快照（数字引用）**：`openclaw browser snapshot` （默认；`--format ai`）
  - 输出：包含数字引用的文本快照。
  - 操作：`openclaw browser click 12`, `openclaw browser type 23 "hello"`。
  - 内部，通过 Playwright 的 `aria-ref` 解析引用。

- **角色快照（角色引用如 `e12`）**：`openclaw browser snapshot --interactive` （或 `--compact`, `--depth`, `--selector`, `--frame`）
  - 输出：基于角色的列表/树，带有 `[ref=e12]` （以及可选的 `[nth=1]`）。
  - 操作：`openclaw browser click e12`, `openclaw browser highlight e12`。
  - 内部，通过 `getByRole(...)` 解析引用（对于重复项使用 `nth()`）。
  - 添加 `--labels` 以包含带有叠加的 `e12` 标签的视口截图。

引用行为：

- 引用 **在导航之间不稳定**；如果出现问题，请重新运行 `snapshot` 并使用新的引用。
- 如果角色快照是通过 `--frame` 获取的，角色引用将限定在该 iframe 内，直到下一次角色快照。

## 等待增强功能

您可以等待不仅仅是时间/文本：

- 等待URL（Playwright支持的glob模式）:
  - `openclaw browser wait --url "**/dash"`
- 等待加载状态:
  - `openclaw browser wait --load networkidle`
- 等待JS谓词:
  - `openclaw browser wait --fn "window.ready===true"`
- 等待选择器变为可见:
  - `openclaw browser wait "#main"`

这些可以组合使用:

```bash
openclaw browser wait "#main" \
  --url "**/dash" \
  --load networkidle \
  --fn "window.ready===true" \
  --timeout-ms 15000
```

## 调试工作流

当操作失败时（例如“不可见”，“严格模式违规”，“被覆盖”）:

1. `openclaw browser snapshot --interactive`
2. 使用 `click <ref>` / `type <ref>`（交互模式下优先使用角色引用）
3. 如果仍然失败：使用 `openclaw browser highlight <ref>` 查看Playwright的目标
4. 如果页面行为异常:
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. 深度调试：记录跟踪:
   - `openclaw browser trace start`
   - 复现问题
   - `openclaw browser trace stop`（打印 `TRACE:<path>`）

## JSON输出

`--json` 用于脚本编写和结构化工具。

示例:

```bash
openclaw browser status --json
openclaw browser snapshot --interactive --json
openclaw browser requests --filter api --json
openclaw browser cookies --json
```

JSON中的角色快照包括 `refs` 加上一个小的 `stats` 块（行/字符/引用/交互），以便工具可以推理有效负载的大小和密度。

## 状态和环境设置

这些对于“使站点表现得像X”的工作流很有用：

- Cookie: `cookies`, `cookies set`, `cookies clear`
- 存储: `storage local|session get|set|clear`
- 离线: `set offline on|off`
- 请求头: `set headers --headers-json '{"X-Debug":"1"}'`（旧版 `set headers --json '{"X-Debug":"1"}'` 仍受支持）
- HTTP基本认证: `set credentials user pass`（或 `--clear`）
- 地理位置: `set geo <lat> <lon> --origin "https://example.com"`（或 `--clear`）
- 媒体: `set media dark|light|no-preference|none`
- 时区/区域设置: `set timezone ...`, `set locale ...`
- 设备/视口:
  - `set device "iPhone 14"`（Playwright设备预设）
  - `set viewport 1280 720`

## 安全与隐私

- openclaw浏览器配置文件可能包含已登录的会话；将其视为敏感信息。
- `browser act kind=evaluate` / `openclaw browser evaluate` 和 `wait --fn`
  在页面上下文中执行任意JavaScript。提示注入可以控制
  这些。如果不需要，请使用 `browser.evaluateEnabled=false` 禁用它。
- 对于登录和反机器人注释（X/Twitter等），请参阅 [浏览器登录 + X/Twitter发布](/tools/browser-login)。
- 保持网关/节点主机私有（回环或仅限tailnet）。
- 远程CDP端点功能强大；请进行隧道传输并保护它们。

## 故障排除

对于Linux特定的问题（尤其是snap Chromium），请参阅
[浏览器故障排除](/tools/browser-linux-troubleshooting)。

## 代理工具 + 控制方式如何工作

代理获得 **一个工具** 用于浏览器自动化：

- `browser` — status/start/stop/tabs/open/focus/close/snapshot/screenshot/navigate/act

映射如下：

- `browser snapshot` 返回一个稳定的UI树（AI或ARIA）。
- `browser act` 使用快照 `ref` ID进行点击/输入/拖动/选择。
- `browser screenshot` 捕获像素（整页或元素）。
- `browser` 接受：
  - `profile` 选择一个命名的浏览器配置文件（openclaw、chrome 或远程 CDP）。
  - `target` (`sandbox` | `host` | `node`) 选择浏览器的位置。
  - 在沙盒会话中，`target: "host"` 需要 `agents.defaults.sandbox.browser.allowHostControl=true`。
  - 如果省略 `target`：沙盒会话默认为 `sandbox`，非沙盒会话默认为 `host`。
  - 如果连接了支持浏览器的节点，该工具可能会自动路由到它，除非你固定 `target="host"` 或 `target="node"`。

这使代理保持确定性并避免脆弱的选择器。