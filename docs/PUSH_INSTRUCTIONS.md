# 推送说明

要将此本地仓库推送到 GitHub，请按以下步骤操作：

## 1. 在 GitHub 上创建仓库
访问 https://github.com/new 创建一个新的公共仓库：
- 仓库名称：`openclaw-chinese-docs`
- 设为公共（Public）
- 不要初始化 README、.gitignore 或 license（我们已有这些）

## 2. 获取访问令牌（如果需要）
如果您没有配置 SSH 访问，请创建一个 GitHub 个人访问令牌：
- 访问 https://github.com/settings/tokens
- 点击 "Generate new token"
- 选择适当的权限（至少需要 repo 权限）
- 复制生成的令牌

## 3. 推送仓库
运行以下命令（如果您使用令牌认证，系统会提示输入用户名和密码，密码处粘贴令牌）：

```bash
git push -u origin main
```

## 4. 配置 GitHub Pages
推送完成后：
- 进入仓库设置
- 选择 Settings 选项卡
- 向下滚动到 "Pages" 部分
- 从下拉菜单中选择 "Deploy from a branch"
- 选择 "main" 分支和 "/" 文件夹
- 点击 "Save"

这样就会启动您设计的自动化翻译系统，它将在 GitHub Actions 中每小时运行一次。