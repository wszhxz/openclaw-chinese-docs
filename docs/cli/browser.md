---
summary: "CLI reference for `openclaw browser` (profiles, tabs, actions, extension relay)"
read_when:
  - You use `openclaw browser` and want examples for common tasks
  - You want to control a browser running on another machine via a node host
  - You want to use the Chrome extension relay (attach/detach via toolbar button)
title: "browser"
---
# `openclaw browser`

管理 OpenClaw 的浏览器控制服务器，并执行浏览器操作（标签页、快照、截图、导航、点击、输入）。

相关文档：

- 浏览器工具 + API：[浏览器工具](/tools/browser)  
- Chrome 扩展中继：[Chrome 扩展](/tools/chrome-extension)

## 常用标志

- `--url <gatewayWsUrl>`: 网关 WebSocket 地址（默认使用配置中的值）。  
- `--token <token>`: 网关令牌（如需认证）。  
- `--timeout <ms>`: 请求超时时间（毫秒）。  
- `--browser-profile <name>`: 选择浏览器配置文件（默认使用配置中的值）。  
- `--json`: 机器可读输出（在支持的命令中启用）。

## 快速开始（本地）

```bash
openclaw browser --browser-profile chrome tabs
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

## 配置文件

配置文件是命名的浏览器路由配置。实际使用中：

- `openclaw`: 启动或连接到一个专用的、由 OpenClaw 管理的 Chrome 实例（使用隔离的用户数据目录）。  
- `chrome`: 通过 Chrome 扩展中继，控制您已有的 Chrome 标签页。

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

导航 / 点击 / 输入（基于引用的 UI 自动化）：

```bash
openclaw browser navigate https://example.com
openclaw browser click <ref>
openclaw browser type <ref> "hello"
```

## Chrome 扩展中继（通过工具栏按钮连接）

此模式允许智能体控制您手动连接的现有 Chrome 标签页（**不会自动连接**）。

将未打包的扩展安装至一个稳定路径：

```bash
openclaw browser extension install
openclaw browser extension path
```

然后打开 Chrome → `chrome://extensions` → 启用“开发者模式” → “加载已解压的扩展程序” → 选择上述打印出的文件夹。

完整指南：[Chrome 扩展](/tools/chrome-extension)

## 远程浏览器控制（节点主机代理）

如果网关运行在与浏览器不同的机器上，请在安装了 Chrome / Brave / Edge / Chromium 的机器上运行一个 **node host**。网关将把浏览器操作代理至该节点（无需单独部署浏览器控制服务器）。

使用 `gateway.nodes.browser.mode` 控制自动路由行为，使用 `gateway.nodes.browser.node` 在多个节点连接时固定指定某一节点。

安全性与远程配置说明：[浏览器工具](/tools/browser)、[远程访问](/gateway/remote)、[Tailscale](/gateway/tailscale)、[安全性](/gateway/security)