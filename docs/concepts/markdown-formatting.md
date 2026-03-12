---
summary: "Markdown formatting pipeline for outbound channels"
read_when:
  - You are changing markdown formatting or chunking for outbound channels
  - You are adding a new channel formatter or style mapping
  - You are debugging formatting regressions across channels
title: "Markdown Formatting"
---
# Markdown 格式化

OpenClaw 通过将出站 Markdown 转换为一种共享的中间表示（IR），再据此生成各渠道特定的输出，从而实现对 Markdown 的格式化处理。该 IR 在保留原始文本内容的同时，携带样式与链接的跨度信息，以确保在不同渠道中分块与渲染行为的一致性。

## 目标

- **一致性：** 仅需一次解析，即可支持多种渲染器。
- **安全分块：** 在渲染前完成文本分块，确保行内格式不会跨块断裂。
- **渠道适配：** 将同一份 IR 映射至 Slack mrkdwn、Telegram HTML 及 Signal 样式范围，无需重新解析 Markdown。

## 处理流程

1. **解析 Markdown → IR**
   - IR 由纯文本及样式跨度（粗体/斜体/删除线/行内代码/剧透）和链接跨度组成。
   - 偏移量以 UTF-16 码元为单位，以确保与 Signal API 的样式范围对齐。
   - 表格仅在渠道显式启用表格转换时才进行解析。
2. **按 IR 分块（先格式化，后分块）**
   - 分块操作作用于 IR 文本，发生在渲染之前。
   - 行内格式不会跨块断裂；各跨度会依分块边界被切分。
3. **按渠道渲染**
   - **Slack：** 渲染为 mrkdwn 标记（粗体/斜体/删除线/行内代码），链接表示为 `<url|label>`。
   - **Telegram：** 渲染为 HTML 标签（`<b>`, `<i>`, `<s>`, `<code>`, `<pre><code>`, `<a href>`）。
   - **Signal：** 渲染为纯文本 + `text-style` 样式范围；当链接标签与 URL 不同时，链接转为 `label (url)`。

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

## 应用场景

- Slack、Telegram 和 Signal 的出站适配器均基于 IR 进行渲染。
- 其他渠道（WhatsApp、iMessage、MS Teams、Discord）仍使用纯文本或各自独立的格式规则；若启用表格转换，则在分块前应用 Markdown 表格转换。

## 表格处理

Markdown 表格在各类聊天客户端中的支持程度不一。请使用 `markdown.tables` 配置项，按渠道（及账户）控制表格转换行为。

- `code`：将表格渲染为代码块（大多数渠道的默认行为）。
- `bullets`：将每行表格转换为项目符号列表（Signal 与 WhatsApp 的默认行为）。
- `off`：禁用表格解析与转换；原始表格文本直接透传。

配置项键名：

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

- 分块限制由渠道适配器或配置提供，并应用于 IR 文本。
- 代码围栏（code fences）作为单个整体保留，并在其后添加换行符，以确保各渠道能正确渲染。
- 列表前缀与引用块前缀属于 IR 文本的一部分，因此分块不会在前缀中间切断。
- 行内样式（粗体/斜体/删除线/行内代码/剧透）绝不会跨块断裂；渲染器会在每个分块内重新开启对应样式。

如需进一步了解各渠道的分块行为，请参阅  
[流式传输与分块](/concepts/streaming)。

## 链接策略

- **Slack：** `[label](url)` → `<url|label>`；裸 URL 保持原样。解析过程中禁用自动链接（autolink），以防重复链接。
- **Telegram：** `[label](url)` → `<a href="url">label</a>`（HTML 解析模式）。
- **Signal：** `[label](url)` → `label (url)`，除非标签与 URL 完全一致。

## 剧透内容

剧透标记（`||spoiler||`）仅针对 Signal 进行解析，并映射为其 SPOILER 样式范围；其他渠道将其视为普通文本。

## 如何新增或更新一个渠道格式化器

1. **仅解析一次：** 使用共享的 `markdownToIR(...)` 辅助函数，并传入渠道专属选项（如是否启用 autolink、标题样式、引用块前缀等）。
2. **渲染：** 实现一个渲染器，接受 `renderMarkdownWithMarkers(...)` 输入，并提供样式标记映射表（或 Signal 样式范围）。
3. **分块：** 在渲染前调用 `chunkMarkdownIR(...)`；随后对每个分块分别渲染。
4. **接入适配器：** 更新对应渠道的出站适配器，使其使用新分块器与新渲染器。
5. **测试：** 增加或更新格式化测试；若该渠道使用分块机制，还需增加出站投递测试。

## 常见陷阱

- Slack 的尖括号标记（`<@U123>`、`<#C123>`、`<https://...>`）必须保留；需安全地转义原始 HTML。
- Telegram 的 HTML 渲染要求对标签外的文本进行转义，以防破坏 HTML 结构。
- Signal 的样式范围依赖 UTF-16 偏移量；切勿使用 Unicode 码点（code point）偏移量。
- 须保留围栏代码块末尾的换行符，以确保闭合标记独占一行。