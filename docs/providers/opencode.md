---
summary: "Use OpenCode Zen (curated models) with OpenClaw"
read_when:
  - You want OpenCode Zen for model access
  - You want a curated list of coding-friendly models
title: "OpenCode Zen"
---
# OpenCode Zen

OpenCode Zen 是由 OpenCode 团队为编码代理精选推荐的**模型列表**。  
它是一个可选的托管模型访问路径，使用 API 密钥和 `opencode` 提供商。  
Zen 当前处于测试版。

## CLI 配置

```bash
openclaw onboard --auth-choice opencode-zen
# 或非交互模式
openclaw onboard --opencode-zen-api-key "$OPENCODE_API_KEY"
```

## 配置片段

```json5
{
  env: { OPENCODE_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-5" } } },
}
```

## 注意事项

- 也支持 `OPENCODE_ZEN_API_KEY`。
- 您需登录 Zen，添加账单信息并复制您的 API 密钥。
- OpenCode Zen 按请求计费；请查看 OpenCode 控制台获取详细信息。