---
summary: "CLI reference for `openclaw cron` (schedule and run background jobs)"
read_when:
  - You want scheduled jobs and wakeups
  - You’re debugging cron execution and logs
title: "cron"
---
# `openclaw cron`

管理 Gateway 调度程序的 cron 任务。

相关：

- cron 任务：[cron 任务](/automation/cron-jobs)

提示：运行 ``openclaw cron --help`` 以获取完整的命令集。

注意：隔离的 ``cron add`` 任务默认使用 ``--announce`` 交付。使用 ``--no-deliver`` 保持输出内部化。``--deliver`` 仍作为 ``--announce`` 的已弃用别名。

注意：由 cron 拥有的隔离运行期望一个纯文本摘要，且运行器拥有最终发送路径。``--no-deliver`` 保持运行内部化；它不会将交付交还给代理的消息工具。

注意：一次性（``--at``）任务默认在成功后删除。使用 ``--keep-after-run`` 保留它们。

注意：``--session`` 支持 ``main``、``isolated``、``current`` 和 ``session:<id>``。使用 ``current`` 在创建时绑定到活动会话，或使用 ``session:<id>`` 指定显式持久会话密钥。

注意：对于一次性 CLI 任务，无偏移量的 ``--at`` 日期时间被视为 UTC，除非你也传递 ``--tz <iana>``，后者会将给定时区中的本地挂钟时间解释为相应时间。

注意：重复任务现在在连续错误后使用指数退避重试（30 秒 → 1 分钟 → 5 分钟 → 15 分钟 → 60 分钟），然后在下次成功运行后恢复正常计划。

注意：``openclaw cron run`` 现在一旦手动运行被排队执行即返回。成功响应包括 ``{ ok: true, enqueued: true, runId }``；使用 ``openclaw cron runs --id <job-id>`` 跟踪最终结果。

注意：``openclaw cron run <job-id>`` 默认强制运行。使用 ``--due`` 保留较旧的“仅在到期时运行”行为。

注意：隔离 cron 会抑制过时的仅确认回复。如果第一个结果只是临时状态更新，且没有后代子代理运行负责最终答案，cron 会在交付前重新提示一次以获取真实结果。

注意：如果隔离的 cron 运行仅返回静默令牌（``NO_REPLY`` / ``no_reply``），cron 将抑制直接出站交付以及后备队列摘要路径，因此不会发布任何内容回聊天。

注意：``cron add|edit --model ...`` 使用该作业选择的允许模型。如果模型不被允许，cron 会发出警告并回退到作业的代理/默认模型选择。配置的后备链仍然适用，但无明确每作业后备列表的普通模型覆盖不再将代理主选作为隐藏的额外重试目标追加。

注意：隔离 cron 模型优先级首先是 Gmail 钩子覆盖，然后是每作业 ``--model``，然后是任何存储的 cron 会话模型覆盖，最后是正常代理/默认选择。

注意：隔离 cron 快速模式遵循解析后的实时模型选择。模型配置 ``params.fastMode`` 默认适用，但存储的会话 ``fastMode`` 覆盖仍然优于配置。

注意：如果隔离运行抛出 ``LiveSessionModelSwitchError``，cron 会在重试之前持久化切换的提供者/模型（以及存在的切换身份验证配置文件覆盖）。外部重试循环限制为初始尝试后的 2 次切换重试，然后中止而不是无限循环。

注意：失败通知首先使用 ``delivery.failureDestination``，然后是全局 ``cron.failureDestination``，最后在没有配置明确的失败目的地时回退到作业的主要公告目标。

注意：保留/修剪在配置中控制：

- ``cron.sessionRetention``（默认 ``24h``）修剪完成的隔离运行会话。
- ``cron.runLog.maxBytes`` + ``cron.runLog.keepLines`` 修剪 ``~/.openclaw/cron/runs/<jobId>.jsonl``。

升级说明：如果您有当前交付/存储格式之前的旧 cron 作业，请运行 ``openclaw doctor --fix``。Doctor 现在标准化旧 cron 字段（``jobId``、``schedule.cron``、顶级交付字段包括旧 ``threadId``、负载 ``provider`` 交付别名），并在配置 ``cron.webhook`` 时将简单的 ``notify: true`` webhook 后备作业迁移到显式 webhook 交付。

## 常见编辑

更新交付设置而不更改消息：

````bash
openclaw cron edit <job-id> --announce --channel telegram --to "123456789"
````

禁用隔离任务的交付：

````bash
openclaw cron edit <job-id> --no-deliver
````

启用隔离任务的轻量级引导上下文：

````bash
openclaw cron edit <job-id> --light-context
````

向特定频道公告：

````bash
openclaw cron edit <job-id> --announce --channel slack --to "channel:C1234567890"
````

创建具有轻量级引导上下文的隔离任务：

````bash
openclaw cron add \
  --name "Lightweight morning brief" \
  --cron "0 7 * * *" \
  --session isolated \
  --message "Summarize overnight updates." \
  --light-context \
  --no-deliver
````

``--light-context`` 仅适用于隔离的代理回合任务。对于 cron 运行，轻量模式保持引导上下文为空，而不是注入完整的工作区引导集。

交付所有权说明：

- 由 cron 拥有的隔离任务始终通过 cron 运行器路由最终用户可见的交付（``announce``、``webhook`` 或仅内部 ``none``）。
- 如果任务提到向某些外部收件人发送消息，代理应在其结果中描述预期目的地，而不是尝试直接发送。

## 常见管理员命令

手动运行：

````bash
openclaw cron run <job-id>
openclaw cron run <job-id> --due
openclaw cron runs --id <job-id> --limit 50
````

代理/会话重定向：

````bash
openclaw cron edit <job-id> --agent ops
openclaw cron edit <job-id> --clear-agent
openclaw cron edit <job-id> --session current
openclaw cron edit <job-id> --session "session:daily-brief"
````

交付调整：

````bash
openclaw cron edit <job-id> --announce --channel slack --to "channel:C1234567890"
openclaw cron edit <job-id> --best-effort-deliver
openclaw cron edit <job-id> --no-best-effort-deliver
openclaw cron edit <job-id> --no-deliver
````

失败交付说明：

- ``delivery.failureDestination`` 支持隔离任务。
- 主会话任务仅在主要交付模式为 ``webhook`` 时才可使用 ``delivery.failureDestination``。
- 如果您未设置任何失败目的地且任务已向频道公告，失败通知将重用该相同公告目标。