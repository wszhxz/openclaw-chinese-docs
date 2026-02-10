---
summary: "Inbound image/audio/video understanding (optional) with provider + CLI fallbacks"
read_when:
  - Designing or refactoring media understanding
  - Tuning inbound audio/video/image preprocessing
title: "Media Understanding"
---
# 媒体理解（入站） — 2026-01-17

OpenClaw可以在回复管道运行之前**总结入站媒体**（图像/音频/视频）。它会自动检测本地工具或提供商密钥是否可用，并且可以被禁用或自定义。如果理解功能关闭，模型仍然会像往常一样接收原始文件/URL。

## 目标

- 可选：预先将入站媒体摘要成短文本以加快路由速度并提高命令解析质量。
- 保留对模型的原始媒体传递（始终如此）。
- 支持**提供商API**和**CLI回退**。
- 允许多个模型按顺序回退（错误/大小/超时）。

## 高层次行为

1. 收集入站附件 (`MediaPaths`, `MediaUrls`, `MediaTypes`)。
2. 对于每个启用的功能（图像/音频/视频），根据策略选择附件（默认：**第一个**）。
3. 选择第一个符合条件的模型条目（大小 + 功能 + 认证）。
4. 如果模型失败或媒体太大，**回退到下一个条目**。
5. 成功时：
   - `Body` 变成 `[Image]`, `[Audio]`, 或 `[Video]` 块。
   - 音频设置 `{{Transcript}}`；命令解析使用字幕文本（如果有），否则使用转录文本。
   - 字幕作为 `User text:` 保留在块内。

如果理解失败或被禁用，**回复流程继续**使用原始正文 + 附件。

## 配置概述

`tools.media` 支持**共享模型**加上按功能覆盖：

- `tools.media.models`: 共享模型列表（使用 `capabilities` 进行门控）。
- `tools.media.image` / `tools.media.audio` / `tools.media.video`:
  - 默认值 (`prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`)
  - 提供商覆盖 (`baseUrl`, `headers`, `providerOptions`)
  - 通过 `tools.media.audio.providerOptions.deepgram` 设置的 Deepgram 音频选项
  - 可选的**按功能 `models` 列表**（优先于共享模型）
  - `attachments` 策略 (`mode`, `maxAttachments`, `prefer`)
  - `scope`（可选的通道/聊天类型/会话密钥门控）
- `tools.media.concurrency`: 最大并发功能运行数（默认 **2**）。

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

- `{{MediaDir}}` (包含媒体文件的目录)
- `{{OutputDir}}` (为本次运行创建的临时目录)
- `{{OutputBase}}` (临时文件的基本路径，不带扩展名)

## 默认值和限制

推荐的默认值：

- `maxChars`: **500** 对于图像/视频（简短且适合命令）
- `maxChars`: **未设置** 对于音频（除非设置了限制，否则为完整转录）
- `maxBytes`:
  - 图像: **10MB**
  - 音频: **20MB**
  - 视频: **50MB**

规则：

- 如果媒体超过 `maxBytes`，该模型会被跳过，并尝试 **下一个模型**。
- 如果模型返回的结果超过 `maxChars`，输出会被截断。
- `prompt` 默认为简单的“描述 {media}。”加上 `maxChars` 的指导（仅适用于图像/视频）。
- 如果 `<capability>.enabled: true` 但没有配置模型，OpenClaw 会尝试
  **活动回复模型** 当其提供商支持该功能时。

### 自动检测媒体理解（默认）

如果 `tools.media.<capability>.enabled` 不是 `false` 并且你没有
配置模型，OpenClaw 按照以下顺序自动检测并 **在第一个
有效选项处停止**：

1. **本地 CLI**（仅音频；如果已安装）
   - `sherpa-onnx-offline`（需要 `SHERPA_ONNX_MODEL_DIR` 包含编码器/解码器/连接器/令牌）
   - `whisper-cli` (`whisper-cpp`; 使用 `WHISPER_CPP_MODEL` 或捆绑的小型模型）
   - `whisper`（Python CLI；自动下载模型）
2. **Gemini CLI** (`gemini`) 使用 `read_many_files`
3. **提供商密钥**
   - 音频: OpenAI → Groq → Deepgram → Google
   - 图像: OpenAI → Anthropic → Google → MiniMax
   - 视频: Google

要禁用自动检测，设置：

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

注意：二进制检测在 macOS/Linux/Windows 上是尽力而为；确保 CLI 在 `PATH` 上（我们扩展 `~`），或者使用完整命令路径显式设置 CLI 模型。

## 功能（可选）

如果你设置了 `capabilities`，该条目仅对这些媒体类型运行。对于共享
列表，OpenClaw 可以推断默认值：

- `openai`, `anthropic`, `minimax`: **图像**
- `google`（Gemini API）: **图像 + 音频 + 视频**
- `groq`: **音频**
- `deepgram`: **音频**

对于 CLI 条目，**显式设置 `capabilities`** 以避免意外匹配。
如果你省略 `capabilities`，该条目有资格出现在它出现的列表中。

## 提供商支持矩阵（OpenClaw 集成）

| 能力     | 提供商集成                                   | 备注                                              |
| -------- | -------------------------------------------- | ------------------------------------------------- |
| 图像     | OpenAI / Anthropic / Google / 其他通过 `pi-ai` | 注册表中的任何支持图像的模型都适用。            |
| 音频     | OpenAI, Groq, Deepgram, Google               | 提供商转录（Whisper/Deepgram/Gemini）。           |
| 视频     | Google (Gemini API)                          | 提供商视频理解。                                  |

## 推荐提供商

**图像**

- 如果您的活动模型支持图像，请优先使用。
- 好的默认选项：`openai/gpt-5.2`, `anthropic/claude-opus-4-6`, `google/gemini-3-pro-preview`。

**音频**

- `openai/gpt-4o-mini-transcribe`, `groq/whisper-large-v3-turbo`, 或 `deepgram/nova-3`。
- CLI 备选方案：`whisper-cli` (whisper-cpp) 或 `whisper`。
- Deepgram 设置：[Deepgram (音频转录)](/providers/deepgram)。

**视频**

- `google/gemini-3-flash-preview` (快速), `google/gemini-3-pro-preview` (更丰富)。
- CLI 备选方案：`gemini` CLI (支持 `read_file` 在视频/音频上)。

## 附件策略

按能力 `attachments` 控制哪些附件被处理：

- `mode`: `first` (默认) 或 `all`
- `maxAttachments`: 限制处理数量（默认 **1**）
- `prefer`: `first`, `last`, `path`, `url`

当 `mode: "all"` 时，输出标记为 `[Image 1/2]`, `[Audio 2/2]` 等。

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
          { provider: "openai", model: "gpt-5.2" },
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

### 4) 多模态单入口（显式功能）

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

这显示了每个功能的结果以及适用时选择的提供商/模型。

## 注意事项

- 理解是**尽力而为**。错误不会阻止回复。
- 即使禁用了理解，附件仍然会传递给模型。
- 使用 `scope` 来限制理解运行的位置（例如仅限私信）。

## 相关文档

- [配置](/gateway/configuration)
- [图像和媒体支持](/nodes/images)