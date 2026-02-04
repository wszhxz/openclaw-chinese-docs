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
它与您的个人浏览器隔离，并通过网关中的一个小的本地控制服务进行管理（仅限回环）。

初学者视角：

- 将其视为一个 **独立的、仅代理使用的浏览器**。
- `openclaw` 配置文件 **不会** 触及您的个人浏览器配置文件。
- 代理可以在安全的环境中 **打开标签页、读取页面、点击和输入**。
- 默认的 `chrome` 配置文件通过扩展中继使用 **系统默认的 Chromium 浏览器**；切换到 `openclaw` 以使用隔离的受管浏览器。

## 您将获得

- 一个名为 **openclaw** 的独立浏览器配置文件（默认橙色强调）。
- 确定性的标签页控制（列出/打开/聚焦/关闭）。
- 代理操作（点击/输入/拖动/选择）、快照、屏幕截图、PDF。
- 可选的多配置文件支持 (`openclaw`, `work`, `remote`, ...)。

此浏览器 **不是** 您的日常驱动程序。它是一个安全、隔离的表面，用于代理自动化和验证。

## 快速开始

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

如果出现“浏览器已禁用”，请在配置中启用它（见下文），然后重启网关。

## 配置文件：`openclaw` 对比 `chrome`

- `openclaw`：受管、隔离的浏览器（无需扩展）。
- `chrome`：扩展中继到您的 **系统浏览器**（需要将 OpenClaw 扩展附加到标签页）。

设置 `browser.defaultProfile: "openclaw"` 以默认使用受管模式。

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

- 浏览器控制服务绑定到从 `gateway.port` 派生的回环端口（默认：`18791`，即网关 + 2）。中继使用下一个端口 (`18792`)。
- 如果您覆盖了网关端口 (`gateway.port` 或 `OPENCLAW_GATEWAY_PORT`)，派生的浏览器端口会相应地移动以保持在同一“系列”中。
- `cdpUrl` 在未设置时默认为中继端口。
- `remoteCdpTimeoutMs` 适用于远程（非回环）CDP 可达性检查。
- `remoteCdpHandshakeTimeoutMs` 适用于远程 CDP WebSocket 可达性检查。
- `attachOnly: true` 表示“永不启动本地浏览器；仅附加已运行的浏览器。”
- `color` + 每个配置文件的 `color` 调整浏览器 UI 以便您可以看到哪个配置文件处于活动状态。
- 默认配置文件是 `chrome`（扩展中继）。使用 `defaultProfile: "openclaw"` 用于受管浏览器。
- 自动检测顺序：如果系统默认浏览器基于 Chromium，则使用它；否则 Chrome → Brave → Edge → Chromium → Chrome Canary。
- 本地 `openclaw` 配置文件自动分配 `cdpPort`/`cdpUrl` — 仅对远程 CDP 设置这些。

## 使用 Brave（或其他基于 Chromium 的浏览器）

如果您的 **系统默认** 浏览器是基于 Chromium 的（Chrome/Brave/Edge 等），OpenClaw 会自动使用它。设置 `browser.executablePath` 以覆盖自动检测：

CLI 示例：

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
- **远程控制（节点主机）：** 在具有浏览器的机器上运行节点主机；网关将浏览器操作代理到该主机。
- **远程 CDP：** 设置 `browser.profiles.<name>.cdpUrl`（或 `browser.cdpUrl`）以附加到远程基于 Chromium 的浏览器。在这种情况下，OpenClaw 不会启动本地浏览器。

远程 CDP URL 可以包含认证信息：

- 查询令牌（例如，`https://provider.example?token=<token>`）
- HTTP 基本认证（例如，`https://user:pass@provider.example`）

OpenClaw 在调用 `/json/*` 端点以及连接到 CDP WebSocket 时保留认证信息。建议使用环境变量或密钥管理器而不是将令牌提交到配置文件中。

## 节点浏览器代理（零配置默认）

如果您在具有浏览器的机器上运行 **节点主机**，OpenClaw 可以自动将浏览器工具调用路由到该节点而无需额外的浏览器配置。这是远程网关的默认路径。

注意事项：

- 节点主机通过 **代理命令** 公开其本地浏览器控制服务器。
- 配置文件来自节点自身的 `browser.profiles` 配置（与本地相同）。
- 如不需要，可禁用：
  - 在节点上：`nodeHost.browserProxy.enabled=false`
  - 在网关上：`gateway.nodes.browser.mode="off"`

## Browserless（托管远程 CDP）

[Browserless](https://browserless.io) 是一个托管的 Chromium 服务，通过 HTTPS 暴露 CDP 端点。您可以将 OpenClaw 浏览器配置文件指向 Browserless 区域端点并通过您的 API 密钥进行身份验证。

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

- 将 `<BROWSERLESS_API_KEY>` 替换为您的实际 Browserless 令牌。
- 选择与您的 Browserless 账户匹配的区域端点（参见他们的文档）。

## 安全性

关键概念：

- 浏览器控制仅限回环；访问流经网关的身份验证或节点配对。
- 将网关和任何节点主机保留在私有网络（Tailscale）上；避免公开暴露。
- 将远程 CDP URL/令牌视为机密；优先使用环境变量或密钥管理器。

远程 CDP 提示：

- 尽可能使用 HTTPS 端点和短期令牌。
- 避免直接在配置文件中嵌入长期令牌。

## 配置文件（多浏览器）

OpenClaw 支持多个命名配置文件（路由配置）。配置文件可以是：

- **openclaw-managed**：一个专用的基于 Chromium 的浏览器实例，具有自己的用户数据目录 + CDP 端口
- **remote**：显式的 CDP URL（在其他地方运行的基于 Chromium 的浏览器）
- **扩展中继**：通过本地中继 + Chrome 扩展使用现有的 Chrome 标签页

默认值：

- 如果缺少，自动创建 `openclaw` 配置文件。
- 内置的 `chrome` 配置文件用于 Chrome 扩展中继（默认指向 `http://127.0.0.1:18792`）。
- 默认情况下，本地 CDP 端口从 **18800–18899** 分配。
- 删除配置文件会将其本地数据目录移到回收站。

所有控制端点接受 `?profile=<name>`；CLI 使用 `--browser-profile`。

## Chrome 扩展中继（使用现有 Chrome）

OpenClaw 还可以通过本地 CDP 中继 + Chrome 扩展驱动 **您的现有 Chrome 标签页**（无需单独的“openclaw” Chrome 实例）。

完整指南：[Chrome 扩展](/tools/chrome-extension)

流程：

- 网关在本地（同一台机器）运行或节点主机在浏览器机器上运行。
- 本地 **中继服务器** 监听回环 `cdpUrl`（默认：`http://127.0.0.1:18792`）。
- 您点击标签上的 **OpenClaw Browser Relay** 扩展图标以附加（它不会自动附加）。
- 代理通过正常的 `browser` 工具控制该标签，通过选择正确的配置文件。

如果网关在其他地方运行，请在浏览器机器上运行节点主机，以便网关可以代理浏览器操作。

### 沙盒会话

如果代理会话被沙盒化，`browser` 工具可能会默认使用 `target="sandbox"`（沙盒浏览器）。
Chrome 扩展中继接管需要主机浏览器控制，因此可以：

- 以非沙盒方式运行会话，或
- 设置 `agents.defaults.sandbox.browser.allowHostControl: true` 并在调用工具时使用 `target="host"`。

### 设置

1. 加载扩展（开发/未打包）：

```bash
openclaw browser extension install
```

- Chrome → `chrome://extensions` → 启用“开发者模式”
- “加载未打包” → 选择 `openclaw browser extension path` 打印的目录
- 固定扩展，然后点击您要控制的标签上的图标（徽章显示 `ON`）。

2. 使用它：

- CLI: `openclaw browser --browser-profile chrome tabs`
- 代理工具: `browser` 使用 `profile="chrome"`

可选：如果您想要不同的名称或中继端口，请创建自己的配置文件：

```bash
openclaw browser create-profile \
  --name my-chrome \
  --driver extension \
  --cdp-url http://127.0.0.1:18792 \
  --color "#00AA00"
```

注意事项：

- 此模式依赖于大多数操作的 Playwright-on-CDP（屏幕截图/快照/操作）。
- 通过再次点击扩展图标来分离。

## 隔离保证

- **专用用户数据目录**：从不触及您的个人浏览器配置文件。
- **专用端口**：避免 `9222` 以防止与开发工作流发生冲突。
- **确定性标签页控制**：按 `targetId` 目标标签页，而不是“最后一个标签”。

## 浏览器选择

在本地启动时，OpenClaw 选择第一个可用的：

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

您可以使用 `browser.executablePath` 进行覆盖。

平台：

- macOS：检查 `/Applications` 和 `~/Applications`。
- Linux：查找 `google-chrome`, `brave`, `microsoft-edge`, `chromium` 等。
- Windows：检查常见的安装位置。

## 控制 API（可选）

仅适用于本地集成，网关暴露一个小的回环 HTTP API：

- 状态/启动/停止: `GET /`, `POST /start`, `POST /stop`
- 标签页: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- 快照/屏幕截图: `GET /snapshot`, `POST /screenshot`
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

### Playwright 要求

某些功能（导航/操作/AI 快照/角色快照、元素屏幕截图、PDF）需要 Playwright。如果未安装 Playwright，这些端点将返回明确的 501 错误。对于 openclaw-managed Chrome，ARIA 快照和基本屏幕截图仍然有效。对于 Chrome 扩展中继驱动程序，ARIA 快照和屏幕截图需要 Playwright。

如果看到 `Playwright is not available in this gateway build`，安装完整的 Playwright 包（不是 `playwright-core`），然后重启网关，或者重新安装带有浏览器支持的 OpenClaw。

#### Docker Playwright 安装

如果您的网关在 Docker 中运行，请避免 `npx playwright`（npm 覆盖冲突）。使用捆绑的 CLI：

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

为了持久化浏览器下载，请设置 `PLAYWRIGHT_BROWSERS_PATH`（例如，`/home/node/.cache/ms-playwright`），并确保 `/home/node` 通过 `OPENCLAW_HOME_VOLUME` 或绑定挂载进行持久化。参见 [Docker](/install/docker)。

## 工作原理（内部）

高层次流程：

- 一个小的 **控制服务器** 接受 HTTP 请求。
- 它通过 **CDP** 连接到基于 Chromium 的浏览器（Chrome/Brave/Edge/Chromium）。
- 对于高级操作（点击/输入/快照/PDF），它在 CDP 之上使用 **Playwright**。
- 当缺少 Playwright 时，仅提供非 Playwright 操作。

这种设计使代理保持在一个稳定、确定性的接口上，同时允许您交换本地/远程浏览器和配置文件。

## CLI 快速参考

所有命令接受 `--browser-profile <name>` 以针对特定配置文件。
所有命令也接受 `--json` 以获得机器可读的输出（稳定的负载）。

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

操作：

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
- `openclaw browser download e12 /tmp/report.pdf`
- `openclaw browser waitfordownload /tmp/report.pdf`
- `openclaw browser upload /tmp/file.pdf`
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
- `openclaw browser set headers --json '{"X-Debug":"1"}'`
- `openclaw browser set credentials user pass`
- `openclaw browser set credentials --clear`
- `openclaw browser set geo 37.7749 -122.4194 --origin "https://example.com"`
- `openclaw browser set geo --clear`
- `openclaw browser set media dark`
- `openclaw browser set timezone America/New_York`
- `openclaw browser set locale en-US`
- `openclaw browser set device "iPhone 14"`

注意事项：

- `upload` 和 `dialog` 是 **预设** 调用；在触发选择器/对话框的点击/按下之前运行它们。
- `upload` 还可以通过 `--input-ref` 或 `--element` 直接设置文件输入。
- `snapshot`:
  - `--format ai`（安装 Playwright 时默认）：返回带有数字引用的 AI 快照 (`aria-ref="<n>"`)。
  - `--format aria`：返回无障碍树（无引用；仅检查）。
  - `--efficient`（或 `--mode efficient`）：紧凑的角色快照预设（交互式 + 紧凑 + 深度 + 较小的最大字符数）。
  - 配置默认（工具/CLI 仅）：设置 `browser.snapshotDefaults.mode: "efficient"` 以在调用者未传递模式时使用高效的快照（参见 [网关配置](/gateway/configuration#browser-openclaw-managed-browser)）。
  - 角色快照选项 (`--interactive`, `--compact`, __CODE_BLOCK_19