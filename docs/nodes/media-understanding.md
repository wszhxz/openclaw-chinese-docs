---
summary: "Inbound image/audio/video understanding (optional) with provider + CLI fallbacks"
read_when:
  - Designing or refactoring media understanding
  - Tuning inbound audio/video/image preprocessing
title: "Media Understanding"
---
# 媒体理解（入站）——2026-01-17

OpenClaw 可在回复流程运行前 **对入站媒体**（图像/音频/视频）进行摘要。它会自动检测本地工具或提供商密钥是否可用，并支持禁用或自定义。若媒体理解功能关闭，模型仍会照常接收原始文件/URL。

## 目标

- 可选：将入站媒体预处理为简短文本，以加快路由速度并提升指令解析效果。
- 始终保留原始媒体向模型的完整传递。
- 支持 **提供商 API** 和 **CLI 回退机制**。
- 支持多个模型及按序回退（因错误/尺寸超限/超时）。

## 高层行为

1. 收集入站附件（``MediaPaths``、``MediaUrls``、``MediaTypes``）。
2. 对每个启用的能力（图像/音频/视频），依据策略选择附件（默认：**首个**）。
3. 选择首个符合条件的模型条目（满足尺寸 + 能力 + 认证要求）。
4. 若某模型失败或媒体过大，则 **回退至下一个条目**。
5. 成功时：
   - ``Body`` 将变为 ``[Image]``、``[Audio]`` 或 ``[Video]`` 块。
   - 音频设置 ``{{Transcript}}``；指令解析优先使用字幕文本（若存在），否则使用转录文本。
   - 字幕作为 ``User text:`` 保留在该块内。

若媒体理解失败或被禁用，**回复流程将继续执行**，携带原始正文 + 附件。

## 配置概览

``tools.media`` 支持 **共享模型** 及按能力覆盖配置：

- ``tools.media.models``：共享模型列表（可使用 ``capabilities`` 进行门控）。
- ``tools.media.image`` / ``tools.media.audio`` / ``tools.media.video``：
  - 默认值（``prompt``、``maxChars``、``maxBytes``、``timeoutSeconds``、``language``）
  - 提供商覆盖项（``baseUrl``、``headers``、``providerOptions``）
  - 通过 ``tools.media.audio.providerOptions.deepgram`` 配置 Deepgram 音频选项
  - 音频转录回显控制（``echoTranscript``，默认为 ``false``；``echoFormat``）
  - 可选的 **按能力指定的 ``models`` 列表**（优先于共享模型）
  - ``attachments`` 策略（``mode``、``maxAttachments``、``prefer``）
  - ``scope``（可选，按 channel/chatType/session key 进行门控）
- ``tools.media.concurrency``：最大并发能力运行数（默认为 **2**）。

````json5
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
````

### 模型条目

每个 ``models[]`` 条目可以是 **提供商** 或 **CLI** 类型：

````json5
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
````

````json5
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
````

CLI 模板还可使用：

- ``{{MediaDir}}``（含媒体文件的目录）
- ``{{OutputDir}}``（为此运行创建的临时目录）
- ``{{OutputBase}}``（临时文件基础路径，不含扩展名）

## 默认值与限制

推荐默认值：

- ``maxChars``：图像/视频为 **500**（简短、适合指令交互）
- ``maxChars``：音频为 **未设置**（除非手动设限，否则返回完整转录）
- ``maxBytes``：
  - 图像：**10MB**
  - 音频：**20MB**
  - 视频：**50MB**

规则：

- 若媒体超出 ``maxBytes``，则跳过该模型并尝试 **下一个模型**。
- 小于 **1024 字节** 的音频文件被视为为空/损坏，在调用提供商/CLI 转录前即被跳过。
- 若模型返回内容超过 ``maxChars``，输出将被截断。
- ``prompt`` 默认为简单提示：“Describe the {media}.” 加上 ``maxChars`` 指引（仅适用于图像/视频）。
- 若启用了 ``<capability>.enabled: true`` 但未配置任何模型，OpenClaw 将在当前活跃回复模型的提供商支持该能力时，尝试使用该 **活跃回复模型**。

### 自动检测媒体理解（默认）

若 ``tools.media.<capability>.enabled`` **未** 设置为 ``false``，且您尚未配置模型，OpenClaw 将按以下顺序自动检测，并 **在首个可用选项处停止**：

1. **本地 CLI**（仅音频；需已安装）
   - ``sherpa-onnx-offline``（需 ``SHERPA_ONNX_MODEL_DIR`` 含编码器/解码器/连接器/词元）
   - ``whisper-cli``（``whisper-cpp``；使用 ``WHISPER_CPP_MODEL`` 或内置的 tiny 模型）
   - ``whisper``（Python CLI；自动下载模型）
2. **Gemini CLI**（``gemini``）使用 ``read_many_files``
3. **提供商密钥**
   - 音频：OpenAI → Groq → Deepgram → Google
   - 图像：OpenAI → Anthropic → Google → MiniMax
   - 视频：Google

如需禁用自动检测，请设置：

````json5
{
  tools: {
    media: {
      audio: {
        enabled: false,
      },
    },
  },
}
````

注意：二进制检测在 macOS/Linux/Windows 上均为尽力而为；请确保 CLI 已加入 ``PATH``（我们会展开 ``~``），或显式配置带完整命令路径的 CLI 模型。

### 代理环境支持（提供商模型）

当启用基于提供商的 **音频** 和 **视频** 媒体理解时，OpenClaw 将遵循标准的出站代理环境变量，用于提供商 HTTP 调用：

- ``HTTPS_PROXY``
- ``HTTP_PROXY``
- ``https_proxy``
- ``http_proxy``

若未设置代理环境变量，媒体理解将直接出站访问。  
若代理值格式错误，OpenClaw 将记录警告并回退至直接获取。

## 能力（可选）

若您设置了 ``capabilities``，该条目仅对所列媒体类型运行。对于共享列表，OpenClaw 可推断默认值：

- ``openai``、``anthropic``、``minimax``：**图像**
- ``google``（Gemini API）：**图像 + 音频 + 视频**
- ``groq``：**音频**
- ``deepgram``：**音频**

对于 CLI 条目，**请显式设置 ``capabilities``**，以避免意外匹配。  
若您省略 ``capabilities``，该条目将对其所在列表中所有能力均生效。

## 提供商支持矩阵（OpenClaw 集成）

| 能力 | 提供商集成                                     | 说明                                                     |
| ---- | ---------------------------------------------- | -------------------------------------------------------- |
| 图像 | OpenAI / Anthropic / Google / 其他通过 ``pi-ai`` | 注册表中任意支持图像的模型均可工作。                     |
| 音频 | OpenAI、Groq、Deepgram、Google、Mistral         | 提供商转录（Whisper/Deepgram/Gemini/Voxtral）。          |
| 视频 | Google（Gemini API）                           | 提供商视频理解。                                         |

## 模型选择建议

- 当质量与安全性至关重要时，应优先选用各媒体能力下最新一代最强模型。
- 对于处理不可信输入的工具增强型智能体，应避免使用较旧/较弱的媒体模型。
- 每种能力至少保留一个回退模型以保障可用性（高质量模型 + 更快/更廉价模型）。
- 当提供商 API 不可用时，CLI 回退机制（``whisper-cli``、``whisper``、``gemini``）非常有用。
- ``parakeet-mlx`` 注意：配合 ``--output-dir``，当输出格式为 ``txt``（或未指定）时，OpenClaw 将读取 ``<output-dir>/<media-basename>.txt``；非 ``txt`` 格式则回退至 stdout。

## 附件策略

按能力的 ``attachments`` 控制哪些附件会被处理：

- ``mode``：``first``（默认）或 ``all``
- ``maxAttachments``：限制处理数量（默认为 **1**）
- ``prefer``：``first``、``last``、``path``、``url``

当启用 ``mode: "all"`` 时，输出将标记为 ``[Image 1/2]``、``[Audio 2/2]`` 等。

## 配置示例

### 1) 共享模型列表 + 覆盖配置

````json5
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
````

### 2) 仅启用音频 + 视频（图像关闭）

````json5
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
````

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

媒体理解运行时，`/status` 包含一行简短的摘要：

```
📎 Media: image ok (openai/gpt-5.2) · audio skipped (maxBytes)
```

这会显示每项能力的执行结果，以及在适用情况下所选用的提供方/模型。

## 注意事项

- 媒体理解为**尽力而为**。发生错误时不会阻断回复。
- 即使禁用了媒体理解，附件仍会传递给模型。
- 使用 `scope` 可限制媒体理解的运行范围（例如仅限私信）。

## 相关文档

- [配置](/gateway/configuration)
- [图像与媒体支持](/nodes/images)