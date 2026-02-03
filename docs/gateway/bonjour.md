---
summary: "Bonjour/mDNS discovery + debugging (Gateway beacons, clients, and common failure modes)"
read_when:
  - Debugging Bonjour discovery issues on macOS/iOS
  - Changing mDNS service types, TXT records, or discovery UX
title: "Bonjour Discovery"
---
--<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context and the key terms. The document is about OpenClaw's use of Bonjour and mDNS for discovering a gateway in a LAN, and then extending that to wide-area networks using Tailscale. There are sections on configuration, DNS setup, security, debugging, and related documentation.

First, I'll note the technical terms that need accurate translation. Terms like "Bonjour," "mDNS," "DNS-SD," "Tailnet," "split DNS," "CoreDNS," "TXT records," and specific commands like "dns-sd" and "dig" should be kept as they are, or translated if there's a standard Chinese equivalent. For example, "mDNS" is commonly known as "多播DNS" in Chinese tech contexts.

I need to ensure that the structure of the document is preserved, including headings, bullet points, code blocks, and any specific formatting like JSON5 code. The user mentioned that only the translated text should be returned, so I must avoid any additional explanations or markdown.

Let me start translating section by section. The first part is the title and introduction. "Bonjour / mDNS discovery" becomes "Bonjour / mDNS 发现". The main text explains that OpenClaw uses Bonjour as a LAN-only convenience. I'll make sure to convey that it's a convenience feature for LAN use only, and that it doesn't replace SSH or Tailnet-based connectivity.

Moving to the section about Wide-area Bonjour over Tailscale. Terms like "unicast DNS-SD" should be translated as "单播 DNS-SD". The high-level steps need to be accurately translated, ensuring that technical steps are clear. For example, "Run a DNS server on the gateway host" becomes "在网关主机上运行 DNS 服务器".

The Gateway config section has a JSON5 block. I need to ensure that the syntax is preserved, and the keys are correctly translated. For instance, "bind: "tailnet"" becomes "绑定: "tailnet"".

The One-time DNS server setup section has a bash command. I'll keep the command as is but translate the surrounding text. For example, "openclaw dns setup --apply" remains the same, but the explanation around it should be in Chinese.

In the Tailscale DNS settings section, terms like "split DNS" should be "拆分 DNS" or "分拆 DNS". The user instructions need to be clear, so I'll make sure the steps are accurately translated.

The Gateway listener security section mentions binding to loopback and enabling auth. I'll translate these terms appropriately, ensuring that the security recommendations are clear.

The "What advertises" section is straightforward, translating the service type names. The TXT keys section lists various keys; I'll translate the key names while keeping the values as they are, since they are specific identifiers.

Debugging sections have commands and explanations. I'll translate the commands and the context around them, ensuring that the troubleshooting steps are clear. For example, "dns-sd -B _openclaw-gw._tcp local." becomes "dns-sd -B _openclaw-gw._tcp local." with the explanation in Chinese.

Common failure modes list issues like network restrictions and mDNS blocking. I'll translate these issues accurately, making sure the technical terms are correctly rendered.

Escaped instance names section explains how Bonjour escapes characters. I'll translate the explanation, ensuring that the technical details about encoding are clear.

Disabling/configuration section lists environment variables and configuration options. I'll translate the variable names and their descriptions, keeping the legacy notes as specified.

Finally, the related docs section has links to other documents. I'll translate the titles of those documents while keeping the URLs intact.

Throughout the translation, I'll maintain the structure, using appropriate Chinese punctuation and formatting. I'll double-check technical terms to ensure consistency and accuracy, especially for terms that might have standard translations in Chinese tech documentation. Also, I'll ensure that code blocks and commands are preserved without any changes, as they are critical for the user's understanding and implementation.
</think>

# 你好 / mDNS 发现

OpenClaw 使用 Bonjour（mDNS / DNS-SD）作为 **仅限局域网的便捷方式** 来发现活动的网关（WebSocket 端点）。这是一种尽力而为的方式，**不会** 替代 SSH 或基于 Tailnet 的连接。

## 跨网络的 Bonjour（单播 DNS-SD）通过 Tailscale

如果节点和网关位于不同的网络中，多播 mDNS 将无法跨网络边界。您可以通过切换到 **单播 DNS-SD**（“广域 Bonjour”）通过 Tailscale 保持相同的发现用户体验。

高级步骤：

1. 在网关主机上运行一个 DNS 服务器（可通过 Tailnet 访问）。
2. 在专用区域下发布 `_openclaw-gw._tcp` 的 DNS-SD 记录（示例：`openclaw.internal.`）。
3. 配置 Tailscale 的 **拆分 DNS**，使您选择的域通过该 DNS 服务器解析（包括 iOS 客户端）。

OpenClaw 支持任何发现域；`openclaw.internal.` 只是一个示例。iOS/Android 节点会浏览 `local.` 和您配置的广域域。

### 网关配置（推荐）

```json5
{
  gateway: { bind: "tailnet" }, // 仅 Tailnet（推荐）
  discovery: { wideArea: { enabled: true } }, // 启用广域 DNS-SD 发布
}
```

### 一次性 DNS 服务器设置（网关主机）

```bash
openclaw dns setup --apply
```

这会安装 CoreDNS 并配置它：

- 仅在网关的 Tailscale 接口上监听端口 53
- 从 `~/.openclaw/dns/<domain>.db` 提供您选择的域（示例：`openclaw.internal.`）

从连接到 Tailnet 的机器验证：

```bash
dns-sd -B _openclaw-gw._tcp openclaw.internal.
dig @<TAILNET_IPV4> -p 53 _openclaw-gw._tcp.openclaw.internal PTR +short
```

### Tailscale DNS 设置

在 Tailscale 管理控制台中：

- 添加一个指向网关 Tailnet IP 的名称服务器（UDP/TCP 53）。
- 添加拆分 DNS，使您的发现域使用该名称服务器。

一旦客户端接受 Tailnet DNS，iOS 节点可以在您的发现域中无需多播浏览 `_openclaw-gw._tcp`。

### 网关监听器安全（推荐）

网关的 WebSocket 端口（默认 `18789`）默认绑定到环回接口。对于 LAN/Tailnet 访问，显式绑定并保持身份验证启用。

对于仅 Tailnet 的设置：

- 在 `~/.openclaw/openclaw.json` 中设置 `gateway.bind: "tailnet"`。
- 重启网关（或重启 macOS 任务栏应用）。

## 仅网关广播

只有网关广播 `_openclaw-gw._tcp`。

## 服务类型

- `_openclaw-gw._tcp` — 网关传输信标（用于 macOS/iOS/Android 节点）。

## TXT 键（非秘密提示）

网关广播小型非秘密提示以简化 UI 流程：

- `role=gateway`
- `displayName=<友好名称>`
- `lanHost=<主机名>.local`
- `gatewayPort=<端口>`（网关 WebSocket + HTTP）
- `gatewayTls=1`（仅在 TLS 启用时）
- `gatewayTlsSha256=<sha256>`（仅在 TLS 启用且指纹可用时）
- `canvasPort=<端口>`（仅在画布主机启用时；默认 `18793`）
- `sshPort=<端口>`（未覆盖时默认为 22）
- `transport=gateway`
- `cliPath=<路径>`（可选；可运行的 `openclaw` 入口点的绝对路径）
- `tailnetDns=<magicdns>`（当 Tailnet 可用时的可选提示）

## macOS 调试

有用的内置工具：

- 浏览实例：
  ```bash
  dns-sd -B _openclaw-gw._tcp local.
  ```
- 解析一个实例（替换 `<instance>`）：
  ```bash
  dns-sd -L "<instance>" _openclaw-gw._tcp local.
  ```

如果浏览正常但解析失败，通常您遇到了 LAN 策略或 mDNS 解析器问题。

## 网关日志调试

网关写入一个滚动日志文件（启动时打印为 `gateway log file: ...`）。查找 `bonjour:` 行，特别是：

- `bonjour: 广告失败 ...`
- `bonjour: ... 名称冲突已解决` / `主机名冲突已解决`
- `bonjour: 看门狗检测到未宣布的服务 . ..`

## iOS 节点调试

iOS 节点使用 `NWBrowser` 来发现 `_openclaw-gw._tcp`。

捕获日志：

- 设置 → 网关 → 高级 → **发现调试日志**
- 设置 → 网关 → 高级