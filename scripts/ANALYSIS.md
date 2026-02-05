# OpenClaw 中文文档项目 - Scripts 目录分析

## 项目概述
OpenClaw 中文文档项目是一个由 AI 助理全程自动化管理的 OpenClaw 中文文档翻译项目。该项目通过智能化的工作流系统，实现了从英文文档同步、中文翻译、质量控制到网站部署的全流程自动化。

## Scripts 目录结构分析

### 核心功能脚本

#### 1. 同步类脚本
- `sync_from_upstream.sh`: 同步英文文档到 original-en 分支
- `create_original_branch.sh`: 创建 original-en 分支
- `compare_branches.sh`: 比较分支差异

#### 2. 检测类脚本
- `detect_changes.sh`: 检测 original-en 分支相对于 main 分支的变更
- `detect_and_copy_new_docs.sh`: 检测并复制新文档

#### 3. 翻译类脚本
- `translate_with_ollama.py`: 使用本地 Ollama 服务进行文档翻译
- `translate_with_libre.py`: 使用 LibreTranslate 进行翻译
- `translate_with_libre_updated.py`: 更新版本的 LibreTranslate 翻译
- `translate_with_llm.py`: 使用大语言模型进行翻译
- `translate_with_llm_chunked.py`: 分块处理的大语言模型翻译
- `translate_with_retry.py`: 带重试机制的翻译脚本
- `translate_multi_service.py`: 多服务翻译脚本
- `translate-docs.js`: JavaScript 版本的翻译脚本

#### 4. 工作流管理脚本
- `master_workflow_final.sh`: 主工作流脚本
- `local_workflow_03.sh`: 本地工作流脚本
- `distributed_translation.sh`: 分布式翻译脚本
- `manage-translation-tasks.sh`: 管理翻译任务脚本

#### 5. 质量控制脚本
- `monitor_translation_progress.py`: 监控翻译进度
- `localize_nav_config.py`: 导航配置本地化工具
- `backup_existing_translations.sh`: 备份现有翻译

#### 6. 系统管理脚本
- `check-workflow-status.js`: 检查工作流状态
- `monitor-workflow.js`: 监控工作流
- `setup_libretranslate.sh`: 设置 LibreTranslate
- `run_local_translation.sh`: 运行本地翻译

### 项目配置文件
- `process-file.js`: 文件处理脚本
- `check-workflow-status.sh`: 检查工作流状态脚本

## 技术架构特点

### 1. 双分支管理
- `main` 分支：存放中文翻译文档
- `original-en` 分支：存放原始英文文档
- 自动检测英文文档更新并触发翻译流程

### 2. AI 驱动的自动化
- 智能同步：自动从上游仓库同步英文文档
- 变更检测：智能识别新增/修改的文档
- 自动翻译：按需启动翻译任务
- 质量保证：保护现有翻译成果不被覆盖

### 3. 多翻译引擎支持
- Ollama 本地模型
- LibreTranslate 服务
- 大语言模型 (LLM)
- 带重试和错误处理机制

### 4. GitHub Actions 工作流
- `01_sync-dual-branch.yml`: 每天凌晨2点同步英文文档
- `03_translate-by-directory.yml`: 触发翻译流程
- `04_translation-review.yml`: 翻译审核流程

## 项目状态
- 文档总数: 已完成全站翻译
- 翻译进度: 100% (持续自动化维护)
- 更新频率: 每天同步一次上游更新
- 部署状态: 自动化部署到 GitHub Pages

## 目录规模
Scripts 目录包含约 30 多个脚本文件，涵盖：
- Bash 脚本 (15+ 个)
- Python 脚本 (8 个)
- JavaScript 文件 (3 个)

这是一个高度自动化、智能化的文档翻译项目，体现了现代 AI 驱动的软件开发和文档管理的最佳实践。