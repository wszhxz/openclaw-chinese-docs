#!/bin/bash

# 真正正确的变更检测脚本
# 比较 original-en 和 main 分支，识别需要翻译的文件
# 重点：检测 original-en 分支上存在但 main 分支上没有或不同的文档

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

echo "开始检测文档变更..."

# 获取所有分支
git fetch origin

# 从 original-en 分支获取文件列表
git checkout original-en 2>/dev/null
ORIGINAL_EN_FILES=$(find docs -name "*.md" -type f | sed 's|docs/||' | sort)

# 切换回 main 分支
git checkout main 2>/dev/null
MAIN_FILES=$(find docs -name "*.md" -type f | sed 's|docs/||' | sort)

# 检查每个 original-en 分支上的文件是否在 main 分支上存在
NEEDS_TRANSLATION=()

for file in $ORIGINAL_EN_FILES; do
    if [ ! -f "docs/$file" ]; then
        # 文件在 main 分支上不存在，需要翻译
        NEEDS_TRANSLATION+=("$file")
        echo "新文件需要翻译: $file"
    else
        # 文件在两个分支上都存在，比较内容（忽略元数据）
        ORIGINAL_CONTENT=$(cd .. && git show original-en:docs/"$file" 2>/dev/null | grep -vE '^[[:space:]]*([a-zA-Z]+:|#|\-\-\-)' | head -20)
        MAIN_CONTENT=$(grep -vE '^[[:space:]]*([a-zA-Z]+:|#|\-\-\-)' docs/"$file" | head -20)
        
        if [ "$ORIGINAL_CONTENT" != "$MAIN_CONTENT" ]; then
            # 内容不同，表示原文有更新，需要重新翻译
            NEEDS_TRANSLATION+=("$file")
            echo "内容更新需要翻译: $file"
        fi
    fi
done

# 输出结果
if [ ${#NEEDS_TRANSLATION[@]} -gt 0 ]; then
    for file in "${NEEDS_TRANSLATION[@]}"; do
        echo "$file"
    done > /tmp/new_or_modified_files.txt
    
    echo "NUMBER_OF_FILES=${#NEEDS_TRANSLATION[@]}" > /tmp/translation_status.txt
    echo "TRANSLATION_STATUS=needed" >> /tmp/translation_status.txt
    echo "FILES_TO_TRANSLATE=/tmp/new_or_modified_files.txt" >> /tmp/translation_status.txt
    
    echo "发现 ${#NEEDS_TRANSLATION[@]} 个需要翻译或更新的文件"
else
    echo "没有发现需要翻译的新或更新的文件"
    echo "TRANSLATION_STATUS=no-changes" > /tmp/translation_status.txt
    > /tmp/new_or_modified_files.txt  # 创建空文件
fi

echo "变更检测完成"

# 确保返回 main 分支
git checkout main 2>/dev/null || echo "Already on main or error occurred"
