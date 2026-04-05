---
summary: "How inbound audio/voice notes are downloaded, transcribed, and injected into replies"
read_when:
  - Changing audio transcription or media handling
title: "Audio and Voice Notes"
---
# 音频 / 语音笔记 (2026-01-17)

## 功能说明

- **媒体理解（音频）**: 如果启用了音频理解（或自动检测），OpenClaw 将：
  1. 定位第一个音频附件（本地路径或 URL）并在需要时下载它。
  2. 在向每个模型条目发送之前强制执行 `maxBytes`。
  3. 按顺序运行第一个符合条件的模型条目（提供商或 CLI）。
  4. 如果失败或跳过（大小/超时），则尝试下一个条目。
  5. 成功后，它将 `Body` 替换为 `[Audio]` 块并设置 `{{Transcript}}`。
- **命令解析**: 当转录成功时，`CommandBody`/`RawBody` 被设置为转录内容，以便斜杠命令仍然有效。
- **详细日志**: 在 `--verbose` 中，我们记录转录何时运行以及何时替换正文。

## 自动检测（默认）

如果您**未配置模型**且 `tools.media.audio.enabled` **未**设置为 `false`，OpenClaw 将按此顺序自动检测并在第一个可用的选项处停止：

1. **活动回复模型**，当其提供商支持音频理解时。
2. **本地 CLI**（如果已安装）
   - `sherpa-onnx-offline`（需要包含编码器/解码器/连接符/令牌的 `SHERPA_ONNX_MODEL_DIR`）
   - `whisper-cli`（来自 `whisper-cpp`；使用 `WHISPER_CPP_MODEL` 或内置的微型模型）
   - `whisper`（Python CLI；自动下载模型）
3. **Gemini CLI** (`gemini`) 使用 `read_many_files`
4. **提供商认证**
   - 首先尝试配置的 `models.providers.*` 条目，这些条目支持音频
   - 内置回退顺序：OpenAI → Groq → Deepgram → Google → Mistral

要禁用自动检测，请设置 `tools.media.audio.enabled: false`。
要自定义，请设置 `tools.media.audio.models`。
注意：二进制检测在 macOS/Linux/Windows 上尽最大努力；确保 CLI 位于 `PATH`（我们会扩展 `~`），或者设置带有完整命令路径的明确 CLI 模型。

## 配置示例

### 提供商 + CLI 回退 (OpenAI + Whisper CLI)

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        maxBytes: 20971520,
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          {
            type: "cli",
            command: "whisper",
            args: ["--model", "base", "{{MediaPath}}"],
            timeoutSeconds: 45,
          },
        ],
      },
    },
  },
}
```

### 仅提供商带范围门控

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        scope: {
          default: "allow",
          rules: [{ action: "deny", match: { chatType: "group" } }],
        },
        models: [{ provider: "openai", model: "gpt-4o-mini-transcribe" }],
      },
    },
  },
}
```

### 仅提供商 (Deepgram)

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "deepgram", model: "nova-3" }],
      },
    },
  },
}
```

### 仅提供商 (Mistral Voxtral)

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

### 回声转录到聊天（需选择加入）

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        echoTranscript: true, // default is false
        echoFormat: '📝 "{transcript}"', // optional, supports {transcript}
        models: [{ provider: "openai", model: "gpt-4o-mini-transcribe" }],
      },
    },
  },
}
```

## 注意事项与限制

- 提供商认证遵循标准模型认证顺序（认证配置文件、环境变量、`models.providers.*.apiKey`）。
- Groq 设置详情：[Groq](/providers/groq)。
- Deepgram 在使用 `provider: "deepgram"` 时会获取 `DEEPGRAM_API_KEY`。
- Deepgram 设置详情：[Deepgram（音频转录）](/providers/deepgram)。
- Mistral 设置详情：[Mistral](/providers/mistral)。
- 音频提供商可以通过 `tools.media.audio` 覆盖 `baseUrl`、`headers` 和 `providerOptions`。
- 默认大小限制为 20MB (`tools.media.audio.maxBytes`)。超出大小的音频会被该模型跳过，并尝试下一个条目。
- 小于 1024 字节的微型/空音频文件会在提供商/CLI 转录之前被跳过。
- 音频的默认 `maxChars` 为**未设置**（完整转录）。设置 `tools.media.audio.maxChars` 或每个条目的 `maxChars` 以修剪输出。
- OpenAI 自动默认值为 `gpt-4o-mini-transcribe`；设置 `model: "gpt-4o-transcribe"` 以获得更高的准确性。
- 使用 `tools.media.audio.attachments` 处理多个语音笔记 (`mode: "all"` + `maxAttachments`)。
- 转录内容可作为 `{{Transcript}}` 提供给模板。
- `tools.media.audio.echoTranscript` 默认为关闭；启用它以在代理处理之前将转录确认发送回原始聊天。
- `tools.media.audio.echoFormat` 自定义回声文本（占位符：`{transcript}`）。
- CLI stdout 有上限（5MB）；保持 CLI 输出简洁。

### 代理环境支持

基于提供商的音频转录支持标准出站代理环境变量：

- `HTTPS_PROXY`
- `HTTP_PROXY`
- `https_proxy`
- `http_proxy`

如果未设置代理环境变量，则使用直接出站。如果代理配置格式错误，OpenClaw 会记录警告并回退到直接获取。

## 群组中的提及检测

当为群聊设置 `requireMention: true` 时，OpenClaw 现在会在检查提及**之前**转录音频。这允许即使语音笔记包含提及也能进行处理。

**工作原理：**

1. 如果语音消息没有文本正文且群组需要提及，OpenClaw 将执行“预检”转录。
2. 检查转录内容中的提及模式（例如 `@BotName`、表情符号触发器）。
3. 如果找到提及，消息将通过完整的回复流程。
4. 转录用于提及检测，因此语音笔记可以通过提及门控。

**回退行为：**

- 如果预检期间转录失败（超时、API 错误等），消息将基于仅文本的提及检测进行处理。
- 这确保了混合消息（文本 + 音频）永远不会被错误丢弃。

**针对 Telegram 群组/主题的退出选项：**

- 设置 `channels.telegram.groups.<chatId>.disableAudioPreflight: true` 以跳过该组的预检转录提及检查。
- 设置 `channels.telegram.groups.<chatId>.topics.<threadId>.disableAudioPreflight` 以按主题覆盖 (`true` 跳过，`false` 强制启用)。
- 默认为 `false`（当提及门控条件匹配时启用预检）。

**示例：** 用户在具有 `requireMention: true` 的 Telegram 群组中发送一条语音笔记，内容为“嘿 @Claude，天气怎么样？”。语音笔记被转录，检测到提及，然后代理回复。

## 注意事项 / 陷阱

- 作用域规则使用首次匹配优先。`chatType` 被规范化为 `direct`、`group` 或 `room`。
- 确保您的 CLI 退出码为 0 并打印纯文本；JSON 需要通过 `jq -r .text` 进行整理。
- 对于 `parakeet-mlx`，如果您传递 `--output-dir`，当 `--output-format` 为 `txt`（或省略）时，OpenClaw 读取 `<output-dir>/<media-basename>.txt`；非 `txt` 输出格式回退到 stdout 解析。
- 保持超时合理 (`timeoutSeconds`，默认 60 秒)，以避免阻塞回复队列。
- 预检转录仅处理**第一个**音频附件以进行提及检测。额外的音频在主媒体理解阶段进行处理。