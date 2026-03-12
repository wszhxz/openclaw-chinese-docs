---
summary: "Use MiniMax M2.5 in OpenClaw"
read_when:
  - You want MiniMax models in OpenClaw
  - You need MiniMax setup guidance
title: "MiniMax"
---
# MiniMax

MiniMax 是一家人工智能公司，致力于构建 **M2/M2.5** 模型系列。当前面向编程场景发布的版本是 **MiniMax M2.5**（2025 年 12 月 23 日发布），专为应对现实世界中的复杂任务而设计。

来源：[MiniMax M2.5 发布说明](https://www.minimax.io/news/minimax-m25)

## 模型概览（M2.5）

MiniMax 强调 M2.5 具备以下改进：

- 更强的**多语言编程能力**（Rust、Java、Go、C++、Kotlin、Objective-C、TS/JS）。
- 更优的**网页/应用开发能力**与美学输出质量（包括原生移动平台）。
- 改进的**复合指令处理能力**，适用于办公类工作流，在交错式思维与集成约束执行基础上进一步增强。
- **更简洁的响应**，降低 token 消耗，加快迭代循环速度。
- 更强的**工具/智能体框架兼容性**与上下文管理能力（支持 Claude Code、Droid/Factory AI、Cline、Kilo Code、Roo Code、BlackBox）。
- 更高质量的**对话与技术写作输出**。

## MiniMax M2.5 与 MiniMax M2.5 Highspeed 对比

- **速度：** `MiniMax-M2.5-highspeed` 是 MiniMax 官方文档中定义的快速推理层级。
- **成本：** MiniMax 定价页面显示，Highspeed 的输入费用与标准版相同，但输出费用更高。
- **当前模型 ID：** 使用 `MiniMax-M2.5` 或 `MiniMax-M2.5-highspeed`。

## 选择一种配置方式

### MiniMax OAuth（Coding Plan）——推荐方式

**最适合：** 通过 OAuth 快速接入 MiniMax Coding Plan，无需 API 密钥。

启用内置 OAuth 插件并完成身份验证：

```bash
openclaw plugins enable minimax-portal-auth  # skip if already loaded.
openclaw gateway restart  # restart if gateway is already running
openclaw onboard --auth-choice minimax-portal
```

系统将提示您选择端点：

- **Global** —— 面向国际用户 (`api.minimax.io`)
- **CN** —— 面向中国用户 (`api.minimaxi.com`)

详情请参阅 [MiniMax OAuth 插件 README](https://github.com/openclaw/openclaw/tree/main/extensions/minimax-portal-auth)。

### MiniMax M2.5（API 密钥方式）

**最适合：** 使用 Anthropic 兼容 API 托管的 MiniMax 服务。

通过 CLI 进行配置：

- 运行 `openclaw configure`
- 选择 **Model/auth**
- 选择 **MiniMax M2.5**

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "minimax/MiniMax-M2.5" } } },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: true,
            input: ["text"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.03, cacheWrite: 0.12 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
          {
            id: "MiniMax-M2.5-highspeed",
            name: "MiniMax M2.5 Highspeed",
            reasoning: true,
            input: ["text"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.03, cacheWrite: 0.12 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### MiniMax M2.5 作为备用模型（示例）

**最适合：** 将您最强的最新一代模型设为主模型，当其不可用时自动降级至 MiniMax M2.5。  
下方示例以 Opus 为主模型；请根据需要替换为您首选的最新一代主模型。

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "primary" },
        "minimax/MiniMax-M2.5": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.5"],
      },
    },
  },
}
```

### 可选：通过 LM Studio 本地运行（手动方式）

**最适合：** 使用 LM Studio 进行本地推理。  
我们在高性能硬件（例如台式机/服务器）上配合 LM Studio 的本地服务器运行 MiniMax M2.5 时，已观察到优异效果。

通过手动编辑 `openclaw.json` 进行配置：

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/minimax-m2.5-gs32" },
      models: { "lmstudio/minimax-m2.5-gs32": { alias: "Minimax" } },
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
            id: "minimax-m2.5-gs32",
            name: "MiniMax M2.5 GS32",
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

## 通过 `openclaw configure` 进行配置

使用交互式配置向导设置 MiniMax，无需手动编辑 JSON：

1. 运行 `openclaw configure`。
2. 选择 **Model/auth**。
3. 选择 **MiniMax M2.5**。
4. 在提示时选择您的默认模型。

## 配置选项

- `models.providers.minimax.baseUrl`：优先使用 `https://api.minimax.io/anthropic`（Anthropic 兼容格式）；`https://api.minimax.io/v1` 为可选，用于 OpenAI 兼容格式的请求负载。
- `models.providers.minimax.api`：优先使用 `anthropic-messages`；`openai-completions` 为可选，用于 OpenAI 兼容格式的请求负载。
- `models.providers.minimax.apiKey`：MiniMax API 密钥（`MINIMAX_API_KEY`）。
- `models.providers.minimax.models`：定义 `id`、`name`、`reasoning`、`contextWindow`、`maxTokens`、`cost`。
- `agents.defaults.models`：为白名单中希望启用的模型设置别名。
- `models.mode`：若您希望在保留内置模型的同时添加 MiniMax，请保持 `merge`。

## 注意事项

- 模型引用为 `minimax/<model>`。
- 推荐使用的模型 ID：`MiniMax-M2.5` 和 `MiniMax-M2.5-highspeed`。
- Coding Plan 使用接口：`https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains`（需提供 Coding Plan 密钥）。
- 若需精确追踪费用，请在 `models.json` 中更新定价参数。
- MiniMax Coding Plan 推荐链接（享 10% 折扣）：[https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
- 关于供应商规则，请参阅 [/concepts/model-providers](/concepts/model-providers)。
- 使用 `openclaw models list` 和 `openclaw models set minimax/MiniMax-M2.5` 切换模型。

## 故障排查

### “Unknown model: minimax/MiniMax-M2.5”

该错误通常表示 **MiniMax 提供商未正确配置**（既无 provider 条目，也未找到 MiniMax 认证配置文件或环境变量密钥）。此检测逻辑的修复已在 **2026.1.12** 版本中完成（撰写本文时尚未发布）。解决方法如下：

- 升级至 **2026.1.12**（或从源码运行 `main`），然后重启网关；
- 运行 `openclaw configure` 并选择 **MiniMax M2.5**；或
- 手动添加 `models.providers.minimax` 配置块；或
- 设置 `MINIMAX_API_KEY`（或配置 MiniMax 认证配置文件），以便自动注入 provider。

请确保模型 ID **区分大小写**：

- `minimax/MiniMax-M2.5`
- `minimax/MiniMax-M2.5-highspeed`

随后使用以下命令重新检查：

```bash
openclaw models list
```