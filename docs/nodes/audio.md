---
summary: "How inbound audio/voice notes are downloaded, transcribed, and injected into replies"
read_when:
  - Changing audio transcription or media handling
title: "Audio and Voice Notes"
---
# 音频/语音笔记 — 2026-01-17

## 工作功能

- **媒体理解（音频）**：如果启用了音频理解（或自动检测），OpenClaw：
  1. 定位第一个音频附件（本地路径或URL）并在需要时下载它。
  2. 在发送到每个模型条目之前强制执行 `maxBytes`。
  3. 按顺序运行第一个符合条件的模型条目（提供程序或CLI）。
  4. 如果失败或跳过（大小/超时），则尝试下一个条目。
  5. 成功时，它将 `Body` 替换为 `[Audio]` 块并设置 `{{Transcript}}`。
- **命令解析**：当转录成功时，`CommandBody`/`RawBody` 被设置为转录文本，因此斜杠命令仍然有效。
- **详细日志记录**：在 `--verbose` 中，我们记录转录运行时间和替换正文的时间。

## 自动检测（默认）

如果您**不配置模型**且 `tools.media.audio.enabled` **未** 设置为 `false`，
OpenClaw 按此顺序自动检测并停止在第一个工作选项：

1. **本地CLIs**（如果已安装）
   - `sherpa-onnx-offline`（需要带有encoder/decoder/joiner/tokens的 `SHERPA_ONNX_MODEL_DIR`）
   - `whisper-cli`（来自 `whisper-cpp`；使用 `WHISPER_CPP_MODEL` 或捆绑的tiny模型）
   - `whisper`（Python CLI；自动下载模型）
2. **Gemini CLI**（`gemini`）使用 `read_many_files`
3. **提供程序密钥**（OpenAI → Groq → Deepgram → Google）

要禁用自动检测，请设置 `tools.media.audio.enabled: false`。
要自定义，请设置 `tools.media.audio.models`。
注意：二进制文件检测在macOS/Linux/Windows上是尽力而为的；确保CLI在 `PATH` 上（我们扩展 `~`），或者使用完整命令路径设置显式CLI模型。

## 配置示例

### 提供程序 + CLI回退（OpenAI + Whisper CLI）

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

### 仅提供程序，带作用域门控

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

### 仅提供程序（Deepgram）

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

## 注意事项和限制

- 提供程序认证遵循标准模型认证顺序（认证配置文件、环境变量、`models.providers.*.apiKey`）。
- 当使用 `provider: "deepgram"` 时，Deepgram会获取 `DEEPGRAM_API_KEY`。
- Deepgram设置详情：[Deepgram（音频转录）](/providers/deepgram)。
- 音频提供程序可以通过 `tools.media.audio` 覆盖 `baseUrl`、`headers` 和 `providerOptions`。
- 默认大小限制为20MB（`tools.media.audio.maxBytes`）。对于该模型，超大音频会被跳过并尝试下一个条目。
- 音频的默认 `maxChars` 是**未设置**（完整转录）。设置 `tools.media.audio.maxChars` 或每个条目的 `maxChars` 来修剪输出。
- OpenAI自动默认值为 `gpt-4o-mini-transcribe`；设置 `model: "gpt-4o-transcribe"` 以获得更高准确性。
- 使用 `tools.media.audio.attachments` 来处理多个语音笔记（`mode: "all"` + `maxAttachments`）。
- 转录文本作为 `{{Transcript}}` 对模板可用。
- CLI标准输出有上限（5MB）；保持CLI输出简洁。

## 注意事项

- 作用域规则使用首次匹配获胜。`chatType` 被标准化为 `direct`、`group` 或 `room`。
- 确保您的CLI以退出码0退出并打印纯文本；JSON需要通过 `jq -r .text` 进行处理。
- 保持合理的超时时间（`timeoutSeconds`，默认60秒）以避免阻塞回复队列。