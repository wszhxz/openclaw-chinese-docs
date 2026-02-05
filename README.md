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

### 2. 自动化翻译流程
- 自动识别需要翻译的新文档
- 保护已有的中文翻译成果
- 完整的翻译质量保障机制

### 3. 全流程自动化
- 同步 → 翻译 → 构建 → 部署
- 每天凌晨2点自动检查上游更新
- 无需人工干预的持续维护

## 🛠️ 技术架构

### 工作流系统
| 工作流 | 功能 | 触发时间 |
|--------|------|----------|
| `01_sync-dual-branch.yml` | 同步原始项目并准备翻译 | 每周日凌晨2点 |
| `03_translate-by-directory.yml` | 自动化翻译 | 01工作流完成后 |
| `04_translation-review.yml` | 翻译质量审查 | 03工作流完成后 |

### 核心技术栈
- **GitHub Actions**: 自动化工作流引擎
- **Jekyll**: 静态网站生成器
- **Git**: 版本控制与差异检测
- **Python/Node.js**: 脚本处理工具
- **AI 助理**: 智能决策与配置管理

## 📊 项目状态

- **文档总数**: 已完成全站翻译
- **翻译进度**: 100% (持续自动化维护)
- **更新频率**: 每天同步一次上游更新
- **部署状态**: 自动化部署到 GitHub Pages

## 🤖 AI 助理管理

本项目由 AI 助理全程自动化管理，包括：

- **智能同步**: 自动从上游仓库同步英文文档
- **变更检测**: 智能识别新增/修改的文档
- **自动翻译**: 按需启动翻译任务
- **质量保证**: 保护现有翻译成果不被覆盖
- **部署维护**: 自动构建并部署网站

AI 助理持续监控项目状态，确保中文文档与英文原始文档保持同步更新。

## 📁 目录结构

```
├── docs/                    # 中文文档目录
│   ├── start/              # 入门指南
│   ├── gateway/            # 网关文档
│   ├── web/                # Web界面文档
│   ├── platforms/          # 平台相关
│   ├── channels/           # 通信渠道
│   ├── concepts/           # 概念文档
│   ├── tools/              # 工具文档
│   ├── cli/                # 命令行接口
│   ├── security/           # 安全文档
│   ├── providers/          # 服务提供商
│   ├── nodes/              # 节点管理
│   ├── install/            # 安装指南
│   ├── help/               # 帮助文档
│   ├── zh-CN/              # 中文本地化文档
│   └── ...                 # 其他分类
├── .github/workflows/      # 自动化工作流
├── scripts/                # 核心脚本
│   ├── translate_with_llm.py  # AI翻译主脚本
│   └── process-file.js     # 文件处理脚本
├── temp_for_translation/   # 待翻译文档临时目录
├── PROJECT_STRUCTURE.md    # 项目结构说明
├── _config.yml             # Jekyll 配置
├── .gitignore              # Git忽略配置
├── package.json            # Node.js依赖配置
├── Gemfile                 # Ruby依赖配置
└── README.md               # 项目说明
```

## 🔧 自定义配置

### 翻译配置
- `scripts/translate_with_llm.py`: AI翻译主脚本，使用qwen3-coder-plus模型
- `scripts/process-file.js`: 文件处理脚本，package.json中指定的主入口
- `_config.yml`: Jekyll站点配置

### 导航配置
- `scripts/localize_nav_config.py`: 导航配置本地化工具

### 工作流配置
- `.github/workflows/01_sync-dual-branch.yml`: 源项目同步工作流
- `.github/workflows/03_translate-by-directory.yml`: AI翻译工作流  
- `.github/workflows/04_translation-review.yml`: 翻译质量审查工作流

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
- ✅ 自动化翻译系统已部署（使用qwen3-coder-plus模型）
- ✅ 翻译质量审查机制已激活
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