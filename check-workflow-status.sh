#!/bin/bash

# 从环境变量或 ~/.zshrc 获取 GitHub 令牌
TOKEN=$(grep GITHUB_TOKEN ~/.zshrc | cut -d '=' -f 2)

if [ -z "$TOKEN" ]; then
    echo "错误: 未找到 GitHub 令牌"
    exit 1
fi

echo "检查 GitHub Actions 工作流状态..."

# 获取最近的运行记录
RESPONSE=$(curl -s -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/wszhxz/openclaw-chinese-docs/actions/runs?per_page=10")

if [ $? -eq 0 ]; then
    RUNS_EXIST=$(echo "$RESPONSE" | jq -r '.workflow_runs | length')
    if [ "$RUNS_EXIST" -gt 0 ]; then
        echo "找到 $RUNS_EXIST 个最近的运行:"
        echo "$RESPONSE" | jq -r '.workflow_runs[] | select(.status != "completed") | "- ID: \(.id), Name: \(.name), Status: \(.status), Started: \(.created_at)"'
        
        # 检查最近的已完成运行
        COMPLETED_RUNS=$(echo "$RESPONSE" | jq -r '.workflow_runs[] | select(.status == "completed") | {id:.id, name:.name, conclusion:.conclusion, created:.created_at} | "- ID: \(.id), Name: \(.name), Conclusion: \(.conclusion), Created: \(.created_at)"')
        
        if [ ! -z "$COMPLETED_RUNS" ]; then
            echo "最近的已完成运行:"
            echo "$COMPLETED_RUNS"
        fi
        
        # 检查是否有失败的运行
        FAILED_RUNS=$(echo "$RESPONSE" | jq -r '.workflow_runs[] | select(.conclusion == "failure") | .id')
        
        if [ ! -z "$FAILED_RUNS" ] && [ "$FAILED_RUNS" != "" ]; then
            echo "⚠️ 发现失败的运行! ID: $FAILED_RUNS"
        else
            echo "✅ 最近的运行都没有失败"
        fi
    else
        echo "暂无运行记录。工作流预计每小时运行一次。"
    fi
else
    echo "错误: 无法获取工作流运行数据"
fi