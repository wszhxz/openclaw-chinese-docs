#!/bin/bash

# 本地翻译脚本，使用Ollama模型
echo "开始本地翻译任务..."
echo "使用Ollama qwen3:8b模型进行翻译"

# 检查Ollama服务是否运行
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "错误: Ollama服务未运行，请先启动Ollama服务"
    echo "启动命令: ollama serve"
    exit 1
fi

# 检查qwen3:8b模型是否存在
if curl -s http://127.0.0.1:11434/api/tags | grep -q "qwen3:8b"; then
    echo "找到qwen3:8b模型，开始翻译..."
else
    echo "错误: 未找到qwen3:8b模型，请先下载模型"
    echo "下载命令: ollama pull qwen3:8b"
    exit 1
fi

# 运行翻译脚本，启用Ollama
python scripts/translate_multi_service.py \
  --source-dir temp_for_translation \
  --target-dir docs \
  --source-lang en \
  --target-lang zh \
  --enable-ollama \
  --ollama-model "qwen3:8b" \
  --ollama-url "http://127.0.0.1:11434/v1" \
  --max-retries 1

echo "本地翻译任务完成！"