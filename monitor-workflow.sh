#!/bin/bash

# 从环境变量或 ~/.zshrc 获取 GitHub 令牌
TOKEN=$(grep GITHUB_TOKEN ~/.zshrc | cut -d '=' -f 2)

if [ -z "$TOKEN" ]; then
    echo "错误: 未找到 GitHub 令牌"
    exit 1
fi

echo "开始监控 GitHub Actions 工作流..."

while true; do
    echo "==================================="
    echo "检查时间: $(date)"
    
    # 获取最近的运行记录
    RESPONSE=$(curl -s -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/wszhxz/openclaw-chinese-docs/actions/runs?per_page=5")
    
    if [ $? -ne 0 ]; then
        echo "错误: 无法获取工作流运行数据"
    else
        RUN_COUNT=$(echo "$RESPONSE" | grep -o '"workflow_runs"' | wc -l)
        if [ $RUN_COUNT -gt 0 ]; then
            RUNS_EXIST=$(echo "$RESPONSE" | jq -r '.workflow_runs | length')
            if [ "$RUNS_EXIST" -gt 0 ]; then
                echo "找到 $RUNS_EXIST 个最近的运行:"
                echo "$RESPONSE" | jq -r '.workflow_runs[] | "- ID: \(.id), Name: \(.name), Status: \(.status), Conclusion: \(.conclusion), Created: \(.created_at)"'
                
                # 检查是否有失败的运行
                FAILED_RUNS=$(echo "$RESPONSE" | jq -r '.workflow_runs[] | select(.conclusion != "success" and .status == "completed") | .id')
                
                if [ ! -z "$FAILED_RUNS" ] && [ "$FAILED_RUNS" != "" ]; then
                    echo "⚠️ 发现失败的运行!"
                    for failed_run_id in $FAILED_RUNS; do
                        echo "获取失败运行 $failed_run_id 的详细信息..."
                        
                        JOB_RESPONSE=$(curl -s -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" \
                            "https://api.github.com/repos/wszhxz/openclaw-chinese-docs/actions/runs/$failed_run_id/jobs")
                        
                        if [ $? -eq 0 ]; then
                            echo "$JOB_RESPONSE" | jq -r '.jobs[] | select(.conclusion != "success") | "  - Job: \(.name), Conclusion: \(.conclusion)"'
                        fi
                    done
                else
                    echo "✅ 所有运行都成功或仍在进行中"
                fi
            else
                echo "暂无运行记录。工作流预计每小时运行一次。"
            fi
        else
            echo "无法解析响应数据"
        fi
    fi
    
    echo "下次检查将在 15 分钟后进行..."
    sleep 900  # 等待 15 分钟
done