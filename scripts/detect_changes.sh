#!/bin/bash

# 正确的变更检测脚本
# 比较 original-en 和 main 分支，识别需要翻译或更新的文件
# 基于文件内容哈希值进行比较

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

echo "开始检测文档变更..."

# 获取所有分支
git fetch origin

# 临时切换到 original-en 分支
git checkout -b original-en origin/original-en 2>/dev/null || git checkout original-en

# 获取 original-en 分支的文件列表
find docs -name "*.md" -type f | sed 's|^docs/||' > /tmp/original_en_files.txt

# 创建临时目录存储 original-en 版本的文件
mkdir -p /tmp/original_en_docs
find docs -name "*.md" -type f -exec cp --parents {} /tmp/original_en_docs/ \;

# 切换回 main 分支
git checkout main 2>/dev/null

# 获取 main 分支的文件列表
find docs -name "*.md" -type f | sed 's|^docs/||' > /tmp/current_main_files.txt

# 创建临时目录存储 main 版本的文件
mkdir -p /tmp/main_docs
find docs -name "*.md" -type f -exec cp --parents {} /tmp/main_docs/ \;

# 查找需要翻译的新文件（在 original-en 中有但在 main 中没有的）
comm -23 <(sort /tmp/original_en_files.txt) <(sort /tmp/current_main_files.txt) > /tmp/new_files.txt

# 查找需要更新翻译的文件（同名但内容不同）
echo "正在检查同名文件的内容差异..."
> /tmp/updated_files.txt  # 清空文件

while IFS= read -r file; do
  if [ -f "/tmp/original_en_docs/docs/$file" ] && [ -f "/tmp/main_docs/docs/$file" ]; then
    # 计算两个版本的哈希值（排除元数据部分）
    original_hash=$(grep -vE '^[[:space:]]*([a-zA-Z]+:|#|\-\-\-)' /tmp/original_en_docs/docs/"$file" | shasum -a 256 | cut -d' ' -f1)
    main_hash=$(grep -vE '^[[:space:]]*([a-zA-Z]+:|#|\-\-\-)' /tmp/main_docs/docs/"$file" | shasum -a 256 | cut -d' ' -f1)
    
    if [ "$original_hash" != "$main_hash" ]; then
      echo "$file" >> /tmp/updated_files.txt
      echo "检测到内容更新: $file"
    fi
  fi
done < <(comm -12 <(sort /tmp/current_main_files.txt) <(sort /tmp/original_en_files.txt))

# 合并新文件和内容更新的文件
cat /tmp/new_files.txt /tmp/updated_files.txt > /tmp/new_or_modified_files.txt

# 检查是否有需要处理的文件
total_files=$(wc -l < /tmp/new_or_modified_files.txt)
total_files=$(echo $total_files | tr -d ' ')  # 移除多余的空格

if [ "$total_files" -gt 0 ]; then
    echo "发现 $total_files 个需要翻译或更新的文件："
    cat /tmp/new_or_modified_files.txt
    echo "NUMBER_OF_FILES=$total_files" > /tmp/translation_status.txt
    echo "TRANSLATION_STATUS=needed" >> /tmp/translation_status.txt
    echo "FILES_TO_TRANSLATE=/tmp/new_or_modified_files.txt" >> /tmp/translation_status.txt
else
    echo "没有发现需要翻译或更新的文件"
    echo "TRANSLATION_STATUS=no-changes" > /tmp/translation_status.txt
fi

# 清理临时文件
rm -f /tmp/original_en_files.txt /tmp/current_main_files.txt /tmp/new_files.txt /tmp/updated_files.txt
rm -rf /tmp/original_en_docs /tmp/main_docs

echo "变更检测完成"

# 确保返回 main 分支
git checkout main 2>/dev/null || echo "Already on main or error occurred"
