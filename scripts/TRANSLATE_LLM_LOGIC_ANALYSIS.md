# translate_with_llm.py 脚本运行逻辑分析

## 脚本概述
这是一个使用大语言模型进行文档翻译的Python脚本，支持多种翻译服务提供商，主要用于OpenClaw中文文档项目的自动化翻译。

## 主要功能模块

### 1. 文件类型判断
- `is_text_file(filepath)`: 判断文件是否为需要翻译的文本文件（.md, .mdx, .txt, .html, .htm, .yaml, .yml）

### 2. 内容预处理
- `extract_frontmatter(content)`: 提取YAML frontmatter（用于Jekyll等静态站点生成器）
- `protect_code_blocks(text)`: 保护代码块、HTML标签、行内代码等内容不被翻译
- `restore_protected_parts(text, protected_parts)`: 恢复受保护的内容

### 3. 多翻译服务支持
脚本支持四种翻译服务：

#### A. OpenAI翻译 (`translate_with_openai`)
- 使用OpenAI API（如gpt-3.5-turbo）
- 通过环境变量或参数获取API密钥
- 使用system prompt指导模型只翻译文本内容，保留代码块

#### B. Anthropic Claude翻译 (`translate_with_claude`)
- 使用Claude API
- 类似的保护机制和翻译提示

#### C. Qwen Portal翻译 (`translate_with_qwen_portal`)
- 使用阿里云通义千问API
- 支持多个模型变体（qwen-coder-plus, qwen-max, qwen-plus等）
- 包含模型验证功能

#### D. Ollama本地翻译 (`translate_with_ollama`)
- 使用本地Ollama服务
- 支持多种本地模型（llama3等）

### 4. 统一翻译接口
- `translate_with_any_llm()`: 根据配置调用指定的翻译服务
- 不再尝试fallback到其他提供商，直接使用指定的服务

### 5. 文件翻译
- `translate_file()`: 翻译单个文件
- 包含完整的错误处理和进度显示
- 保持frontmatter和代码块完整性

### 6. 目录批量处理
- `process_directory()`: 批量处理整个目录
- 支持重试机制（默认最多2次）
- 统计翻译进度和结果
- 包含GitHub Actions兼容的日志格式

## 运行流程

### 1. 初始化阶段
- 解析命令行参数
- 验证源目录存在
- 构建翻译配置

### 2. 文件发现阶段
- 搜索源目录中的所有文件
- 检测是否存在docs子目录
- 统计待处理文件数量

### 3. 翻译执行阶段
- 遍历所有文件
- 对于文本文件：调用翻译函数
- 对于非文本文件：直接复制
- 实施重试机制处理失败的文件

### 4. 结果处理阶段
- 统计翻译结果
- 记录失败文件列表
- 提交Git更改

## 关键特性

### 1. 代码块保护
- 使用正则表达式识别和保护代码块（```...```）
- 保护行内代码（`...`）
- 保护HTML标签内容
- 防止代码被意外翻译

### 2. 错误处理和重试
- 完整的异常捕获机制
- 重试失败的翻译任务
- 详细的错误日志记录

### 3. 进度显示
- GitHub Actions兼容的日志格式
- 实时显示处理进度
- 详细的统计信息

### 4. Git集成
- 自动提交翻译结果
- 跳过CI标记避免无限循环

## 配置参数

### 必需参数
- `--source-dir`: 源目录（默认temp_for_translation）
- `--target-dir`: 目标目录（默认docs）
- `--provider`: 翻译服务提供商（qwen-portal, openai, claude, ollama）

### 服务特定参数
- API密钥（通过参数或环境变量）
- 模型名称
- 服务端点URL
- 重试次数设置

## 适用场景
- 自动化文档翻译项目
- 技术文档国际化
- 保持代码和格式的翻译任务
- GitHub Actions集成的CI/CD流程

这个脚本是一个设计完善的文档翻译工具，特别适用于技术文档的国际化工作，能够有效保持原文档的格式和代码完整性。