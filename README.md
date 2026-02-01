# OpenClaw 中文文档项目

## 项目概述

本项目致力于将 OpenClaw 英文文档完整翻译为中文，方便中文用户阅读和使用。

## 分支管理策略

本项目采用双分支管理模式：

- **`main` 分支**：存放中文翻译文档
  - 包含所有文档的中文翻译版本
  - 用于 GitHub Pages 部署
  - 通过 Jekyll 配置优化中文显示

- **`original-en` 分支**：存放原始英文文档
  - 与上游 openclaw/openclaw 仓库保持同步
  - 作为翻译工作的参考基准
  - 便于追踪英文原文的更新

## 文档结构

- `/docs/` - 存放所有文档文件
- `_config.yml` - Jekyll 配置文件
- `_layouts/` - 页面布局模板
- `assets/` - 静态资源（CSS、图片等）

## 翻译进度

- 总计文档：298 个
- 已翻译文档：223 个（约 75%）
- 待翻译文档：75 个

## 自动化工作流

项目集成了分布式翻译自动化系统，能够：

1. 检测英文原文的更新
2. 自动分配翻译任务
3. 同步更改到 GitHub
4. 监控翻译进度

## 贡献指南

### 添加新翻译

1. 切换到 `original-en` 分支查看原文
2. 在 `main` 分支中创建对应的中文翻译
3. 确保使用正确的 permalink 配置
4. 提交 PR 到 `main` 分支

### 同步上游变更

```bash
# 更新英文原文分支
git fetch upstream
git checkout original-en
git merge upstream/main

# 在 main 分支中合并上游变更
git checkout main
# 手动合并新增的英文文档到中文翻译
```

## 部署

网站通过 GitHub Pages 自动部署，地址：
https://wszhxz.github.io/openclaw-chinese-docs/

## 技术特性

- 支持中文内容的 Jekyll 配置
- 优化的导航和链接结构
- 正确的资源文件引用路径
- GitHub Pages 兼容的目录结构