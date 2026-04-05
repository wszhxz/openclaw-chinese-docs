---
summary: "CLI reference for `openclaw docs` (search the live docs index)"
read_when:
  - You want to search the live OpenClaw docs from the terminal
title: "docs"
---
# `openclaw docs`

搜索实时文档索引。

参数：

- `[query...]`: 要发送至实时文档索引的搜索词

示例：

```bash
openclaw docs
openclaw docs browser existing-session
openclaw docs sandbox allowHostControl
openclaw docs gateway token secretref
```

注意：

- 若无查询，`openclaw docs` 将打开实时文档搜索入口点。
- 多词查询将作为一个搜索请求传递。