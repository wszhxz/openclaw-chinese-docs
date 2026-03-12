---
title: "Diffs"
summary: "Read-only diff viewer and file renderer for agents (optional plugin tool)"
description: "Use the optional Diffs plugin to render before and after text or unified patches as a gateway-hosted diff view, a file (PNG or PDF), or both."
read_when:
  - You want agents to show code or markdown edits as diffs
  - You want a canvas-ready viewer URL or a rendered diff file
  - You need controlled, temporary diff artifacts with secure defaults
---
# Diffs

`diffs` 是一个可选的插件工具，带有简短的内置系统指南和一个配套技能，可以将变更内容转换为供代理使用的只读差异工件。

它可以接受：

- `before` 和 `after` 文本
- 统一的 `patch`

它可以返回：

- 用于画布展示的网关查看器 URL
- 渲染文件路径（PNG 或 PDF）用于消息传递
- 在一次调用中同时提供两种输出

启用后，插件会在系统提示空间中添加简洁的使用指南，并在代理需要更完整说明的情况下暴露详细的技能。

## 快速开始

1. 启用插件。
2. 对于以画布为主的流程，使用 `diffs` 调用 `mode: "view"`。
3. 对于聊天文件传递流程，使用 `diffs` 调用 `mode: "file"`。
4. 当你需要两种工件时，使用 `diffs` 调用 `mode: "both"`。

## 启用插件

```json5
{
  plugins: {
    entries: {
      diffs: {
        enabled: true,
      },
    },
  },
}
```

## 禁用内置系统指南

如果你想保持 `diffs` 工具启用但禁用其内置系统提示指南，请将 `plugins.entries.diffs.hooks.allowPromptInjection` 设置为 `false`：

```json5
{
  plugins: {
    entries: {
      diffs: {
        enabled: true,
        hooks: {
          allowPromptInjection: false,
        },
      },
    },
  },
}
```

这会阻止 diffs 插件的 `before_prompt_build` 钩子，同时保持插件、工具和配套技能可用。

如果想同时禁用指南和工具，请禁用插件。

## 典型代理工作流程

1. 代理调用 `diffs`。
2. 代理读取 `details` 字段。
3. 代理可以选择：
   - 使用 `canvas present` 打开 `details.viewerUrl`
   - 使用 `path` 或 `filePath` 发送 `details.filePath` 和 `message`
   - 同时进行以上两项操作

## 输入示例

之前和之后：

```json
{
  "before": "# Hello\n\nOne",
  "after": "# Hello\n\nTwo",
  "path": "docs/example.md",
  "mode": "view"
}
```

补丁：

```json
{
  "patch": "diff --git a/src/example.ts b/src/example.ts\n--- a/src/example.ts\n+++ b/src/example.ts\n@@ -1 +1 @@\n-const x = 1;\n+const x = 2;\n",
  "mode": "both"
}
```

## 工具输入参考

除非特别注明，所有字段都是可选的：

- `before` (`string`)：原始文本。当省略 `patch` 时，与 `after` 一起需要。
- `after` (`string`)：更新后的文本。当省略 `patch` 时，与 `before` 一起需要。
- `patch` (`string`)：统一的差异文本。与 `before` 和 `after` 相互排斥。
- `path` (`string`)：前后模式下的显示文件名。
- `lang` (`string`)：前后模式下的语言覆盖提示。
- `title` (`string`)：查看器标题覆盖。
- `mode` (`"view" | "file" | "both"`)：输出模式。默认为插件默认值 `defaults.mode`。
- `theme` (`"light" | "dark"`)：查看器主题。默认为插件默认值 `defaults.theme`。
- `layout` (`"unified" | "split"`)：差异布局。默认为插件默认值 `defaults.layout`。
- `expandUnchanged` (`boolean`)：当有完整上下文时展开未更改部分。仅限每次调用选项（不是插件默认键）。
- `fileFormat` (`"png" | "pdf"`)：渲染文件格式。默认为插件默认值 `defaults.fileFormat`。
- `fileQuality` (`"standard" | "hq" | "print"`)：PNG 或 PDF 渲染的质量预设。
- `fileScale` (`number`)：设备缩放覆盖 (`1`-`4`)。
- `fileMaxWidth` (`number`)：最大渲染宽度（CSS 像素，`640`-`2400`）。
- `ttlSeconds` (`number`)：查看器工件的 TTL（秒）。默认 1800 秒，最大 21600 秒。
- `baseUrl` (`string`)：查看器 URL 源覆盖。必须是 `http` 或 `https`，不允许查询/哈希。

验证和限制：

- `before` 和 `after` 每个最大 512 KiB。
- `patch` 最大 2 MiB。
- `path` 最大 2048 字节。
- `lang` 最大 128 字节。
- `title` 最大 1024 字节。
- 补丁复杂度上限：最多 128 个文件和总计 120000 行。
- `patch` 和 `before` 或 `after` 一起被拒绝。
- 渲染文件安全限制（适用于 PNG 和 PDF）：
  - `fileQuality: "standard"`：最大 8 MP（8,000,000 渲染像素）。
  - `fileQuality: "hq"`：最大 14 MP（14,000,000 渲染像素）。
  - `fileQuality: "print"`：最大 24 MP（24,000,000 渲染像素）。
  - PDF 还有一个最大 50 页的限制。

## 输出详细信息合同

该工具在 `details` 下返回结构化元数据。

创建查看器模式的共享字段：

- `artifactId`
- `viewerUrl`
- `viewerPath`
- `title`
- `expiresAt`
- `inputKind`
- `fileCount`
- `mode`

当渲染 PNG 或 PDF 时的文件字段：

- `filePath`
- `path`（与 `filePath` 的值相同，为了消息工具兼容性）
- `fileBytes`
- `fileFormat`
- `fileQuality`
- `fileScale`
- `fileMaxWidth`

模式行为摘要：

- `mode: "view"`：仅查看器字段。
- `mode: "file"`：仅文件字段，无查看器工件。
- `mode: "both"`：查看器字段加上文件字段。如果文件渲染失败，查看器仍会返回 `fileError`。

## 折叠未更改部分

- 查看器可以显示像 `N unmodified lines` 这样的行。
- 这些行上的展开控件是有条件的，并非每种输入类型都保证出现。
- 当渲染的差异具有可扩展的上下文数据时，会出现展开控件，这是前后输入的典型情况。
- 对于许多统一补丁输入，省略的上下文主体在解析的补丁块中不可用，因此该行可能没有展开控件。这是预期的行为。
- `expandUnchanged` 仅在存在可扩展上下文时适用。

## 插件默认设置

在 `~/.openclaw/openclaw.json` 中设置插件范围的默认值：

```json5
{
  plugins: {
    entries: {
      diffs: {
        enabled: true,
        config: {
          defaults: {
            fontFamily: "Fira Code",
            fontSize: 15,
            lineSpacing: 1.6,
            layout: "unified",
            showLineNumbers: true,
            diffIndicators: "bars",
            wordWrap: true,
            background: true,
            theme: "dark",
            fileFormat: "png",
            fileQuality: "standard",
            fileScale: 2,
            fileMaxWidth: 960,
            mode: "both",
          },
        },
      },
    },
  },
}
```

支持的默认值：

- `fontFamily`
- `fontSize`
- `lineSpacing`
- `layout`
- `showLineNumbers`
- `diffIndicators`
- `wordWrap`
- `background`
- `theme`
- `fileFormat`
- `fileQuality`
- `fileScale`
- `fileMaxWidth`
- `mode`

显式工具参数会覆盖这些默认值。

## 安全配置

- `security.allowRemoteViewer` (`boolean`, 默认 `false`)
  - `false`：到查看器路由的非回环请求被拒绝。
  - `true`：如果令牌化路径有效，则允许远程查看器。

示例：

```json5
{
  plugins: {
    entries: {
      diffs: {
        enabled: true,
        config: {
          security: {
            allowRemoteViewer: false,
          },
        },
      },
    },
  },
}
```

## 工件生命周期和存储

- 工件存储在临时子文件夹下：`$TMPDIR/openclaw-diffs`。
- 查看器工件元数据包含：
  - 随机工件 ID（20 个十六进制字符）
  - 随机令牌（48 个十六进制字符）
  - `createdAt` 和 `expiresAt`
  - 存储的 `viewer.html` 路径
- 默认查看器 TTL 为 30 分钟（未指定时）。
- 接受的最大查看器 TTL 为 6 小时。
- 在工件创建后机会性地运行清理。
- 过期的工件将被删除。
- 备用清理会移除缺少元数据且超过 24 小时的陈旧文件夹。

## 查看器 URL 和网络行为

查看器路由：

- `/plugins/diffs/view/{artifactId}/{token}`

查看器资源：

- `/plugins/diffs/assets/viewer.js`
- `/plugins/diffs/assets/viewer-runtime.js`

URL 构建行为：

- 如果提供了 `baseUrl`，则在严格验证后使用。
- 如果没有 `baseUrl`，查看器 URL 默认为回环 `127.0.0.1`。
- 如果网关绑定模式为 `custom` 并设置了 `gateway.customBindHost`，则使用该主机。

`baseUrl` 规则：

- 必须是 `http://` 或 `https://`。
- 查询和哈希被拒绝。
- 允许源加上可选的基本路径。

## 安全模型

查看器加固：

- 默认仅回环。
- 带有严格 ID 和令牌验证的令牌化查看器路径。
- 查看器响应 CSP：
  - `default-src 'none'`
  - 仅从自身加载脚本和资源
  - 无出站 `connect-src`
- 启用远程访问时的远程错失节流：
  - 每 60 秒 40 次失败
  - 60 秒锁定（`429 Too Many Requests`）

文件渲染加固：

- 截图浏览器请求路由默认拒绝。
- 仅允许来自 `http://127.0.0.1/plugins/diffs/assets/*` 的本地查看器资源。
- 阻止外部网络请求。

## 文件模式的浏览器要求

`mode: "file"` 和 `mode: "both"` 需要与 Chromium 兼容的浏览器。

解析顺序：

1. OpenClaw 配置中的 `browser.executablePath`。
2. 环境变量：
   - `OPENCLAW_BROWSER_EXECUTABLE_PATH`
   - `BROWSER_EXECUTABLE_PATH`
   - `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`
3. 平台命令/路径发现回退。

常见的失败文本：

- `Diff PNG/PDF rendering requires a Chromium-compatible browser...`

通过安装 Chrome、Chromium、Edge 或 Brave，或设置上述可执行路径选项之一来修复。

## 故障排除

输入验证错误：

- `Provide patch or both before and after text.`
  - 包括 `before` 和 `after`，或提供 `patch`。
- `Provide either patch or before/after input, not both.`
  - 不要混合输入模式。
- `Invalid baseUrl: ...`
  - 使用 `http(s)` 源，可选路径，无查询/哈希。
- `{field} exceeds maximum size (...)`
  - 减少负载大小。
- 大补丁拒绝
  - 减少补丁文件数量或总行数。

查看器访问问题：

- 查看器 URL 默认解析为 `127.0.0.1`。
- 对于远程访问场景，可以：
  - 每次工具调用时传递 `baseUrl`，或
  - 使用 `gateway.bind=custom` 和 `gateway.customBindHost`
- 仅当你打算进行外部查看器访问时才启用 `security.allowRemoteViewer`。

未修改行的行没有展开按钮：

- 对于补丁输入，当补丁不携带可扩展上下文时，这种情况可能发生。
- 这是预期的行为，并不表示查看器故障。

找不到工件：

- 工件因TTL到期。
- 令牌或路径已更改。
- 清理移除了陈旧数据。

## 操作指南

- 对于本地交互式审查，优先使用`mode: "view"`。
- 对于需要附件的外发聊天渠道，优先使用`mode: "file"`。
- 除非部署需要远程查看器URL，否则保持`allowRemoteViewer`禁用状态。
- 为敏感差异设置明确的短`ttlSeconds`。
- 除非必要，否则避免在差异输入中发送密钥。
- 如果您的渠道对图像进行强力压缩（例如Telegram或WhatsApp），请优先选择PDF输出(`fileFormat: "pdf"`)。

差异渲染引擎：

- 由[Diffs](https://diffs.com)提供支持。

## 相关文档

- [工具概述](/tools)
- [插件](/tools/plugin)
- [浏览器](/tools/browser)