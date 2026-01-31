# 建议的工作流配置更新

为了让工作流能够在推送时自动触发，建议更新 `.github/workflows/auto-translate.yml` 文件，在 `on:` 部分添加 push 触发器：

```yaml
on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      batch_size:
        description: 'Number of files to process per batch (default: 5)'
        required: false
        default: '5'
```

这样，任何推送到 main 分支的操作都会触发工作流运行。