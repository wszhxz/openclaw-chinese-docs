---
summary: "Apply multi-file patches with the apply_patch tool"
read_when:
  - You need structured file edits across multiple files
  - You want to document or debug patch-based edits
title: "apply_patch Tool"
---
# apply_patch 工具

使用结构化补丁格式应用文件更改。这适用于需要对多个文件或多个hunk进行编辑的情况，此时单个`edit`调用会很脆弱。

该工具接受一个包含一个或多个文件操作的`input`字符串：

```
*** 开始补丁
*** 添加文件: path/to/file.txt
+line 1
+line 2
*** 更新文件: src/app.ts
@@
-old line
+new line
*** 删除文件: obsolete.txt
*** 结束补丁
```

## 参数

- `input`（必填）：包含`*** 开始补丁`和`*** 结束补丁`的完整补丁内容。

## 说明

- 路径相对于工作区根目录解析。
- 在`*** 更新文件:` hunk中使用`*** 移动到:`可重命名文件。
- `*** 结束文件`表示仅在文件末尾插入。
- 实验性功能，默认禁用。可通过`tools.exec.applyPatch.enabled`启用。
- 仅限OpenAI（包括OpenAI Codex）。可通过`tools.exec.applyPatch.allowModels`按模型进行限制。
- 配置仅位于`tools.exec`下。

## 示例

```json
{
  "tool": "apply_patch",
  "input": "*** 开始补丁\n*** 更新文件: src/index.ts\n@@\n-const foo = 1\n+const foo = 2\n*** 结束补丁"
}
```