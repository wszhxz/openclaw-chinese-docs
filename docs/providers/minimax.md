---
summary: "Use MiniMax M2.1 in OpenClaw"
read_when:
  - You want MiniMax models in OpenClaw
  - You need MiniMax setup guidance
title: "MiniMax"
---
# MiniMax

MiniMax 是一家AI公司，构建了 **M2/M2.1** 模型系列。当前面向编码的发布版本是 **MiniMax M2.1**（2025年12月23日），专为现实世界复杂任务设计。

来源：[MiniMax M2.1 发布说明](https://www.minimax.io/news/minimax-m21)

## 模型概述 (M2.1)

MiniMax 在 M2.1 中强调了这些改进：

- 更强的 **多语言编码**（Rust, Java, Go, C++, Kotlin, Objective-C, TS/JS）。
- 更好的 **Web/App 开发** 和美学输出质量（包括原生移动应用）。
- 改进的 **复合指令** 处理能力，适用于办公风格的工作流，基于交错思维和集成约束执行。
- 更简洁的响应，使用更少的标记和更快的迭代循环。
- 更强的 **工具/代理框架** 兼容性和上下文管理（Claude Code, Droid/Factory AI, Cline, Kilo Code, Roo Code, BlackBox）。
- 更高质量的 **对话和技术写作** 输出。

## MiniMax M2.1 与 MiniMax M2.1 Lightning

- **速度：** Lightning 是 MiniMax 定价文档中的“快速”变体。
- **成本：** 定价显示相同的输入成本，但 Lightning 的输出成本更高。
- **编码计划路由：** Lightning 后端不在 MiniMax 编码计划中直接可用。MiniMax 自动将大多数请求路由到 Lightning，但在流量高峰期间会回退到常规的 M2.1 后端。

## 选择设置

### MiniMax OAuth（编码计划）—— 推荐

**适用场景：** 通过 OAuth 快速设置 MiniMax 编码计划，无需 API 密钥。

启用捆绑的 OAuth 插件并进行身份验证：

```bash
openclaw plugins enable minimax-portal-auth  # skip if already loaded.
openclaw gateway restart  # restart if gateway is already running
openclaw onboard --auth-choice minimax-portal
```

您将被提示选择一个端点：

- **Global** - 国际用户 (`api.minimax.io`)
- **CN** - 中国用户 (`api.minimaxi.com`)

详情请参阅 [MiniMax OAuth 插件 README](https://github.com/openclaw/openclaw/tree/main/extensions/minimax-portal-auth)。

### MiniMax M2.1（API 密钥）

**适用场景：** 使用与 Anthropic 兼容的 API 托管 MiniMax。

通过 CLI 配置：

- 运行 `openclaw configure`
- 选择 **Model/auth**
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

### MiniMax M2.1 作为备用（Opus 主要）

**适用场景：** 将 Opus 4.5 作为主要模型，失败时切换到 MiniMax M2.1。

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

### 可选：本地通过 LM Studio（手动）

**适用场景：** 使用 LM Studio 进行本地推理。
我们在强大的硬件（例如桌面/服务器）上使用 LM Studio 的本地服务器运行 MiniMax M2.1 时获得了很好的结果。

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

使用交互式配置向导设置 MiniMax 而无需编辑 JSON：

1. 运行 `openclaw configure`。
2. 选择 **Model/auth**。
3. 选择 **MiniMax M2.1**。
4. 根据提示选择默认模型。

## 配置选项

- `models.providers.minimax.baseUrl`: 偏好 `https://api.minimax.io/anthropic`（与 Anthropic 兼容）；`https://api.minimax.io/v1` 对于与 OpenAI 兼容的有效负载是可选的。
- `models.providers.minimax.api`: 偏好 `anthropic-messages`；`openai-completions` 对于与 OpenAI 兼容的有效负载是可选的。
- `models.providers.minimax.apiKey`: MiniMax API 密钥 (`MINIMAX_API_KEY`)。
- `models.providers.minimax.models`: 定义 `id`, `name`, `reasoning`, `contextWindow`, `maxTokens`, `cost`。
- `agents.defaults.models`: 将您希望列入白名单的模型别名。
- `models.mode`: 如果您想将 MiniMax 与内置模型一起使用，请保留 `merge`。

## 注意事项

- 模型引用是 `minimax/<model>`。
- 编码计划使用 API: `https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains`（需要编码计划密钥）。
- 如果需要精确的成本跟踪，请在 `models.json` 中更新定价值。
- MiniMax 编码计划推荐链接（10% 折扣）：https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link
- 查看 [/concepts/model-providers](/concepts/model-providers) 了解提供商规则。
- 使用 `openclaw models list` 和 `openclaw models set minimax/MiniMax-M2.1` 切换。

## 故障排除

### “未知模型: minimax/MiniMax-M2.1”

这通常意味着 **MiniMax 提供商未配置**（没有提供商条目且未找到 MiniMax 认证配置文件/环境密钥）。此检测的修复将在 **2026.1.12** 中（撰写时未发布）。修复方法如下：

- 升级到 **2026.1.12**（或从源代码运行 `main`），然后重启网关。
- 运行 `openclaw configure` 并选择 **MiniMax M2.1**，或
- 手动添加 `models.providers.minimax` 块，或
- 设置 `MINIMAX_API_KEY`（或 MiniMax 认证配置文件）以便注入提供商。

确保模型 ID 是 **区分大小写** 的：

- `minimax/MiniMax-M2.1`
- `minimax/MiniMax-M2.1-lightning`

然后重新检查：

```bash
openclaw models list
```