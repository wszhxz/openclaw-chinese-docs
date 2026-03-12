---
summary: "Chrome extension: let OpenClaw drive your existing Chrome tab"
read_when:
  - You want the agent to drive an existing Chrome tab (toolbar button)
  - You need remote Gateway + local browser automation via Tailscale
  - You want to understand the security implications of browser takeover
title: "Chrome Extension"
---
# Chrome 扩展程序（浏览器中继）

OpenClaw Chrome 扩展程序允许代理控制您的**现有 Chrome 标签页**（您的普通 Chrome 窗口），而不是启动一个单独的 openclaw 管理的 Chrome 配置文件。

通过**单个 Chrome 工具栏按钮**进行附加/分离。

## 它是什么（概念）

有三个部分：

- **浏览器控制服务**（网关或节点）：代理/工具调用的 API（通过网关）
- **本地中继服务器**（回环 CDP）：在控制服务器和扩展程序之间架桥（默认为 `http://127.0.0.1:18792`）
- **Chrome MV3 扩展程序**：使用 `chrome.debugger` 附加到活动标签页，并将 CDP 消息传递给中继

然后，OpenClaw 通过正常的 `browser` 工具界面（选择正确的配置文件）来控制附加的标签页。

## 安装/加载（未打包）

1. 将扩展程序安装到稳定的本地路径：

```bash
openclaw browser extension install
```

2. 打印已安装扩展程序目录路径：

```bash
openclaw browser extension path
```

3. Chrome → `chrome://extensions`

- 启用“开发者模式”
- “加载未打包”→ 选择上面打印的目录

4. 固定扩展程序。

## 更新（无需构建步骤）

扩展程序作为静态文件包含在 OpenClaw 发行版（npm 包）中。没有单独的“构建”步骤。

升级 OpenClaw 后：

- 重新运行 `openclaw browser extension install` 以刷新 OpenClaw 状态目录下的已安装文件。
- Chrome → `chrome://extensions` → 单击扩展程序上的“重新加载”。

## 使用它（设置一次网关令牌）

OpenClaw 带有一个名为 `chrome` 的内置浏览器配置文件，该配置文件针对默认端口上的扩展程序中继。

首次附加之前，请打开扩展程序选项并设置：

- `Port`（默认 `18792`）
- `Gateway token`（必须与 `gateway.auth.token` / `OPENCLAW_GATEWAY_TOKEN` 匹配）

使用方法：

- CLI: `openclaw browser --browser-profile chrome tabs`
- 代理工具: `browser` 与 `profile="chrome"`

如果您想要不同的名称或不同的中继端口，请创建自己的配置文件：

```bash
openclaw browser create-profile \
  --name my-chrome \
  --driver extension \
  --cdp-url http://127.0.0.1:18792 \
  --color "#00AA00"
```

### 自定义网关端口

如果您使用自定义网关端口，则扩展程序中继端口会自动派生：

**扩展程序中继端口 = 网关端口 + 3**

示例：如果 `gateway.port: 19001`，则：

- 扩展程序中继端口: `19004`（网关 + 3）

在扩展程序选项页面中配置扩展程序以使用派生的中继端口。

## 附加/分离（工具栏按钮）

- 打开您希望 OpenClaw 控制的标签页。
- 单击扩展程序图标。
  - 当附加时，徽章显示 `ON`。
- 再次单击以分离。

## 它控制哪个标签页？

- 它**不会**自动控制“您正在查看的任何标签页”。
- 它仅控制**您通过单击工具栏按钮明确附加的标签页**。
- 要切换：打开其他标签页并在那里单击扩展程序图标。

## 徽章 + 常见错误

- `ON`：已附加；OpenClaw 可以驱动该标签页。
- `…`：正在连接到本地中继。
- `!`：无法到达/认证中继（最常见的原因是中继服务器未运行，或者缺少/错误的网关令牌）。

如果您看到 `!`：

- 确保网关在本地运行（默认设置），或者如果网关在其他地方运行，则在此计算机上运行一个节点主机。
- 打开扩展程序选项页面；它验证中继可达性 + 网关令牌认证。

## 远程网关（使用节点主机）

### 本地网关（与 Chrome 在同一台机器上）— 通常**不需要额外步骤**

如果网关与 Chrome 在同一台机器上运行，它会在回环上启动浏览器控制服务并自动启动中继服务器。扩展程序与本地中继通信；CLI/工具调用转到网关。

### 远程网关（网关在其他地方运行）— **运行一个节点主机**

如果您的网关在另一台机器上运行，请在运行 Chrome 的机器上启动一个节点主机。网关将浏览器操作代理到该节点；扩展程序 + 中继保持在浏览器机器本地。

如果有多个节点连接，请使用 `gateway.nodes.browser.node` 或设置 `gateway.nodes.browser.mode` 来固定一个。

## 沙箱（工具容器）

如果您的代理会话被沙箱化（`agents.defaults.sandbox.mode != "off"`），则可以限制 `browser` 工具：

- 默认情况下，沙箱会话通常针对**沙箱浏览器**（`target="sandbox"`），而不是您的主机 Chrome。
- Chrome 扩展程序中继接管需要控制**主机**浏览器控制服务。

选项：

- 最简单的方法：从**非沙箱**会话/代理使用扩展程序。
- 或者允许沙箱会话的主机浏览器控制：

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

然后确保工具不被工具策略拒绝，并且（如果需要）调用 `browser` 与 `target="host"`。

调试：`openclaw sandbox explain`

## 远程访问提示

- 保持网关和节点主机在同一尾网；避免将中继端口暴露给局域网或公共互联网。
- 故意配对节点；如果您不想远程控制，请禁用浏览器代理路由（`gateway.nodes.browser.mode="off"`）。

## “扩展程序路径”的工作原理

`openclaw browser extension path` 打印包含扩展程序文件的**已安装**磁盘目录。

CLI 故意**不**打印 `node_modules` 路径。始终先运行 `openclaw browser extension install` 以将扩展程序复制到 OpenClaw 状态目录下的稳定位置。

如果您移动或删除该安装目录，Chrome 会将扩展程序标记为损坏，直到您从有效路径重新加载它为止。

## 安全影响（请阅读）

这是强大且有风险的。将其视为授予模型“对您的浏览器的直接控制”。

- 扩展程序使用 Chrome 的调试器 API（`chrome.debugger`）。当附加时，模型可以：
  - 在该标签页中点击/输入/导航
  - 读取页面内容
  - 访问该标签页登录会话可以访问的所有内容
- **这不是隔离的**，就像专用的 openclaw 管理的配置文件一样。
  - 如果您附加到日常使用的配置文件/标签页，您就授予了对该帐户状态的访问权限。

建议：

- 优先使用专用的 Chrome 配置文件（与您的个人浏览分开）用于扩展程序中继使用。
- 保持网关和任何节点主机仅限于尾网；依赖网关认证 + 节点配对。
- 避免通过局域网（`0.0.0.0`）暴露中继端口，并避免使用 Funnel（公共）。
- 中继阻止非扩展程序来源，并要求对 `/cdp` 和 `/extension` 进行网关令牌认证。

相关：

- 浏览器工具概述：[Browser](/tools/browser)
- 安全审计：[Security](/gateway/security)
- Tailscale 设置：[Tailscale](/gateway/tailscale)