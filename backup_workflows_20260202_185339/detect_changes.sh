#!/bin/bash

# 修正的变更检测脚本
# 检测 original-en 分支相对于 main 分支的变更，用于触发翻译

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

echo "开始检测文档变更..."

# 临时存储当前分支
CURRENT_BRANCH=$(git branch --show-current)

# 确保获取最新的远程分支信息
git fetch origin

# 检查 original-en 本地分支是否存在，如果不存在则从远程创建
if ! git show-ref --verify --quiet refs/heads/original-en; then
    git checkout -b original-en origin/original-en
else
    # 如果存在，则切换到 original-en 并更新
    git checkout original-en
    git pull origin original-en
fi

# 检查 docs 目录是否存在
if [ -d "docs" ]; then
    ORIGINAL_EN_FILES=$(find docs -name "*.md" -type f | sed 's|docs/||' | sort)
else
    ORIGINAL_EN_FILES=""
    echo "original-en 分支上没有找到 docs 目录"
fi

# 切换回 main 分支
git checkout "$CURRENT_BRANCH" 2>/dev/null || { echo "无法切换回原分支 $CURRENT_BRANCH"; exit 1; }

# 获取 main 分支上的文件列表（中文文档）
if [ -d "docs" ]; then
    MAIN_FILES=$(find docs -name "*.md" -type f | sed 's|docs/||' | sort)
else
    MAIN_FILES=""
    echo "main 分支上没有找到 docs 目录"
fi

# 比较文件列表，找出需要翻译的文件
# 这里我们找出在 original-en 分支中有但在 main 分支上可能缺失或不同的文件
NEEDS_TRANSLATION=()

for file in $ORIGINAL_EN_FILES; do
    if [ ! -f "docs/$file" ]; then
        # 文件在 main 分支上不存在，需要翻译
        NEEDS_TRANSLATION+=("$file")
        echo "新文件需要翻译: $file"
    else
        # 为了比较内容，我们需要从 original-en 分支获取英文内容
        TEMP_EN_CONTENT=$(git show original-en:docs/"$file" 2>/dev/null | grep -vE '^[[:space:]]*([a-zA-Z]+:|#|\-\-\-|title:|lang:|permalink:|nav_order:|nav_exclude:|layout:|parent:|has_children:|has_toc_file:|search:)' | head -50)
        MAIN_CONTENT=$(grep -vE '^[[:space:]]*([a-zA-Z]+:|#|\-\-\-|title:|lang:|permalink:|nav_order:|nav_exclude:|layout:|parent:|has_children:|has_toc_file:|search:)' docs/"$file" 2>/dev/null | head -50)
        
        if [ "$TEMP_EN_CONTENT" != "$MAIN_CONTENT" ]; then
            # 内容不同，需要重新翻译
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
    
    echo "发现 ${#NEEDS_TRANSLATION[@]} 个需要翻译的文件"
else
    echo "没有发现需要翻译的新或更新的文件"
    echo "TRANSLATION_STATUS=no-changes" > /tmp/translation_status.txt
    > /tmp/new_or_modified_files.txt  # 创建空文件
fi

echo "变更检测完成"

# 确保返回 main 分支
git checkout main 2>/dev/null || echo "Already on main or error occurred"