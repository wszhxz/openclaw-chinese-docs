---
summary: "Manual logins for browser automation + X/Twitter posting"
read_when:
  - You need to log into sites for browser automation
  - You want to post updates to X/Twitter
title: "Browser Login"
---
# 浏览器登录 + X/Twitter 发帖

## 手动登录（推荐）

当网站需要登录时，在**宿主**浏览器配置文件（openclaw 浏览器）中**手动登录**。

**不要**向模型提供您的凭据。自动登录经常会触发反机器人防御机制，并可能导致账户被锁定。

返回主浏览器文档：[Browser](/tools/browser)。

## 使用哪个 Chrome 配置文件？

OpenClaw 控制一个**专用的 Chrome 配置文件**（命名为 `openclaw`，橙色界面）。这与您的日常浏览器配置文件是分开的。

两种轻松访问的方法：

1. **让代理打开浏览器**，然后您自己登录。
2. **通过 CLI 打开**：

```bash
openclaw browser start
openclaw browser open https://x.com
```

如果您有多个配置文件，请传递 `--browser-profile <name>`（默认是 `openclaw`）。

## X/Twitter：推荐流程

- **阅读/搜索/线程：** 使用 **bird** CLI 技能（无需浏览器，稳定）。
  - 仓库：https://github.com/steipete/bird
- **发布更新：** 使用**宿主**浏览器（手动登录）。

## 沙盒化 + 宿主浏览器访问

沙盒化的浏览器会话**更有可能**触发机器人检测。对于 X/Twitter（及其他严格网站），建议使用**宿主**浏览器。

如果代理被沙盒化，浏览器工具默认使用沙盒。要允许宿主控制：

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

然后针对宿主浏览器：

```bash
openclaw browser open https://x.com --browser-profile openclaw --target host
```

或者为发布更新的代理禁用沙盒化。