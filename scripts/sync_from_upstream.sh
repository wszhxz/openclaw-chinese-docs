#!/bin/bash
# 同步英文文档到 original-en 分支

set -e

echo "开始执行分支同步..."

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

# 检查 original-en 分支是否存在，如果不存在则创建
if ! git ls-remote --heads origin original-en | grep -q "refs/heads/original-en"; then
    echo "创建 original-en 分支..."
    git checkout -b original-en
    git push origin original-en
    git checkout main
else
    echo "original-en 分支已存在"
fi

# 克隆最新的英文文档
echo "克隆最新的 OpenClaw 英文文档..."
if [ -d "temp-openclaw-upstream" ]; then
    rm -rf temp-openclaw-upstream
fi

git clone --depth 1 https://github.com/openclaw/openclaw.git temp-openclaw-upstream

# 确保在 original-en 分支上操作
git fetch origin
git checkout -B original-en origin/original-en

# 同步新内容
echo "正在同步项目内容..."
ram -rf./*
mkdir docs
rsync -av temp-openclaw-upstream/docs  ./docs


# 检查是否有更改需要提交
if ! git diff --staged --quiet && git diff --quiet; then
    echo "没有更改需要提交"
else
    # 添加更改
    git add docs/
    
    # 提交更改到 original-en 分支
    git config user.name "GitHub Action"
    git config user.email "action@github.com"
    git commit -m "Sync: Update English docs from upstream [skip ci]" || echo "No changes to commit"
    
    # 推送更改到远程 original-en 分支
    git push origin original-en
fi


echo "original-en 分支已更新，包含最新的英文文档内容"
echo 

git checkout main
