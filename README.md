# OpenClaw 中文文档

这是 OpenClaw 项目的完整中文文档网站，由 GitHub Actions 自动翻译和维护。

## 项目概述

本文档项目基于 [OpenClaw](https://github.com/openclaw/openclaw) 官方文档自动翻译为中文。

**核心特点：**
- 完全自动化的翻译流程，无需人工干预
- 每小时检查上游更新并自动同步
- 基于 Jekyll 构建，与官方文档保持相同架构
- 零本地资源占用，全部处理在 GitHub Actions 中完成

## 自动化流程

项目采用全自动化工作流程：

1. **定时检查**：GitHub Actions 每小时检查 OpenClaw 项目更新
2. **自动翻译**：使用预定义术语表进行专业术语翻译
3. **质量保证**：保持与官方文档结构和格式的一致性
4. **自动部署**：翻译完成后自动部署到 GitHub Pages

## 技术栈

- GitHub Actions (自动化执行)
- Node.js (翻译脚本)
- Jekyll (网站构建)
- GitHub Pages (托管服务)

## 项目结构

- `scripts/translate-docs.js` - 自动翻译脚本
- `terminology.json` - 专业术语对照表
- `.github/workflows/auto-translate.yml` - 自动化工作流
- `docs/` - 翻译后的文档（由自动化流程生成）

## 贡献

如发现翻译质量问题，请提交 Issue。本项目专注于自动化翻译流程的优化。

## 许可证

遵循原项目的许可证协议。本项目为衍生作品，原项目版权归属于 OpenClaw 开发团队。