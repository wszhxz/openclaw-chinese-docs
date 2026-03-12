---
summary: "Configure Moonshot K2 vs Kimi Coding (separate providers + keys)"
read_when:
  - You want Moonshot K2 (Moonshot Open Platform) vs Kimi Coding setup
  - You need to understand separate endpoints, keys, and model refs
  - You want copy/paste config for either provider
title: "Moonshot AI"
---
# 月之暗面 AI（Kimi）

月之暗面提供了与 OpenAI 兼容的 Kimi API。请配置该提供者，并将默认模型设为 `moonshot/kimi-k2.5`，或使用 Kimi Coding 并指定 `kimi-coding/k2p5`。

当前 Kimi K2 模型 ID：

<!-- markdownlint-disable MD037 -->

{/_ moonshot-kimi-k2-ids:start _/ && null}

<!-- markdownlint-enable MD037 -->

- `kimi-k2.5`
- `kimi-k2-0905-preview`
- `kimi-k2-turbo-preview`
- `kimi-k2-thinking`
- `kimi-k2-thinking-turbo`
  <!-- markdownlint-disable MD037 -->
  {/_ moonshot-kimi-k2-ids:end _/ && null}
  <!-- markdownlint-enable MD037 -->

```bash
openclaw onboard --auth-choice moonshot-api-key
```

Kimi Coding：

```bash
openclaw onboard --auth-choice kimi-code-api-key
```

注意：月之暗面与 Kimi Coding 是两个独立的提供者。密钥不可互换，端点不同，且模型引用也不同（月之暗面使用 `moonshot/...`，Kimi Coding 使用 `kimi-coding/...`）。

## 配置片段（月之暗面 API）

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: {
        // moonshot-kimi-k2-aliases:start
        "moonshot/kimi-k2.5": { alias: "Kimi K2.5" },
        "moonshot/kimi-k2-0905-preview": { alias: "Kimi K2" },
        "moonshot/kimi-k2-turbo-preview": { alias: "Kimi K2 Turbo" },
        "moonshot/kimi-k2-thinking": { alias: "Kimi K2 Thinking" },
        "moonshot/kimi-k2-thinking-turbo": { alias: "Kimi K2 Thinking Turbo" },
        // moonshot-kimi-k2-aliases:end
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          // moonshot-kimi-k2-models:start
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 256000,
            maxTokens: 8192,
          },
          {
            id: "kimi-k2-0905-preview",
            name: "Kimi K2 0905 Preview",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 256000,
            maxTokens: 8192,
          },
          {
            id: "kimi-k2-turbo-preview",
            name: "Kimi K2 Turbo",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 256000,
            maxTokens: 8192,
          },
          {
            id: "kimi-k2-thinking",
            name: "Kimi K2 Thinking",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 256000,
            maxTokens: 8192,
          },
          {
            id: "kimi-k2-thinking-turbo",
            name: "Kimi K2 Thinking Turbo",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 256000,
            maxTokens: 8192,
          },
          // moonshot-kimi-k2-models:end
        ],
      },
    },
  },
}
```

## Kimi Coding

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi-coding/k2p5" },
      models: {
        "kimi-coding/k2p5": { alias: "Kimi K2.5" },
      },
    },
  },
}
```

## 注意事项

- 月之暗面的模型引用使用 `moonshot/<modelId>`；Kimi Coding 的模型引用使用 `kimi-coding/<modelId>`。
- 如有需要，可在 `models.providers` 中覆盖定价和上下文元数据。
- 若月之暗面为某模型公布了不同的上下文长度限制，请相应调整 `contextWindow`。
- 国际端点请使用 `https://api.moonshot.ai/v1`，中国端点请使用 `https://api.moonshot.cn/v1`。

## 原生思维模式（月之暗面）

月之暗面 Kimi 支持二元原生思维模式：

- `thinking: { type: "enabled" }`
- `thinking: { type: "disabled" }`

可通过 `agents.defaults.models.<provider/model>.params` 按模型进行配置：

```json5
{
  agents: {
    defaults: {
      models: {
        "moonshot/kimi-k2.5": {
          params: {
            thinking: { type: "disabled" },
          },
        },
      },
    },
  },
}
```

OpenClaw 同时为月之暗面映射了运行时的 `/think` 级别：

- `/think off` → `thinking.type=disabled`
- 任意非 `off` 的思维级别 → `thinking.type=enabled`

当启用月之暗面思维模式时，`tool_choice` 必须为 `auto` 或 `none`。为确保兼容性，OpenClaw 会将不兼容的 `tool_choice` 值标准化为 `auto`。