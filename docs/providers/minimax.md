---
summary: "Use MiniMax M2.1 in OpenClaw"
read_when:
  - You want MiniMax models in OpenClaw
  - You need MiniMax setup guidance
title: "MiniMax"
---
# MiniMax

MiniMax 是一家构建 **M2/M2.1** 模型系列的 AI 公司。当前专注于编码的版本是 **MiniMax M2.1**（2025 年 12 月 23 日发布），专为现实世界的复杂任务设计。

来源：[MiniMax M2.1 发布说明](https://www.minimax.io/news/minimax-m21)

## 模型概述（M2.1）

MiniMax 在 M2.1 中突出了以下改进：

- 更强的 **多语言编程**（Rust、Java、Go、C++、Kotlin、Objective-C、TS/JS）。
- 更好的 **网页/应用开发** 和审美输出质量（包括原生移动应用）。
- 改进的 **复合指令处理**，适用于办公风格的工作流，基于交错思维和集成约束执行。
- **更简洁的响应**，使用更少的 token 且迭代循环更快。
- 更强的 **工具/代理框架** 兼容性与上下文管理（Claude Code、Droid/Factory AI、Cline、Kilo Code、Roo Code、BlackBox）。
- 更高质量的 **对话与技术写作** 输出。

## MiniMax M2.1 与 MiniMax M2.1 Lightning 的对比

- **速度**：Lightning 是 MiniMax 定价文档中的“快速”版本。
- **成本**：定价显示输入成本相同，但 Lightning 的输出成本更高。
- **编码计划路由**：Lightning 的后端不在 MiniMax 编码计划中直接可用。MiniMax 会自动将大多数请求路由到 Lightning，但在流量高峰时会回退到常规的 M2.1 后端。

## 选择配置方式

### MiniMax OAuth（编码计划）— 推荐

**最佳适用场景**：通过 OAuth 快速设置 MiniMax 编码计划，无需 API 密钥。

启用捆绑的 OAuth 插件并进行身份验证：

```bash
openclaw plugins enable minimax-portal-auth  # 如果已加载则跳过。
openclaw gateway restart  # 如果网关已运行则重启
openclaw onboard --auth-choice minimax-portal
```

您将被提示选择一个端点：

- **全球** - 国际用户 (`api.minimax.io`)
- **CN** - 中国用户 (`api.minimaxi.com`)

详情请参见 [MiniMax OAuth 插件 README](https://github.com/openclaw/openclaw/tree/main/extensions/minimax-portal-auth)。

### MiniMax M2.1（API 密钥）

**最佳适用场景**：使用与 Anthropic 兼容的 API 的托管 MiniMax。

通过 CLI 配置：

- 运行 `openclaw configure`
- 选择 **模型/认证**
- 选择 **MiniMax M2.1**

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "minimax/MiniMax-M2.1" } } },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.1",
            name: "MiniMax M2.1",
            reasoning: false,
            input: ["text"],
            cost: { input: 15, output: 60, cacheRead: 2, cacheWrite: 10 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### MiniMax M2.1 作为备用（Opus 主用）

**最佳适用场景**：保持 Opus 4.5 为主用，故障时切换到 MiniMax M2.1。

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-5": { alias: "opus" },
        "minimax/MiniMax-M2.1": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-5",
        fallbacks: ["minimax/MiniMax-M2.1"],
      },
    },
  },
}
```

### 可选：通过 LM Studio 本地（手动）

**最佳适用场景**：使用 LM Studio 进行本地推理。
我们在使用 LM Studio 的本地服务器时，看到 MiniMax M2.1 在强大硬件（如桌面/服务器）上取得了显著效果。

通过 `openclaw.json` 手动配置：

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/minimax-m2.1-gs32" },
      models: { "lmstudio/minimax-m2.1-gs32": { alias: "Minimax" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "minimax-m2.1-gs32",
            name: "MiniMax M2.1 GS32",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## 通过 `openclaw configure` 配置

使用交互式配置向导设置 MiniMax，无需编辑 JSON：

1. 运行 `openclaw configure`。
2. 选择 **模型/认证**。
3. 选择 **MiniMax M2.1**。
4. 在提示时选择默认模型。

## 配置选项

- `models.providers.minimax.baseUrl`：优先使用 `https://api.minimax.io/anthropic`（与 Anthropic 兼容）；`https://api.minimax.io/v1` 是可选的 OpenAI 兼容负载。
- `models.providers.minimax.api`：优先使用 `anthropic-messages`；`openai-completions` 是可选的 OpenAI 兼容负载。
- `models.providers.minimax.apiKey`：MiniMax API 密钥（`MINIM