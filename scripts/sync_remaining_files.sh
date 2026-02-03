#!/bin/bash
# 同步original-en分支中docs目录下未翻译的文件到main分支的docs目录
# 只对比文件名，保留已翻译的中文文档和未翻译的原始文件

set -e

echo "开始同步original-en分支中docs目录下的剩余文件..."

# 首先备份本地docs文件夹的翻译成果
echo "正在备份本地docs文件夹的翻译成果..."
BACKUP_DIR="$HOME/claw/openclaw_docs_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
if [ -d "docs" ]; then
    cp -r docs "$BACKUP_DIR/"
    echo "翻译成果已备份到: $BACKUP_DIR"
else
    echo "警告: docs目录不存在，跳过备份"
fi

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

# 保存当前分支
CURRENT_BRANCH=$(git branch --show-current)

# 确保获取最新的远程分支信息
git fetch origin

# 切换到original-en分支并更新
echo "切换到original-en分支..."
git checkout -B original-en origin/original-en

# 获取original-en分支中docs目录的所有文件（包括子目录）
ORIGINAL_EN_FILES=$(find docs -type f 2>/dev/null | sed 's|^docs/||' | sort)

if [ -z "$ORIGINAL_EN_FILES" ]; then
    echo "original-en分支中没有找到docs目录或其中没有文件"
    exit 0
fi

echo "在original-en分支的docs目录中找到 $(echo "$ORIGINAL_EN_FILES" | wc -l) 个文件"

# 切换回main分支
echo "切换回main分支..."
git checkout "$CURRENT_BRANCH"

# 获取main分支中docs目录的文件
if [ -d "docs" ]; then
    MAIN_DOCS_FILES=$(find docs -type f 2>/dev/null | sed 's|^docs/||' | sort)
    echo "在main分支的docs目录中找到 $(echo "$MAIN_DOCS_FILES" | wc -l) 个文件"
else
    MAIN_DOCS_FILES=""
    echo "main分支中没有找到docs目录"
    mkdir -p docs
fi

# 找出在original-en中有但在main中缺失的文件
MISSING_FILES=()
for file in $ORIGINAL_EN_FILES; do
    if ! echo "$MAIN_DOCS_FILES" | grep -q "^${file}$"; then
        MISSING_FILES+=("$file")
        echo "发现缺失文件: $file"
    fi
done

# 如果有缺失的文件，则从original-en分支复制
if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "开始复制 ${#MISSING_FILES[@]} 个缺失的文件..."
    
    # 创建临时工作区来获取original-en分支的文件
    git worktree add temp_worktree_sync origin/original-en
    
    for file in "${MISSING_FILES[@]}"; do
        # 创建目标目录结构
        TARGET_DIR="docs/$(dirname "$file")"
        mkdir -p "$TARGET_DIR"
        
        # 从original-en分支复制文件
        cp "temp_worktree_sync/docs/$file" "docs/$file"
        echo "已复制: $file"
    done
    
    # 清理临时工作区
    git worktree remove temp_worktree_sync
    git worktree prune
    
    echo "缺失文件复制完成"
else
    echo "没有发现缺失的文件"
fi

# 添加所有更改到git
git add docs/

# 检查是否有更改需要提交
if ! git diff --staged --quiet && git diff --quiet; then
    echo "没有更改需要提交"
else
    # 提交更改
    git config user.name "GitHub Action"
    git config user.email "action@github.com"
    git commit -m "Sync: Add remaining files from original-en branch docs directory [skip ci]"
    echo "已提交同步的文件"
fi

# 确保回到main分支
git checkout main

echo "同步完成！"
echo "main分支的docs目录现在包含所有必要的文件"