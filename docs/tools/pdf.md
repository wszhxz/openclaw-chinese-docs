---
title: "PDF Tool"
summary: "Analyze one or more PDF documents with native provider support and extraction fallback"
read_when:
  - You want to analyze PDFs from agents
  - You need exact pdf tool parameters and limits
  - You are debugging native PDF mode vs extraction fallback
---
# PDF 工具

`pdf` 分析一个或多个PDF文档并返回文本。

快速行为：

- 为Anthropic和Google模型提供商提供原生提供商模式。
- 为其他提供商提供提取回退模式（首先提取文本，然后在需要时提取页面图像）。
- 支持单个(`pdf`)或多(`pdfs`)输入，每次调用最多10个PDF。

## 可用性

只有当OpenClaw能够为代理解析出支持PDF的模型配置时，该工具才会被注册：

1. `agents.defaults.pdfModel`
2. 回退到`agents.defaults.imageModel`
3. 根据可用认证回退到最佳努力提供商默认值

如果无法解析出可用模型，则不公开`pdf`工具。

## 输入参考

- `pdf` (`string`)：一个PDF路径或URL
- `pdfs` (`string[]`)：多个PDF路径或URL，总共最多10个
- `prompt` (`string`)：分析提示，默认为`Analyze this PDF document.`
- `pages` (`string`)：页面过滤器如`1-5` 或 `1,3,7-9`
- `model` (`string`)：可选模型覆盖(`provider/model`)
- `maxBytesMb` (`number`)：每个PDF的大小上限（MB）

输入注意事项：

- `pdf` 和 `pdfs` 在加载前会被合并并去重。
- 如果没有提供PDF输入，工具将报错。
- `pages` 被解析为基于1的页码，去重、排序，并限制在配置的最大页数内。
- `maxBytesMb` 默认为 `agents.defaults.pdfMaxBytesMb` 或 `10`。

## 支持的PDF引用

- 本地文件路径（包括`~`扩展）
- `file://` URL
- `http://` 和 `https://` URL

引用注意事项：

- 其他URI方案（例如`ftp://`）会因`unsupported_pdf_reference`而被拒绝。
- 在沙箱模式下，远程`http(s)` URL将被拒绝。
- 启用了仅工作区文件策略后，允许根目录外的本地文件路径将被拒绝。

## 执行模式

### 原生提供商模式

原生模式用于提供商`anthropic` 和 `google`。
该工具直接将原始PDF字节发送给提供商API。

原生模式限制：

- 不支持`pages`。如果设置，工具将返回错误。

### 提取回退模式

回退模式用于非原生提供商。

流程：

1. 从选定页面中提取文本（最多`agents.defaults.pdfMaxPages`，默认为`20`）。
2. 如果提取的文本长度低于`200`字符，则将选定页面渲染为PNG图像并包含它们。
3. 将提取的内容加上提示发送给所选模型。

回退详情：

- 页面图像提取使用`4,000,000`像素预算。
- 如果目标模型不支持图像输入且没有可提取的文本，工具将报错。
- 提取回退需要`pdfjs-dist`（以及用于图像渲染的`@napi-rs/canvas`）。

## 配置

```json5
{
  agents: {
    defaults: {
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5-mini"],
      },
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
    },
  },
}
```

有关完整字段详细信息，请参阅[配置参考](/gateway/configuration-reference)。

## 输出详情

该工具以`content[0].text`格式返回文本，并以`details`格式返回结构化元数据。

常见的`details`字段：

- `model`：已解析的模型引用(`provider/model`)
- `native`：原生提供商模式下的`true`，回退模式下的`false`
- `attempts`：成功之前的失败回退尝试次数

路径字段：

- 单个PDF输入：`details.pdf`
- 多个PDF输入：具有`pdf`条目的`details.pdfs[]`
- 沙箱路径重写元数据（适用时）：`rewrittenFrom`

## 错误行为

- 缺少PDF输入：抛出`pdf required: provide a path or URL to a PDF document`
- PDF过多：在`details.error = "too_many_pdfs"`中返回结构化错误
- 不支持的引用方案：返回`details.error = "unsupported_pdf_reference"`
- 带有`pages`的原生模式：抛出明确的`pages is not supported with native PDF providers`错误

## 示例

单个PDF：

```json
{
  "pdf": "/tmp/report.pdf",
  "prompt": "Summarize this report in 5 bullets"
}
```

多个PDF：

```json
{
  "pdfs": ["/tmp/q1.pdf", "/tmp/q2.pdf"],
  "prompt": "Compare risks and timeline changes across both documents"
}
```

带有页面过滤的回退模型：

```json
{
  "pdf": "https://example.com/report.pdf",
  "pages": "1-3,7",
  "model": "openai/gpt-5-mini",
  "prompt": "Extract only customer-impacting incidents"
}
```