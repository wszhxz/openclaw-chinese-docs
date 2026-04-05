---
summary: "CLI reference for `openclaw backup` (create local backup archives)"
read_when:
  - You want a first-class backup archive for local OpenClaw state
  - You want to preview which paths would be included before reset or uninstall
title: "backup"
---
# `openclaw backup`

为 OpenClaw 状态、配置、认证档案、通道/提供商凭据、会话以及可选的工作区创建本地备份归档。

```bash
openclaw backup create
openclaw backup create --output ~/Backups
openclaw backup create --dry-run --json
openclaw backup create --verify
openclaw backup create --no-include-workspace
openclaw backup create --only-config
openclaw backup verify ./2026-03-09T00-00-00.000Z-openclaw-backup.tar.gz
```

## 注意

- 归档包含一个 ``manifest.json`` 文件，其中包含解析后的源路径和归档布局。
- 默认输出是当前工作目录中时间戳化的 ``.tar.gz`` 归档。
- 如果当前工作目录位于已备份的源树内部，OpenClaw 将回退到用户主目录作为默认归档位置。
- 现有的归档文件永远不会被覆盖。
- 为了避免自我包含，源状态/工作区树内的输出路径将被拒绝。
- ``openclaw backup verify <archive>`` 验证归档是否仅包含一个根清单，拒绝遍历风格的归档路径，并检查每个清单声明的有效负载是否存在于 tarball 中。
- ``openclaw backup create --verify`` 在写入归档后立即运行该验证。
- ``openclaw backup create --only-config`` 仅备份活动的 JSON 配置文件。

## 备份内容

``openclaw backup create`` 从您本地的 OpenClaw 安装规划备份源：

- OpenClaw 本地状态解析器返回的状态目录，通常是 ``~/.openclaw``
- 活动配置文件路径
- 当它存在于状态目录之外时，解析后的 ``credentials/`` 目录
- 从当前配置发现的工作区目录，除非您传递 ``--no-include-workspace``

模型认证档案已经是状态目录的一部分，位于
``agents/<agentId>/agent/auth-profiles.json``，因此它们通常由状态备份条目覆盖。

如果您使用 ``--only-config``，OpenClaw 将跳过状态、凭据目录和工作区发现，仅归档活动配置文件路径。

OpenClaw 在构建归档之前会对路径进行规范化。如果配置、
凭据目录或工作区已经位于状态目录内，
它们不会作为单独的一级备份源重复。缺失的路径将被
跳过。

归档有效负载存储来自这些源树的文件内容，嵌入的 ``manifest.json`` 记录解析后的绝对源路径以及用于每个资产的归档布局。

## 无效配置行为

``openclaw backup`` 有意绕过正常的配置预检，以便在恢复期间仍能提供帮助。由于工作区发现依赖于有效的配置，``openclaw backup create`` 现在会快速失败，当配置文件存在但无效且工作区备份仍处于启用状态时。

如果您在这种情况下仍想要部分备份，请重新运行：

````bash
openclaw backup create --no-include-workspace
````

这将使状态、配置和外部凭据目录在范围内，同时
完全跳过工作区发现。

如果您只需要配置文件本身的副本，``--only-config`` 在配置格式错误时也有效，因为它不依赖解析配置来发现工作区。

## 大小与性能

OpenClaw 不强制执行内置的最大备份大小或每文件大小限制。

实际限制来自本地机器和目标文件系统：

- 临时归档写入加上最终归档的可用空间
- 遍历大型工作区树并将其压缩为 ``.tar.gz`` 所需的时间
- 如果您使用 ``openclaw backup create --verify`` 或运行 ``openclaw backup verify``，重新扫描归档所需的时间
- 目标路径处的文件系统行为。OpenClaw 首选无覆盖硬链接发布步骤，当不支持硬链接时回退到独占复制

大型工作区通常是归档大小的主要驱动因素。如果您想要更小或更快的备份，请使用 ``--no-include-workspace``。

为了获得最小的归档，请使用 ``--only-config``。