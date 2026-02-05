---
summary: "Apply multi-file patches with the apply_patch tool"
read_when:
  - You need structured file edits across multiple files
  - You want to document or debug patch-based edits
title: "apply_patch Tool"
---
# apply_patch 工具

使用结构化补丁格式应用文件更改。这对于多文件或多段编辑非常理想，其中单个 `edit` 调用会变得脆弱。

该工具接受一个包含一个或多个文件操作的 `input` 字符串：

```
*** Begin Patch
*** Add File: path/to/file.txt
+line 1
+line 2
*** Update File: src/app.ts
@@
-old line
+new line
*** Delete File: obsolete.txt
*** End Patch
```

## 参数

- `input`（必需）：完整的补丁内容，包括 `*** Begin Patch` 和 `*** End Patch`。

## 注意事项

- 路径相对于工作区根目录解析。
- 在 `*** Update File:` 段中使用 `*** Move to:` 重命名文件。
- 当需要时，`*** End of File` 标记仅插入EOF。
- 实验性功能，默认情况下处于禁用状态。通过 `tools.exec.applyPatch.enabled` 启用。
- 仅限OpenAI（包括OpenAI Codex）。可选地通过模型启用 `tools.exec.applyPatch.allowModels`。
- 配置仅在 `tools.exec` 下进行。

## 示例

```json
{
  "tool": "apply_patch",
  "input": "*** Begin Patch\n*** Update File: src/index.ts\n@@\n-const foo = 1\n+const foo = 2\n*** End Patch"
}
```