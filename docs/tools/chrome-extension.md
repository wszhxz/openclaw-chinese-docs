---
summary: "Chrome extension: let OpenClaw drive your existing Chrome tab"
read_when:
  - You want the agent to drive an existing Chrome tab (toolbar button)
  - You need remote Gateway + local browser automation via Tailscale
  - You want to understand the security implications of browser takeover
title: "Chrome Extension"
---
# Chrome 扩展（浏览器中继）

OpenClaw Chrome 扩展允许代理控制您的 **现有 Chrome 标签页**（您的正常 Chrome 窗口），而不是启动一个单独的由 openclaw 管理的 Chrome 配置文件。

附加/分离通过 **单个 Chrome 工具栏按钮** 进行。

## 它是什么（概念）

有三个部分：

- **浏览器控制服务**（网关或节点）：代理/工具调用的 API（通过网关）
- **本地中继服务器**（回环 CDP）：在控制服务器和扩展之间架起桥梁（默认为 `http://127.0.0.1:18792`）
- **Chrome MV3 扩展**：使用 `chrome.debugger` 附加到活动标签页，并将 CDP 消息管道传输到中继

然后 OpenClaw 通过正常的 `browser` 工具界面（选择正确的配置文件）控制附加的标签页。

## 安装 / 加载（未打包）

1. 将扩展安装到稳定的本地路径：

```bash
openclaw browser extension install
```

2. 打印已安装扩展目录路径：

```bash
openclaw browser extension path
```

3. Chrome → `chrome://extensions`

- 启用“开发者模式”
- “加载已解压的扩展程序” → 选择上面打印的目录

4. 固定扩展程序。

## 更新（无需构建步骤）

扩展作为静态文件包含在 OpenClaw 发布版（npm 包）中。没有单独的“构建”步骤。

升级 OpenClaw 后：

- 重新运行 `openclaw browser extension install` 以刷新 OpenClaw 状态目录下的已安装文件。
- Chrome → `chrome://extensions` → 点击扩展程序上的“重新加载”。

## 使用它（无需额外配置）

OpenClaw 内置了一个名为 `chrome` 的浏览器配置文件，针对默认端口上的扩展中继。

使用方法：

- 命令行：`openclaw browser --browser-profile chrome tabs`
- 代理工具：`browser` 使用 `profile="chrome"`

如果您想要不同的名称或不同的中继端口，请创建自己的配置文件：

```bash
openclaw browser create-profile \
  --name my-chrome \
  --driver extension \
  --cdp-url http://127.0.0.1:18792 \
  --color "#00AA00"
```

## 附加 / 分离（工具栏按钮）

- 打开您希望 OpenClaw 控制的标签页。
- 点击扩展图标。
  - 徽章显示 `ON` 表示已附加。
- 再次点击以分离。

## 它控制哪个标签页？

- 它 **不会** 自动控制“您正在查看的任何标签页”。
- 它仅控制 **您通过点击工具栏按钮显式附加的标签页**。
- 要切换：打开其他标签页并点击该处的扩展图标。

## 徽章 + 常见错误

- `ON`：已附加；OpenClaw 可以驱动该标签页。
- `…`：正在连接到本地中继。
- `!`：中继不可达（最常见：浏览器中继服务器未在此机器上运行）。

如果看到 `!`：

- 确保网关在本地运行（默认设置），或者如果网关运行在其他地方，则在此机器上运行一个节点主机。
- 打开扩展选项页面；它会显示中继是否可达。

## 远程网关（使用节点主机）

### 本地网关（与 Chrome 在同一台机器上）—— 通常 **无需额外步骤**

如果网关与 Chrome 在同一台机器上运行，它会在回环上启动浏览器控制服务，并自动启动中继服务器。扩展与本地中继通信；CLI/工具调用发送到网关。

### 远程网关（网关运行在其他地方）—— **运行一个节点主机**

如果您的网关运行在另一台机器上，在运行 Chrome 的机器上启动一个节点主机。
网关将代理浏览器操作到该节点；扩展 + 中继保持在浏览器机器的本地。

如果有多个节点连接，请使用 `gateway.nodes.browser.node` 固定一个或设置 `gateway.nodes.browser.mode`。

## 沙箱（工具容器）

如果您的代理会话被沙盒化 (`agents.defaults.sandbox.mode != "off"`)，`browser` 工具可能会受到限制：

- 默认情况下，沙盒化会话通常针对 **沙盒浏览器** (`target="sandbox"`)，而不是您的主机 Chrome。
- Chrome 扩展中继接管需要控制 **主机** 浏览器控制服务器。

选项：

- 最简单：从 **非沙盒化** 会话/代理使用扩展。
- 或者允许沙盒化会话中的主机浏览器控制：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        browser: {
          allowHostControl: true,
        },
      },
    },
  },
}
```

然后确保工具不受工具策略拒绝，并且（如果需要）使用 `target="host"` 调用 `browser`。

调试：`openclaw sandbox explain`

## 远程访问提示

- 将网关和节点主机保持在同一尾网中；避免将中继端口暴露给局域网或公共互联网。
- 故意配对节点；如果不需要远程控制，请禁用浏览器代理路由 (`gateway.nodes.browser.mode="off"`)。

## “扩展路径”如何工作

`openclaw browser extension path` 打印包含扩展文件的 **已安装** 磁盘目录。

CLI 故意 **不** 打印 `node_modules` 路径。始终先运行 `openclaw browser extension install` 将扩展复制到 OpenClaw 状态目录下的稳定位置。

如果您移动或删除该安装目录，Chrome 会将扩展标记为损坏，直到您从有效路径重新加载它。

## 安全影响（请阅读）

这非常强大且具有风险。将其视为赋予模型“对您的浏览器的操作权”。

- 扩展使用 Chrome 的调试器 API (`chrome.debugger`)。附加时，模型可以：
  - 在该标签页中点击/输入/导航
  - 读取页面内容
  - 访问该标签页登录会话可以访问的任何内容
- **这不是隔离的** 像专用的 openclaw 管理的配置文件。
  - 如果您附加到日常使用的配置文件/标签页，您是在授予对该账户状态的访问权限。

建议：

- 优先使用专用的 Chrome 配置文件（与个人浏览分开）用于扩展中继使用。
- 将网关和任何节点主机保持在尾网中；依赖网关认证 + 节点配对。
- 避免通过局域网 (`0.0.0.0`) 暴露中继端口，并避免使用 Funnel（公开）。
- 中继阻止非扩展来源，并要求 CDP 客户端的内部认证令牌。

相关：

- 浏览器工具概述：[Browser](/tools/browser)
- 安全审计：[Security](/gateway/security)
- Tailscale 设置：[Tailscale](/gateway/tailscale)