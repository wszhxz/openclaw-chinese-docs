const fs = require('fs');
const { exec } = require('child_process');

function checkWorkflowStatus() {
    console.log(`[${new Date().toISOString()}] 检查工作流状态...`);
    
    // 检查最近的同步工作流运行状态
    const cmd = `curl -s -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github.v3+json" "https://api.github.com/repos/wszhxz/openclaw-chinese-docs/actions/runs?event=push&per_page=10"`;
    
    exec(cmd, (error, stdout, stderr) => {
        if (error) {
            console.log("无法访问 GitHub API，请检查 GITHUB_TOKEN 设置");
            console.log("错误:", stderr);
            return;
        }
        
        try {
            const response = JSON.parse(stdout);
            
            if (response.workflow_runs && response.workflow_runs.length > 0) {
                const syncRuns = response.workflow_runs.filter(run => 
                    run.name === "OpenClaw Docs - Dual Branch Sync"
                );
                
                if (syncRuns.length > 0) {
                    const latestRun = syncRuns[0];
                    console.log(`\n=== 最新同步工作流状态 ===`);
                    console.log(`ID: ${latestRun.id}`);
                    console.log(`名称: ${latestRun.name}`);
                    console.log(`状态: ${latestRun.status}`);
                    console.log(`结论: ${latestRun.conclusion || 'running'}`);
                    console.log(`创建时间: ${latestRun.created_at}`);
                    console.log(`更新时间: ${latestRun.updated_at}`);
                    
                    if (latestRun.status !== 'completed') {
                        console.log(`工作流仍在运行中...`);
                    } else if (latestRun.conclusion === 'failure') {
                        console.log(`❌ 工作流运行失败！需要立即处理。`);
                        
                        // 记录失败状态
                        const failRecord = {
                            timestamp: new Date().toISOString(),
                            runId: latestRun.id,
                            status: 'failed',
                            message: 'Sync workflow failed'
                        };
                        
                        console.log('失败记录:', failRecord);
                    } else if (latestRun.conclusion === 'success') {
                        console.log(`✅ 工作流运行成功！`);
                    }
                } else {
                    console.log("未找到同步工作流运行记录");
                }
            } else {
                console.log("未找到任何工作流运行记录");
            }
        } catch (e) {
            console.error("解析响应数据时出错:", e.message);
        }
    });
}

// 立即检查一次
checkWorkflowStatus();

// 每5分钟检查一次，持续监控
setInterval(checkWorkflowStatus, 5 * 60 * 1000);