const { exec } = require('child_process');
require('dotenv').config();

// 从环境变量获取GitHub令牌
const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;

if (!token) {
  console.error('错误: 未找到GitHub令牌。请设置 GITHUB_TOKEN 或 GH_TOKEN 环境变量。');
  process.exit(1);
}

function checkWorkflowRuns() {
  console.log(`正在检查工作流运行状态... ${new Date().toISOString()}`);
  
  const cmd = `curl -s -H "Authorization: token ${token}" -H "Accept: application/vnd.github.v3+json" "https://api.github.com/repos/wszhxz/openclaw-chinese-docs/actions/runs?per_page=5"`;

  exec(cmd, (error, stdout, stderr) => {
    if (error) {
      console.error(`执行错误: ${error.message}`);
      return;
    }

    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }

    try {
      const data = JSON.parse(stdout);
      
      if (data.workflow_runs && data.workflow_runs.length > 0) {
        console.log(`找到 ${data.workflow_runs.length} 个最近的运行:`);
        
        for (const run of data.workflow_runs) {
          console.log(`- 运行ID: ${run.id}, 名称: ${run.name}, 状态: ${run.status}, 结论: ${run.conclusion}, 创建时间: ${run.created_at}`);
          
          // 如果运行已完成但失败，显示详细信息
          if (run.status === 'completed' && run.conclusion !== 'success') {
            console.log(`  ❌ 失败的运行详情:`);
            console.log(`    - 运行ID: ${run.id}`);
            console.log(`    - 工作流: ${run.display_title}`);
            console.log(`    - 结论: ${run.conclusion}`);
            console.log(`    - 开始时间: ${run.started_at}`);
            console.log(`    - URL: ${run.html_url}`);
            
            // 获取失败作业的详细信息
            getJobDetails(run.id);
          }
        }
      } else {
        console.log("暂无运行记录。工作流预计每小时运行一次。");
      }
    } catch (parseError) {
      console.error(`解析响应错误: ${parseError.message}`);
      console.error(`原始响应: ${stdout}`);
    }
  });
}

function getJobDetails(runId) {
  const cmd = `curl -s -H "Authorization: token ${token}" -H "Accept: application/vnd.github.v3+json" "https://api.github.com/repos/wszhxz/openclaw-chinese-docs/actions/runs/${runId}/jobs"`;

  exec(cmd, (error, stdout, stderr) => {
    if (error) {
      console.error(`获取作业详情错误: ${error.message}`);
      return;
    }

    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return;
    }

    try {
      const data = JSON.parse(stdout);
      
      if (data.jobs && data.jobs.length > 0) {
        for (const job of data.jobs) {
          if (job.conclusion !== 'success') {
            console.log(`    - 作业名称: ${job.name}, 结论: ${job.conclusion}`);
            
            // 获取作业步骤详情
            if (job.steps) {
              for (const step of job.steps) {
                if (step.conclusion !== 'success') {
                  console.log(`      - 步骤: ${step.name}, 结论: ${step.conclusion}`);
                }
              }
            }
          }
        }
      }
    } catch (parseError) {
      console.error(`解析作业详情错误: ${parseError.message}`);
    }
  });
}

// 立即检查一次
checkWorkflowRuns();

// 每15分钟检查一次
setInterval(checkWorkflowRuns, 15 * 60 * 1000);

module.exports = { checkWorkflowRuns };