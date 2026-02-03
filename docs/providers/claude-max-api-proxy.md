---
summary: "Use Claude Max/Pro subscription as an OpenAI-compatible API endpoint"
read_when:
  - You want to use Claude Max subscription with OpenAI-compatible tools
  - You want a local API server that wraps Claude Code CLI
  - You want to save money by using subscription instead of API keys
title: "Claude Max API Proxy"
---
# Claude Max API 代理

**claude-max-api-proxy** 是一个社区工具，它将您的 Claude Max/Pro 订阅暴露为 OpenAI 兼容的 API 端点。这使您可以将订阅用于任何支持 OpenAI API 格式的工具。

## 为什么使用这个工具？

| 方法               | 成本                                                | 最佳用途                                   |
|---------------------|---------------------------------------------------|------------------------------------------ |
| Anthropic API      | 按 token 计费（输入约 $15/百万，输出约 $75/百万 对于 Opus） | 生产应用，高流量                           |
| Claude Max 订阅   | 每月 $200 固定费用                                 | 个人使用，开发，无限制使用                 |

如果您拥有 Claude Max 订阅并希望将其用于 OpenAI 兼容的工具，此代理可以为您节省大量费用。

## 工作原理

```
您的应用 → claude-max-api-proxy → Claude Code CLI → Anthropic（通过订阅）
     （OpenAI 格式）               （转换格式）         （使用您的登录信息）
```

代理：

1. 在 `http://localhost:3456/v1/chat/completions` 接受 OpenAI 格式的请求
2. 将其转换为 Claude Code CLI 命令
3. 以 OpenAI 格式返回响应（支持流式传输）

## 安装

```bash
# 需要 Node.js 20+ 和 Claude Code CLI
npm install -g claude-max-api-proxy

# 验证 Claude CLI 是否已认证
claude --version
```

## 使用

### 启动服务器

```bash
claude-max-api
# 服务器运行在 http://localhost:3456
```

### 测试

```bash
# 健康检查
curl http://localhost:3456/health

# 列出模型
curl http://localhost:3456/v1/models

# 聊天完成
curl http://localhost:3456/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 使用 OpenClaw

您可以将 OpenClaw 指向代理作为自定义的 OpenAI 兼容端点：

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

| 模型 ID          | 映射到         |
| -------------    | -----------    |
| `claude-opus-4`  | Claude Opus 4  |
| `claude-sonnet-4`| Claude Sonnet 4 |
| `claude-haiku-4` | Claude Haiku 4  |

## 在 macOS 上自动启动

创建一个 LaunchAgent 以自动运行代理：

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

## 链接

- **npm:** https://www.npmjs.com/package/claude-max-api-proxy
- **GitHub:** https://github.com/atalovesyou/claude-max-api-proxy
- **问题:** https://github.com/atalovesyou/claude-max-api-proxy/issues

## 注意事项

- 这是一个 **社区工具**，并非由 Anthropic 或 OpenClaw 官方支持
- 需要具有 Claude Code CLI 认证的活跃 Claude Max/Pro 订阅
- 代理在本地运行，不会将数据发送到任何第三方服务器
- 支持流式响应

## 参见

- [Anthropic 提供商](/providers/anthropic) - 与 Claude 配置 setup-token 或 API 密钥的原生 OpenClaw 集成
- [OpenAI 提供商](/providers/openai) - 用于 OpenAI/Codex 订阅