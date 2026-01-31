#!/bin/bash

# 调试脚本：检查工作流中的问题并提供修复建议

echo "=== OpenClaw Chinese Docs 自动翻译工作流调试器 ==="
echo

# 检查本地环境
echo "1. 检查本地环境..."
echo "Node 版本: $(node --version)"
echo "NPM 版本: $(npm --version)"
echo "Git 版本: $(git --version)"
echo

# 检查依赖
echo "2. 检查依赖项..."
if [ -f "package.json" ]; then
    echo "✓ package.json 存在"
    echo "依赖项:"
    cat package.json | grep -A 10 dependencies
else
    echo "✗ package.json 不存在"
fi
echo

# 检查脚本文件
echo "3. 检查脚本文件..."
if [ -f "scripts/process-file.js" ]; then
    echo "✓ scripts/process-file.js 存在"
else
    echo "✗ scripts/process-file.js 不存在"
fi

if [ -f "scripts/translate-docs.js" ]; then
    echo "✓ scripts/translate-docs.js 存在"
else
    echo "✗ scripts/translate-docs.js 不存在"
fi

if [ -f "terminology.json" ]; then
    echo "✓ terminology.json 存在"
else
    echo "✗ terminology.json 不存在"
fi
echo

# 检查工作流文件
echo "4. 检查 GitHub Actions 工作流..."
if [ -f ".github/workflows/auto-translate.yml" ]; then
    echo "✓ .github/workflows/auto-translate.yml 存在"
    echo "工作流触发器:"
    grep -A 5 "on:" .github/workflows/auto-translate.yml
else
    echo "✗ .github/workflows/auto-translate.yml 不存在"
fi
echo

# 测试脚本功能
echo "5. 测试脚本功能..."
TEST_FILE="debug_test.md"
echo '# Test Document

This is a test with OpenClaw gateway and agent terms.' > "$TEST_FILE"

echo "创建测试文件: $TEST_FILE"
echo "内容:"
cat "$TEST_FILE"
echo

echo "运行翻译脚本..."
node scripts/process-file.js "$TEST_FILE" "debug_output.md"
if [ $? -eq 0 ]; then
    echo "✓ 翻译脚本执行成功"
    echo "翻译结果:"
    cat debug_output.md
else
    echo "✗ 翻译脚本执行失败"
fi
echo

# 清理测试文件
rm -f "$TEST_FILE" debug_output.md

# 检查 Git 配置
echo "6. 检查 Git 配置..."
echo "远程仓库:"
git remote -v
echo

# 提供修复建议
echo "7. 修复建议:"
echo "- 如果工作流继续失败，请检查 GitHub Actions 日志中的具体错误信息"
echo "- 确保仓库的 GITHUB_TOKEN 具有足够的权限"
echo "- 验证术语表格式是否正确"
echo "- 检查是否有网络连接问题导致无法克隆 OpenClaw 仓库"
echo "- 考虑添加更多错误处理和调试输出到工作流"
echo

echo "=== 调试完成 ==="