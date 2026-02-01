# OpenClaw 中文文档

此项目旨在提供 OpenClaw 项目的中文文档翻译。

## 项目状态

- ✅ 工作流：已修复并正常运行
- ✅ 文档同步：每12小时自动从上游仓库同步最新文档
- ✅ 翻译功能：基础框架已完成，已添加首页中文翻译
- ✅ 自动部署：翻译后的内容自动部署到 GitHub Pages

## 架构说明

- `.github/workflows/simple-sync.yml`：主要工作流，负责文档构建和部署
- `docs/`：存放中文文档源文件
- `_config.yml`：Jekyll 配置文件
- `Gemfile`：Ruby 依赖配置

## 工作流程

1. 每12小时，工作流会自动构建最新文档
2. 使用 Jekyll 将 Markdown 文档转换为静态网站
3. 将生成的网站部署到 GitHub Pages

## 贡献

如果您想帮助改进中文翻译，请参考以下步骤：

1. Fork 此仓库
2. 创建特性分支
3. 添加或改进翻译内容
4. 提交您的修改
5. 发起 Pull Request

## 许可证

此项目采用 MIT 许可证。