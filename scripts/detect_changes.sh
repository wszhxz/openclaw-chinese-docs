#!/bin/bash

# 改进的变更检测脚本
# 比较 original-en 和 main 分支，识别需要翻译的文件
# 不仅比较文件列表，还比较内容差异

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
cp -r docs/* /tmp/original_en_docs/ 2>/dev/null || echo "No docs to copy"

# 切换回 main 分支
git checkout main 2>/dev/null

# 获取 main 分支的文件列表
find docs -name "*.md" -type f | sed 's|^docs/||' > /tmp/current_main_files.txt

# 比较文件列表，找出在 original-en 中有但在 main 中没有的文件（新文件）
comm -13 <(sort /tmp/current_main_files.txt) <(sort /tmp/original_en_files.txt) > /tmp/new_files.txt

# 检查现有文件的内容差异
echo "正在检查现有文件的内容差异..."
> /tmp/modified_files.txt  # 清空文件

while IFS= read -r file; do
  if [ -f "/tmp/original_en_docs/$file" ] && [ -f "docs/$file" ]; then
    # 比较文件内容，忽略前几行的元数据差异（如日期等）
    original_content=$(grep -vE '^ *#' /tmp/original_en_docs/"$file" | grep -v "^---$" | grep -v "^title:" | grep -v "^summary:" | head -50)
    main_content=$(grep -vE '^ *#' docs/"$file" | grep -v "^---$" | grep -v "^title:" | grep -v "^summary:" | head -50)
    
    if [ "$original_content" != "$main_content" ]; then
      echo "$file" >> /tmp/modified_files.txt
      echo "检测到内容差异: $file"
    fi
  fi
done < <(comm -12 <(sort /tmp/current_main_files.txt) <(sort /tmp/original_en_files.txt))

# 合并新文件和修改过的文件
cat /tmp/new_files.txt /tmp/modified_files.txt > /tmp/new_or_modified_files.txt

# 检查是否有需要翻译的文件
if [ -s /tmp/new_or_modified_files.txt ]; then
    echo "发现需要翻译的文件："
    cat /tmp/new_or_modified_files.txt
    echo "NUMBER_OF_FILES=$(wc -l < /tmp/new_or_modified_files.txt)" > /tmp/translation_status.txt
    echo "TRANSLATION_STATUS=needed" >> /tmp/translation_status.txt
    echo "FILES_TO_TRANSLATE=/tmp/new_or_modified_files.txt" >> /tmp/translation_status.txt
else
    echo "没有发现需要翻译的新或修改过的文件"
    echo "TRANSLATION_STATUS=no-changes" > /tmp/translation_status.txt
fi

# 清理临时文件
rm -f /tmp/original_en_files.txt /tmp/current_main_files.txt /tmp/new_files.txt /tmp/modified_files.txt
rm -rf /tmp/original_en_docs

echo "变更检测完成"

# 确保返回 main 分支
git checkout main 2>/dev/null || echo "Already on main or error occurred"
