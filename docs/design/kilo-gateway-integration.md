# Kilo Gateway Provider 集成设计

## 概述

本文档概述了将 "Kilo Gateway" 作为 OpenClaw 中的一流 provider 进行集成的设计，仿照现有的 OpenRouter 实现。Kilo Gateway 使用具有不同 base URL 的 OpenAI 兼容 completions API。

## 设计决策

### 1. Provider 命名

**建议：`kilocode`**

理由：

- 与提供的用户配置示例匹配（`kilocode` provider key）
- 与现有 provider 命名模式一致（例如 `openrouter`、`opencode`、`moonshot`）
- 简短易记
- 避免与通用的 "kilo" 或 "gateway" 术语混淆

考虑的替代方案：`kilo-gateway` - 被拒绝，因为连字符名称在代码库中较少见，且 `kilocode` 更简洁。

### 2. 默认模型引用

**建议：`kilocode/anthropic/claude-opus-4.6`**

理由：

- 基于用户配置示例
- Claude Opus 4.5 是一个可靠的默认模型
- 显式模型选择避免依赖自动路由

### 3. Base URL 配置

**建议：硬编码默认值，支持配置覆盖**

- **默认 Base URL:** `https://api.kilo.ai/api/gateway/`
- **可配置：** 是，通过 `models.providers.kilocode.baseUrl`

这与 Moonshot、Venice 和 Synthetic 等其他 provider 使用的模式匹配。

### 4. 模型扫描

**建议：初期无专用模型扫描 endpoint**

理由：

- Kilo Gateway 代理到 OpenRouter，因此模型是动态的
- 用户可以在其 config 中手动配置模型
- 如果 Kilo Gateway 未来暴露 `/models` endpoint，则可以添加扫描

### 5. 特殊处理

**建议：继承 OpenRouter 对 Anthropic 模型的行为**

由于 Kilo Gateway 代理到 OpenRouter，应应用相同的特殊处理：

- `anthropic/*` 模型的 Cache TTL 资格
- `anthropic/*` 模型的额外参数 (cacheControlTtl)
- Transcript 策略遵循 OpenRouter 模式

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

添加到 `resolveEnvApiKey()` 中的 `envMap`：

```typescript
const envMap: Record<string, string> = {
  // ... existing entries
  kilocode: "KILOCODE_API_KEY",
};
```

#### 3. `src/config/io.ts`

添加到 `SHELL_ENV_EXPECTED_KEYS`：

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

### Auth Choice 系统

#### 5. `src/commands/onboard-types.ts`

添加到 `AuthChoice` 类型：

```typescript
export type AuthChoice =
  // ... existing choices
  "kilocode-api-key";
// ...
```

添加到 `OnboardOptions`：

```typescript
export type OnboardOptions = {
  // ... existing options
  kilocodeApiKey?: string;
  // ...
};
```

#### 6. `src/commands/auth-choice-options.ts`

添加到 `AuthChoiceGroupId`：

```typescript
export type AuthChoiceGroupId =
  // ... existing groups
  "kilocode";
// ...
```

添加到 `AUTH_CHOICE_GROUP_DEFS`：

```typescript
{
  value: "kilocode",
  label: "Kilo Gateway",
  hint: "API key (OpenRouter-compatible)",
  choices: ["kilocode-api-key"],
},
```

添加到 `buildAuthChoiceOptions()`：

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

### Auth Choice 应用

#### 8. `src/commands/auth-choice.apply.api-providers.ts`

添加导入：

```typescript
import {
  // ... existing imports
  applyKilocodeConfig,
  applyKilocodeProviderConfig,
  KILOCODE_DEFAULT_MODEL_REF,
  setKilocodeApiKey,
} from "./onboard-auth.js";
```

添加对 `kilocode-api-key` 的处理：

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

同时在函数顶部添加 tokenProvider 映射：

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

添加到 action handler：

```typescript
kilocodeApiKey: opts.kilocodeApiKey as string | undefined,
```

更新 auth-choice 帮助文本：

```typescript
.option(
  "--auth-choice <choice>",
  "Auth: setup-token|token|chutes|openai-codex|openai-api-key|openrouter-api-key|kilocode-api-key|ai-gateway-api-key|...",
)
```

### 非交互式引导

#### 10. `src/commands/onboard-non-interactive/local/auth-choice.ts`

添加对 `kilocode-api-key` 的处理：

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

添加导出：

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

添加 Kilo Gateway 处理（类似于 OpenRouter）：

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
   - 测试 `setKilocodeApiKey()` 写入正确的配置文件
   - 测试 `applyKilocodeConfig()` 设置正确的默认值
   - 测试 `resolveEnvApiKey("kilocode")` 返回正确的环境变量

2. **集成测试：**
   - 测试带有 `--auth-choice kilocode-api-key` 的引导流程
   - 测试带有 `--kilocode-api-key` 的非交互式引导
   - 测试带有 `kilocode/` 前缀的模型选择

3. **端到端测试：**
   - 测试通过 Kilo Gateway 的实际 API 调用（实时测试）

## 迁移说明

- 现有用户无需迁移
- 新用户可以立即使用 `kilocode-api-key` 认证选项
- 带有 `kilocode` 提供商的现有手动配置将继续有效

## 未来考虑

1. **模型目录：** 如果 Kilo Gateway 公开了 `/models` 端点，添加类似于 `scanOpenRouterModels()` 的扫描支持

2. **OAuth 支持：** 如果 Kilo Gateway 添加 OAuth，相应地扩展认证系统

3. **速率限制：** 如果需要，考虑添加特定于 Kilo Gateway 的速率限制处理

4. **文档：** 在 `docs/providers/kilocode.md` 添加文档以解释设置和用法

## 变更摘要

| 文件                                                        | 变更类型 | 描述                                                             |
| ----------------------------------------------------------- | ----------- | ----------------------------------------------------------------------- |
| `src/commands/onboard-auth.credentials.ts`                  | 添加         | `KILOCODE_DEFAULT_MODEL_REF`, `setKilocodeApiKey()`                     |
| `src/agents/model-auth.ts`                                  | 修改      | 向 `envMap` 添加 `kilocode`                                              |
| `src/config/io.ts`                                          | 修改      | 向 shell 环境变量键添加 `KILOCODE_API_KEY`                                |
| `src/commands/onboard-auth.config-core.ts`                  | 添加         | `applyKilocodeProviderConfig()`, `applyKilocodeConfig()`                |
| `src/commands/onboard-types.ts`                             | 修改      | 向 `AuthChoice` 添加 `kilocode-api-key`，向选项添加 `kilocodeApiKey` |
| `src/commands/auth-choice-options.ts`                       | 修改      | 添加 `kilocode` 组和选项                                         |
| `src/commands/auth-choice.preferred-provider.ts`            | 修改      | 添加 `kilocode-api-key` 映射                                          |
| `src/commands/auth-choice.apply.api-providers.ts`           | 修改      | 添加 `kilocode-api-key` 处理                                         |
| `src/cli/program/register.onboard.ts`                       | 修改      | 添加 `--kilocode-api-key` 选项                                         |
| `src/commands/onboard-non-interactive/local/auth-choice.ts` | 修改      | 添加非交互式处理                                            |
| `src/commands/onboard-auth.ts`                              | 修改      | 导出新函数                                                    |
| `src/agents/pi-embedded-runner/cache-ttl.ts`                | 修改      | 添加 kilocode 支持                                                    |
| `src/agents/transcript-policy.ts`                           | 修改      | 添加 kilocode Gemini 处理                                            |