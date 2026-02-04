---
summary: "CLI reference for `openclaw skills` (list/info/check) and skill eligibility"
read_when:
  - You want to see which skills are available and ready to run
  - You want to debug missing binaries/env/config for skills
title: "skills"
---
# `openclaw skills`

检查技能（捆绑 + 工作区 + 管理覆盖）并查看哪些符合条件以及哪些缺少要求。

相关：

- 技能系统：[Skills](/tools/skills)
- 技能配置：[Skills config](/tools/skills-config)
- ClawHub 安装：[ClawHub](/tools/clawhub)

## 命令

```bash
openclaw skills list
openclaw skills list --eligible
openclaw skills info <name>
openclaw skills check
```