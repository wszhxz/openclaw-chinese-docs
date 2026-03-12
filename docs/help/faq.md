---
summary: "Frequently asked questions about OpenClaw setup, configuration, and usage"
read_when:
  - Answering common setup, install, onboarding, or runtime support questions
  - Triaging user-reported issues before deeper debugging
title: "FAQ"
---
# 常见问题解答（FAQ）

快速解答，以及针对实际部署场景（本地开发、VPS、多智能体、OAuth/API 密钥、模型故障转移）的深入排查指南。如需运行时诊断，请参阅 [故障排除](/gateway/troubleshooting)。如需完整配置参考，请参阅 [配置](/gateway/configuration)。

## 目录

- [快速入门与首次运行设置]
  - [我卡住了，最快脱困的方法是什么？](#im-stuck-whats-the-fastest-way-to-get-unstuck)
  - [安装和配置 OpenClaw 的推荐方式是什么？](#whats-the-recommended-way-to-install-and-set-up-openclaw)
  - [完成初始设置后，如何打开控制台？](#how-do-i-open-the-dashboard-after-onboarding)
  - [在本地（localhost）与远程环境下，如何对控制台（token）进行身份验证？](#how-do-i-authenticate-the-dashboard-token-on-localhost-vs-remote)
  - [我需要什么运行时环境？](#what-runtime-do-i-need)
  - [它能在树莓派（Raspberry Pi）上运行吗？](#does-it-run-on-raspberry-pi)
  - [树莓派安装有什么建议？](#any-tips-for-raspberry-pi-installs)
  - [它卡在“唤醒我的朋友” / 初始设置无法完成。现在该怎么办？](#it-is-stuck-on-wake-up-my-friend-onboarding-will-not-hatch-what-now)
  - [我可以将现有配置迁移到新机器（如 Mac mini）而不重新执行初始设置吗？](#can-i-migrate-my-setup-to-a-new-machine-mac-mini-without-redoing-onboarding)
  - [我在哪里可以查看最新版本中新增了哪些内容？](#where-do-i-see-what-is-new-in-the-latest-version)
  - [我无法访问 docs.openclaw.ai（SSL 错误）。现在该怎么办？](#i-cant-access-docsopenclawai-ssl-error-what-now)
  - [稳定版（stable）与测试版（beta）有何区别？](#whats-the-difference-between-stable-and-beta)
  - [如何安装测试版（beta），以及测试版（beta）与开发版（dev）有何区别？](#how-do-i-install-the-beta-version-and-whats-the-difference-between-beta-and-dev)
  - [如何尝试最新构建的版本？](#how-do-i-try-the-latest-bits)
  - [安装与初始设置通常需要多长时间？](#how-long-does-install-and-onboarding-usually-take)
  - [安装程序卡住了。我该如何获取更多反馈信息？](#installer-stuck-how-do-i-get-more-feedback)
  - [Windows 安装提示未找到 git 或无法识别 openclaw](#windows-install-says-git-not-found-or-openclaw-not-recognized)
  - [Windows 执行输出显示乱码中文，我该怎么办？](#windows-exec-output-shows-garbled-chinese-text-what-should-i-do)
  - [文档没有回答我的问题——我该如何获得更准确的答案？](#the-docs-didnt-answer-my-question-how-do-i-get-a-better-answer)
  - [如何在 Linux 上安装 OpenClaw？](#how-do-i-install-openclaw-on-linux)
  - [如何在 VPS 上安装 OpenClaw？](#how-do-i-install-openclaw-on-a-vps)
  - [云服务/VPS 安装指南在哪里？](#where-are-the-cloudvps-install-guides)
  - [我可以要求 OpenClaw 自动更新自身吗？](#can-i-ask-openclaw-to-update-itself)
  - [初始设置向导实际做了哪些事情？](#what-does-the-onboarding-wizard-actually-do)
  - [运行本项目是否需要 Claude 或 OpenAI 订阅？](#do-i-need-a-claude-or-openai-subscription-to-run-this)
  - [我可以仅使用 Claude Max 订阅而无需 API 密钥吗？](#can-i-use-claude-max-subscription-without-an-api-key)
  - [Anthropic 的 “setup-token” 认证机制是如何工作的？](#how-does-anthropic-setuptoken-auth-work)
  - [我在哪里可以找到 Anthropic 的 setup-token？](#where-do-i-find-an-anthropic-setuptoken)
  - [是否支持 Claude 订阅认证（Claude Pro 或 Max）？](#do-you-support-claude-subscription-auth-claude-pro-or-max)
  - [为什么我从 Anthropic 收到了 `HTTP 429: rate_limit_error`？](#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)
  - [是否支持 AWS Bedrock？](#is-aws-bedrock-supported)
  - [Codex 认证机制是如何工作的？](#how-does-codex-auth-work)
  - [是否支持 OpenAI 订阅认证（Codex OAuth）？](#do-you-support-openai-subscription-auth-codex-oauth)
  - [如何设置 Gemini CLI OAuth？](#how-do-i-set-up-gemini-cli-oauth)
  - [本地模型是否适用于日常闲聊？](#is-a-local-model-ok-for-casual-chats)
  - [如何确保托管模型的流量保留在特定区域？](#how-do-i-keep-hosted-model-traffic-in-a-specific-region)
  - [我必须购买 Mac Mini 才能安装本项目吗？](#do-i-have-to-buy-a-mac-mini-to-install-this)
  - [我需要 Mac mini 才能支持 iMessage 吗？](#do-i-need-a-mac-mini-for-imessage-support)
  - [如果我购买一台 Mac mini 来运行 OpenClaw，能否将其连接到我的 MacBook Pro？](#if-i-buy-a-mac-mini-to-run-openclaw-can-i-connect-it-to-my-macbook-pro)
  - [我可以使用 Bun 吗？](#can-i-use-bun)
  - [Telegram：``allowFrom`` 中应填写什么？](#telegram-what-goes-in-allowfrom)
  - [多个用户能否共用一个 WhatsApp 号码，并各自运行不同的 OpenClaw 实例？](#can-multiple-people-use-one-whatsapp-number-with-different-openclaw-instances)
  - [我可以同时运行一个“快速聊天”智能体和一个“Opus 编程专用”智能体吗？](#can-i-run-a-fast-chat-agent-and-an-opus-for-coding-agent)
  - [Homebrew 是否支持 Linux？](#does-homebrew-work-on-linux)
  - [可修改源码（git）安装方式与 npm 安装方式有何区别？](#whats-the-difference-between-the-hackable-git-install-and-npm-install)
  - [之后能否在 npm 安装与 git 安装之间切换？](#can-i-switch-between-npm-and-git-installs-later)
  - [我应该在我的笔记本电脑还是 VPS 上运行 Gateway？](#should-i-run-the-gateway-on-my-laptop-or-a-vps)
  - [将 OpenClaw 运行在专用设备上有多重要？](#how-important-is-it-to-run-openclaw-on-a-dedicated-machine)
  - [VPS 的最低配置要求及推荐操作系统是什么？](#what-are-the-minimum-vps-requirements-and-recommended-os)
  - [我可以在虚拟机（VM）中运行 OpenClaw 吗？有哪些要求？](#can-i-run-openclaw-in-a-vm-and-what-are-the-requirements)
- [什么是 OpenClaw？](#what-is-openclaw)
  - [用一段话概括 OpenClaw 是什么？](#what-is-openclaw-in-one-paragraph)
  - [它的核心价值主张是什么？](#whats-the-value-proposition)
  - [我刚刚完成部署，接下来该做什么？](#i-just-set-it-up-what-should-i-do-first)
  - [OpenClaw 最常用的五大日常应用场景是什么？](#what-are-the-top-five-everyday-use-cases-for-openclaw)
  - [OpenClaw 能否协助 SaaS 公司开展潜在客户获取（lead gen）相关的外联广告与博客撰写？](#can-openclaw-help-with-lead-gen-outreach-ads-and-blogs-for-a-saas)
  - [相较于 Claude Code，OpenClaw 在 Web 开发方面有哪些优势？](#what-are-the-advantages-vs-claude-code-for-web-development)
- [技能与自动化](#skills-and-automation)
  - [如何自定义技能，同时避免污染代码仓库？](#how-do-i-customize-skills-without-keeping-the-repo-dirty)
  - [我可以从自定义文件夹加载技能吗？](#can-i-load-skills-from-a-custom-folder)
  - [我如何为不同任务指定不同模型？](#how-can-i-use-different-models-for-different-tasks)
  - [机器人在执行繁重任务时会冻结。我该如何卸载这些负载？](#the-bot-freezes-while-doing-heavy-work-how-do-i-offload-that)
  - [定时任务（Cron）或提醒功能未触发。我应检查哪些方面？](#cron-or-reminders-do-not-fire-what-should-i-check)
  - [如何在 Linux 上安装技能？](#how-do-i-install-skills-on-linux)
  - [OpenClaw 是否支持按计划调度或持续后台运行任务？](#can-openclaw-run-tasks-on-a-schedule-or-continuously-in-the-background)
  - [我能否在 Linux 上运行仅限 Apple macOS 的技能？](#can-i-run-apple-macos-only-skills-from-linux)
  - [你们是否提供 Notion 或 HeyGen 集成？](#do-you-have-a-notion-or-heygen-integration)
  - [如何安装用于浏览器接管的 Chrome 扩展？](#how-do-i-install-the-chrome-extension-for-browser-takeover)
- [沙箱与内存](#sandboxing-and-memory)
  - [是否有专门介绍沙箱机制的文档？](#is-there-a-dedicated-sandboxing-doc)
  - [如何将主机文件夹挂载进沙箱？](#how-do-i-bind-a-host-folder-into-the-sandbox)
  - [内存机制是如何工作的？](#how-does-memory-work)
  - [记忆总是被遗忘。我该如何让其持久化？](#memory-keeps-forgetting-things-how-do-i-make-it-stick)
  - [记忆是否会永久保留？其限制是什么？](#does-memory-persist-forever-what-are-the-limits)
  - [语义记忆搜索是否需要 OpenAI API 密钥？](#does-semantic-memory-search-require-an-openai-api-key)
- [数据在磁盘上的存储位置](#where-things-live-on-disk)
  - [所有与 OpenClaw 交互的数据是否都保存在本地？](#is-all-data-used-with-openclaw-saved-locally)
  - [OpenClaw 将其数据存储在何处？](#where-does-openclaw-store-its-data)
  - [`AGENTS.md` / `SOUl.md` / `USER.md` / `MEMORY.md` 应该放在哪里？](#where-should-agentsmd-soulmd-usermd-memorymd-live)
  - [推荐的备份策略是什么？](#whats-the-recommended-backup-strategy)
  - [我该如何彻底卸载 OpenClaw？](#how-do-i-completely-uninstall-openclaw)
  - [智能体能否在工作区之外运行？](#can-agents-work-outside-the-workspace)
  - [我处于远程模式——会话存储（session store）位于何处？](#im-in-remote-mode-where-is-the-session-store)
- [配置基础](#config-basics)
  - [配置文件采用什么格式？它存放在哪里？](#what-format-is-the-config-where-is-it)
  - [我设置了 ``gateway.bind: "lan"``（或 ``"tailnet"``），结果没有任何服务监听 / UI 显示“未授权”](#i-set-gatewaybind-lan-or-tailnet-and-now-nothing-listens-the-ui-says-unauthorized)
  - [为什么我现在在 localhost 上也需要 token？](#why-do-i-need-a-token-on-localhost-now)
  - [修改配置后是否必须重启？](#do-i-have-to-restart-after-changing-config)
  - [如何禁用 CLI 中有趣的标语（taglines）？](#how-do-i-disable-funny-cli-taglines)
  - [如何启用网页搜索（及网页抓取）？](#how-do-i-enable-web-search-and-web-fetch)
  - [`config.apply` 清空了我的配置。我该如何恢复并避免此类问题？](#configapply-wiped-my-config-how-do-i-recover-and-avoid-this)
  - [如何跨设备运行一个中心化的 Gateway 并搭配专用 Worker？](#how-do-i-run-a-central-gateway-with-specialized-workers-across-devices)
  - [OpenClaw 浏览器能否以无头（headless）模式运行？](#can-the-openclaw-browser-run-headless)
  - [如何使用 Brave 浏览器实现浏览器控制？](#how-do-i-use-brave-for-browser-control)
- [远程网关与节点](#remote-gateways-and-nodes)
  - [命令如何在 Telegram、Gateway 和节点之间传播？](#how-do-commands-propagate-between-telegram-the-gateway-and-nodes)
  - [如果 Gateway 托管在远程服务器上，我的智能体如何访问我的本地计算机？](#how-can-my-agent-access-my-computer-if-the-gateway-is-hosted-remotely)
  - [Tailscale 已连接，但我收不到任何回复。

接下来该怎么办？](#tailscale-is-connected-but-i-get-no-replies-what-now)
  - [两个 OpenClaw 实例能否相互通信（本地 + VPS）？](#can-two-openclaw-instances-talk-to-each-other-local-vps)
  - [多个智能体是否需要各自独立的 VPS？](#do-i-need-separate-vpses-for-multiple-agents)
  - [使用个人笔记本上的节点，相比从 VPS 发起 SSH 连接，有何优势？](#is-there-a-benefit-to-using-a-node-on-my-personal-laptop-instead-of-ssh-from-a-vps)
  - [节点是否运行网关服务？](#do-nodes-run-a-gateway-service)
  - [是否存在通过 API / RPC 方式应用配置的方法？](#is-there-an-api-rpc-way-to-apply-config)
  - [首次安装所需的最小“合理”配置是什么？](#whats-a-minimal-sane-config-for-a-first-install)
  - [如何在 VPS 上设置 Tailscale 并从 Mac 连接？](#how-do-i-set-up-tailscale-on-a-vps-and-connect-from-my-mac)
  - [如何将 Mac 节点连接至远程网关（Tailscale Serve）？](#how-do-i-connect-a-mac-node-to-a-remote-gateway-tailscale-serve)
  - [我应该在第二台笔记本上重新安装，还是仅添加一个节点？](#should-i-install-on-a-second-laptop-or-just-add-a-node)
- [环境变量与 `.env` 文件加载](#env-vars-and-env-loading)
  - [OpenClaw 如何加载环境变量？](#how-does-openclaw-load-environment-variables)
  - [“我通过系统服务启动了网关，但我的环境变量丢失了。”接下来该怎么办？](#i-started-the-gateway-via-the-service-and-my-env-vars-disappeared-what-now)
  - [我设置了 ``COPILOT_GITHUB_TOKEN``，但模型状态却显示“Shell env: off.”，为什么？](#i-set-copilotgithubtoken-but-models-status-shows-shell-env-off-why)
- [会话与多轮对话](#sessions-and-multiple-chats)
  - [如何开启一次全新对话？](#how-do-i-start-a-fresh-conversation)
  - [如果我从未发送 ``/new``，会话是否会自动重置？](#do-sessions-reset-automatically-if-i-never-send-new)
  - [能否将一组 OpenClaw 实例组织为一个 CEO 和多个智能体的协作团队？](#is-there-a-way-to-make-a-team-of-openclaw-instances-one-ceo-and-many-agents)
  - [为何上下文在任务中途被截断？如何避免？](#why-did-context-get-truncated-midtask-how-do-i-prevent-it)
  - [如何彻底重置 OpenClaw，同时保留其已安装状态？](#how-do-i-completely-reset-openclaw-but-keep-it-installed)
  - [我收到“context too large”错误——该如何重置或压缩上下文？](#im-getting-context-too-large-errors-how-do-i-reset-or-compact)
  - [为何我看到“LLM request rejected: messages.content.tool_use.input field required”？](#why-am-i-seeing-llm-request-rejected-messagescontenttool_useinput-field-required)
  - [为何我每 30 分钟就会收到一次心跳消息？](#why-am-i-getting-heartbeat-messages-every-30-minutes)
  - [我是否需要向 WhatsApp 群组中添加一个“机器人账号”？](#do-i-need-to-add-a-bot-account-to-a-whatsapp-group)
  - [如何获取 WhatsApp 群组的 JID？](#how-do-i-get-the-jid-of-a-whatsapp-group)
  - [为何 OpenClaw 在群组中不回复消息？](#why-doesnt-openclaw-reply-in-a-group)
  - [群组/会话线程是否与私聊共享上下文？](#do-groupsthreads-share-context-with-dms)
  - [我可以创建多少个工作区和智能体？](#how-many-workspaces-and-agents-can-i-create)
  - [我能否同时运行多个机器人或聊天（例如 Slack），以及应如何配置？](#can-i-run-multiple-bots-or-chats-at-the-same-time-slack-and-how-should-i-set-that-up)
- [模型：默认值、选择、别名、切换](#models-defaults-selection-aliases-switching)
  - [什么是“默认模型”？](#what-is-the-default-model)
  - [您推荐使用哪个模型？](#what-model-do-you-recommend)
  - [如何在不擦除现有配置的前提下切换模型？](#how-do-i-switch-models-without-wiping-my-config)
  - [能否使用自托管模型（如 llama.cpp、vLLM、Ollama）？](#can-i-use-selfhosted-models-llamacpp-vllm-ollama)
  - [OpenClaw、Flawd 和 Krill 分别使用哪些模型？](#what-do-openclaw-flawd-and-krill-use-for-models)
  - [如何动态切换模型（无需重启）？](#how-do-i-switch-models-on-the-fly-without-restarting)
  - [能否对日常任务使用 GPT 5.2，而对编程任务使用 Codex 5.3？](#can-i-use-gpt-52-for-daily-tasks-and-codex-53-for-coding)
  - [为何我看到“Model … is not allowed”，随后无任何回复？](#why-do-i-see-model-is-not-allowed-and-then-no-reply)
  - [为何我看到“Unknown model: minimax/MiniMax-M2.5”？](#why-do-i-see-unknown-model-minimaxminimaxm25)
  - [能否将 MiniMax 设为默认模型，而对复杂任务使用 OpenAI？](#can-i-use-minimax-as-my-default-and-openai-for-complex-tasks)
  - [opus / sonnet / gpt 是否为内置快捷方式？](#are-opus-sonnet-gpt-builtin-shortcuts)
  - [如何定义/覆盖模型快捷方式（别名）？](#how-do-i-defineoverride-model-shortcuts-aliases)
  - [如何添加来自其他服务商（如 OpenRouter 或 Z.AI）的模型？](#how-do-i-add-models-from-other-providers-like-openrouter-or-zai)
- [模型故障转移与“All models failed”错误](#model-failover-and-all-models-failed)
  - [故障转移机制是如何工作的？](#how-does-failover-work)
  - [该错误意味着什么？](#what-does-this-error-mean)
  - [``No credentials found for profile "anthropic:default"`` 故障排查清单](#fix-checklist-for-no-credentials-found-for-profile-anthropicdefault)
  - [为何它还尝试了 Google Gemini 却失败了？](#why-did-it-also-try-google-gemini-and-fail)
- [认证配置文件：含义及管理方式](#auth-profiles-what-they-are-and-how-to-manage-them)
  - [什么是认证配置文件？](#what-is-an-auth-profile)
  - [典型的配置文件 ID 有哪些？](#what-are-typical-profile-ids)
  - [我能控制优先尝试哪个认证配置文件吗？](#can-i-control-which-auth-profile-is-tried-first)
  - [OAuth 与 API 密钥的区别是什么？](#oauth-vs-api-key-whats-the-difference)
- [网关：端口、“已在运行”提示及远程模式](#gateway-ports-already-running-and-remote-mode)
  - [网关使用哪个端口？](#what-port-does-the-gateway-use)
  - [为何 ``openclaw gateway status`` 显示 ``Runtime: running``，但 ``RPC probe: failed``？](#why-does-openclaw-gateway-status-say-runtime-running-but-rpc-probe-failed)
  - [为何 ``openclaw gateway status`` 显示的 `config-cli` 与 `config-service` 不同？](#why-does-openclaw-gateway-status-show-config-cli-and-config-service-different)
  - [“另一个网关实例已在监听”是什么意思？](#what-does-another-gateway-instance-is-already-listening-mean)
  - [如何以远程模式运行 OpenClaw（客户端连接至其他位置的网关）？](#how-do-i-run-openclaw-in-remote-mode-client-connects-to-a-gateway-elsewhere)
  - [控制界面显示“未授权”（或持续重连），接下来该怎么办？](#the-control-ui-says-unauthorized-or-keeps-reconnecting-what-now)
  - [我设置了 ``gateway.bind: "tailnet"``，但它无法绑定 / 没有任何端口监听，怎么办？](#i-set-gatewaybind-tailnet-but-it-cant-bind-nothing-listens)
  - [能否在同一主机上运行多个网关？](#can-i-run-multiple-gateways-on-the-same-host)
  - [“无效握手” / 错误码 1008 是什么意思？](#what-does-invalid-handshake-code-1008-mean)
- [日志与调试](#logging-and-debugging)
  - [日志存放在哪里？](#where-are-logs)
  - [如何启动/停止/重启网关服务？](#how-do-i-startstoprestart-the-gateway-service)
  - [我在 Windows 上关闭了终端——如何重新启动 OpenClaw？](#i-closed-my-terminal-on-windows-how-do-i-restart-openclaw)
  - [网关已启动，但回复始终未到达。我应检查哪些方面？](#the-gateway-is-up-but-replies-never-arrive-what-should-i-check)
  - [“Disconnected from gateway: no reason”——接下来该怎么办？](#disconnected-from-gateway-no-reason-what-now)
  - [Telegram 的 setMyCommands 因网络错误失败。我应检查哪些方面？](#telegram-setmycommands-fails-with-network-errors-what-should-i-check)
  - [TUI 无任何输出。我应检查哪些方面？](#tui-shows-no-output-what-should-i-check)
  - [如何彻底停止再重新启动网关？](#how-do-i-completely-stop-then-start-the-gateway)
  - [小白解释：``openclaw gateway restart`` 与 ``openclaw gateway`` 的区别](#eli5-openclaw-gateway-restart-vs-openclaw-gateway)
  - [当某项操作失败时，最快获取详细信息的方式是什么？](#whats-the-fastest-way-to-get-more-details-when-something-fails)
- [媒体与附件](#media-and-attachments)
  - [我的技能生成了一张图片/PDF，但没有任何内容被发送出去](#my-skill-generated-an-imagepdf-but-nothing-was-sent)
- [安全与访问控制](#security-and-access-control)
  - [将 OpenClaw 暴露给入站私信是否安全？](#is-it-safe-to-expose-openclaw-to-inbound-dms)
  - [提示注入攻击是否仅对公开机器人构成威胁？](#is-prompt-injection-only-a-concern-for-public-bots)
  - [我的机器人是否应拥有独立的邮箱 GitHub 账号或手机号？](#should-my-bot-have-its-own-email-github-account-or-phone-number)
  - [能否赋予它对我短信的自主控制权？这样做安全吗？](#can-i-give-it-autonomy-over-my-text-messages-and-is-that-safe)
  - [能否对个人助理类任务使用成本更低的模型？](#can-i-use-cheaper-models-for-personal-assistant-tasks)
  - [我在 Telegram 中运行了 ``/start``，但未收到配对码](#i-ran-start-in-telegram-but-didnt-get-a-pairing-code)
  - [WhatsApp：它会向我的联系人发送消息吗？配对机制是怎样的？](#whatsapp-will-it-message-my-contacts-how-does-pairing-work)
- [聊天命令、中止任务与“停不下来”问题](#chat-commands-aborting-tasks-and-it-wont-stop)
  - [如何阻止内部系统消息显示在聊天窗口中？](#how-do-i-stop-internal-system-messages-from-showing-in-chat)
  - [如何停止/取消一个正在运行的任务？](#how-do-i-stopcancel-a-running-task)
  - [如何从 Telegram 向 Discord 发送消息？（提示：“跨上下文消息被拒绝”）](#how-do-i-send-a-discord-message-from-telegram-crosscontext-messaging-denied)
  - [为何感觉机器人会“忽略”连续快速发送的消息？](#why-does-it-feel-like-the-bot-ignores-rapidfire-messages)

## 如果出现问题，前60秒应急指南

1. **快速状态检查（首要检查）**

   ```bash
   openclaw status
   ```

   本地快速概览：操作系统及更新状态、网关/服务可达性、代理/会话、提供商配置 + 运行时问题（仅当网关可达时）。

2. **可粘贴报告（可安全分享）**

   ```bash
   openclaw status --all
   ```

   只读诊断信息，附带日志尾部（令牌已脱敏）。

3. **守护进程 + 端口状态**

   ```bash
   openclaw gateway status
   ```

   显示 supervisor 运行时状态与 RPC 可达性、探测目标 URL，以及服务实际加载的配置。

4. **深度探测**

   ```bash
   openclaw status --deep
   ```

   执行网关健康检查 + 提供商探测（需网关可达）。参见 [Health](/gateway/health)。

5. **查看最新日志**

   ```bash
   openclaw logs --follow
   ```

   若 RPC 不可用，则回退至：

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   文件日志与服务日志相互独立；详见 [Logging](/logging) 和 [Troubleshooting](/gateway/troubleshooting)。

6. **运行 doctor（自动修复）**

   ```bash
   openclaw doctor
   ```

   修复/迁移配置与状态，并执行健康检查。参见 [Doctor](/gateway/doctor)。

7. **网关快照**

   ```bash
   openclaw health --json
   openclaw health --verbose   # shows the target URL + config path on errors
   ```

   向正在运行的网关请求完整快照（仅限 WebSocket 协议）。参见 [Health](/gateway/health)。

## 快速入门与首次运行设置

### 我卡住了，最快脱困方式是什么？

使用一个能**看到你本机环境**的本地 AI 代理。这远比在 Discord 中提问更高效，因为大多数“我卡住了”的情况都属于**本地配置或环境问题**，远程协助者无法直接检查。

- **Claude Code**：[https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
- **OpenAI Codex**：[https://openai.com/codex/](https://openai.com/codex/)

这些工具可读取代码仓库、执行命令、检查日志，并协助修复你的机器级配置（PATH、服务、权限、认证文件等）。请通过可修改（基于 git）的安装方式，向其提供**完整的源码检出副本**：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
```

该方式从 git 检出安装 OpenClaw，因此 AI 代理可读取源码与文档，并准确推理你当前运行的确切版本。之后你随时可通过不带 `--install-method git` 参数重新运行安装器，切换回稳定版。

提示：请让 AI 代理先**规划并监督**修复流程（分步执行），再仅执行必要命令。这样可使变更最小化，也更便于审计。

如你发现真实 Bug 或修复方案，请提交 GitHub Issue 或 Pull Request：
[https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)  
[https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

请先运行以下命令（求助时请一并提供输出）：

```bash
openclaw status
openclaw models status
openclaw doctor
```

各命令作用如下：

- `openclaw status`：快速获取网关/代理健康状态 + 基础配置快照。
- `openclaw models status`：检查提供商认证状态 + 模型可用性。
- `openclaw doctor`：验证并修复常见配置/状态问题。

其他有用的 CLI 检查命令：`openclaw status --all`、`openclaw logs --follow`、  
`openclaw gateway status`、`openclaw health --verbose`。

快速调试循环：[如果出现问题，前60秒应急指南](#first-60-seconds-if-somethings-broken)。  
安装文档：[Install](/install)、[Installer flags](/install/installer)、[Updating](/install/updating)。

### 安装和设置 OpenClaw 的推荐方式是什么？

本仓库推荐从源码运行，并使用引导向导：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard --install-daemon
```

该向导还可自动构建 UI 资源。完成引导后，网关通常运行于端口 **18789**。

从源码运行（贡献者/开发者）：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm build
pnpm ui:build # auto-installs UI deps on first run
openclaw onboard
```

若尚未全局安装，可通过 `pnpm openclaw onboard` 运行。

### 引导完成后如何打开仪表板？

向导会在引导完成后立即用浏览器打开一个干净（非令牌化）的仪表板 URL，并同时在摘要中打印该链接。请保持该标签页开启；若未自动打开，请在同一台机器上复制粘贴控制台打印的 URL。

### 如何在 localhost 与远程环境下对仪表板令牌进行身份验证？

**本地主机（同一台机器）：**

- 打开 `http://127.0.0.1:18789/`。
- 若提示身份验证，请将 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）中的令牌粘贴至 Control UI 设置中。
- 从网关主机获取令牌：`openclaw config get gateway.auth.token`（或生成新令牌：`openclaw doctor --generate-gateway-token`）。

**非本地主机：**

- **Tailscale Serve（推荐）**：保持绑定为回环地址，运行 `openclaw gateway --tailscale serve`，然后打开 `https://<magicdns>/`。若 `gateway.auth.allowTailscale` 为 `true`，则身份标识头（identity headers）即可满足 Control UI/WebSocket 认证要求（无需令牌，假定网关主机可信）；HTTP API 仍需令牌/密码。
- **Tailnet 绑定**：运行 `openclaw gateway --bind tailnet --token "<token>"`，打开 `http://<tailscale-ip>:18789/`，并在仪表板设置中粘贴令牌。
- **SSH 隧道**：执行 `ssh -N -L 18789:127.0.0.1:18789 user@host`，然后打开 `http://127.0.0.1:18789/` 并在 Control UI 设置中粘贴令牌。

详见 [Dashboard](/web/dashboard) 与 [Web surfaces](/web)，了解绑定模式与认证细节。

### 我需要什么运行时环境？

必须使用 **Node >= 22**。推荐使用 `pnpm`。Bun **不推荐**用于网关。

### 它能在树莓派上运行吗？

可以。网关非常轻量——文档中标明 **512MB–1GB 内存**、**1 核 CPU** 及约 **500MB 磁盘空间** 即可满足个人使用需求，并特别注明 **Raspberry Pi 4 可运行该网关**。

若你希望预留更多余量（用于日志、媒体或其他服务），**推荐 2GB 内存**，但这并非硬性最低要求。

提示：小型树莓派或 VPS 即可托管网关，你还可以将 **节点（nodes）** 配对至笔记本电脑或手机，以支持本地屏幕/摄像头/画布或命令执行。参见 [Nodes](/nodes)。

### 树莓派安装有何建议？

简而言之：可行，但需预期存在一些粗糙之处。

- 使用 **64 位** 操作系统，并确保 Node >= 22。
- 优先选择 **可修改（git）安装方式**，以便查看日志并快速更新。
- 初始启动时不启用频道/技能，待基础运行稳定后再逐个添加。
- 若遇到奇怪的二进制问题，通常是 **ARM 兼容性** 问题。

文档参考：[Linux](/platforms/linux)、[Install](/install)。

### 它卡在“唤醒我的朋友”引导界面，无法继续，怎么办？

该界面依赖网关可达且已完成身份验证。TUI 也会在首次孵化时自动发送 “Wake up, my friend!”。若你看到该提示行却**无任何响应**，且令牌计数始终为 0，则代理从未运行。

1. 重启网关：

```bash
openclaw gateway restart
```

2. 检查状态与认证：

```bash
openclaw status
openclaw models status
openclaw logs --follow
```

3. 若仍卡住，请运行：

```bash
openclaw doctor
```

若网关位于远程，请确保隧道/Tailscale 连接已就绪，且 UI 指向正确的网关。参见 [Remote access](/gateway/remote)。

### 我能否将现有配置迁移到新机器（如 Mac mini）而无需重新引导？

可以。只需复制 **状态目录（state directory）** 和 **工作区（workspace）**，然后运行一次 Doctor。只要**同时复制这两个位置**，即可使你的机器人“完全一致”（记忆、会话历史、认证信息及频道状态）：

1. 在新机器上安装 OpenClaw。
2. 从旧机器复制 `$OPENCLAW_STATE_DIR`（默认路径：`~/.openclaw`）。
3. 复制你的工作区（默认路径：`~/.openclaw/workspace`）。
4. 运行 `openclaw doctor` 并重启网关服务。

此操作可保留配置、认证配置文件、WhatsApp 凭据、会话及记忆。若处于远程模式，请注意会话存储与工作区均由网关主机持有。

**重要提示：** 若你仅将工作区提交/推送至 GitHub，则只备份了 **记忆 + 初始化文件**，而**不会备份**会话历史或认证信息。这些内容存放在 `~/.openclaw/` 下（例如 `~/.openclaw/agents/<agentId>/sessions/`）。

相关文档：[Migrating](/install/migrating)、[Where things live on disk](/help/faq#where-does-openclaw-store-its-data)、  
[Agent workspace](/concepts/agent-workspace)、[Doctor](/gateway/doctor)、[Remote mode](/gateway/remote)。

### 我在哪里能看到最新版本的更新内容？

请查阅 GitHub 更新日志：  
[https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

最新条目位于顶部。若顶部章节标记为 **Unreleased**，则下一个带日期的章节即为最新发布的版本。条目按 **Highlights（亮点）**、**Changes（变更）** 和 **Fixes（修复）** 分组（必要时还包括文档/其他类别）。

### 我无法访问 docs.openclaw.ai，出现 SSL 错误，怎么办？

部分 Comcast/Xfinity 网络连接会因 Xfinity 高级安全功能错误拦截 `docs.openclaw.ai`。请禁用该功能或允许 `docs.openclaw.ai`，然后重试。更多详情参见：[Troubleshooting](/help/troubleshooting#docsopenclawai-shows-an-ssl-error-comcastxfinity)。  
欢迎通过此处帮助我们解除屏蔽：[https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status)。

若仍无法访问该网站，文档亦镜像托管于 GitHub：  
[https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

### stable 与 beta 版本有何区别？

**stable** 与 **beta** 是 **npm dist-tags（分发标签）**，而非独立代码分支：

- `latest` = 稳定版  
- `beta` = 用于测试的早期构建版  

我们会将构建产物发布至 **beta**，经充分测试后，一旦某构建版确认稳定，便**将同一版本提升至 `latest`**。正因如此，beta 与 stable 可能指向**同一版本号**。

查看变更内容：  
[https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

### 如何安装 Beta 版本？Beta 与 Dev 有何区别？

**Beta** 是 npm 的 dist-tag `beta`（可能与 `latest` 一致）。  
**Dev** 是 `main`（git）的持续演进主干；发布时使用 npm 的 dist-tag `dev`。

一键安装命令（macOS/Linux）：

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
```

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
```

Windows 安装程序（PowerShell）：  
[https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

更多详情：[开发通道](/install/development-channels) 和 [安装程序标志](/install/installer)。

### 安装与初始配置通常需要多长时间？

大致参考：

- **安装：** 2–5 分钟  
- **初始配置：** 5–15 分钟，具体取决于您配置的频道/模型数量  

若卡住，请参阅 [安装程序卡住](/help/faq#installer-stuck-how-do-i-get-more-feedback)，  
以及 [我卡住了](/help/faq#im-stuck--whats-the-fastest-way-to-get-unstuck) 中的快速调试循环。

### 如何尝试最新版本？

两种方式：

1. **Dev 通道（git checkout）：**

```bash
openclaw update --channel dev
```

该命令切换至 `main` 分支，并从源码更新。

2. **可编辑安装（通过安装程序网站）：**

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
```

这将为您生成一个本地代码仓库，您可直接编辑，再通过 git 更新。

若您希望手动执行干净克隆，请使用：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm build
```

文档：[更新](/cli/update)、[开发通道](/install/development-channels)、[安装](/install)。

### 安装程序卡住了，如何获取更多信息？

以**详细输出模式**重新运行安装程序：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
```

启用详细日志的 Beta 安装：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
```

对于可编辑（git）安装：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
```

Windows（PowerShell）等效命令：

```powershell
# install.ps1 has no dedicated -Verbose flag yet.
Set-PSDebug -Trace 1
& ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
Set-PSDebug -Trace 0
```

更多选项：[安装程序标志](/install/installer)。

### Windows 安装提示“未找到 git”或“无法识别 openclaw”

Windows 上两个常见问题：

**1) npm 报错 spawn git / 未找到 git**

- 安装 **Git for Windows**，并确保 `git` 已加入您的 PATH。  
- 关闭并重新打开 PowerShell，然后重试安装程序。

**2) 安装后提示“无法识别 openclaw”**

- 您的 npm 全局 bin 目录未加入 PATH。  
- 检查路径：

  ```powershell
  npm config get prefix
  ```

- 将该目录添加到您的用户 PATH（Windows 上无需添加 `\bin` 后缀；在大多数系统上为 `%AppData%\npm`）。  
- 更新 PATH 后，请关闭并重新打开 PowerShell。

如需最顺畅的 Windows 配置体验，建议改用 **WSL2** 而非原生 Windows。  
文档：[Windows](/platforms/windows)。

### Windows 执行输出中显示乱码中文，该如何处理？

这通常是原生 Windows 终端中控制台代码页不匹配所致。

典型现象：

- `system.run`/`exec` 输出将中文渲染为乱码（mojibake）  
- 同一命令在其他终端配置文件中显示正常  

PowerShell 快速临时解决方案：

```powershell
chcp 65001
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
```

然后重启 Gateway 并重试命令：

```powershell
openclaw gateway restart
```

若您在最新版 OpenClaw 中仍复现此问题，请在以下位置跟踪或提交报告：

- [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

### 文档未解答我的问题，如何获得更准确的回答？

请使用 **可编辑（git）安装**，以便在本地拥有完整源码和文档，然后在该目录下向您的 Bot（或 Claude/Codex）提问，使其能读取整个代码仓库并给出精准回答。

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
```

更多详情：[安装](/install) 和 [安装程序标志](/install/installer)。

### 如何在 Linux 上安装 OpenClaw？

简要回答：遵循 Linux 指南，然后运行初始配置向导。

- Linux 快速路径 + 服务安装：[Linux](/platforms/linux)。  
- 完整操作指南：[入门](/start/getting-started)。  
- 安装与更新：[安装与更新](/install/updating)。

### 如何在 VPS 上安装 OpenClaw？

任意 Linux VPS 均可。在服务器上完成安装后，即可通过 SSH/Tailscale 访问 Gateway。

相关指南：[exe.dev](/install/exe-dev)、[Hetzner](/install/hetzner)、[Fly.io](/install/fly)。  
远程访问：[Gateway 远程访问](/gateway/remote)。

### 云 VPS 安装指南在哪里？

我们维护了一个涵盖主流服务商的 **托管中心（hosting hub）**。请选择任一服务商并按对应指南操作：

- [VPS 托管](/vps)（所有服务商汇总）  
- [Fly.io](/install/fly)  
- [Hetzner](/install/hetzner)  
- [exe.dev](/install/exe-dev)

在云端的工作原理：**Gateway 运行于服务器上**，您可通过控制界面（Control UI）或 Tailscale/SSH 从笔记本电脑/手机访问它。您的状态（state）与工作区（workspace）均保存在服务器上，因此请将服务器视为唯一可信数据源，并为其做好备份。

您还可将 **节点（nodes）**（Mac/iOS/Android/无头设备）配对至该云 Gateway，从而访问本地屏幕/摄像头/画布，或在笔记本电脑上执行命令，同时保持 Gateway 位于云端。

中心入口：[平台](/platforms)。远程访问：[Gateway 远程访问](/gateway/remote)。  
节点相关：[节点](/nodes)、[节点 CLI](/cli/nodes)。

### 我能否让 OpenClaw 自动更新自身？

简要回答：**技术上可行，但不推荐**。更新流程可能导致 Gateway 重启（中断当前会话）、需要执行干净的 git 克隆，且可能弹出确认提示。更稳妥的方式是：由操作员在 Shell 中手动执行更新。

请使用 CLI：

```bash
openclaw update
openclaw update status
openclaw update --channel stable|beta|dev
openclaw update --tag <dist-tag|version>
openclaw update --no-restart
```

若必须由 Agent 自动化执行：

```bash
openclaw update --yes --no-restart
openclaw gateway restart
```

文档：[更新](/cli/update)、[更新说明](/install/updating)。

### 初始配置向导实际执行了哪些操作？

`openclaw onboard` 是推荐的设置路径。在 **本地模式** 下，它将引导您完成以下步骤：

- **模型/认证配置**（支持提供商 OAuth/设置令牌流程及 API 密钥，也支持 LM Studio 等本地模型）  
- **工作区（Workspace）** 位置及初始化文件  
- **Gateway 设置**（绑定地址/端口/认证/Tailscale）  
- **消息提供商**（WhatsApp、Telegram、Discord、Mattermost（插件）、Signal、iMessage）  
- **守护进程安装**（macOS 上为 LaunchAgent；Linux/WSL2 上为 systemd 用户单元）  
- **健康检查** 与 **技能（skills）** 选择  

此外，若检测到所配置模型未知或缺少认证信息，向导也会发出警告。

### 我是否必须订阅 Claude 或 OpenAI 才能运行 OpenClaw？

不需要。您可以使用 **API 密钥**（Anthropic/OpenAI/其他提供商）或 **纯本地模型** 运行 OpenClaw，确保您的数据始终保留在本地设备上。Claude Pro/Max 或 OpenAI Codex 等订阅服务仅为可选的身份验证方式。

若您选择 Anthropic 订阅认证，请自行判断是否采用：Anthropic 曾在过往限制过 Claude Code 以外场景的订阅使用。OpenAI Codex OAuth 明确支持 OpenClaw 等外部工具。

文档：[Anthropic](/providers/anthropic)、[OpenAI](/providers/openai)、[本地模型](/gateway/local-models)、[模型](/concepts/models)。

### 我能否在不提供 API 密钥的情况下使用 Claude Max 订阅？

可以。您可使用 **setup-token** 进行身份验证，而非 API 密钥。这是订阅用户的认证路径。

Claude Pro/Max 订阅 **不包含 API 密钥**，因此 setup-token 是订阅账户的技术实现路径。但最终决定权在您：Anthropic 曾在过往限制过 Claude Code 以外场景的订阅使用。若您追求最清晰、最安全的生产环境支持路径，建议使用 Anthropic API 密钥。

### Anthropic setup-token 认证机制是怎样的？

`claude setup-token` 通过 Claude Code CLI 生成一个 **token 字符串**（Web 控制台中不可用），您可在 **任意机器** 上运行该命令。在向导中选择 **Anthropic token（粘贴 setup-token）**，或使用 `openclaw models auth paste-token --provider anthropic` 粘贴该 token。该 token 将作为 **anthropic** 提供商的认证配置文件被存储，并像 API 密钥一样使用（不支持自动刷新）。更多详情：[OAuth](/concepts/oauth)。

### 我在哪里可以获取 Anthropic setup-token？

它 **不在** Anthropic 控制台中。setup-token 由 **Claude Code CLI** 在 **任意机器** 上生成：

```bash
claude setup-token
```

复制其打印出的 token，然后在向导中选择 **Anthropic token（粘贴 setup-token）**。若您希望在 Gateway 主机上运行该命令，请使用 `openclaw models auth setup-token --provider anthropic`。若您已在其他机器上运行了 `claude setup-token`，请在 Gateway 主机上使用 `openclaw models auth paste-token --provider anthropic` 粘贴该 token。参见 [Anthropic](/providers/anthropic)。

### 是否支持 Claude 订阅认证（Claude Pro 或 Max）？

支持 —— 通过 **setup-token**。OpenClaw 不再复用 Claude Code CLI 的 OAuth token；请使用 setup-token 或 Anthropic API 密钥。您可在任意位置生成该 token，并将其粘贴至 Gateway 主机。参见 [Anthropic](/providers/anthropic) 和 [OAuth](/concepts/oauth)。

重要提示：这是技术层面的兼容性，而非政策保证。Anthropic 曾在过往限制过 Claude Code 以外场景的订阅使用。您需自行判断是否采用，并核实 Anthropic 当前条款。对于生产环境或多人协作场景，Anthropic API 密钥认证是更安全、更受推荐的选择。

### 为何我从 Anthropic 收到了 HTTP 429 ratelimiterror？

这意味着您的 **Anthropic 配额/速率限制** 已在当前时间窗口内耗尽。如果您使用的是 **Claude 订阅**（setup-token），请等待窗口重置或升级您的计划。如果您使用的是 **Anthropic API 密钥**，请前往 Anthropic 控制台检查用量/账单，并根据需要提升限额。

如果提示信息明确为：
`Extra usage is required for long context requests`，则该请求正尝试使用 Anthropic 的 1M 上下文 Beta 版本（`context1m: true`）。此功能仅在您的凭据符合长上下文计费资格时可用（即采用 API 密钥计费，或启用了“额外用量”的订阅）。

提示：设置一个 **备用模型**，以便在某服务商遭遇限流时，OpenClaw 仍可继续响应。参见 [模型](/cli/models)、[OAuth](/concepts/oauth)，以及 [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context)。

### 是否支持 AWS Bedrock

支持——通过 pi-ai 提供的 **Amazon Bedrock（Converse）** 服务，需 **手动配置**。您必须在网关主机上提供 AWS 凭据和区域，并在模型配置中添加一条 Bedrock 提供商条目。详见 [Amazon Bedrock](/providers/bedrock) 和 [模型提供商](/providers/models)。若您更倾向受管密钥流程，也可在 Bedrock 前部署一个兼容 OpenAI 的代理，这仍是有效方案。

### Codex 认证如何工作

OpenClaw 通过 OAuth（ChatGPT 登录）支持 **OpenAI Code（Codex）**。向导可运行 OAuth 流程，并在适当时将默认模型设为 `openai-codex/gpt-5.4`。参见 [模型提供商](/concepts/model-providers) 和 [向导](/start/wizard)。

### 是否支持 OpenAI 订阅认证的 Codex OAuth

支持。OpenClaw 完全支持 **OpenAI Code（Codex）订阅 OAuth**。OpenAI 明确允许在 OpenClaw 等外部工具/工作流中使用订阅 OAuth。入门向导可为您自动运行 OAuth 流程。

参见 [OAuth](/concepts/oauth)、[模型提供商](/concepts/model-providers) 和 [向导](/start/wizard)。

### 如何设置 Gemini CLI 的 OAuth

Gemini CLI 使用 **插件式认证流程**，而非在 `openclaw.json` 中配置 client id 或 secret。

步骤如下：

1. 启用插件：`openclaw plugins enable google-gemini-cli-auth`  
2. 登录：`openclaw models auth login --provider google-gemini-cli --set-default`

OAuth 令牌将存储在网关主机上的认证配置文件中。详情参见：[模型提供商](/concepts/model-providers)。

### 本地模型是否适合日常闲聊

通常不适合。OpenClaw 需要大上下文容量与强安全性；小型显卡会截断上下文并导致信息泄露。若必须使用，请在本地运行您所能承载的 **最大规格** MiniMax M2.5 构建版（例如通过 LM Studio），并参阅 [/gateway/local-models](/gateway/local-models)。更小或量化后的模型会增加提示注入风险——详见 [安全](/gateway/security)。

### 如何确保托管模型流量保留在特定区域内

请选择区域绑定的端点。OpenRouter 为 MiniMax、Kimi 和 GLM 提供了美国托管选项；选择美国托管变体即可确保数据驻留于该区域内。您仍可通过使用 `models.mode: "merge"` 将 Anthropic/OpenAI 列入配置，从而在保障所选区域化提供商的前提下保留备用选项。

### 我是否必须购买 Mac mini 才能安装此软件

不必。OpenClaw 支持 macOS 或 Linux（Windows 可通过 WSL2 运行）。Mac mini 是可选设备——部分用户购买它作为常开主机，但小型 VPS、家用服务器或树莓派级别设备同样适用。

您仅在需要 **macOS 专属工具** 时才需配备 Mac。对于 iMessage，请使用 [BlueBubbles](/channels/bluebubbles)（推荐）——BlueBubbles 服务端可在任意 Mac 上运行，而网关则可部署于 Linux 或其他平台。若您还需其他 macOS 专属工具，可将网关部署于 Mac，或配对一台 macOS 节点。

文档参考：[BlueBubbles](/channels/bluebubbles)、[节点](/nodes)、[Mac 远程模式](/platforms/mac/remote)。

### 我是否必须使用 Mac mini 才能支持 iMessage

您只需一台 **已登录信息（Messages）应用的 macOS 设备**。它 **不一定是 Mac mini** ——任何 Mac 均可满足要求。**请使用 [BlueBubbles](/channels/bluebubbles)**（推荐）来支持 iMessage——BlueBubbles 服务端运行于 macOS，而网关可运行于 Linux 或其他平台。

常见部署方式：

- 在 Linux/VPS 上运行网关，在任意已登录信息应用的 Mac 上运行 BlueBubbles 服务端。  
- 若追求最简单的单机部署，可将全部组件运行于同一台 Mac 上。

文档参考：[BlueBubbles](/channels/bluebubbles)、[节点](/nodes)、[Mac 远程模式](/platforms/mac/remote)。

### 若我购买 Mac mini 运行 OpenClaw，能否将其连接至我的 MacBook Pro

可以。**Mac mini 可运行网关**，而您的 MacBook Pro 可作为 **节点**（伴生设备）接入。节点本身不运行网关，而是提供屏幕/摄像头/画布等额外能力，以及该设备上的 `system.run`。

常见模式：

- 网关部署于 Mac mini（保持常开）。  
- MacBook Pro 运行 macOS 应用或节点宿主程序，并与网关配对。  
- 使用 `openclaw nodes status` / `openclaw nodes list` 查看其状态。

文档参考：[节点](/nodes)、[节点 CLI](/cli/nodes)。

### 我能否使用 Bun

**不推荐使用 Bun**。我们观察到运行时存在 Bug，尤其在 WhatsApp 和 Telegram 场景下。请使用 **Node** 以保障网关稳定运行。

若您仍希望实验性地使用 Bun，请仅在非生产环境的网关上尝试，且避免启用 WhatsApp/Telegram。

### Telegram 的 `allowFrom` 字段应填写什么

`channels.telegram.allowFrom` 是 **人类发送者的 Telegram 用户 ID**（纯数字），并非机器人用户名。

入门向导接受 `@username` 形式的输入并自动解析为数字 ID，但 OpenClaw 的授权机制仅识别数字 ID。

更安全的方式（无需第三方机器人）：

- 向您的机器人发起私聊（DM），然后运行 `openclaw logs --follow` 并读取 `from.id`。

官方 Bot API 方式：

- 向您的机器人发起私聊（DM），然后调用 `https://api.telegram.org/bot<bot_token>/getUpdates` 并读取 `message.from.id`。

第三方方式（隐私性较低）：

- 向 `@userinfobot` 或 `@getidsbot` 发起私聊（DM）。

参见 [/channels/telegram](/channels/telegram#access-control-dms--groups)。

### 多人能否共用一个 WhatsApp 号码，各自运行不同的 OpenClaw 实例

可以，通过 **多智能体路由（multi-agent routing）** 实现。将每位发送者的 WhatsApp **私聊（DM）**（对端 `kind: "direct"`，发送者 E.164 号码如 `+15551234567`）分别绑定至不同的 `agentId`，使每人拥有独立的工作区与会话存储。回复仍统一来自 **同一 WhatsApp 账户**，而私聊访问控制（`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`）则按 WhatsApp 账户全局生效。参见 [多智能体路由](/concepts/multi-agent) 和 [WhatsApp](/channels/whatsapp)。

### 我能否同时运行一个快速聊天智能体与一个用于编程的 Opus 智能体

可以。使用多智能体路由：为每个智能体指定各自的默认模型，再将入站路由（提供商账户或特定对端）分别绑定至各智能体。示例配置见 [多智能体路由](/concepts/multi-agent)。另请参阅 [模型](/concepts/models) 和 [配置](/gateway/configuration)。

### Homebrew 是否支持 Linux

支持。Homebrew 支持 Linux（即 Linuxbrew）。快速安装方式如下：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
brew install <formula>
```

若您通过 systemd 运行 OpenClaw，请确保服务的 PATH 包含 `/home/linuxbrew/.linuxbrew/bin`（或您的 brew 前缀），以便在非登录 Shell 中正确解析由 `brew` 安装的工具。  
最新版本构建还默认在 Linux systemd 服务中预置常见用户 bin 目录（例如 `~/.local/bin`、`~/.npm-global/bin`、`~/.local/share/pnpm`、`~/.bun/bin`），并在设置时尊重 `PNPM_HOME`、`NPM_CONFIG_PREFIX`、`BUN_INSTALL`、`VOLTA_HOME`、`ASDF_DATA_DIR`、`NVM_DIR` 和 `FNM_DIR`。

### 可定制的 Git 安装与 npm 安装有何区别

- **可定制（Git）安装**：完整源码检出，可编辑，最适合贡献者。您需在本地构建，并可自行修补代码/文档。  
- **npm 安装**：全局 CLI 安装，无仓库，最适合“开箱即用”场景。更新通过 npm 发布标签获取。

文档参考：[入门指南](/start/getting-started)、[更新说明](/install/updating)。

### 我之后能否在 npm 与 git 安装之间切换

可以。安装另一种形式后，运行 Doctor 工具，使网关服务指向新的入口点。  
此操作 **不会删除您的数据** —— 仅更改 OpenClaw 的代码安装路径。您的状态（`~/.openclaw`）与工作区（`~/.openclaw/workspace`）均保持不变。

从 npm → git：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm build
openclaw doctor
openclaw gateway restart
```

从 git → npm：

```bash
npm install -g openclaw@latest
openclaw doctor
openclaw gateway restart
```

Doctor 会检测网关服务入口点不匹配，并提供重写服务配置以匹配当前安装的选项（自动化脚本中可使用 `--repair`）。  
备份建议：参见 [备份策略](/help/faq#whats-the-recommended-backup-strategy)。

### 我应在笔记本电脑还是 VPS 上运行网关

简短回答：**若追求 24/7 可靠性，请使用 VPS**；若追求最低门槛且可接受休眠/重启影响，则可在本地运行。

**笔记本电脑（本地网关）**

- **优点**：无需服务器费用，可直接访问本地文件，支持实时浏览器窗口。  
- **缺点**：休眠/网络中断将导致断连，系统更新/重启会中断服务，需保持唤醒状态。

**VPS / 云服务器**

- **优点**：持续在线、网络稳定、无笔记本休眠问题、更易长期维持运行。  
- **缺点**：通常为无头运行（依赖截图）、仅支持远程文件访问、更新需通过 SSH 执行。

**OpenClaw 特别说明**：WhatsApp、Telegram、Slack、Mattermost（插件版）及 Discord 均可在 VPS 上正常运行。唯一实质权衡在于 **无头浏览器** 与 **可见窗口** 之间的取舍。参见 [浏览器](/tools/browser)。

**推荐默认方案**：若您此前曾遭遇网关断连，建议选用 VPS；若您正积极使用 Mac，且需要本地文件访问或借助可见浏览器进行 UI 自动化，则本地运行非常理想。

### 在专用机器上运行 OpenClaw 是否重要

非强制要求，但 **为保障可靠性与隔离性，强烈推荐**。

- **专用主机（VPS / Mac mini / 树莓派）：** 始终在线，睡眠/重启中断更少，权限更干净，更易于持续运行。  
- **共享笔记本电脑/台式机：** 完全适用于测试和日常使用，但需注意设备进入睡眠状态或进行系统更新时会出现暂停。

如果您希望兼顾两者优势，可将网关（Gateway）部署在专用主机上，并将您的笔记本电脑配对为一个**节点（Node）**，用于本地屏幕、摄像头及执行类工具。参见 [Nodes](/nodes)。  
如需安全方面的指导，请阅读 [Security](/gateway/security)。

### 最低 VPS 配置要求及推荐操作系统是什么？

OpenClaw 轻量高效。对于基础网关 + 一个聊天频道的场景：

- **绝对最低配置：** 1 个 vCPU、1GB 内存、约 500MB 磁盘空间。  
- **推荐配置：** 1–2 个 vCPU、2GB 或更高内存（预留空间用于日志、媒体文件、多个频道等）。节点工具与浏览器自动化可能占用较多资源。

操作系统：请使用 **Ubuntu LTS**（或任何现代 Debian/Ubuntu 发行版）。Linux 安装路径在此类系统上经过最充分的测试。

文档：[Linux](/platforms/linux)，[VPS 托管](/vps)。

### 我能否在虚拟机中运行 OpenClaw？有何要求？

可以。请将虚拟机（VM）视同 VPS：它必须始终在线、可被访问，并具备足够内存以支撑网关及其启用的各频道。

基础建议如下：

- **绝对最低配置：** 1 个 vCPU、1GB 内存。  
- **推荐配置：** 若运行多个频道、浏览器自动化或媒体工具，建议 2GB 或更高内存。  
- **操作系统：** Ubuntu LTS 或其他现代 Debian/Ubuntu 发行版。

若您使用 Windows 系统，**WSL2 是最便捷的虚拟机式部署方式**，且工具兼容性最佳。参见 [Windows](/platforms/windows)，[VPS 托管](/vps)。  
若您在虚拟机中运行 macOS，请参阅 [macOS VM](/install/macos-vm)。

## 什么是 OpenClaw？

### 用一段话概括 OpenClaw

OpenClaw 是一款您可在自有设备上运行的个人 AI 助手。它可在您已使用的各类消息平台（WhatsApp、Telegram、Slack、Mattermost（插件）、Discord、Google Chat、Signal、iMessage、WebChat）中自动回复，并在支持的平台上提供语音交互与实时画布（Canvas）功能。**网关（Gateway）** 是始终在线的控制平面；而助手本身即为产品。

### OpenClaw 的核心价值主张是什么？

OpenClaw 并非“仅是 Claude 的封装层”。它是一个**以本地优先（local-first）为理念的控制平面**，让您能在**自己的硬件上**运行功能完备的助手，通过您日常使用的聊天应用即可访问，具备有状态会话、记忆能力与工具集成——无需将工作流控制权交予托管型 SaaS 服务。

亮点包括：

- **您的设备，您的数据：** 可将网关部署于任意位置（Mac、Linux、VPS），并将工作区与会话历史保留在本地。  
- **真实消息渠道，而非网页沙箱：** 支持 WhatsApp / Telegram / Slack / Discord / Signal / iMessage 等，以及在支持平台上的移动端语音与 Canvas 功能。  
- **模型无关（Model-agnostic）：** 可接入 Anthropic、OpenAI、MiniMax、OpenRouter 等多种模型，支持按智能体（agent）路由与故障转移。  
- **纯本地运行选项：** 可运行本地模型，从而实现**所有数据完全保留在您的设备上**。  
- **多智能体路由：** 每个频道、账号或任务均可分配独立智能体，各自拥有专属工作区与默认配置。  
- **开源且高度可定制：** 可自由审查、扩展并自托管，无厂商锁定风险。

文档：[Gateway](/gateway)，[Channels](/channels)，[Multi-agent](/concepts/multi-agent)，[Memory](/concepts/memory)。

### 我刚完成部署，接下来该做什么？

推荐的入门项目：

- 搭建一个网站（WordPress、Shopify 或简易静态站点）。  
- 原型化一款移动应用（梳理大纲、设计界面、规划 API）。  
- 整理文件与文件夹（清理冗余、规范命名、添加标签）。  
- 连接 Gmail 并自动化摘要生成或后续跟进提醒。

它能处理大型任务，但效果最佳的方式是将其拆分为若干阶段，并利用子智能体（sub-agent）并行执行。

### OpenClaw 日常使用的五大高频场景有哪些？

日常典型应用场景包括：

- **个人简报：** 汇总收件箱、日历及您关注的新闻内容。  
- **调研与草稿撰写：** 快速开展调研、生成摘要，并为邮件或文档撰写初稿。  
- **提醒与后续跟进：** 基于定时任务（cron）或心跳机制（heartbeat）触发提示与检查清单。  
- **浏览器自动化：** 自动填写表单、采集网页数据、重复执行网页操作。  
- **跨设备协同：** 从手机发起任务，由网关在服务器端执行，并将结果返回至聊天窗口。

### OpenClaw 能否协助 SaaS 公司开展潜在客户开发（lead gen）、广告文案与博客撰写？

适用于**调研、筛选与草稿撰写**。它可扫描网站、构建候选名单、汇总目标客户信息，并撰写外联邮件或广告文案初稿。

对于**实际外联或广告投放**，请务必保持人工审核环节。避免发送垃圾信息，遵守当地法律法规及平台政策，并在发送前审阅全部内容。最稳妥的模式是：由 OpenClaw 起草，您最终确认。

文档：[Security](/gateway/security)。

### 相较于 Claude Code，OpenClaw 在 Web 开发方面有何优势？

OpenClaw 是一款**个人助理与协调层**，而非 IDE 替代品。在代码仓库内进行快速直接编码时，请使用 Claude Code 或 Codex；当您需要持久化记忆、跨设备访问及工具编排能力时，则应选用 OpenClaw。

优势包括：

- **跨会话的持久化记忆与工作区**  
- **多平台访问能力**（WhatsApp、Telegram、TUI、WebChat）  
- **工具编排能力**（浏览器、文件、调度、钩子）  
- **始终在线的网关**（可部署于 VPS，随时随地交互）  
- **节点（Nodes）支持本地浏览器/屏幕/摄像头/执行环境**

案例展示：[https://openclaw.ai/showcase](https://openclaw.ai/showcase)

## 技能与自动化

### 如何自定义技能而不污染代码仓库？

请使用受管覆盖（managed overrides），而非直接修改仓库副本。将您的变更置于 `~/.openclaw/skills/<name>/SKILL.md`（或通过 `skills.load.extraDirs` 在 `~/.openclaw/openclaw.json` 中添加文件夹）。优先级顺序为 `<workspace>/skills` > `~/.openclaw/skills` > 内置版本，因此受管覆盖无需触碰 Git 即可生效。仅当变更具备上游价值时，才应提交至仓库并以 PR 形式发布。

### 我能否从自定义文件夹加载技能？

可以。可通过 `skills.load.extraDirs` 在 `~/.openclaw/openclaw.json` 中添加额外目录（最低优先级）。默认优先级顺序保持不变：`<workspace>/skills` → `~/.openclaw/skills` → 内置版本 → `skills.load.extraDirs`。`clawhub` 默认安装至 `./skills`，OpenClaw 将其视为 `<workspace>/skills`。

### 如何为不同任务指定不同模型？

当前支持的模式包括：

- **定时任务（Cron jobs）：** 各隔离任务可为其单独设置 `model` 覆盖项。  
- **子智能体（Sub-agents）：** 将任务路由至具有不同默认模型的独立智能体。  
- **按需切换（On-demand switch）：** 使用 `/model` 在任意时刻切换当前会话所用模型。

参见 [Cron jobs](/automation/cron-jobs)，[Multi-Agent Routing](/concepts/multi-agent)，[Slash commands](/tools/slash-commands)。

### 机器人在执行繁重任务时卡住，如何卸载负载？

请为耗时较长或需并行执行的任务使用**子智能体（sub-agents）**。子智能体在独立会话中运行，返回摘要结果，同时确保主聊天界面保持响应。

可向机器人发出指令：“为此任务启动一个子智能体”，或使用 `/subagents`。  
在聊天中输入 `/status`，可实时查看网关当前正在执行的操作（及其是否处于繁忙状态）。

Token 提示：长时间任务与子智能体均消耗 token。若成本敏感，可通过 `agents.defaults.subagents.model` 为子智能体指定更经济的模型。

文档：[Sub-agents](/tools/subagents)。

### 在 Discord 上，线程绑定的子智能体会话如何运作？

请使用线程绑定（thread bindings）。您可以将 Discord 线程绑定至某个子智能体或会话目标，使该线程内的后续消息始终保留在对应绑定会话中。

基本流程如下：

- 使用 `sessions_spawn` 启动，配合 `thread: true`（并可选地使用 `mode: "session"` 实现持久化后续交互）。  
- 或手动绑定：使用 `/focus <target>`。  
- 使用 `/agents` 查看当前绑定状态。  
- 使用 `/session idle <duration|off>` 与 `/session max-age <duration|off>` 控制自动失焦行为。  
- 使用 `/unfocus` 解除线程绑定。

必需配置项：

- 全局默认值：`session.threadBindings.enabled`、`session.threadBindings.idleHours`、`session.threadBindings.maxAgeHours`。  
- Discord 覆盖项：`channels.discord.threadBindings.enabled`、`channels.discord.threadBindings.idleHours`、`channels.discord.threadBindings.maxAgeHours`。  
- 启动时自动绑定：设置 `channels.discord.threadBindings.spawnSubagentSessions: true`。

文档：[Sub-agents](/tools/subagents)，[Discord](/channels/discord)，[Configuration Reference](/gateway/configuration-reference)，[Slash commands](/tools/slash-commands)。

### 定时任务（Cron）或提醒未触发，我该检查什么？

Cron 在网关进程内部运行。若网关未持续运行，定时任务将无法执行。

检查清单：

- 确认 Cron 已启用（`cron.enabled`），且 `OPENCLAW_SKIP_CRON` 未被设置。  
- 确保网关 24/7 持续运行（无睡眠/重启）。  
- 核对任务的时区设置（`--tz` 与宿主机时区是否一致）。

调试命令：

```bash
openclaw cron run <jobId> --force
openclaw cron runs --id <jobId> --limit 50
```

文档：[Cron jobs](/automation/cron-jobs)，[Cron vs Heartbeat](/automation/cron-vs-heartbeat)。

### 如何在 Linux 上安装技能？

请使用 **ClawHub**（CLI）或直接将技能文件放入您的工作区。macOS 的图形化技能界面在 Linux 上不可用。  
技能浏览地址：[https://clawhub.com](https://clawhub.com)。

安装 ClawHub CLI（任选一种包管理器）：

```bash
npm i -g clawhub
```

```bash
pnpm add -g clawhub
```

### OpenClaw 是否支持按计划或持续后台运行任务？

支持。请使用网关内置调度器：

- **Cron 任务**：适用于定时或周期性任务（重启后仍持续生效）。  
- **Heartbeat（心跳）**：用于“主会话”的周期性检查。  
- **隔离任务（Isolated jobs）**：适用于自主运行的智能体，可发布摘要或推送至聊天窗口。

文档：[Cron jobs](/automation/cron-jobs)，[Cron vs Heartbeat](/automation/cron-vs-heartbeat)，[Heartbeat](/gateway/heartbeat)。

### 我能否在 Linux 上运行仅限 Apple macOS 的技能？

不能直接运行。macOS 技能受 `metadata.openclaw.os` 及所需二进制文件限制，且仅当技能在**网关主机**上满足启用条件时，才会出现在系统提示词中。在 Linux 上，仅限 `darwin` 的技能（例如 `apple-notes`、`apple-reminders`、`things-mac`）将不会加载，除非您主动覆盖该限制条件。

您有三种受支持的模式：

**选项 A — 在 Mac 上运行网关（最简单）**  
在 macOS 二进制文件所在的位置运行网关，然后从 Linux 以[远程模式](#how-do-i-run-openclaw-in-remote-mode-client-connects-to-a-gateway-elsewhere)或通过 Tailscale 连接。技能可正常加载，因为网关主机为 macOS。

**选项 B — 使用 macOS 节点（无需 SSH）**  
在 Linux 上运行网关，配对一个 macOS 节点（菜单栏应用），并在 Mac 上将 **节点运行命令（Node Run Commands）** 设为“始终询问”或“始终允许”。当所需二进制文件存在于该节点时，OpenClaw 可将仅限 macOS 的技能视为可用。代理会通过 `nodes` 工具运行这些技能。若您选择“始终询问”，在弹出提示中批准“始终允许”，即可将该命令加入白名单。

**选项 C — 通过 SSH 代理 macOS 二进制文件（高级）**  
保持网关运行在 Linux 上，但使所需的 CLI 二进制文件解析为在 Mac 上运行的 SSH 封装脚本。随后覆盖技能配置，允许其在 Linux 上运行，从而维持其可用性。

1. 为二进制文件创建 SSH 封装脚本（示例：针对 Apple Notes 的 `memo`）：

   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
   ```

2. 将该封装脚本置于 Linux 主机上的 `PATH`（例如 `~/bin/memo`）。
3. 覆盖技能元数据（工作区或 `~/.openclaw/skills`），以允许 Linux：

   ```markdown
   ---
   name: apple-notes
   description: Manage Apple Notes via the memo CLI on macOS.
   metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
   ---
   ```

4. 启动新会话，以便技能快照刷新。

### 您是否已有 Notion 或 HeyGen 集成？

目前尚未内置支持。

可选方案：

- **自定义技能 / 插件：** 最适合稳定调用 API（Notion/HeyGen 均提供公开 API）。
- **浏览器自动化：** 无需编码即可实现，但速度较慢且更易出错。

若需为每位客户保持上下文（如代理机构工作流），一种简洁模式是：

- 为每位客户创建一个 Notion 页面（含上下文 + 偏好设置 + 当前工作内容）。
- 请代理在会话开始时获取该页面。

若您希望获得原生集成，请提交功能请求，或自行构建一个面向上述 API 的技能。

安装技能：

```bash
clawhub install <skill-slug>
clawhub update --all
```

ClawHub 安装至当前目录下的 `./skills`（若未配置，则回退至您设定的 OpenClaw 工作区）；OpenClaw 在下次会话中将该路径视为 `<workspace>/skills`。若需在多个代理间共享技能，请将其放置于 `~/.openclaw/skills/<name>/SKILL.md`。部分技能依赖通过 Homebrew 安装的二进制文件；在 Linux 上则对应 Linuxbrew（参见上方 Homebrew Linux 常见问题解答条目）。详见 [技能](/tools/skills) 和 [ClawHub](/tools/clawhub)。

### 如何安装 Chrome 扩展以接管浏览器

使用内置安装器，然后在 Chrome 中加载解包的扩展：

```bash
openclaw browser extension install
openclaw browser extension path
```

接着依次进入 Chrome → `chrome://extensions` → 启用“开发者模式” → 点击“加载已解压的扩展程序” → 选择该文件夹。

完整指南（含远程网关与安全注意事项）：[Chrome 扩展](/tools/chrome-extension)

若网关与 Chrome 运行在同一台机器上（默认配置），通常 **无需额外操作**。  
若网关运行于其他位置，请在浏览器所在机器上运行一个节点主机，以便网关可代理浏览器操作。  
您仍需点击您希望控制的标签页上的扩展按钮（它不会自动附加）。

## 沙箱与内存

### 是否有专门的沙箱文档？

有。请参阅 [沙箱](/gateway/sandboxing)。如需 Docker 特定配置（完整网关容器化或沙箱镜像），请参阅 [Docker](/install/docker)。

### Docker 感觉功能受限，如何启用全部特性？

默认镜像以安全性为首要考量，以 `node` 用户身份运行，因此不包含系统软件包、Homebrew 或捆绑的浏览器。如需更完整的配置：

- 使用 `OPENCLAW_HOME_VOLUME` 持久化 `/home/node`，以确保缓存得以保留。
- 通过 `OPENCLAW_DOCKER_APT_PACKAGES` 将系统依赖项构建进镜像。
- 使用内置 CLI 安装 Playwright 浏览器：
  `node /app/node_modules/playwright-core/cli.js install chromium`
- 设置 `PLAYWRIGHT_BROWSERS_PATH` 并确保该路径被持久化。

相关文档：[Docker](/install/docker)，[浏览器](/tools/browser)。

**能否在单个代理下，让私聊（DM）保持私密，而群组对话公开且受沙箱保护？**

可以——前提是您的私密通信仅为 **私聊（DMs）**，而公开通信仅为 **群组（groups）**。

使用 `agents.defaults.sandbox.mode: "non-main"`，使群组/频道会话（非主密钥会话）在 Docker 中运行，而主私聊会话保留在宿主机上。随后，通过 `tools.sandbox.tools` 限制沙箱会话中可用的工具。

配置流程与示例配置：[群组：私密 DM + 公开群组（单代理）](/channels/groups#pattern-personal-dms-public-groups-single-agent)

关键配置参考：[网关配置](/gateway/configuration#agentsdefaultssandbox)

### 如何将宿主机文件夹挂载进沙箱？

将 `agents.defaults.sandbox.docker.binds` 设为 `["host:path:mode"]`（例如 `"/home/user/src:/src:ro"`）。全局挂载与每代理挂载会合并；当 `scope: "shared"` 时，每代理挂载将被忽略。对于敏感内容，请使用 `:ro`，并牢记挂载会绕过沙箱的文件系统隔离机制。示例与安全说明详见 [沙箱](/gateway/sandboxing#custom-bind-mounts) 以及 [沙箱 vs 工具策略 vs 提权](/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check)。

### 内存机制是如何工作的？

OpenClaw 的内存即代理工作区中的 Markdown 文件：

- 每日笔记存于 `memory/YYYY-MM-DD.md`  
- 经整理的长期笔记存于 `MEMORY.md`（仅限主会话/私密会话）

OpenClaw 还会执行一次**静默预压缩内存刷新（silent pre-compaction memory flush）**，提醒模型在自动压缩前将重要信息写入持久化笔记。此操作仅在工作区可写时运行（只读沙箱会跳过）。详见 [内存](/concepts/memory)。

### 内存总在遗忘内容，如何让它“记住”？

请向机器人明确指示：**将该事实写入内存**。长期笔记应存入 `MEMORY.md`，短期上下文则放入 `memory/YYYY-MM-DD.md`。

该领域仍在持续优化中。主动提醒模型存储记忆会有帮助，它会知道如何处理。若持续遗忘，请确认网关每次运行均使用同一工作区。

相关文档：[内存](/concepts/memory)，[代理工作区](/concepts/agent-workspace)。

### 语义内存搜索是否需要 OpenAI API 密钥？

仅当您使用 **OpenAI 嵌入模型（embeddings）** 时才需要。Codex OAuth 支持 chat/completions，但 **不授予嵌入访问权限**，因此 **使用 Codex（OAuth 或 Codex CLI 登录）登录对此无帮助**。OpenAI 嵌入仍需真实 API 密钥（`OPENAI_API_KEY` 或 `models.providers.openai.apiKey`）。

若您未显式指定提供方，OpenClaw 将在能解析到 API 密钥时（通过认证配置文件、`models.providers.*.apiKey` 或环境变量）自动选择提供方。优先级顺序为：若可解析 OpenAI 密钥，则首选 OpenAI；否则尝试 Gemini；再之后是 Voyage、Mistral。若无可使用的远程密钥，内存搜索将保持禁用状态，直至您完成配置。若您已配置并存在本地模型路径，OpenClaw 将优先使用 `local`。Ollama 在您显式设置 `memorySearch.provider = "ollama"` 时受支持。

若您倾向完全本地化，请设置 `memorySearch.provider = "local"`（并可选设置 `memorySearch.fallback = "none"`）。若您希望使用 Gemini 嵌入，请设置 `memorySearch.provider = "gemini"` 并提供 `GEMINI_API_KEY`（或 `memorySearch.remote.apiKey`）。我们支持 **OpenAI、Gemini、Voyage、Mistral、Ollama 或本地** 嵌入模型——详细配置方法请参阅 [内存](/concepts/memory)。

### 内存是否永久保存？有何限制？

内存文件保存在磁盘上，除非您手动删除，否则将持续存在。限制因素是您的存储空间，而非模型本身。但 **会话上下文** 仍受限于模型的上下文窗口长度，因此长对话可能被压缩或截断。这正是内存搜索存在的意义——它仅将相关部分重新拉回上下文中。

相关文档：[内存](/concepts/memory)，[上下文](/concepts/context)。

## 数据在磁盘上的存放位置

### OpenClaw 使用的所有数据是否都保存在本地？

否——**OpenClaw 的状态是本地的**，但 **外部服务仍能看到您发送给它们的内容**。

- **默认本地：** 会话、内存文件、配置及工作区均保存在网关主机上（`~/.openclaw` + 您的工作区目录）。
- **必需远程：** 发送给模型提供商（Anthropic/OpenAI 等）的消息将送达其 API；聊天平台（WhatsApp/Telegram/Slack 等）也将消息数据存储在其服务器上。
- **您掌控足迹范围：** 使用本地模型可使提示词保留在您的设备上，但渠道通信流量仍需经由对应渠道的服务器。

相关文档：[代理工作区](/concepts/agent-workspace)，[内存](/concepts/memory)。

### OpenClaw 将其数据存放在何处？

所有数据均位于 `$OPENCLAW_STATE_DIR` 下（默认为 `~/.openclaw`）：

| 路径                                                            | 用途                                                            |
| --------------------------------------------------------------- | ------------------------------------------------------------------ |
| `$OPENCLAW_STATE_DIR/openclaw.json`                             | 主配置（JSON5）                                                |
| `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | 遗留 OAuth 导入（首次使用时复制到认证配置文件中）       |
| `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | 认证配置文件（OAuth、API 密钥，以及可选的 `keyRef`/`tokenRef`）  |
| `$OPENCLAW_STATE_DIR/secrets.json`                              | 可选的基于文件的密钥有效载荷，供 `file` SecretRef 提供者使用 |
| `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | 遗留兼容性文件（已清除静态 `api_key` 条目）      |
| `$OPENCLAW_STATE_DIR/credentials/`                              | 提供者状态（例如：`whatsapp/<accountId>/creds.json`）            |
| `$OPENCLAW_STATE_DIR/agents/`                                   | 每个代理的状态（agentDir + 会话）                              |
| `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | 对话历史与状态（按代理划分）                           |
| `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | 会话元数据（按代理划分）                                       |

遗留单代理路径：`~/.openclaw/agent/*`（由 `openclaw doctor` 迁移）。

您的 **工作区**（AGENTS.md、记忆文件、技能等）是独立的，通过 `agents.defaults.workspace`（默认值：`~/.openclaw/workspace`）进行配置。

### AGENTS.md、SOUL.md、USER.md、MEMORY.md 应该放在哪里

这些文件位于 **代理工作区** 中，而非 `~/.openclaw`。

- **工作区（每个代理）**：`AGENTS.md`、`SOUL.md`、`IDENTITY.md`、`USER.md`、  
  `MEMORY.md`（或 `memory.md`）、`memory/YYYY-MM-DD.md`，以及可选的 `HEARTBEAT.md`。  
- **状态目录（`~/.openclaw`）**：配置、凭据、认证配置文件、会话、日志，  
  以及共享技能（`~/.openclaw/skills`）。

默认工作区为 `~/.openclaw/workspace`，可通过以下方式配置：

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

如果机器人在重启后“遗忘”，请确认网关每次启动时均使用相同的工作区（并注意：远程模式使用的是 **网关主机** 的工作区，而非您本地笔记本电脑的工作区）。

提示：如果您希望行为或偏好具有持久性，请让机器人将相关内容 **写入 AGENTS.md 或 MEMORY.md**，而非依赖聊天记录。

参见 [代理工作区](/concepts/agent-workspace) 和 [记忆](/concepts/memory)。

### 推荐的备份策略是什么

将您的 **代理工作区** 放入一个 **私有** Git 仓库，并在某个私有位置（例如 GitHub 私有仓库）进行备份。这可以保存记忆 + AGENTS/SOUL/USER 文件，并允许您日后恢复助手的“心智”。

**切勿** 提交 `~/.openclaw` 下的任何内容（凭据、会话、令牌或加密密钥有效载荷）。如需完整恢复，请分别备份工作区和状态目录（参见上方迁移问题）。

文档：[代理工作区](/concepts/agent-workspace)。

### 如何完全卸载 OpenClaw

请参阅专用指南：[卸载](/install/uninstall)。

### 代理能否在工作区之外运行

可以。工作区是 **默认当前工作目录（cwd）** 和记忆锚点，并非硬性沙箱。相对路径在工作区内解析，但绝对路径可访问主机其他位置（除非启用了沙箱）。如需隔离，请使用  
[`agents.defaults.sandbox`](/gateway/sandboxing) 或按代理设置沙箱。如需将某个代码仓库设为默认工作目录，请将该代理的  
`workspace` 指向仓库根目录。OpenClaw 仓库仅为源代码；请将工作区与其分离，除非您明确希望代理在其中运行。

示例（将仓库设为默认 cwd）：

```json5
{
  agents: {
    defaults: {
      workspace: "~/Projects/my-repo",
    },
  },
}
```

### 我处于远程模式，会话存储在哪里

会话状态由 **网关主机** 拥有。若您处于远程模式，则您关心的会话存储位于远程机器上，而非您的本地笔记本电脑。参见 [会话管理](/concepts/session)。

## 配置基础

### 配置采用什么格式？位于何处？

OpenClaw 从 `$OPENCLAW_CONFIG_PATH`（默认：`~/.openclaw/openclaw.json`）读取一个可选的 **JSON5** 配置：

```
$OPENCLAW_CONFIG_PATH
```

若该文件缺失，则使用较安全的默认值（包括默认工作区 `~/.openclaw/workspace`）。

### 我设置了 `gateway.bind` 为 `lan` 或 `tailnet`，但现在没有任何监听，UI 显示“未授权”

非回环地址绑定 **需要身份验证**。请配置 `gateway.auth.mode` + `gateway.auth.token`（或使用 `OPENCLAW_GATEWAY_TOKEN`）。

```json5
{
  gateway: {
    bind: "lan",
    auth: {
      mode: "token",
      token: "replace-me",
    },
  },
}
```

注意事项：

- 单独启用 `gateway.remote.token` / `.password` **不会** 启用本地网关身份验证。  
- 本地调用路径可在 `gateway.auth.*` 未设置时，使用 `gateway.remote.*` 作为备选方案。  
- 控制 UI 通过 `connect.params.auth.token`（存储于应用/UI 设置中）进行身份验证。请避免将令牌放入 URL 中。

### 为什么现在 localhost 也需要令牌

OpenClaw 默认强制执行令牌身份验证，包括回环地址。若未配置令牌，网关启动时将自动生成一个并保存至 `gateway.auth.token`，因此 **本地 WebSocket 客户端必须完成身份验证**。此举可阻止其他本地进程调用网关。

若您 **确实** 希望开放回环访问，请在配置中显式设置 `gateway.auth.mode: "none"`。Doctor 工具可随时为您生成令牌：`openclaw doctor --generate-gateway-token`。

### 修改配置后是否必须重启

网关会监控配置文件并支持热重载：

- `gateway.reload.mode: "hybrid"`（默认）：对安全变更热应用，关键变更则需重启  
- `hot`、`restart`、`off` 同样受支持  

### 如何禁用 CLI 中有趣的标语

在配置中设置 `cli.banner.taglineMode`：

```json5
{
  cli: {
    banner: {
      taglineMode: "off", // random | default | off
    },
  },
}
```

- `off`：隐藏标语文字，但保留横幅标题/版本行。  
- `default`：每次均使用 `All your chats, one OpenClaw.`。  
- `random`：轮换显示有趣/应季标语（默认行为）。  
- 若您希望完全不显示横幅，请设置环境变量 `OPENCLAW_HIDE_BANNER=1`。

### 如何启用网页搜索和网页抓取

`web_fetch` 无需 API 密钥即可运行。`web_search` 需要 Brave Search API 密钥。**推荐做法**：运行 `openclaw configure --section web` 将其存入  
`tools.web.search.apiKey`。环境变量替代方案：为网关进程设置 `BRAVE_API_KEY`。

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "BRAVE_API_KEY_HERE",
        maxResults: 5,
      },
      fetch: {
        enabled: true,
      },
    },
  },
}
```

注意事项：

- 若您使用白名单，请添加 `web_search`/`web_fetch` 或 `group:web`。  
- `web_fetch` 默认启用（除非被显式禁用）。  
- 守护进程从 `~/.openclaw/.env`（或服务环境）读取环境变量。

文档：[网页工具](/tools/web)。

### 如何跨设备运行一个中心化网关及专用工作节点

常见模式是 **一个网关**（例如树莓派）搭配 **节点** 和 **代理**：

- **网关（中心）**：负责信道（Signal/WhatsApp）、路由及会话管理。  
- **节点（设备）**：Mac/iOS/Android 作为外设连接，并暴露本地工具（`system.run`、`canvas`、`camera`）。  
- **代理（工作者）**：为特定角色（例如：“Hetzner 运维”、“个人数据”）提供独立的大脑/工作区。  
- **子代理**：当您需要并行处理时，由主代理启动后台任务。  
- **TUI**：连接至网关并切换代理/会话。

文档：[节点](/nodes)、[远程访问](/gateway/remote)、[多代理路由](/concepts/multi-agent)、[子代理](/tools/subagents)、[TUI](/web/tui)。

### OpenClaw 浏览器能否无头运行

可以。这是一个配置选项：

```json5
{
  browser: { headless: true },
  agents: {
    defaults: {
      sandbox: { browser: { headless: true } },
    },
  },
}
```

默认为 `false`（有界面）。无头模式更可能在某些网站触发反爬虫检测。参见 [浏览器](/tools/browser)。

无头模式使用 **相同的 Chromium 引擎**，适用于大多数自动化任务（表单填写、点击、网页抓取、登录）。主要区别如下：

- 无可见浏览器窗口（如需可视化效果，请使用截图功能）。  
- 某些网站对无头模式下的自动化更为严格（验证码、反爬虫机制）。  
  例如，X/Twitter 常常屏蔽无头会话。

### 如何使用 Brave 实现浏览器控制

将 `browser.executablePath` 设置为您本地的 Brave 二进制文件路径（或任意基于 Chromium 的浏览器），然后重启网关。  
完整配置示例请参见 [浏览器](/tools/browser#use-brave-or-another-chromium-based-browser)。

## 远程网关与节点

### 命令如何在 Telegram、网关与节点之间传播

Telegram 消息由 **网关** 处理。网关运行代理，仅当需要调用节点工具时，才通过 **网关 WebSocket** 调用节点：

Telegram → 网关 → 代理 → `node.*` → 节点 → 网关 → Telegram

节点无法看到入站提供方流量；它们仅接收节点 RPC 调用。

### 如果网关托管在远程服务器上，我的代理如何访问我的计算机

简短回答：**将您的计算机配对为一个节点**。网关运行在别处，但可通过网关 WebSocket 在您的本地机器上调用 `node.*` 工具（屏幕、摄像头、系统）。

典型部署步骤：

1. 在始终在线的主机（VPS/家庭服务器）上运行网关。  
2. 将网关主机与您的计算机置于同一 Tailnet 网络中。  
3. 确保网关 WebSocket 可达（Tailnet 绑定或 SSH 隧道）。  
4. 在本地 macOS 应用中打开，并以 **SSH 远程模式**（或直连 Tailnet）连接，以便注册为节点。  
5. 在网关上批准该节点：

无需单独的 TCP 桥接；节点通过网关 WebSocket 连接。

安全提醒：配对一台 macOS 节点设备，将允许 `system.run` 在该设备上执行。请仅配对您信任的设备，并查阅 [安全性](/gateway/security)。

文档：[节点](/nodes)、[网关协议](/gateway/protocol)、[macOS 远程模式](/platforms/mac/remote)、[安全性](/gateway/security)。

### Tailscale 已连接，但我收不到任何响应，接下来怎么办？

检查基础项：

- 网关正在运行：`openclaw gateway status`
- 网关健康状态：`openclaw status`
- 通道健康状态：`openclaw channels status`

然后验证认证与路由配置：

- 若使用 Tailscale Serve，请确保 `gateway.auth.allowTailscale` 设置正确。
- 若通过 SSH 隧道连接，请确认本地隧道已启动且指向正确的端口。
- 确认您的白名单（私聊或群组）中包含您的账户。

文档：[Tailscale](/gateway/tailscale)、[远程访问](/gateway/remote)、[通道](/channels)。

### 两个 OpenClaw 实例能否相互通信（本地 VPS 场景）？

可以。系统未内置“机器人到机器人”的桥接机制，但您可通过几种可靠方式手动搭建：

**最简单方式**：使用一个两个机器人都可访问的常规聊天通道（Telegram / Slack / WhatsApp）。让 Bot A 向 Bot B 发送消息，Bot B 再按常规方式回复。

**CLI 桥接（通用）**：运行一个脚本，调用另一个网关的 `openclaw agent --message ... --deliver` 接口，目标为另一个机器人监听的聊天通道。若其中一个机器人部署在远程 VPS 上，可通过 SSH/Tailscale 将您的 CLI 指向该远程网关（参见 [远程访问](/gateway/remote)）。

示例模式（在能访问目标网关的机器上运行）：

```bash
openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
```

提示：添加防护机制，防止两个机器人陷入无限循环（例如仅响应 @ 提及、限制通道白名单，或设定“不回复机器人消息”的规则）。

文档：[远程访问](/gateway/remote)、[代理 CLI](/cli/agent)、[代理发送工具](/tools/agent-send)。

### 多个代理是否需要各自独立的 VPS？

不需要。一个网关可托管多个代理，每个代理拥有独立的工作区、模型默认值和路由配置。这是标准部署方式，远比为每个代理单独运行一台 VPS 更经济、更简洁。

仅当您需要**强隔离**（安全边界）或配置差异极大、完全不希望共享时，才应使用独立 VPS。其余情况下，请统一使用单个网关，并通过多个代理或子代理实现扩展。

### 相比从 VPS 通过 SSH 访问，为何要在个人笔记本上部署节点？

是的——节点是远程网关访问您笔记本的首选方式，其能力远超 Shell 访问。网关支持 macOS/Linux（Windows 通过 WSL2），资源占用极低（小型 VPS 或树莓派规格设备即可胜任；4 GB 内存已绰绰有余），因此常见部署方案是：一台常驻主机运行网关 + 笔记本作为节点。

- **无需开放入站 SSH**：节点主动向外连接至网关 WebSocket，并通过设备配对完成身份验证。
- **更安全的执行控制**：`system.run` 受限于该笔记本上的节点白名单/审批机制。
- **更丰富的设备工具**：节点除提供 `system.run` 外，还暴露 `canvas`、`camera` 和 `screen`。
- **本地浏览器自动化**：将网关保留在 VPS 上，但在本地运行 Chrome，并借助 Chrome 扩展 + 笔记本上的节点主机实现控制中继。

SSH 适合临时性的 Shell 访问，但节点更适合长期运行的代理工作流与设备自动化任务。

文档：[节点](/nodes)、[节点 CLI](/cli/nodes)、[Chrome 扩展](/tools/chrome-extension)。

### 我是否应在第二台笔记本上安装网关，还是仅添加一个节点？

若您仅需在第二台笔记本上使用**本地工具**（屏幕/摄像头/执行），则应将其添加为**节点**。这可维持单一网关架构，避免配置重复。当前本地节点工具仅支持 macOS，但我们计划将其扩展至其他操作系统。

仅当您需要**强隔离**或两个完全独立的机器人时，才应安装第二个网关。

文档：[节点](/nodes)、[节点 CLI](/cli/nodes)、[多个网关](/gateway/multiple-gateways)。

### 节点是否会运行网关服务？

不会。除非您有意运行隔离的配置文件（参见 [多个网关](/gateway/multiple-gateways)），否则每台主机上**仅应运行一个网关**。节点是外围设备，用于连接网关（如 iOS/Android 节点，或 macOS “节点模式”下的菜单栏应用）。对于无头节点主机及命令行控制，请参阅 [节点主机 CLI](/cli/node)。

对 `gateway`、`discovery` 和 `canvasHost` 的修改需执行**完整重启**。

### 是否存在通过 API RPC 应用配置的方式？

存在。`config.apply` 会在执行操作过程中完成配置校验、写入及网关重启。

### configapply 清空了我的配置，如何恢复并避免此类问题？

`config.apply` 会**完全替换整个配置**。若您发送的是部分对象，则其余所有配置项均将被移除。

恢复方法：

- 从备份中还原（Git 或已复制的 `~/.openclaw/openclaw.json`）。
- 若无备份，请重新运行 `openclaw doctor` 并重新配置通道与模型。
- 若此情况属意外发生，请提交 Bug 报告，并附上您最后已知的配置或任意可用备份。
- 本地编码代理通常可依据日志或历史记录重建一份可用配置。

规避方法：

- 对小范围修改，请使用 `openclaw config set`。
- 对交互式编辑，请使用 `openclaw configure`。

文档：[配置](/cli/config)、[配置命令](/cli/configure)、[诊断工具](/gateway/doctor)。

### 首次安装所需的最小合理配置是什么？

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

该配置设定了您的工作区，并限制了可触发机器人的人员范围。

### 如何在 VPS 上设置 Tailscale 并从 Mac 连接？

最小步骤如下：

1. **在 VPS 上安装并登录**

   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```

2. **在您的 Mac 上安装并登录**
   - 使用 Tailscale 应用程序并登录至同一 tailnet。
3. **启用 MagicDNS（推荐）**
   - 在 Tailscale 管理控制台中启用 MagicDNS，使 VPS 拥有稳定名称。
4. **使用 tailnet 主机名**
   - SSH：`ssh user@your-vps.tailnet-xxxx.ts.net`
   - 网关 WebSocket：`ws://your-vps.tailnet-xxxx.ts.net:18789`

若您希望在不使用 SSH 的前提下访问控制界面，请在 VPS 上启用 Tailscale Serve：

```bash
openclaw gateway --tailscale serve
```

此方式使网关仅绑定至回环地址，并通过 Tailscale 暴露 HTTPS。参见 [Tailscale](/gateway/tailscale)。

### 如何将 Mac 节点连接至远程网关的 Tailscale Serve？

Serve 暴露的是**网关控制界面 + WebSocket**。节点即通过该同一 WebSocket 终端连接。

推荐设置如下：

1. **确保 VPS 与 Mac 处于同一 tailnet 中**。
2. **在 macOS 应用中启用远程模式**（SSH 目标可设为 tailnet 主机名）。该应用将自动建立网关端口隧道，并以节点身份连接。
3. **在网关上批准该节点**：

   ```bash
   openclaw devices list
   openclaw devices approve <requestId>
   ```

文档：[网关协议](/gateway/protocol)、[发现机制](/gateway/discovery)、[macOS 远程模式](/platforms/mac/remote)。

## 环境变量与 .env 加载

### OpenClaw 如何加载环境变量？

OpenClaw 从父进程（Shell、launchd/systemd、CI 等）读取环境变量，并额外加载以下内容：

- 当前工作目录下的 `.env`
- 全局后备 `.env`（位于 `~/.openclaw/.env`，即 `$OPENCLAW_STATE_DIR/.env`）

任一 `.env` 文件均**不会覆盖**已存在的环境变量。

您也可在配置中内联定义环境变量（仅当进程环境未提供时生效）：

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
  },
}
```

详见 [/environment](/help/environment) 获取完整的优先级与来源说明。

### 我通过服务启动网关后，环境变量丢失了，该怎么办？

两种常见修复方式：

1. 将缺失的密钥放入 `~/.openclaw/.env`，确保即使服务未继承您的 Shell 环境也能加载。
2. 启用 Shell 导入（可选便捷功能）：

```json5
{
  env: {
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

该功能将运行您的登录 Shell，并仅导入缺失的预期密钥（绝不会覆盖已有变量）。对应环境变量为：
`OPENCLAW_LOAD_SHELL_ENV=1`、`OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`。

### 我设置了 COPILOTGITHUBTOKEN，但模型状态却显示“Shell env off”，为什么？

`openclaw models status` 表示**Shell 环境导入功能**是否启用。“Shell env: off” **并不意味着**您的环境变量缺失——它仅表示 OpenClaw 不会自动加载您的登录 Shell。

若网关以服务形式运行（launchd/systemd），则无法继承您的 Shell 环境。请通过以下任一方式修复：

1. 将令牌放入 `~/.openclaw/.env`：

   ```
   COPILOT_GITHUB_TOKEN=...
   ```

2. 或启用 Shell 导入（`env.shellEnv.enabled: true`）。
3. 或将其添加至配置的 `env` 区块（仅在进程环境未提供时生效）。

随后重启网关并重新检查：

```bash
openclaw models status
```

Copilot 令牌从 `COPILOT_GITHUB_TOKEN`（亦支持 `GH_TOKEN` / `GITHUB_TOKEN`）读取。参见 [/concepts/model-providers](/concepts/model-providers) 与 [/environment](/help/environment)。

## 会话与多聊天场景

### 如何开启一次全新对话？

单独发送 `/new` 或 `/reset` 即可。详见 [会话管理](/concepts/session)。

### 若我从未发送新消息，会话是否会自动重置？

会。会话将在 `session.idleMinutes`（默认为 **60**）分钟后过期。**下一条**消息将为此聊天键生成全新的会话 ID。此操作**不会删除**对话记录，仅启动新会话。

```json5
{
  session: {
    idleMinutes: 240,
  },
}
```

### 是否可将一组 OpenClaw 实例组织为“一位 CEO + 多位代理”的团队结构？

可以，通过**多代理路由**与**子代理**机制实现。您可以创建一个协调代理（CEO），以及若干拥有各自工作区与模型的执行代理（Workers）。

话虽如此，这最好被视为一项**有趣的实验**。它消耗大量 token，且通常不如使用一个具备多个独立会话的机器人高效。我们设想的典型模型是：你与一个机器人对话，该机器人为并行任务维护不同的会话。该机器人在需要时还可生成子代理（sub-agents）。

文档：[多代理路由](/concepts/multi-agent)，[子代理](/tools/subagents)，[代理 CLI](/cli/agents)。

### 为什么上下文会在任务中途被截断？如何防止？

会话上下文受限于模型的上下文窗口（context window）。长时间聊天、大型工具输出或大量文件都可能触发压缩（compaction）或截断（truncation）。

以下方法有助于缓解：

- 让机器人总结当前状态，并将其写入文件。
- 在执行长时间任务前使用 `/compact`，切换话题时使用 `/new`。
- 将重要上下文保留在工作区（workspace）中，并让机器人重新读取。
- 对于耗时或并行任务，使用子代理，以保持主聊天上下文更小。
- 若此问题频繁发生，请选用上下文窗口更大的模型。

### 如何完全重置 OpenClaw 但保留其已安装状态？

使用重置命令：

```bash
openclaw reset
```

非交互式完整重置：

```bash
openclaw reset --scope full --yes --non-interactive
```

然后重新运行入门向导（onboarding）：

```bash
openclaw onboard --install-daemon
```

注意事项：

- 入门向导在检测到已有配置时也会提供 **重置（Reset）** 选项。参见 [向导](/start/wizard)。
- 若您使用了配置文件（profiles）（即 `--profile` / `OPENCLAW_PROFILE`），请重置每个状态目录（state dir）；默认路径为 `~/.openclaw-<profile>`。
- 开发者专用重置：`openclaw gateway --dev --reset`（仅限开发环境；将清除开发配置 + 凭据 + 会话 + 工作区）。

### 我遇到“上下文过大”错误，该如何重置或压缩？

可使用以下任一方式：

- **压缩（Compact）**（保留对话历史，但对较早轮次进行摘要）：

  ```
  /compact
  ```

  或使用 `/compact <instructions>` 来引导摘要内容。

- **重置（Reset）**（为同一聊天密钥生成新的会话 ID）：

  ```
  /new
  /reset
  ```

若问题持续出现：

- 启用或调整 **会话剪枝（session pruning）**（`agents.defaults.contextPruning`），以裁剪旧的工具输出。
- 使用上下文窗口更大的模型。

文档：[压缩（Compaction）](/concepts/compaction)，[会话剪枝（Session pruning）](/concepts/session-pruning)，[会话管理（Session management）](/concepts/session)。

### 为何我看到 “LLM request rejected: messages.content.tool_use.input field required” 错误？

这是由提供商（provider）触发的校验错误：模型输出了一个 `tool_use` 块，但缺少必需的 `input` 字段。通常意味着会话历史已过期或损坏（常见于长对话线程后，或工具/模式 schema 发生变更之后）。

修复方法：使用 `/new`（独立消息）启动一个全新会话。

### 为何我每 30 分钟就收到一次心跳消息（heartbeat messages）？

心跳默认每 **30 分钟** 运行一次。您可调优或禁用它：

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "2h", // or "0m" to disable
      },
    },
  },
}
```

若 `HEARTBEAT.md` 文件存在但实质为空（仅含空行和类似 `# Heading` 的 Markdown 标题），OpenClaw 将跳过本次心跳运行以节省 API 调用。若该文件缺失，心跳仍会运行，由模型决定后续操作。

按代理（per-agent）覆盖设置使用 `agents.list[].heartbeat`。文档：[心跳（Heartbeat）](/gateway/heartbeat)。

### 我是否需要为 WhatsApp 群组添加一个机器人账号？

不需要。OpenClaw 运行在**您自己的账号**上，因此只要您本人在该群组中，OpenClaw 即可看到群组消息。默认情况下，群组回复功能被阻止，直到您明确允许特定发送者（`groupPolicy: "allowlist"`）。

若您希望**仅限您本人**可触发群组回复：

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
}
```

### 如何获取 WhatsApp 群组的 JID？

方法一（最快）：追踪日志并在此群组中发送一条测试消息：

```bash
openclaw logs --follow --json
```

查找以 `@g.us` 结尾的 `chatId`（或 `from`），例如：
`1234567890-1234567890@g.us`。

方法二（若已配置/已加入白名单）：从配置中列出群组：

```bash
openclaw directory groups list --channel whatsapp
```

文档：[WhatsApp](/channels/whatsapp)，[目录（Directory）](/cli/directory)，[日志（Logs）](/cli/logs)。

### 为何 OpenClaw 不在群组中回复？

两个常见原因：

- 启用了提及门控（mention gating，为默认设置）：您必须 @ 提及机器人（或匹配 `mentionPatterns`）。
- 您配置了 `channels.whatsapp.groups`，但未配置 `"*"`，且该群组未加入白名单。

参见 [群组（Groups）](/channels/groups) 和 [群组消息（Group messages）](/channels/group-messages)。

### 群组/线程是否与私聊（DMs）共享上下文？

默认情况下，直接聊天（DM）会合并至主会话。而群组/频道拥有各自独立的会话密钥；Telegram 主题（topics）和 Discord 线程（threads）则各自为独立会话。参见 [群组（Groups）](/channels/groups) 和 [群组消息（Group messages）](/channels/group-messages)。

### 我最多可创建多少个工作区（workspaces）和代理（agents）？

无硬性限制。数十个（甚至数百个）均可，但请注意：

- **磁盘空间增长**：会话与对话记录均存储于 `~/.openclaw/agents/<agentId>/sessions/` 目录下。
- **Token 成本**：代理越多，并发模型调用越多。
- **运维开销**：每个代理需单独管理认证配置文件（auth profiles）、工作区及通道路由（channel routing）。

建议：

- 每个代理仅保留一个 **活跃的** 工作区（`agents.defaults.workspace`）。
- 若磁盘空间增长明显，可清理旧会话（删除 JSONL 文件或其中的条目）。
- 使用 `openclaw doctor` 查找游离的工作区及配置文件不匹配问题。

### 我能否同时运行多个机器人或聊天（如 Slack）？应如何配置？

可以。使用 **多代理路由（Multi-Agent Routing）** 可运行多个相互隔离的代理，并依据通道（channel）、账号（account）或对端（peer）路由入站消息。Slack 已作为通道支持，并可绑定至特定代理。

浏览器访问功能强大，但并非“人类能做的，它都能做”——反爬机制、验证码（CAPTCHA）和多重身份验证（MFA）仍可能阻断自动化。为获得最可靠的浏览器控制能力，请在运行浏览器的机器上使用 Chrome 扩展中继（Chrome extension relay）（网关 Gateway 可部署于任意位置）。

最佳实践配置：

- 始终在线的网关主机（VPS / Mac mini）。
- 每种角色对应一个代理（通过 bindings 绑定）。
- 将 Slack 频道（channel(s)）绑定至这些代理。
- 在需要时，通过本地浏览器扩展中继（或节点 node）接入。

文档：[多代理路由（Multi-Agent Routing）](/concepts/multi-agent)，[Slack](/channels/slack)，[浏览器（Browser）](/tools/browser)，[Chrome 扩展（Chrome extension）](/tools/chrome-extension)，[节点（Nodes）](/nodes)。

## 模型：默认值、选择、别名、动态切换

### 默认模型是什么？

OpenClaw 的默认模型即您所设置的：

```
agents.defaults.model.primary
```

模型以 `provider/model` 格式引用（例如：`anthropic/claude-opus-4-6`）。若您省略提供商（provider），OpenClaw 当前会临时回退至 `anthropic`（作为弃用过渡方案）——但您仍应**显式指定** `provider/model`。

### 您推荐使用哪种模型？

**推荐默认值**：使用您所用提供商栈中最新一代、性能最强的模型。  
**对于启用工具或处理不可信输入的代理**：优先考虑模型能力，而非成本。  
**对于常规/低风险聊天场景**：使用更廉价的备用模型，并按代理角色进行路由。

MiniMax M2.5 拥有专属文档：[MiniMax](/providers/minimax) 和 [本地模型（Local models）](/gateway/local-models)。

经验法则：对高风险任务，使用您**负担得起的最佳模型**；对日常聊天或摘要等常规任务，则可选用更廉价的模型。您可按代理路由模型，并利用子代理并行化长任务（每个子代理均消耗 token）。参见 [模型（Models）](/concepts/models) 和 [子代理（Sub-agents）](/tools/subagents)。

强烈警告：较弱或过度量化（over-quantized）的模型更易遭受提示注入（prompt injection）攻击，并表现出不安全行为。参见 [安全性（Security）](/gateway/security)。

更多背景信息：[模型（Models）](/concepts/models)。

### 我能否使用自托管模型（如 llama.cpp、vLLM、Ollama）？

可以。若您的本地服务器暴露了兼容 OpenAI 的 API 接口，您即可为其配置一个自定义提供商（custom provider）。Ollama 已获原生支持，是最简易的接入路径。

安全提示：更小或高度量化的模型更易受提示注入攻击。我们强烈建议：**任何可调用工具的机器人，均应使用大模型**。若您仍需使用小模型，请务必启用沙箱（sandboxing）并严格限制可用工具清单（tool allowlists）。

文档：[Ollama](/providers/ollama)，[本地模型（Local models）](/gateway/local-models)，[模型提供商（Model providers）](/concepts/model-providers)，[安全性（Security）](/gateway/security)，[沙箱（Sandboxing）](/gateway/sandboxing)。

### 如何切换模型而不清空现有配置？

使用 **模型命令（model commands）**，或仅编辑配置中的 **model** 字段。避免整体替换配置。

安全选项包括：

- 在聊天中输入 `/model`（快捷，仅限当前会话）
- 运行 `openclaw models set ...`（仅更新模型配置）
- 运行 `openclaw configure --section model`（交互式）
- 编辑 `agents.defaults.model` 文件中的 `~/.openclaw/openclaw.json`

除非您有意替换整个配置，否则请勿使用 `config.apply` 并传入部分对象。若已意外覆盖配置，请从备份恢复，或重新运行 `openclaw doctor` 以自动修复。

文档：[模型（Models）](/concepts/models)，[配置（Configure）](/cli/configure)，[配置文件（Config）](/cli/config)，[诊断（Doctor）](/gateway/doctor)。

### OpenClaw、Flawd 和 Krill 分别使用哪些模型？

- 这些部署的具体模型可能不同，且随时间变化；不存在固定的提供商推荐。
- 请使用 `openclaw models status` 查看各网关当前运行时设置。
- 对于安全性敏感或启用了工具的代理，请使用您所能获得的最新一代、性能最强的模型。

### 如何在不重启的情况下动态切换模型？

使用 `/model` 命令作为一条独立消息：

```
/model sonnet
/model haiku
/model opus
/model gpt
/model gpt-mini
/model gemini
/model gemini-flash
```

您可通过以下任一命令列出可用模型：`/model`、`/model list` 或 `/model status`。

`/model`（及 `/model list`）将显示一个紧凑、带编号的选择器。通过编号选择：

```
/model 3
```

您还可为提供商强制指定特定的认证配置文件（auth profile）（按会话生效）：

```
/model opus@anthropic:default
/model opus@anthropic:work
```

提示：`/model status` 将显示当前激活的代理、正在使用的 `auth-profiles.json` 文件，以及下一个将尝试的认证配置文件。当可用时，它还会显示已配置的提供商端点（`baseUrl`）和 API 模式（`api`）。

**如何取消之前用 `profile` 命令设定的配置文件固定（unpin）？**  
重新运行 `/model`，**不加** `@profile` 后缀：

```
/model anthropic/claude-opus-4-6
```

如需恢复为默认设置，请从 `/model` 中选择（或发送 `/model <default provider/model>`）。
使用 `/model status` 确认当前激活的认证配置文件（auth profile）。

### 我能否日常任务使用 GPT 5.2，编程时使用 Codex 5.3

可以。将其中一个设为默认，并按需切换：

- **快速切换（每会话）：** 使用 `/model gpt-5.2` 处理日常任务，使用 `/model openai-codex/gpt-5.4` 启用 Codex OAuth 进行编码。
- **默认 + 切换：** 将 `agents.defaults.model.primary` 设为 `openai/gpt-5.2`，编码时再切换至 `openai-codex/gpt-5.4`（或反之）。
- **子智能体（Sub-agents）：** 将编码任务路由至采用不同默认模型的子智能体。

参见 [模型](/concepts/models) 和 [斜杠命令](/tools/slash-commands)。

### 为何我看到 “Model is not allowed”，随后无任何回复

若设置了 `agents.defaults.models`，它将成为 `/model` 及所有会话覆盖项的**白名单**。  
若所选模型不在该列表中，则返回：

```
Model "provider/model" is not allowed. Use /model to list available models.
```

该错误将**替代**正常回复直接返回。修复方法：将模型加入 `agents.defaults.models`、移除白名单，或从 `/model list` 中选择一个模型。

### 为何我看到未知模型名 minimaxMiniMaxM25

这表示**供应商未配置**（未找到 MiniMax 供应商配置或认证配置文件），因此无法解析该模型。此检测问题的修复已纳入 **2026.1.12** 版本（撰写本文时尚未发布）。

修复检查清单：

1. 升级至 **2026.1.12**（或从源码运行 `main`），然后重启网关。
2. 确保已配置 MiniMax（通过向导或 JSON），或确保环境变量 / 认证配置文件中存在 MiniMax API 密钥，以便注入该供应商。
3. 使用精确的模型 ID（区分大小写）：`minimax/MiniMax-M2.5` 或  
   `minimax/MiniMax-M2.5-highspeed`。
4. 运行：

   ```bash
   openclaw models list
   ```

   并从列表中选择（或在聊天中输入 `/model list`）。

参见 [MiniMax](/providers/minimax) 和 [模型](/concepts/models)。

### 我能否将 MiniMax 设为默认，而对复杂任务使用 OpenAI

可以。将 **MiniMax 设为默认**，并在需要时**按会话切换模型**。  
回退机制（fallback）用于处理**错误**，而非“高难度任务”，因此请使用 `/model` 或独立智能体。

**选项 A：按会话切换**

```json5
{
  env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.5" },
      models: {
        "minimax/MiniMax-M2.5": { alias: "minimax" },
        "openai/gpt-5.2": { alias: "gpt" },
      },
    },
  },
}
```

然后：

```
/model gpt
```

**选项 B：分离智能体**

- 智能体 A 默认：MiniMax  
- 智能体 B 默认：OpenAI  
- 按智能体路由，或使用 `/agent` 切换  

文档参考：[模型](/concepts/models)、[多智能体路由](/concepts/multi-agent)、[MiniMax](/providers/minimax)、[OpenAI](/providers/openai)。

### opus、sonnet、gpt 是否为内置快捷方式

是的。OpenClaw 自带若干默认简写（仅当对应模型存在于 `agents.defaults.models` 中时生效）：

- `opus` → `anthropic/claude-opus-4-6`  
- `sonnet` → `anthropic/claude-sonnet-4-5`  
- `gpt` → `openai/gpt-5.2`  
- `gpt-mini` → `openai/gpt-5-mini`  
- `gemini` → `google/gemini-3.1-pro-preview`  
- `gemini-flash` → `google/gemini-3-flash-preview`  

若您自定义了同名别名，则以您设定的值为准。

### 如何定义/覆盖模型快捷方式别名

别名来源于 `agents.defaults.models.<modelId>.alias`。示例：

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "anthropic/claude-sonnet-4-5": { alias: "sonnet" },
        "anthropic/claude-haiku-4-5": { alias: "haiku" },
      },
    },
  },
}
```

此后，`/model sonnet`（或未来支持的 `/<alias>`）将解析为该模型 ID。

### 如何添加 OpenRouter 或 Z.AI 等其他供应商的模型

OpenRouter（按 token 计费；支持大量模型）：

```json5
{
  agents: {
    defaults: {
      model: { primary: "openrouter/anthropic/claude-sonnet-4-5" },
      models: { "openrouter/anthropic/claude-sonnet-4-5": {} },
    },
  },
  env: { OPENROUTER_API_KEY: "sk-or-..." },
}
```

Z.AI（GLM 模型）：

```json5
{
  agents: {
    defaults: {
      model: { primary: "zai/glm-5" },
      models: { "zai/glm-5": {} },
    },
  },
  env: { ZAI_API_KEY: "..." },
}
```

若您引用了某供应商/模型，但缺少所需供应商密钥，则将收到运行时认证错误（例如：`No API key found for provider "zai"`）。

**新增智能体后提示 “No API key found for provider”**

这通常意味着**新智能体**的认证存储为空。认证信息按智能体隔离，存储于：

```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

修复方案：

- 运行 `openclaw agents add <id>`，并在向导中完成认证配置。  
- 或将主智能体 `agentDir` 中的 `auth-profiles.json` 复制到新智能体的 `agentDir` 中。

**切勿**在多个智能体间复用 `agentDir`；否则将引发认证/会话冲突。

## 模型故障转移与 “All models failed”

### 故障转移如何工作

故障转移分两个阶段进行：

1. 在同一供应商内轮换**认证配置文件（auth profile）**。  
2. 按 `agents.defaults.model.fallbacks` 中顺序，对下一模型执行**模型回退（model fallback）**。

失败的配置文件将启用冷却机制（指数退避），因此即使某供应商遭遇限流或临时故障，OpenClaw 仍可持续响应。

### 此错误含义是什么

```
No credentials found for profile "anthropic:default"
```

表示系统尝试使用认证配置文件 ID `anthropic:default`，但在预期的认证存储中未能找到其凭据。

### “No credentials found for profile anthropicdefault” 错误修复清单

- **确认认证配置文件所在路径（新路径 vs 旧路径）**  
  - 当前路径：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`  
  - 旧路径：`~/.openclaw/agent/*`（由 `openclaw doctor` 迁移）  
- **确认环境变量已被网关加载**  
  - 若在 shell 中设置了 `ANTHROPIC_API_KEY`，但通过 systemd/launchd 启动网关，则可能未继承该变量。请将其写入 `~/.openclaw/.env`，或启用 `env.shellEnv`。  
- **确保正在编辑正确的智能体**  
  - 多智能体部署下可能存在多个 `auth-profiles.json` 文件。  
- **验证模型/认证状态**  
  - 使用 `openclaw models status` 查看已配置模型及各供应商的认证状态。

**“No credentials found for profile anthropic” 错误修复清单**

这意味着当前运行被绑定至 Anthropic 认证配置文件，但网关在其认证存储中找不到该配置文件。

- **使用 setup-token**  
  - 运行 `claude setup-token`，然后使用 `openclaw models auth setup-token --provider anthropic` 粘贴该令牌。  
  - 若该令牌在其他机器上生成，请使用 `openclaw models auth paste-token --provider anthropic`。  
- **若希望改用 API 密钥**  
  - 将 `ANTHROPIC_API_KEY` 放入网关主机上的 `~/.openclaw/.env`。  
  - 清除任何强制指向缺失配置文件的已固定顺序：

    ```bash
    openclaw models auth order clear --provider anthropic
    ```

- **确认命令在网关主机上执行**  
  - 远程模式下，认证配置文件位于网关机器，而非您的笔记本电脑。

### 为何它还尝试了 Google Gemini 并失败

若您的模型配置中包含 Google Gemini 作为回退选项（或您切换到了 Gemini 简写），OpenClaw 将在模型回退过程中尝试它。若您尚未配置 Google 凭据，将看到 `No API key found for provider "google"`。

修复方法：提供 Google 认证凭据，或从 `agents.defaults.model.fallbacks` / 别名中移除/避免使用 Google 模型，防止回退路由至该处。

**LLM 请求被拒绝，提示 “signature required google antigravity”**

原因：会话历史中存在**无签名的思考块（thinking blocks）**（常源于中断/不完整流）。Google Antigravity 要求所有思考块必须带签名。

修复：OpenClaw 当前已为 Google Antigravity Claude 自动剥离无签名思考块。若问题仍存在，请启动一个**新会话**，或为该智能体设置 `/thinking off`。

## 认证配置文件（Auth profiles）：定义与管理方式

相关文档：[/concepts/oauth](/concepts/oauth)（OAuth 流程、令牌存储、多账户模式）

### 什么是认证配置文件（auth profile）

认证配置文件是一个命名的凭证记录（OAuth 或 API 密钥），与特定供应商绑定。配置文件存于：

```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

### 典型的配置文件 ID 是什么

OpenClaw 使用带供应商前缀的 ID，例如：

- `anthropic:default`（常见于无邮箱身份时）  
- `anthropic:<email>`（用于 OAuth 身份）  
- 您自定义的 ID（例如：`anthropic:work`）

### 我能否控制优先尝试哪个认证配置文件

可以。配置支持为配置文件添加可选元数据，以及为每个供应商指定排序（`auth.order.<provider>`）。该机制**不存储密钥**，仅将 ID 映射至供应商/模式，并设定轮换顺序。

若某配置文件处于短期**冷却（cooldown）** 状态（因限流/超时/认证失败），或长期**禁用（disabled）** 状态（因账单/额度不足），OpenClaw 可能暂时跳过它。可通过运行 `openclaw models status --json` 并检查 `auth.unusableProfiles` 来诊断。调优参数：`auth.cooldowns.billingBackoffHours*`。

您还可通过 CLI 为特定智能体设置**每智能体排序覆盖**（保存于该智能体的 `auth-profiles.json`）：

```bash
# Defaults to the configured default agent (omit --agent)
openclaw models auth order get --provider anthropic

# Lock rotation to a single profile (only try this one)
openclaw models auth order set --provider anthropic anthropic:default

# Or set an explicit order (fallback within provider)
openclaw models auth order set --provider anthropic anthropic:work anthropic:default

# Clear override (fall back to config auth.order / round-robin)
openclaw models auth order clear --provider anthropic
```

若需指定目标智能体：

```bash
openclaw models auth order set --provider anthropic --agent main anthropic:default
```

### OAuth 与 API 密钥的区别是什么

OpenClaw 同时支持以下两种方式：

- **OAuth**（通常在适用情况下采用订阅访问模式）。
- **API 密钥**（按 token 计费）。

向导明确支持 Anthropic 的 setup-token 和 OpenAI Codex 的 OAuth，并可为您存储 API 密钥。

## 网关：端口、“已在运行”提示及远程模式

### 网关使用哪个端口？

`gateway.port` 控制 WebSocket + HTTP 的单一多路复用端口（控制界面、钩子等）。

优先级顺序如下：

```
--port > OPENCLAW_GATEWAY_PORT > gateway.port > default 18789
```

### 为何 `openclaw gateway status` 显示 “Runtime running”，但 RPC 探测失败？

因为 “running” 是**进程管理器**（launchd/systemd/schtasks）的视角；而 RPC 探测是 CLI 实际连接网关 WebSocket 并调用 `status` 的过程。

请使用 `openclaw gateway status` 并信任以下几行输出：

- `Probe target:`（探测实际使用的 URL）
- `Listening:`（该端口上实际绑定的服务）
- `Last gateway error:`（进程存活但端口未监听时的常见根本原因）

### 为何 `openclaw gateway status` 显示 Config cli 和 Config service 不一致？

您正在编辑一个配置文件，而服务却在运行另一个配置文件（通常是 `--profile` / `OPENCLAW_STATE_DIR` 不匹配）。

修复方法：

```bash
openclaw gateway install --force
```

请从您希望服务使用的同一 `--profile` / 环境中执行该命令。

### “另一个网关实例已在监听” 是什么意思？

OpenClaw 在启动时立即绑定 WebSocket 监听器（默认为 `ws://127.0.0.1:18789`），以此实施运行时锁。若绑定失败并返回 `EADDRINUSE` 错误，则抛出 `GatewayLockError`，表明已有其他实例正在监听该端口。

修复方法：停止另一实例、释放端口，或使用 `openclaw gateway --port <port>` 运行。

### 如何以远程模式运行 OpenClaw（客户端连接至其他位置的网关）？

设置 `gateway.mode: "remote"` 并指向远程 WebSocket URL，可选地附带 token/密码：

```json5
{
  gateway: {
    mode: "remote",
    remote: {
      url: "ws://gateway.tailnet:18789",
      token: "your-token",
      password: "your-password",
    },
  },
}
```

注意事项：

- `openclaw gateway` 仅在 `gateway.mode` 为 `local`（或您传入覆盖标志）时启动。
- macOS 应用会监控配置文件，并在这些值变更时实时切换运行模式。

### 控制界面显示 “unauthorized” 或持续重连，该怎么办？

您的网关启用了身份验证（`gateway.auth.*`），但控制界面未发送匹配的 token/密码。

事实（源自代码）：

- 控制界面将 token 保留在当前浏览器标签页内存中；不再将网关 token 持久化至浏览器 localStorage。

修复方法：

- 最快方式：执行 `openclaw dashboard`（打印并复制仪表板 URL，尝试自动打开；若为无头环境则显示 SSH 提示）。
- 若尚未获取 token：运行 `openclaw doctor --generate-gateway-token`。
- 若为远程场景，请先建立隧道：执行 `ssh -N -L 18789:127.0.0.1:18789 user@host`，然后打开 `http://127.0.0.1:18789/`。
- 在网关主机上设置 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 在控制界面设置中粘贴相同的 token。
- 仍无法解决？运行 `openclaw status --all` 并参考 [故障排除](/gateway/troubleshooting)。有关身份验证详情，请参阅 [仪表板](/web/dashboard)。

### 我设置了 `gatewaybind tailnet`，但无法绑定，没有任何服务监听，为什么？

`tailnet` 绑定会从您的网络接口中选取一个 Tailscale IP（100.64.0.0/10）。若该机器未接入 Tailscale（或对应接口已关闭），则无可用地址用于绑定。

修复方法：

- 在该主机上启动 Tailscale（使其获得一个 100.x 地址），或  
- 切换至 `gateway.bind: "loopback"` / `"lan"`。

注意：`tailnet` 是显式指定；`auto` 优先使用回环地址；当您需要仅在 tailnet 上绑定时，请使用 `gateway.bind: "tailnet"`。

### 我能否在同一台主机上运行多个网关？

通常不建议——单个网关即可运行多个消息通道和智能体。仅在需要冗余（例如救援机器人）或严格隔离时才部署多个网关。

可以，但您必须确保以下各项相互隔离：

- `OPENCLAW_CONFIG_PATH`（每个实例的独立配置）
- `OPENCLAW_STATE_DIR`（每个实例的独立状态）
- `agents.defaults.workspace`（工作区隔离）
- `gateway.port`（端口唯一性）

快速搭建（推荐）：

- 每个实例使用 `openclaw --profile <name> …`（自动创建 `~/.openclaw-<name>`）。
- 在每个配置文件中设置唯一的 `gateway.port`（或手动运行时传入 `--port`）。
- 为每个配置文件安装专属服务：`openclaw --profile <name> gateway install`。

配置文件还会为服务名添加后缀（`ai.openclaw.<profile>`；旧版为 `com.openclaw.*`、`openclaw-gateway-<profile>.service`、`OpenClaw Gateway (<profile>)`）。
完整指南见：[多个网关](/gateway/multiple-gateways)。

### “invalid handshake code 1008” 是什么意思？

网关是一个**WebSocket 服务器**，它期望收到的第一条消息是 `connect` 帧。若收到其他内容，即以 **code 1008**（策略违规）关闭连接。

常见原因：

- 您在浏览器中打开了 **HTTP** URL（`http://...`），而非 WebSocket 客户端。
- 使用了错误的端口或路径。
- 代理或隧道剥离了身份验证头，或发送了非网关请求。

快速修复：

1. 使用 WebSocket URL：`ws://<host>:18789`（若启用 HTTPS，则为 `wss://...`）。
2. 不要在普通浏览器标签页中打开 WebSocket 端口。
3. 若启用了身份验证，请在 `connect` 帧中包含 token/密码。

若您使用 CLI 或 TUI，URL 格式应为：

```
openclaw tui --url ws://<host>:18789 --token <token>
```

协议细节详见：[网关协议](/gateway/protocol)。

## 日志与调试

### 日志存放在哪里？

文件日志（结构化格式）：

```
/tmp/openclaw/openclaw-YYYY-MM-DD.log
```

您可通过 `logging.file` 设置稳定路径。文件日志级别由 `logging.level` 控制；控制台详细程度由 `--verbose` 和 `logging.consoleLevel` 控制。

最快查看日志尾部：

```bash
openclaw logs --follow
```

服务/进程管理器日志（当网关通过 launchd/systemd 运行时）：

- macOS：`$OPENCLAW_STATE_DIR/logs/gateway.log` 和 `gateway.err.log`（默认为 `~/.openclaw/logs/...`；配置文件使用 `~/.openclaw-<profile>/logs/...`）
- Linux：`journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
- Windows：`schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

更多信息请参阅：[故障排除](/gateway/troubleshooting#log-locations)。

### 如何启动/停止/重启网关服务？

使用网关辅助命令：

```bash
openclaw gateway status
openclaw gateway restart
```

若您手动运行网关，`openclaw gateway --force` 可回收端口。详见 [网关](/gateway)。

### 我在 Windows 上关闭了终端，如何重启 OpenClaw？

Windows 有两种安装模式：

**1）WSL2（推荐）：** 网关运行于 Linux 内部。

打开 PowerShell，进入 WSL，然后重启：

```powershell
wsl
openclaw gateway status
openclaw gateway restart
```

若您尚未安装服务，请以前台模式启动：

```bash
openclaw gateway run
```

**2）原生 Windows（不推荐）：** 网关直接运行于 Windows。

打开 PowerShell 并运行：

```powershell
openclaw gateway status
openclaw gateway restart
```

若您手动运行（未安装服务），请使用：

```powershell
openclaw gateway run
```

文档参考：[Windows（WSL2）](/platforms/windows)，[网关服务操作手册](/gateway)。

### 网关已启动，但始终无响应，应检查什么？

首先进行快速健康检查：

```bash
openclaw status
openclaw models status
openclaw channels status
openclaw logs --follow
```

常见原因：

- **网关主机**上未加载模型身份验证信息（检查 `models status`）。
- 通道配对/白名单阻止了响应（检查通道配置及日志）。
- WebChat/仪表板已打开，但未提供正确 token。

若您处于远程环境，请确认隧道/Tailscale 连接正常，且网关 WebSocket 可达。

文档参考：[通道](/channels)，[故障排除](/gateway/troubleshooting)，[远程访问](/gateway/remote)。

### 显示“Disconnected from gateway, no reason”，该怎么办？

这通常意味着控制界面丢失了 WebSocket 连接。请检查：

1. 网关是否正在运行？`openclaw gateway status`
2. 网关是否健康？`openclaw status`
3. 控制界面是否拥有正确的 token？`openclaw dashboard`
4. 若为远程连接，隧道/Tailscale 链路是否畅通？

随后查看日志尾部：

```bash
openclaw logs --follow
```

文档参考：[仪表板](/web/dashboard)，[远程访问](/gateway/remote)，[故障排除](/gateway/troubleshooting)。

### Telegram `setMyCommands` 因网络错误失败，应检查什么？

首先查看日志与通道状态：

```bash
openclaw channels status
openclaw channels logs --channel telegram
```

若您位于 VPS 或代理之后，请确认出站 HTTPS 已放行且 DNS 正常工作。  
若网关为远程部署，请确保您正在网关主机上查看日志。

文档参考：[Telegram](/channels/telegram)，[通道故障排除](/channels/troubleshooting)。

### TUI 无任何输出，应检查什么？

首先确认网关可达且智能体可正常运行：

```bash
openclaw status
openclaw models status
openclaw logs --follow
```

在 TUI 中，使用 `/status` 查看当前状态。若您期望在聊天通道中收到回复，请确保已启用投递功能（`/deliver on`）。

文档参考：[TUI](/web/tui)，[斜杠命令](/tools/slash-commands)。

### 如何彻底停止再重新启动网关？

若您已安装服务：

```bash
openclaw gateway stop
openclaw gateway start
```

此命令将停止/启动**受管服务**（macOS 上为 launchd，Linux 上为 systemd）。  
当网关作为后台守护进程运行时，请使用该命令。

若您以前台模式运行，请按 Ctrl-C 停止，然后执行：

```bash
openclaw gateway run
```

文档参考：[网关服务操作手册](/gateway)。

### ELI5：`openclaw gateway restart` 与 `openclaw gateway` 的区别

- `openclaw gateway restart`：重启**后台服务**（launchd/systemd）。
- `openclaw gateway`：在当前终端会话中以前台模式运行网关。

若您已安装服务，请使用网关命令。当您需要一次性、前台运行时，请使用 `openclaw gateway`。

### 出现故障时，如何最快获取更多详细信息？

使用 `--verbose` 启动网关以获得更详细的控制台输出。然后检查日志文件，重点关注通道认证、模型路由和 RPC 错误。

## 媒体与附件

### 我的技能生成了 imagePDF，但什么都没发送出去

代理发出的附件必须包含单独一行的 `Content-Type: application/pdf`（独占一行）。参见 [OpenClaw 助理设置](/start/openclaw) 和 [代理发送](/tools/agent-send)。

CLI 发送方式：

```bash
claw agent send --file report.pdf --type application/pdf
```

还需检查：

- 目标通道支持外发媒体，并且未被白名单拦截。
- 文件大小在服务商限制范围内（图像将被缩放至最大 2048px）。

参见 [图像](/nodes/images)。

## 安全与访问控制

### 将 OpenClaw 暴露给入站私信（DM）是否安全？

请将入站私信视为**不可信输入**。默认配置旨在降低风险：

- 在支持 DM 的通道上，默认行为为 **配对（pairing）**：
  - 未知发送者会收到一个配对码；机器人**不会处理**其消息。
  - 使用以下命令批准配对：`/pair <code>`
  - 待处理请求在每个通道上最多允许 **3 个**；若未收到配对码，请检查 `/pending`。

- 公开开放 DM 需要显式启用（设置 `allow_dm: true` 并配置白名单 `allowlist`）。

运行 `claw security check-dm` 以识别存在风险的 DM 策略。

### 提示注入（prompt injection）仅对公开机器人构成威胁吗？

不是。提示注入关注的是 **不可信内容**，而不仅限于谁可以向机器人发送私信。  
如果您的助理读取外部内容（如网络搜索/抓取、浏览器页面、邮件、文档、附件、粘贴的日志等），这些内容可能包含试图劫持模型的指令。即使 **您是唯一发送者**，这种情况也可能发生。

最大风险出现在启用了工具时：模型可能被诱骗泄露上下文，或代表您调用工具。可通过以下方式缩小影响范围：

- 使用只读或禁用工具的“阅读器”代理来汇总不可信内容；
- 对启用了工具的代理，关闭 `tool_allowlist` / `tool_denylist` / `tool_auto_approve`；
- 实施沙箱机制并严格限制工具白名单。

详情参见：[安全](/gateway/security)。

### 我的机器人是否应拥有独立的邮箱、GitHub 账号或电话号码？

是的，大多数部署场景下都建议如此。为机器人分配独立账号和电话号码，可在出现问题时显著缩小影响范围；同时也便于轮换凭证或撤销权限，而不会波及您的个人账户。

从小规模开始：仅授予实际所需的工具和账号权限，后续按需扩展。

文档参考：[安全](/gateway/security)，[配对](/channels/pairing)。

### 我能否赋予它对我短信的完全自主权？这样做安全吗？

我们**不推荐**对您的个人短信赋予完全自主权。最安全的做法是：

- 将私信保持在 **配对模式** 或严格的白名单中；
- 若希望它代您发送消息，请使用 **独立号码或账号**；
- 让它起草消息，然后由您 **审核后才发送**。

如需尝试实验性功能，请在专用账号上进行，并确保其完全隔离。参见 [安全](/gateway/security)。

### 我能否对个人助理任务使用更便宜的模型？

可以，**前提是**该代理仅用于纯聊天且输入内容可信。较小规格的模型更容易受到指令劫持攻击，因此请勿将其用于启用了工具的代理，或用于读取不可信内容的场景。若您必须使用较小模型，请严格锁定可用工具，并在沙箱环境中运行。参见 [安全](/gateway/security)。

### 我在 Telegram 中运行了 start，但未收到配对码

配对码**仅在**未知发送者向机器人发送消息且 `pairing: true` 已启用时才会发送。仅启用 `allow_dm: true` **不会**触发配对码生成。

检查待处理请求：

```bash
/pending
```

如需立即访问，可将您的发送者 ID 加入白名单，或为该账号设置 `allow_dm: true`。

### WhatsApp：它会自动给我联系人发消息吗？配对机制如何工作？

不会。WhatsApp 默认的私信策略为 **配对（pairing）**。未知发送者只会收到配对码，其消息**不会被处理**。OpenClaw 仅回复它接收到的聊天，或您主动触发的明确发送操作。

使用以下命令批准配对：

```bash
/pair <code>
```

列出待处理请求：

```bash
/pending
```

向导中的手机号提示：该号码用于设定您的 **白名单/所有者身份**，以便您的私信被允许通过；它**不用于自动发送消息**。如果您在自己的 WhatsApp 号码上运行，请使用该号码并启用 `allow_dm: true`。

## 聊天命令、中止任务与“它停不下来”

### 如何阻止内部系统消息显示在聊天窗口中？

大多数内部消息或工具消息仅在当前会话启用了 **verbose** 或 **reasoning** 时才会显示。

在您看到该消息的聊天窗口中执行以下操作：

```bash
/verbose off
```

若仍过于嘈杂，请检查控制界面（Control UI）中的会话设置，并将 verbose 设为 **inherit**。同时确认您未在配置中使用设置了 `reasoning: true` 的机器人配置文件。

文档参考：[思考与详细输出](/tools/thinking)，[安全 —— 群组中的推理与详细输出](/gateway/security#reasoning--verbose-output-in-groups)。

### 如何中止/取消正在运行的任务？

发送以下任意一项作为**独立消息**（不带斜杠）：

```
stop
cancel
abort
```

这些是中止触发词（非斜杠命令）。

对于后台进程（来自 exec 工具），您可以要求代理执行：

```bash
/exec kill <pid>
```

斜杠命令概览：参见 [斜杠命令](/tools/slash-commands)。  
大多数命令必须作为以 `/` 开头的**独立消息**发送，但少数快捷方式（例如 `/stop`）对白名单内的发送者也支持内联使用。

### 如何从 Telegram 发送 Discord 消息？提示“跨上下文消息被拒绝”

OpenClaw 默认禁止 **跨服务商（cross-provider）** 消息。若某工具调用绑定在 Telegram 上，则除非您显式允许，否则它不会向 Discord 发送消息。

为代理启用跨服务商消息：

```yaml
cross_provider: true
```

修改配置后重启网关。若您仅希望对单个代理启用此功能，请将其设置在 `agents.<name>.cross_provider` 下而非全局配置中。

### 为何感觉机器人会忽略连续快速发送的消息？

队列模式（queue mode）控制新消息如何与正在进行的任务交互。使用 `/queue <mode>` 更改模式：

- `/queue redirect` — 新消息重定向当前任务  
- `/queue serial` — 按顺序逐条运行消息  
- `/queue batch` — 批量收集消息并统一回复（默认）  
- `/queue steer` — 立即转向新指令，随后处理积压消息  
- `/queue abort` — 中止当前运行，重新开始  

您还可添加类似 `/queue followup` 的选项以启用后续交互模式。

## 根据截图/聊天记录中的问题，给出准确回答

**问：“使用 API 密钥时，Anthropic 的默认模型是什么？”**  

**答：** 在 OpenClaw 中，凭证与模型选择是相互独立的。设置 `ANTHROPIC_API_KEY`（或在认证配置文件中存储 Anthropic API 密钥）仅用于身份验证，而实际的默认模型取决于您在 `model` 字段中配置的内容（例如 `claude-3-haiku-20240307` 或 `claude-3-5-sonnet-20240620`）。若您看到 `anthropic auth failed`，说明网关未能在当前运行代理所预期的 `auth_profiles` 中找到 Anthropic 凭证。

---

仍遇到困难？欢迎前往 [Discord](https://discord.com/invite/clawd) 提问，或开启一个 [GitHub 讨论](https://github.com/openclaw/openclaw/discussions)。