---
summary: "Run OpenClaw in a sandboxed macOS VM (local or hosted) when you need isolation or iMessage"
read_when:
  - You want OpenClaw isolated from your main macOS environment
  - You want iMessage integration (BlueBubbles) in a sandbox
  - You want a resettable macOS environment you can clone
  - You want to compare local vs hosted macOS VM options
title: "macOS VMs"
---
# 在 macOS 虚拟机上运行 OpenClaw（沙箱化）

## 推荐默认设置（大多数用户）

- **小型 Linux VPS** 用于全天候网关和低成本。参见 [VPS 托管](/vps)。
- **专用硬件**（Mac mini 或 Linux 机器）如果您需要完全控制和 **住宅 IP** 进行浏览器自动化。许多网站会阻止数据中心 IP，因此本地浏览通常效果更好。
- **混合模式**：将网关保留在便宜的 VPS 上，并在需要浏览器/UI 自动化时将您的 Mac 连接为 **节点**。参见 [节点](/nodes) 和 [远程网关](/gateway/remote)。

当您特别需要 macOS 专属功能（如 iMessage/BlueBubbles）或希望严格隔离您的日常 Mac 时，请使用 macOS 虚拟机。

## macOS 虚拟机选项

### 您的 Apple Silicon Mac 上的本地虚拟机（Lume）

使用 [Lume](https://cua.ai/docs/lume) 在您的现有 Apple Silicon Mac 上运行沙箱化的 macOS 虚拟机。

这将为您提供：

- 隔离的完整 macOS 环境（主机保持干净）
- 通过 BlueBubbles 支持 iMessage（在 Linux/Windows 上无法实现）
- 通过克隆虚拟机实现即时重置
- 无需额外硬件或云成本

### 云中的托管 Mac 提供商

如果您希望在云中使用 macOS，托管 Mac 提供商同样适用：

- [MacStadium](https://www.macstadium.com/)（托管 Mac 机器）
- 其他托管 Mac 供应商也适用；请遵循其 VM + SSH 文档

一旦您拥有对 macOS 虚拟机的 SSH 访问权限，请继续下方第 6 步。

---

## 快速路径（Lume，经验用户）

1. 安装 Lume
2. `lume create openclaw --os macos --ipsw latest`
3. 完成设置助手，启用远程登录（SSH）
4. `lume run openclaw --no-display`
5. SSH 登录，安装 OpenClaw，配置通道
6. 完成

---

## 所需条件（Lume）

- Apple Silicon Mac（M1/M2/M3/M4）
- 主机上的 macOS Sequoia 或更高版本
- 每个虚拟机约 60 GB 空闲磁盘空间
- 约 20 分钟

---

## 1) 安装 Lume

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/trycua/cua/main/libs/lume/scripts/install.sh)"
```

如果 `~/.local/bin` 不在您的 PATH 中：

```bash
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.zshrc && source ~/.zshrc
```

验证：

```bash
lume --version
```

文档：[Lume 安装](https://cua.ai/docs/lume/guide/getting-started/installation)

---

## 2) 创建 macOS 虚拟机

```bash
lume create openclaw --os macos --ipsw latest
```

这将下载 macOS 并创建虚拟机。一个 VNC 窗口会自动打开。

注意：下载时间取决于您的网络连接。

---

## 3) 完成设置助手

在 VNC 窗口中：

1. 选择语言和区域
2. 跳过 Apple ID（或登录以稍后使用 iMessage）
3. 创建用户账户（记住用户名和密码）
4. 跳过所有可选功能

设置完成后，启用 SSH：

1. 打开系统设置 → 通用 → 共享
2. 启用 "远程登录"

---

## 4) 获取虚拟机的 IP 地址

```bash
lume get openclaw
```

查找 IP 地址（通常为 `192.168.64.x`）。

---

## 5) SSH 登录虚拟机

```bash
ssh youruser@192.168.64.X
```

将 `youruser` 替换为您创建的账户，将 IP 替换为您的虚拟机 IP。

---

## 6) 安装 OpenClaw

在虚拟机内：

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

按照引导提示设置您的模型提供商（Anthropic、OpenAI 等）。

---

## 7) 配置通道

编辑配置文件：

```bash
nano ~/.openclaw/openclaw.json
```

添加您的通道：

```json
{
  "channels": {
    "whatsapp": {
      "dmPolicy": "allowlist",
      "allowFrom": ["+15551234567"]
    },
    "telegram": {
      "botToken": "YOUR_BOT_TOKEN"
    }
  }
}
```

然后登录 WhatsApp（扫描二维码）：

```bash
openclaw channels login
```

---

## 8) 无头运行虚拟机

停止虚拟机并以无显示模式重启：

```bash
lume stop openclaw
lume run openclaw --no-display
```

虚拟机在后台运行。OpenClaw 的守护进程保持网关运行。

检查状态：

```bash
ssh youruser@192.168.64.X "openclaw status"
```

---

## 额外提示：iMessage 集成

这是在 macOS 上运行的杀手级功能。使用 [BlueBubbles](https://bluebubbles.app) 将 iMessage 添加到 OpenClaw。

在虚拟机内：

1. 从 bluebubbles.app 下载 BlueBubbles
2. 使用您的 Apple ID 登录
3. 启用 Web API 并设置密码
4. 将 BlueBubbles 的 Webhook 指向您的网关（示例：`https://your-gateway-host:3000/bluebubbles-webhook?password=<password>`）

添加到您的 OpenClaw 配置中：

```json
{
  "channels": {
    "bluebubbles": {
      "serverUrl": "http://localhost:1234",
      "password": "your-api-password",
      "webhookPath": "/bluebubbles-webhook"
    }
  }
}
```

重启网关。现在您的代理可以发送和接收 iMessage。

完整设置详情：[BlueBubbles 通道](/channels/bluebubbles)

---

## 保存