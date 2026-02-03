---
summary: "Where OpenClaw loads environment variables and the precedence order"
read_when:
  - You need to know which env vars are loaded, and in what order
  - You are debugging missing API keys in the Gateway
  - You are documenting provider auth or deployment environments
title: "Environment Variables"
---
# 环境变量

OpenClaw 从多个来源拉取环境变量。规则是 **从不覆盖现有值**。

## 优先级（从高到低）

1. **进程环境**（网关进程从父 shell/守护进程已有的内容）。
2. 当前工作目录中的 **`.env`**（dotenv 默认；不覆盖）。
3. 全局 **`.env`** 在 `~/.openclaw/.env`（即 `$OPENCLAW_STATE_DIR/.env`；不覆盖）。
4. **Config `env` 块** 在 `~/.openclaw/openclaw.json`（仅在缺失时应用）。
5. **可选登录 shell 导入**（`env.shellEnv.enabled` 或 `OPENCLAW_LOAD_SHELL_ENV=1`），仅在预期键缺失时应用。

如果配置文件完全缺失，则跳过步骤 4；如果启用，shell 导入仍然运行。

## Config `env` 块

设置内联环境变量的两种等效方式（两者均为非覆盖）：

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

`env.shellEnv` 运行您的登录 shell 并仅导入 **缺失** 的预期键：

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

您可以在配置字符串值中直接引用环境变量，使用 `${VAR_NAME}` 语法：

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

有关详细信息，请参阅 [配置：环境变量替换](/gateway/configuration#env-var-substitution-in-config)。

## 相关

- [网关配置](/gateway/configuration)
- [FAQ：环境变量和 .env 加载](/help/faq#env-vars-and-env-loading)
- [模型概述](/concepts/models)