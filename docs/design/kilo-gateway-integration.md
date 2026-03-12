# Kilo 网关提供程序集成设计

## 概述

本文档概述了将“Kilo 网关”作为一级提供程序集成到 OpenClaw 中的设计方案，其设计参考了现有的 OpenRouter 实现。Kilo 网关使用与 OpenAI 兼容的补全（completions）API，但基础 URL 不同。

## 设计决策

### 1. 提供程序命名

**建议：`kilocode`**

理由：

- 与用户配置示例中提供的 (`kilocode` 提供程序键) 保持一致  
- 符合现有提供程序的命名模式（例如 `openrouter`、`opencode`、`moonshot`）
- 简短且易于记忆
- 避免与泛义的 “kilo” 或 “gateway” 术语混淆

曾考虑的替代方案：`kilo-gateway` —— 已否决，因为连字符命名在代码库中较少见，且 `kilocode` 更为简洁。

### 2. 默认模型引用

**建议：`kilocode/anthropic/claude-opus-4.6`**

理由：

- 基于用户配置示例
- Claude Opus 4.5 是一个能力出色的默认模型
- 显式指定模型可避免依赖自动路由机制

### 3. 基础 URL 配置

**建议：硬编码默认值，并支持配置覆盖**

- **默认基础 URL：** `https://api.kilo.ai/api/gateway/`  
- **是否可配置：** 是，通过 `models.providers.kilocode.baseUrl`

该方式与 Moonshot、Venice 和 Synthetic 等其他提供程序所采用的模式一致。

### 4. 模型扫描

**建议：初始阶段不提供专用的模型扫描端点**

理由：

- Kilo 网关代理至 OpenRouter，因此模型是动态的  
- 用户可在其配置中手动配置模型  
- 若未来 Kilo 网关暴露了 `/models` 端点，则可后续添加扫描功能

### 5. 特殊处理

**建议：对 Anthropic 模型继承 OpenRouter 的行为**

由于 Kilo 网关代理至 OpenRouter，应沿用相同的特殊处理逻辑：

- 对 `anthropic/*` 模型启用缓存 TTL 合规性检查  
- 对 `anthropic/*` 模型附加额外参数（`cacheControlTtl`）  
- 转录策略遵循 OpenRouter 的模式

## 需修改的文件

### 核心凭证管理

#### 1. `src/commands/onboard-auth.credentials.ts`

添加：

```typescript
export const KILOCODE_DEFAULT_MODEL_REF = "kilocode/anthropic/claude-opus-4.6";

export async function setKilocodeApiKey(key: string, agentDir?: string) {
  upsertAuthProfile({
    profileId: "kilocode:default",
    credential: {
      type: "api_key",
      provider: "kilocode",
      key,
    },
    agentDir: resolveAuthAgentDir(agentDir),
  });
}
```

#### 2. `src/agents/model-auth.ts`

在 `resolveEnvApiKey()` 的 `envMap` 中添加：

```typescript
const envMap: Record<string, string> = {
  // ... existing entries
  kilocode: "KILOCODE_API_KEY",
};
```

#### 3. `src/config/io.ts`

在 `SHELL_ENV_EXPECTED_KEYS` 中添加：

```typescript
const SHELL_ENV_EXPECTED_KEYS = [
  // ... existing entries
  "KILOCODE_API_KEY",
];
```

### 配置应用

#### 4. `src/commands/onboard-auth.config-core.ts`

添加新函数：

```typescript
export const KILOCODE_BASE_URL = "https://api.kilo.ai/api/gateway/";

export function applyKilocodeProviderConfig(cfg: OpenClawConfig): OpenClawConfig {
  const models = { ...cfg.agents?.defaults?.models };
  models[KILOCODE_DEFAULT_MODEL_REF] = {
    ...models[KILOCODE_DEFAULT_MODEL_REF],
    alias: models[KILOCODE_DEFAULT_MODEL_REF]?.alias ?? "Kilo Gateway",
  };

  const providers = { ...cfg.models?.providers };
  const existingProvider = providers.kilocode;
  const { apiKey: existingApiKey, ...existingProviderRest } = (existingProvider ?? {}) as Record<
    string,
    unknown
  > as { apiKey?: string };
  const resolvedApiKey = typeof existingApiKey === "string" ? existingApiKey : undefined;
  const normalizedApiKey = resolvedApiKey?.trim();

  providers.kilocode = {
    ...existingProviderRest,
    baseUrl: KILOCODE_BASE_URL,
    api: "openai-completions",
    ...(normalizedApiKey ? { apiKey: normalizedApiKey } : {}),
  };

  return {
    ...cfg,
    agents: {
      ...cfg.agents,
      defaults: {
        ...cfg.agents?.defaults,
        models,
      },
    },
    models: {
      mode: cfg.models?.mode ?? "merge",
      providers,
    },
  };
}

export function applyKilocodeConfig(cfg: OpenClawConfig): OpenClawConfig {
  const next = applyKilocodeProviderConfig(cfg);
  const existingModel = next.agents?.defaults?.model;
  return {
    ...next,
    agents: {
      ...next.agents,
      defaults: {
        ...next.agents?.defaults,
        model: {
          ...(existingModel && "fallbacks" in (existingModel as Record<string, unknown>)
            ? {
                fallbacks: (existingModel as { fallbacks?: string[] }).fallbacks,
              }
            : undefined),
          primary: KILOCODE_DEFAULT_MODEL_REF,
        },
      },
    },
  };
}
```

### 认证选项系统

#### 5. `src/commands/onboard-types.ts`

在 `AuthChoice` 类型中添加：

```typescript
export type AuthChoice =
  // ... existing choices
  "kilocode-api-key";
// ...
```

在 `OnboardOptions` 中添加：

```typescript
export type OnboardOptions = {
  // ... existing options
  kilocodeApiKey?: string;
  // ...
};
```

#### 6. `src/commands/auth-choice-options.ts`

在 `AuthChoiceGroupId` 中添加：

```typescript
export type AuthChoiceGroupId =
  // ... existing groups
  "kilocode";
// ...
```

在 `AUTH_CHOICE_GROUP_DEFS` 中添加：

```typescript
{
  value: "kilocode",
  label: "Kilo Gateway",
  hint: "API key (OpenRouter-compatible)",
  choices: ["kilocode-api-key"],
},
```

在 `buildAuthChoiceOptions()` 中添加：

```typescript
options.push({
  value: "kilocode-api-key",
  label: "Kilo Gateway API key",
  hint: "OpenRouter-compatible gateway",
});
```

#### 7. `src/commands/auth-choice.preferred-provider.ts`

添加映射：

```typescript
const PREFERRED_PROVIDER_BY_AUTH_CHOICE: Partial<Record<AuthChoice, string>> = {
  // ... existing mappings
  "kilocode-api-key": "kilocode",
};
```

### 认证选项应用

#### 8. `src/commands/auth-choice.apply.api-providers.ts`

添加导入语句：

```typescript
import {
  // ... existing imports
  applyKilocodeConfig,
  applyKilocodeProviderConfig,
  KILOCODE_DEFAULT_MODEL_REF,
  setKilocodeApiKey,
} from "./onboard-auth.js";
```

为 `kilocode-api-key` 添加处理逻辑：

```typescript
if (authChoice === "kilocode-api-key") {
  const store = ensureAuthProfileStore(params.agentDir, {
    allowKeychainPrompt: false,
  });
  const profileOrder = resolveAuthProfileOrder({
    cfg: nextConfig,
    store,
    provider: "kilocode",
  });
  const existingProfileId = profileOrder.find((profileId) => Boolean(store.profiles[profileId]));
  const existingCred = existingProfileId ? store.profiles[existingProfileId] : undefined;
  let profileId = "kilocode:default";
  let mode: "api_key" | "oauth" | "token" = "api_key";
  let hasCredential = false;

  if (existingProfileId && existingCred?.type) {
    profileId = existingProfileId;
    mode =
      existingCred.type === "oauth" ? "oauth" : existingCred.type === "token" ? "token" : "api_key";
    hasCredential = true;
  }

  if (!hasCredential && params.opts?.token && params.opts?.tokenProvider === "kilocode") {
    await setKilocodeApiKey(normalizeApiKeyInput(params.opts.token), params.agentDir);
    hasCredential = true;
  }

  if (!hasCredential) {
    const envKey = resolveEnvApiKey("kilocode");
    if (envKey) {
      const useExisting = await params.prompter.confirm({
        message: `Use existing KILOCODE_API_KEY (${envKey.source}, ${formatApiKeyPreview(envKey.apiKey)})?`,
        initialValue: true,
      });
      if (useExisting) {
        await setKilocodeApiKey(envKey.apiKey, params.agentDir);
        hasCredential = true;
      }
    }
  }

  if (!hasCredential) {
    const key = await params.prompter.text({
      message: "Enter Kilo Gateway API key",
      validate: validateApiKeyInput,
    });
    await setKilocodeApiKey(normalizeApiKeyInput(String(key)), params.agentDir);
    hasCredential = true;
  }

  if (hasCredential) {
    nextConfig = applyAuthProfileConfig(nextConfig, {
      profileId,
      provider: "kilocode",
      mode,
    });
  }
  {
    const applied = await applyDefaultModelChoice({
      config: nextConfig,
      setDefaultModel: params.setDefaultModel,
      defaultModel: KILOCODE_DEFAULT_MODEL_REF,
      applyDefaultConfig: applyKilocodeConfig,
      applyProviderConfig: applyKilocodeProviderConfig,
      noteDefault: KILOCODE_DEFAULT_MODEL_REF,
      noteAgentModel,
      prompter: params.prompter,
    });
    nextConfig = applied.config;
    agentModelOverride = applied.agentModelOverride ?? agentModelOverride;
  }
  return { config: nextConfig, agentModelOverride };
}
```

同时，在函数顶部添加 `tokenProvider` 映射：

```typescript
if (params.opts.tokenProvider === "kilocode") {
  authChoice = "kilocode-api-key";
}
```

### CLI 注册

#### 9. `src/cli/program/register.onboard.ts`

添加 CLI 选项：

```typescript
.option("--kilocode-api-key <key>", "Kilo Gateway API key")
```

在操作处理器中添加：

```typescript
kilocodeApiKey: opts.kilocodeApiKey as string | undefined,
```

更新 `auth-choice` 帮助文本：

```typescript
.option(
  "--auth-choice <choice>",
  "Auth: setup-token|token|chutes|openai-codex|openai-api-key|openrouter-api-key|kilocode-api-key|ai-gateway-api-key|...",
)
```

### 非交互式入门流程

#### 10. `src/commands/onboard-non-interactive/local/auth-choice.ts`

为 `kilocode-api-key` 添加处理逻辑：

```typescript
if (authChoice === "kilocode-api-key") {
  const resolved = await resolveNonInteractiveApiKey({
    provider: "kilocode",
    cfg: baseConfig,
    flagValue: opts.kilocodeApiKey,
    flagName: "--kilocode-api-key",
    envVar: "KILOCODE_API_KEY",
  });
  await setKilocodeApiKey(resolved.apiKey, agentDir);
  nextConfig = applyAuthProfileConfig(nextConfig, {
    profileId: "kilocode:default",
    provider: "kilocode",
    mode: "api_key",
  });
  // ... apply default model
}
```

### 导出更新

#### 11. `src/commands/onboard-auth.ts`

添加导出项：

```typescript
export {
  // ... existing exports
  applyKilocodeConfig,
  applyKilocodeProviderConfig,
  KILOCODE_BASE_URL,
} from "./onboard-auth.config-core.js";

export {
  // ... existing exports
  KILOCODE_DEFAULT_MODEL_REF,
  setKilocodeApiKey,
} from "./onboard-auth.credentials.js";
```

### 特殊处理（可选）

#### 12. `src/agents/pi-embedded-runner/cache-ttl.ts`

为 Anthropic 模型添加 Kilo Gateway 支持：

```typescript
export function isCacheTtlEligibleProvider(provider: string, modelId: string): boolean {
  const normalizedProvider = provider.toLowerCase();
  const normalizedModelId = modelId.toLowerCase();
  if (normalizedProvider === "anthropic") return true;
  if (normalizedProvider === "openrouter" && normalizedModelId.startsWith("anthropic/"))
    return true;
  if (normalizedProvider === "kilocode" && normalizedModelId.startsWith("anthropic/")) return true;
  return false;
}
```

#### 13. `src/agents/transcript-policy.ts`

添加 Kilo Gateway 处理逻辑（类似于 OpenRouter）：

```typescript
const isKilocodeGemini = provider === "kilocode" && modelId.toLowerCase().includes("gemini");

// Include in needsNonImageSanitize check
const needsNonImageSanitize =
  isGoogle || isAnthropic || isMistral || isOpenRouterGemini || isKilocodeGemini;
```

## 配置结构

### 用户配置示例

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "kilocode": {
        "baseUrl": "https://api.kilo.ai/api/gateway/",
        "apiKey": "xxxxx",
        "api": "openai-completions",
        "models": [
          {
            "id": "anthropic/claude-opus-4.6",
            "name": "Anthropic: Claude Opus 4.6"
          },
          { "id": "minimax/minimax-m2.5:free", "name": "Minimax: Minimax M2.5" }
        ]
      }
    }
  }
}
```

### 认证配置文件结构

```json
{
  "profiles": {
    "kilocode:default": {
      "type": "api_key",
      "provider": "kilocode",
      "key": "xxxxx"
    }
  }
}
```

## 测试注意事项

1. **单元测试：**
   - 测试 `setKilocodeApiKey()` 是否写入正确的配置文件
   - 测试 `applyKilocodeConfig()` 是否设置正确的默认值
   - 测试 `resolveEnvApiKey("kilocode")` 是否返回正确的环境变量

2. **集成测试：**
   - 使用 `--auth-choice kilocode-api-key` 测试初始引导流程
   - 使用 `--kilocode-api-key` 测试非交互式初始引导
   - 使用 `kilocode/` 前缀测试模型选择

3. **端到端测试：**
   - 通过 Kilo Gateway 执行实际 API 调用（真实环境测试）

## 迁移说明

- 现有用户无需迁移
- 新用户可立即使用 `kilocode-api-key` 认证选项
- 已存在的、使用 `kilocode` 提供商的手动配置将继续正常工作

## 后续考虑事项

1. **模型目录：** 若 Kilo Gateway 提供 `/models` 接口，则添加类似 `scanOpenRouterModels()` 的扫描支持

2. **OAuth 支持：** 若 Kilo Gateway 增加 OAuth 功能，则相应扩展认证系统

3. **速率限制：** 如有必要，可考虑为 Kilo Gateway 添加专用的速率限制处理机制

4. **文档：** 在 `docs/providers/kilocode.md` 添加说明文档，解释配置与使用方法

## 变更摘要

| 文件                                                        | 变更类型 | 描述                                                             |
| ----------------------------------------------------------- | -------- | ---------------------------------------------------------------- |
| `src/commands/onboard-auth.credentials.ts`                  | 新增         | `KILOCODE_DEFAULT_MODEL_REF`、`setKilocodeApiKey()`                     |
| `src/agents/model-auth.ts`                                  | 修改         | 在 `envMap` 中添加 `kilocode`                                              |
| `src/config/io.ts`                                          | 修改         | 将 `KILOCODE_API_KEY` 添加至 shell 环境变量键列表                                |
| `src/commands/onboard-auth.config-core.ts`                  | 新增         | `applyKilocodeProviderConfig()`、`applyKilocodeConfig()`                |
| `src/commands/onboard-types.ts`                             | 修改         | 在 `AuthChoice` 中添加 `kilocode-api-key`，在选项中添加 `kilocodeApiKey` |
| `src/commands/auth-choice-options.ts`                       | 修改         | 添加 `kilocode` 分组及对应选项                                         |
| `src/commands/auth-choice.preferred-provider.ts`            | 修改         | 添加 `kilocode-api-key` 映射                                          |
| `src/commands/auth-choice.apply.api-providers.ts`           | 修改         | 添加 `kilocode-api-key` 处理逻辑                                         |
| `src/cli/program/register.onboard.ts`                       | 修改         | 添加 `--kilocode-api-key` 选项                                         |
| `src/commands/onboard-non-interactive/local/auth-choice.ts` | 修改         | 添加非交互式处理逻辑                                            |
| `src/commands/onboard-auth.ts`                              | 修改         | 导出新函数                                                    |
| `src/agents/pi-embedded-runner/cache-ttl.ts`                | 修改         | 添加 kilocode 支持                                                    |
| `src/agents/transcript-policy.ts`                           | 修改         | 添加 kilocode Gemini 处理逻辑                                            |