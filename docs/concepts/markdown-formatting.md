---
summary: "Markdown formatting pipeline for outbound channels"
read_when:
  - You are changing markdown formatting or chunking for outbound channels
  - You are adding a new channel formatter or style mapping
  - You are debugging formatting regressions across channels
title: "Markdown Formatting"
---
# Markdown 格式化

OpenClaw 通过将传出的 Markdown 转换为共享的中间表示（IR），然后渲染特定渠道的输出来格式化传出的 Markdown。IR 在保持源文本完整的同时携带样式/链接跨度，因此分块和渲染可以在各个渠道间保持一致。

## 目标

- **一致性：** 一个解析步骤，多个渲染器。
- **安全分块：** 在渲染之前分割文本，这样内联格式永远不会跨块中断。
- **渠道适配：** 将相同的 IR 映射到 Slack mrkdwn、Telegram HTML 和 Signal 样式范围，无需重新解析 Markdown。

## 管道

1. **解析 Markdown -> IR**
   - IR 是纯文本加上样式跨度（粗体/斜体/删除线/代码/隐藏）和链接跨度。
   - 偏移量是 UTF-16 代码单元，以便 Signal 样式范围与其 API 对齐。
   - 表格仅在渠道选择加入表格转换时才被解析。
2. **分块 IR（格式优先）**
   - 分块发生在渲染之前的 IR 文本上。
   - 内联格式不会跨块分割；跨度按块切片。
3. **按渠道渲染**
   - **Slack：** mrkdwn 标记（粗体/斜体/删除线/代码），链接作为 `<url|label>`。
   - **Telegram：** HTML 标签（`<b>`，`<i>`，`<s>`，`<code>`，`<pre><code>`，`<a href>`）。
   - **Signal：** 纯文本 + `text-style` 范围；当标签不同时，链接变为 `label (url)`。

## IR 示例

输入 Markdown：

```markdown
Hello **world** — see [docs](https://docs.openclaw.ai).
```

IR（示意图）：

```json
{
  "text": "Hello world — see docs.",
  "styles": [{ "start": 6, "end": 11, "style": "bold" }],
  "links": [{ "start": 19, "end": 23, "href": "https://docs.openclaw.ai" }]
}
```

## 使用位置

- Slack、Telegram 和 Signal 传出适配器从 IR 渲染。
- 其他渠道（WhatsApp、iMessage、MS Teams、Discord）仍使用纯文本或其自己的格式规则，在启用时在分块之前应用 Markdown 表格转换。

## 表格处理

Markdown 表格在聊天客户端中没有得到一致支持。使用 `markdown.tables` 来控制每个渠道（和每个账户）的转换。

- `code`：将表格渲染为代码块（大多数渠道的默认设置）。
- `bullets`：将每行转换为项目符号（Signal + WhatsApp 的默认设置）。
- `off`：禁用表格解析和转换；原始表格文本直接通过。

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

- 分块限制来自渠道适配器/配置，并应用于 IR 文本。
- 代码围栏作为单个块保留，并带有尾随换行符，以便渠道正确渲染它们。
- 列表前缀和引用块前缀是 IR 文本的一部分，因此分块不会在前缀中间分割。
- 内联样式（粗体/斜体/删除线/内联代码/隐藏）永远不会跨块分割；渲染器在每个块内部重新打开样式。

如果您需要了解跨渠道的更多分块行为，请参见
[流式传输 + 分块](/concepts/streaming)。

## 链接策略

- **Slack：** `[label](url)` -> `<url|label>`；裸露 URL 保持原样。解析期间禁用自动链接以避免双重链接。
- **Telegram：** `[label](url)` -> `<a href="url">label</a>`（HTML 解析模式）。
- **Signal：** `[label](url)` -> `label (url)`，除非标签与 URL 匹配。

## 隐藏内容

隐藏标记（`||spoiler||`）仅针对 Signal 进行解析，在那里它们映射到 SPOILER 样式范围。其他渠道将其视为纯文本。

## 如何添加或更新渠道格式化程序

1. **解析一次：** 使用共享的 `markdownToIR(...)` 辅助函数，使用适合渠道的选项（自动链接、标题样式、引用块前缀）。
2. **渲染：** 实现一个渲染器，使用 `renderMarkdownWithMarkers(...)` 和样式标记映射（或 Signal 样式范围）。
3. **分块：** 在渲染之前调用 `chunkMarkdownIR(...)`；渲染每个块。
4. **连接适配器：** 更新渠道传出适配器以使用新的分块器和渲染器。
5. **测试：** 添加或更新格式测试，如果渠道使用分块，则添加传出传递测试。

## 常见陷阱

- Slack 角括号标记（`<@U123>`，`<#C123>`，`<https://...>`）必须保留；安全转义原始 HTML。
- Telegram HTML 需要转义标签外的文本以避免损坏的标记。
- Signal 样式范围依赖于 UTF-16 偏移量；不要使用代码点偏移量。
- 保留围栏代码块的尾随换行符，以便关闭标记位于自己的行上。