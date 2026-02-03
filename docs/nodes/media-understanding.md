---
summary: "Inbound image/audio/video understanding (optional) with provider + CLI fallbacks"
read_when:
  - Designing or refactoring media understanding
  - Tuning inbound audio/video/image preprocessing
title: "Media Understanding"
---
# 媒体理解（入站）— 2026-01-17

OpenClaw 可以在回复流程运行前**对入站媒体**（图像/音频/视频）进行摘要处理。它会自动检测本地工具或提供者密钥是否可用，并且可以禁用或自定义。如果理解功能关闭，模型仍会如常接收原始文件/URL。

## 目标

- 可选：将入站媒体预处理为简短文本，以加快路由 + 更好的命令解析。
- 保留原始媒体传递给模型（始终）。
- 支持**提供者 API**和**CLI 回退**。
- 允许多个模型按顺序回退（错误/大小/超时）。

## 高级行为

1. 收集入站附件（`MediaPaths`、`MediaUrls`、`MediaTypes`）。
2. 对于每个启用的能力（图像/音频/视频），按策略选择附件（默认：**第一个**）。
3. 选择第一个符合条件的模型条目（大小 + 能力 + 认证）。
4. 如果模型失败或媒体过大，**回退到下一个条目**。
5. 成功时：
   - `Body` 变为 `[Image]`、`[Audio]` 或 `[Video]` 块。
   - 音频设置 `{{Transcript}}`；命令解析使用现有标题文本，否则使用转录内容。
   - 标题内容被保留为 `User text:` 内部的块。

如果理解失败或被禁用，**回复流程将继续使用原始正文 + 附件**。

## 配置概览

`tools.media` 支持**共享模型**以及按能力覆盖：

- `tools.media.models`：共享模型列表（使用 `capabilities` 进行控制）。
- `tools.media.image` / `tools.media.audio` / `tools.media.video`：
  - 默认值（`prompt`、`maxChars`、`maxBytes`、`timeoutSeconds`、`language`）
  - 提供者覆盖（`baseUrl`、`headers`、`providerOptions`）
  - 通过 `tools.media.audio.providerOptions.deepgram` 支持 Deepgram 音频选项
  - 可选的**按能力 `models` 列表**（优先于共享模型）
  - `attachments` 策略（`mode`、`maxAttachments`、`prefer`）
  - `scope`（可选的通过频道/聊天类型/会话密钥进行控制）
- `tools.media.concurrency`：最大并发能力运行数（默认 **2**）。

```json5
{
  tools: {
    media: {
      models: [
        /* 共享列表 */
      ],
      image: {
        /* 可选覆盖 */
      },
      audio: {
        /* 可选覆盖 */
      },
      video: {
        /* 可选覆盖 */
      },
    },
  },
}
```

### 模型条目

每个 `models[]` 条目可以是**提供者**或**CLI**：

```json5
{
  type: "provider", // 默认值，若省略
  provider: "openai",
  model: "gpt-5.2",
  prompt: "用 <= 500 个字符描述图像。",
  maxChars: 500,
  maxBytes: 10485760,
  timeoutSeconds: 30,
  language: "zh"
}
```

```json5
{
  type: "cli",
  command: "whisper",
  args: ["--model", "base", "{{MediaPath}}"],
  providerOptions: {
    "baseUrl": "https://api.example.com"
  }
}
```

### 模型条目（CLI 示例）

```json5
{
  type: "cli",
  command: "gemini",
  args: [
    "-m",
    "gemini-3-flash",
    "--allowed-tools",
    "read_file",
    "读取 {{MediaPath}} 并用 <= {{MaxChars}} 个字符描述。"
  ]
}
```

### 模型条目（提供者示例）

```json5
{
  provider: "google",
  model: "gemini-3-pro-preview",
  capabilities: ["image", "video", "audio"],
  prompt: "用 <= {{MaxChars}} 个字符描述 {{MediaPath}}。",
  maxChars: 500,
  maxBytes: 10485760,
  timeoutSeconds: 30,
  language: "zh"
}
```

### 状态输出

当媒体理解运行时，`/status` 包含一行简要摘要：

```
📎 媒体：图像正常（openai/gpt-5.2）· 音频跳过（maxBytes）
```

这显示了每个能力的结果以及适用的提供者/模型。

## 注意事项

- 理解是**尽力而为**。错误不会阻止回复。
- 即使理解被禁用，附件仍会传递给模型。
- 使用 `scope` 限制理解运行的范围（例如仅限 DM）。

## 相关文档

- [配置](/gateway/configuration)
- [图像与媒体支持](/nodes/images)