# 翻译完成后的操作清单

## 重要提醒
- 远程仓库可能存在名为`docs`的文件，与本地`docs`目录冲突
- 推送时可能会出错，需要特别处理

## 操作步骤

### 1. 备份翻译成果
在进行任何推送操作前，先备份本地翻译成果：
```bash
# 创建备份目录
mkdir ~/backup_openclaw_docs_$(date +%Y%m%d_%H%M%S)
# 复制docs目录
cp -r ~/github/openclaw-chinese-docs/docs ~/backup_openclaw_docs_$(date +%Y%m%d_%H%M%S)/
```

### 2. 解决冲突
- 远程仓库可能存在`docs`文件，需要先删除
- 本地`docs`目录是GitHub Pages必需的，以本地为准

### 3. 同步剩余文件
运行脚本同步original-en分支中docs目录下未翻译的文件（如配置文件、图片等）：
```bash
bash ~/github/openclaw-chinese-docs/scripts/sync_remaining_files.sh
```

该脚本会：
- 对比original-en和main分支的docs目录文件名
- 只复制main分支中缺失的文件（不对比内容，因为MD文件已被翻译）
- 保持完整的文档结构

### 4. 推送操作
- 确保远程仓库结构正确后再推送
- 检查GitHub Pages配置是否正常

### 5. 验证
- 确认GitHub Pages能正常访问
- 检查文档完整性
- 验证路径映射是否正确