#!/bin/bash

# 本地工作流程03：文档翻译脚本
# 相当于在本地运行03号GitHub工作流

set -e  # 遇到错误时退出

echo "==================================="
echo "本地工作流程03：文档翻译"
echo "使用Ollama qwen3:8b模型进行翻译"
echo "==================================="

# 检查Ollama服务是否运行
echo "检查Ollama服务..."
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "错误: Ollama服务未运行，请先启动Ollama服务"
    echo "启动命令: ollama serve"
    exit 1
fi

# 检查qwen3:8b模型是否存在
echo "检查qwen3:8b模型..."
if curl -s http://127.0.0.1:11434/api/tags | grep -q "qwen3:8b"; then
    echo "✓ 找到qwen3:8b模型"
else
    echo "错误: 未找到qwen3:8b模型，请先下载模型"
    echo "下载命令: ollama pull qwen3:8b"
    exit 1
fi

# 检查temp_for_translation目录是否存在且有内容
if [ ! -d "temp_for_translation" ] || [ -z "$(ls -A temp_for_translation 2>/dev/null)" ]; then
    echo "错误: temp_for_translation目录不存在或为空"
    echo "请确保有需要翻译的文档在此目录中"
    exit 1
else
    echo "✓ temp_for_translation目录存在且有内容"
    echo "  文件数量: $(find temp_for_translation -type f | wc -l)"
fi

# 运行翻译脚本，启用Ollama
echo "开始翻译文档..."
echo "使用Ollama qwen3:8b模型..."

start_time=$(date +%s)
python3 scripts/translate_multi_service.py \
  --source-dir temp_for_translation \
  --target-dir docs \
  --source-lang en \
  --target-lang zh \
  --enable-ollama \
  --ollama-model "qwen3:8b" \
  --ollama-url "http://127.0.0.1:11434/v1" \
  --max-retries 1
end_time=$(date +%s)

duration=$((end_time - start_time))
echo "翻译完成！耗时: ${duration}秒"

# 检查是否成功生成了docs目录
if [ -d "docs" ] && [ -n "$(ls -A docs 2>/dev/null)" ]; then
    echo "✓ 文档翻译成功，已生成docs目录"
    echo "  翻译文件数量: $(find docs -type f | wc -l)"
    
    # 删除旧的temp_for_translation目录
    echo "清理temp_for_translation目录..."
    rm -rf temp_for_translation
    
    echo "==================================="
    echo "本地工作流程03完成！"
    echo "接下来您可以："
    echo "1. 检查docs目录中的翻译结果"
    echo "2. 如果满意，执行: git add . && git commit -m 'Translate: Add translated documents' && git push"
    echo "==================================="
else
    echo "✗ 翻译可能失败，docs目录未生成或为空"
    exit 1
fi