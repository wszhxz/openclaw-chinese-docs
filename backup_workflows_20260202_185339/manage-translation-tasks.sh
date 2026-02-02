#!/bin/bash

# 翻译任务管理脚本
# 管理检测到的变更和审查结果，协调翻译任务

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

echo "管理翻译任务..."

# 创建翻译任务目录
mkdir -p temp_translation_tasks

# 从检测工作流获取需要翻译的文件
if [ -f "/tmp/new_or_modified_files.txt" ] && [ -s "/tmp/new_or_modified_files.txt" ]; then
    cp /tmp/new_or_modified_files.txt temp_translation_tasks/from_detection.txt
    echo "从检测工作流获取 $(cat temp_translation_tasks/from_detection.txt | wc -l) 个文件"
else
    touch temp_translation_tasks/from_detection.txt
    echo "检测工作流未提供文件列表"
fi

# 从翻译审查工作流获取需要更新的文件
if [ -f "/tmp/translations_needing_update.txt" ] && [ -s "/tmp/translations_needing_update.txt" ]; then
    cp /tmp/translations_needing_update.txt temp_translation_tasks/from_review.txt
    echo "从翻译审查获取 $(cat temp_translation_tasks/from_review.txt | wc -l) 个文件"
else
    touch temp_translation_tasks/from_review.txt
    echo "翻译审查未提供文件列表"
fi

# 合并两个列表，去重
cat temp_translation_tasks/from_detection.txt temp_translation_tasks/from_review.txt | sort | uniq > temp_translation_tasks/all_pending_translations.txt

# 统计总数
TOTAL_PENDING=$(cat temp_translation_tasks/all_pending_translations.txt | wc -l)
echo "总计需要翻译的文件数: $TOTAL_PENDING"

# 创建环境变量文件供GitHub Actions使用
echo "TOTAL_TRANSLATION_TASKS=$TOTAL_PENDING" > temp_translation_tasks/task_summary.env
if [ "$TOTAL_PENDING" -gt 0 ]; then
    echo "HAS_TRANSLATION_TASKS=true" >> temp_translation_tasks/task_summary.env
    echo "FIRST_TRANSLATION_TASK=$(head -n 1 temp_translation_tasks/all_pending_translations.txt)" >> temp_translation_tasks/task_summary.env
else
    echo "HAS_TRANSLATION_TASKS=false" >> temp_translation_tasks/task_summary.env
    echo "FIRST_TRANSLATION_TASK=" >> temp_translation_tasks/task_summary.env
fi

echo "翻译任务管理完成"
