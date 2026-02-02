#!/bin/bash
# 检测 original-en 分支相对于 main 分支新增的文档，并将其复制到 main 分支的待翻译目录

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

echo "开始检测并复制新增的文档..."

# 保存当前分支
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

# 获取 original-en 分支上的所有文档文件
if [ -d "docs" ]; then
    ORIGINAL_EN_FILES=$(find docs -name "*.md" -type f | sed 's|^docs/||' | sort)
    echo "在 original-en 分支找到 $(echo "$ORIGINAL_EN_FILES" | wc -w) 个文档文件"
else
    ORIGINAL_EN_FILES=""
    echo "original-en 分支上没有找到 docs 目录"
fi

# 切换回 main 分支
git checkout "$CURRENT_BRANCH" 2>/dev/null || { echo "无法切换回原分支 $CURRENT_BRANCH"; exit 1; }

# 检查 main 分支上是否有 docs 目录
if [ -d "docs" ]; then
    MAIN_FILES=$(find docs -name "*.md" -type f | sed 's|^docs/||' | sort)
    echo "在 main 分支找到 $(echo "$MAIN_FILES" | wc -w) 个文档文件"
else
    MAIN_FILES=""
    echo "main 分支上没有找到 docs 目录"
fi

# 创建待翻译文件目录
TEMP_TRANSLATION_DIR="temp_for_translation"
mkdir -p "$TEMP_TRANSLATION_DIR"

# 比较文件列表，找出在 original-en 分支有而 main 分支没有的文件
NEW_FILES=()

for file in $ORIGINAL_EN_FILES; do
    if ! echo "$MAIN_FILES" | grep -q "^${file}$"; then
        # 文件在 main 分支上不存在，需要添加到待翻译列表
        NEW_FILES+=("$file")
        echo "发现新文件: $file"
        
        # 创建目标目录结构
        TARGET_DIR="$TEMP_TRANSLATION_DIR/$(dirname "$file")"
        mkdir -p "$TARGET_DIR"
        
        # 从 original-en 分支复制文件
        git show original-en:docs/"$file" > "$TEMP_TRANSLATION_DIR/$file"
        echo "已复制新文件: $file -> $TEMP_TRANSLATION_DIR/$file"
    fi
done

# 输出结果
if [ ${#NEW_FILES[@]} -gt 0 ]; then
    for file in "${NEW_FILES[@]}"; do
        echo "$file"
    done > /tmp/new_docs_to_translate.txt
    
    echo "NUMBER_OF_NEW_FILES=${#NEW_FILES[@]}" > /tmp/translation_status.txt
    echo "TRANSLATION_STATUS=needed" >> /tmp/translation_status.txt
    echo "NEW_FILES_LIST=/tmp/new_docs_to_translate.txt" >> /tmp/translation_status.txt
    
    echo "发现 ${#NEW_FILES[@]} 个新文档需要翻译，已复制到 $TEMP_TRANSLATION_DIR 目录"
    
    # 显示复制的文件列表
    echo "复制的文件:"
    find "$TEMP_TRANSLATION_DIR" -type f | sort
else
    echo "没有发现新的文档需要翻译"
    echo "TRANSLATION_STATUS=no-new-files" > /tmp/translation_status.txt
    > /tmp/new_docs_to_translate.txt  # 创建空文件
    
    # 即使没有新文件，也要确保待翻译目录存在
    touch "$TEMP_TRANSLATION_DIR/.gitkeep"
fi

echo "检测和复制完成"

# 确保返回 main 分支
git checkout main 2>/dev/null || echo "Already on main or error occurred"