#!/bin/bash
# 创建一个纯净的original-en分支，只包含从openclaw项目同步的docs目录

set -e

echo "开始创建纯净的 original-en 分支..."

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

# 创建临时目录用于下载上游项目
TEMP_DIR=$(mktemp -d)
echo "使用临时目录: $TEMP_DIR"

# 克隆上游 openclaw 项目到临时目录
echo "克隆上游 openclaw 项目..."
git clone --depth 1 https://github.com/openclaw/openclaw.git "$TEMP_DIR/openclaw-repo"

# 检查是否包含docs目录
if [ ! -d "$TEMP_DIR/openclaw-repo/docs" ]; then
    echo "错误: 上游项目不包含 docs 目录"
    exit 1
fi

echo "上游项目包含 docs 目录，继续处理..."

# 切换到 main 分支以确保基础
git checkout main

# 检查 original-en 分支是否存在
if git show-ref --verify --quiet refs/heads/original-en; then
    echo "删除现有的 original-en 分支..."
    git branch -D original-en
    # 删除远程分支
    git push origin --delete original-en 2>/dev/null || true
fi

# 创建一个没有任何历史的孤儿分支
echo "创建纯净的 original-en 孤儿分支..."
git checkout --orphan original-en

# 清空当前暂存区和工作区的所有文件
git rm -rf .

# 复制上游项目的 docs 目录到当前目录
cp -r "$TEMP_DIR/openclaw-repo/docs" ./

# 初始化并配置 Git 用户信息
git config user.name "GitHub Action"
git config user.email "action@github.com"

# 添加 docs 目录
git add docs/

# 提交更改
git commit -m "Initial commit: Add English docs from openclaw project"

# 强制推送到远程 original-en 分支
git push -f origin original-en

# 清理临时目录
rm -rf "$TEMP_DIR"

echo "original-en 分支已创建并推送，仅包含上游项目的 docs 目录"