---
summary: "Where OpenClaw loads environment variables and the precedence order"
read_when:
  - You need to know which env vars are loaded, and in what order
  - You are debugging missing API keys in the Gateway
  - You are documenting provider auth or deployment environments
title: "Environment Variables"
---
# 环境变量

OpenClaw 从多个来源获取环境变量。规则是**绝不覆盖已有的值**。

## 优先级（最高 → 最低）

1. **进程环境**（Gateway 进程从父 shell/守护进程已有的环境变量）。
2. **当前工作目录中的 .env 文件**（dotenv 默认行为；不覆盖）。
3. **全局 .env 文件**位于 `~/.openclaw/.env`（即 `$OPENCLAW_STATE_DIR/.env`；不覆盖）。
4. **配置文件 `env` 块**在 `~/.openclaw/openclaw.json`（仅在缺失时应用）。
5. **可选的登录 shell 导入**（`env.shellEnv.enabled` 或 `OPENCLAW_LOAD_SHELL_ENV=1`），仅在缺失预期键时应用。

如果配置文件完全缺失，步骤 4 将被跳过；若启用，shell 导入仍会运行。

## 配置 `env` 块

设置内联环境变量的两种等效方式（两者均不覆盖）：

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: {
      GROQ_API_KEY: "gsk-...",
    },
  },
}
```

## Shell 环境导入

`env.shellEnv` 会运行你的登录 shell，并仅导入**缺失的预期键**：

```json5
{
  env: {
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

环境变量等效项：

- `OPENCLAW_LOAD_SHELL_ENV=1`
- `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`

## 配置中的环境变量替换

你可以在配置字符串值中直接引用环境变量，使用 `${VAR_NAME}` 语法：

```json5
{
  models: {
    providers: {
      "vercel-gateway": {
        apiKey: "${VERCEL_GATEWAY_API_KEY}",
      },
    },
  },
}
```

详见 [配置：环境变量替换](/gateway/configuration#env-var-substitution-in-config) 获取完整详情。

## 相关内容

- [网关配置](/gateway/configuration)
- [FAQ：环境变量和 .env 加载](/help/faq#env-vars-and-env-loading)
- [模型概览](/concepts/models)