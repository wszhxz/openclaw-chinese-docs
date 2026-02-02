#!/bin/bash

# 备份现有翻译成果脚本
# 在执行新的同步策略前，备份现有的中文翻译内容

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

echo "开始备份现有翻译成果..."

# 创建备份目录
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR/existing_translations"

echo "搜索现有中文翻译内容..."

# 查找包含中文内容的文件并备份
find docs/ -name "*.md" -exec grep -l "中文\|翻译\|Chinese\|chinese" {} \; > /tmp/chinese_files.txt

if [ -s /tmp/chinese_files.txt ]; then
    echo "发现以下包含中文内容的文件："
    cat /tmp/chinese_files.txt
    
    # 备份这些文件
    while IFS= read -r file; do
        if [ -n "$file" ] && [ -f "$file" ]; then
            dest_file="$BACKUP_DIR/existing_translations/$file"
            mkdir -p "$(dirname "$dest_file")"
            cp "$file" "$dest_file"
            echo "已备份: $file"
        fi
    done < /tmp/chinese_files.txt
    
    echo "现有中文翻译已备份到: $BACKUP_DIR/existing_translations/"
else
    echo "未发现明显的中文翻译内容"
fi

# 也备份重要的配置文件
echo "备份现有配置文件..."
mkdir -p "$BACKUP_DIR/config"
cp -f docs/_config.yml "$BACKUP_DIR/config/" 2>/dev/null || echo "无 _config.yml 需要备份"
cp -f docs/docs.json "$BACKUP_DIR/config/" 2>/dev/null || echo "无 docs.json 需要备份"
cp -f docs/_layouts/default.html "$BACKUP_DIR/config/" 2>/dev/null || echo "无 default.html 需要备份"

echo "配置文件已备份到: $BACKUP_DIR/config/"

# 创建备份清单
echo "创建备份清单..."
echo "Backup created on: $(date)" > "$BACKUP_DIR/backup_manifest.txt"
echo "Repository: $REPO_DIR" >> "$BACKUP_DIR/backup_manifest.txt"
echo "Chinese files backed up:" >> "$BACKUP_DIR/backup_manifest.txt"
cat /tmp/chinese_files.txt >> "$BACKUP_DIR/backup_manifest.txt" 2>/dev/null || echo "No Chinese files" >> "$BACKUP_DIR/backup_manifest.txt"

echo "备份清单已创建: $BACKUP_DIR/backup_manifest.txt"

echo "备份完成！"
echo "备份位置: $BACKUP_DIR"