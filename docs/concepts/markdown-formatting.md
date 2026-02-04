---
summary: "Markdown formatting pipeline for outbound channels"
read_when:
  - You are changing markdown formatting or chunking for outbound channels
  - You are adding a new channel formatter or style mapping
  - You are debugging formatting regressions across channels
title: "Markdown Formatting"
---
# Markdown 格式化

OpenClaw 通过将其转换为共享中间表示（IR）来格式化出站 Markdown，然后再渲染特定于通道的输出。IR 保留源文本的同时携带样式/链接跨度，以便在各个通道中分块和渲染保持一致。

## 目标

- **一致性：** 一次解析步骤，多个渲染器。
- **安全分块：** 在渲染之前拆分文本，以确保内联格式永远不会跨块中断。
- **通道适配：** 将相同的 IR 映射到 Slack mrkdwn、Telegram HTML 和 Signal 样式范围，而无需重新解析 Markdown。

## 流程

1. **解析 Markdown -> IR**
   - IR 是纯文本加上样式跨度（粗体/斜体/删除线/代码/spoiler）和链接跨度。
   - 偏移量是 UTF-16 代码单元，以便 Signal 样式范围与其实现的 API 对齐。
   - 表格仅在通道选择进行表格转换时才进行解析。
2. **分块 IR（格式优先）**
   - 分块发生在渲染之前的 IR 文本上。
   - 内联格式不会跨块拆分；跨度按块切片。
3. **按通道渲染**
   - **Slack：** mrkdwn 标记（粗体/斜体/删除线/代码），链接作为 `<url|label>`。
   - **Telegram：** HTML 标签 (`<b>`, `<i>`, `<s>`, `<code>`, `<pre><code>`, `<a href>`)。
   - **Signal：** 纯文本 + `text-style` 范围；当标签不同时，链接变为 `label (url)`。

## IR 示例

输入 Markdown：

```markdown
Hello **world** — see [docs](https://docs.openclaw.ai).
```

IR（示意性）：

```json
{
  "text": "Hello world — see docs.",
  "styles": [{ "start": 6, "end": 11, "style": "bold" }],
  "links": [{ "start": 19, "end": 23, "href": "https://docs.openclaw.ai" }]
}
```

## 使用场景

- Slack、Telegram 和 Signal 出站适配器从 IR 渲染。
- 其他通道（WhatsApp、iMessage、MS Teams、Discord）仍然使用纯文本或其自身的格式规则，并在启用时在分块前应用 Markdown 表格转换。

## 表格处理

Markdown 表格在聊天客户端中并不一致支持。使用 `markdown.tables` 来控制每个通道（以及每个账户）的转换。

- `code`：将表格渲染为代码块（大多数通道的默认设置）。
- `bullets`：将每一行转换为项目符号（Signal + WhatsApp 的默认设置）。
- `off`：禁用表格解析和转换；原始表格文本通过。

配置键：

```yaml
channels:
  discord:
    markdown:
      tables: code
    accounts:
      work:
        markdown:
          tables: off
```

## 分块规则

- 分块限制来自通道适配器/配置，并应用于 IR 文本。
- 代码围栏被保留为一个带有尾随换行符的单个块，以便通道正确渲染它们。
- 列表前缀和引用前缀是 IR 文本的一部分，因此分块不会在前缀中途拆分。
- 内联样式（粗体/斜体/删除线/内联代码/spoiler）永远不会跨块拆分；渲染器会在每个块中重新打开样式。

如果需要更多关于通道间分块行为的信息，请参阅 [流式传输 + 分块](/concepts/streaming)。

## 链接策略

- **Slack：** `[label](url)` -> `<url|label>`；裸 URL 保持不变。解析期间禁用自动链接以避免双重链接。
- **Telegram：** `[label](url)` -> `<a href="url">label</a>`（HTML 解析模式）。
- **Signal：** `[label](url)` -> `label (url)` 除非标签匹配 URL。

## 隐藏内容

隐藏标记 (`||spoiler||`) 仅在 Signal 中解析，其中它们映射到 SPOILER 样式范围。其他通道将它们视为纯文本。

## 如何添加或更新通道格式化程序

1. **解析一次：** 使用共享的 `markdownToIR(...)` 辅助工具并使用适当的通道选项（自动链接、标题样式、引用前缀）。
2. **渲染：** 实现一个渲染器，使用 `renderMarkdownWithMarkers(...)` 和样式标记映射（或 Signal 样式范围）。
3. **分块：** 在渲染之前调用 `chunkMarkdownIR(...)`；渲染每个块。
4. **连接适配器：** 更新通道出站适配器以使用新的分块器和渲染器。
5. **测试：** 添加或更新格式测试和出站交付测试（如果通道使用分块）。

## 常见陷阱

- Slack 角括号标记 (`<@U123>`, `<#C123>`, `<https://...>`) 必须保留；安全地转义原始 HTML。
- Telegram HTML 需要转义标签外的文本以避免损坏的标记。
- Signal 样式范围依赖于 UTF-16 偏移量；不要使用代码点偏移量。
- 保留代码围栏的尾随换行符，以便关闭标记位于单独的一行。