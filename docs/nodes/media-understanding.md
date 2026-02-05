---
summary: "Inbound image/audio/video understanding (optional) with provider + CLI fallbacks"
read_when:
  - Designing or refactoring media understanding
  - Tuning inbound audio/video/image preprocessing
title: "Media Understanding"
---
# 媒体理解（入站）— 2026-01-17

OpenClaw 可以在回复流水线运行之前**总结入站媒体**（图像/音频/视频）。当本地工具或提供商密钥可用时，它会自动检测，并且可以禁用或自定义。如果理解功能关闭，模型仍然像往常一样接收原始文件/URL。

## 目标

- 可选：将入站媒体预消化为短文本，以实现更快的路由和更好的命令解析。
- 保留原始媒体传递给模型（始终如此）。
- 支持**提供商 API** 和**CLI 回退**。
- 允许多个模型按顺序回退（错误/大小/超时）。

## 高级行为

1. 收集入站附件（`MediaPaths`、`MediaUrls`、`MediaTypes`）。
2. 对于每个启用的功能（图像/音频/视频），根据策略选择附件（默认：**第一个**）。
3. 选择第一个符合条件的模型条目（大小 + 功能 + 认证）。
4. 如果模型失败或媒体太大，**回退到下一个条目**。
5. 成功时：
   - `Body` 变为 `[Image]`、`[Audio]` 或 `[Video]` 块。
   - 音频设置 `{{Transcript}}`；命令解析使用字幕文本（如果存在），
     否则使用转录文本。
   - 字幕作为 `User text:` 保留在块内。

如果理解失败或被禁用，**回复流程继续**使用原始正文 + 附件。

## 配置概览

`tools.media` 支持**共享模型**加上每功能覆盖：

- `tools.media.models`：共享模型列表（使用 `capabilities` 进行控制）。
- `tools.media.image` / `tools.media.audio` / `tools.media.video`：
  - 默认值（`prompt`、`maxChars`、`maxBytes`、`timeoutSeconds`、`language`）
  - 提供商覆盖（`baseUrl`、`headers`、`providerOptions`）
  - 通过 `tools.media.audio.providerOptions.deepgram` 的 Deepgram 音频选项
  - 可选的**每功能 `models` 列表**（在共享模型之前优先）
  - `attachments` 策略（`mode`、`maxAttachments`、`prefer`）
  - `scope`（可选的按频道/chatType/会话键控制）
- `tools.media.concurrency`：最大并发功能运行数（默认 **2**）。

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
      },
      video: {
        /* optional overrides */
      },
    },
  },
}
```

### 模型条目

每个 `models[]` 条目可以是**提供商**或**CLI**：

```json5
{
  type: "provider", // default if omitted
  provider: "openai",
  model: "gpt-5.2",
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

CLI 模板还可以使用：

- `{{MediaDir}}`（包含媒体文件的目录）
- `{{OutputDir}}`（为此运行创建的临时目录）
- `{{OutputBase}}`（临时文件基础路径，无扩展名）

## 默认值和限制

推荐的默认值：

- `maxChars`：**500** 用于图像/视频（简短，命令行友好）
- `maxChars`：**未设置** 用于音频（完整转录，除非您设置了限制）
- `maxBytes`：
  - 图像：**10MB**
  - 音频：**20MB**
  - 视频：**50MB**

规则：

- 如果媒体超过 `maxBytes`，该模型将被跳过并**尝试下一个模型**。
- 如果模型返回超过 `maxChars`，输出将被裁剪。
- `prompt` 默认为简单的"描述这个{media}。"加上 `maxChars` 指导（仅图像/视频）。
- 如果 `<capability>.enabled: true` 但没有配置模型，当其提供者支持该功能时，OpenClaw 会尝试**活动回复模型**。

### 自动检测媒体理解（默认）

如果 `tools.media.<capability>.enabled` **不** 设置为 `false` 并且您没有
配置模型，OpenClaw 按此顺序自动检测并**在第一个工作选项处停止**：

1. **本地 CLI**（仅音频；如果已安装）
   - `sherpa-onnx-offline`（需要 `SHERPA_ONNX_MODEL_DIR` 带编码器/解码器/连接器/标记）
   - `whisper-cli`（`whisper-cpp`；使用 `WHISPER_CPP_MODEL` 或捆绑的小型模型）
   - `whisper`（Python CLI；自动下载模型）
2. **Gemini CLI**（`gemini`）使用 `read_many_files`
3. **提供者密钥**
   - 音频：OpenAI → Groq → Deepgram → Google
   - 图像：OpenAI → Anthropic → Google → MiniMax
   - 视频：Google

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

注意：二进制检测在 macOS/Linux/Windows 上是尽力而为的；确保 CLI 在 `PATH` 上（我们展开 `~`），或者使用完整命令路径设置明确的 CLI 模型。

## 功能（可选）

如果您设置了 `capabilities`，条目仅针对那些媒体类型运行。对于共享
列表，OpenClaw 可以推断默认值：

- `openai`、`anthropic`、`minimax`：**图像**
- `google`（Gemini API）：**图像 + 音频 + 视频**
- `groq`：**音频**
- `deepgram`：**音频**

对于 CLI 条目，**明确设置 `capabilities`** 以避免意外匹配。
如果您省略 `capabilities`，该条目适用于它出现的列表。

## 提供者支持矩阵（OpenClaw 集成）

| 功能       | 提供商集成                                       | 备注                                              |
| ---------- | ------------------------------------------------ | ------------------------------------------------- |
| 图像       | OpenAI / Anthropic / Google / 其他通过 `pi-ai` | 注册表中的任何支持图像的模型都可工作。            |
| 音频       | OpenAI, Groq, Deepgram, Google                   | 提供商转录（Whisper/Deepgram/Gemini）。           |
| 视频       | Google (Gemini API)                              | 提供商视频理解。                                  |

## 推荐的提供商

**图像**

- 如果当前模型支持图像，请优先使用。
- 良好的默认值：`openai/gpt-5.2`, `anthropic/claude-opus-4-5`, `google/gemini-3-pro-preview`。

**音频**

- `openai/gpt-4o-mini-transcribe`, `groq/whisper-large-v3-turbo`, 或 `deepgram/nova-3`。
- CLI 回退：`whisper-cli` (whisper-cpp) 或 `whisper`。
- Deepgram 设置：[Deepgram（音频转录）](/providers/deepgram)。

**视频**

- `google/gemini-3-flash-preview` (快速)，`google/gemini-3-pro-preview` (更丰富)。
- CLI 回退：`gemini` CLI (在视频/音频上支持 `read_file`)。

## 附件策略

按功能的 `attachments` 控制处理哪些附件：

- `mode`: `first` (默认) 或 `all`
- `maxAttachments`: 限制处理的数量（默认为 **1**）
- `prefer`: `first`, `last`, `path`, `url`

当 `mode: "all"` 时，输出被标记为 `[Image 1/2]`, `[Audio 2/2]` 等。

## 配置示例

### 1) 共享模型列表 + 覆盖

```json5
{
  tools: {
    media: {
      models: [
        { provider: "openai", model: "gpt-5.2", capabilities: ["image"] },
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

### 2) 仅音频 + 视频（关闭图像）

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

### 3) 可选的图像理解

```json5
{
  tools: {
    media: {
      image: {
        enabled: true,
        maxBytes: 10485760,
        maxChars: 500,
        models: [
          { provider: "openai", model: "gpt-5.2" },
          { provider: "anthropic", model: "claude-opus-4-5" },
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

### 4) 多模态单一入口（显式功能）

```json5
{
  tools: {
    media: {
      image: {
        models: [
          {
            provider: "google",
            model: "gemini-3-pro-preview",
            capabilities: ["image", "video", "audio"],
          },
        ],
      },
      audio: {
        models: [
          {
            provider: "google",
            model: "gemini-3-pro-preview",
            capabilities: ["image", "video", "audio"],
          },
        ],
      },
      video: {
        models: [
          {
            provider: "google",
            model: "gemini-3-pro-preview",
            capabilities: ["image", "video", "audio"],
          },
        ],
      },
    },
  },
}
```

## 状态输出

当媒体理解运行时，`/status` 包含一个简短的摘要行：

```
📎 Media: image ok (openai/gpt-5.2) · audio skipped (maxBytes)
```

这显示了每个功能的结果以及适用时选择的提供程序/模型。

## 注意事项

- 理解是**尽力而为**的。错误不会阻止回复。
- 即使禁用了理解功能，附件仍会传递给模型。
- 使用 `scope` 来限制理解运行的位置（例如仅限私信）。

## 相关文档

- [配置](/gateway/configuration)
- [图像和媒体支持](/nodes/images)