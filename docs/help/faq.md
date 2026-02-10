---
summary: "Frequently asked questions about OpenClaw setup, configuration, and usage"
title: "FAQ"
---
# 常见问题解答

快速答案以及针对真实环境设置（本地开发、VPS、多代理、OAuth/API密钥、模型故障转移）的深入故障排除。有关运行时诊断，请参阅[故障排除](/gateway/troubleshooting)。有关完整配置参考，请参阅[配置](/gateway/configuration)。

## 目录

- [快速入门和首次运行设置]
  - [我卡住了，最快的方法是什么？](#im-stuck-whats-the-fastest-way-to-get-unstuck)
  - [推荐的安装和设置OpenClaw的方法是什么？](#whats-the-recommended-way-to-install-and-set-up-openclaw)
  - [入职后如何打开仪表板？](#how-do-i-open-the-dashboard-after-onboarding)
  - [如何在本地主机与远程认证仪表板（令牌）？](#how-do-i-authenticate-the-dashboard-token-on-localhost-vs-remote)
  - [我需要什么运行时？](#what-runtime-do-i-need)
  - [它能在树莓派上运行吗？](#does-it-run-on-raspberry-pi)
  - [树莓派安装的任何技巧吗？](#any-tips-for-raspberry-pi-installs)
  - [它卡在“唤醒我的朋友”/入职不会孵化怎么办？](#it-is-stuck-on-wake-up-my-friend-onboarding-will-not-hatch-what-now)
  - [我可以迁移设置到新机器（Mac mini）而无需重新入职吗？](#can-i-migrate-my-setup-to-a-new-machine-mac-mini-without-redoing-onboarding)
  - [在哪里查看最新版本的新功能？](#where-do-i-see-what-is-new-in-the-latest-version)
  - [我无法访问docs.openclaw.ai（SSL错误）。怎么办？](#i-cant-access-docsopenclawai-ssl-error-what-now)
  - [稳定版和测试版有什么区别？](#whats-the-difference-between-stable-and-beta)
  - [如何安装测试版，测试版和开发版有什么区别？](#how-do-i-install-the-beta-version-and-whats-the-difference-between-beta-and-dev)
  - [如何尝试最新的代码？](#how-do-i-try-the-latest-bits)
  - [安装和入职通常需要多长时间？](#how-long-does-install-and-onboarding-usually-take)
  - [安装程序卡住了。

如何获取更多反馈？](#installer-stuck-how-do-i-get-more-feedback)
  - [Windows 安装提示找不到 git 或未识别 openclaw](#windows-install-says-git-not-found-or-openclaw-not-recognized)
  - [文档没有回答我的问题 - 我该如何获得更好的答案？](#the-docs-didnt-answer-my-question-how-do-i-get-a-better-answer)
  - [如何在 Linux 上安装 OpenClaw？](#how-do-i-install-openclaw-on-linux)
  - [如何在 VPS 上安装 OpenClaw？](#how-do-i-install-openclaw-on-a-vps)
  - [云/VPS 安装指南在哪里？](#where-are-the-cloudvps-install-guides)
  - [我可以要求 OpenClaw 自动更新吗？](#can-i-ask-openclaw-to-update-itself)
  - [入站向导实际上做了什么？](#what-does-the-onboarding-wizard-actually-do)
  - [运行此程序是否需要 Claude 或 OpenAI 订阅？](#do-i-need-a-claude-or-openai-subscription-to-run-this)
  - [我可以在没有 API 密钥的情况下使用 Claude Max 订阅吗？](#can-i-use-claude-max-subscription-without-an-api-key)
  - [Anthropic 的 "setup-token" 认证是如何工作的？](#how-does-anthropic-setuptoken-auth-work)
  - [我在哪里可以找到 Anthropic 的 setup-token？](#where-do-i-find-an-anthropic-setuptoken)
  - [你们支持 Claude 订阅认证（Claude Pro 或 Max）吗？](#do-you-support-claude-subscription-auth-claude-pro-or-max)
  - [为什么我会看到来自 Anthropic 的 `HTTP 429: rate_limit_error`？](#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)
  - [是否支持 AWS Bedrock？](#is-aws-bedrock-supported)
  - [Codex 认证是如何工作的？](#how-does-codex-auth-work)
  - [你们支持 OpenAI 订阅认证（Codex OAuth）吗？](#do-you-support-openai-subscription-auth-codex-oauth)
  - [如何设置 Gemini CLI OAuth](#how-do-i-set-up-gemini-cli-oauth)
  - [本地模型适合日常聊天吗？](#is-a-local-model-ok-for-casual-chats)
  - [如何将托管模型流量保持在特定区域？](#how-do-i-keep-hosted-model-traffic-in-a-specific-region)
  - [我必须购买 Mac Mini 才能安装这个吗？](#do-i-have-to-buy-a-mac-mini-to-install-this)
  - [我需要 Mac mini 才能支持 iMessage 吗？](#do-i-need-a-mac-mini-for-imessage-support)
  - [如果我购买 Mac Mini 来运行 OpenClaw，可以将其连接到我的 MacBook Pro 吗？](#if-i-buy-a-mac-mini-to-run-openclaw-can-i-connect-it-to-my-macbook-pro)
  - [我可以使用 Bun 吗？](#can-i-use-bun)
  - [Telegram：`allowFrom` 中应该填写什么？](#telegram-what-goes-in-allowfrom)
  - [多个人可以使用一个 WhatsApp 号码并运行不同的 OpenClaw 实例吗？](#can-multiple-people-use-one-whatsapp-number-with-different-openclaw-instances)
  - [我可以运行“快速聊天”代理和“Opus for coding”代理吗？](#can-i-run-a-fast-chat-agent-and-an-opus-for-coding-agent)
  - [Homebrew 是否适用于 Linux？](#does-homebrew-work-on-linux)
  - [可修改（git）安装和 npm 安装有什么区别？](#whats-the-difference-between-the-hackable-git-install-and-npm-install)
  - [我以后可以在这两者之间切换吗？](#can-i-switch-between-npm-and-git-installs-later)
  - [我应该在我的笔记本电脑上还是 VPS 上运行网关？](#should-i-run-the-gateway-on-my-laptop-or-a-vps)
  - [在专用机器上运行 OpenClaw 多重要？](#how-important-is-it-to-run-openclaw-on-a-dedicated-machine)
  - [最低 VPS 要求和推荐的操作系统是什么？](#what-are-the-minimum-vps-requirements-and-recommended-os)
  - [我可以在虚拟机中运行 OpenClaw 吗？具体要求是什么？](#can-i-run-openclaw-in-a-vm-and-what-are-the-requirements)
- [什么是 OpenClaw？](#what-is-openclaw)
  - [用一句话描述 OpenClaw 是什么？](#what-is-openclaw-in-one-paragraph)
  - [价值主张是什么？](#whats-the-value-proposition)
  - [我已经设置了它，我应该先做什么？](#i-just-set-it-up-what-should-i-do-first)
  - [OpenClaw 的五大日常用例是什么？](#what-are-the-top-five-everyday-use-cases-for-openclaw)
  - [OpenClaw 能否帮助生成 SaaS 的潜在客户推广广告和博客？](#can-openclaw-help-with-lead-gen-outreach-ads-and-blogs-for-a-saas)
  - [与 Claude Code 相比，OpenClaw 在 Web 开发方面的优势是什么？](#what-are-the-advantages-vs-claude-code-for-web-development)
- [技能和自动化](#skills-and-automation)
  - [如何自定义技能而不弄脏仓库？](#how-do-i-customize-skills-without-keeping-the-repo-dirty)
  - [我可以从自定义文件夹加载技能吗？](#can-i-load-skills-from-a-custom-folder)
  - [如何为不同的任务使用不同的模型？](#how-can-i-use-different-models-for-different-tasks)
  - [机器人在执行繁重工作时会冻结。

如何卸载这些任务？](#the-bot-freezes-while-doing-heavy-work-how-do-i-offload-that)
  - [Cron 或提醒没有触发。我应该检查什么？](#cron-or-reminders-do-not-fire-what-should-i-check)
  - [如何在 Linux 上安装技能？](#how-do-i-install-skills-on-linux)
  - [OpenClaw 能否按计划或在后台持续运行任务？](#can-openclaw-run-tasks-on-a-schedule-or-continuously-in-the-background)
  - [我能否从 Linux 运行仅适用于 Apple macOS 的技能？](#can-i-run-apple-macos-only-skills-from-linux)
  - [你们有 Notion 或 HeyGen 集成吗？](#do-you-have-a-notion-or-heygen-integration)
  - [如何安装浏览器接管的 Chrome 扩展？](#how-do-i-install-the-chrome-extension-for-browser-takeover)
- [沙箱和内存](#sandboxing-and-memory)
  - [是否有专门的沙箱文档？](#is-there-a-dedicated-sandboxing-doc)
  - [如何将主机文件夹绑定到沙箱？](#how-do-i-bind-a-host-folder-into-the-sandbox)
  - [内存是如何工作的？](#how-does-memory-work)
  - [内存总是忘记事情。我该如何让它记住？](#memory-keeps-forgetting-things-how-do-i-make-it-stick)
  - [内存会永远保存吗？有什么限制？](#does-memory-persist-forever-what-are-the-limits)
  - [语义记忆搜索是否需要 OpenAI API 密钥？](#does-semantic-memory-search-require-an-openai-api-key)
- [磁盘上的文件位置](#where-things-live-on-disk)
  - [与 OpenClaw 使用的所有数据都保存在本地吗？](#is-all-data-used-with-openclaw-saved-locally)
  - [OpenClaw 存储其数据的位置在哪里？](#where-does-openclaw-store-its-data)
  - [AGENTS.md / SOUL.md / USER.md / MEMORY.md 应该放在哪里？](#where-should-agentsmd-soulmd-usermd-memorymd-live)
  - [推荐的备份策略是什么？](#whats-the-recommended-backup-strategy)
  - [如何完全卸载 OpenClaw？](#how-do-i-completely-uninstall-openclaw)
  - [代理可以在工作区外工作吗？](#can-agents-work-outside-the-workspace)
  - [我在远程模式下 - 会话存储在哪里？](#im-in-remote-mode-where-is-the-session-store)
- [配置基础](#config-basics)
  - [配置的格式是什么？它在哪里？](#what-format-is-the-config-where-is-it)
  - [我设置了 `gateway.bind: "lan"`（或 `"tailnet"`），现在没有任何监听/界面显示未经授权](#i-set-gatewaybind-lan-or-tailnet-and-now-nothing-listens-the-ui-says-unauthorized)
  - [为什么我现在在本地主机上需要一个令牌？](#why-do-i-need-a-token-on-localhost-now)
  - [更改配置后是否需要重启？](#do-i-have-to-restart-after-changing-config)
  - [如何启用网络搜索（和网络获取）？](#how-do-i-enable-web-search-and-web-fetch)
  - [config.apply 清除了我的配置。

如何恢复并避免这种情况？](#configapply-wiped-my-config-how-do-i-recover-and-avoid-this)
  - [如何在设备间运行一个中心网关和专用工作者？](#how-do-i-run-a-central-gateway-with-specialized-workers-across-devices)
  - [OpenClaw浏览器可以无头运行吗？](#can-the-openclaw-browser-run-headless)
  - [如何使用Brave进行浏览器控制？](#how-do-i-use-brave-for-browser-control)
- [远程网关和节点](#remote-gateways-and-nodes)
  - [Telegram、网关和节点之间命令如何传播？](#how-do-commands-propagate-between-telegram-the-gateway-and-nodes)
  - [如果网关托管在远程位置，我的代理如何访问我的计算机？](#how-can-my-agent-access-my-computer-if-the-gateway-is-hosted-remotely)
  - [Tailscale已连接但没有收到回复。怎么办？](#tailscale-is-connected-but-i-get-no-replies-what-now)
  - [两个OpenClaw实例可以相互通信吗（本地+VPS）？](#can-two-openclaw-instances-talk-to-each-other-local-vps)
  - [多个代理是否需要单独的VPS？](#do-i-need-separate-vpses-for-multiple-agents)
  - [在我的个人笔记本电脑上使用节点而不是从VPS通过SSH连接是否有好处？](#is-there-a-benefit-to-using-a-node-on-my-personal-laptop-instead-of-ssh-from-a-vps)
  - [节点是否运行网关服务？](#do-nodes-run-a-gateway-service)
  - [是否有API/RPC方式来应用配置？](#is-there-an-api-rpc-way-to-apply-config)
  - [首次安装时最小的“合理”配置是什么？](#whats-a-minimal-sane-config-for-a-first-install)
  - [如何在VPS上设置Tailscale并从Mac连接？](#how-do-i-set-up-tailscale-on-a-vps-and-connect-from-my-mac)
  - [如何将Mac节点连接到远程网关（Tailscale Serve）？](#how-do-i-connect-a-mac-node-to-a-remote-gateway-tailscale-serve)
  - [应该在第二台笔记本电脑上安装还是只是添加一个节点？](#should-i-install-on-a-second-laptop-or-just-add-a-node)
- [环境变量和.env加载](#env-vars-and-env-loading)
  - [OpenClaw如何加载环境变量？](#how-does-openclaw-load-environment-variables)
  - [“我通过服务启动了网关，我的环境变量消失了。”怎么办？](#i-started-the-gateway-via-the-service-and-my-env-vars-disappeared-what-now)
  - [我设置了`COPILOT_GITHUB_TOKEN`，但模型状态显示“Shell env: off。”为什么？](#i-set-copilotgithubtoken-but-models-status-shows-shell-env-off-why)
- [会话和多个聊天](#sessions-and-multiple-chats)
  - [如何开始一个新的对话？](#how-do-i-start-a-fresh-conversation)
  - [如果我从未发送过`/new`，会话是否会自动重置？](#do-sessions-reset-automatically-if-i-never-send-new)
  - [是否有方法使OpenClaw实例团队化，一个CEO和多个代理？](#is-there-a-way-to-make-a-team-of-openclaw-instances-one-ceo-and-many-agents)
  - [为什么上下文在任务中途被截断。

如何防止这种情况？](#why-did-context-get-truncated-midtask-how-do-i-prevent-it)
  - [如何完全重置OpenClaw但保留安装？](#how-do-i-completely-reset-openclaw-but-keep-it-installed)
  - [我收到“上下文太大”错误 - 如何重置或压缩？](#im-getting-context-too-large-errors-how-do-i-reset-or-compact)
  - [为什么我会看到“LLM请求被拒绝：messages.N.content.X.tool_use.input：字段必需”？](#why-am-i-seeing-llm-request-rejected-messagesncontentxtooluseinput-field-required)
  - [为什么我每30分钟收到一次心跳消息？](#why-am-i-getting-heartbeat-messages-every-30-minutes)
  - [我是否需要向WhatsApp群组添加一个“机器人账户”？](#do-i-need-to-add-a-bot-account-to-a-whatsapp-group)
  - [如何获取WhatsApp群组的JID？](#how-do-i-get-the-jid-of-a-whatsapp-group)
  - [为什么OpenClaw不在群组中回复？](#why-doesnt-openclaw-reply-in-a-group)
  - [群组/线程是否与DM共享上下文？](#do-groupsthreads-share-context-with-dms)
  - [我可以创建多少个工作区和代理？](#how-many-workspaces-and-agents-can-i-create)
  - [我可以在同一时间运行多个机器人或聊天（Slack），应该如何设置？](#can-i-run-multiple-bots-or-chats-at-the-same-time-slack-and-how-should-i-set-that-up)
- [模型：默认值、选择、别名、切换](#models-defaults-selection-aliases-switching)
  - [什么是“默认模型”？](#what-is-the-default-model)
  - [你推荐使用哪个模型？](#what-model-do-you-recommend)
  - [如何在不擦除配置的情况下切换模型？](#how-do-i-switch-models-without-wiping-my-config)
  - [我可以使用自托管模型（llama.cpp、vLLM、Ollama）吗？](#can-i-use-selfhosted-models-llamacpp-vllm-ollama)
  - [OpenClaw、Flawd和Krill使用什么模型？](#what-do-openclaw-flawd-and-krill-use-for-models)
  - [如何实时切换模型（无需重启）？](#how-do-i-switch-models-on-the-fly-without-restarting)
  - [我可以使用GPT 5.2进行日常任务，Codex 5.3进行编码吗？](#can-i-use-gpt-52-for-daily-tasks-and-codex-53-for-coding)
  - [为什么我会看到“模型……不允许”然后没有回复？](#why-do-i-see-model-is-not-allowed-and-then-no-reply)
  - [为什么我会看到“未知模型：minimax/MiniMax-M2.1”？](#why-do-i-see-unknown-model-minimaxminimaxm21)
  - [我可以使用MiniMax作为默认模型，OpenAI用于复杂任务吗？](#can-i-use-minimax-as-my-default-and-openai-for-complex-tasks)
  - [opus / sonnet / gpt是内置快捷方式吗？](#are-opus-sonnet-gpt-builtin-shortcuts)
  - [如何定义/覆盖模型快捷方式（别名）？](#how-do-i-defineoverride-model-shortcuts-aliases)
  - [如何添加来自其他提供商的模型，如OpenRouter或Z.AI？](#how-do-i-add-models-from-other-providers-like-openrouter-or-zai)
- [模型故障转移和“All models failed”](#model-failover-and-all-models-failed)
  - [故障转移是如何工作的？](#how-does-failover-work)
  - [这个错误是什么意思？](#what-does-this-error-mean)
  - [针对`No credentials found for profile "anthropic:default"`的修复检查表](#fix-checklist-for-no-credentials-found-for-profile-anthropicdefault)
  - [为什么它也尝试了Google Gemini并失败了？](#why-did-it-also-try-google-gemini-and-fail)
- [身份验证配置文件：它们是什么以及如何管理它们](#auth-profiles-what-they-are-and-how-to-manage-them)
  - [什么是身份验证配置文件？](#what-is-an-auth-profile)
  - [典型的配置文件ID有哪些？](#what-are-typical-profile-ids)
  - [我可以控制首先尝试哪个身份验证配置文件吗？](#can-i-control-which-auth-profile-is-tried-first)
  - [OAuth与API密钥：有什么区别？](#oauth-vs-api-key-whats-the-difference)
- [网关：端口、“已经在运行”和远程模式](#gateway-ports-already-running-and-remote-mode)
  - [网关使用哪个端口？](#what-port-does-the-gateway-use)
  - [为什么`openclaw gateway status`显示`Runtime: running`但`RPC probe: failed`？](#why-does-openclaw-gateway-status-say-runtime-running-but-rpc-probe-failed)
  - [为什么`openclaw gateway status`显示`Config (cli)`和`Config (service)`不同？](#why-does-openclaw-gateway-status-show-config-cli-and-config-service-different)
  - [“另一个网关实例已经在监听”是什么意思？](#what-does-another-gateway-instance-is-already-listening-mean)
  - [如何以远程模式运行OpenClaw（客户端连接到其他地方的网关）？](#how-do-i-run-openclaw-in-remote-mode-client-connects-to-a-gateway-elsewhere)
  - 控制UI显示“未授权”（或不断重新连接）。

现在怎么办？](#the-control-ui-says-unauthorized-or-keeps-reconnecting-what-now)
  - [我设置了 `gateway.bind: "tailnet"` 但无法绑定 / 没有监听](#i-set-gatewaybind-tailnet-but-it-cant-bind-nothing-listens)
  - [我可以在同一主机上运行多个网关吗？](#can-i-run-multiple-gateways-on-the-same-host)
  - [“无效握手” / 代码 1008 是什么意思？](#what-does-invalid-handshake-code-1008-mean)
- [日志记录和调试](#logging-and-debugging)
  - [日志在哪里？](#where-are-logs)
  - [如何启动/停止/重启网关服务？](#how-do-i-startstoprestart-the-gateway-service)
  - [我在 Windows 上关闭了终端 - 如何重新启动 OpenClaw？](#i-closed-my-terminal-on-windows-how-do-i-restart-openclaw)
  - [网关已启动但回复从未到达。我应该检查什么？](#the-gateway-is-up-but-replies-never-arrive-what-should-i-check)
  - [“与网关断开连接：无原因” - 现在怎么办？](#disconnected-from-gateway-no-reason-what-now)
  - [Telegram setMyCommands 因网络错误失败。我应该检查什么？](#telegram-setmycommands-fails-with-network-errors-what-should-i-check)
  - [TUI 显示没有输出。我应该检查什么？](#tui-shows-no-output-what-should-i-check)
  - [如何完全停止然后启动网关？](#how-do-i-completely-stop-then-start-the-gateway)
  - [ELI5: `openclaw gateway restart` vs `openclaw gateway`](#eli5-openclaw-gateway-restart-vs-openclaw-gateway)
  - [当某件事失败时，获取更多详细信息的最快方法是什么？](#whats-the-fastest-way-to-get-more-details-when-something-fails)
- [媒体和附件](#media-and-attachments)
  - [我的技能生成了一张图片/PDF，但什么也没发送](#my-skill-generated-an-imagepdf-but-nothing-was-sent)
- [安全和访问控制](#security-and-access-control)
  - [将 OpenClaw 暴露给传入的直接消息是否安全？](#is-it-safe-to-expose-openclaw-to-inbound-dms)
  - [提示注入仅对公共机器人是一个问题吗？](#is-prompt-injection-only-a-concern-for-public-bots)
  - [我的机器人是否应该有自己的电子邮件 GitHub 账户或电话号码](#should-my-bot-have-its-own-email-github-account-or-phone-number)
  - [我可以让它自主处理我的短信吗，这样做安全吗](#can-i-give-it-autonomy-over-my-text-messages-and-is-that-safe)
  - [我可以使用更便宜的模型来执行个人助理任务吗？](#can-i-use-cheaper-models-for-personal-assistant-tasks)
  - [我在 Telegram 中运行了 `/start` 但没有收到配对码](#i-ran-start-in-telegram-but-didnt-get-a-pairing-code)
  - [WhatsApp：它会给我联系人发消息。配对是如何工作的？](#whatsapp-will-it-message-my-contacts-how-does-pairing-work)
- [聊天命令、取消任务以及“它不会停止”](#chat-commands-aborting-tasks-and-it-wont-stop)
  - [如何阻止内部系统消息显示在聊天中](#how-do-i-stop-internal-system-messages-from-showing-in-chat)
  - [如何停止/取消正在运行的任务？](#how-do-i-stopcancel-a-running-task)
  - [如何从 Telegram 发送 Discord 消息。

("跨上下文消息被拒绝")](#how-do-i-send-a-discord-message-from-telegram-crosscontext-messaging-denied)
  - [为什么感觉机器人“忽略了”连发的消息？](#why-does-it-feel-like-the-bot-ignores-rapidfire-messages).

## 如果出现问题时的前60秒

1. **快速状态检查（首次检查）**

   ```bash
   openclaw status
   ```

   快速本地摘要：操作系统 + 更新，网关/服务可达性，代理/会话，提供商配置 + 运行时问题（当网关可达时）。

2. **可粘贴报告（安全共享）**

   ```bash
   openclaw status --all
   ```

   只读诊断带有日志尾部（令牌已红acted）。

3. **守护进程 + 端口状态**

   ```bash
   openclaw gateway status
   ```

   显示监督器运行时与RPC可达性，探测目标URL，以及服务可能使用的配置。

4. **深入探测**

   ```bash
   openclaw status --deep
   ```

   运行网关健康检查 + 提供商探测（需要可达的网关）。参见 [Health](/gateway/health)。

5. **查看最新的日志**

   ```bash
   openclaw logs --follow
   ```

   如果RPC关闭，回退到：

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   文件日志与服务日志分开；参见 [Logging](/logging) 和 [Troubleshooting](/gateway/troubleshooting)。

6. **运行医生（修复）**

   ```bash
   openclaw doctor
   ```

   修复/迁移配置/状态 + 运行健康检查。参见 [Doctor](/gateway/doctor)。

7. **网关快照**

   ```bash
   openclaw health --json
   openclaw health --verbose   # shows the target URL + config path on errors
   ```

   请求正在运行的网关进行完整快照（仅限WS）。参见 [Health](/gateway/health)。

## 快速开始和首次运行设置

### 我卡住了，最快的方法是什么？

使用一个可以**看到你的机器**的本地AI代理。这比在Discord上询问要有效得多，因为大多数“I'm stuck”情况是**本地配置或环境问题**，远程助手无法检查。

- **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
- **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

这些工具可以读取仓库，运行命令，检查日志，并帮助你修复机器级别的设置（PATH，服务，权限，认证文件）。通过可修改的（git）安装方式提供**完整的源代码检出**：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
```

这将从git检出安装OpenClaw，因此代理可以读取代码 + 文档并推理你正在运行的确切版本。稍后你可以通过不带 `--install-method git` 的重新运行安装程序切换回稳定版。

提示：要求代理**计划和监督**修复（逐步），然后只执行必要的命令。这样可以保持更改小且更容易审计。

如果你发现了一个真正的bug或修复，请提交GitHub问题或发送PR：
[https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
[https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

从这些命令开始（请求帮助时分享输出）：

```bash
openclaw status
openclaw models status
openclaw doctor
```

它们的作用：

- `openclaw status`: 网关/代理健康状况快速快照 + 基本配置。
- `openclaw models status`: 检查提供商认证 + 模型可用性。
- `openclaw doctor`: 验证并修复常见的配置/状态问题。

其他有用的CLI检查：`openclaw status --all`, `openclaw logs --follow`,
`openclaw gateway status`, `openclaw health --verbose`.

快速调试循环：[如果出现问题，前60秒](#first-60-seconds-if-somethings-broken).
安装文档：[安装](/install), [安装器标志](/install/installer), [更新](/install/updating).

### 推荐的OpenClaw安装和设置方式是什么

仓库推荐从源代码运行并使用入站向导：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
openclaw onboard --install-daemon
```

向导还可以自动构建UI资源。入站后，通常在端口 **18789** 上运行网关。

从源代码（贡献者/开发人员）：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm build
pnpm ui:build # auto-installs UI deps on first run
openclaw onboard
```

如果没有全局安装，通过 `pnpm openclaw onboard` 运行它。

### 入站后如何打开仪表板

向导会在入站后立即使用干净的（非令牌化的）仪表板URL打开浏览器，并在摘要中打印链接。保持该选项卡打开；如果未启动，请在同一台机器上复制/粘贴打印的URL。

### 如何在本地主机与远程之间验证仪表板令牌

**本地主机（同一台机器）：**

- 打开 `http://127.0.0.1:18789/`。
- 如果需要身份验证，请将来自 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）的令牌粘贴到控制UI设置中。
- 从网关主机检索它：`openclaw config get gateway.auth.token`（或生成一个：`openclaw doctor --generate-gateway-token`）。

**不在本地主机：**

- **Tailscale Serve**（推荐）：保持绑定回环，运行 `openclaw gateway --tailscale serve`，打开 `https://<magicdns>/`。如果 `gateway.auth.allowTailscale` 是 `true`，身份头满足身份验证（无需令牌）。
- **Tailnet 绑定**：运行 `openclaw gateway --bind tailnet --token "<token>"`，打开 `http://<tailscale-ip>:18789/`，在仪表板设置中粘贴令牌。
- **SSH 隧道**：`ssh -N -L 18789:127.0.0.1:18789 user@host` 然后打开 `http://127.0.0.1:18789/` 并在控制UI设置中粘贴令牌。

参见 [仪表板](/web/dashboard) 和 [Web 表面](/web) 以获取绑定模式和身份验证详细信息。

### 我需要什么运行时

需要 Node **>= 22**。推荐 `pnpm`。不建议在网关中使用 Bun。

### 它是否可以在树莓派上运行

是的。网关轻量级 - 文档列出 **512MB-1GB 内存**，**1 核心**，以及大约 **500MB**
磁盘空间作为个人使用的足够配置，并注意 **Raspberry Pi 4 可以运行它**。

如果您需要额外的空间（日志、媒体、其他服务），**建议使用2GB**，但这并不是最低要求。

提示：一个小的树莓派/VPS可以托管网关，并且您可以在笔记本电脑/手机上配对**节点**以进行本地屏幕/摄像头/画布或命令执行。参见[Nodes](/nodes)。

### 关于Raspberry Pi安装的任何建议

简短版本：它可以工作，但请做好遇到问题的准备。

- 使用**64位**操作系统并保持Node >= 22。
- 偏好使用**可修改的（git）安装**，以便您可以查看日志并快速更新。
- 从不带通道/技能开始，然后逐个添加。
- 如果遇到奇怪的二进制问题，通常是**ARM兼容性**问题。

文档：[Linux](/platforms/linux)，[Install](/install)。

### 它卡在“唤醒我的朋友”入职流程无法启动怎么办

该屏幕依赖于网关可达且已认证。TUI也会在首次启动时自动发送“唤醒我的朋友！”。如果您看到该行但**没有回复**且令牌保持为0，则代理从未运行过。

1. 重启网关：

```bash
openclaw gateway restart
```

2. 检查状态+认证：

```bash
openclaw status
openclaw models status
openclaw logs --follow
```

3. 如果仍然卡住，请运行：

```bash
openclaw doctor
```

如果网关是远程的，请确保隧道/Tailscale连接正常，并且UI指向正确的网关。参见[远程访问](/gateway/remote)。

### 我可以将设置迁移到新机器Mac mini而无需重新入职吗

可以。复制**状态目录**和**工作区**，然后运行一次Doctor。这将使您的机器人“完全相同”（内存、会话历史、认证和通道状态），只要您复制了**两个**位置：

1. 在新机器上安装OpenClaw。
2. 从旧机器复制`$OPENCLAW_STATE_DIR`（默认：`~/.openclaw`）。
3. 复制您的工作区（默认：`~/.openclaw/workspace`）。
4. 运行`openclaw doctor`并重启网关服务。

这将保留配置、认证配置文件、WhatsApp凭证、会话和内存。如果您处于远程模式，请记住网关主机拥有会话存储和工作区。

**重要：** 如果您仅将工作区提交/推送到GitHub，则备份的是**内存+引导文件**，而不是会话历史或认证。这些位于`~/.openclaw/`下（例如`~/.openclaw/agents/<agentId>/sessions/`）。

相关：[迁移](/install/migrating)，[磁盘上的位置](/help/faq#where-does-openclaw-store-its-data)，[代理工作区](/concepts/agent-workspace)，[Doctor](/gateway/doctor)，[远程模式](/gateway/remote)。

### 我在哪里可以看到最新版本的新功能

检查GitHub变更日志：
[https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

最新的条目在顶部。如果顶部部分标记为**未发布**，则下一个有日期的部分是最新发布的版本。条目按**亮点**、**更改**和**修复**分组（如有需要，还包括文档/其他部分）。

### 我无法访问 docs.openclaw.ai SSL 错误怎么办

一些Comcast/Xfinity连接通过Xfinity Advanced Security错误地阻止了`docs.openclaw.ai`。禁用它或将`docs.openclaw.ai`加入白名单，然后重试。更多详情：[故障排除](/help/troubleshooting#docsopenclawai-shows-an-ssl-error-comcastxfinity)。
请通过报告帮助我们解除阻止：[https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status)。

如果您仍然无法访问该网站，文档已镜像到GitHub：
[https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

### 稳定版和测试版有什么区别

**稳定版**和**测试版**是**npm dist-tags**，而不是独立的代码线：

- `latest` = 稳定版
- `beta` = 用于测试的早期构建

我们将构建版本发布到**测试版**，进行测试，一旦某个构建版本稳定，我们就将其**提升到`latest`**。这就是为什么测试版和稳定版可以指向**同一个版本**。

查看更改内容：
[https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

### 如何安装测试版以及测试版与开发版有什么区别

**测试版**是npm dist-tag `beta`（可能与`latest`匹配）。**开发版**是`main`（git）的最新提交；发布时，它使用npm dist-tag `dev`。

单行命令（macOS/Linux）：

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
```

```bash
curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
```

Windows安装程序（PowerShell）：
[https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

更多详情：[开发渠道](/install/development-channels) 和 [安装程序标志](/install/installer)。

### 安装和入门通常需要多长时间

大致指南：

- **安装：** 2-5分钟
- **入门：** 根据您配置的频道/模型数量，需要5-15分钟

如果卡住了，请使用[安装程序卡住](/help/faq#installer-stuck-how-do-i-get-more-feedback)
和[我卡住了](/help/faq#im-stuck--whats-the-fastest-way-to-get-unstuck)中的快速调试循环。

### 如何尝试最新的代码

两个选项：

1. **开发渠道（git checkout）：**

```bash
openclaw update --channel dev
```

这会切换到`main`分支并从源代码更新。

2. **可编辑安装（来自安装程序网站）：**

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
```

这为您提供了一个可以编辑的本地仓库，然后通过git进行更新。

如果您更喜欢手动进行干净的克隆，请使用：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm build
```

文档：[更新](/cli/update)，[开发渠道](/install/development-channels)，
[安装](/install)。

### 安装程序卡住如何获取更多信息

使用**详细输出**重新运行安装程序：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
```

Beta 安装并启用详细输出：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
```

对于可修改的 (git) 安装：

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
```

更多选项：[安装器标志](/install/installer)。

### Windows 安装提示找不到 git 或 openclaw 未被识别

两个常见的 Windows 问题：

**1) npm 错误 spawn git / 找不到 git**

- 安装 **Git for Windows** 并确保 `git` 在你的 PATH 中。
- 关闭并重新打开 PowerShell，然后重新运行安装程序。

**2) 安装后 openclaw 未被识别**

- 你的 npm 全局 bin 文件夹不在 PATH 中。
- 检查路径：

  ```powershell
  npm config get prefix
  ```

- 确保 `<prefix>\\bin` 在 PATH 中（在大多数系统上它是 `%AppData%\\npm`）。
- 更新 PATH 后关闭并重新打开 PowerShell。

如果你希望获得最流畅的 Windows 设置，请使用 **WSL2** 而不是原生 Windows。
文档：[Windows](/platforms/windows)。

### 文档没有回答我的问题，我该如何得到更好的答案

使用 **可修改的 (git) 安装**，这样你就可以在本地拥有完整的源代码和文档，然后从该文件夹询问
你的机器人（或 Claude/Codex），以便它可以读取仓库并准确回答。

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
```

更多详情：[安装](/install) 和 [安装器标志](/install/installer)。

### 如何在 Linux 上安装 OpenClaw

简短答案：按照 Linux 指南操作，然后运行入站向导。

- Linux 快速路径 + 服务安装：[Linux](/platforms/linux)。
- 完整指南：[入门](/start/getting-started)。
- 安装程序 + 更新：[安装 & 更新](/install/updating)。

### 如何在 VPS 上安装 OpenClaw

任何 Linux VPS 都可以。在服务器上安装，然后使用 SSH/Tailscale 访问网关。

指南：[exe.dev](/install/exe-dev)，[Hetzner](/install/hetzner)，[Fly.io](/install/fly)。
远程访问：[网关远程](/gateway/remote)。

### 云 VPS 安装指南在哪里

我们维护了一个 **托管中心**，其中包含常见提供商。选择一个并按照指南操作：

- [VPS 托管](/vps)（所有提供商集中在一起）
- [Fly.io](/install/fly)
- [Hetzner](/install/hetzner)
- [exe.dev](/install/exe-dev)

在云端的工作原理：**网关在服务器上运行**，你可以通过控制界面（或 Tailscale/SSH）从笔记本电脑/手机访问它。
你的状态 + 工作区存储在服务器上，因此将主机视为真相来源并进行备份。

你可以将 **节点**（Mac/iOS/Android/无头）与该云网关配对以访问
本地屏幕/摄像头/画布或在保持网关在云端的同时在笔记本电脑上运行命令。

中心：[平台](/platforms)。远程访问：[网关远程](/gateway/remote)。
节点：[节点](/nodes)，[节点 CLI](/cli/nodes)。

### 我可以让 OpenClaw 自动更新吗？

简短回答：**可能，但不推荐**。更新流程可能会重启Gateway（这会中断活动会话），可能需要干净的git检出，并且可能会提示确认。更安全的做法是从shell作为操作员运行更新。

使用CLI：

```bash
openclaw update
openclaw update status
openclaw update --channel stable|beta|dev
openclaw update --tag <dist-tag|version>
openclaw update --no-restart
```

如果必须从代理自动化：

```bash
openclaw update --yes --no-restart
openclaw gateway restart
```

文档：[Update](/cli/update), [Updating](/install/updating).

### 入门向导实际上做了什么

`openclaw onboard` 是推荐的设置路径。在 **本地模式** 下，它会引导你完成：

- **模型/身份验证设置**（Anthropic **setup-token** 推荐用于Claude订阅，支持OpenAI Codex OAuth，API密钥可选，支持LM Studio本地模型）
- **工作区** 位置 + 引导文件
- **Gateway 设置**（绑定/端口/身份验证/Tailscale）
- **提供商**（WhatsApp, Telegram, Discord, Mattermost (插件), Signal, iMessage）
- **守护进程安装**（macOS上的LaunchAgent；Linux/WSL2上的systemd用户单元）
- **健康检查** 和 **技能** 选择

如果配置的模型未知或缺少身份验证，它也会发出警告。

### 我是否需要Claude或OpenAI订阅才能运行此程序

不需要。你可以使用 **API密钥**（Anthropic/OpenAI/其他）或仅使用 **本地模型** 运行OpenClaw，以便数据保留在你的设备上。订阅（Claude Pro/Max 或 OpenAI Codex）是这些提供商的身份验证的可选方式。

文档：[Anthropic](/providers/anthropic), [OpenAI](/providers/openai), [本地模型](/gateway/local-models), [模型](/concepts/models).

### 我可以在没有API密钥的情况下使用Claude Max订阅吗

可以。你可以使用 **setup-token** 而不是API密钥进行身份验证。这是订阅路径。

Claude Pro/Max订阅 **不包括API密钥**，因此对于订阅账户，这是正确的做法。重要：你必须与Anthropic核实，这种使用方式符合他们的订阅政策和条款。如果你想走最明确、受支持的路径，请使用Anthropic API密钥。

### Anthropic setuptoken身份验证是如何工作的

`claude setup-token` 通过Claude Code CLI生成一个 **令牌字符串**（在Web控制台中不可用）。你可以在 **任何机器** 上运行它。在向导中选择 **Anthropic令牌（粘贴setup-token）** 或使用 `openclaw models auth paste-token --provider anthropic` 粘贴它。该令牌作为 **anthropic** 提供商的身份验证配置文件存储，并像API密钥一样使用（不自动刷新）。更多详情：[OAuth](/concepts/oauth).

### 我在哪里可以找到Anthropic setuptoken

它 **不在** Anthropic控制台中。setup-token由 **Claude Code CLI** 在 **任何机器** 上生成：

```bash
claude setup-token
```

请将以下token复制，然后在向导中选择 **Anthropic token (paste setup-token)**。如果您想在网关主机上运行它，请使用 `openclaw models auth setup-token --provider anthropic`。如果您在其他地方运行了 `claude setup-token`，请将其粘贴到网关主机上并使用 `openclaw models auth paste-token --provider anthropic`。参见 [Anthropic](/providers/anthropic)。

### 您支持Claude订阅认证（Claude Pro或Max）吗？

是的 - 通过 **setup-token**。OpenClaw不再重用Claude Code CLI OAuth令牌；请使用setup-token或Anthropic API密钥。在任何地方生成令牌并将其粘贴到网关主机上。参见 [Anthropic](/providers/anthropic) 和 [OAuth](/concepts/oauth)。

注意：Claude订阅访问受Anthropic条款的约束。对于生产或多用户工作负载，API密钥通常是更安全的选择。

### 为什么我看到来自Anthropic的HTTP 429 ratelimiterror

这意味着您当前窗口内的 **Anthropic配额/速率限制** 已耗尽。如果您使用的是 **Claude订阅**（setup-token或Claude Code OAuth），请等待窗口重置或升级您的计划。如果您使用的是 **Anthropic API密钥**，请检查Anthropic控制台中的使用情况/计费，并根据需要提高限制。

提示：设置一个 **备用模型**，以便在提供商被限速时OpenClaw可以继续回复。参见 [Models](/cli/models) 和 [OAuth](/concepts/oauth)。

### 是否支持AWS Bedrock

是的 - 通过pi-ai的 **Amazon Bedrock (Converse)** 提供商使用 **手动配置**。您必须在网关主机上提供AWS凭据/区域，并在模型配置中添加Bedrock提供商条目。参见 [Amazon Bedrock](/providers/bedrock) 和 [Model providers](/providers/models)。如果您更喜欢托管密钥流，在Bedrock前面使用兼容OpenAI的代理仍然是一个有效的选项。

### Codex认证是如何工作的

OpenClaw通过OAuth（ChatGPT登录）支持 **OpenAI Code (Codex)**。向导可以运行OAuth流程，并在适当的情况下将默认模型设置为 `openai-codex/gpt-5.3-codex`。参见 [Model providers](/concepts/model-providers) 和 [Wizard](/start/wizard)。

### 您支持OpenAI订阅认证Codex OAuth吗？

是的。OpenClaw完全支持 **OpenAI Code (Codex) 订阅OAuth**。入站向导可以为您运行OAuth流程。

参见 [OAuth](/concepts/oauth)，[Model providers](/concepts/model-providers)，和 [Wizard](/start/wizard)。

### 如何设置Gemini CLI OAuth

Gemini CLI使用 **插件认证流程**，而不是在 `openclaw.json` 中使用client id或secret。

步骤：

1. 启用插件：`openclaw plugins enable google-gemini-cli-auth`
2. 登录：`openclaw models auth login --provider google-gemini-cli --set-default`

这会在网关主机上的auth配置文件中存储OAuth令牌。详情：[Model providers](/concepts/model-providers)。

### 本地模型适合随意聊天吗？

通常不需要。OpenClaw 需要大量上下文 + 强大的安全性；小卡片会截断并泄露信息。如果必须，本地运行你最大的 MiniMax M2.1 构建（LM Studio），并查看 [/gateway/local-models](/gateway/local-models)。较小/量化的模型会增加提示注入风险 - 查看 [Security](/gateway/security)。

### 如何将托管模型流量保持在特定区域

选择区域锁定的端点。OpenRouter 提供了针对 MiniMax、Kimi 和 GLM 的美国托管选项；选择美国托管的变体以保持数据在区域内。你可以通过使用 `models.mode: "merge"` 列出 Anthropic/OpenAI 等，以便在选择区域化提供商的同时保持回退选项可用。

### 我是否需要购买 Mac Mini 来安装这个

不需要。OpenClaw 运行在 macOS 或 Linux（通过 WSL2 在 Windows 上）。Mac mini 是可选的 - 有些人购买它作为始终在线的主机，但小型 VPS、家庭服务器或树莓派类设备也可以。

你只需要一台 Mac **用于仅限 macOS 的工具**。对于 iMessage，使用 [BlueBubbles](/channels/bluebubbles)（推荐）- BlueBubbles 服务器运行在任何 Mac 上，而网关可以运行在 Linux 或其他地方。如果你想要其他仅限 macOS 的工具，请在 Mac 上运行网关或配对一个 macOS 节点。

文档：[BlueBubbles](/channels/bluebubbles)，[Nodes](/nodes)，[Mac 远程模式](/platforms/mac/remote)。

### 我是否需要 Mac Mini 来支持 iMessage

你需要 **已登录 Messages 的某些 macOS 设备**。它 **不必** 是 Mac mini - 任何 Mac 都可以工作。**使用 [BlueBubbles](/channels/bluebubbles)**（推荐）来支持 iMessage - BlueBubbles 服务器运行在 macOS 上，而网关可以运行在 Linux 或其他地方。

常见设置：

- 在 Linux/VPS 上运行网关，并在任何已登录 Messages 的 Mac 上运行 BlueBubbles 服务器。
- 如果你想要最简单的单机设置，可以在 Mac 上运行所有内容。

文档：[BlueBubbles](/channels/bluebubbles)，[Nodes](/nodes)，[Mac 远程模式](/platforms/mac/remote)。

### 如果我购买 Mac Mini 来运行 OpenClaw，我可以将其连接到我的 MacBook Pro

可以。**Mac mini 可以运行网关**，而你的 MacBook Pro 可以作为 **节点**（配套设备）连接。节点不运行网关 - 它们提供该设备上的额外功能，如屏幕/摄像头/画布和 `system.run`。

常见模式：

- 网关在 Mac mini 上（始终在线）。
- MacBook Pro 运行 macOS 应用程序或节点主机，并与网关配对。
- 使用 `openclaw nodes status` / `openclaw nodes list` 查看。

文档：[Nodes](/nodes)，[Nodes CLI](/cli/nodes)。

### 我可以使用 Bun 吗

不建议使用 Bun。我们发现运行时错误，特别是在使用 WhatsApp 和 Telegram 时。使用 **Node** 来获得稳定的网关。

如果你仍然想尝试 Bun，请在非生产网关上进行，不要使用 WhatsApp/Telegram。

### Telegram 中 allowFrom 应该填写什么

`channels.telegram.allowFrom` 是 **人类发送者的 Telegram 用户 ID**（数字，推荐）或 `@username`。它不是机器人的用户名。

更安全（无第三方机器人）：

- 私信您的机器人，然后运行 `openclaw logs --follow` 并阅读 `from.id`。

官方机器人API:

- 私信您的机器人，然后调用 `https://api.telegram.org/bot<bot_token>/getUpdates` 并阅读 `message.from.id`。

第三方（隐私较低）:

- 私信 `@userinfobot` 或 `@getidsbot`。

参见 [/channels/telegram](/channels/telegram#access-control-dms--groups)。

### 多个人可以使用一个WhatsApp号码和不同的OpenClaw实例吗？

是的，通过 **多代理路由**。将每个发送者的WhatsApp **私信**（对等方 `kind: "direct"`，发送者E.164如 `+15551234567`）绑定到不同的 `agentId`，因此每个人都有自己的工作区和会话存储。回复仍然来自 **同一个WhatsApp账户**，并且私信访问控制 (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) 对于每个WhatsApp账户是全局的。参见 [多代理路由](/concepts/multi-agent) 和 [WhatsApp](/channels/whatsapp)。

### 我可以运行一个快速聊天代理和一个Opus编码代理吗？

可以。使用多代理路由：为每个代理分配默认模型，然后将入站路由（提供商账户或特定对等方）绑定到每个代理。示例配置位于 [多代理路由](/concepts/multi-agent)。另请参见 [模型](/concepts/models) 和 [配置](/gateway/configuration)。

### Homebrew在Linux上可用吗？

是的。Homebrew支持Linux（Linuxbrew）。快速设置：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
brew install <formula>
```

如果您通过systemd运行OpenClaw，请确保服务PATH包含 `/home/linuxbrew/.linuxbrew/bin`（或您的brew前缀），以便在非登录shell中解析由 `brew` 安装的工具。
最近的构建还会在Linux systemd服务中前置常见的用户bin目录（例如 `~/.local/bin`，`~/.npm-global/bin`，`~/.local/share/pnpm`，`~/.bun/bin`），并尊重 `PNPM_HOME`，`NPM_CONFIG_PREFIX`，`BUN_INSTALL`，`VOLTA_HOME`，`ASDF_DATA_DIR`，`NVM_DIR` 和 `FNM_DIR` 的设置（如果已设置）。

### 可破解的git安装和npm安装有什么区别？

- **可破解（git）安装：** 完整源码检出，可编辑，最适合贡献者。
  您可以在本地运行构建并修补代码/文档。
- **npm安装：** 全局CLI安装，无仓库，最适合“直接运行”。
  更新来自npm分发标签。

文档：[入门](/start/getting-started)，[更新](/install/updating)。

### 我以后可以在这两种安装方式之间切换吗？

可以。安装另一种风格，然后运行Doctor，使网关服务指向新的入口点。
这 **不会删除您的数据** - 它仅更改OpenClaw代码安装。您的状态
(`~/.openclaw`) 和工作区 (`~/.openclaw/workspace`) 将保持不变。

从npm → git：

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm build
openclaw doctor
openclaw gateway restart
```

从git → npm：

```bash
npm install -g openclaw@latest
openclaw doctor
openclaw gateway restart
```

Doctor 检测到网关服务入口点不匹配，并提供重写服务配置以匹配当前安装的选项（在自动化中使用 `--repair`）。

备份提示：参见[备份策略](/help/faq#whats-the-recommended-backup-strategy)。

### 我应该在我的笔记本电脑上还是VPS上运行网关

简短答案：**如果你需要24/7的可靠性，请使用VPS**。如果你想最低的摩擦并且可以接受睡眠/重启，可以在本地运行它。

**笔记本电脑（本地网关）**

- **优点：** 无需服务器费用，直接访问本地文件，实时浏览器窗口。
- **缺点：** 睡眠/网络中断 = 断开连接，操作系统更新/重启中断，必须保持唤醒状态。

**VPS / 云**

- **优点：** 始终在线，稳定网络，无笔记本电脑睡眠问题，更容易保持运行。
- **缺点：** 通常无头运行（使用截图），仅限远程文件访问，必须通过SSH进行更新。

**OpenClaw特定说明：** WhatsApp/Telegram/Slack/Mattermost（插件）/Discord 都可以从VPS正常工作。唯一的真正权衡是**无头浏览器**与可见窗口。参见[浏览器](/tools/browser)。

**推荐默认设置：** 如果你之前遇到过网关断开连接的情况，请使用VPS。当你积极使用Mac并且需要本地文件访问或带有可见浏览器的UI自动化时，本地运行很好。

### 在专用机器上运行OpenClaw有多重要

不是必需的，但**为了可靠性和隔离性而推荐**。

- **专用主机（VPS/Mac mini/Pi）：** 始终在线，较少的睡眠/重启中断，更清晰的权限，更容易保持运行。
- **共享笔记本电脑/台式机：** 完全适合测试和活跃使用，但期望在机器睡眠或更新时会有暂停。

如果你想两者兼得，将网关保留在专用主机上，并将笔记本电脑配对为**节点**用于本地屏幕/摄像头/执行工具。参见[节点](/nodes)。
有关安全指导，请阅读[安全](/gateway/security)。

### 最小VPS要求和推荐的操作系统是什么

OpenClaw很轻量级。对于基本网关+一个聊天频道：

- **绝对最小值：** 1 vCPU, 1GB 内存, ~500MB 磁盘。
- **推荐：** 1-2 vCPU, 2GB 内存或更多以备不时之需（日志、媒体、多个频道）。节点工具和浏览器自动化可能会消耗大量资源。

操作系统：使用 **Ubuntu LTS**（或其他现代Debian/Ubuntu）。Linux安装路径在那里经过最佳测试。

文档：[Linux](/platforms/linux), [VPS托管](/vps)。

### 我可以在虚拟机中运行OpenClaw吗？要求是什么

可以。将虚拟机视为VPS：它需要始终保持在线，可访问，并且有足够的内存供网关和启用的任何频道使用。

基本指南：

- **绝对最小值：** 1 vCPU, 1GB 内存。
- **推荐：** 如果运行多个频道、浏览器自动化或媒体工具，则需要2GB 内存或更多。
- **操作系统：** Ubuntu LTS 或其他现代Debian/Ubuntu。

如果您使用的是Windows，**WSL2是最简单的虚拟机风格设置**，并且具有最佳的工具兼容性。请参阅[Windows](/platforms/windows)，[VPS托管](/vps)。
如果您在虚拟机中运行macOS，请参阅[macOS虚拟机](/install/macos-vm)。

## 什么是OpenClaw？

### 一句话介绍OpenClaw

OpenClaw是一个您可以在自己的设备上运行的个人AI助手。它会在您已经使用的消息平台上回复（WhatsApp, Telegram, Slack, Mattermost (插件), Discord, Google Chat, Signal, iMessage, WebChat），并且还可以在支持的平台上进行语音+实时画布操作。**网关**是始终在线的控制平面；助手是产品。

### 价值主张是什么

OpenClaw不仅仅是“Claude的包装”。它是一个**以本地为中心的控制平面**，允许您在**自己的硬件**上运行一个功能强大的助手，可以通过您已经使用的聊天应用访问，具有状态会话、内存和工具——而无需将工作流程的控制权交给托管的SaaS。

亮点：

- **您的设备，您的数据：** 将网关运行在您想要的任何地方（Mac, Linux, VPS），并保持工作区+会话历史记录本地。
- **真实渠道，而不是网页沙箱：** WhatsApp/Telegram/Slack/Discord/Signal/iMessage等，以及支持平台上的移动语音和画布。
- **模型不可知：** 使用Anthropic, OpenAI, MiniMax, OpenRouter等，每个代理路由和故障转移。
- **仅限本地选项：** 运行本地模型，因此如果需要，**所有数据都可以保留在您的设备上**。
- **多代理路由：** 每个通道、账户或任务单独的代理，每个代理都有自己的工作区和默认设置。
- **开源且可扩展：** 检查、扩展和自托管，无需供应商锁定。

文档：[网关](/gateway)，[渠道](/channels)，[多代理](/concepts/multi-agent)，[记忆](/concepts/memory)。

### 我刚刚设置好了，我应该先做什么

好的第一个项目：

- 构建一个网站（WordPress, Shopify，或一个简单的静态站点）。
- 原型化一个移动应用（大纲、屏幕、API计划）。
- 组织文件和文件夹（清理、命名、标记）。
- 连接Gmail并自动化摘要或跟进。

它可以处理大型任务，但最好将其拆分为阶段并使用子代理进行并行工作。

### OpenClaw有哪些最常见的日常使用案例

日常胜利通常如下：

- **个人简报：** 您关心的收件箱、日历和新闻的摘要。
- **研究和草稿：** 快速研究、摘要和电子邮件或文档的第一草稿。
- **提醒和跟进：** cron或心跳驱动的提示和清单。
- **浏览器自动化：** 填写表单、收集数据和重复网页任务。
- **跨设备协调：** 从手机发送任务，让网关在服务器上运行，并通过聊天获取结果。

### OpenClaw能否帮助生成潜在客户推广广告和博客文章用于SaaS

可以用于**研究、资格认定和草稿**。它可以扫描网站、建立短名单、总结潜在客户，并撰写外展或广告副本草稿。

对于**外展或广告活动**，保持人工参与。避免发送垃圾信息，遵循当地法律法规和平台政策，并在发送之前审查所有内容。最安全的做法是让OpenClaw草拟，然后您进行审批。

文档：[安全性](/gateway/security)。

### 与Claude Code相比，OpenClaw在Web开发中的优势是什么

OpenClaw是一个**个人助理**和协调层，而不是IDE的替代品。使用Claude Code或Codex在仓库中进行最快的直接编码循环。当您需要持久化内存、跨设备访问和工具编排时使用OpenClaw。

优势：

- **跨会话的持久化内存 + 工作区**
- **多平台访问**（WhatsApp, Telegram, TUI, WebChat）
- **工具编排**（浏览器、文件、调度、钩子）
- **始终在线的网关**（运行在VPS上，从任何地方交互）
- **节点**用于本地浏览器/屏幕/摄像头/执行

展示：[https://openclaw.ai/showcase](https://openclaw.ai/showcase)

## 技能和自动化

### 如何自定义技能而不使仓库变得混乱

使用托管覆盖而不是编辑仓库副本。将您的更改放入`~/.openclaw/skills/<name>/SKILL.md`（或通过`skills.load.extraDirs`在`~/.openclaw/openclaw.json`中添加一个文件夹）。优先级为`<workspace>/skills` > `~/.openclaw/skills` > 内置，因此托管覆盖无需接触git即可生效。只有值得上游合并的更改应保留在仓库中并通过PR发布。

### 我可以从自定义文件夹加载技能吗

可以。通过在`~/.openclaw/openclaw.json`中使用`skills.load.extraDirs`添加额外目录（最低优先级）。默认优先级保持不变：`<workspace>/skills` → `~/.openclaw/skills` → 内置 → `skills.load.extraDirs`。`clawhub`默认安装到`./skills`，OpenClaw将其视为`<workspace>/skills`。

### 如何为不同的任务使用不同的模型

目前支持的模式有：

- **Cron作业**：隔离的任务可以为每个作业设置`model`覆盖。
- **子代理**：将任务路由到具有不同默认模型的单独代理。
- **按需切换**：使用`/model`随时切换当前会话的模型。

参见[Cron作业](/automation/cron-jobs)，[多代理路由](/concepts/multi-agent)，和[斜杠命令](/tools/slash-commands)。

### 机器人在执行繁重任务时冻结了，我该如何卸载这些任务

使用**子代理**处理长时间或并行任务。子代理在其自己的会话中运行，返回摘要，并保持主聊天响应迅速。

请求您的机器人“为此任务生成一个子代理”或使用`/subagents`。
使用`/status`在聊天中查看网关当前正在做什么（以及它是否繁忙）。

令牌提示：长时间任务和子代理都会消耗令牌。如果成本是问题，请通过`agents.defaults.subagents.model`为子代理设置更便宜的模型。

文档：[子代理](/tools/subagents)。

### Cron或提醒未触发，我应该检查什么

Cron在网关进程中运行。如果网关没有连续运行，计划的任务将不会运行。

检查清单：

- 确认 cron 已启用 (`cron.enabled`) 并且 `OPENCLAW_SKIP_CRON` 未设置。
- 检查 Gateway 是否 24/7 运行（无休眠/重启）。
- 验证作业 (`--tz`) 的时区设置与主机时区一致。

调试：

```bash
openclaw cron run <jobId> --force
openclaw cron runs --id <jobId> --limit 50
```

文档：[Cron 作业](/automation/cron-jobs)，[Cron vs 心跳](/automation/cron-vs-heartbeat)。

### 如何在 Linux 上安装技能

使用 **ClawHub** (CLI) 或将技能放入工作区。macOS 技能 UI 在 Linux 上不可用。
浏览技能：[https://clawhub.com](https://clawhub.com)。

安装 ClawHub CLI（选择一个包管理器）：

```bash
npm i -g clawhub
```

```bash
pnpm add -g clawhub
```

### OpenClaw 能否按计划或在后台连续运行任务？

可以。使用 Gateway 调度器：

- **Cron 作业** 用于计划或重复任务（重启后持久化）。
- **心跳** 用于“主会话”定期检查。
- **隔离作业** 用于自主代理发布摘要或发送到聊天。

文档：[Cron 作业](/automation/cron-jobs)，[Cron vs 心跳](/automation/cron-vs-heartbeat)，[心跳](/gateway/heartbeat)。

### 我能否从 Linux 运行仅限 Apple macOS 的技能？

不能直接。macOS 技能受 `metadata.openclaw.os` 加载限制以及所需的二进制文件，并且只有在 **Gateway 主机** 上有资格时才会出现在系统提示中。在 Linux 上，仅限 `darwin` 的技能（如 `apple-notes`，`apple-reminders`，`things-mac`）除非覆盖加载限制否则不会加载。

您有三种支持的模式：

**选项 A - 在 Mac 上运行 Gateway（最简单）。**
在包含 macOS 二进制文件的地方运行 Gateway，然后通过 [远程模式](#如何在远程模式下运行-openclaw-客户端连接到其他位置的-gateway) 或 Tailscale 从 Linux 连接。由于 Gateway 主机是 macOS，技能会正常加载。

**选项 B - 使用 macOS 节点（无需 SSH）。**
在 Linux 上运行 Gateway，配对一个 macOS 节点（菜单栏应用），并在 Mac 上将 **节点运行命令** 设置为“始终询问”或“始终允许”。OpenClaw 可以在节点上存在所需二进制文件时将仅限 macOS 的技能视为有资格。代理通过 `nodes` 工具运行这些技能。如果您选择“始终询问”，则在提示中批准“始终允许”会将该命令添加到允许列表。

**选项 C - 通过 SSH 代理 macOS 二进制文件（高级）。**
保持 Gateway 在 Linux 上，但使所需的 CLI 二进制文件解析为在 Mac 上运行的 SSH 包装器。然后覆盖技能以允许 Linux 使其保持有资格。

1. 为二进制文件创建 SSH 包装器（示例：`memo` 用于 Apple Notes）：

   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
   ```

2. 将包装器放在 Linux 主机上的 `PATH`（例如 `~/bin/memo`）。
3. 覆盖技能元数据（工作区或 `~/.openclaw/skills`）以允许 Linux：

```markdown
   ---
   name: apple-notes
   description: Manage Apple Notes via the memo CLI on macOS.
   metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
   ---
   ```

4. 启动一个新会话以便技能快照刷新。

### 您是否有 Notion 或 HeyGen 集成

今天尚未内置。

选项：

- **自定义技能 / 插件：** 最适合可靠的 API 访问（Notion/HeyGen 均提供 API）。
- **浏览器自动化：** 不需要代码即可工作，但速度较慢且更脆弱。

如果您希望按客户保持上下文（适用于代理工作流），一个简单的模式是：

- 每个客户一个 Notion 页面（上下文 + 首选项 + 活动工作）。
- 要求代理在会话开始时获取该页面。

如果您希望原生集成，请提交功能请求或针对这些 API 构建一个技能。

安装技能：

```bash
clawhub install <skill-slug>
clawhub update --all
```

ClawHub 安装到当前目录下的 `./skills`（或回退到您配置的 OpenClaw 工作区）；OpenClaw 在下次会话中将其视为 `<workspace>/skills`。对于跨代理共享的技能，请将它们放在 `~/.openclaw/skills/<name>/SKILL.md`。某些技能期望通过 Homebrew 安装的二进制文件；在 Linux 上这意味着 Linuxbrew（参见上述 Homebrew Linux 常见问题条目）。参阅 [Skills](/tools/skills) 和 [ClawHub](/tools/clawhub)。

### 如何安装 Chrome 扩展以接管浏览器

使用内置安装程序，然后在 Chrome 中加载未打包的扩展：

```bash
openclaw browser extension install
openclaw browser extension path
```

然后 Chrome → `chrome://extensions` → 启用“开发者模式” → “加载已解压” → 选择该文件夹。

完整指南（包括远程网关 + 安全说明）：[Chrome 扩展](/tools/chrome-extension)

如果网关与 Chrome 运行在同一台机器上（默认设置），通常**不需要**额外内容。
如果网关运行在其他地方，请在浏览器机器上运行一个节点主机，以便网关可以代理浏览器操作。
您仍然需要点击要控制的标签页上的扩展按钮（它不会自动附加）。

## 沙箱化和内存

### 是否有专门的沙箱化文档

是。参阅 [Sandboxing](/gateway/sandboxing)。有关 Docker 特定设置（完整的网关在 Docker 或沙盒镜像中），参阅 [Docker](/install/docker)。

### Docker 感觉受限，如何启用全部功能

默认镜像是安全优先的，并以 `node` 用户身份运行，因此不包含系统包、Homebrew 或捆绑的浏览器。为了更完整的设置：

- 使用 `OPENCLAW_HOME_VOLUME` 持久化 `/home/node` 以便缓存得以保留。
- 使用 `OPENCLAW_DOCKER_APT_PACKAGES` 将系统依赖项烘焙到镜像中。
- 通过捆绑的 CLI 安装 Playwright 浏览器：
  `node /app/node_modules/playwright-core/cli.js install chromium`
- 设置 `PLAYWRIGHT_BROWSERS_PATH` 并确保路径得以持久化。

文档：[Docker](/install/docker)，[Browser](/tools/browser)。

**我可以保持 DM 个人化但使组公开沙盒化并使用一个代理吗**

是 - 如果您的私人流量是 **DMs** 而公共流量是 **groups**。

使用 `agents.defaults.sandbox.mode: "non-main"` 使组/频道会话（非主密钥）在Docker中运行，而主DM会话保留在主机上。然后通过 `tools.sandbox.tools` 限制沙盒会话中可用的工具。

设置指南 + 示例配置：[Groups: personal DMs + public groups](/channels/groups#pattern-personal-dms-public-groups-single-agent)

关键配置参考：[Gateway configuration](/gateway/configuration#agentsdefaultssandbox)

### 如何将主机文件夹绑定到沙盒

将 `agents.defaults.sandbox.docker.binds` 设置为 `["host:path:mode"]`（例如，`"/home/user/src:/src:ro"`）。全局和每个代理的绑定会合并；当 `scope: "shared"` 时，忽略每个代理的绑定。使用 `:ro` 绑定任何敏感内容，并记住绑定会绕过沙盒文件系统墙。参见 [Sandboxing](/gateway/sandboxing#custom-bind-mounts) 和 [Sandbox vs Tool Policy vs Elevated](/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) 获取示例和安全注意事项。

### 内存是如何工作的

OpenClaw 内存只是代理工作区中的 Markdown 文件：

- 每日笔记在 `memory/YYYY-MM-DD.md`
- 精选的长期笔记在 `MEMORY.md`（仅主/私有会话）

OpenClaw 还运行一个 **静默预压缩内存刷新** 来提醒模型在自动压缩之前写入持久化笔记。这仅在工作区可写时运行（只读沙盒会跳过此步骤）。参见 [Memory](/concepts/memory)。

### 内存总是忘记事情，如何让它记住

要求机器人将 **事实写入内存**。长期笔记属于 `MEMORY.md`，短期上下文进入 `memory/YYYY-MM-DD.md`。

这仍然是我们正在改进的领域。提醒模型存储记忆有助于；它会知道该做什么。如果它仍然忘记，请验证 Gateway 在每次运行时是否使用相同的 工作区。

文档：[Memory](/concepts/memory)，[Agent workspace](/concepts/agent-workspace)。

### 语义记忆搜索是否需要 OpenAI API 密钥

仅当您使用 **OpenAI embeddings** 时需要。Codex OAuth 覆盖聊天/补全，但 **不** 授予嵌入访问权限，因此 **使用 Codex 登录（OAuth 或 Codex CLI 登录）** 对于语义记忆搜索没有帮助。OpenAI embeddings 仍然需要一个真实的 API 密钥 (`OPENAI_API_KEY` 或 `models.providers.openai.apiKey`)。

如果您没有显式设置提供者，OpenClaw 会在能够解析 API 密钥时自动选择一个提供者（身份验证配置文件，`models.providers.*.apiKey` 或环境变量）。
如果有 OpenAI 密钥解析，则优先选择 OpenAI；否则如果有 Gemini 密钥解析，则选择 Gemini。如果没有密钥可用，则内存搜索将保持禁用状态，直到您进行配置。如果您配置并存在本地模型路径，OpenClaw 优先选择 `local`。

如果您希望保持本地化，请设置 `memorySearch.provider = "local"`（并可选地设置
`memorySearch.fallback = "none"`）。如果您想要Gemini嵌入，请设置
`memorySearch.provider = "gemini"`并提供`GEMINI_API_KEY`（或
`memorySearch.remote.apiKey`）。我们支持 **OpenAI, Gemini, 或本地** 嵌入模型 - 请参阅[Memory](/concepts/memory)获取设置详细信息。

### 记忆是否永久存在 有什么限制

记忆文件存储在磁盘上，直到您删除它们为止。限制在于您的存储空间，而不是模型。**会话上下文**仍然受限于模型的上下文窗口，因此长时间的对话可能会被压缩或截断。这就是为什么存在记忆搜索 - 它只会将相关部分拉回到上下文中。

文档: [Memory](/concepts/memory), [Context](/concepts/context).

## 数据存储位置

### 使用OpenClaw的所有数据是否都保存在本地

不 - **OpenClaw的状态是本地的**，但**外部服务仍然能看到您发送给它们的内容**。

- **默认本地：** 会话、记忆文件、配置和工作区存储在网关主机上
  (`~/.openclaw` + 您的工作区目录)。
- **必要时远程：** 您发送给模型提供商（Anthropic/OpenAI等）的消息会发送到
  他们的API，而聊天平台（WhatsApp/Telegram/Slack等）会在其服务器上存储消息数据。
- **您控制占用空间：** 使用本地模型会使提示保留在您的机器上，但频道流量仍然会通过频道的服务器。

相关: [Agent workspace](/concepts/agent-workspace), [Memory](/concepts/memory).

### OpenClaw将其数据存储在哪里

所有内容都存储在 `$OPENCLAW_STATE_DIR` 下（默认: `~/.openclaw`）：

| 路径                                                            | 目的                                                      |
| --------------------------------------------------------------- | ------------------------------------------------------------ |
| `$OPENCLAW_STATE_DIR/openclaw.json`                             | 主配置（JSON5）                                          |
| `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | 旧版OAuth导入（首次使用时复制到身份验证配置文件中） |
| `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | 身份验证配置文件（OAuth + API密钥）                             |
| `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | 运行时身份验证缓存（自动管理）                   |
| `$OPENCLAW_STATE_DIR/credentials/`                              | 提供程序状态（例如 `whatsapp/<accountId>/creds.json`)      |
| `$OPENCLAW_STATE_DIR/agents/`                                   | 每个代理的状态（agentDir + 会话）                        |
| `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | 对话历史记录和状态（每个代理）                     |
| `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | 会话元数据（每个代理）                                 |

旧版单代理路径: `~/.openclaw/agent/*` (迁移自 `openclaw doctor`).

您的 **workspace** (AGENTS.md, 内存文件, 技能等) 是独立的，并通过 `agents.defaults.workspace` 配置 (默认: `~/.openclaw/workspace`).

### AGENTSmd SOULmd USERmd MEMORYmd 应该存放在哪里

这些文件存放在 **代理工作区** 中，而不是 `~/.openclaw`.

- **工作区 (每个代理)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
  `MEMORY.md` (或 `memory.md`), `memory/YYYY-MM-DD.md`, 可选 `HEARTBEAT.md`.
- **状态目录 (`~/.openclaw`)**: 配置, 凭证, 认证配置文件, 会话, 日志,
  和共享技能 (`~/.openclaw/skills`).

默认工作区是 `~/.openclaw/workspace`，可通过以下方式配置:

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

如果机器人在重启后“忘记了”某些内容，请确认网关在每次启动时使用相同的工作区（并记住：远程模式使用的是 **网关主机** 的工作区，而不是您的本地笔记本电脑）。

提示: 如果您希望行为或偏好具有持久性，请让机器人将其 **写入 AGENTS.md 或 MEMORY.md** 而不是依赖聊天历史记录。

参见 [代理工作区](/concepts/agent-workspace) 和 [内存](/concepts/memory).

### 推荐的备份策略是什么

将您的 **代理工作区** 放在一个 **私有** 的 git 仓库中，并将其备份到某个私有位置（例如 GitHub 私有仓库）。这将捕获内存 + AGENTS/SOUL/USER 文件，并允许您稍后恢复助手的“思维”。

**不要** 提交 `~/.openclaw` 下的任何内容（凭证, 会话, 令牌）。如果您需要完整恢复，请分别备份工作区和状态目录（参见上面的迁移问题）。

文档: [代理工作区](/concepts/agent-workspace).

### 如何完全卸载 OpenClaw

请参阅专用指南: [卸载](/install/uninstall).

### 代理可以在工作区之外工作吗

可以。工作区是 **默认的当前工作目录** 和内存锚点，而不是硬沙盒。相对路径在工作区内解析，但绝对路径可以访问其他主机位置，除非启用了沙盒。如果您需要隔离，请使用 [`agents.defaults.sandbox`](/gateway/sandboxing) 或每个代理的沙盒设置。如果您希望一个仓库成为默认的工作目录，请将该代理的 `workspace` 指向仓库根目录。OpenClaw 仓库只是源代码；除非有意让代理在其内部工作，否则请保持工作区独立。

示例（仓库作为默认当前工作目录）:

```json5
{
  agents: {
    defaults: {
      workspace: "~/Projects/my-repo",
    },
  },
}
```

### 我在远程模式下，会话存储在哪里

会话状态由 **网关主机** 拥有。如果您处于远程模式，您关心的会话存储在远程机器上，而不是您的本地笔记本电脑。参见 [会话管理](/concepts/session).

## 配置基础

### 配置的格式是什么？它在哪里

OpenClaw 从 `$OPENCLAW_CONFIG_PATH` 读取可选的 **JSON5** 配置（默认: `~/.openclaw/openclaw.json`）:

```
$OPENCLAW_CONFIG_PATH
```

如果文件丢失，它会使用安全的默认值（包括默认工作区 `~/.openclaw/workspace`）。

### 我设置了 gatewaybind lan 或 tailnet 现在没有任何进程监听 UI 显示未授权

非回环绑定 **需要认证**。配置 `gateway.auth.mode` + `gateway.auth.token`（或使用 `OPENCLAW_GATEWAY_TOKEN`）。

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

注意：

- `gateway.remote.token` 仅用于 **远程 CLI 调用**；它不会启用本地网关认证。
- 控制 UI 通过 `connect.params.auth.token`（存储在 app/UI 设置中）进行身份验证。避免在 URL 中放置令牌。

### 为什么我现在需要在 localhost 上使用令牌

向导默认生成一个网关令牌（即使在回环上），因此 **本地 WS 客户端必须进行身份验证**。这阻止了其他本地进程调用网关。将令牌粘贴到控制 UI 设置（或您的客户端配置）中以连接。

如果您 **确实** 想要开放回环，请从配置中移除 `gateway.auth`。Doctor 可以随时为您生成令牌：`openclaw doctor --generate-gateway-token`。

### 更改配置后是否需要重启

网关监视配置并支持热重载：

- `gateway.reload.mode: "hybrid"`（默认）：热应用安全更改，关键更改时重启
- 支持 `hot`，`restart`，`off`

### 如何启用 Web 搜索和 Web 获取

`web_fetch` 不需要 API 密钥即可工作。`web_search` 需要 Brave Search API 密钥。**推荐**：运行 `openclaw configure --section web` 将其存储在 `tools.web.search.apiKey` 中。环境替代方案：为网关进程设置 `BRAVE_API_KEY`。

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

注意：

- 如果您使用允许列表，请添加 `web_search`/`web_fetch` 或 `group:web`。
- 默认情况下启用 `web_fetch`（除非显式禁用）。
- 守护程序从 `~/.openclaw/.env`（或服务环境）读取环境变量。

文档：[Web 工具](/tools/web)。

### 如何在设备间运行中央网关和专用工作者

常见模式是 **一个网关**（例如 Raspberry Pi）加上 **节点** 和 **代理**：

- **网关（中央）：** 拥有通道（Signal/WhatsApp）、路由和会话。
- **节点（设备）：** Macs/iOS/Android 作为外设连接并暴露本地工具 (`system.run`，`canvas`，`camera`)。
- **代理（工作者）：** 为特殊角色（例如 "Hetzner ops"，"个人数据"）提供独立的大脑/工作区。
- **子代理：** 当您需要并行性时，从主代理生成后台工作。
- **TUI：** 连接到网关并切换代理/会话。

文档：[节点](/nodes)，[远程访问](/gateway/remote)，[多代理路由](/concepts/multi-agent)，[子代理](/tools/subagents)，[TUI](/web/tui)。

### OpenClaw 浏览器可以无头运行吗

是的。这是一个配置选项：

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

默认值是 `false`（有头模式）。无头模式更有可能在某些网站上触发反机器人检查。请参阅 [Browser](/tools/browser)。

无头模式使用 **相同的Chromium引擎**，适用于大多数自动化任务（表单填写、点击、抓取、登录）。主要区别在于：

- 没有可见的浏览器窗口（如果需要视觉效果，请使用截图）。
- 某些网站对无头模式下的自动化更加严格（验证码、反机器人）。
  例如，X/Twitter经常阻止无头会话。

### 如何使用Brave进行浏览器控制

将 `browser.executablePath` 设置为您的Brave二进制文件（或任何基于Chromium的浏览器），然后重启网关。
请参阅 [Browser](/tools/browser#use-brave-or-another-chromium-based-browser) 中的完整配置示例。

## 远程网关和节点

### Telegram网关和节点之间命令如何传播

Telegram消息由 **网关** 处理。网关运行代理程序，并且仅在需要节点工具时通过 **网关WebSocket** 调用节点：

Telegram → 网关 → 代理程序 → `node.*` → 节点 → 网关 → Telegram

节点看不到传入的提供商流量；它们只接收节点RPC调用。

### 如果我的网关托管在远程位置，我的代理程序如何访问我的计算机

简短答案：**将您的计算机配对为节点**。网关运行在其他地方，但它可以通过网关WebSocket在本地机器上调用 `node.*` 工具（屏幕、摄像头、系统）。

典型设置：

1. 在始终在线的主机（VPS/家庭服务器）上运行网关。
2. 将网关主机和您的计算机放在同一个tailnet上。
3. 确保网关WS可达（tailnet绑定或SSH隧道）。
4. 在本地打开macOS应用程序并以 **通过SSH远程** 模式连接（或直接tailnet），以便它可以注册为节点。
5. 在网关上批准该节点：

   ```bash
   openclaw nodes pending
   openclaw nodes approve <requestId>
   ```

不需要单独的TCP桥接；节点通过网关WebSocket连接。

安全提醒：将macOS节点配对允许 `system.run` 在该机器上运行。仅配对您信任的设备，并查看 [Security](/gateway/security)。

文档：[Nodes](/nodes)，[网关协议](/gateway/protocol)，[macOS远程模式](/platforms/mac/remote)，[Security](/gateway/security)。

### Tailscale已连接但没有收到回复怎么办

检查基本事项：

- 网关正在运行：`openclaw gateway status`
- 网关健康状况：`openclaw status`
- 通道健康状况：`openclaw channels status`

然后验证身份验证和路由：

- 如果您使用Tailscale Serve，请确保 `gateway.auth.allowTailscale` 设置正确。
- 如果您通过SSH隧道连接，请确认本地隧道已启动并且指向正确的端口。
- 确认您的允许列表（直接消息或群组）包含您的账户。

文档：[Tailscale](/gateway/tailscale)，[远程访问](/gateway/remote)，[Channels](/channels)。

### 两个OpenClaw实例能否在本地VPS之间通信

可以。没有内置的“机器人到机器人”桥接，但你可以通过几种可靠的方式实现：

**最简单：** 使用两个机器人都可以访问的正常聊天频道（Telegram/Slack/WhatsApp）。
让机器人A发送消息给机器人B，然后让机器人B像往常一样回复。

**CLI桥接（通用）：** 运行一个脚本，调用另一个网关的`openclaw agent --message ... --deliver`，目标是一个其他机器人
监听的聊天。如果一个机器人在远程VPS上，通过SSH/Tailscale指向该远程网关
（参见[远程访问](/gateway/remote)）。

示例模式（从可以访问目标网关的机器运行）：

```bash
openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
```

提示：添加一个防护措施，防止两个机器人无限循环（仅提及、频道白名单或“不回复机器人消息”的规则）。

文档：[远程访问](/gateway/remote)，[代理CLI](/cli/agent)，[代理发送](/tools/agent-send)。

### 多个代理是否需要单独的VPS

不需要。一个网关可以托管多个代理，每个代理都有自己的工作区、模型默认设置
和路由。这是正常的设置，并且比每个代理运行一个VPS更便宜和简单。

仅在需要硬隔离（安全边界）或非常不同的配置而不希望共享时使用单独的VPS。
否则，保持一个网关并使用多个代理或子代理。

### 在个人笔记本电脑上使用节点而不是从VPS通过SSH是否有好处

是的 - 节点是从远程网关访问笔记本电脑的第一类方式，并且它们
解锁了不仅仅是shell访问。网关运行在macOS/Linux（通过WSL2在Windows上）并且
轻量级（一个小的VPS或树莓派级别的盒子就足够；4GB内存绰绰有余），因此常见的
设置是一个始终在线的主机加上笔记本电脑作为节点。

- **无需入站SSH。** 节点连接到网关WebSocket并使用设备配对。
- **更安全的执行控制。** `system.run`受该笔记本电脑上的节点允许列表/批准的限制。
- **更多设备工具。** 节点除了`system.run`之外还暴露`canvas`，`camera`，和`screen`。
- **本地浏览器自动化。** 将网关保留在VPS上，但在本地运行Chrome并通过Chrome扩展+笔记本电脑上的节点主机进行控制传递。

SSH适合临时shell访问，但节点更适合持续的代理工作流程和
设备自动化。

文档：[节点](/nodes)，[节点CLI](/cli/nodes)，[Chrome扩展](/tools/chrome-extension)。

### 我应该在第二台笔记本电脑上安装还是只添加一个节点

如果你只需要第二台笔记本电脑上的**本地工具**（屏幕/摄像头/执行），将其作为
**节点**添加。这保持了一个网关并避免了配置重复。当前本地节点工具仅限macOS，
但我们计划将其扩展到其他操作系统。

仅在需要**硬隔离**或两个完全独立的机器人时才安装第二个网关。

文档: [节点](/nodes), [节点 CLI](/cli/nodes), [多个网关](/gateway/multiple-gateways).

### 节点是否运行网关服务

不，每个主机上**只应运行一个网关**，除非你有意运行隔离的配置文件（参见[多个网关](/gateway/multiple-gateways)）。节点是连接到网关的外设（iOS/Android 节点，或 macOS 的“节点模式”菜单栏应用）。对于无头节点主机和 CLI 控制，请参阅[节点主机 CLI](/cli/node)。

对于 `gateway`、`discovery` 和 `canvasHost` 的更改需要完全重启。

### 是否有 API RPC 方法来应用配置

是的。`config.apply` 验证并写入完整配置，并作为操作的一部分重启网关。

### configapply 清除了我的配置，我该如何恢复并避免这种情况

`config.apply` 替换**整个配置**。如果你发送一个部分对象，其他所有内容都会被移除。

恢复：

- 从备份中恢复（git 或复制的 `~/.openclaw/openclaw.json`）。
- 如果没有备份，重新运行 `openclaw doctor` 并重新配置通道/模型。
- 如果这是意外情况，请提交一个错误报告并包括你的最后一个已知配置或任何备份。
- 本地编码代理通常可以从日志或历史记录中重建一个有效的配置。

避免这种情况：

- 使用 `openclaw config set` 进行小更改。
- 使用 `openclaw configure` 进行交互式编辑。

文档: [配置](/cli/config), [配置](/cli/configure), [诊断](/gateway/doctor).

### 第一次安装的最小合理配置是什么

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

这设置了你的工作区并限制谁可以触发机器人。

### 如何在 VPS 上设置 Tailscale 并从我的 Mac 连接

最小步骤：

1. **在 VPS 上安装并登录**

   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```

2. **在你的 Mac 上安装并登录**
   - 使用 Tailscale 应用并登录到同一个 tailnet。
3. **启用 MagicDNS（推荐）**
   - 在 Tailscale 管理控制台中启用 MagicDNS，以便 VPS 具有稳定的名称。
4. **使用 tailnet 主机名**
   - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
   - 网关 WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

如果你想在没有 SSH 的情况下使用控制 UI，请在 VPS 上使用 Tailscale Serve：

```bash
openclaw gateway --tailscale serve
```

这将网关绑定到回环，并通过 Tailscale 暴露 HTTPS。参见 [Tailscale](/gateway/tailscale)。

### 如何将 Mac 节点连接到远程网关 Tailscale Serve

Serve 暴露了**网关控制 UI + WS**。节点通过相同的网关 WS 终端连接。

推荐设置：

1. **确保 VPS 和 Mac 在同一个 tailnet 上**。
2. **在远程模式下使用 macOS 应用**（SSH 目标可以是 tailnet 主机名）。
   该应用将隧道网关端口并作为节点连接。
3. **在网关上批准节点**：

   ```bash
   openclaw nodes pending
   openclaw nodes approve <requestId>
   ```

文档: [网关协议](/gateway/protocol), [发现](/gateway/discovery), [macOS 远程模式](/platforms/mac/remote).

## 环境变量和 .env 加载

### OpenClaw 如何加载环境变量

OpenClaw 从父进程（shell、launchd/systemd、CI 等）读取环境变量，并且额外加载：

- `.env` 从当前工作目录
- 全局回退 `.env` 从 `~/.openclaw/.env`（即 `$OPENCLAW_STATE_DIR/.env`）

`.env` 文件不会覆盖现有的环境变量。

你也可以在配置中定义内联环境变量（仅在进程环境缺失时应用）：

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
  },
}
```

详见 [/environment](/help/environment) 获取完整的优先级和来源。

### 我通过服务启动了网关，我的环境变量消失了怎么办

两个常见的解决方法：

1. 将缺失的键放入 `~/.openclaw/.env`，以便即使服务没有继承你的 shell 环境也能被拾取。
2. 启用 shell 导入（可选便利功能）：

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

这会运行你的登录 shell 并仅导入预期的缺失键（从不覆盖）。环境变量等效项：
`OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`。

### 我设置了 COPILOTGITHUBTOKEN 但模型状态显示 Shell env off 为什么

`openclaw models status` 报告是否启用了 **shell env 导入**。“Shell env: off”
并不意味着你的环境变量丢失——它只是意味着 OpenClaw 不会自动加载你的登录 shell。

如果网关作为服务（launchd/systemd）运行，它不会继承你的 shell 环境。通过以下方法之一修复：

1. 将令牌放入 `~/.openclaw/.env`：

   ```
   COPILOT_GITHUB_TOKEN=...
   ```

2. 或启用 shell 导入 (`env.shellEnv.enabled: true`)。
3. 或将其添加到你的配置 `env` 块（仅在缺失时应用）。

然后重启网关并重新检查：

```bash
openclaw models status
```

Copilot 令牌从 `COPILOT_GITHUB_TOKEN` 读取（也包括 `GH_TOKEN` / `GITHUB_TOKEN`）。
详见 [/concepts/model-providers](/concepts/model-providers) 和 [/environment](/help/environment)。

## 会话和多个聊天

### 如何开始一个新的对话

发送 `/new` 或 `/reset` 作为独立消息。详见 [会话管理](/concepts/session)。

### 如果我从未发送新消息，会话是否会自动重置

是的。会话在 `session.idleMinutes` 后过期（默认 **60** 分钟）。**下一个**
消息会为该聊天键启动一个新的会话 ID。这不会删除记录——它只是启动一个新会话。

```json5
{
  session: {
    idleMinutes: 240,
  },
}
```

### 是否有一种方法可以创建一个 OpenClaw 实例团队，一个 CEO 和许多代理

是的，通过 **多代理路由** 和 **子代理**。你可以创建一个协调器代理和几个具有自己工作区和模型的工作代理。

也就是说，这最好被视为一个**有趣的实验**。它消耗大量的token，并且通常不如使用一个带有独立会话的机器人高效。我们设想的典型模型是一个你可以对话的机器人，对于并行工作使用不同的会话。该机器人在需要时还可以生成子代理。

文档：[多代理路由](/concepts/multi-agent), [子代理](/tools/subagents), [代理CLI](/cli/agents)。

### 为什么上下文在任务中途被截断 如何防止

会话上下文受模型窗口限制。长时间的聊天、大型工具输出或许多文件可能会触发压缩或截断。

有帮助的方法：

- 让机器人总结当前状态并将其写入文件。
- 在长任务之前使用`/compact`，并在切换话题时使用`/new`。
- 将重要上下文保留在工作区，并让机器人读取它。
- 使用子代理进行长时间或并行工作，以使主要聊天保持较小。
- 如果这种情况经常发生，请选择具有更大上下文窗口的模型。

### 如何完全重置OpenClaw但保留安装

使用重置命令：

```bash
openclaw reset
```

非交互式完整重置：

```bash
openclaw reset --scope full --yes --non-interactive
```

然后重新运行引导程序：

```bash
openclaw onboard --install-daemon
```

注意：

- 如果引导程序发现现有配置，它也会提供**重置**选项。参见[向导](/start/wizard)。
- 如果你使用了配置文件(`--profile` / `OPENCLAW_PROFILE`)，请重置每个状态目录（默认值为`~/.openclaw-<profile>`）。
- 开发者重置：`openclaw gateway --dev --reset`（仅限开发人员；清除开发配置+凭据+会话+工作区）。

### 我收到上下文太大的错误如何重置或压缩

使用以下方法之一：

- **压缩**（保留对话但总结较旧的部分）：

  ```
  /compact
  ```

  或使用`/compact <instructions>`来指导摘要。

- **重置**（相同的聊天密钥的新会话ID）：

  ```
  /new
  /reset
  ```

如果这种情况持续发生：

- 启用或调整**会话修剪**(`agents.defaults.contextPruning`)以修剪旧的工具输出。
- 使用具有更大上下文窗口的模型。

文档：[压缩](/concepts/compaction), [会话修剪](/concepts/session-pruning), [会话管理](/concepts/session)。

### 为什么我看到LLM请求被拒绝的消息 NcontentXtooluseinput 字段必需

这是一个提供商验证错误：模型发出一个`tool_use`块而没有必需的`input`。通常这意味着会话历史过时或已损坏（通常在长时间线程之后或工具/模式更改后）。

解决方法：使用`/new`启动一个新的会话（独立消息）。

### 为什么我每30分钟收到一次心跳消息

心跳默认每**30分钟**运行一次。调整或禁用它们：

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

如果 `HEARTBEAT.md` 存在但实际上是空的（只有空白行和markdown标题如 `# Heading`），OpenClaw 将跳过心跳运行以节省API调用。如果文件丢失，心跳仍然会运行，模型将决定如何处理。

每个代理的覆盖使用 `agents.list[].heartbeat`。文档：[Heartbeat](/gateway/heartbeat)。

### 我需要将机器人账户添加到WhatsApp群组吗？

不需要。OpenClaw 运行在 **您自己的账户** 上，因此如果您在群组中，OpenClaw 可以看到它。
默认情况下，群组回复会被阻止，直到您允许发件人 (`groupPolicy: "allowlist"`)。

如果您希望只有 **您** 能够触发群组回复：

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

### 如何获取WhatsApp群组的JID

选项1（最快）：跟踪日志并在群组中发送测试消息：

```bash
openclaw logs --follow --json
```

查找以 `@g.us` 结尾的 `chatId`（或 `from`），例如：
`1234567890-1234567890@g.us`。

选项2（如果已经配置/白名单）：从配置中列出群组：

```bash
openclaw directory groups list --channel whatsapp
```

文档：[WhatsApp](/channels/whatsapp)，[Directory](/cli/directory)，[Logs](/cli/logs)。

### 为什么OpenClaw不在群组中回复

两个常见原因：

- 提及门控已开启（默认）。您必须@提及机器人（或匹配 `mentionPatterns`）。
- 您配置了 `channels.whatsapp.groups` 而没有 `"*"` 并且群组未被白名单。

参见 [Groups](/channels/groups) 和 [Group messages](/channels/group-messages)。

### 群组线程是否与DM共享上下文

直接聊天默认合并到主会话中。群组/频道有自己的会话密钥，并且Telegram主题/Discord线程是独立的会话。参见 [Groups](/channels/groups) 和 [Group messages](/channels/group-messages)。

### 我可以创建多少个工作区和代理

没有硬性限制。几十个（甚至几百个）都可以，但请注意：

- **磁盘增长：** 会话+对话记录位于 `~/.openclaw/agents/<agentId>/sessions/` 下。
- **令牌成本：** 更多代理意味着更多的并发模型使用。
- **运维开销：** 每个代理的身份验证配置文件、工作区和渠道路由。

提示：

- 每个代理保持一个 **活跃** 的工作区 (`agents.defaults.workspace`)。
- 如果磁盘增长，请清理旧会话（删除JSONL或存储条目）。
- 使用 `openclaw doctor` 发现孤立的工作区和配置文件不匹配。

### 我可以同时运行多个机器人或聊天吗？Slack应该如何设置

可以。使用 **Multi-Agent Routing** 来运行多个隔离的代理并通过渠道/账户/对等点路由传入消息。Slack 作为渠道受支持，并可以绑定到特定代理。

浏览器访问功能强大但不是“人类能做的一切”——反机器人、CAPTCHA和MFA仍然可以阻止自动化。为了最可靠的浏览器控制，请在运行浏览器的机器上使用Chrome扩展中继（并将网关放在任何地方）。

最佳实践设置：

- 始终开启的网关主机 (VPS/Mac mini)。
- 每个角色一个代理（绑定）。
- 绑定到这些代理的 Slack 频道。
- 根据需要通过扩展中继（或节点）使用本地浏览器。

文档: [Multi-Agent Routing](/concepts/multi-agent), [Slack](/channels/slack),
[Browser](/tools/browser), [Chrome extension](/tools/chrome-extension), [Nodes](/nodes).

## 模型：默认设置、选择、别名、切换

### 默认模型是什么

OpenClaw 的默认模型是你设置的：

```
agents.defaults.model.primary
```

模型被引用为 `provider/model`（示例：`anthropic/claude-opus-4-6`）。如果你省略了提供商，OpenClaw 目前假定 `anthropic` 作为临时弃用回退——但你应该仍然**显式地**设置 `provider/model`。

### 你推荐使用哪种模型

**推荐默认设置:** `anthropic/claude-opus-4-6`。
**良好替代方案:** `anthropic/claude-sonnet-4-5`。
**可靠（较少字符):** `openai/gpt-5.2` - 几乎与 Opus 一样好，只是个性较少。
**预算:** `zai/glm-4.7`。

MiniMax M2.1 有自己的文档: [MiniMax](/providers/minimax) 和
[本地模型](/gateway/local-models)。

经验法则：对于高风险工作，请使用你能负担得起的**最佳模型**，而对于常规聊天或摘要，请使用更便宜的模型。你可以根据代理路由模型，并使用子代理来并行化长时间任务（每个子代理消耗令牌）。参见 [Models](/concepts/models) 和
[Sub-agents](/tools/subagents)。

强烈警告：较弱/过度量化的模型更容易受到提示注入和不安全行为的影响。参见 [Security](/gateway/security)。

更多背景: [Models](/concepts/models)。

### 我可以使用自托管模型 llamacpp vLLM Ollama 吗

可以。如果你的本地服务器暴露了一个 OpenAI 兼容的 API，你可以将其指向一个自定义提供商。Ollama 直接支持并且是最简单的路径。

安全说明：较小或高度量化的模型更容易受到提示注入的影响。我们强烈建议对于任何可以使用工具的机器人使用**大型模型**。
如果你仍然希望使用小型模型，请启用沙箱和严格的工具白名单。

文档: [Ollama](/providers/ollama), [本地模型](/gateway/local-models),
[模型提供商](/concepts/model-providers), [Security](/gateway/security),
[Sandboxing](/gateway/sandboxing)。

### 如何在不擦除配置的情况下切换模型

使用**模型命令**或仅编辑**模型**字段。避免完整的配置替换。

安全选项：

- `/model` 在聊天中（快速，每会话）
- `openclaw models set ...`（仅更新模型配置）
- `openclaw configure --section model`（交互式）
- 编辑 `agents.defaults.model` 在 `~/.openclaw/openclaw.json`

避免使用部分对象的 `config.apply`，除非你打算替换整个配置。
如果你确实覆盖了配置，请从备份中恢复或重新运行 `openclaw doctor` 以修复。

文档: [Models](/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/gateway/doctor)。

### OpenClaw, Flawd 和 Krill 使用什么模型

- **OpenClaw + Flawd:** Anthropic Opus (`anthropic/claude-opus-4-6`) - 请参阅 [Anthropic](/providers/anthropic).
- **Krill:** MiniMax M2.1 (`minimax/MiniMax-M2.1`) - 请参阅 [MiniMax](/providers/minimax).

### 如何在不重启的情况下切换模型

使用 `/model` 命令作为独立消息：

```
/model sonnet
/model haiku
/model opus
/model gpt
/model gpt-mini
/model gemini
/model gemini-flash
```

您可以使用 `/model`、`/model list` 或 `/model status` 列出可用模型。

`/model` (和 `/model list`) 显示一个紧凑的编号选择器。通过编号选择：

```
/model 3
```

您还可以为提供商（每个会话）强制指定特定的身份验证配置文件：

```
/model opus@anthropic:default
/model opus@anthropic:work
```

提示：`/model status` 显示哪个代理处于活动状态，正在使用的 `auth-profiles.json` 文件以及将尝试的下一个身份验证配置文件。
它还显示配置的提供商端点 (`baseUrl`) 和 API 模式 (`api`)（如果可用）。

**如何取消我使用 profile 设置的配置文件**

重新运行 `/model` **不带** `@profile` 后缀：

```
/model anthropic/claude-opus-4-6
```

如果您想恢复默认设置，请从 `/model` 中选择（或发送 `/model <default provider/model>`）。
使用 `/model status` 确认哪个身份验证配置文件处于活动状态。

### 我可以使用 GPT 5.2 进行日常任务，使用 Codex 5.3 进行编码吗？

可以。将其中一个设置为默认，并根据需要进行切换：

- **快速切换（每个会话）：** 使用 `/model gpt-5.2` 进行日常任务，使用 `/model gpt-5.3-codex` 进行编码。
- **默认 + 切换：** 将 `agents.defaults.model.primary` 设置为 `openai/gpt-5.2`，然后在编码时切换到 `openai-codex/gpt-5.3-codex`（或反之亦然）。
- **子代理：** 将编码任务路由到具有不同默认模型的子代理。

请参阅 [Models](/concepts/models) 和 [Slash commands](/tools/slash-commands).

### 为什么我会看到“Model is not allowed”然后没有回复

如果设置了 `agents.defaults.models`，它将成为 `/model` 的 **允许列表** 以及任何
会话重写。选择不在该列表中的模型将返回：

```
Model "provider/model" is not allowed. Use /model to list available models.
```

该错误将 **代替** 正常回复返回。解决方法：将模型添加到
`agents.defaults.models`，移除允许列表，或从 `/model list` 中选择模型。

### 为什么我会看到“Unknown model minimaxMiniMaxM21”

这意味着 **提供商未配置**（未找到 MiniMax 提供商配置或身份验证
配置文件），因此无法解析模型。此检测的修复程序将在 **2026.1.12** 中（撰写本文时尚未发布）。

修复检查清单：

1. 升级到 **2026.1.12**（或从源代码运行 `main`），然后重启网关。
2. 确保已配置 MiniMax（向导或 JSON），或者 env/auth 配置文件中存在 MiniMax API 密钥
   以便注入提供商。
3. 使用确切的模型 ID（区分大小写）：`minimax/MiniMax-M2.1` 或
   `minimax/MiniMax-M2.1-lightning`。
4. 运行：

   ```bash
   openclaw models list
   ```

并从列表中选择（或聊天中的`/model list`）。

参见 [MiniMax](/providers/minimax) 和 [Models](/concepts/models)。

### 我可以将MiniMax作为默认选项，而将OpenAI用于复杂任务吗？

可以。使用 **MiniMax作为默认选项**，并在需要时按**会话**切换模型。
回退选项是为**错误**设计的，而不是“硬任务”，因此请使用`/model`或单独的代理。

**选项A：按会话切换**

```json5
{
  env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.1" },
      models: {
        "minimax/MiniMax-M2.1": { alias: "minimax" },
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

**选项B：单独的代理**

- 代理A默认：MiniMax
- 代理B默认：OpenAI
- 按代理路由或使用`/agent`进行切换

文档：[Models](/concepts/models), [Multi-Agent Routing](/concepts/multi-agent), [MiniMax](/providers/minimax), [OpenAI](/providers/openai)。

### opus sonnet gpt是否内置快捷方式

是。OpenClaw附带了一些默认缩写（仅在模型存在于`agents.defaults.models`时应用）：

- `opus` → `anthropic/claude-opus-4-6`
- `sonnet` → `anthropic/claude-sonnet-4-5`
- `gpt` → `openai/gpt-5.2`
- `gpt-mini` → `openai/gpt-5-mini`
- `gemini` → `google/gemini-3-pro-preview`
- `gemini-flash` → `google/gemini-3-flash-preview`

如果您设置了同名的自定义别名，则您的值优先。

### 如何定义/覆盖模型快捷方式别名

别名来自`agents.defaults.models.<modelId>.alias`。示例：

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

然后`/model sonnet`（或`/<alias>`当支持时）解析为该模型ID。

### 如何添加来自其他提供商的模型，如OpenRouter或ZAI

OpenRouter（按令牌付费；多种模型）：

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

Z.AI（GLM模型）：

```json5
{
  agents: {
    defaults: {
      model: { primary: "zai/glm-4.7" },
      models: { "zai/glm-4.7": {} },
    },
  },
  env: { ZAI_API_KEY: "..." },
}
```

如果您引用了提供商/模型但缺少所需的提供商密钥，您将收到运行时身份验证错误（例如`No API key found for provider "zai"`）。

**添加新代理后未找到提供商的API密钥**

这通常意味着**新代理**的身份验证存储为空。每个代理的身份验证信息存储在：

```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

解决方法：

- 运行 `openclaw agents add <id>` 并在向导中配置身份验证。
- 或者从主代理的 `agentDir` 复制 `auth-profiles.json` 到新代理的 `agentDir`。

不要 在多个代理之间重用 `agentDir`；这会导致身份验证/会话冲突。

## 模型故障转移和“所有模型失败”

### 故障转移如何工作

故障转移分为两个阶段：

1. **同一提供商内的身份验证配置文件轮换**。
2. **模型回退**到 `agents.defaults.model.fallbacks` 中的下一个模型。

对失败的配置文件应用冷却时间（指数退避），因此即使提供商被限速或暂时失败，OpenClaw 也可以继续响应。

### 此错误意味着什么

```
No credentials found for profile "anthropic:default"
```

这意味着系统尝试使用身份验证配置文件 ID `anthropic:default`，但在预期的身份验证存储中找不到凭据。

### 没有找到配置文件 anthropicdefault 的凭据的修复检查清单

- **确认身份验证配置文件的位置**（新路径与旧路径）
  - 当前：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
  - 旧版：`~/.openclaw/agent/*`（由 `openclaw doctor` 迁移）
- **确认您的环境变量是否被网关加载**
  - 如果您在 shell 中设置了 `ANTHROPIC_API_KEY` 但通过 systemd/launchd 运行网关，则可能不会继承它。将其放入 `~/.openclaw/.env` 或启用 `env.shellEnv`。
- **确保您正在编辑正确的代理**
  - 多代理设置意味着可能存在多个 `auth-profiles.json` 文件。
- **检查模型/身份验证状态**
  - 使用 `openclaw models status` 查看已配置的模型以及提供商是否经过身份验证。

**没有找到配置文件 anthropic 的凭据的修复检查清单**

这意味着运行被固定到一个 Anthropic 身份验证配置文件，但网关在其身份验证存储中找不到它。

- **使用设置令牌**
  - 运行 `claude setup-token`，然后将其粘贴到 `openclaw models auth setup-token --provider anthropic`。
  - 如果该令牌是在另一台机器上创建的，请使用 `openclaw models auth paste-token --provider anthropic`。
- **如果您想改用 API 密钥**
  - 将 `ANTHROPIC_API_KEY` 放在 **网关主机** 的 `~/.openclaw/.env` 中。
  - 清除任何强制使用缺失配置文件的固定顺序：

    ```bash
    openclaw models auth order clear --provider anthropic
    ```

- **确认您在网关主机上运行命令**
  - 在远程模式下，身份验证配置文件位于网关机器上，而不是您的笔记本电脑上。

### 为什么它还尝试了 Google Gemini 并失败

如果您的模型配置包括 Google Gemini 作为回退选项（或您切换到了 Gemini 简写），OpenClaw 将在模型回退期间尝试使用它。如果您没有配置 Google 凭据，您将看到 `No API key found for provider "google"`。

修复方法：要么提供 Google 身份验证，要么在 `agents.defaults.model.fallbacks` / 别名中删除/避免使用 Google 模型，以便回退不会路由到那里。

**LLM 请求被拒绝消息认为需要签名 google antigravity**

原因：会话历史中包含**没有签名的thinking blocks**（通常是由于中止/部分流导致的）。Google Antigravity需要thinking blocks的签名。

修复：OpenClaw现在会为Google Antigravity Claude去除无签名的thinking blocks。如果仍然出现，请开始一个**新会话**或为该代理设置`/thinking off`。

## 认证配置文件：它们是什么以及如何管理它们

相关：[/concepts/oauth](/concepts/oauth) (OAuth流程、令牌存储、多账户模式)

### 认证配置文件是什么

认证配置文件是与提供商绑定的命名凭据记录（OAuth或API密钥）。配置文件位于：

```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

### 典型的配置文件ID有哪些

OpenClaw使用带有提供商前缀的ID，例如：

- `anthropic:default`（当不存在电子邮件身份时常见）
- `anthropic:<email>`用于OAuth身份
- 您选择的自定义ID（例如`anthropic:work`）

### 我可以控制首先尝试哪个认证配置文件吗

可以。配置支持配置文件的可选元数据和每个提供商的顺序(`auth.order.<provider>`)。这**不**存储机密信息；它将ID映射到提供商/模式并设置轮换顺序。

如果某个配置文件处于短暂的**冷却**状态（速率限制/超时/认证失败）或更长的**禁用**状态（计费/信用不足），OpenClaw可能会暂时跳过该配置文件。要检查此状态，请运行`openclaw models status --json`并检查`auth.unusableProfiles`。调优：`auth.cooldowns.billingBackoffHours*`。

您还可以通过CLI设置**每个代理**的顺序覆盖（存储在该代理的`auth-profiles.json`中）：

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

要针对特定代理：

```bash
openclaw models auth order set --provider anthropic --agent main anthropic:default
```

### OAuth与API密钥有什么区别

OpenClaw同时支持：

- **OAuth**通常利用订阅访问（适用时）。
- **API密钥**使用按令牌付费的计费方式。

向导明确支持Anthropic设置令牌和OpenAI Codex OAuth，并可以为您存储API密钥。

## 网关：端口、“已运行”以及远程模式

### 网关使用哪个端口

`gateway.port`控制WebSocket + HTTP（控制UI、钩子等）的单个多路复用端口。

优先级：

```
--port > OPENCLAW_GATEWAY_PORT > gateway.port > default 18789
```

### 为什么openclaw网关状态显示Runtime正在运行但RPC探测失败

因为 "running" 是 **supervisor's** 视图 (launchd/systemd/schtasks)。The RPC probe 是 CLI 实际连接到网关 WebSocket 并调用 `status`。

使用 `openclaw gateway status` 并信任这些行：

- `Probe target:` (probe 实际使用的 URL)
- `Listening:` (实际绑定在端口上的内容)
- `Last gateway error:` (进程存活但端口未监听的常见原因)

### 为什么 openclaw 网关状态显示 Config cli 和 Config service 不同

你正在编辑一个配置文件，而服务正在运行另一个（通常是 `--profile` / `OPENCLAW_STATE_DIR` 不匹配）。

解决方法：

```bash
openclaw gateway install --force
```

从与服务相同的 `--profile` / 环境中运行该命令。

### 什么是另一个网关实例已经在监听的意思

OpenClaw 通过在启动时立即绑定 WebSocket 监听器来强制执行运行时锁（默认 `ws://127.0.0.1:18789`）。如果绑定失败并抛出 `EADDRINUSE`，则会抛出 `GatewayLockError` 表示另一个实例已经在监听。

解决方法：停止其他实例，释放端口，或使用 `openclaw gateway --port <port>` 运行。

### 如何在远程模式下运行 OpenClaw 客户端连接到其他位置的网关

设置 `gateway.mode: "remote"` 并指向远程 WebSocket URL，可选地带有令牌/密码：

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

注意：

- `openclaw gateway` 仅在 `gateway.mode` 为 `local`（或传递覆盖标志）时启动。
- macOS 应用程序监视配置文件，并在这些值更改时实时切换模式。

### 控制 UI 显示未经授权或不断重新连接怎么办

你的网关正在启用身份验证 (`gateway.auth.*`)，但 UI 没有发送匹配的令牌/密码。

事实（来自代码）：

- 控制 UI 将令牌存储在浏览器 localStorage 键 `openclaw.control.settings.v1` 中。

解决方法：

- 最快：`openclaw dashboard`（打印并复制仪表板 URL，尝试打开；如果无头则显示 SSH 提示）。
- 如果你还没有令牌：`openclaw doctor --generate-gateway-token`。
- 如果是远程，请先建立隧道：`ssh -N -L 18789:127.0.0.1:18789 user@host` 然后打开 `http://127.0.0.1:18789/`。
- 在网关主机上设置 `gateway.auth.token`（或 `OPENCLAW_GATEWAY_TOKEN`）。
- 在控制 UI 设置中粘贴相同的令牌。
- 仍然卡住？运行 `openclaw status --all` 并遵循 [故障排除](/gateway/troubleshooting)。参见 [仪表板](/web/dashboard) 获取身份验证详细信息。

### 我设置了 gatewaybind tailnet 但它无法绑定 没有东西在监听

`tailnet` 绑定从你的网络接口选择一个 Tailscale IP（100.64.0.0/10）。如果机器不在 Tailscale 上（或接口已关闭），则没有东西可以绑定。

解决方法：

- 在该主机上启动 Tailscale（以便它有一个 100.x 地址），或
- 切换到 `gateway.bind: "loopback"` / `"lan"`。

注意：`tailnet` 是显式的。`auto` 偏好回环；当你只想绑定到尾网时使用 `gateway.bind: "tailnet"`。

### 我可以在同一主机上运行多个网关吗？

通常不可以 - 一个网关可以运行多个消息通道和代理。仅在需要冗余（例如：救援机器人）或硬隔离时才使用多个网关。

可以，但你必须隔离：

- `OPENCLAW_CONFIG_PATH`（每个实例的配置）
- `OPENCLAW_STATE_DIR`（每个实例的状态）
- `agents.defaults.workspace`（工作区隔离）
- `gateway.port`（唯一端口）

快速设置（推荐）：

- 每个实例使用 `openclaw --profile <name> …`（自动创建 `~/.openclaw-<name>`）。
- 在每个配置文件中设置唯一的 `gateway.port`（或在手动运行时传递 `--port`）。
- 安装每个配置文件的服务：`openclaw --profile <name> gateway install`。

配置文件还会为服务名称添加后缀（`bot.molt.<profile>`；旧版 `com.openclaw.*`，`openclaw-gateway-<profile>.service`，`OpenClaw Gateway (<profile>)`）。
完整指南：[多个网关](/gateway/multiple-gateways)。

### 无效握手代码 1008 的含义是什么

网关是一个 **WebSocket 服务器**，它期望第一个消息是一个 `connect` 帧。如果收到其他内容，它将以 **代码 1008**（策略违规）关闭连接。

常见原因：

- 你在浏览器中打开了 **HTTP** URL (`http://...`) 而不是 WS 客户端。
- 你使用了错误的端口或路径。
- 代理或隧道剥离了认证头或发送了非网关请求。

快速修复：

1. 使用 WS URL：`ws://<host>:18789`（或 `wss://...` 如果使用 HTTPS）。
2. 不要在普通浏览器标签页中打开 WS 端口。
3. 如果启用了认证，请在 `connect` 帧中包含令牌/密码。

如果你使用的是 CLI 或 TUI，URL 应该如下所示：

```
openclaw tui --url ws://<host>:18789 --token <token>
```

协议详情：[网关协议](/gateway/protocol)。

## 日志记录和调试

### 日志在哪里

文件日志（结构化）：

```
/tmp/openclaw/openclaw-YYYY-MM-DD.log
```

你可以通过 `logging.file` 设置一个稳定的路径。文件日志级别由 `logging.level` 控制。控制台详细程度由 `--verbose` 和 `logging.consoleLevel` 控制。

最快的日志跟踪：

```bash
openclaw logs --follow
```

服务/监督日志（当网关通过 launchd/systemd 运行时）：

- macOS: `$OPENCLAW_STATE_DIR/logs/gateway.log` 和 `gateway.err.log`（默认：`~/.openclaw/logs/...`；配置文件使用 `~/.openclaw-<profile>/logs/...`）
- Linux: `journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
- Windows: `schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

更多请参见 [故障排除](/gateway/troubleshooting#log-locations)。

### 如何启动/停止/重启网关服务

使用网关辅助工具：

```bash
openclaw gateway status
openclaw gateway restart
```

如果你手动运行网关，`openclaw gateway --force` 可以回收端口。详见 [网关](/gateway)。

### 我在 Windows 上关闭了终端，如何重启 OpenClaw

有 **两种 Windows 安装模式**:

**1) WSL2 (推荐):** Gateway 在 Linux 内运行。

打开 PowerShell，进入 WSL，然后重启：

```powershell
wsl
openclaw gateway status
openclaw gateway restart
```

如果您从未安装过服务，请在前台启动：

```bash
openclaw gateway run
```

**2) 原生 Windows (不推荐):** Gateway 直接在 Windows 内运行。

打开 PowerShell 并运行：

```powershell
openclaw gateway status
openclaw gateway restart
```

如果您手动运行（无服务），使用：

```powershell
openclaw gateway run
```

文档: [Windows (WSL2)](/platforms/windows), [Gateway 服务运行手册](/gateway).

### Gateway 已启动但回复从未到达 我应该检查什么

从快速健康检查开始：

```bash
openclaw status
openclaw models status
openclaw channels status
openclaw logs --follow
```

常见原因：

- 模型认证未加载到 **gateway 主机** (检查 `models status`)。
- 通道配对/允许列表阻止回复 (检查通道配置 + 日志)。
- WebChat/Dashboard 未使用正确的令牌打开。

如果您是远程访问，请确认隧道/Tailscale 连接正常且 Gateway WebSocket 可达。

文档: [Channels](/channels), [故障排除](/gateway/troubleshooting), [远程访问](/gateway/remote).

### 与 gateway 断开连接没有原因 现在该怎么办

这通常意味着 UI 失去了 WebSocket 连接。检查：

1. Gateway 是否正在运行？ `openclaw gateway status`
2. Gateway 是否健康？ `openclaw status`
3. UI 是否使用了正确的令牌？ `openclaw dashboard`
4. 如果是远程访问，隧道/Tailscale 链接是否正常？

然后查看日志：

```bash
openclaw logs --follow
```

文档: [Dashboard](/web/dashboard), [远程访问](/gateway/remote), [故障排除](/gateway/troubleshooting).

### Telegram setMyCommands 出现网络错误 应该检查什么

从日志和通道状态开始：

```bash
openclaw channels status
openclaw channels logs --channel telegram
```

如果您在 VPS 或代理后面，请确认出站 HTTPS 允许且 DNS 正常工作。
如果 Gateway 是远程的，请确保您查看的是 Gateway 主机的日志。

文档: [Telegram](/channels/telegram), [通道故障排除](/channels/troubleshooting).

### TUI 显示无输出 应该检查什么

首先确认 Gateway 可达且代理可以运行：

```bash
openclaw status
openclaw models status
openclaw logs --follow
```

在 TUI 中，使用 `/status` 查看当前状态。如果您期望在聊天通道中收到回复，请确保已启用交付 (`/deliver on`)。

文档: [TUI](/web/tui), [斜杠命令](/tools/slash-commands).

### 如何完全停止然后启动 Gateway

如果您安装了服务：

```bash
openclaw gateway stop
openclaw gateway start
```

这会停止/启动 **受监督的服务** (macOS 上的 launchd, Linux 上的 systemd)。
当 Gateway 作为后台守护进程运行时使用此方法。

如果您在前台运行，请使用 Ctrl-C 停止，然后：

```bash
openclaw gateway run
```

文档: [网关服务运行手册](/gateway).

### ELI5 openclaw gateway restart vs openclaw gateway

- `openclaw gateway restart`: 重启 **后台服务** (launchd/systemd).
- `openclaw gateway`: 在此终端会话中以 **前台模式** 运行网关.

如果您安装了服务，请使用网关命令。当您需要一次性前台运行时使用 `openclaw gateway`。

### 当出现问题时，获取更多详细信息的最快方法是什么

使用 `--verbose` 启动网关以获取更多控制台详细信息。然后检查日志文件以查找通道认证、模型路由和RPC错误。

## 媒体和附件

### 我的技能生成了一个imagePDF但没有发送出去

代理发出的附件必须包含一个 `MEDIA:<path-or-url>` 行（单独一行）。参见 [OpenClaw 助理设置](/start/openclaw) 和 [代理发送](/tools/agent-send).

CLI 发送:

```bash
openclaw message send --target +15555550123 --message "Here you go" --media /path/to/file.png
```

另外检查：

- 目标频道支持传出媒体且未被白名单阻止。
- 文件在提供商的大小限制内（图像最大调整为2048px）。

参见 [图像](/nodes/images).

## 安全性和访问控制

### 将OpenClaw暴露给传入的DM是否安全

将传入的DM视为不受信任的输入。默认设置旨在降低风险：

- 支持DM的频道上的默认行为是 **配对**：
  - 未知发送者会收到一个配对码；机器人不会处理他们的消息。
  - 使用以下命令批准：`openclaw pairing approve <channel> <code>`
  - 待处理请求每个频道最多 **3个**；如果代码未到达，请检查 `openclaw pairing list <channel>`。
- 公开打开DM需要显式同意 (`dmPolicy: "open"` 和白名单 `"*"`)。

运行 `openclaw doctor` 以显示有风险的DM策略。

### 提示注入仅对公共机器人是一个问题吗

不完全是。提示注入涉及 **不受信任的内容**，而不仅仅是谁可以向机器人发送DM。
如果您的助手读取外部内容（网络搜索/获取、浏览器页面、电子邮件、文档、附件、粘贴的日志），这些内容可能包含试图劫持模型的指令。即使 **只有您是发送者**，这也可能发生。

最大的风险是在启用工具时：模型可能会被诱骗泄露上下文或代表您调用工具。通过以下方式减少影响范围：

- 使用只读或禁用工具的“阅读器”代理来总结不受信任的内容
- 对于启用工具的代理，关闭 `web_search` / `web_fetch` / `browser`
- 沙盒化和严格的工具白名单

详情：[安全性](/gateway/security).

### 我的机器人是否应该有自己的电子邮件GitHub账户或电话号码

对于大多数设置来说，是的。使用单独的账户和电话号码隔离机器人可以减少出现问题时的影响范围。这也有助于轻松轮换凭据或撤销访问权限而不影响您的个人账户。

从小开始。仅授予您实际需要的工具和账户访问权限，并在需要时扩展。

文档：[安全](/gateway/security)，[配对](/channels/pairing)。

### 我可以赋予它对我短信的自主权吗？这样做安全吗

我们**不**建议对个人消息赋予完全自主权。最安全的做法是：

- 将DM保持在**配对模式**或一个严格的白名单中。
- 如果希望它代表您发送消息，请使用**单独的号码或账户**。
- 让它起草，然后**批准后再发送**。

如果您想进行实验，请在一个专用账户上进行并保持隔离。参见[安全](/gateway/security)。

### 我可以使用更便宜的模型来执行个人助理任务吗

是的，**如果**代理仅限于聊天且输入是可信的。较小的层级更容易受到指令劫持，因此避免在启用工具的代理或读取不可信内容时使用它们。如果必须使用较小的模型，请锁定工具并在沙箱中运行。参见[安全](/gateway/security)。

### 我在Telegram上运行了start但没有收到配对码

配对码**仅**在未知发件人向机器人发送消息且`dmPolicy: "pairing"`已启用时发送。`/start`本身不会生成代码。

检查待处理请求：

```bash
openclaw pairing list telegram
```

如果您希望立即获得访问权限，请将您的发件人ID加入白名单或为该账户设置`dmPolicy: "open"`。

### WhatsApp会向我的联系人发送消息吗？配对是如何工作的

不。默认的WhatsApp DM策略是**配对**。未知发件人只会收到配对码且他们的消息**不会被处理**。OpenClaw仅回复接收到的聊天或您触发的显式发送。

通过以下方式批准配对：

```bash
openclaw pairing approve whatsapp <code>
```

列出待处理请求：

```bash
openclaw pairing list whatsapp
```

向导电话号码提示：用于设置您的**白名单/所有者**，以便允许自己的DM。它不用于自动发送。如果您使用的是个人WhatsApp号码，请使用该号码并启用`channels.whatsapp.selfChatMode`。

## 聊天命令、取消任务以及“它不会停止”

### 如何阻止内部系统消息显示在聊天中

大多数内部或工具消息仅在该会话启用了**verbose**或**reasoning**时出现。

在看到它的聊天中修复：

```
/verbose off
/reasoning off
```

如果仍然嘈杂，请检查控制UI中的会话设置并将verbose设置为**inherit**。同时确认您没有使用设置了`verboseDefault`为`on`的机器人配置文件。

文档：[思考和详细输出](/tools/thinking)，[安全](/gateway/security#reasoning--verbose-output-in-groups)。

### 如何停止/取消正在运行的任务

发送以下任意一个**作为独立消息**（无斜杠）：

```
stop
abort
esc
wait
exit
interrupt
```

这些是中止触发器（不是斜杠命令）。

对于后台进程（来自exec工具），您可以要求代理运行：

```
process action:kill sessionId:XXX
```

斜杠命令概述：参见[斜杠命令](/tools/slash-commands)。

大多数命令必须作为以`/`开头的**独立**消息发送，但一些快捷方式（如`/status`）也允许白名单发送者在行内使用。

### 如何从Telegram发送Discord消息 跨上下文消息被拒绝

OpenClaw默认阻止**跨提供商**消息。如果工具调用绑定到Telegram，则不会发送到Discord，除非您明确允许。

为代理启用跨提供商消息：

```json5
{
  agents: {
    defaults: {
      tools: {
        message: {
          crossContext: {
            allowAcrossProviders: true,
            marker: { enabled: true, prefix: "[from {channel}] " },
          },
        },
      },
    },
  },
}
```

编辑配置后重启网关。如果您只想为单个代理启用此功能，请将其设置在`agents.list[].tools.message`下。

### 为什么感觉机器人忽略了连发的消息

队列模式控制新消息如何与正在进行的任务交互。使用`/queue`更改模式：

- `steer` - 新消息重定向当前任务
- `followup` - 逐条运行消息
- `collect` - 批量消息并一次回复（默认）
- `steer-backlog` - 立即处理，然后处理积压消息
- `interrupt` - 中止当前运行并重新开始

您可以添加选项如`debounce:2s cap:25 drop:summarize`用于后续模式。

## 根据截图/聊天记录回答确切的问题

**Q: "Anthropic的默认模型是什么？（带有API密钥）"**

**A:** 在OpenClaw中，凭据和模型选择是分开的。设置`ANTHROPIC_API_KEY`（或将Anthropic API密钥存储在身份验证配置文件中）可启用身份验证，但实际的默认模型是您在`agents.defaults.model.primary`中配置的（例如，`anthropic/claude-sonnet-4-5`或`anthropic/claude-opus-4-6`）。如果您看到`No credentials found for profile "anthropic:default"`，这意味着网关无法在代理运行时预期的`auth-profiles.json`中找到Anthropic凭据。

---

仍然有问题？在[Discord](https://discord.com/invite/clawd)提问或在[GitHub讨论](https://github.com/openclaw/openclaw/discussions)中打开讨论。