---
summary: "CLI reference for `openclaw browser` (lifecycle, profiles, tabs, actions, state, and debugging)"
read_when:
  - You use `openclaw browser` and want examples for common tasks
  - You want to control a browser running on another machine via a node host
  - You want to attach to your local signed-in Chrome via Chrome MCP
title: "browser"
---
# `openclaw browser`

管理 OpenClaw 的浏览器控制面并运行浏览器操作（生命周期、配置文件、标签页、快照、屏幕截图、导航、输入、状态模拟和调试）。

相关：

- 浏览器工具 + API: [浏览器工具](/tools/browser)

## 通用标志

- ``--url <gatewayWsUrl>``: Gateway WebSocket URL（默认为 config）。
- ``--token <token>``: Gateway Token（如果需要）。
- ``--timeout <ms>``: 请求超时（ms）。
- ``--expect-final``: 等待最终的 Gateway 响应。
- ``--browser-profile <name>``: 选择浏览器配置文件（默认来自 config）。
- ``--json``: 机器可读输出（如支持）。

## 快速开始（本地）

````bash
openclaw browser profiles
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
````

## 生命周期

````bash
openclaw browser status
openclaw browser start
openclaw browser stop
openclaw browser --browser-profile openclaw reset-profile
````

注意：

- 对于 ``attachOnly`` 和远程 CDP 配置文件，``openclaw browser stop`` 会关闭活动的控制会话并清除临时模拟覆盖，即使 OpenClaw 本身未启动浏览器进程。
- 对于本地托管配置文件，``openclaw browser stop`` 会停止生成的浏览器进程。

## 如果命令缺失

如果 ``openclaw browser`` 是未知命令，请检查 ``~/.openclaw/openclaw.json`` 中的 ``plugins.allow``。

当存在 ``plugins.allow`` 时，必须显式列出捆绑的浏览器插件：

````json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
````

``browser.enabled=true`` 在插件白名单排除 ``browser`` 时不会恢复 CLI 子命令。

相关：[浏览器工具](/tools/browser#missing-browser-command-or-tool)

## 配置文件

配置文件是命名的浏览器路由配置。实际上：

- ``openclaw``: 启动或附加到专用的 OpenClaw 托管 Chrome 实例（隔离的用户数据目录）。
- ``user``: 通过 Chrome DevTools MCP 控制您现有的已登录 Chrome 会话。
- 自定义 CDP 配置文件：指向本地或远程 CDP 端点。

````bash
openclaw browser profiles
openclaw browser create-profile --name work --color "#FF5A36"
openclaw browser create-profile --name chrome-live --driver existing-session
openclaw browser create-profile --name remote --cdp-url https://browser-host.example.com
openclaw browser delete-profile --name work
````

使用特定配置文件：

````bash
openclaw browser --browser-profile work tabs
````

## 标签页

````bash
openclaw browser tabs
openclaw browser tab new
openclaw browser tab select 2
openclaw browser tab close 2
openclaw browser open https://docs.openclaw.ai
openclaw browser focus <targetId>
openclaw browser close <targetId>
````

## 快照 / 屏幕截图 / 操作

快照：

````bash
openclaw browser snapshot
````

屏幕截图：

````bash
openclaw browser screenshot
openclaw browser screenshot --full-page
openclaw browser screenshot --ref e12
````

注意：

- ``--full-page`` 仅用于页面捕获；不能与 ``--ref`` 或 ``--element`` 结合使用。
- ``existing-session`` / ``user`` 配置文件支持页面屏幕截图和来自快照输出的 ``--ref`` 屏幕截图，但不支持 CSS ``--element`` 屏幕截图。

导航/点击/输入（基于引用的 UI 自动化）：

````bash
openclaw browser navigate https://example.com
openclaw browser click <ref>
openclaw browser type <ref> "hello"
openclaw browser press Enter
openclaw browser hover <ref>
openclaw browser scrollintoview <ref>
openclaw browser drag <startRef> <endRef>
openclaw browser select <ref> OptionA OptionB
openclaw browser fill --fields '[{"ref":"1","value":"Ada"}]'
openclaw browser wait --text "Done"
openclaw browser evaluate --fn '(el) => el.textContent' --ref <ref>
````

文件 + 对话框助手：

````bash
openclaw browser upload /tmp/openclaw/uploads/file.pdf --ref <ref>
openclaw browser waitfordownload
openclaw browser download <ref> report.pdf
openclaw browser dialog --accept
````

## 状态和存储

视口 + 模拟：

````bash
openclaw browser resize 1280 720
openclaw browser set viewport 1280 720
openclaw browser set offline on
openclaw browser set media dark
openclaw browser set timezone Europe/London
openclaw browser set locale en-GB
openclaw browser set geo 51.5074 -0.1278 --accuracy 25
openclaw browser set device "iPhone 14"
openclaw browser set headers '{"x-test":"1"}'
openclaw browser set credentials myuser mypass
````

Cookie + 存储：

````bash
openclaw browser cookies
openclaw browser cookies set session abc123 --url https://example.com
openclaw browser cookies clear
openclaw browser storage local get
openclaw browser storage local set token abc123
openclaw browser storage session clear
````

## 调试

````bash
openclaw browser console --level error
openclaw browser pdf
openclaw browser responsebody "**/api"
openclaw browser highlight <ref>
openclaw browser errors --clear
openclaw browser requests --filter api
openclaw browser trace start
openclaw browser trace stop --out trace.zip
````

## 通过 MCP 使用现有 Chrome

使用内置的 ``user`` 配置文件，或创建您自己的 ``existing-session`` 配置文件：

````bash
openclaw browser --browser-profile user tabs
openclaw browser create-profile --name chrome-live --driver existing-session
openclaw browser create-profile --name brave-live --driver existing-session --user-data-dir "~/Library/Application Support/BraveSoftware/Brave-Browser"
openclaw browser --browser-profile chrome-live tabs
````

此路径仅限主机。对于 Docker、无头服务器、Browserless 或其他远程设置，请使用 CDP 配置文件。

当前现有会话限制：

- 基于快照的操作使用 refs，而非 CSS 选择器
- ``click`` 仅限左键单击
- ``type`` 不支持 ``slowly=true``
- ``press`` 不支持 ``delayMs``
- ``hover``、``scrollintoview``、``drag``、``select``、``fill`` 和 ``evaluate`` 拒绝按调用超时覆盖
- ``select`` 仅支持一个值
- ``wait --load networkidle`` 不受支持
- 文件上传需要 ``--ref`` / ``--input-ref``，不支持 CSS ``--element``，且目前仅支持一次一个文件
- 对话框钩子不支持 ``--timeout``
- 屏幕截图支持页面捕获和 ``--ref``，但不支持 CSS ``--element``
- ``responsebody``、下载拦截、PDF 导出和批量操作仍然需要托管浏览器或原始 CDP 配置文件

## 远程浏览器控制（Node Host 代理）

如果 Gateway 在与浏览器不同的机器上运行，请在拥有 Chrome/Brave/Edge/Chromium 的机器上运行 **Node Host**。Gateway 将把浏览器操作代理到该节点（无需单独的浏览器控制服务器）。

使用 ``gateway.nodes.browser.mode`` 控制自动路由，如果连接了多个节点，则使用 ``gateway.nodes.browser.node`` 固定特定节点。

安全 + 远程设置：[浏览器工具](/tools/browser)、[远程访问](/gateway/remote)、[Tailscale](/gateway/tailscale)、[安全](/gateway/security)