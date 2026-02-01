const fs = require('fs');
const { exec } = require('child_process');
const path = require('path');

// 监控工作流状态
function monitorWorkflow() {
    console.log(`[${new Date().toISOString()}] 开始监控工作流状态...`);
    
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
            
            if (response && response.workflow_runs && response.workflow_runs.length > 0) {
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
                    
                    // 检查工作流状态并采取相应措施
                    if (latestRun.status !== 'completed') {
                        console.log(`⏳ 工作流仍在运行中...`);
                        
                        // 5分钟后再次检查
                        setTimeout(monitorWorkflow, 5 * 60 * 1000);
                    } else if (latestRun.conclusion === 'failure') {
                        console.log(`❌ 工作流运行失败！需要立即处理。`);
                        
                        // 创建告警文件
                        const alertData = {
                            timestamp: new Date().toISOString(),
                            runId: latestRun.id,
                            status: 'failed',
                            message: 'Sync workflow failed',
                            details: latestRun
                        };
                        
                        fs.writeFileSync('./workflow-alert.json', JSON.stringify(alertData, null, 2));
                        console.log('🚨 已记录失败状态到 workflow-alert.json');
                        
                        // 发送告警（这里可以扩展为发送消息给用户）
                        console.log('🚨 工作流失败告警已触发，请检查！');
                        
                    } else if (latestRun.conclusion === 'success') {
                        console.log(`✅ 工作流运行成功！`);
                        
                        // 记录成功状态
                        const successRecord = {
                            timestamp: new Date().toISOString(),
                            runId: latestRun.id,
                            status: 'success',
                            message: 'Sync workflow completed successfully'
                        };
                        
                        fs.writeFileSync('./workflow-success.json', JSON.stringify(successRecord, null, 2));
                        console.log('✅ 成功状态已记录到 workflow-success.json');
                        
                    } else {
                        console.log(`⚠️ 工作流状态: ${latestRun.conclusion}`);
                    }
                } else {
                    console.log("未找到同步工作流运行记录，可能还未开始运行...");
                    
                    // 10分钟后再次检查
                    setTimeout(monitorWorkflow, 10 * 60 * 1000);
                }
            } else {
                console.log("未找到任何工作流运行记录，可能还未开始运行...");
                
                // 10分钟后再次检查
                setTimeout(monitorWorkflow, 10 * 60 * 1000);
            }
        } catch (e) {
            console.error("解析响应数据时出错:", e.message);
            
            // 5分钟后重试
            setTimeout(monitorWorkflow, 5 * 60 * 1000);
        }
    });
}

// 启动监控
monitorWorkflow();