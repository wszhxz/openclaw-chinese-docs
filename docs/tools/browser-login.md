---
summary: "Manual logins for browser automation + X/Twitter posting"
read_when:
  - You need to log into sites for browser automation
  - You want to post updates to X/Twitter
title: "Browser Login"
---
# 浏览器登录 + X/Twitter 发布

## 手动登录（推荐）

当网站需要登录时，请在 **主机** 浏览器配置文件中 **手动登录**（即 openclaw 浏览器）。

**不要** 将您的凭据提供给模型。自动登录通常会触发反爬虫防御机制，可能导致账号被锁定。

返回主浏览器文档：[浏览器](/tools/browser)。

## 使用的是哪个 Chrome 配置文件？

OpenClaw 控制一个 **专用 Chrome 配置文件**（名称为 `openclaw`，橙色调界面）。这与您的日常浏览器配置文件是分开的。

访问它的两种简单方式：

1. **请代理打开浏览器**，然后您自行登录。
2. **通过 CLI 打开**：

```bash
openclaw browser start
openclaw browser open https://x.com
```

如果您有多个配置文件，请通过 `--browser-profile <name>` 指定（默认为 `openclaw`）。

## X/Twitter：推荐流程

- **阅读/搜索/查看线程**：使用 **bird** CLI 工具（无需浏览器，稳定）。
  - 仓库：https://github.com/steipete/bird
- **发布更新**：使用 **主机** 浏览器（手动登录）。

## 沙箱化 + 主机浏览器访问

沙箱化的浏览器会话 **更可能** 触发机器人检测。对于 X/Twitter（及其他严格网站），建议使用 **主机** 浏览器。

如果代理是沙箱化的，浏览器工具默认使用沙箱。要允许主机控制：

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        browser: {
          allowHostControl: true,
        },
      },
    },
  },
}
```

然后针对主机浏览器操作：

```bash
openclaw browser open https://x.com --browser-profile openclaw --target host
```

或禁用发布更新代理的沙箱功能。