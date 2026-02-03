---
summary: "Chrome extension: let OpenClaw drive your existing Chrome tab"
read_when:
  - You want the agent to drive an existing Chrome tab (toolbar button)
  - You need remote Gateway + local browser automation via Tailscale
  - You want to understand the security implications of browser takeover
title: "Chrome Extension"
---
# Chrome扩展（浏览器中继）

OpenClaw Chrome扩展允许代理控制您的**现有Chrome标签页**（您的正常Chrome窗口），而不是启动一个独立的openclaw管理的Chrome配置文件。

附加/分离通过一个**Chrome工具栏按钮**完成。

## 它是什么（概念）

有三个部分：

- **浏览器控制服务**（网关或节点）：代理/工具调用的API（通过网关）
- **本地中继服务器**（环回CDP）：在控制服务器和扩展之间建立桥梁（默认为`http://127.0.0.1:18792`）
- **Chrome MV3扩展**：通过`chrome.debugger`附加到活动标签页，并将CDP消息传递给中继

OpenClaw随后通过正常的`browser`工具界面控制已附加的标签页（选择正确的配置文件）。

## 安装/加载（未打包）

1. 安装扩展到一个稳定的本地路径：

```bash
openclaw browser extension install
```

2. 打印已安装的扩展目录路径：

```bash
openclaw browser extension path
```

3. Chrome → `chrome://extensions`

- 启用“开发者模式”
- “加载未打包” → 选择上述打印的目录

4. 固定扩展。

## 更新（无需构建步骤）

扩展作为静态文件包含在OpenClaw发布版（npm包）中。没有单独的“构建”步骤。

升级OpenClaw后：

- 重新运行`openclaw browser extension install`以刷新您的OpenClaw状态目录下的安装文件。
- Chrome → `chrome://extensions` → 点击扩展的“重新加载”。

## 使用它（无需额外配置）

OpenClaw附带一个名为`chrome`的内置浏览器配置文件，目标是扩展中继的默认端口。

使用它：

- CLI：`openclaw browser --browser-profile chrome tabs`
- 代理工具：`browser`带有`profile="chrome"`

如果您想要不同的名称或不同的中继端口，请创建自己的配置文件：

```bash
openclaw browser create-profile \
  --name my-chrome \
  --driver extension \
  --cdp-url http://127.0.0.1:18792 \
  --color "#00AA00"
```

## 附加/分离（工具栏按钮）

- 打开您希望OpenClaw控制的标签页。
- 点击扩展图标。
  - 附加时徽章显示`ON`。
- 再次点击以分离。

## 它控制哪个标签页？

- 它**不会**自动控制“您正在查看的任意标签页”。
- 它仅控制**您通过点击工具栏按钮显式附加的标签页**。
- 要切换：打开另一个标签页并点击该位置的扩展图标。

## 徽章 + 常见错误

- `ON`：已附加；OpenClaw可以控制该标签页。
- `…`：正在连接本地中继。
- `!`：中继不可达（最常见的：浏览器中继服务器在此机器上未运行）。

如果您看到`!`：

- 确保网关在本地运行（默认设置），或如果网关在其他机器上运行，请在此机器上运行一个节点主机。
- 打开扩展选项页面；它会显示中继是否可达。

## 远程网关（使用节点主机）

### 本地网关（与Chrome在同一台机器）——通常**无需额外步骤**

如果网关在与Chrome相同的机器上运行，它会在环回接口上启动浏览器控制服务，并自动启动中继服务器。扩展与本地中继通信；CLI/工具调用发送到网关。

### 远程网关（网关在其他位置运行）——**运行一个节点主机**

如果您的网关在另一台机器上运行，请在运行Chrome的机器上启动一个节点主机。网关将通过该节点代理浏览器操作；扩展 + 中继保持在浏览器机器本地。

如果多个节点连接，请使用`gateway.nodes.browser.node`固定一个，或设置`gateway.nodes.browser.mode`。

## 沙箱（工具容器）

如果您的代理会话被沙箱化（`agents.defaults.sandbox.mode != "off"`），`browser`工具可能会受到限制：

- 默认情况下，沙箱化会话通常针对**沙箱浏览器**（`target="sandbox"`），而不是您的主机Chrome。
- Chrome扩展中继接管需要控制**主机**浏览器控制服务器。

选项：

- 最简单：在非沙箱化会话/代理中使用扩展。
- 或允许沙箱化会话的主机浏览器控制：

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

然后确保工具未被工具策略拒绝，并（如果需要）调用`browser`时使用`target="host"`。

调试：`openclaw sandbox explain`

## 远程访问提示

- 保持网关和节点主机在同一tailnet；避免将中继端口暴露给局域网或公共互联网。
- 故意配对节点；如果您不希望远程控制，请禁用浏览器代理路由（`gateway.nodes.browser.mode="off"`）。

## “扩展路径”如何工作

`openclaw browser extension path`打印的**已安装**磁盘目录，其中包含扩展文件。

CLI有意**不打印**`node_modules`路径。始终首先运行`openclaw browser extension install`将扩展复制到您的OpenClaw状态目录下的稳定位置。

如果您移动或删除该安装目录，Chrome会在您从有效路径重新加载它之前将扩展标记为损坏。

## 安全影响（请阅读此内容）

这功能强大且有风险。将其视为赋予模型“对浏览器的直接控制”。

- 扩展使用Chrome的调试器API（`chrome.debugger`）。附加后，模型可以：
  - 在该标签页中点击/输入/导航
  - 读取页面内容
  - 访问该标签页登录会话所能访问的内容
- **这不是隔离的**，不像专用的openclaw管理的配置文件。
  - 如果您附加到日常使用的配置文件/标签页，您将授予该账户状态的访问权限。

建议：

- 更倾向于为扩展中继使用专用的Chrome配置文件（与您的个人浏览分离）。
- 保持网关和任何节点主机仅限tailnet；依赖网关认证 + 节点配对。
- 避免将中继端口暴露在局域网（`0.0.0.