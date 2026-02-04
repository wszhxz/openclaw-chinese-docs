---
summary: "CLI reference for `openclaw browser` (profiles, tabs, actions, extension relay)"
read_when:
  - You use `openclaw browser` and want examples for common tasks
  - You want to control a browser running on another machine via a node host
  - You want to use the Chrome extension relay (attach/detach via toolbar button)
title: "browser"
---
# `openclaw browser`

管理 OpenClaw 的浏览器控制服务器并运行浏览器操作（标签页、快照、截图、导航、点击、输入）。

相关：

- 浏览器工具 + API: [Browser tool](/tools/browser)
- Chrome 扩展中继: [Chrome extension](/tools/chrome-extension)

## 常用标志

- `--url <gatewayWsUrl>`: 网关 WebSocket URL（默认为配置）。
- `--token <token>`: 网关令牌（如果需要）。
- `--timeout <ms>`: 请求超时时间（毫秒）。
- `--browser-profile <name>`: 选择浏览器配置文件（默认从配置）。
- `--json`: 机器可读输出（在支持的情况下）。

## 快速开始（本地）

```bash
openclaw browser --browser-profile chrome tabs
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

## 配置文件

配置文件是命名的浏览器路由配置。实际上：

- `openclaw`: 启动/附加到一个专用的 OpenClaw 管理的 Chrome 实例（隔离的用户数据目录）。
- `chrome`: 通过 Chrome 扩展中继控制您的现有 Chrome 标签页。

```bash
openclaw browser profiles
openclaw browser create-profile --name work --color "#FF5A36"
openclaw browser delete-profile --name work
```

使用特定配置文件：

```bash
openclaw browser --browser-profile work tabs
```

## 标签页

```bash
openclaw browser tabs
openclaw browser open https://docs.openclaw.ai
openclaw browser focus <targetId>
openclaw browser close <targetId>
```

## 快照 / 截图 / 操作

快照：

```bash
openclaw browser snapshot
```

截图：

```bash
openclaw browser screenshot
```

导航/点击/输入（基于引用的 UI 自动化）：

```bash
openclaw browser navigate https://example.com
openclaw browser click <ref>
openclaw browser type <ref> "hello"
```

## Chrome 扩展中继（通过工具栏按钮附加）

此模式允许代理手动附加到您现有的 Chrome 标签页（不会自动附加）。

将未打包的扩展安装到稳定路径：

```bash
openclaw browser extension install
openclaw browser extension path
```

然后 Chrome → `chrome://extensions` → 启用“开发者模式” → “加载已解压” → 选择打印的文件夹。

完整指南：[Chrome 扩展](/tools/chrome-extension)

## 远程浏览器控制（节点主机代理）

如果网关运行在与浏览器不同的机器上，请在具有 Chrome/Brave/Edge/Chromium 的机器上运行一个 **节点主机**。网关将代理浏览器操作到该节点（不需要单独的浏览器控制服务器）。

使用 `gateway.nodes.browser.mode` 控制自动路由，并使用 `gateway.nodes.browser.node` 固定特定节点（如果有多个节点连接）。

安全 + 远程设置：[Browser tool](/tools/browser), [Remote access](/gateway/remote), [Tailscale](/gateway/tailscale), [Security](/gateway/security)