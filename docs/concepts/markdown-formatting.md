---
summary: "Markdown formatting pipeline for outbound channels"
read_when:
  - You are changing markdown formatting or chunking for outbound channels
  - You are adding a new channel formatter or style mapping
  - You are debugging formatting regressions across channels
title: "Markdown Formatting"
---
# Markdown 格式化

OpenClaw 通过将 Markdown 转换为共享的中间表示（IR）后再渲染特定渠道的输出格式。IR 保留了源文本的完整性，同时携带样式/链接跨度，以确保在不同渠道中分块和渲染的一致性。

## 目标

- **一致性：** 一次解析，多个渲染器。
- **安全分块：** 在渲染前拆分文本，确保内联格式不会跨分块。
- **渠道适配：** 将相同的 IR 映射到 Slack mrkdwn、Telegram HTML 和 Signal 样式范围，无需重新解析 Markdown。

## 流程

1. **解析 Markdown -> IR**
   - IR 是纯文本加上样式跨度（粗体/斜体/删除线/代码/剧透）和链接跨度。
   - 偏移量使用 UTF-16 编码单元，以便 Signal 样式范围与 API 对齐。
   - 表格仅在渠道启用表格转换时解析。
2. **分块 IR（格式优先）**
   - 分块在渲染前对 IR 文本进行。
   - 内联格式不会跨分块；跨度按分块切分。
3. **按渠道渲染**
   - **Slack：** mrkdwn 标记（粗体/斜体/删除线/代码），链接格式为 `<url|label>`。
   - **Telegram：** HTML 标签（`<b>`、`<i>`、`<s>`、`<code>`、`<pre><code>`、`<a href>`）。
   - **Signal：** 纯文本 + `text-style` 范围；当标签与 URL 不同时，链接变为 `label (url)`。

## IR 示例

输入 Markdown：

```markdown
Hello **world** — see [docs](https://docs.openclaw.ai).
``
```

IR（示意图）：

```json
{
  "text": "Hello world — see docs.",
  "styles": [{ "start": 6, "end": 11, "style": "bold" }],
  "links": [{ "start": 19, "end": 23, "href": "https://docs.openclaw.ai" }]
}
``
```

## 使用场景

- Slack、Telegram 和 Signal 的传出适配器从 IR 渲染。
- 其他渠道（WhatsApp、iMessage、MS Teams、Discord）仍使用纯文本或各自的格式规则，启用时在分块前应用 Markdown 表格转换。

## 表格处理

Markdown 表格在聊天客户端中支持不一致。使用 `markdown.tables` 控制每个渠道（及每个账户）的转换。

- `code`：以代码块渲染表格（大多数渠道的默认设置）。
- `bullets`：将每一行转换为项目符号（Signal + WhatsApp 的默认设置）。
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
``
```

## 分块规则

- 分块限制来自渠道适配器/配置，并应用于 IR 文本。
- 代码块边界保留为一个块并带有尾随换行，以便渠道正确渲染。
- 列表前缀和块引用前缀是 IR 文本的一部分，因此分块不会在前缀中间拆分。
- 内联样式（粗体/斜体/删除线/内联代码/剧透）永远不会跨分块；渲染器会在每个分块内重新打开样式。

如需了解跨渠道的分块行为，请参见 [流式传输 + 分块](/concepts/streaming)。

## 链接策略

- **Slack：** `[label](url)` -> `<url|label>`；裸 URL 保持原样。解析时禁用自动链接以避免双重链接。
- **Telegram：** `[label](url)` -> `<a href="url">label</a>`（HTML 解析模式）。
- **Signal：** `[label](url)` -> `label (url)`，除非标签与 URL 相同。

## 剧透

剧透标记（`||spoiler||`）仅在 Signal 中解析，映射到 SPOILER 样式范围。其他渠道将其视为纯文本。

## 如何添加或更新渠道格式化器

1. **一次解析：** 使用共享的 `markdownToIR(...)` 辅助函数并传入渠道适用的选项（自动链接、标题样式、块引用前缀）。
2. **渲染：** 实现一个使用 `renderMarkdownWithMarkers(...)` 和样式标记映射（或 Signal 样式范围）的渲染器。
3. **分块：** 在渲染前调用 `chunkMarkdownIR(...)`；渲染每个分块。
4. **连接适配器：** 更新渠道传出适配器以使用新的分块器和渲染器。
5. **测试：** 添加或更新格式测试，并在渠道使用分块时添加传出交付测试。

## 常见问题

- Slack 的尖括号标记（`<@U123>`、`<#C123>`、`<https://...>`）必须保留；安全转义原始 HTML。
- Telegram 的 HTML 需要转义标签外的文本以避免损坏的标记。
- Signal 的样式范围依赖 UTF-16 偏移量；不要使用代码点偏