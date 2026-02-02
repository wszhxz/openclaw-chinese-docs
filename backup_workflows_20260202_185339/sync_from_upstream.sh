#!/bin/bash

# 双分支同步脚本 - 实现思维导图中的同步策略
# 同步英文文档到 original-en 分支，同时保护 main 分支的本地化配置

set -e

echo "开始执行双分支同步策略..."

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

# 保存当前的本地化配置
echo "备份本地化配置文件..."
mkdir -p backup_configs
cp -f docs/docs.json backup_configs/ 2>/dev/null || echo "No docs.json to backup"
cp -f docs/_config.yml backup_configs/ 2>/dev/null || echo "No _config.yml to backup"
cp -f docs/_layouts/default.html backup_configs/ 2>/dev/null || echo "No default.html to backup"

# 同步新内容（除了配置文件和已有的中文翻译）
echo "同步英文文档内容..."
mkdir -p docs

# 先备份现有的中文翻译文件
mkdir -p backup_translations
find docs/ -name "*.md" -exec grep -l "中文\|翻译\|Chinese\|chinese" {} \; | while read file; do
  rel_path="${file#docs/}"
  if [ -n "$rel_path" ]; then
    mkdir -p "backup_translations/$(dirname "$rel_path")"
    cp "$file" "backup_translations/$rel_path"
    echo "备份中文翻译文件: $rel_path"
  fi
done

# 同步新内容（除了配置文件和GitHub工作流）
rsync -av --delete \
  --exclude 'docs.json' \
  --exclude '_config.yml' \
  --exclude '_layouts/' \
  --exclude '_includes/' \
  --exclude 'assets/' \
  --exclude '.github/' \
  temp-openclaw-upstream/docs/ docs/

# 恢复本地化配置
echo "恢复本地化配置文件..."
cp -f backup_configs/docs.json docs/ 2>/dev/null || echo "No docs.json to restore"
cp -f backup_configs/_config.yml docs/ 2>/dev/null || echo "No _config.yml to restore"

# 恢复必要的布局文件
mkdir -p docs/_layouts
cp -f backup_configs/default.html docs/_layouts/ 2>/dev/null || echo "No default.html to restore"

# 恢复现有的中文翻译文件
if [ -d "backup_translations" ]; then
  echo "恢复现有中文翻译文件..."
  rsync -av backup_translations/ docs/
  rm -rf backup_translations
fi

# 清理备份
rm -rf backup_configs

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

echo "双分支同步完成！"
echo "original-en 分支已更新，包含最新的英文文档内容"
echo "本地化配置文件已保护，未被覆盖"
# 切换回 main 分支
git checkout main
