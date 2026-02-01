# OpenClaw 中文文档项目

<div align="center">
  <h3>🤖 AI 驱动的开源文档翻译项目</h3>
  <p><em>由 AI 助理自动维护的 OpenClaw 中文文档</em></p>
  
  [![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Deployed-green)](https://wszhxz.github.io/openclaw-chinese-docs/)
  [![AI Automated](https://img.shields.io/badge/AI_Automated-%F0%9F%A4%96-green)](https://github.com/wszhxz/openclaw-chinese-docs)
  [![Dual Branch Sync](https://img.shields.io/badge/Workflow-Dual_Branch_Sync-blue)](.github/workflows/)
  [![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
</div>

---

## 📖 项目简介

本项目是由 AI 助理全程自动化管理的 OpenClaw 中文文档翻译项目。通过智能化的工作流系统，实现了从英文文档同步、中文翻译、质量控制到网站部署的全流程自动化。

- **项目地址**: [https://wszhxz.github.io/openclaw-chinese-docs/](https://wszhxz.github.io/openclaw-chinese-docs/)
- **原始项目**: [https://github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
- **AI 助理**: 自动化维护与更新

## 🚀 核心特性

### 1. 智能双分支管理
- `main` 分支：存放中文翻译文档
- `original-en` 分支：存放原始英文文档
- 自动检测英文文档更新并触发翻译流程

### 2. 分布式自动化翻译
- 按目录结构分割翻译任务
- 自动识别需要翻译的新文档
- 保护已有的中文翻译成果

### 3. 全流程自动化
- 同步 → 翻译 → 构建 → 部署
- 每6小时自动检查上游更新
- 无需人工干预的持续维护

## 🛠️ 技术架构

### 工作流系统
| 工作流 | 功能 | 触发时间 |
|--------|------|----------|
| `sync-dual-branch.yml` | 双分支同步 | 每6小时 |
| `detect-changes.yml` | 变更检测 | 每6小时（同步后） |
| `translate-by-directory.yml` | 分布式翻译 | 检测到变更时 |
| `build-site.yml` | 网站构建部署 | 翻译完成后 |

### 核心技术栈
- **GitHub Actions**: 自动化工作流引擎
- **Jekyll**: 静态网站生成器
- **Git**: 版本控制与差异检测
- **Python/Node.js**: 脚本处理工具
- **AI 助理**: 智能决策与配置管理

## 📊 项目状态

- **文档总数**: ~298 篇
- **翻译进度**: 持续自动化更新
- **更新频率**: 每6小时同步一次上游更新
- **部署状态**: 自动化部署到 GitHub Pages

## 🤖 AI 助理管理

本项目由 AI 助理全程自动化管理，包括：

- **智能同步**: 自动从上游仓库同步英文文档
- **变更检测**: 智能识别新增/修改的文档
- **翻译调度**: 按需启动翻译任务
- **质量保证**: 保护现有翻译成果不被覆盖
- **部署维护**: 自动构建并部署网站

AI 助理持续监控项目状态，确保中文文档与英文原始文档保持同步更新。

## 📁 目录结构

```
├── docs/                 # 中文文档目录
│   ├── start/           # 入门指南
│   ├── gateway/         # 网关文档
│   ├── web/             # Web界面文档
│   ├── platforms/       # 平台相关
│   ├── tools/           # 工具文档
│   ├── concepts/        # 概念文档
│   └── ...              # 其他分类
├── .github/workflows/   # 自动化工作流
├── scripts/             # 辅助脚本
└── _config.yml          # Jekyll 配置
```

## 🔧 自定义配置

### 导航配置
- `docs.json`: Mintlify 导航配置（中文本地化）
- `_config.yml`: Jekyll 导航配置（中文本地化）
- `_layouts/default.html`: 导航渲染模板

### 自动化脚本
- `scripts/sync_from_upstream.sh`: 双分支同步脚本
- `scripts/detect_changes.sh`: 变更检测脚本
- `scripts/localize_nav_config.py`: 导航配置本地化工具

## 🤝 贡献指南

本项目由 AI 助理自动化维护，但仍欢迎社区贡献：

### 参与方式
1. **内容反馈**: 发现翻译问题可在 Issues 中报告
2. **改进建议**: 对自动化流程提出改进建议
3. **功能增强**: 提交 PR 优化脚本和工作流

### 贡献流程
1. Fork 仓库
2. 创建功能分支
3. 提交改进
4. 开启 Pull Request

## 📈 项目演进

### 当前状态
- ✅ 双分支管理系统已上线
- ✅ 自动化同步工作流已激活
- ✅ 分布式翻译系统已部署
- ✅ 网站自动构建与部署

### 未来计划
- 🔄 智能翻译质量评估
- 🔄 社区反馈整合机制
- 🔄 多语言支持扩展

## 📞 联系方式

- **GitHub Issues**: [Issues](https://github.com/wszhxz/openclaw-chinese-docs/issues)
- **项目主页**: [https://wszhxz.github.io/openclaw-chinese-docs/](https://wszhxz.github.io/openclaw-chinese-docs/)

## 📄 许可证

本项目遵循 MIT 许可证。详情请参见 [LICENSE](LICENSE) 文件。

---

<div align="center">
  <p><strong>🤖 由 AI 助理自动化维护 | 🔄 持续同步更新</strong></p>
  <p><em>让技术文档跨越语言障碍</em></p>
</div>