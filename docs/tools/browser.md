---
summary: "Integrated browser control service + action commands"
read_when:
  - Adding agent-controlled browser automation
  - Debugging why openclaw is interfering with your own Chrome
  - Implementing browser settings + lifecycle in the macOS app
title: "Browser (OpenClaw-managed)"
---
# 浏览器 (openclaw-managed)

OpenClaw 可以运行一个**专用的 Chrome/Brave/Edge/Chromium 配置文件**，该配置文件由代理控制。
它与您的个人浏览器隔离，并通过网关内的小型本地控制服务进行管理（仅限回环）。

初学者视图：

- 将其视为一个**独立的、仅供代理使用的浏览器**。
- `openclaw` 配置文件**不会**影响您的个人浏览器配置文件。
- 代理可以在安全通道中**打开标签页、读取页面、点击和输入**。
- 默认的 `chrome` 配置文件通过扩展中继使用**系统默认的 Chromium 浏览器**；切换到 `openclaw` 以使用隔离的托管浏览器。

## 您将获得

- 一个名为 **openclaw** 的单独浏览器配置文件（默认为橙色强调）。
- 确定性的标签页控制（列表/打开/聚焦/关闭）。
- 代理操作（点击/输入/拖动/选择）、快照、屏幕截图、PDF。
- 可选的多配置文件支持 (`openclaw`, `work`, `remote`, ...).

此浏览器**不是**您的日常驱动程序。它是用于代理自动化和验证的安全隔离环境。

## 快速开始

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

如果出现“浏览器已禁用”，请在配置中启用它（见下文）并重新启动网关。

## 配置文件: `openclaw` vs `chrome`

- `openclaw`: 托管的、隔离的浏览器（不需要扩展）。
- `chrome`: 到您的**系统浏览器**的扩展中继（需要将 OpenClaw 扩展附加到标签页）。

如果您希望默认使用托管模式，请设置 `browser.defaultProfile: "openclaw"`。

## 配置

浏览器设置位于 `~/.openclaw/openclaw.json` 中。

```json5
{
  browser: {
    enabled: true, // default: true
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true, // default trusted-network mode
      // allowPrivateNetwork: true, // legacy alias
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
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

- 浏览器控制服务绑定到从 `gateway.port` 派生的回环端口（默认：`18791`，即网关 + 2）。中继使用下一个端口 (`18792`)。
- 如果您覆盖了网关端口 (`gateway.port` 或 `OPENCLAW_GATEWAY_PORT`)，派生的浏览器端口会相应移动以保持在同一“家族”内。
- 当未设置时，`cdpUrl` 默认为中继端口。
- `remoteCdpTimeoutMs` 适用于远程（非回环）CDP 可达性检查。
- `remoteCdpHandshakeTimeoutMs` 适用于远程 CDP WebSocket 可达性检查。
- 浏览器导航/打开标签页在导航前受到 SSRF 保护，并在导航后的最终 `http(s)` URL 上进行最佳努力的重新检查。
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` 默认为 `true`（受信任网络模型）。将其设置为 `false` 以进行严格的仅公共浏览。
- `browser.ssrfPolicy.allowPrivateNetwork` 作为遗留别名继续支持以保持兼容性。
- `attachOnly: true` 表示“永不启动本地浏览器；仅当它已经在运行时才附加。”
- `color` + 每个配置文件的 `color` 为浏览器 UI 着色，以便您可以查看哪个配置文件处于活动状态。
- 默认配置文件是 `openclaw`（OpenClaw 托管的独立浏览器）。使用 `defaultProfile: "chrome"` 选择 Chrome 扩展中继。
- 自动检测顺序：基于 Chromium 的系统默认浏览器；否则按 Chrome → Brave → Edge → Chromium → Chrome Canary 顺序检测。
- 本地 `openclaw` 配置文件自动分配 `cdpPort`/`cdpUrl` —— 仅在远程 CDP 时设置这些。

## 使用 Brave（或其他基于 Chromium 的浏览器）

如果您的**系统默认**浏览器是基于 Chromium 的（Chrome/Brave/Edge 等），OpenClaw 会自动使用它。设置 `browser.executablePath` 以覆盖自动检测：

命令行示例：

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

- **本地控制（默认）：** 网关启动回环控制服务并可以启动本地浏览器。
- **远程控制（节点主机）：** 在具有浏览器的机器上运行节点主机；网关将浏览器操作代理到该节点。
- **远程 CDP：** 设置 `browser.profiles.<name>.cdpUrl`（或 `browser.cdpUrl`）以连接到远程基于 Chromium 的浏览器。在这种情况下，OpenClaw 不会启动本地浏览器。

远程 CDP URL 可以包含认证：

- 查询令牌（例如，`https://provider.example?token=<token>`）
- HTTP 基本认证（例如，`https://user:pass@provider.example`）

OpenClaw 在调用 `/json/*` 端点和连接到 CDP WebSocket 时保留认证。建议使用环境变量或密钥管理器来存储令牌，而不是将它们提交到配置文件中。

## 节点浏览器代理（零配置默认）

如果您在具有浏览器的机器上运行**节点主机**，OpenClaw 可以自动将浏览器工具调用路由到该节点，而无需任何额外的浏览器配置。这是远程网关的默认路径。

注意事项：

- 节点主机通过**代理命令**暴露其本地浏览器控制服务器。
- 配置文件来自节点自己的 `browser.profiles` 配置（与本地相同）。
- 如果您不想使用它：
  - 在节点上：`nodeHost.browserProxy.enabled=false`
  - 在网关上：`gateway.nodes.browser.mode="off"`

## 无浏览器（托管远程 CDP）

[Browserless](https://browserless.io) 是一个托管的 Chromium 服务，通过 HTTPS 暴露 CDP 端点。您可以将 OpenClaw 浏览器配置文件指向 Browserless 区域端点，并使用您的 API 密钥进行身份验证。

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

- 用您的真实 Browserless 令牌替换 `<BROWSERLESS_API_KEY>`。
- 选择与您的 Browserless 账户匹配的区域端点（参阅他们的文档）。

## 安全

关键概念：

- 浏览器控制仅限于回环；访问通过网关的身份验证或节点配对流动。
- 如果启用了浏览器控制且未配置身份验证，OpenClaw 会在启动时自动生成 `gateway.auth.token` 并将其持久化到配置中。
- 将网关和任何节点主机保留在私有网络（Tailscale）上；避免公开暴露。
- 将远程 CDP URL 和令牌视为机密；优先使用环境变量或密钥管理器。

远程 CDP 提示：

- 尽可能使用 HTTPS 端点和短期令牌。
- 避免直接在配置文件中嵌入长期令牌。

## 配置文件（多浏览器）

OpenClaw 支持多个命名配置文件（路由配置）。配置文件可以是：

- **openclaw-managed**: 一个专用的基于 Chromium 的浏览器实例，具有自己的用户数据目录 + CDP 端口
- **remote**: 明确的 CDP URL（在其他地方运行的基于 Chromium 的浏览器）
- **extension relay**: 通过本地中继 + Chrome 扩展使用您现有的 Chrome 标签页

默认值：

- 如果缺少 `openclaw` 配置文件，则会自动创建。
- `chrome` 配置文件内置用于 Chrome 扩展中继（默认指向 `http://127.0.0.1:18792`）。
- 本地 CDP 端口默认从 **18800–18899** 分配。
- 删除配置文件会将其本地数据目录移至回收站。

所有控制端点都接受 `?profile=<name>`；CLI 使用 `--browser-profile`。

## Chrome 扩展中继（使用您现有的 Chrome）

OpenClaw 还可以通过本地 CDP 中继 + Chrome 扩展来驱动**您现有的 Chrome 标签页**（无需单独的“openclaw”Chrome 实例）。

完整指南：[Chrome 扩展](/tools/chrome-extension)

流程：

- 网关在本地运行（同一台机器）或在浏览器机器上运行节点主机。
- 本地**中继服务器**监听回环 `cdpUrl`（默认：`http://127.0.0.1:18792`）。
- 单击标签页上的**OpenClaw 浏览器中继**扩展图标以附加（它不会自动附加）。
- 代理通过选择正确的配置文件，使用常规的 `browser` 工具控制该标签页。

如果网关在其他地方运行，请在浏览器机器上运行节点主机，以便网关可以代理浏览器操作。

### 沙盒会话

如果代理会话被沙盒化，`browser` 工具可能会默认为 `target="sandbox"`（沙盒浏览器）。
Chrome 扩展中继接管需要主机浏览器控制，因此：

- 以非沙盒方式运行会话，或
- 设置 `agents.defaults.sandbox.browser.allowHostControl: true` 并在调用工具时使用 `target="host"`。

### 设置

1. 加载扩展（开发/未打包）：

```bash
openclaw browser extension install
```

- Chrome → `chrome://extensions` → 启用“开发者模式”
- “加载未打包的扩展程序”→ 选择由 `openclaw browser extension path` 打印的目录
- 固定扩展程序，然后单击要控制的标签页上的扩展程序（徽章显示 `ON`）。

2. 使用它：

- CLI: `openclaw browser --browser-profile chrome tabs`
- 代理工具: `browser` 与 `profile="chrome"`

可选：如果您想要不同的名称或中继端口，可以创建自己的配置文件：

注意事项：

- 此模式依赖于Playwright-on-CDP进行大多数操作（截图/快照/动作）。
- 通过再次点击扩展图标来分离。

## 隔离保证

- **专用用户数据目录**：从不触碰您的个人浏览器配置文件。
- **专用端口**：避免`9222`以防止与开发工作流程发生冲突。
- **确定性标签控制**：通过`targetId`而不是“最后一个标签”来定位标签。

## 浏览器选择

本地启动时，OpenClaw会选择第一个可用的浏览器：

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

您可以使用`browser.executablePath`覆盖此设置。

平台：

- macOS: 检查`/Applications`和`~/Applications`。
- Linux: 查找`google-chrome`, `brave`, `microsoft-edge`, `chromium`等。
- Windows: 检查常见的安装位置。

## 控制API（可选）

仅对于本地集成，网关暴露了一个小型回环HTTP API：

- 状态/启动/停止: `GET /`, `POST /start`, `POST /stop`
- 标签: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- 快照/截图: `GET /snapshot`, `POST /screenshot`
- 动作: `POST /navigate`, `POST /act`
- 钩子: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- 下载: `POST /download`, `POST /wait/download`
- 调试: `GET /console`, `POST /pdf`
- 调试: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- 网络: `POST /response/body`
- 状态: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- 状态: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- 设置: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

所有端点接受`?profile=<name>`。

如果配置了网关认证，则浏览器HTTP路由也需要认证：

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>`或带有该密码的HTTP基本认证

### Playwright要求

某些功能（导航/执行/AI快照/角色快照、元素截图、PDF）需要
Playwright。如果没有安装Playwright，这些端点将返回明确的501错误。
ARIA快照和基本截图仍然适用于openclaw管理的Chrome。
对于Chrome扩展中继驱动程序，ARIA快照和截图需要Playwright。

如果您看到`Playwright is not available in this gateway build`，请安装完整的
Playwright包（不是`playwright-core`），然后重启网关，或者重新安装
带浏览器支持的OpenClaw。

#### Docker中的Playwright安装

如果您的网关运行在Docker中，请避免`npx playwright`（npm覆盖冲突）。
改用捆绑的CLI：

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

要持久化浏览器下载，请设置`PLAYWRIGHT_BROWSERS_PATH`（例如，
`/home/node/.cache/ms-playwright`），并确保通过
`OPENCLAW_HOME_VOLUME`或绑定挂载来持久化`/home/node`。参见[Docker](/install/docker)。

## 工作原理（内部）

高层次流程：

- 一个小的**控制服务器**接收HTTP请求。
- 它通过**CDP**连接到基于Chromium的浏览器（Chrome/Brave/Edge/Chromium）。
- 对于高级操作（点击/输入/快照/PDF），它在CDP之上使用**Playwright**。
- 当缺少Playwright时，只有非Playwright操作可用。

这种设计保持代理在一个稳定且确定性的接口上，同时允许您切换本地/远程浏览器和配置文件。

## CLI快速参考

所有命令都接受`--browser-profile <name>`以针对特定配置文件。
所有命令还接受`--json`以获得机器可读输出（稳定的负载）。

基础：

- `openclaw browser status`
- `openclaw browser start`
- `openclaw browser stop`
- `openclaw browser tabs`
- `openclaw browser tab`
- `openclaw browser tab new`
- `openclaw browser tab select 2`
- `openclaw browser tab close 2`
- `openclaw browser open https://example.com`
- `openclaw browser focus abcd1234`
- `openclaw browser close abcd1234`

检查：

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

动作：

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

状态：

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

注意事项：

- `upload`和`dialog`是**预设**调用；在触发选择器/对话框的点击/按下之前运行它们。
- 下载和跟踪输出路径限制在OpenClaw临时根目录内：
  - 跟踪: `/tmp/openclaw`（备用: `${os.tmpdir()}/openclaw`）
  - 下载: `/tmp/openclaw/downloads`（备用: `${os.tmpdir()}/openclaw/downloads`）
- 上传路径限制在OpenClaw临时上传根目录内：
  - 上传: `/tmp/openclaw/uploads`（备用: `${os.tmpdir()}/openclaw/uploads`）
- `upload`也可以通过`--input-ref`或`--element`直接设置文件输入。
- `snapshot`:
  - `--format ai`（默认情况下安装了Playwright）：返回带有数字引用的AI快照(`aria-ref="<n>"`)。
  - `--format aria`：返回无障碍树（无引用；仅用于检查）。
  - `--efficient`（或`--mode efficient`）：紧凑的角色快照预设（交互式+紧凑+深度+较低的最大字符数）。
  - 配置默认值（仅工具/CLI）：设置`browser.snapshotDefaults.mode: "efficient"`以在调用者未传递模式时使用高效的快照（参见[网关配置](/gateway/configuration#browser-openclaw-managed-browser)）。
  - 角色快照选项(`--interactive`, `--compact`, `--depth`, `--selector`)强制使用带有类似`ref=e12`引用的角色快照。
  - `--frame "<iframe selector>"`将角色快照范围限制在一个iframe内（与像`e12`这样的角色引用配对）。
  - `--labels`输出一个扁平的、易于选择的交互元素列表（最适合驱动动作）。
  - `--labels`添加一个仅视口的屏幕截图，并带有叠加的引用标签（打印`MEDIA:<path>`）。
- `click`/`type`/等需要来自`snapshot`的`ref`（数字`12`或角色引用`e12`）。
  CSS选择器故意不支持用于动作。

## 快照和引用

OpenClaw支持两种“快照”样式：

- **AI快照（数字引用）**：`openclaw browser snapshot`（默认；`--format ai`）
  - 输出：包含数字引用的文本快照。
  - 动作：`openclaw browser click 12`, `openclaw browser type 23 "hello"`。
  - 内部，引用通过Playwright的`aria-ref`解析。

- **角色快照（如`e12`的角色引用）**：`openclaw browser snapshot --interactive`（或`--compact`, `--depth`, `--selector`, `--frame`）
  - 输出：带有`[ref=e12]`（和可选的`[nth=1]`）的角色列表/树。
  - 动作：`openclaw browser click e12`, `openclaw browser highlight e12`。
  - 内部，引用通过`getByRole(...)`解析（加上`nth()`处理重复项）。
  - 添加`--labels`以包括带有叠加`e12`标签的视口截图。

引用行为：

- 引用**不会在导航之间保持稳定**；如果出现问题，请重新运行`snapshot`并使用新的引用。
- 如果角色快照是使用`--frame`拍摄的，那么直到下一个角色快照前，角色引用将被限制在那个iframe内。

## 等待增强

您可以等待不仅仅是时间/文本：

- 等待URL（Playwright支持的通配符）：
  - `openclaw browser wait --url "**/dash"`
- 等待加载状态：
  - `openclaw browser wait --load networkidle`
- 等待JS谓词：
  - `openclaw browser wait --fn "window.ready===true"`
- 等待选择器变为可见：
  - `openclaw browser wait "#main"`

这些可以组合使用：

## 调试工作流

当某个操作失败（例如：“不可见”、“严格模式违规”、“被覆盖”）时：

1. `openclaw browser snapshot --interactive`
2. 使用 `click <ref>` / `type <ref>`（在交互模式下优先使用角色引用）
3. 如果仍然失败：`openclaw browser highlight <ref>` 以查看 Playwright 的目标
4. 如果页面行为异常：
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. 深度调试：记录一个跟踪：
   - `openclaw browser trace start`
   - 复现问题
   - `openclaw browser trace stop`（打印 `TRACE:<path>`）

## JSON 输出

`--json` 用于脚本和结构化工具。

示例：

```bash
openclaw browser status --json
openclaw browser snapshot --interactive --json
openclaw browser requests --filter api --json
openclaw browser cookies --json
```

JSON 中的角色快照包括 `refs` 加上一个小的 `stats` 块（行/字符/引用/交互），以便工具可以推理有效负载大小和密度。

## 状态和环境设置

这些对于“使站点表现得像 X”的工作流程非常有用：

- Cookies: `cookies`, `cookies set`, `cookies clear`
- 存储: `storage local|session get|set|clear`
- 离线: `set offline on|off`
- 标头: `set headers --headers-json '{"X-Debug":"1"}'`（旧版 `set headers --json '{"X-Debug":"1"}'` 仍受支持）
- HTTP 基本认证: `set credentials user pass`（或 `--clear`）
- 地理位置: `set geo <lat> <lon> --origin "https://example.com"`（或 `--clear`）
- 媒体: `set media dark|light|no-preference|none`
- 时区/区域设置: `set timezone ...`, `set locale ...`
- 设备/视口:
  - `set device "iPhone 14"`（Playwright 设备预设）
  - `set viewport 1280 720`

## 安全与隐私

- openclaw 浏览器配置文件可能包含已登录会话；将其视为敏感信息。
- `browser act kind=evaluate` / `openclaw browser evaluate` 和 `wait --fn`
  在页面上下文中执行任意 JavaScript。提示注入可以引导这一点。如果您不需要它，请使用 `browser.evaluateEnabled=false` 禁用它。
- 对于登录和反机器人注释（X/Twitter 等），请参阅 [浏览器登录 + X/Twitter 发布](/tools/browser-login)。
- 保持网关/节点主机私有（仅限回环或尾网）。
- 远程 CDP 端点功能强大；对其进行隧道传输并保护它们。

严格模式示例（默认阻止私有/内部目的地）：

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"], // optional exact allow
    },
  },
}
```

## 故障排除

对于特定于 Linux 的问题（尤其是 snap Chromium），请参阅 [浏览器故障排除](/tools/browser-linux-troubleshooting)。

## 代理工具及控制方式

代理获得 **一个工具** 用于浏览器自动化：

- `browser` — 状态/启动/停止/标签页/打开/聚焦/关闭/快照/截图/导航/操作

映射方式：

- `browser snapshot` 返回稳定的 UI 树（AI 或 ARIA）。
- `browser act` 使用快照 `ref` ID 进行点击/输入/拖动/选择。
- `browser screenshot` 捕获像素（整页或元素）。
- `browser` 接受：
  - `profile` 以选择命名的浏览器配置文件（openclaw、chrome 或远程 CDP）。
  - `target` (`sandbox` | `host` | `node`) 以选择浏览器所在的位置。
  - 在沙盒会话中，`target: "host"` 需要 `agents.defaults.sandbox.browser.allowHostControl=true`。
  - 如果省略了 `target`：沙盒会话默认为 `sandbox`，非沙盒会话默认为 `host`。
  - 如果连接了能够运行浏览器的节点，除非您固定了 `target="host"` 或 `target="node"`，否则工具可能会自动路由到该节点。

这使得代理具有确定性，并避免脆弱的选择器。