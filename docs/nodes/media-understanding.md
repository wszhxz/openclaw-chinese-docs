---
summary: "Inbound image/audio/video understanding (optional) with provider + CLI fallbacks"
read_when:
  - Designing or refactoring media understanding
  - Tuning inbound audio/video/image preprocessing
title: "Media Understanding"
---
# 媒体理解 - 入站 (2026-01-17)

OpenClaw 可以在回复流水线运行前 **总结入站媒体**（图像/音频/视频）。它会自动检测本地工具或提供商密钥是否可用，并且可以禁用或自定义。如果理解功能关闭，模型仍会像往常一样接收原始文件/URL。

特定于厂商的媒体行为由厂商插件注册，而 OpenClaw 核心拥有共享的 `tools.media` 配置、回退顺序和回复流水线集成。

## 目标

- 可选：将入站媒体预消化为短文本，以实现更快的路由 + 更好的命令解析。
- 始终保留原始媒体交付给模型。
- 支持 **提供商 API** 和 **CLI 回退**。
- 允许使用有序回退（错误/大小/超时）的多个模型。

## 高级行为

1. 收集入站附件（`MediaPaths`, `MediaUrls`, `MediaTypes`）。
2. 对于每个启用的能力（图像/音频/视频），按策略选择附件（默认：**第一个**）。
3. 选择第一个合格的模型条目（大小 + 能力 + 认证）。
4. 如果模型失败或媒体太大，**回退到下一个条目**。
5. 成功时：
   - `Body` 变为 `[Image]`、`[Audio]` 或 `[Video]` 块。
   - 音频设置 `{{Transcript}}`；命令解析使用字幕文本（如果存在），否则使用转录文本。
   - 字幕作为 `User text:` 保留在块内。

如果理解失败或已禁用，**回复流程将继续**，使用原始正文 + 附件。

## 配置概览

`tools.media` 支持 **共享模型** 以及每能力覆盖：

- `tools.media.models`: 共享模型列表（使用 `capabilities` 进行门控）。
- `tools.media.image` / `tools.media.audio` / `tools.media.video`:
  - 默认值 (`prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`)
  - 提供商覆盖 (`baseUrl`, `headers`, `providerOptions`)
  - 通过 `tools.media.audio.providerOptions.deepgram` 的 Deepgram 音频选项
  - 音频转录回声控制 (`echoTranscript`，默认 `false`; `echoFormat`)
  - 可选的 **每能力 `models` 列表**（在共享模型之前首选）
  - `attachments` 策略 (`mode`, `maxAttachments`, `prefer`)
  - `scope`（可选的门控，按频道/聊天类型/会话键）
- `tools.media.concurrency`: 最大并发能力运行次数（默认 **2**）。

```json5
{
  tools: {
    media: {
      models: [
        /* shared list */
      ],
      image: {
        /* optional overrides */
      },
      audio: {
        /* optional overrides */
        echoTranscript: true,
        echoFormat: '📝 "{transcript}"',
      },
      video: {
        /* optional overrides */
      },
    },
  },
}
```

### 模型条目

每个 `models[]` 条目可以是 **提供商** 或 **CLI**：

```json5
{
  type: "provider", // default if omitted
  provider: "openai",
  model: "gpt-5.4-mini",
  prompt: "Describe the image in <= 500 chars.",
  maxChars: 500,
  maxBytes: 10485760,
  timeoutSeconds: 60,
  capabilities: ["image"], // optional, used for multi‑modal entries
  profile: "vision-profile",
  preferredProfile: "vision-fallback",
}
```

```json5
{
  type: "cli",
  command: "gemini",
  args: [
    "-m",
    "gemini-3-flash",
    "--allowed-tools",
    "read_file",
    "Read the media at {{MediaPath}} and describe it in <= {{MaxChars}} characters.",
  ],
  maxChars: 500,
  maxBytes: 52428800,
  timeoutSeconds: 120,
  capabilities: ["video", "image"],
}
```

CLI 模板也可以使用：

- `{{MediaDir}}`（包含媒体文件的目录）
- `{{OutputDir}}`（为此运行创建的临时目录）
- `{{OutputBase}}`（临时文件基础路径，无扩展名）

## 默认值和限制

推荐默认值：

- `maxChars`: **500**（用于图像/视频，简短，适合命令）
- `maxChars`: **未设置**（用于音频，完整转录，除非你设置了限制）
- `maxBytes`:
  - 图像：**10MB**
  - 音频：**20MB**
  - 视频：**50MB**

规则：

- 如果媒体超过 `maxBytes`，则跳过该模型并**尝试下一个模型**。
- 小于 **1024 字节** 的音频文件被视为空/损坏，并在提供商/CLI 转录之前跳过。
- 如果模型返回多于 `maxChars`，输出将被修剪。
- `prompt` 默认为简单的“描述{media}。”加上 `maxChars` 指导（仅限图像/视频）。
- 如果活动的主图像模型已经原生支持视觉，OpenClaw 将跳过 `[Image]` 摘要块，并将原始图像传递给模型。
- 如果 `<capability>.enabled: true` 但未配置任何模型，当提供商支持该能力时，OpenClaw 会尝试**活动回复模型**。

### 自动检测媒体理解（默认）

如果 `tools.media.<capability>.enabled` 未设置为 `false` 且你尚未配置模型，OpenClaw 将按此顺序自动检测，并在第一个可行选项处停止：

1. **活动回复模型**，当其提供商支持该能力时。
2. **`agents.defaults.imageModel`** 主/回退引用（仅限图像）。
3. **本地 CLI**（仅限音频；如果已安装）
   - `sherpa-onnx-offline`（需要带有编码器/解码器/拼接器/令牌的 `SHERPA_ONNX_MODEL_DIR`）
   - `whisper-cli`（`whisper-cpp`; 使用 `WHISPER_CPP_MODEL` 或捆绑的微型模型）
   - `whisper`（Python CLI；自动下载模型）
4. **Gemini CLI**（`gemini`）使用 `read_many_files`
5. **提供商认证**
   - 配置的支持该能力的 `models.providers.*` 条目在捆绑回退顺序之前尝试。
   - 具有图像能力模型的仅图像配置提供商即使不是捆绑的厂商插件也会自动注册媒体理解。
   - 捆绑回退顺序：
     - 音频：OpenAI → Groq → Deepgram → Google → Mistral
     - 图像：OpenAI → Anthropic → Google → MiniMax → MiniMax Portal → Z.AI
     - 视频：Google → Qwen → Moonshot

要禁用自动检测，请设置：

```json5
{
  tools: {
    media: {
      audio: {
        enabled: false,
      },
    },
  },
}
```

注意：二进制检测在 macOS/Linux/Windows 上是尽力而为的；确保 CLI 在 `PATH` 中（我们会扩展 `~`），或者设置一个带有完整命令路径的显式 CLI 模型。

### 代理环境支持（提供商模型）

当启用基于提供商的 **音频** 和 **视频** 媒体理解时，OpenClaw 遵守用于提供商 HTTP 调用的标准出站代理环境变量：

- `HTTPS_PROXY`
- `HTTP_PROXY`
- `https_proxy`
- `http_proxy`

如果未设置代理环境变量，媒体理解使用直接出口。如果代理值格式错误，OpenClaw 记录警告并回退到直接获取。

## 能力（可选）

如果你设置 `capabilities`，该条目仅针对这些媒体类型运行。对于共享列表，OpenClaw 可以推断默认值：

- `openai`, `anthropic`, `minimax`: **图像**
- `minimax-portal`: **图像**
- `moonshot`: **图像 + 视频**
- `openrouter`: **图像**
- `google`（Gemini API）: **图像 + 音频 + 视频**
- `qwen`: **图像 + 视频**
- `mistral`: **音频**
- `zai`: **图像**
- `groq`: **音频**
- `deepgram`: **音频**
- 任何带有图像能力模型的 `models.providers.<id>.models[]` 目录：
  **图像**

对于 CLI 条目，**显式设置 `capabilities`** 以避免意外匹配。如果你省略 `capabilities`，该条目有资格出现在其所在的列表中。

## 提供商支持矩阵（OpenClaw 集成）

| 能力 | 提供商集成 | 备注 |
| ---------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 图像 | OpenAI, OpenRouter, Anthropic, Google, MiniMax, Moonshot, Qwen, Z.AI, 配置提供商 | 厂商插件注册图像支持；MiniMax 和 MiniMax OAuth 都使用 `MiniMax-VL-01`；图像能力配置提供商自动注册。 |
| 音频 | OpenAI, Groq, Deepgram, Google, Mistral | 提供商转录（Whisper/Deepgram/Gemini/Voxtral）。 |
| 视频 | Google, Qwen, Moonshot | 通过厂商插件进行提供商视频理解；Qwen 视频理解使用标准 DashScope 端点。 |

MiniMax 说明：

- `minimax` 和 `minimax-portal` 图像理解来自插件拥有的 `MiniMax-VL-01` 媒体提供商。
- 捆绑的 MiniMax 文本目录仍以纯文本开始；显式 `models.providers.minimax` 条目实现图像能力的 M2.7 聊天引用。

## 模型选择指南

- 当质量和安全很重要时，优先选择可用的每种媒体能力的最强最新一代模型。
- 对于处理不受信任输入的工具启用代理，避免使用较旧/较弱媒体模型。
- 每种能力至少保留一个回退以保证可用性（质量模型 + 更快/更便宜模型）。
- CLI 回退（`whisper-cli`, `whisper`, `gemini`）在提供商 API 不可用时很有用。
- `parakeet-mlx` 说明：带有 `--output-dir`，当输出格式为 `<output-dir>/<media-basename>.txt`（或未指定）时，OpenClaw 读取 `txt`；非 `txt` 格式回退到标准输出。

## 附件策略

每能力 `attachments` 控制处理哪些附件：

- `mode`: `first`（默认）或 `all`
- `maxAttachments`: 限制处理的数量（默认 **1**）
- `prefer`: `first`, `last`, `path`, `url`

当 `mode: "all"`，输出被标记为 `[Image 1/2]`, `[Audio 2/2]` 等。

文件附件提取行为：

- 提取的文件文本在追加到媒体提示之前会被包裹为 **不可信的外部内容**。
- 注入的块使用明确的边界标记，例如 `<<<EXTERNAL_UNTRUSTED_CONTENT id="...">>>` / `<<<END_EXTERNAL_UNTRUSTED_CONTENT id="...">>>`，并包含一个 `Source: External` 元数据行。
- 此附件提取路径有意省略了长的 `SECURITY NOTICE:` 横幅，以避免媒体提示臃肿；边界标记和元数据仍然保留。
- 如果文件没有可提取的文本，OpenClaw 会注入 `[No extractable text]`。
- 如果 PDF 在此路径中回退到渲染后的页面图像，媒体提示将保留占位符 `[PDF content rendered to images; images not forwarded to model]`，因为此附件提取步骤转发的是文本块，而不是渲染后的 PDF 图像。

## 配置示例

### 1) 共享模型列表 + 覆盖项

```json5
{
  tools: {
    media: {
      models: [
        { provider: "openai", model: "gpt-5.4-mini", capabilities: ["image"] },
        {
          provider: "google",
          model: "gemini-3-flash-preview",
          capabilities: ["image", "audio", "video"],
        },
        {
          type: "cli",
          command: "gemini",
          args: [
            "-m",
            "gemini-3-flash",
            "--allowed-tools",
            "read_file",
            "Read the media at {{MediaPath}} and describe it in <= {{MaxChars}} characters.",
          ],
          capabilities: ["image", "video"],
        },
      ],
      audio: {
        attachments: { mode: "all", maxAttachments: 2 },
      },
      video: {
        maxChars: 500,
      },
    },
  },
}
```

### 2) 仅音频 + 视频（图像关闭）

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          {
            type: "cli",
            command: "whisper",
            args: ["--model", "base", "{{MediaPath}}"],
          },
        ],
      },
      video: {
        enabled: true,
        maxChars: 500,
        models: [
          { provider: "google", model: "gemini-3-flash-preview" },
          {
            type: "cli",
            command: "gemini",
            args: [
              "-m",
              "gemini-3-flash",
              "--allowed-tools",
              "read_file",
              "Read the media at {{MediaPath}} and describe it in <= {{MaxChars}} characters.",
            ],
          },
        ],
      },
    },
  },
}
```

### 3) 可选图像理解

```json5
{
  tools: {
    media: {
      image: {
        enabled: true,
        maxBytes: 10485760,
        maxChars: 500,
        models: [
          { provider: "openai", model: "gpt-5.4-mini" },
          { provider: "anthropic", model: "claude-opus-4-6" },
          {
            type: "cli",
            command: "gemini",
            args: [
              "-m",
              "gemini-3-flash",
              "--allowed-tools",
              "read_file",
              "Read the media at {{MediaPath}} and describe it in <= {{MaxChars}} characters.",
            ],
          },
        ],
      },
    },
  },
}
```

### 4) 多模态单入口（显式能力）

```json5
{
  tools: {
    media: {
      image: {
        models: [
          {
            provider: "google",
            model: "gemini-3.1-pro-preview",
            capabilities: ["image", "video", "audio"],
          },
        ],
      },
      audio: {
        models: [
          {
            provider: "google",
            model: "gemini-3.1-pro-preview",
            capabilities: ["image", "video", "audio"],
          },
        ],
      },
      video: {
        models: [
          {
            provider: "google",
            model: "gemini-3.1-pro-preview",
            capabilities: ["image", "video", "audio"],
          },
        ],
      },
    },
  },
}
```

## 状态输出

当媒体理解运行时，`/status` 包含一行简短摘要：

```
📎 Media: image ok (openai/gpt-5.4-mini) · audio skipped (maxBytes)
```

这显示了各能力的结果以及适用的选定提供者/模型。

## 注意

- 理解是 **尽力而为** 的。错误不会阻止回复。
- 即使禁用理解，附件仍会传递给模型。
- 使用 `scope` 限制理解运行的位置（例如仅限 DMs）。

## 相关文档

- [配置](/gateway/configuration)
- [图像与媒体支持](/nodes/images)