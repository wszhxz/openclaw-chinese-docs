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

1. **进程环境**（网关进程从父 shell/守护进程已经拥有的）。
2. 当前工作目录中的 **`.env`**（dotenv 默认；不覆盖）。
3. 全局 **`.env`** 在 `~/.openclaw/.env`（即 `$OPENCLAW_STATE_DIR/.env`；不覆盖）。
4. **Config `env` 块** 在 `~/.openclaw/openclaw.json`（仅在缺失时应用）。
5. **可选登录 shell 导入**（`env.shellEnv.enabled` 或 `OPENCLAW_LOAD_SHELL_ENV=1`），仅在预期键缺失时应用。

如果配置文件完全缺失，则跳过步骤 4；如果启用，shell 导入仍然会运行。

## Config `env` 块

设置内联 env vars 的两种等效方法（两者均为非覆盖）：

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

## Shell env 导入

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

Env var 等价物：

- `OPENCLAW_LOAD_SHELL_ENV=1`
- `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`

## 配置中的 env var 替换

您可以在配置字符串值中直接引用 env var，使用 `${VAR_NAME}` 语法：

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

有关详细信息，请参阅 [配置：Env var 替换](/gateway/configuration#env-var-substitution-in-config)。

## 与路径相关的 env var

| 变量               | 目的                                                                                                                                                                          |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `OPENCLAW_HOME`        | 覆盖用于所有内部路径解析的主目录 (`~/.openclaw/`，代理目录，会话，凭据)。在以专用服务用户身份运行 OpenClaw 时很有用。 |
| `OPENCLAW_STATE_DIR`   | 覆盖状态目录（默认 `~/.openclaw`）。                                                                                                                            |
| `OPENCLAW_CONFIG_PATH` | 覆盖配置文件路径（默认 `~/.openclaw/openclaw.json`）。                                                                                                             |

### `OPENCLAW_HOME`

设置时，`OPENCLAW_HOME` 替换系统主目录 (`$HOME` / `os.homedir()`) 用于所有内部路径解析。这为无头服务账户启用了完整的文件系统隔离。

**优先级：** `OPENCLAW_HOME` > `$HOME` > `USERPROFILE` > `os.homedir()`

**示例**（macOS LaunchDaemon）：

```xml
<key>EnvironmentVariables</key>
<dict>
  <key>OPENCLAW_HOME</key>
  <string>/Users/kira</string>
</dict>
```

`OPENCLAW_HOME` 也可以设置为波浪号路径（例如 `~/svc`），在使用前使用 `$HOME` 展开。

## 相关

- [网关配置](/gateway/configuration)
- [FAQ: env vars 和 .env 加载](/help/faq#env-vars-and-env-loading)
- [模型概述](/concepts/models)