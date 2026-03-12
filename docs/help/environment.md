---
summary: "Where OpenClaw loads environment variables and the precedence order"
read_when:
  - You need to know which env vars are loaded, and in what order
  - You are debugging missing API keys in the Gateway
  - You are documenting provider auth or deployment environments
title: "Environment Variables"
---
# 环境变量

OpenClaw 从多个来源读取环境变量。规则是：**绝不覆盖已存在的值**。

## 优先级（从高到低）

1. **进程环境**（网关进程从父 shell/守护进程继承的环境变量）。
2. 当前工作目录下的 **`.env`**（dotenv 默认行为；不覆盖现有值）。
3. 全局 **`.env`**，位于 **`~/.openclaw/.env`**（即 **`$OPENCLAW_STATE_DIR/.env`**；不覆盖现有值）。
4. **`env`** 配置块（仅在对应值缺失时应用），位于 **`~/.openclaw/openclaw.json`** 中。
5. 可选的登录 shell 导入（**`env.shellEnv.enabled`** 或 **`OPENCLAW_LOAD_SHELL_ENV=1`**），仅对预期但缺失的键执行导入。

如果配置文件完全不存在，则跳过第 4 步；若启用，shell 导入仍会运行。

## 配置中的 **`env`** 块

设置内联环境变量的两种等效方式（均不覆盖现有值）：

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

## Shell 环境变量导入

**`env.shellEnv`** 运行您的登录 shell，并仅导入**缺失的**预期键：

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

环境变量等价形式：

- `OPENCLAW_LOAD_SHELL_ENV=1`
- `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`

## 运行时注入的环境变量

OpenClaw 还会在派生的子进程中注入上下文标记：

- `OPENCLAW_SHELL=exec`：对通过 **`exec`** 工具运行的命令设置。
- `OPENCLAW_SHELL=acp`：对 ACP 运行时后端进程派生操作设置（例如 **`acpx`**）。
- `OPENCLAW_SHELL=acp-client`：对 **`openclaw acp client`** 在派生 ACP 桥接进程时设置。
- `OPENCLAW_SHELL=tui-local`：对本地 TUI **`!`** shell 命令设置。

这些是运行时标记（非用户必需配置），可在 shell/profile 逻辑中用于应用上下文相关的规则。

## 配置中的环境变量替换

您可在配置字符串值中直接引用环境变量，使用 **`${VAR_NAME}`** 语法：

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

完整细节请参阅 [配置：配置中的环境变量替换](/gateway/configuration#env-var-substitution-in-config)。

## SecretRef 与 **`${ENV}`** 字符串

OpenClaw 支持两种基于环境变量的模式：

- 配置值中的 **`${VAR}`** 字符串替换。
- SecretRef 对象（**`{ source: "env", provider: "default", id: "VAR" }`**），适用于支持密钥引用的字段。

两者均在激活时从进程环境解析。SecretRef 的详细信息见 [密钥管理](/gateway/secrets)。

## 与路径相关的环境变量

| 变量               | 用途                                                                                                                                                                          |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `OPENCLAW_HOME`        | 覆盖所有内部路径解析所使用的主目录（**`~/.openclaw/`**、代理目录、会话、凭据）。在以专用服务用户身份运行 OpenClaw 时非常有用。 |
| `OPENCLAW_STATE_DIR`   | 覆盖状态目录（默认为 **`~/.openclaw`**）。                                                                                                                            |
| `OPENCLAW_CONFIG_PATH` | 覆盖配置文件路径（默认为 **`~/.openclaw/openclaw.json`**）。                                                                                                             |

## 日志记录

| 变量             | 用途                                                                                                                                                                                      |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `OPENCLAW_LOG_LEVEL` | 覆盖文件和控制台的日志级别（例如 **`debug`**、**`trace`**）。其优先级高于配置中的 **`logging.level`** 和 **`logging.consoleLevel`**。无效值将被忽略，并发出警告。 |

### `OPENCLAW_HOME`

当设置该变量时，**`OPENCLAW_HOME`** 将替代系统主目录（**`$HOME`** / **`os.homedir()`**），用于所有内部路径解析。这可为无头服务账户提供完整的文件系统隔离。

**优先级：** **`OPENCLAW_HOME`** > **`$HOME`** > **`USERPROFILE`** > **`os.homedir()`**

**示例**（macOS LaunchDaemon）：

```xml
<key>EnvironmentVariables</key>
<dict>
  <key>OPENCLAW_HOME</key>
  <string>/Users/kira</string>
</dict>
```

**`OPENCLAW_HOME`** 也可设为波浪线路径（例如 **`~/svc`**），该路径将在使用前通过 **`$HOME`** 展开。

## 相关内容

- [网关配置](/gateway/configuration)
- [常见问题解答：环境变量与 .env 加载](/help/faq#env-vars-and-env-loading)
- [模型概述](/concepts/models)