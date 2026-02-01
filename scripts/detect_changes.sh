#!/bin/bash

# 修正的变更检测脚本
# 与原始 OpenClaw 项目对比，而不是在本地分支之间对比

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

echo "开始检测文档变更..."

# 克隆最新的 OpenClaw 原始项目
if [ -d "temp-original-openclaw" ]; then
    rm -rf temp-original-openclaw
fi

git clone --depth 1 https://github.com/openclaw/openclaw.git temp-original-openclaw

# 获取当前 original-en 分支上的文件列表
git checkout original-en 2>/dev/null
CURRENT_FILES=$(find docs -name "*.md" -type f | sed 's|docs/||' | sort)

# 获取原始 OpenClaw 项目的文件列表
ORIGIN_FILES=$(find temp-original-openclaw/docs -name "*.md" -type f | sed 's|temp-original-openclaw/docs/||' | sort)

# 比较文件列表，找出新增或更新的文件
# 这里我们找出在原始项目中有但在 original-en 分支上可能缺失或不同的文件
NEEDS_TRANSLATION=()

for file in $ORIGIN_FILES; do
    if [ ! -f "docs/$file" ]; then
        # 文件在 original-en 分支上不存在，需要同步
        NEEDS_TRANSLATION+=("$file")
        echo "新文件需要同步到 original-en: $file"
    else
        # 文件在两个地方都存在，比较内容
        CURRENT_CONTENT=$(grep -vE '^[[:space:]]*([a-zA-Z]+:|#|\-\-\-)' docs/"$file" | head -20)
        ORIGIN_CONTENT=$(grep -vE '^[[:space:]]*([a-zA-Z]+:|#|\-\-\-)' temp-original-openclaw/docs/"$file" | head -20)
        
        if [ "$CURRENT_CONTENT" != "$ORIGIN_CONTENT" ]; then
            # 内容不同，需要更新 original-en 分支
            NEEDS_TRANSLATION+=("$file")
            echo "内容更新需要同步到 original-en: $file"
        fi
    fi
done

# 切换回 main 分支
git checkout main 2>/dev/null

# 输出结果
if [ ${#NEEDS_TRANSLATION[@]} -gt 0 ]; then
    for file in "${NEEDS_TRANSLATION[@]}"; do
        echo "$file"
    done > /tmp/new_or_modified_files.txt
    
    echo "NUMBER_OF_FILES=${#NEEDS_TRANSLATION[@]}" > /tmp/translation_status.txt
    echo "TRANSLATION_STATUS=needed" >> /tmp/translation_status.txt
    echo "FILES_TO_TRANSLATE=/tmp/new_or_modified_files.txt" >> /tmp/translation_status.txt
    
    echo "发现 ${#NEEDS_TRANSLATION[@]} 个需要同步的文件"
else
    echo "没有发现需要同步的新或更新的文件"
    echo "TRANSLATION_STATUS=no-changes" > /tmp/translation_status.txt
    > /tmp/new_or_modified_files.txt  # 创建空文件
fi

# 清理临时目录
rm -rf temp-original-openclaw

echo "变更检测完成"

# 确保返回 main 分支
git checkout main 2>/dev/null || echo "Already on main or error occurred"
