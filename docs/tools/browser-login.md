---
summary: "Manual logins for browser automation + X/Twitter posting"
read_when:
  - You need to log into sites for browser automation
  - You want to post updates to X/Twitter
title: "Browser Login"
---
# 浏览器登录 + X/Twitter 发布

## 手动登录（推荐）

当某个网站需要登录时，请在**主机**浏览器配置文件（即 openclaw 浏览器）中**手动登录**。

**不要**将您的凭据提供给模型。自动登录通常会触发反机器人防御机制，并可能导致账户被锁定。

返回到主浏览器文档：[Browser](/tools/browser)。

## 使用哪个 Chrome 配置文件？

OpenClaw 控制一个**专用的 Chrome 配置文件**（名为 `openclaw`，橙色调 UI）。这与您日常使用的浏览器配置文件是分开的。

两种简单的访问方法：

1. **让代理打开浏览器**，然后自己登录。
2. **通过 CLI 打开**：

```bash
openclaw browser start
openclaw browser open https://x.com
```

如果您有多个配置文件，请传递 `--browser-profile <name>`（默认为 `openclaw`）。

## X/Twitter：推荐流程

- **阅读/搜索/帖子：** 使用**主机**浏览器（手动登录）。
- **发布更新：** 使用**主机**浏览器（手动登录）。

## 沙盒 + 主机浏览器访问

沙盒化的浏览器会话**更有可能**触发机器人检测。对于 X/Twitter（以及其他严格的网站），建议使用**主机**浏览器。

如果代理被沙盒化，浏览器工具将默认使用沙盒。要允许主机控制：

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

然后定位到主机浏览器：

```bash
openclaw browser open https://x.com --browser-profile openclaw --target host
```

或者禁用发布更新的代理的沙盒功能。