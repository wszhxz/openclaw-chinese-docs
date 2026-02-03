---
summary: "Use Venice AI privacy-focused models in OpenClaw"
read_when:
  - You want privacy-focused inference in OpenClaw
  - You want Venice AI setup guidance
title: "Venice AI"
---
# 威尼斯AI（威尼斯亮点）

**威尼斯**是我们针对隐私优先推理的亮点设置，支持可选的匿名化访问专有模型。

威尼斯AI提供隐私导向的AI推理，支持无审查模型，并通过其匿名化代理访问主要的专有模型。所有推理默认私密——不使用您的数据进行训练，不记录日志。

## 为什么选择威尼斯在OpenClaw中

- **私密推理**用于开源模型（无日志记录）。
- **无审查模型**在您需要时使用。
- **匿名化访问**专有模型（Opus/GPT/Gemini）在质量重要时使用。
- OpenAI兼容的`/v1`端点。

## 隐私模式

威尼斯提供两种隐私级别——理解这一点对于选择您的模型至关重要：

| 模式           | 描述                         | 模型                                         |
| -------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| **私密**       | 完全私密。提示/响应**从不存储或记录**。瞬时。                                          | Llama, Qwen, DeepSeek, Venice无审查等。 |
| **匿名化**     | 通过威尼斯代理，元数据被剥离。底层提供者（OpenAI, Anthropic）看到匿名请求。 | Claude, GPT, Gemini, Grok, Kimi, MiniMax       |

## 功能

- **隐私导向**：在“私密”（完全私密）和“匿名化”（代理）模式之间选择
- **无审查模型**：访问无内容限制的模型
- **主要模型访问**：通过威尼斯的匿名化代理使用Claude, GPT-5.2, Gemini, Grok
- **OpenAI兼容API**：标准`/v1`端点，便于集成
- **流式传输**：✅ 所有模型均支持
- **函数调用**：✅ 选择模型支持（检查模型能力）
- **视觉**：✅ 视觉能力模型支持
- **无硬性速率限制**：极端使用时可能应用公平使用限制

## 设置

### 1. 获取API密钥

1. 在[venice.ai](https://venice.ai)注册
2. 前往**设置 → API密钥 → 创建新密钥**
3. 复制您的API密钥（格式：`vapi_xxxxxxxxxxxx`）

### 2. 配置OpenClaw

**选项A：环境变量**

```bash
export VENICE_API_KEY="vapi_xxxxxxxxxxxx"
```

**选项B：交互式设置（推荐）**

```bash
openclaw models list
```

**选项C：静态配置文件**

```json5
{
  "env": { "VENICE_API_KEY": "vapi_..." },
  "agents": { "defaults": { "model": { "primary": "venice/llama-3.3-70b" } } },
  "models": {
    "mode": "merge",
    "providers": {
      "venice": {
        "baseUrl": "https://api.venice.ai/api/v1",
        "apiKey": "${VENICE_API_KEY}",
        "api": "openai-completions",
        "models": [
          {
            "id": "llama-3.3-70b",
            "name": "Llama 3.3 70B",
            "reasoning": false,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 131072,
            "maxTokens": 8192,
          },
        ],
      },
    },
  },
}
```

### 3. 验证配置

```bash
echo $VENICE_API_KEY
openclaw models list | grep venice
```

确保密钥以`vapi_`开头。

## 模型发现

当`VENICE_API_KEY`设置时，OpenClaw会自动从威尼斯API发现模型。如果API不可达，将回退到静态目录。

`/models`端点是公开的（无需认证即可列出），但推理需要有效的API密钥。

## 流式传输与工具支持

| 功能              | 支持                                                 |
| -------------------- | ------------------------------------------------------- |
| **流式传输**        | ✅ 所有模型                                           |
| **函数调用**        | ✅ 大多数模型（检查API中的`supportsFunctionCalling`） |
| **视觉/图像**       | ✅ 标记为“视觉”功能的模型                            |
| **JSON模式**        | ✅ 通过`response_format`支持                         |

## 价格

威尼斯使用信用系统。查看[venice.ai/pricing](https://venice.ai/pricing)获取当前价格：

- **私密模型**：通常成本较低
- **匿名化模型**：与直接API定价相似 + 小额威尼斯费用

## 比较：威尼斯 vs 直接API

| 方面       | 威尼斯（匿名化）           | 直接API          |
| ------------ | ----------------------------- | ------------------- |
| **隐私**  | 元数据被剥离，匿名化 | 您的账户链接 |
| **延迟**  | +10-50ms（代理）              | 直接              |
| **功能** | 大多数功能支持       | 全部功能       |
| **计费**  | 威尼斯信用                | 提供商计费    |

## 使用示例

```bash
# 使用默认私密模型
openclaw chat --model venice/llama-3.3-70b

# 通过威尼斯使用Claude（匿名化）
openclaw chat --model venice/claude-opus-45

# 使用无审查模型
openclaw chat --model venice/venice-uncensored

# 使用带图像的视觉模型
openclaw chat --model venice/qwen3-vl-235b-a22b

# 使用编码模型
openclab chat --model venice/qwen3-coder-480b-a35b-instruct
```

## 故障排除

### API密钥未被识别

```bash
echo $VENICE_API_KEY
openclaw models list | grep venice
```

确保密钥以`vapi_`开头。

### 模型不可用

威尼斯模型目录动态更新。运行`openclab models list`查看当前可用模型。某些模型可能暂时离线。

### 连接问题

威尼斯API位于`https://api.venice.ai/api/v1`。确保您的网络允许HTTPS连接。

## 配置文件示例

```json5
{
  "env": { "VEN