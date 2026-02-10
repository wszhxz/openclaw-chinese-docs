# AGENTS.md - ja-JP 文档翻译工作区

## 阅读时机

- 维护 `docs/ja-JP/**`
- 更新日语翻译流水线（术语表/记忆库/提示）
- 处理日语翻译反馈或回退

## 流水线 (docs-i18n)

- 源文档: `docs/**/*.md`
- 目标文档: `docs/ja-JP/**/*.md`
- 术语表: `docs/.i18n/glossary.ja-JP.json`
- 翻译记忆库: `docs/.i18n/ja-JP.tm.jsonl`
- 提示规则: `scripts/docs-i18n/prompt.go`

常见运行：

```bash
# Bulk (doc mode; parallel OK)
cd scripts/docs-i18n
go run . -docs ../../docs -lang ja-JP -mode doc -parallel 6 ../../docs/**/*.md

# Single file
cd scripts/docs-i18n
go run . -docs ../../docs -lang ja-JP -mode doc ../../docs/start/getting-started.md

# Small patches (segment mode; uses TM; no parallel)
cd scripts/docs-i18n
go run . -docs ../../docs -lang ja-JP -mode segment ../../docs/start/getting-started.md
```

注意事项：

- 整页翻译时优先使用 `doc` 模式；小修时使用 `segment` 模式。
- 如果非常大的文件超时，进行针对性编辑或在重新运行前拆分页面。
- 翻译后检查：代码片段/块未更改，链接/锚点未更改，占位符保留。