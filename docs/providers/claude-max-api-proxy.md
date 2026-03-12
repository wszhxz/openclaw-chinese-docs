---
summary: "Community proxy to expose Claude subscription credentials as an OpenAI-compatible endpoint"
read_when:
  - You want to use Claude Max subscription with OpenAI-compatible tools
  - You want a local API server that wraps Claude Code CLI
  - You want to evaluate subscription-based vs API-key-based Anthropic access
title: "Claude Max API Proxy"
---
# Claude Max API 代理

**claude-max-api-proxy** 是一款社区工具，可将您的 Claude Max/Pro 订阅暴露为与 OpenAI 兼容的 API 端点。这使您能够将订阅用于任何支持 OpenAI API 格式的工具。

<Warning>
This path is technical compatibility only. Anthropic has blocked some subscription
usage outside Claude Code in the past. You must decide for yourself whether to use
it and verify Anthropic's current terms before relying on it.
</Warning>

## 为何使用此工具？

| 方式                     | 成本                                                   | 最适合的场景                         |
| ------------------------ | ------------------------------------------------------ | -------------------------------------- |
| Anthropic API            | 按 Token 计费（Opus 模型约为 $15/百万输入 Token，$75/百万输出 Token） | 生产级应用、高吞吐量场景               |
| Claude Max 订阅          | 每月固定 $200                                          | 个人使用、开发、无限制调用             |

如果您已拥有 Claude Max 订阅，并希望将其与兼容 OpenAI 的工具配合使用，该代理可能在某些工作流中降低使用成本。但对于生产环境，API 密钥仍是更明确且符合政策要求的方式。

## 工作原理

```
Your App → claude-max-api-proxy → Claude Code CLI → Anthropic (via subscription)
     (OpenAI format)              (converts format)      (uses your login)
```

该代理：

1. 在 `http://localhost:3456/v1/chat/completions` 接收符合 OpenAI 格式的请求  
2. 将其转换为 Claude Code CLI 命令  
3. 以 OpenAI 格式返回响应（支持流式响应）

## 安装

```bash
# Requires Node.js 20+ and Claude Code CLI
npm install -g claude-max-api-proxy

# Verify Claude CLI is authenticated
claude --version
```

## 使用方法

### 启动服务器

```bash
claude-max-api
# Server runs at http://localhost:3456
```

### 测试代理

```bash
# Health check
curl http://localhost:3456/health

# List models
curl http://localhost:3456/v1/models

# Chat completion
curl http://localhost:3456/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 与 OpenClaw 配合使用

您可以将 OpenClaw 指向该代理，作为自定义的 OpenAI 兼容端点：

```json5
{
  env: {
    OPENAI_API_KEY: "not-needed",
    OPENAI_BASE_URL: "http://localhost:3456/v1",
  },
  agents: {
    defaults: {
      model: { primary: "openai/claude-opus-4" },
    },
  },
}
```

## 可用模型

| 模型 ID           | 对应模型         |
| ----------------- | ---------------- |
| `claude-opus-4`   | Claude Opus 4    |
| `claude-sonnet-4` | Claude Sonnet 4  |
| `claude-haiku-4`  | Claude Haiku 4   |

## 在 macOS 上自动启动

创建一个 LaunchAgent，使代理自动运行：

```bash
cat > ~/Library/LaunchAgents/com.claude-max-api.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.claude-max-api</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/node</string>
    <string>/usr/local/lib/node_modules/claude-max-api-proxy/dist/server/standalone.js</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/opt/homebrew/bin:~/.local/bin:/usr/bin:/bin</string>
  </dict>
</dict>
</plist>
EOF

launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude-max-api.plist
```

## 相关链接

- **npm：** [https://www.npmjs.com/package/claude-max-api-proxy](https://www.npmjs.com/package/claude-max-api-proxy)  
- **GitHub：** [https://github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy)  
- **问题反馈：** [https://github.com/atalovesyou/claude-max-api-proxy/issues](https://github.com/atalovesyou/claude-max-api-proxy/issues)

## 注意事项

- 这是一款 **社区维护的工具**，并非 Anthropic 或 OpenClaw 官方支持  
- 需要有效的 Claude Max/Pro 订阅，并已完成 Claude Code CLI 的身份验证  
- 代理在本地运行，不会将数据发送至任何第三方服务器  
- 完全支持流式响应  

## 参见

- [Anthropic 提供程序](/providers/anthropic) —— OpenClaw 原生集成 Claude，支持 setup-token 或 API 密钥方式  
- [OpenAI 提供程序](/providers/openai) —— 适用于 OpenAI/Codex 订阅