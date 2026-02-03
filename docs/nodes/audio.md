---
summary: "How inbound audio/voice notes are downloaded, transcribed, and injected into replies"
read_when:
  - Changing audio transcription or media handling
title: "Audio and Voice Notes"
---
# 音频/语音备忘录 — 2026-01-17

## 有效功能

- **媒体理解（音频）**：如果启用了音频理解（或自动检测），OpenClaw：
  1. 定位第一个音频附件（本地路径或URL），如有需要则下载。
  2. 在发送到每个模型条目前强制执行`maxBytes`。
  3. 按顺序运行第一个符合条件的模型条目（提供者或CLI）。
  4. 如果失败或跳过（因大小/超时），则尝试下一个条目。
  5. 成功时，将`Body`替换为`[Audio]`块并设置`{{Transcript}}`。
- **命令解析**：当转录成功时，`CommandBody`/`RawBody`会被设置为转录内容，因此斜杠命令仍可正常运行。
- **详细日志**：在`--verbose`模式下，我们会记录转录运行时和替换正文的时间。

## 自动检测（默认）

如果你**未配置模型**且`tools.media.audio.enabled`未被设置为`false`，OpenClaw将按以下顺序自动检测并停止在第一个可用选项：

1. **本地CLI**（如果已安装）
   - `sherpa-onnx-offline`（需要`SHERPA_ONNX_MODEL_DIR`包含编码器/解码器/连接器/令牌）
   - `whisper-cli`（来自`whisper-cpp`；使用`WHISPER_CPP_MODEL`或捆绑的tiny模型）
   - `whisper`（Python CLI；会自动下载模型）
2. **Gemini CLI**（使用`read_many_files`）
3. **提供者密钥**（OpenAI → Groq → Deepgram → Google）

要禁用自动检测，请将`tools.media.audio.enabled: false`。
要自定义，请设置`tools.media.audio.models`。
注意：二进制检测在macOS/Linux/Windows上为尽力而为；确保CLI在`PATH`中（我们展开`~`），或设置带有完整命令路径的显式CLI模型。

## 配置示例

### 提供者 + CLI回退（OpenAI + Whisper CLI）

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

### 仅提供者（带作用域控制）

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

### 仅提供者（Deepgram）

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

## 注意事项与限制

- 提供者认证遵循标准模型认证顺序（认证配置文件、环境变量、`models.providers.*.apiKey`）。
- 使用`provider: "deepgram"`时，Deepgram会拾取`DEEPGRAM_API_KEY`。
- Deepgram设置详情：[Deepgram（音频转录）](/providers/deepgram)。
- 音频提供者可通过`tools.media.audio`覆盖`baseUrl`、`headers`和`providerOptions`。
- 默认大小限制为20MB（`tools.media.audio.maxBytes`）。超大音频将跳过该模型并尝试下一个条目。
- 音频默认`maxChars`为**未设置**（完整转录）。设置`tools.media.audio.maxChars`或每条目`maxChars`以截断输出。
- OpenAI默认使用`gpt-4o-mini-transcribe`；设置`model: "gpt-4o-transcribe"`以获得更高准确性。
- 使用`tools.media.audio.attachments`处理多个语音备忘录（`mode: "all"` + `maxAttachments`）。
- 转录内容可通过`{{Transcript}}`在模板中使用。
- CLI标准输出受限（5MB）；保持CLI输出简洁。

## 注意事项

- 作用域规则采用首次匹配优先。`chatType`会规范化为`direct`、`group`或`room`。
- 确保CLI退出码为0并输出纯文本；JSON需通过`jq -r .text`进行处理。
- 保持超时合理（`timeoutSeconds`，默认60秒），以避免阻塞回复队列。