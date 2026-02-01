#!/bin/bash

# 变更检测脚本 - 实现思维导图中的变更检测功能
# 比较 original-en 和 main 分支，识别需要翻译的文件

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

echo "开始检测文档变更..."

# 获取所有分支
git fetch origin

# 临时切换到 original-en 分支获取文件列表
git checkout -b original-en origin/original-en 2>/dev/null || git checkout original-en
find docs -name "*.md" -type f | sed 's|^docs/||' > /tmp/original_en_files.txt

# 切换回 main 分支获取当前文件列表
git checkout main 2>/dev/null
find docs -name "*.md" -type f | sed 's|^docs/||' > /tmp/current_main_files.txt

# 比较文件列表，找出新增或修改的文件
echo "正在比较文件变更..."
comm -13 <(sort /tmp/current_main_files.txt) <(sort /tmp/original_en_files.txt) > /tmp/new_or_modified_files.txt

# 检查是否有变更
if [ -s /tmp/new_or_modified_files.txt ]; then
    echo "发现需要翻译的文件："
    cat /tmp/new_or_modified_files.txt
    echo "NUMBER_OF_FILES=$(wc -l < /tmp/new_or_modified_files.txt)" > /tmp/translation_status.txt
    echo "TRANSLATION_STATUS=needed" >> /tmp/translation_status.txt
    echo "FILES_TO_TRANSLATE=/tmp/new_or_modified_files.txt" >> /tmp/translation_status.txt
else
    echo "没有发现需要翻译的新文件"
    echo "TRANSLATION_STATUS=up-to-date" > /tmp/translation_status.txt
fi

# 清理临时文件
rm -f /tmp/original_en_files.txt /tmp/current_main_files.txt

echo "变更检测完成"
