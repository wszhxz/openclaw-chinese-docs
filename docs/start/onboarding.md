---
summary: "First-run onboarding flow for OpenClaw (macOS app)"
read_when:
  - Designing the macOS onboarding assistant
  - Implementing auth or identity setup
title: "Onboarding"
---
# 引导 (macOS 应用)

本文档描述了**当前**的首次运行引导流程。目标是实现一个平滑的“第0天”体验：选择网关运行位置、连接认证、运行向导，并让代理自行初始化。

## 页面顺序 (当前)

1. 欢迎 + 安全提示
2. **网关选择** (本地 / 远程 / 后续配置)
3. **认证 (Anthropic OAuth)** — 仅限本地
4. **设置向导** (网关驱动)
5. **权限** (TCC 提示)
6. **CLI** (可选)
7. **引导聊天** (专用会话)
8. 准备就绪

## 1) 欢迎 + 安全提示

阅读显示的安全提示并根据提示决定。

## 2) 本地 vs 远程

**网关**运行在何处？

- **本地 (此 Mac):** 引导可以运行 OAuth 流程并在本地写入凭证。
- **远程 (通过 SSH/Tailnet):** 引导**不**在本地运行 OAuth；凭证必须存在于网关主机上。
- **后续配置:** 跳过设置并保持应用未配置。

网关认证提示：

- 向导现在即使对于回环地址也会生成**令牌**，因此本地 WebSocket 客户端必须进行认证。
- 如果禁用认证，任何本地进程都可以连接；仅在完全信任的机器上使用。
- 使用**令牌**进行多机访问或非回环绑定。

## 3) 仅限本地认证 (Anthropic OAuth)

macOS 应用支持 Anthropic OAuth (Claude Pro/Max)。流程如下：

- 打开浏览器进行 OAuth (PKCE)
- 要求用户粘贴 `code#state` 值
- 将凭证写入 `~/.openclaw/credentials/oauth.json`

其他提供者 (OpenAI、自定义 API) 目前通过环境变量或配置文件进行配置。

## 4) 设置向导 (网关驱动)

应用可以运行与 CLI 相同的设置向导。这使引导与网关端行为保持同步，并避免在 SwiftUI 中重复逻辑。

## 5) 权限

引导请求 TCC 权限，用于以下功能：

- 通知
- 可访问性
- 屏幕录制
- 麦克风 / 语音识别
- 自动化 (AppleScript)

## 6) CLI (可选)

应用可通过 npm/pnpm 安装全局 `openclaw` CLI，使终端工作流和 launchd 任务开箱即用。

## 7) 引导聊天 (专用会话)

设置完成后，应用打开专用的引导聊天会话，以便代理自我介绍并指导下一步。这将首次运行的引导指导与您的常规对话分开。

## 代理初始化仪式

首次运行代理时，OpenClaw 会初始化一个工作区（默认 `~/.openclaw/workspace`）：

- 初始化 `AGENTS.md`、`BOOTSTRAP.md`、`IDENTITY.md`、`USER.md`
- 运行一个简短的问答仪式（每次一个问题）
- 将身份 + 偏好写入 `IDENTITY.md`、`USER.md`、`SOUL.md`
- 完成后删除 `BOOTSTRAP.md`，确保仅运行一次

## 可选：Gmail 钩子 (手动)

Gmail Pub/Sub 设置目前仍为手动步骤。使用：

```bash
openclaw webhooks gmail setup --account you@gmail.com
```

详情请参见 [/自动化/gmail-pubsub](/自动化/gmail-pubsub)。

## 远程模式说明

当网关运行在另一台机器上时，凭证和工作区文件存储在**该主机**上。如果需要在远程模式中使用 OAuth，请在网关主机上创建以下文件：

- `~/.openclaw/credentials/oauth.json`
- `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`